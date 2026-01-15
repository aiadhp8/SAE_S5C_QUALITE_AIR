"""
Script 00 - Fusion complète des données
========================================
Fusionne OpenAQ + World Cities + World Bank en une base unique pour analyse.
"""

import sys
sys.path.append(str(__file__).rsplit('scripts', 1)[0])

import pandas as pd
import numpy as np
from config import DATA_RAW, DATA_CLEANED

def load_openaq():
    """Charge les données OpenAQ."""
    print("Chargement OpenAQ...")
    df = pd.read_csv(DATA_RAW / "openaq_country_averages.csv")

    # Pivoter pour avoir un polluant par colonne
    df_pivot = df.pivot_table(
        index=['country_code', 'country_name'],
        columns='parameter',
        values='average',
        aggfunc='mean'
    ).reset_index()

    # Renommer les colonnes
    df_pivot.columns = ['country_code', 'country_name'] + [f'pollution_{c}' for c in df_pivot.columns[2:]]

    print(f"  {len(df_pivot)} pays avec données pollution")
    return df_pivot

def load_world_cities():
    """Charge les données World Cities agrégées par pays."""
    print("Chargement World Cities...")
    df = pd.read_csv(DATA_RAW / "world_cities_by_country.csv")
    print(f"  {len(df)} pays")
    return df

def load_worldbank():
    """Charge et fusionne toutes les données World Bank."""
    print("Chargement World Bank...")

    files = {
        'transport': DATA_RAW / "worldbank_transport.csv",
        'economie': DATA_RAW / "worldbank_economie.csv",
        'demographie': DATA_RAW / "worldbank_demographie.csv",
        'energie': DATA_RAW / "worldbank_energie.csv",
        'sante': DATA_RAW / "worldbank_sante.csv"
    }

    all_data = []
    for name, path in files.items():
        if path.exists():
            df = pd.read_csv(path)
            all_data.append(df)
            print(f"  {name}: {len(df)} lignes")

    if not all_data:
        return None

    # Combiner tous les fichiers
    df_all = pd.concat(all_data, ignore_index=True)

    # Prendre l'année la plus récente pour chaque indicateur/pays
    df_recent = df_all.sort_values('year', ascending=False).drop_duplicates(
        subset=['economy', 'indicator_code'], keep='first'
    )

    # Pivoter pour avoir un indicateur par colonne
    df_pivot = df_recent.pivot_table(
        index='economy',
        columns='indicator_code',
        values='value',
        aggfunc='first'
    ).reset_index()

    df_pivot = df_pivot.rename(columns={'economy': 'country_code'})

    print(f"  {len(df_pivot)} pays, {len(df_pivot.columns)-1} indicateurs")
    return df_pivot

def merge_all_data(df_openaq, df_cities, df_worldbank):
    """Fusionne toutes les sources de données."""
    print("\nFusion des données...")

    # Standardiser les codes pays
    df_openaq['country_code'] = df_openaq['country_code'].str.upper()
    df_cities['country_code_iso2'] = df_cities['country_code_iso2'].str.upper()
    df_cities['country_code_iso3'] = df_cities['country_code_iso3'].str.upper()
    df_worldbank['country_code'] = df_worldbank['country_code'].str.upper()

    # Fusion 1: OpenAQ + World Cities (pour obtenir la correspondance ISO2 -> ISO3)
    df = pd.merge(
        df_openaq,
        df_cities,
        left_on='country_code',
        right_on='country_code_iso2',
        how='left'
    )

    # Fusion 2: + World Bank (via ISO3, car World Bank utilise des codes ISO3!)
    # IMPORTANT: World Bank utilise des codes ISO3 (FRA, USA, DEU...)
    # alors qu'OpenAQ utilise ISO2 (FR, US, DE...)
    df = pd.merge(
        df,
        df_worldbank,
        left_on='country_code_iso3',  # Code ISO3 de World Cities
        right_on='country_code',      # Code ISO3 de World Bank
        how='left',
        suffixes=('', '_wb')
    )

    print(f"  {len(df)} pays dans la base fusionnée")

    # Nettoyer les colonnes en double
    cols_to_drop = [c for c in df.columns if c.endswith('_x') or c.endswith('_y') or c.endswith('_wb')]
    cols_to_drop += ['country_code_iso2', 'country_code_wb']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

    return df

def add_derived_variables(df):
    """Ajoute des variables dérivées utiles."""
    print("\nAjout de variables dérivées...")

    # Indice de qualité de l'air global (moyenne des polluants normalisés)
    pollution_cols = [c for c in df.columns if c.startswith('pollution_')]
    if pollution_cols:
        # Normaliser chaque polluant (0-1)
        for col in pollution_cols:
            if df[col].notna().sum() > 0:
                df[f'{col}_norm'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

        norm_cols = [c for c in df.columns if c.endswith('_norm')]
        df['indice_pollution_global'] = df[norm_cols].mean(axis=1)

    # Catégories de pays par PIB
    if 'NY.GDP.PCAP.CD' in df.columns:
        df['categorie_revenu'] = pd.cut(
            df['NY.GDP.PCAP.CD'],
            bins=[0, 1045, 4095, 12695, float('inf')],
            labels=['Faible', 'Moyen-inférieur', 'Moyen-supérieur', 'Élevé']
        )

    # Catégories par taille de population urbaine
    if 'SP.URB.TOTL' in df.columns:
        valid_data = df['SP.URB.TOTL'].dropna()
        if len(valid_data) >= 4:
            try:
                df['categorie_pop_urbaine'] = pd.qcut(
                    valid_data,
                    q=4,
                    labels=['Petite', 'Moyenne', 'Grande', 'Très grande'],
                    duplicates='drop'
                ).reindex(df.index)
            except ValueError:
                print("  Note: Impossible de créer les catégories de population urbaine")

    return df

def compute_statistics(df):
    """Calcule des statistiques descriptives."""
    print("\n" + "=" * 60)
    print("STATISTIQUES DE LA BASE FUSIONNÉE")
    print("=" * 60)

    print(f"\nNombre de pays: {len(df)}")
    print(f"Nombre de variables: {len(df.columns)}")

    # Statistiques pollution
    pollution_cols = [c for c in df.columns if c.startswith('pollution_') and not c.endswith('_norm')]
    if pollution_cols:
        print("\n--- Pollution (moyennes) ---")
        for col in pollution_cols:
            polluant = col.replace('pollution_', '').upper()
            moy = df[col].mean()
            med = df[col].median()
            print(f"  {polluant}: moyenne={moy:.2f}, médiane={med:.2f}, N={df[col].notna().sum()}")

    # Couverture des données
    print("\n--- Couverture des données ---")
    cols_importantes = ['pollution_pm25', 'pollution_no2', 'NY.GDP.PCAP.CD',
                        'SP.URB.TOTL.IN.ZS', 'NV.IND.TOTL.ZS', 'IS.VEH.NVEH.P3']
    for col in cols_importantes:
        if col in df.columns:
            n = df[col].notna().sum()
            pct = n / len(df) * 100
            print(f"  {col}: {n} pays ({pct:.0f}%)")

    return df

def main():
    print("=" * 60)
    print("FUSION COMPLÈTE DES DONNÉES")
    print("=" * 60)

    # Charger les données
    df_openaq = load_openaq()
    df_cities = load_world_cities()
    df_worldbank = load_worldbank()

    if df_openaq is None:
        print("ERREUR: Données OpenAQ manquantes")
        return

    # Fusionner
    df = merge_all_data(df_openaq, df_cities, df_worldbank)

    # Ajouter variables dérivées
    df = add_derived_variables(df)

    # Statistiques
    df = compute_statistics(df)

    # Sauvegarder
    output_path = DATA_CLEANED / "base_analyse_complete.csv"
    df.to_csv(output_path, index=False)
    print(f"\n\nBase sauvegardée: {output_path}")

    # Sauvegarder aussi une version avec les colonnes renommées en français
    rename_map = {
        'country_code': 'code_pays',
        'country_name': 'nom_pays',
        'country': 'pays',
        'pollution_pm25': 'pm25',
        'pollution_pm10': 'pm10',
        'pollution_no2': 'no2',
        'pollution_o3': 'o3',
        'pollution_so2': 'so2',
        'pollution_co': 'co',
        'NY.GDP.PCAP.CD': 'pib_habitant',
        'NY.GDP.PCAP.PP.CD': 'pib_habitant_ppa',
        'SP.URB.TOTL.IN.ZS': 'pct_urbain',
        'SP.POP.TOTL': 'population',
        'NV.IND.TOTL.ZS': 'pct_industrie',
        'IS.VEH.NVEH.P3': 'vehicules_1000hab',
        'EN.ATM.CO2E.PC': 'co2_habitant',
        'EG.USE.PCAP.KG.OE': 'energie_habitant',
        'nb_villes': 'nb_villes',
        'population_urbaine_totale': 'pop_urbaine_totale'
    }

    df_fr = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df_fr.to_csv(DATA_CLEANED / "base_analyse_fr.csv", index=False)
    print(f"Version FR: {DATA_CLEANED / 'base_analyse_fr.csv'}")

    print("\n" + "=" * 60)
    print("FUSION TERMINÉE")
    print("=" * 60)

    return df

if __name__ == "__main__":
    main()
