"""
AXE SANTÉ/ENVIRONNEMENT - Pipeline Complet
===========================================
MEMBRE RESPONSABLE: [Membre E - À assigner]

Ce script gère l'axe SANTÉ/ENVIRONNEMENT de bout en bout:
1. Extraction des indicateurs World Bank liés à la santé
2. Nettoyage et traitement
3. Analyse et corrélations avec la pollution
4. Génération des visualisations

Indicateurs traités:
- Exposition PM2.5 (données World Bank)
- Décès liés à la pollution
- Espérance de vie
- Dépenses de santé
"""

import sys
sys.path.append(str(__file__).rsplit('scripts', 1)[0])

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

try:
    import wbgapi as wb
except ImportError:
    print("Installez wbgapi: pip install wbgapi")
    wb = None

from config import (
    DATA_RAW, DATA_CLEANED, DATA_FINAL, REPORTS_DIR,
    AXE_SANTE_ENVIRONNEMENT, ANNEES_ANALYSE, ANNEE_REFERENCE, get_label
)

# =============================================================================
# CONFIGURATION DE L'AXE
# =============================================================================
AXE_NOM = "sante"
INDICATEURS = AXE_SANTE_ENVIRONNEMENT

# =============================================================================
# ÉTAPE 1: EXTRACTION
# =============================================================================

def extract_world_bank_data():
    """
    Extrait les indicateurs World Bank pour l'axe santé.
    Utilise les données pré-générées ou l'API World Bank.
    """
    print("=" * 60)
    print(f"EXTRACTION AXE {AXE_NOM.upper()}")
    print("=" * 60)

    existing_path = DATA_RAW / f"worldbank_{AXE_NOM}.csv"
    if existing_path.exists():
        print(f"  Chargement données existantes: {existing_path}")
        df = pd.read_csv(existing_path)
        print(f"  {len(df)} enregistrements chargés")
        return df

    if wb is None:
        print("ERREUR: wbgapi non installé et pas de données locales")
        return None

    all_data = []

    for indicator_code, indicator_name in INDICATEURS.items():
        print(f"\n  Extraction: {indicator_name} ({indicator_code})...")

        try:
            data = wb.data.DataFrame(
                indicator_code,
                time=range(min(ANNEES_ANALYSE), max(ANNEES_ANALYSE) + 1),
                labels=True
            )

            if data.empty:
                print(f"    Aucune donnée disponible")
                continue

            data = data.reset_index()
            data_melted = data.melt(
                id_vars=['economy'],
                var_name='year',
                value_name='value'
            )
            data_melted['indicator_code'] = indicator_code
            data_melted['indicator_name'] = indicator_name
            data_melted['year'] = data_melted['year'].str.replace('YR', '').astype(int)

            all_data.append(data_melted)
            print(f"    {len(data_melted)} enregistrements")

        except Exception as e:
            print(f"    Erreur: {e}")

    if not all_data:
        print("\nAucune donnée extraite!")
        return None

    df = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal: {len(df)} enregistrements")

    output_path = DATA_RAW / f"worldbank_{AXE_NOM}.csv"
    df.to_csv(output_path, index=False)
    print(f"Sauvegardé: {output_path}")

    return df

# =============================================================================
# ÉTAPE 2: NETTOYAGE
# =============================================================================

def clean_data(df):
    """
    Nettoie les données World Bank.
    """
    print("\n" + "=" * 60)
    print("NETTOYAGE DES DONNÉES")
    print("=" * 60)

    if df is None:
        print("Chargement depuis fichier...")
        path = DATA_RAW / f"worldbank_{AXE_NOM}.csv"
        if not path.exists():
            print(f"ERREUR: {path} n'existe pas")
            return None
        df = pd.read_csv(path)

    print(f"Données initiales: {len(df)} lignes")

    df_clean = df.dropna(subset=['value'])
    print(f"  Après suppression NaN: {len(df_clean)} lignes")

    df_clean = df_clean[df_clean['year'].isin(ANNEES_ANALYSE)]
    print(f"  Après filtre années: {len(df_clean)} lignes")

    def remove_outliers(group):
        if len(group) < 5:
            return group
        z_scores = np.abs(stats.zscore(group['value'], nan_policy='omit'))
        return group[z_scores < 3]

    df_clean = df_clean.groupby('indicator_code', group_keys=False).apply(remove_outliers)
    print(f"  Après suppression outliers: {len(df_clean)} lignes")

    df_pivot = df_clean.pivot_table(
        index=['economy', 'year'],
        columns='indicator_code',
        values='value',
        aggfunc='mean'
    ).reset_index()

    rename_map = {code: f"sante_{code.replace('.', '_')}" for code in INDICATEURS.keys()}
    df_pivot = df_pivot.rename(columns=rename_map)

    print(f"\nDonnées pivotées: {len(df_pivot)} lignes, {len(df_pivot.columns)} colonnes")

    numeric_cols = df_pivot.select_dtypes(include=[np.number]).columns.tolist()
    if 'year' in numeric_cols:
        numeric_cols.remove('year')

    df_mean = df_pivot.groupby('economy')[numeric_cols].mean().reset_index()
    print(f"Moyennes par pays: {len(df_mean)} pays")

    output_path = DATA_CLEANED / f"{AXE_NOM}_cleaned.csv"
    df_pivot.to_csv(output_path, index=False)
    print(f"\nSauvegardé: {output_path}")

    output_path_mean = DATA_CLEANED / f"{AXE_NOM}_mean.csv"
    df_mean.to_csv(output_path_mean, index=False)
    print(f"Sauvegardé: {output_path_mean}")

    return df_mean

# =============================================================================
# ÉTAPE 3: FUSION AVEC BASE COMMUNE
# =============================================================================

def merge_with_base_commune(df_axe):
    """
    Fusionne les données de l'axe avec la base commune.
    """
    print("\n" + "=" * 60)
    print("FUSION AVEC BASE COMMUNE")
    print("=" * 60)

    base_path = DATA_CLEANED / "base_commune.csv"
    if not base_path.exists():
        print(f"ERREUR: {base_path} n'existe pas")
        print("Exécutez d'abord: scripts/common/03_base_commune.py")
        return None

    df_base = pd.read_csv(base_path)
    print(f"Base commune: {len(df_base)} pays")

    # Standardiser les codes pays (World Bank utilise ISO3)
    df_axe['economy'] = df_axe['economy'].str.upper()
    df_base['code_pays_iso3'] = df_base['code_pays_iso3'].str.upper()

    # Fusionner sur code_pays_iso3 (ISO3)
    df_merged = pd.merge(
        df_base,
        df_axe,
        left_on='code_pays_iso3',
        right_on='economy',
        how='inner'
    )

    if 'economy' in df_merged.columns:
        df_merged = df_merged.drop(columns=['economy'])

    print(f"Après fusion: {len(df_merged)} pays")

    output_path = DATA_FINAL / f"base_{AXE_NOM}.csv"
    df_merged.to_csv(output_path, index=False)
    print(f"Sauvegardé: {output_path}")

    return df_merged

# =============================================================================
# ÉTAPE 4: ANALYSE
# =============================================================================

def analyze_correlations(df):
    """
    Analyse les corrélations entre santé et pollution.
    """
    print("\n" + "=" * 60)
    print("ANALYSE DES CORRÉLATIONS")
    print("=" * 60)

    pollution_cols = [c for c in df.columns if c.startswith('pollution_')]
    sante_cols = [c for c in df.columns if c.startswith('sante_')]

    print(f"Colonnes pollution: {pollution_cols}")
    print(f"Colonnes santé: {sante_cols}")

    if not pollution_cols or not sante_cols:
        print("Données insuffisantes pour l'analyse")
        return None

    cols_analyse = pollution_cols + sante_cols
    df_analyse = df[cols_analyse].dropna()

    if len(df_analyse) < 10:
        print(f"Trop peu de données: {len(df_analyse)} lignes")
        return None

    print(f"\nAnalyse sur {len(df_analyse)} pays avec données complètes")

    correlations = df_analyse.corr()

    results = []
    for s_col in sante_cols:
        for p_col in pollution_cols:
            corr = correlations.loc[s_col, p_col]
            n = df_analyse[[s_col, p_col]].dropna().shape[0]
            if n > 3:
                t_stat = corr * np.sqrt(n - 2) / np.sqrt(1 - corr**2)
                p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
            else:
                p_value = 1.0

            results.append({
                'indicateur_sante': s_col.replace('sante_', ''),
                'polluant': p_col.replace('pollution_', ''),
                'correlation': corr,
                'p_value': p_value,
                'significatif': p_value < 0.05,
                'n_observations': n
            })

    df_results = pd.DataFrame(results)

    print("\n" + "-" * 40)
    print("CORRÉLATIONS SIGNIFICATIVES (p < 0.05):")
    print("-" * 40)

    df_signif = df_results[df_results['significatif']].sort_values('correlation', key=abs, ascending=False)

    if len(df_signif) > 0:
        for _, row in df_signif.iterrows():
            signe = "+" if row['correlation'] > 0 else "-"
            print(f"  {row['indicateur_sante']} <-> {row['polluant']}: "
                  f"r={row['correlation']:.3f} ({signe}) p={row['p_value']:.4f}")
    else:
        print("  Aucune corrélation significative trouvée")

    output_path = REPORTS_DIR / f"correlations_{AXE_NOM}.csv"
    df_results.to_csv(output_path, index=False)
    print(f"\nRésultats sauvegardés: {output_path}")

    return df_results, correlations

# =============================================================================
# ÉTAPE 5: VISUALISATION
# =============================================================================

def create_visualizations(df, correlations):
    """
    Crée les visualisations pour l'axe santé.
    """
    print("\n" + "=" * 60)
    print("CRÉATION DES VISUALISATIONS")
    print("=" * 60)

    pollution_cols = [c for c in df.columns if c.startswith('pollution_')]
    sante_cols = [c for c in df.columns if c.startswith('sante_')]

    if not pollution_cols or not sante_cols:
        print("Données insuffisantes pour les visualisations")
        return

    fig_dir = REPORTS_DIR / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # 1. Heatmap des corrélations
    print("  Création heatmap...")
    plt.figure(figsize=(12, 8))

    cols_all = pollution_cols + sante_cols
    corr_matrix = df[cols_all].corr()

    labels = [get_label(c) for c in cols_all]

    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt='.2f',
        cmap='RdBu_r',
        center=0,
        xticklabels=labels,
        yticklabels=labels,
        annot_kws={'size': 9}
    )
    plt.title(f'Corrélations Santé - Pollution')
    plt.tight_layout()
    plt.savefig(fig_dir / f"heatmap_{AXE_NOM}.png", dpi=150)
    plt.close()

    # 2. Espérance de vie vs pollution
    print("  Création analyse espérance de vie...")
    life_cols = [c for c in sante_cols if 'LE00' in c or 'life' in c.lower()]

    if life_cols and 'pollution_pm25' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))

        life_col = life_cols[0]
        df_plot = df[['pollution_pm25', life_col, 'nom_pays']].dropna()

        if len(df_plot) > 5:
            ax.scatter(df_plot['pollution_pm25'], df_plot[life_col], alpha=0.6)

            z = np.polyfit(df_plot['pollution_pm25'], df_plot[life_col], 1)
            p = np.poly1d(z)
            x_line = np.linspace(df_plot['pollution_pm25'].min(), df_plot['pollution_pm25'].max(), 100)
            ax.plot(x_line, p(x_line), "r--", alpha=0.8)

            corr = df_plot[['pollution_pm25', life_col]].corr().iloc[0, 1]
            ax.set_xlabel('PM2.5 (µg/m³)')
            ax.set_ylabel('Espérance de vie (années)')
            ax.set_title(f'Pollution vs Espérance de vie (r = {corr:.3f})')

        plt.tight_layout()
        plt.savefig(fig_dir / f"esperance_vie_{AXE_NOM}.png", dpi=150)
        plt.close()

    # 3. Décès pollution vs niveaux PM2.5
    print("  Création analyse mortalité...")
    death_cols = [c for c in sante_cols if 'AIRP' in c or 'death' in c.lower()]

    if death_cols and 'pollution_pm25' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))

        death_col = death_cols[0]
        df_plot = df[['pollution_pm25', death_col, 'nom_pays']].dropna()

        if len(df_plot) > 5:
            ax.scatter(df_plot['pollution_pm25'], df_plot[death_col], alpha=0.6)

            z = np.polyfit(df_plot['pollution_pm25'], df_plot[death_col], 1)
            p = np.poly1d(z)
            x_line = np.linspace(df_plot['pollution_pm25'].min(), df_plot['pollution_pm25'].max(), 100)
            ax.plot(x_line, p(x_line), "r--", alpha=0.8)

            corr = df_plot[['pollution_pm25', death_col]].corr().iloc[0, 1]
            ax.set_xlabel('PM2.5 (µg/m³)')
            ax.set_ylabel('Décès liés à la pollution (pour 100k)')
            ax.set_title(f'Pollution vs Mortalité (r = {corr:.3f})')

        plt.tight_layout()
        plt.savefig(fig_dir / f"mortalite_{AXE_NOM}.png", dpi=150)
        plt.close()

    # 4. Comparaison PM2.5 OpenAQ vs World Bank
    print("  Création comparaison sources...")
    wb_pm25_cols = [c for c in sante_cols if 'PM25' in c.upper() and 'MC_M3' in c.upper()]

    if wb_pm25_cols and 'pollution_pm25' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))

        wb_col = wb_pm25_cols[0]
        df_plot = df[['pollution_pm25', wb_col, 'nom_pays']].dropna()

        if len(df_plot) > 5:
            ax.scatter(df_plot['pollution_pm25'], df_plot[wb_col], alpha=0.6)

            # Ligne y=x (correspondance parfaite)
            max_val = max(df_plot['pollution_pm25'].max(), df_plot[wb_col].max())
            ax.plot([0, max_val], [0, max_val], 'g--', alpha=0.5, label='y=x')

            corr = df_plot[['pollution_pm25', wb_col]].corr().iloc[0, 1]
            ax.set_xlabel('PM2.5 OpenAQ (µg/m³)')
            ax.set_ylabel('PM2.5 World Bank (µg/m³)')
            ax.set_title(f'Comparaison sources PM2.5 (r = {corr:.3f})')
            ax.legend()

        plt.tight_layout()
        plt.savefig(fig_dir / f"comparaison_sources_{AXE_NOM}.png", dpi=150)
        plt.close()

    print(f"\nFigures sauvegardées dans: {fig_dir}")

# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================

def run_pipeline():
    """
    Exécute le pipeline complet pour l'axe santé.
    """
    print("\n" + "=" * 70)
    print(f"   PIPELINE COMPLET - AXE {AXE_NOM.upper()}")
    print("=" * 70)

    df_raw = extract_world_bank_data()
    df_clean = clean_data(df_raw)

    if df_clean is None:
        print("\nPIPELINE INTERROMPU: Données manquantes")
        return

    df_merged = merge_with_base_commune(df_clean)

    if df_merged is None:
        print("\nPIPELINE INTERROMPU: Fusion impossible")
        return

    results = analyze_correlations(df_merged)

    if results:
        df_results, correlations = results
        create_visualizations(df_merged, correlations)

    print("\n" + "=" * 70)
    print(f"   PIPELINE {AXE_NOM.upper()} TERMINÉ AVEC SUCCÈS")
    print("=" * 70)
    print(f"\nFichiers générés:")
    print(f"  - data/raw/worldbank_{AXE_NOM}.csv")
    print(f"  - data/cleaned/{AXE_NOM}_cleaned.csv")
    print(f"  - data/cleaned/{AXE_NOM}_mean.csv")
    print(f"  - data/final/base_{AXE_NOM}.csv")
    print(f"  - reports/correlations_{AXE_NOM}.csv")
    print(f"  - reports/figures/")

if __name__ == "__main__":
    run_pipeline()
