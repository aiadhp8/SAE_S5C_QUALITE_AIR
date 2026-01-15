"""
Script 01 - Extraction des données de Pollution (Historique multi-années)
=========================================================================
Ce script extrait les données historiques de qualité de l'air depuis AWS S3 OpenAQ.

Les données OpenAQ sont archivées sur le bucket S3 public 'openaq-data-archive'.
Structure: s3://openaq-data-archive/records/csv.gz/locationid={id}/year={year}/month={month}/

Processus:
1. Récupérer la liste des locations avec leurs métadonnées (pays, paramètres) via l'API v3
2. Échantillonner des locations par pays
3. Télécharger les données CSV depuis S3 pour chaque location/année
4. Agréger par pays/année/polluant

Sortie: data/raw/openaq_country_averages.csv
"""

import sys
sys.path.append(str(__file__).rsplit('scripts', 1)[0])

import os
import requests
import pandas as pd
import gzip
import io
from collections import defaultdict
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

from config import DATA_RAW, ANNEES_ANALYSE

# =============================================================================
# CONFIGURATION
# =============================================================================
BASE_URL_V3 = "https://api.openaq.org/v3"
S3_BASE_URL = "https://openaq-data-archive.s3.amazonaws.com"

OPENAQ_API_KEY = os.getenv('OPENAQ_API_KEY')

HEADERS = {
    "Accept": "application/json",
}

if OPENAQ_API_KEY:
    HEADERS["X-API-Key"] = OPENAQ_API_KEY

# Paramètres d'intérêt
PARAMETERS_OF_INTEREST = ["pm25", "pm10", "o3", "no2", "so2", "co"]

# Années à extraire
YEARS_TO_EXTRACT = ANNEES_ANALYSE  # [2018, 2019, 2020, 2021, 2022, 2023]

# Nombre de locations à échantillonner par pays
MAX_LOCATIONS_PER_COUNTRY = 10

# Nombre de mois à échantillonner par année (pour réduire le volume)
MONTHS_TO_SAMPLE = [1, 4, 7, 10]  # Janvier, Avril, Juillet, Octobre


# =============================================================================
# FONCTIONS API
# =============================================================================

def api_request(url, params=None, max_retries=3):
    """Effectue une requête API avec gestion des erreurs."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=60)

            if response.status_code == 429:
                wait_time = 30 * (attempt + 1)
                print(f"    Rate limited, attente {wait_time}s...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                return None
    return None


def get_locations_metadata(max_pages=100):
    """
    Récupère les métadonnées des locations (id, pays, paramètres disponibles).

    Returns:
        dict: {location_id: {"country_code": str, "country_name": str, "parameters": set}}
    """
    url = f"{BASE_URL_V3}/locations"
    locations = {}
    page = 1

    print("  Récupération des métadonnées des stations...")

    while page <= max_pages:
        params = {"limit": 1000, "page": page}
        data = api_request(url, params)

        if not data:
            break

        results = data.get("results", [])
        if not results:
            break

        for loc in results:
            loc_id = loc.get("id")
            country = loc.get("country") or {}
            sensors = loc.get("sensors") or []

            if not loc_id or not country.get("code"):
                continue

            # Extraire les paramètres disponibles pour cette location
            params_available = set()
            for sensor in sensors:
                param = sensor.get("parameter", {})
                param_name = param.get("name", "").lower()
                if param_name in PARAMETERS_OF_INTEREST:
                    params_available.add(param_name)

            if params_available:
                locations[loc_id] = {
                    "country_code": country.get("code", ""),
                    "country_name": country.get("name", ""),
                    "parameters": params_available
                }

        print(f"    Page {page}: {len(results)} stations ({len(locations)} avec paramètres d'intérêt)")

        # Vérifier si on a tout récupéré
        found = data.get("meta", {}).get("found", 0)
        if isinstance(found, str):
            try:
                found = int(found)
            except ValueError:
                found = 999999

        if page * 1000 >= found:
            break

        page += 1
        time.sleep(0.3)

    return locations


def sample_locations_by_country(locations, max_per_country=MAX_LOCATIONS_PER_COUNTRY):
    """
    Échantillonne des locations par pays pour limiter le volume de données.

    Returns:
        list: [(location_id, country_code, country_name, parameters), ...]
    """
    # Grouper par pays
    by_country = defaultdict(list)
    country_names = {}

    for loc_id, info in locations.items():
        cc = info["country_code"]
        by_country[cc].append((loc_id, info["parameters"]))
        country_names[cc] = info["country_name"]

    # Échantillonner
    sampled = []
    for cc, locs in by_country.items():
        # Trier par nombre de paramètres (prendre les plus complets)
        locs.sort(key=lambda x: len(x[1]), reverse=True)
        for loc_id, params in locs[:max_per_country]:
            sampled.append((loc_id, cc, country_names[cc], params))

    return sampled


# =============================================================================
# FONCTIONS S3
# =============================================================================

def download_s3_file(location_id, year, month):
    """
    Télécharge et parse un fichier mensuel depuis S3.

    Returns:
        pd.DataFrame ou None
    """
    # Construire le préfixe S3
    prefix = f"records/csv.gz/locationid={location_id}/year={year}/month={month:02d}/"
    list_url = f"{S3_BASE_URL}?prefix={prefix}"

    try:
        # Lister les fichiers dans ce répertoire
        response = requests.get(list_url, timeout=30)
        if response.status_code != 200:
            return None

        # Parser le XML S3 pour trouver les fichiers
        content = response.text

        # Extraire les clés des fichiers (simple parsing XML)
        import re
        keys = re.findall(r'<Key>([^<]+\.csv\.gz)</Key>', content)

        if not keys:
            return None

        # Télécharger le premier fichier (ou tous et concaténer)
        all_data = []
        for key in keys[:5]:  # Limiter à 5 fichiers par mois
            file_url = f"{S3_BASE_URL}/{key}"
            try:
                resp = requests.get(file_url, timeout=60)
                if resp.status_code == 200:
                    # Décompresser et lire
                    with gzip.GzipFile(fileobj=io.BytesIO(resp.content)) as f:
                        df = pd.read_csv(f)
                        all_data.append(df)
            except Exception:
                continue

        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return None

    except Exception as e:
        return None


def extract_location_yearly_data(location_id, year, country_code, country_name):
    """
    Extrait les données annuelles pour une location.
    Échantillonne quelques mois pour être efficace.

    Returns:
        list: [{country_code, country_name, year, parameter, values: [...]}, ...]
    """
    results = defaultdict(list)

    for month in MONTHS_TO_SAMPLE:
        df = download_s3_file(location_id, year, month)

        if df is None or df.empty:
            continue

        # Filtrer les paramètres d'intérêt
        if 'parameter' not in df.columns or 'value' not in df.columns:
            continue

        for param in PARAMETERS_OF_INTEREST:
            param_data = df[df['parameter'].str.lower() == param]
            if not param_data.empty:
                # Filtrer les valeurs aberrantes
                values = param_data['value'].dropna()
                values = values[(values >= 0) & (values <= 5000)]
                results[param].extend(values.tolist())

    # Convertir en liste de résultats
    output = []
    for param, values in results.items():
        if values:
            output.append({
                "country_code": country_code,
                "country_name": country_name,
                "year": year,
                "parameter": param,
                "values": values
            })

    return output


# =============================================================================
# EXTRACTION PRINCIPALE
# =============================================================================

def extract_historical_data_s3():
    """
    Extrait les données historiques depuis AWS S3.
    """
    print("\n--- Extraction OpenAQ depuis AWS S3 ---")
    print(f"  Années cibles: {YEARS_TO_EXTRACT}")
    print(f"  Mois échantillonnés: {MONTHS_TO_SAMPLE}")

    # Étape 1: Récupérer les métadonnées des locations
    locations = get_locations_metadata()

    if not locations:
        print("  Échec de récupération des métadonnées")
        return None

    print(f"\n  {len(locations)} stations avec paramètres d'intérêt")

    # Étape 2: Échantillonner par pays
    sampled = sample_locations_by_country(locations)
    print(f"  {len(sampled)} stations échantillonnées ({len(set(s[1] for s in sampled))} pays)")

    # Étape 3: Extraire les données par location/année
    # Structure: {(country_code, year, param): [values]}
    aggregated = defaultdict(list)
    country_names = {}

    total_tasks = len(sampled) * len(YEARS_TO_EXTRACT)
    processed = 0

    print(f"\n  Téléchargement des données S3 ({total_tasks} tâches)...")
    print("  Cela peut prendre 10-30 minutes...\n")

    for loc_id, cc, cn, params in sampled:
        country_names[cc] = cn

        for year in YEARS_TO_EXTRACT:
            processed += 1

            if processed % 50 == 0:
                pct = 100 * processed // total_tasks
                unique_keys = len(aggregated)
                print(f"    Progression: {processed}/{total_tasks} ({pct}%) - {unique_keys} combinaisons pays/année/param")

            results = extract_location_yearly_data(loc_id, year, cc, cn)

            for r in results:
                key = (r["country_code"], r["year"], r["parameter"])
                aggregated[key].extend(r["values"])

            time.sleep(0.1)  # Rate limiting léger

    # Étape 4: Calculer les moyennes
    print("\n  Agrégation finale...")

    all_data = []
    for (cc, year, param), values in aggregated.items():
        if not values:
            continue

        # Supprimer les outliers (> 3 écarts-types)
        import numpy as np
        arr = np.array(values)
        mean = np.mean(arr)
        std = np.std(arr)
        if std > 0:
            filtered = arr[np.abs(arr - mean) <= 3 * std]
        else:
            filtered = arr

        if len(filtered) == 0:
            continue

        all_data.append({
            "year": year,
            "country_code": cc,
            "country_name": country_names.get(cc, ""),
            "parameter": param,
            "average": round(float(np.mean(filtered)), 2),
            "median": round(float(np.median(filtered)), 2),
            "min": round(float(np.min(filtered)), 2),
            "max": round(float(np.max(filtered)), 2),
            "std": round(float(np.std(filtered)), 2),
            "measurement_count": len(filtered),
            "unit": "µg/m³"
        })

    if all_data:
        df = pd.DataFrame(all_data)
        df = df.sort_values(["year", "country_code", "parameter"])
        return df

    return None


def extract_latest_fallback():
    """
    Fallback: Récupère uniquement les dernières mesures via l'API.
    """
    print("\n--- Fallback: Extraction des dernières mesures via API ---")

    url = f"{BASE_URL_V3}/locations"
    locations_map = {}
    page = 1

    while page <= 10:
        params = {"limit": 1000, "page": page}
        data = api_request(url, params)

        if not data:
            break

        results = data.get("results", [])
        if not results:
            break

        for loc in results:
            loc_id = loc.get("id")
            country = loc.get("country") or {}
            sensors = loc.get("sensors") or []

            if loc_id and country.get("code"):
                for sensor in sensors:
                    param = sensor.get("parameter", {})
                    param_name = param.get("name", "").lower()
                    latest = sensor.get("latest", {})
                    value = latest.get("value")

                    if param_name in PARAMETERS_OF_INTEREST and value is not None:
                        if 0 <= value <= 5000:
                            key = (country.get("code"), param_name)
                            if key not in locations_map:
                                locations_map[key] = {
                                    "country_name": country.get("name", ""),
                                    "values": []
                                }
                            locations_map[key]["values"].append(value)

        page += 1
        time.sleep(0.3)

    # Agréger
    current_year = datetime.now().year
    all_data = []

    for (cc, param), info in locations_map.items():
        values = info["values"]
        if values:
            import numpy as np
            all_data.append({
                "year": current_year,
                "country_code": cc,
                "country_name": info["country_name"],
                "parameter": param,
                "average": round(float(np.mean(values)), 2),
                "median": round(float(np.median(values)), 2),
                "min": round(float(np.min(values)), 2),
                "max": round(float(np.max(values)), 2),
                "std": round(float(np.std(values)), 2),
                "measurement_count": len(values),
                "unit": "µg/m³"
            })

    if all_data:
        return pd.DataFrame(all_data)
    return None


# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================

def main():
    """Fonction principale d'extraction."""
    print("=" * 70)
    print("EXTRACTION DES DONNÉES DE POLLUTION - HISTORIQUE MULTI-ANNÉES")
    print("=" * 70)

    if OPENAQ_API_KEY:
        print(f"  Clé API OpenAQ: Configurée")
    else:
        print("  Clé API OpenAQ: Non configurée (requêtes limitées)")

    print(f"  Années cibles: {min(YEARS_TO_EXTRACT)}-{max(YEARS_TO_EXTRACT)}")
    print(f"  Polluants: {', '.join(PARAMETERS_OF_INTEREST)}")

    # Extraction principale via S3
    df = extract_historical_data_s3()

    # Fallback si échec
    if df is None or len(df) < 20:
        print("\n  Données S3 insuffisantes, utilisation du fallback API...")
        df = extract_latest_fallback()

    if df is not None and len(df) > 0:
        output_path = DATA_RAW / "openaq_country_averages.csv"
        df.to_csv(output_path, index=False)

        print(f"\n{'=' * 70}")
        print(f"DONNÉES SAUVEGARDÉES: {output_path}")
        print(f"  {len(df)} enregistrements")
        print(f"  {df['country_code'].nunique()} pays")
        print(f"  {df['parameter'].nunique()} polluants")

        years_list = sorted(df['year'].unique())
        print(f"  Années: {years_list}")
        print(f"  Couverture: {len(years_list)} années ({min(years_list)}-{max(years_list)})")
        print("=" * 70)

        # Résumé par année
        print("\n" + "-" * 70)
        print("RÉSUMÉ PAR ANNÉE (pour analyse temporelle)")
        print("-" * 70)
        for year in years_list:
            year_df = df[df['year'] == year]
            params = sorted(year_df['parameter'].unique())
            print(f"  {year}: {len(year_df):4d} records | {year_df['country_code'].nunique():3d} pays | {', '.join(params)}")

        # Résumé par polluant
        print("\n" + "-" * 70)
        print("RÉSUMÉ PAR POLLUANT")
        print("-" * 70)
        for param in sorted(df['parameter'].unique()):
            param_df = df[df['parameter'] == param]
            param_years = sorted(param_df['year'].unique())
            print(f"  {param:6s}: {len(param_df):4d} records | {param_df['country_code'].nunique():3d} pays | {min(param_years)}-{max(param_years)}")

        # Aperçu des données
        print("\n" + "-" * 70)
        print("APERÇU DES DONNÉES")
        print("-" * 70)
        print(df.head(10).to_string(index=False))

    else:
        print("\nERREUR: Aucune donnée extraite!")
        print("Vérifiez votre connexion et la clé API OpenAQ")


if __name__ == "__main__":
    main()
