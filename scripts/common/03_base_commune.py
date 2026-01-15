"""
Script 03 - Construction de la Base Commune
============================================
MEMBRE RESPONSABLE: [Données de Base - À assigner]

Ce script fusionne les données OpenAQ et World Cities pour créer
la base commune que tous les membres utiliseront.

Entrées:
    - data/raw/openaq_country_averages.csv
    - data/raw/world_cities_by_country.csv

Sortie:
    - data/cleaned/base_commune.csv
"""

import sys
sys.path.append(str(__file__).rsplit('scripts', 1)[0])

import pandas as pd
import numpy as np
from config import DATA_RAW, DATA_CLEANED, ANNEE_REFERENCE, POLLUANTS

def load_openaq_data():
    """
    Charge les données OpenAQ agrégées par pays.
    """
    print("Chargement des données OpenAQ...")
    path = DATA_RAW / "openaq_country_averages.csv"

    if not path.exists():
        print(f"  ERREUR: {path} n'existe pas")
        print("  Exécutez d'abord: 01_extract_openaq.py")
        return None

    df = pd.read_csv(path)
    print(f"  {len(df)} enregistrements chargés")
    print(f"  {df['country_code'].nunique()} pays")
    print(f"  Années: {df['year'].min()} - {df['year'].max()}")
    return df

def load_world_cities_data():
    """
    Charge les données World Cities agrégées par pays.
    """
    print("\nChargement des données World Cities...")
    path = DATA_RAW / "world_cities_by_country.csv"

    if not path.exists():
        print(f"  ERREUR: {path} n'existe pas")
        print("  Exécutez d'abord: 02_extract_world_cities.py")
        return None

    df = pd.read_csv(path)
    print(f"  {len(df)} pays chargés")
    return df

def pivot_pollution_data(df_openaq, year=None):
    """
    Pivote les données de pollution pour avoir un polluant par colonne.
    """
    print(f"\nPréparation des données de pollution (année: {year or 'toutes'})...")

    if year:
        df = df_openaq[df_openaq['year'] == year].copy()
    else:
        # Prendre la moyenne sur toutes les années
        df = df_openaq.groupby(['country_code', 'parameter']).agg({
            'average': 'mean',
            'measurement_count': 'sum'
        }).reset_index()

    # Pivoter
    df_pivot = df.pivot_table(
        index='country_code',
        columns='parameter',
        values='average',
        aggfunc='mean'
    ).reset_index()

    # Renommer les colonnes
    df_pivot.columns = ['country_code'] + [f"pollution_{col}" for col in df_pivot.columns[1:]]

    print(f"  {len(df_pivot)} pays avec données de pollution")
    return df_pivot

def merge_data(df_pollution, df_cities):
    """
    Fusionne les données de pollution avec les données des villes.
    """
    print("\nFusion des données...")

    # Standardiser les codes pays
    df_pollution['country_code'] = df_pollution['country_code'].str.upper()
    df_cities['country_code_iso2'] = df_cities['country_code_iso2'].str.upper()

    # Fusionner
    df_merged = pd.merge(
        df_pollution,
        df_cities,
        left_on='country_code',
        right_on='country_code_iso2',
        how='inner'
    )

    print(f"  {len(df_merged)} pays avec données complètes")

    # Afficher les pays sans correspondance
    missing_pollution = set(df_pollution['country_code']) - set(df_merged['country_code'])
    missing_cities = set(df_cities['country_code_iso2']) - set(df_merged['country_code'])

    if missing_pollution:
        print(f"  Pays sans données villes: {len(missing_pollution)}")
    if missing_cities:
        print(f"  Pays sans données pollution: {len(missing_cities)}")

    return df_merged

def clean_merged_data(df):
    """
    Nettoie et finalise la base commune.
    """
    print("\nNettoyage final...")

    # Sélectionner les colonnes pertinentes
    colonnes = [
        'country_code',
        'country',
        'country_code_iso3',
        'nb_villes',
        'population_urbaine_totale',
        'population_ville_max',
        'population_ville_moyenne',
        'latitude_moyenne',
        'longitude_moyenne'
    ]

    # Ajouter les colonnes de pollution existantes
    pollution_cols = [c for c in df.columns if c.startswith('pollution_')]
    colonnes.extend(pollution_cols)

    # Garder uniquement les colonnes existantes
    colonnes = [c for c in colonnes if c in df.columns]
    df_clean = df[colonnes].copy()

    # Renommer pour clarté
    df_clean = df_clean.rename(columns={
        'country_code': 'code_pays',
        'country': 'nom_pays',
        'country_code_iso3': 'code_pays_iso3'
    })

    # Statistiques descriptives
    print("\n  Statistiques de la base commune:")
    print(f"    - {len(df_clean)} pays")
    print(f"    - {len(df_clean.columns)} colonnes")

    if pollution_cols and len(df_clean) > 0:
        pollution_stats = df_clean[pollution_cols].describe()
        print(f"\n  Statistiques pollution:")
        print(pollution_stats.round(2).to_string())
    else:
        print("\n  Aucune donnée de pollution disponible")

    return df_clean

def add_quality_flags(df):
    """
    Ajoute des indicateurs de qualité des données.
    """
    print("\nAjout des indicateurs de qualité...")

    # Compter les valeurs manquantes par polluant
    pollution_cols = [c for c in df.columns if c.startswith('pollution_')]

    df['nb_polluants_disponibles'] = df[pollution_cols].notna().sum(axis=1)
    df['donnees_completes'] = df['nb_polluants_disponibles'] == len(pollution_cols)

    # Qualité globale
    def quality_score(row):
        score = 0
        if row['nb_polluants_disponibles'] >= 3:
            score += 1
        if pd.notna(row.get('population_urbaine_totale', np.nan)):
            score += 1
        if pd.notna(row.get('nb_villes', np.nan)):
            score += 1
        return score

    df['score_qualite'] = df.apply(quality_score, axis=1)

    print(f"  Répartition score qualité: {df['score_qualite'].value_counts().to_dict()}")

    return df

def main():
    """
    Fonction principale.
    """
    print("=" * 60)
    print("CONSTRUCTION DE LA BASE COMMUNE")
    print("=" * 60)

    # Charger les données
    df_openaq = load_openaq_data()
    df_cities = load_world_cities_data()

    if df_openaq is None or df_cities is None:
        print("\nERREUR: Données manquantes. Exécutez d'abord les scripts 01 et 02.")
        return

    # Utiliser l'année la plus récente disponible dans les données
    annee_dispo = df_openaq['year'].max()
    if annee_dispo != ANNEE_REFERENCE:
        print(f"\n  Note: Utilisation de l'année {annee_dispo} (données disponibles)")
        print(f"        au lieu de {ANNEE_REFERENCE} (année de référence config)")

    # Pivoter les données de pollution
    df_pollution = pivot_pollution_data(df_openaq, year=annee_dispo)

    # Fusionner
    df_merged = merge_data(df_pollution, df_cities)

    if len(df_merged) == 0:
        print("\nERREUR: Aucune correspondance entre les données de pollution et les villes.")
        print("Vérifiez que les codes pays correspondent entre les sources.")
        return

    # Nettoyer
    df_clean = clean_merged_data(df_merged)

    # Ajouter les flags de qualité
    df_final = add_quality_flags(df_clean)

    # Sauvegarder
    output_path = DATA_CLEANED / "base_commune.csv"
    df_final.to_csv(output_path, index=False)
    print(f"\n\nBase commune sauvegardée: {output_path}")

    # Créer aussi une version avec toutes les années
    print("\n" + "-" * 40)
    print("Création de la base multi-années...")

    df_pollution_all = pivot_pollution_data(df_openaq, year=None)
    df_merged_all = merge_data(df_pollution_all, df_cities)

    if len(df_merged_all) > 0:
        df_clean_all = clean_merged_data(df_merged_all)
        df_final_all = add_quality_flags(df_clean_all)

        output_path_all = DATA_CLEANED / "base_commune_moyenne.csv"
        df_final_all.to_csv(output_path_all, index=False)
        print(f"Base moyenne sauvegardée: {output_path_all}")
    else:
        print("  Aucune donnée pour la base multi-années")

    print("\n" + "=" * 60)
    print("BASE COMMUNE CRÉÉE AVEC SUCCÈS")
    print("=" * 60)
    print("\nProchaine étape: Chaque membre peut maintenant lancer")
    print("son script d'axe thématique pour ajouter ses indicateurs.")

if __name__ == "__main__":
    main()
