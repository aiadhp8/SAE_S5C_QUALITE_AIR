"""
AXE TRANSPORT - Pipeline Complet
=================================
MEMBRE RESPONSABLE: [Membre A - À assigner]

Ce script gère l'axe TRANSPORT de bout en bout:
1. Extraction des indicateurs World Bank liés au transport
2. Nettoyage et traitement
3. Analyse et corrélations avec la pollution
4. Génération des visualisations

Indicateurs traités:
- Véhicules pour 1000 habitants
- Réseau routier
- Transport aérien
- Transport ferroviaire
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
    AXE_TRANSPORT, ANNEES_ANALYSE, ANNEE_REFERENCE, get_label
)

# =============================================================================
# CONFIGURATION DE L'AXE
# =============================================================================
AXE_NOM = "transport"
INDICATEURS = AXE_TRANSPORT

# =============================================================================
# ÉTAPE 1: EXTRACTION
# =============================================================================

def extract_world_bank_data(force_download=False):
    """
    Extrait les indicateurs World Bank pour l'axe transport.
    Utilise les données pré-générées ou l'API World Bank.
    """
    print("=" * 60)
    print(f"EXTRACTION AXE {AXE_NOM.upper()}")
    print("=" * 60)

    # Vérifier si les données existent déjà
    existing_path = DATA_RAW / f"worldbank_{AXE_NOM}.csv"
    need_download = force_download

    if existing_path.exists() and not force_download:
        print(f"  Chargement données existantes: {existing_path}")
        df = pd.read_csv(existing_path)
        print(f"  {len(df)} enregistrements chargés")

        # Vérifier si tous les indicateurs configurés sont présents
        existing_indicators = set(df['indicator_code'].unique())
        configured_indicators = set(INDICATEURS.keys())
        missing = configured_indicators - existing_indicators

        if missing:
            print(f"  ATTENTION: {len(missing)} indicateurs manquants: {missing}")
            print(f"  Téléchargement des données complètes...")
            need_download = True
        else:
            return df
    else:
        need_download = True

    # Télécharger via l'API
    if wb is None:
        print("ERREUR: wbgapi non installé. Installez-le avec: pip install wbgapi")
        if existing_path.exists():
            print("  Utilisation des données partielles existantes")
            return pd.read_csv(existing_path)
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

    # Sauvegarder
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

    # 1. Supprimer les valeurs manquantes
    df_clean = df.dropna(subset=['value'])
    print(f"  Après suppression NaN: {len(df_clean)} lignes")

    # 2. Filtrer les années d'intérêt
    df_clean = df_clean[df_clean['year'].isin(ANNEES_ANALYSE)]
    print(f"  Après filtre années: {len(df_clean)} lignes")

    # 3. Supprimer les valeurs aberrantes (> 3 écarts-types)
    def remove_outliers(group):
        if len(group) < 5:
            return group
        z_scores = np.abs(stats.zscore(group['value'], nan_policy='omit'))
        return group[z_scores < 3]

    df_clean = df_clean.groupby('indicator_code', group_keys=False).apply(remove_outliers)
    print(f"  Après suppression outliers: {len(df_clean)} lignes")

    # 4. Pivoter pour avoir un indicateur par colonne
    df_pivot = df_clean.pivot_table(
        index=['economy', 'year'],
        columns='indicator_code',
        values='value',
        aggfunc='mean'
    ).reset_index()

    # Renommer les colonnes avec le nom de l'indicateur
    rename_map = {code: f"transport_{code.replace('.', '_')}" for code in INDICATEURS.keys()}
    df_pivot = df_pivot.rename(columns=rename_map)

    print(f"\nDonnées pivotées: {len(df_pivot)} lignes, {len(df_pivot.columns)} colonnes")

    # 5. Créer une version avec moyenne par pays (toutes années)
    numeric_cols = df_pivot.select_dtypes(include=[np.number]).columns.tolist()
    if 'year' in numeric_cols:
        numeric_cols.remove('year')

    df_mean = df_pivot.groupby('economy')[numeric_cols].mean().reset_index()
    print(f"Moyennes par pays: {len(df_mean)} pays")

    # Sauvegarder
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

    # Charger la base commune
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

    # Supprimer la colonne dupliquée
    if 'economy' in df_merged.columns:
        df_merged = df_merged.drop(columns=['economy'])

    print(f"Après fusion: {len(df_merged)} pays")

    # Sauvegarder
    output_path = DATA_FINAL / f"base_{AXE_NOM}.csv"
    df_merged.to_csv(output_path, index=False)
    print(f"Sauvegardé: {output_path}")

    return df_merged

# =============================================================================
# ÉTAPE 4: ANALYSE
# =============================================================================

def analyze_correlations(df):
    """
    Analyse les corrélations entre transport et pollution.
    """
    print("\n" + "=" * 60)
    print("ANALYSE DES CORRÉLATIONS")
    print("=" * 60)

    # Identifier les colonnes
    pollution_cols = [c for c in df.columns if c.startswith('pollution_')]
    transport_cols = [c for c in df.columns if c.startswith('transport_')]

    print(f"Colonnes pollution: {pollution_cols}")
    print(f"Colonnes transport: {transport_cols}")

    if not pollution_cols or not transport_cols:
        print("Données insuffisantes pour l'analyse")
        return None

    # Calculer la matrice de corrélation
    cols_analyse = pollution_cols + transport_cols
    df_analyse = df[cols_analyse].dropna()

    if len(df_analyse) < 10:
        print(f"Trop peu de données: {len(df_analyse)} lignes")
        return None

    print(f"\nAnalyse sur {len(df_analyse)} pays avec données complètes")

    # Corrélations
    correlations = df_analyse.corr()

    # Extraire les corrélations transport-pollution
    results = []
    for t_col in transport_cols:
        for p_col in pollution_cols:
            corr = correlations.loc[t_col, p_col]
            # Test de significativité
            n = df_analyse[[t_col, p_col]].dropna().shape[0]
            if n > 3:
                t_stat = corr * np.sqrt(n - 2) / np.sqrt(1 - corr**2)
                p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))
            else:
                p_value = 1.0

            results.append({
                'indicateur_transport': t_col.replace('transport_', ''),
                'polluant': p_col.replace('pollution_', ''),
                'correlation': corr,
                'p_value': p_value,
                'significatif': p_value < 0.05,
                'n_observations': n
            })

    df_results = pd.DataFrame(results)

    # Afficher les résultats
    print("\n" + "-" * 40)
    print("CORRÉLATIONS SIGNIFICATIVES (p < 0.05):")
    print("-" * 40)

    df_signif = df_results[df_results['significatif']].sort_values('correlation', key=abs, ascending=False)

    if len(df_signif) > 0:
        for _, row in df_signif.iterrows():
            signe = "+" if row['correlation'] > 0 else "-"
            print(f"  {row['indicateur_transport']} <-> {row['polluant']}: "
                  f"r={row['correlation']:.3f} ({signe}) p={row['p_value']:.4f}")
    else:
        print("  Aucune corrélation significative trouvée")

    # Sauvegarder les résultats
    output_path = REPORTS_DIR / f"correlations_{AXE_NOM}.csv"
    df_results.to_csv(output_path, index=False)
    print(f"\nRésultats sauvegardés: {output_path}")

    return df_results, correlations

# =============================================================================
# ÉTAPE 5: VISUALISATION
# =============================================================================

def create_visualizations(df, correlations):
    """
    Crée les visualisations pour l'axe transport.
    """
    print("\n" + "=" * 60)
    print("CRÉATION DES VISUALISATIONS")
    print("=" * 60)

    # Identifier les colonnes
    pollution_cols = [c for c in df.columns if c.startswith('pollution_')]
    transport_cols = [c for c in df.columns if c.startswith('transport_')]

    if not pollution_cols or not transport_cols:
        print("Données insuffisantes pour les visualisations")
        return

    # Créer le dossier des figures
    fig_dir = REPORTS_DIR / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # 1. Heatmap des corrélations
    print("  Création heatmap...")
    plt.figure(figsize=(12, 8))

    # Extraire sous-matrice
    cols_all = pollution_cols + transport_cols
    corr_matrix = df[cols_all].corr()

    # Labels lisibles en français
    labels = [get_label(c) for c in cols_all]

    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt='.2f',
        cmap='RdBu_r',
        center=0,
        xticklabels=labels,
        yticklabels=labels
    )
    plt.title(f'Corrélations Transport - Pollution')
    plt.tight_layout()
    plt.savefig(fig_dir / f"heatmap_{AXE_NOM}.png", dpi=150)
    plt.close()

    # 2. Scatter plots pour les corrélations les plus fortes
    print("  Création scatter plots...")
    if 'pollution_pm25' in df.columns and transport_cols:
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()

        for i, t_col in enumerate(transport_cols[:4]):
            ax = axes[i]
            df_plot = df[['pollution_pm25', t_col, 'nom_pays']].dropna()

            if len(df_plot) > 5:
                ax.scatter(df_plot[t_col], df_plot['pollution_pm25'], alpha=0.6)

                # Ligne de tendance
                z = np.polyfit(df_plot[t_col], df_plot['pollution_pm25'], 1)
                p = np.poly1d(z)
                x_line = np.linspace(df_plot[t_col].min(), df_plot[t_col].max(), 100)
                ax.plot(x_line, p(x_line), "r--", alpha=0.8)

                # Corrélation
                corr = df_plot[['pollution_pm25', t_col]].corr().iloc[0, 1]
                ax.set_xlabel(t_col.replace('transport_', ''))
                ax.set_ylabel('PM2.5 (µg/m³)')
                ax.set_title(f'r = {corr:.3f}')

        plt.suptitle('Relations Transport - PM2.5', fontsize=14)
        plt.tight_layout()
        plt.savefig(fig_dir / f"scatter_{AXE_NOM}.png", dpi=150)
        plt.close()

    # 3. Distribution des indicateurs
    print("  Création distributions...")
    n_cols = len(transport_cols)
    if n_cols > 0:
        fig, axes = plt.subplots((n_cols + 1) // 2, 2, figsize=(12, 3 * ((n_cols + 1) // 2)))
        axes = axes.flatten() if n_cols > 1 else [axes]

        for i, col in enumerate(transport_cols):
            ax = axes[i]
            df[col].dropna().hist(bins=30, ax=ax, edgecolor='black')
            ax.set_title(col.replace('transport_', ''))
            ax.set_xlabel('Valeur')
            ax.set_ylabel('Fréquence')

        # Masquer les axes inutilisés
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)

        plt.suptitle(f'Distribution des Indicateurs Transport', fontsize=14)
        plt.tight_layout()
        plt.savefig(fig_dir / f"distributions_{AXE_NOM}.png", dpi=150)
        plt.close()

    print(f"\nFigures sauvegardées dans: {fig_dir}")

# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================

def run_pipeline():
    """
    Exécute le pipeline complet pour l'axe transport.
    """
    print("\n" + "=" * 70)
    print(f"   PIPELINE COMPLET - AXE {AXE_NOM.upper()}")
    print("=" * 70)

    # Étape 1: Extraction
    df_raw = extract_world_bank_data()

    # Étape 2: Nettoyage
    df_clean = clean_data(df_raw)

    if df_clean is None:
        print("\nPIPELINE INTERROMPU: Données manquantes")
        return

    # Étape 3: Fusion
    df_merged = merge_with_base_commune(df_clean)

    if df_merged is None:
        print("\nPIPELINE INTERROMPU: Fusion impossible")
        return

    # Étape 4: Analyse
    results = analyze_correlations(df_merged)

    if results:
        df_results, correlations = results

        # Étape 5: Visualisation
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
