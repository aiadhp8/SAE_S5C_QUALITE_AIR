"""
Extracteur de données World Bank
=================================
Ce module extrait les données réelles depuis l'API World Bank
pour tous les axes du projet (transport, énergie, économie, démographie, santé).

Utilise l'API wbgapi pour récupérer les indicateurs officiels.
"""

import sys
from pathlib import Path

# Ajout du chemin projet pour imports
sys.path.append(str(Path(__file__).parent.parent.parent))

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

try:
    import wbgapi as wb
    WBGAPI_AVAILABLE = True
except ImportError:
    print("ATTENTION: wbgapi non installé. Installez-le avec: pip install wbgapi")
    WBGAPI_AVAILABLE = False
    wb = None

from config import (
    DATA_RAW,
    ANNEES_ANALYSE,
    AXE_TRANSPORT,
    AXE_ENERGIE,
    AXE_ECONOMIE_INDUSTRIE,
    AXE_DEMOGRAPHIE_URBANISATION,
    AXE_SANTE_ENVIRONNEMENT
)

# =============================================================================
# CONFIGURATION DES AXES ET INDICATEURS
# =============================================================================

AXES_CONFIG = {
    "transport": AXE_TRANSPORT,
    "energie": AXE_ENERGIE,
    "economie": AXE_ECONOMIE_INDUSTRIE,
    "demographie": AXE_DEMOGRAPHIE_URBANISATION,
    "sante": AXE_SANTE_ENVIRONNEMENT,
}

# =============================================================================
# EXTRACTION DEPUIS L'API WORLD BANK
# =============================================================================

def extract_indicator(indicator_code, indicator_name, years):
    """
    Extrait un indicateur spécifique depuis l'API World Bank.

    Args:
        indicator_code: Code de l'indicateur World Bank (ex: "NY.GDP.PCAP.CD")
        indicator_name: Nom descriptif de l'indicateur
        years: Liste des années à extraire

    Returns:
        DataFrame avec les données ou None si erreur
    """
    if not WBGAPI_AVAILABLE:
        return None

    try:
        # Récupération des données via wbgapi
        data = wb.data.DataFrame(
            indicator_code,
            time=range(min(years), max(years) + 1),
            labels=False  # Utiliser les codes pays
        )

        if data.empty:
            return None

        # Réorganisation des données
        data = data.reset_index()

        # Le format de wbgapi retourne un DataFrame avec les pays en index
        # et les années en colonnes (YR2018, YR2019, etc.)
        data_melted = data.melt(
            id_vars=['economy'],
            var_name='year',
            value_name='value'
        )

        # Nettoyage des années (YR2018 -> 2018)
        data_melted['year'] = data_melted['year'].str.replace('YR', '').astype(int)

        # Ajout des métadonnées
        data_melted['indicator_code'] = indicator_code
        data_melted['indicator_name'] = indicator_name

        # Suppression des valeurs manquantes
        data_melted = data_melted.dropna(subset=['value'])

        return data_melted

    except Exception as e:
        print(f"    Erreur extraction {indicator_code}: {e}")
        return None


def extract_axe_data(axe_name, indicators_dict):
    """
    Extrait toutes les données pour un axe donné.

    Args:
        axe_name: Nom de l'axe (transport, energie, etc.)
        indicators_dict: Dictionnaire {code_indicateur: nom_indicateur}

    Returns:
        DataFrame avec toutes les données de l'axe
    """
    print(f"\n{'='*60}")
    print(f"EXTRACTION AXE: {axe_name.upper()}")
    print(f"{'='*60}")
    print(f"Indicateurs à extraire: {len(indicators_dict)}")
    print(f"Années: {min(ANNEES_ANALYSE)} - {max(ANNEES_ANALYSE)}")

    all_data = []
    success_count = 0

    for indicator_code, indicator_name in indicators_dict.items():
        print(f"\n  [{indicator_code}] {indicator_name}...")

        df = extract_indicator(indicator_code, indicator_name, ANNEES_ANALYSE)

        if df is not None and len(df) > 0:
            all_data.append(df)
            print(f"    -> {len(df)} enregistrements")
            success_count += 1
        else:
            print(f"    -> Aucune donnée disponible")

    if not all_data:
        print(f"\nAUCUNE DONNÉE extraite pour l'axe {axe_name}")
        return None

    # Concaténation de tous les indicateurs
    df_final = pd.concat(all_data, ignore_index=True)

    print(f"\n{'-'*40}")
    print(f"Résumé {axe_name}:")
    print(f"  - Indicateurs réussis: {success_count}/{len(indicators_dict)}")
    print(f"  - Total enregistrements: {len(df_final)}")
    print(f"  - Pays couverts: {df_final['economy'].nunique()}")

    return df_final


def save_worldbank_data(output_dir):
    """
    Extrait et sauvegarde toutes les données World Bank pour tous les axes.

    Args:
        output_dir: Répertoire de sortie pour les fichiers CSV

    Returns:
        True si succès, False sinon
    """
    if not WBGAPI_AVAILABLE:
        print("ERREUR: wbgapi non disponible")
        print("Installez-le avec: pip install wbgapi")
        return False

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*70)
    print("   EXTRACTION DES DONNÉES WORLD BANK")
    print("="*70)
    print(f"Répertoire de sortie: {output_dir}")

    results = {}

    for axe_name, indicators in AXES_CONFIG.items():
        df = extract_axe_data(axe_name, indicators)

        if df is not None and len(df) > 0:
            # Sauvegarde du fichier CSV
            output_path = output_dir / f"worldbank_{axe_name}.csv"
            df.to_csv(output_path, index=False)
            print(f"\n  Sauvegardé: {output_path.name} ({len(df)} lignes)")
            results[axe_name] = len(df)
        else:
            results[axe_name] = 0

    # Résumé final
    print("\n" + "="*70)
    print("   RÉSUMÉ DE L'EXTRACTION")
    print("="*70)

    total = 0
    for axe_name, count in results.items():
        status = "OK" if count > 0 else "ÉCHEC"
        print(f"  {axe_name:15} : {count:6} enregistrements [{status}]")
        total += count

    print(f"\n  TOTAL: {total} enregistrements")

    return total > 0


# =============================================================================
# FONCTION LEGACY POUR COMPATIBILITÉ
# =============================================================================

def save_demo_data(output_dir):
    """
    Fonction de compatibilité - appelle save_worldbank_data.
    Renommée pour indiquer que ce sont de vraies données.
    """
    return save_worldbank_data(output_dir)


# =============================================================================
# GÉNÉRATEURS INDIVIDUELS POUR COMPATIBILITÉ
# =============================================================================

def generate_transport_data():
    """Extrait les données transport depuis World Bank."""
    return extract_axe_data("transport", AXE_TRANSPORT)


def generate_energie_data():
    """Extrait les données énergie depuis World Bank."""
    return extract_axe_data("energie", AXE_ENERGIE)


def generate_economie_data():
    """Extrait les données économie depuis World Bank."""
    return extract_axe_data("economie", AXE_ECONOMIE_INDUSTRIE)


def generate_demographie_data():
    """Extrait les données démographie depuis World Bank."""
    return extract_axe_data("demographie", AXE_DEMOGRAPHIE_URBANISATION)


def generate_sante_data():
    """Extrait les données santé depuis World Bank."""
    return extract_axe_data("sante", AXE_SANTE_ENVIRONNEMENT)


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

if __name__ == "__main__":
    print("Extraction des données World Bank...")
    print("(Cela peut prendre quelques minutes selon la connexion)")

    success = save_worldbank_data(DATA_RAW)

    if success:
        print("\nExtraction terminée avec succès!")
    else:
        print("\nExtraction échouée. Vérifiez votre connexion internet et l'installation de wbgapi.")
