"""
Script 02 - Extraction des données World Cities Database
=========================================================
MEMBRE RESPONSABLE: [Données de Base - À assigner]

Ce script télécharge et traite la base World Cities de SimpleMaps.
C'est une donnée COMMUNE utilisée par tous les membres du groupe.

Source: https://simplemaps.com/data/world-cities
Sortie: data/raw/world_cities.csv
"""

import sys
sys.path.append(str(__file__).rsplit('scripts', 1)[0])

import pandas as pd
import zipfile
from config import DATA_RAW

# =============================================================================
# CONFIGURATION
# =============================================================================

# URL de téléchargement (version gratuite)
DOWNLOAD_URL = "https://simplemaps.com/data/world-cities"
LOCAL_FILE = DATA_RAW / "worldcities.csv"
LOCAL_ZIP = DATA_RAW / "simplemaps_worldcities_basic.zip"

# Colonnes d'intérêt
COLONNES_UTILES = [
    'city',           # Nom de la ville
    'city_ascii',     # Nom ASCII (sans accents)
    'lat',            # Latitude
    'lng',            # Longitude
    'country',        # Nom du pays
    'iso2',           # Code ISO2 du pays
    'iso3',           # Code ISO3 du pays
    'admin_name',     # Région/Province
    'capital',        # Type de capitale
    'population',     # Population
    'id'              # Identifiant unique
]

def download_world_cities():
    """
    Charge le fichier World Cities depuis SimpleMaps.
    Demande à l'utilisateur de télécharger manuellement si nécessaire.
    """
    # Vérifier si le fichier existe déjà
    if LOCAL_FILE.exists():
        print(f"Fichier trouvé: {LOCAL_FILE}")
        df = pd.read_csv(LOCAL_FILE)
        print(f"  {len(df)} villes chargées")
        return df

    if LOCAL_ZIP.exists():
        print(f"Archive trouvée: {LOCAL_ZIP}")
        return extract_zip(LOCAL_ZIP)

    # Fichier non trouvé, demander à l'utilisateur de le télécharger
    print("\n" + "=" * 60)
    print("TELECHARGEMENT MANUEL REQUIS")
    print("=" * 60)
    print(f"\n1. Ouvrez ce lien dans votre navigateur:")
    print(f"   {DOWNLOAD_URL}")
    print(f"\n2. Cliquez sur 'Free Download' pour télécharger le fichier ZIP")
    print(f"\n3. Placez le fichier téléchargé dans:")
    print(f"   {DATA_RAW}")
    print(f"\n4. Renommez-le en:")
    print(f"   worldcities.csv  (si CSV)")
    print(f"   OU gardez le ZIP tel quel")
    print("\n" + "=" * 60)

    input("\nAppuyez sur Entrée une fois le fichier placé...")

    # Vérifier à nouveau
    if LOCAL_FILE.exists():
        print(f"\nFichier trouvé: {LOCAL_FILE}")
        df = pd.read_csv(LOCAL_FILE)
        print(f"  {len(df)} villes chargées")
        return df

    # Chercher un fichier ZIP
    zip_files = list(DATA_RAW.glob("*worldcities*.zip")) + list(DATA_RAW.glob("*world_cities*.zip"))
    if zip_files:
        return extract_zip(zip_files[0])

    # Chercher un fichier CSV
    csv_files = list(DATA_RAW.glob("*worldcities*.csv")) + list(DATA_RAW.glob("*world_cities*.csv"))
    if csv_files:
        print(f"\nFichier trouvé: {csv_files[0]}")
        df = pd.read_csv(csv_files[0])
        print(f"  {len(df)} villes chargées")
        return df

    print("\nErreur: Aucun fichier World Cities trouvé.")
    return None


def extract_zip(zip_path):
    """
    Extrait le CSV depuis un fichier ZIP.
    """
    print(f"Extraction de {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as z:
        csv_files = [f for f in z.namelist() if f.endswith('.csv')]
        if not csv_files:
            print("Erreur: Aucun fichier CSV trouvé dans le ZIP")
            return None

        csv_filename = csv_files[0]
        print(f"  Extraction de {csv_filename}...")

        with z.open(csv_filename) as f:
            df = pd.read_csv(f)

    print(f"  {len(df)} villes chargées")
    return df

def clean_world_cities(df):
    """
    Nettoie et enrichit les données World Cities.
    """
    print("\nNettoyage des données...")

    # Garder uniquement les colonnes utiles
    available_cols = [c for c in COLONNES_UTILES if c in df.columns]
    df_clean = df[available_cols].copy()

    # Renommer pour cohérence
    rename_map = {
        'city_ascii': 'city_ascii',
        'lat': 'latitude',
        'lng': 'longitude',
        'iso2': 'country_code_iso2',
        'iso3': 'country_code_iso3',
        'admin_name': 'region'
    }
    df_clean = df_clean.rename(columns={k: v for k, v in rename_map.items() if k in df_clean.columns})

    # Nettoyer les valeurs
    print("  - Conversion des types...")
    if 'population' in df_clean.columns:
        df_clean['population'] = pd.to_numeric(df_clean['population'], errors='coerce')

    if 'latitude' in df_clean.columns:
        df_clean['latitude'] = pd.to_numeric(df_clean['latitude'], errors='coerce')

    if 'longitude' in df_clean.columns:
        df_clean['longitude'] = pd.to_numeric(df_clean['longitude'], errors='coerce')

    # Supprimer les doublons
    print("  - Suppression des doublons...")
    initial_count = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=['city', 'country'], keep='first')
    print(f"    {initial_count - len(df_clean)} doublons supprimés")

    # Supprimer les villes sans coordonnées
    print("  - Filtrage des données incomplètes...")
    df_clean = df_clean.dropna(subset=['latitude', 'longitude'])

    # Catégoriser les villes par taille
    print("  - Catégorisation par taille...")
    def categorize_city_size(pop):
        if pd.isna(pop):
            return 'inconnu'
        elif pop >= 10_000_000:
            return 'megapole'      # > 10M
        elif pop >= 1_000_000:
            return 'metropole'     # 1M - 10M
        elif pop >= 500_000:
            return 'grande_ville'  # 500k - 1M
        elif pop >= 100_000:
            return 'ville_moyenne' # 100k - 500k
        elif pop >= 50_000:
            return 'petite_ville'  # 50k - 100k
        else:
            return 'commune'       # < 50k

    if 'population' in df_clean.columns:
        df_clean['city_category'] = df_clean['population'].apply(categorize_city_size)

    # Statistiques
    print(f"\n  Résumé après nettoyage:")
    print(f"    - {len(df_clean)} villes")
    print(f"    - {df_clean['country'].nunique()} pays")
    if 'population' in df_clean.columns:
        print(f"    - Population totale: {df_clean['population'].sum():,.0f}")
        print(f"    - Catégories: {df_clean['city_category'].value_counts().to_dict()}")

    return df_clean

def aggregate_by_country(df):
    """
    Agrège les données au niveau pays (pour correspondre à World Bank).
    """
    print("\nAgrégation au niveau pays...")

    if 'population' not in df.columns:
        print("  Colonne population manquante, agrégation limitée")
        agg_df = df.groupby(['country', 'country_code_iso2', 'country_code_iso3']).agg(
            nb_villes=('city', 'count')
        ).reset_index()
    else:
        agg_df = df.groupby(['country', 'country_code_iso2', 'country_code_iso3']).agg(
            nb_villes=('city', 'count'),
            population_urbaine_totale=('population', 'sum'),
            population_ville_max=('population', 'max'),
            population_ville_moyenne=('population', 'mean'),
            latitude_moyenne=('latitude', 'mean'),
            longitude_moyenne=('longitude', 'mean')
        ).reset_index()

    print(f"  {len(agg_df)} pays agrégés")
    return agg_df

def main():
    """
    Fonction principale.
    """
    print("=" * 60)
    print("EXTRACTION WORLD CITIES DATABASE")
    print("=" * 60)

    # Télécharger depuis le site
    df = download_world_cities()

    if df is None:
        print("\nÉchec du téléchargement. Aucune donnée disponible.")
        return

    # Sauvegarder les données brutes
    raw_path = DATA_RAW / "world_cities_raw.csv"
    df.to_csv(raw_path, index=False)
    print(f"\nDonnées brutes sauvegardées: {raw_path}")

    # Nettoyer
    df_clean = clean_world_cities(df)

    # Sauvegarder les données nettoyées
    clean_path = DATA_RAW / "world_cities_clean.csv"
    df_clean.to_csv(clean_path, index=False)
    print(f"\nDonnées nettoyées sauvegardées: {clean_path}")

    # Agréger par pays
    df_country = aggregate_by_country(df_clean)

    # Sauvegarder l'agrégation
    country_path = DATA_RAW / "world_cities_by_country.csv"
    df_country.to_csv(country_path, index=False)
    print(f"\nAgrégation par pays sauvegardée: {country_path}")

    print("\n" + "=" * 60)
    print("EXTRACTION TERMINÉE")
    print("=" * 60)

if __name__ == "__main__":
    main()
