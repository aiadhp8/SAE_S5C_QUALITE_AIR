"""
Analyses Avancées - ACP, Modèles Prédictifs, Analyse Temporelle et Chi2
========================================================================
RESPONSABLE: Chef de projet / Équipe

Ce script effectue les analyses avancées sur la base fusionnée:
1. Analyse Temporelle (évolution 2018-2023)
2. Tests du Chi2 (indépendance entre variables catégorielles)
3. Analyse en Composantes Principales (ACP)
4. Modèles prédictifs (Régression, Arbres de décision)
5. Comparaison des modèles

Entrée:
    - data/final/base_complete.csv
    - data/raw/openaq_country_averages.csv (données multi-années)

Sorties:
    - reports/acp_results.csv
    - reports/models_comparison.csv
    - reports/temporal_analysis.csv
    - reports/chi2_results.csv
    - reports/figures/acp_*.png
    - reports/figures/models_*.png
    - reports/figures/temporal_*.png
    - reports/figures/chi2_*.png
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

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

from config import DATA_FINAL, DATA_RAW, REPORTS_DIR

# =============================================================================
# CHARGEMENT DES DONNÉES
# =============================================================================

def load_data():
    """
    Charge la base complète fusionnée.
    """
    print("=" * 60)
    print("CHARGEMENT DES DONNÉES")
    print("=" * 60)

    path = DATA_FINAL / "base_complete.csv"
    if not path.exists():
        print(f"ERREUR: {path} n'existe pas")
        print("Exécutez d'abord: scripts/fusion/01_fusion_axes.py")
        return None

    df = pd.read_csv(path)
    print(f"Base chargée: {len(df)} pays, {len(df.columns)} colonnes")

    return df

def prepare_data_for_analysis(df, target='pollution_pm25'):
    """
    Prépare les données pour les analyses (suppression NaN, standardisation).
    """
    print(f"\nPréparation des données (cible: {target})...")

    # Colonnes explicatives (tout sauf pollution et identifiants)
    exclude_cols = ['code_pays', 'nom_pays', 'code_pays_iso3'] + \
                   [c for c in df.columns if c.startswith('pollution_')]

    feature_cols = [c for c in df.columns if c not in exclude_cols]

    # Garder uniquement les lignes complètes pour la cible
    df_clean = df.dropna(subset=[target])

    # Pour les features, on peut imputer ou supprimer
    # Ici on supprime les colonnes avec trop de NaN (> 50%)
    valid_features = []
    for col in feature_cols:
        pct_missing = df_clean[col].isna().mean()
        if pct_missing < 0.5:
            valid_features.append(col)

    print(f"  Features valides: {len(valid_features)}/{len(feature_cols)}")

    # Supprimer les lignes avec NaN dans les features valides
    df_analysis = df_clean.dropna(subset=valid_features + [target])
    print(f"  Observations complètes: {len(df_analysis)}")

    X = df_analysis[valid_features]
    y = df_analysis[target]

    return X, y, df_analysis

# =============================================================================
# ANALYSE TEMPORELLE (2018-2023)
# =============================================================================

def run_temporal_analysis():
    """
    Analyse l'évolution temporelle de la pollution (2018-2023).
    Utilise les données multi-années d'OpenAQ.
    """
    print("\n" + "=" * 60)
    print("ANALYSE TEMPORELLE (2018-2023)")
    print("=" * 60)

    # Charger les données OpenAQ multi-années
    openaq_path = DATA_RAW / "openaq_country_averages.csv"
    if not openaq_path.exists():
        print(f"ERREUR: {openaq_path} n'existe pas")
        return None

    df = pd.read_csv(openaq_path)
    print(f"\n  Données chargées: {len(df)} enregistrements")
    print(f"  Années: {sorted(df['year'].unique())}")
    print(f"  Pays: {df['country_code'].nunique()}")
    print(f"  Polluants: {sorted(df['parameter'].unique())}")

    fig_dir = REPORTS_DIR / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    # 1. Évolution globale par polluant
    print("\n  1. Évolution globale par polluant...")

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    polluants = ['pm25', 'pm10', 'no2', 'o3', 'so2', 'co']
    evolution_data = []

    for idx, polluant in enumerate(polluants):
        pol_df = df[df['parameter'] == polluant]

        if pol_df.empty:
            continue

        # Moyenne mondiale par année
        yearly_avg = pol_df.groupby('year').agg({
            'average': 'mean',
            'country_code': 'nunique'
        }).reset_index()
        yearly_avg.columns = ['year', 'moyenne_mondiale', 'nb_pays']

        ax = axes[idx]
        ax.plot(yearly_avg['year'], yearly_avg['moyenne_mondiale'], 'o-', linewidth=2, markersize=8)
        ax.set_title(f'{polluant.upper()}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Année')
        ax.set_ylabel('Concentration moyenne (µg/m³)')
        ax.grid(True, alpha=0.3)

        # Annoter le nombre de pays
        for _, row in yearly_avg.iterrows():
            ax.annotate(f"n={int(row['nb_pays'])}",
                       (row['year'], row['moyenne_mondiale']),
                       textcoords="offset points", xytext=(0, 10),
                       ha='center', fontsize=8, alpha=0.7)

        # Calculer la tendance
        if len(yearly_avg) > 2:
            slope, intercept, r, p, se = stats.linregress(yearly_avg['year'], yearly_avg['moyenne_mondiale'])
            evolution_data.append({
                'polluant': polluant,
                'pente_annuelle': round(slope, 3),
                'variation_pct': round(100 * slope / yearly_avg['moyenne_mondiale'].iloc[0], 2) if yearly_avg['moyenne_mondiale'].iloc[0] > 0 else 0,
                'r2': round(r**2, 3),
                'p_value': round(p, 4),
                'tendance': 'baisse' if slope < 0 else 'hausse',
                'significatif': 'oui' if p < 0.05 else 'non'
            })

    plt.tight_layout()
    plt.savefig(fig_dir / "temporal_evolution_globale.png", dpi=150)
    plt.close()

    results['evolution_globale'] = pd.DataFrame(evolution_data)
    print("\n  Tendances par polluant:")
    for _, row in results['evolution_globale'].iterrows():
        sig = "***" if row['significatif'] == 'oui' else ""
        print(f"    {row['polluant']:6s}: {row['tendance']:6s} ({row['variation_pct']:+.1f}%/an) {sig}")

    # 2. Évolution par région (Europe, Asie, Amériques, Afrique)
    print("\n  2. Évolution par région...")

    regions = {
        'Europe': ['AD', 'AL', 'AT', 'BA', 'BE', 'BG', 'CH', 'CZ', 'DE', 'DK', 'ES', 'FI', 'FR', 'GB', 'GR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LV', 'MK', 'MT', 'NL', 'NO', 'PL', 'PT', 'RO', 'RS', 'SE', 'SI', 'SK', 'XK'],
        'Asie': ['BD', 'CN', 'HK', 'ID', 'IN', 'JP', 'KR', 'MN', 'MY', 'PH', 'SG', 'TH', 'TW', 'VN', 'TJ', 'TM', 'UZ'],
        'Amériques': ['AR', 'BR', 'CA', 'CL', 'CO', 'CR', 'EC', 'MX', 'PE', 'PR', 'US'],
        'Afrique': ['ET', 'GH', 'KE', 'NG', 'RW', 'SD', 'TD', 'UG', 'ZA'],
        'Moyen-Orient': ['AE', 'BH', 'IL', 'KW', 'QA', 'SA', 'TR']
    }

    df['region'] = df['country_code'].apply(
        lambda x: next((r for r, codes in regions.items() if x in codes), 'Autre')
    )

    # Focus sur PM2.5
    pm25_df = df[df['parameter'] == 'pm25']

    fig, ax = plt.subplots(figsize=(12, 6))

    for region in ['Europe', 'Asie', 'Amériques', 'Afrique']:
        region_df = pm25_df[pm25_df['region'] == region]
        if region_df.empty:
            continue

        yearly = region_df.groupby('year')['average'].mean()
        if len(yearly) > 1:
            ax.plot(yearly.index, yearly.values, 'o-', label=region, linewidth=2, markersize=8)

    ax.set_xlabel('Année', fontsize=12)
    ax.set_ylabel('PM2.5 moyen (µg/m³)', fontsize=12)
    ax.set_title('Évolution du PM2.5 par Région (2018-2023)', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=5, color='r', linestyle='--', label='Seuil OMS', alpha=0.7)

    plt.tight_layout()
    plt.savefig(fig_dir / "temporal_evolution_regions.png", dpi=150)
    plt.close()

    # 3. Top pays avec plus forte évolution
    print("\n  3. Pays avec plus forte évolution...")

    country_evolution = []

    for country in df['country_code'].unique():
        country_pm25 = df[(df['country_code'] == country) & (df['parameter'] == 'pm25')]
        if len(country_pm25) >= 4:  # Au moins 4 années de données
            yearly = country_pm25.groupby('year')['average'].mean()
            if len(yearly) >= 4:
                slope, _, r, p, _ = stats.linregress(yearly.index, yearly.values)
                first_val = yearly.iloc[0]
                last_val = yearly.iloc[-1]
                country_evolution.append({
                    'country_code': country,
                    'country_name': country_pm25['country_name'].iloc[0],
                    'pm25_2018': round(first_val, 1) if yearly.index[0] == 2018 else None,
                    'pm25_2023': round(last_val, 1) if yearly.index[-1] == 2023 else None,
                    'variation_absolue': round(last_val - first_val, 2),
                    'variation_pct': round(100 * (last_val - first_val) / first_val, 1) if first_val > 0 else 0,
                    'pente': round(slope, 2),
                    'r2': round(r**2, 3),
                    'tendance': 'amélioration' if slope < 0 else 'dégradation'
                })

    df_evolution = pd.DataFrame(country_evolution)
    df_evolution = df_evolution.sort_values('variation_absolue')

    results['country_evolution'] = df_evolution

    # Top 10 améliorations et dégradations
    print("\n  Top 5 améliorations (baisse PM2.5):")
    for _, row in df_evolution.head(5).iterrows():
        print(f"    {row['country_name']:25s}: {row['variation_absolue']:+.1f} µg/m³ ({row['variation_pct']:+.1f}%)")

    print("\n  Top 5 dégradations (hausse PM2.5):")
    for _, row in df_evolution.tail(5).iloc[::-1].iterrows():
        print(f"    {row['country_name']:25s}: {row['variation_absolue']:+.1f} µg/m³ ({row['variation_pct']:+.1f}%)")

    # Visualisation top évolutions
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Améliorations
    top_improve = df_evolution.head(10)
    ax = axes[0]
    colors = ['green' if x < 0 else 'red' for x in top_improve['variation_absolue']]
    ax.barh(range(len(top_improve)), top_improve['variation_absolue'], color=colors)
    ax.set_yticks(range(len(top_improve)))
    ax.set_yticklabels(top_improve['country_name'])
    ax.set_xlabel('Variation PM2.5 (µg/m³)')
    ax.set_title('Top 10 Améliorations', fontweight='bold')
    ax.axvline(x=0, color='black', linewidth=0.5)

    # Dégradations
    top_degrade = df_evolution.tail(10).iloc[::-1]
    ax = axes[1]
    colors = ['green' if x < 0 else 'red' for x in top_degrade['variation_absolue']]
    ax.barh(range(len(top_degrade)), top_degrade['variation_absolue'], color=colors)
    ax.set_yticks(range(len(top_degrade)))
    ax.set_yticklabels(top_degrade['country_name'])
    ax.set_xlabel('Variation PM2.5 (µg/m³)')
    ax.set_title('Top 10 Dégradations', fontweight='bold')
    ax.axvline(x=0, color='black', linewidth=0.5)

    plt.tight_layout()
    plt.savefig(fig_dir / "temporal_top_evolutions.png", dpi=150)
    plt.close()

    # 4. Heatmap évolution par pays/année
    print("\n  4. Heatmap pays/année...")

    # Sélectionner les pays avec données complètes
    pm25_pivot = pm25_df.pivot_table(index='country_code', columns='year', values='average', aggfunc='mean')
    # Garder les pays avec au moins 4 années
    pm25_pivot = pm25_pivot.dropna(thresh=4)

    if len(pm25_pivot) > 5:
        # Trier par moyenne
        pm25_pivot['mean'] = pm25_pivot.mean(axis=1)
        pm25_pivot = pm25_pivot.sort_values('mean', ascending=False).drop('mean', axis=1)

        fig, ax = plt.subplots(figsize=(12, max(8, len(pm25_pivot) * 0.3)))
        sns.heatmap(pm25_pivot.head(30), annot=True, fmt='.0f', cmap='RdYlGn_r',
                    cbar_kws={'label': 'PM2.5 (µg/m³)'}, ax=ax)
        ax.set_title('Évolution PM2.5 par Pays (2018-2023)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Année')
        ax.set_ylabel('Pays')
        plt.tight_layout()
        plt.savefig(fig_dir / "temporal_heatmap_pays.png", dpi=150)
        plt.close()

    # 5. Impact COVID-19 (2019 vs 2020)
    print("\n  5. Analyse impact COVID-19 (2019 vs 2020)...")

    covid_analysis = []
    for country in df['country_code'].unique():
        for param in ['pm25', 'pm10', 'no2']:
            data_2019 = df[(df['country_code'] == country) & (df['year'] == 2019) & (df['parameter'] == param)]
            data_2020 = df[(df['country_code'] == country) & (df['year'] == 2020) & (df['parameter'] == param)]

            if not data_2019.empty and not data_2020.empty:
                val_2019 = data_2019['average'].values[0]
                val_2020 = data_2020['average'].values[0]
                if val_2019 > 0:
                    covid_analysis.append({
                        'country_code': country,
                        'country_name': data_2019['country_name'].values[0],
                        'parameter': param,
                        'val_2019': val_2019,
                        'val_2020': val_2020,
                        'variation_pct': round(100 * (val_2020 - val_2019) / val_2019, 1)
                    })

    df_covid = pd.DataFrame(covid_analysis)
    results['covid_impact'] = df_covid

    if not df_covid.empty:
        # Résumé par polluant
        print("\n  Variation moyenne 2019->2020 (effet COVID):")
        for param in ['pm25', 'pm10', 'no2']:
            param_data = df_covid[df_covid['parameter'] == param]
            if not param_data.empty:
                mean_var = param_data['variation_pct'].mean()
                print(f"    {param:6s}: {mean_var:+.1f}%")

        # Graphique
        fig, ax = plt.subplots(figsize=(10, 6))
        covid_summary = df_covid.groupby('parameter')['variation_pct'].mean()
        colors = ['green' if x < 0 else 'red' for x in covid_summary.values]
        bars = ax.bar(covid_summary.index, covid_summary.values, color=colors)
        ax.axhline(y=0, color='black', linewidth=0.5)
        ax.set_ylabel('Variation moyenne (%)')
        ax.set_title('Impact COVID-19 sur la Pollution (2019 vs 2020)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Polluant')

        for bar, val in zip(bars, covid_summary.values):
            ax.annotate(f'{val:+.1f}%', xy=(bar.get_x() + bar.get_width()/2, val),
                       ha='center', va='bottom' if val > 0 else 'top', fontsize=10)

        plt.tight_layout()
        plt.savefig(fig_dir / "temporal_covid_impact.png", dpi=150)
        plt.close()

    # Sauvegarder les résultats
    if 'evolution_globale' in results:
        results['evolution_globale'].to_csv(REPORTS_DIR / "temporal_evolution_globale.csv", index=False)
    if 'country_evolution' in results:
        results['country_evolution'].to_csv(REPORTS_DIR / "temporal_country_evolution.csv", index=False)
    if 'covid_impact' in results:
        results['covid_impact'].to_csv(REPORTS_DIR / "temporal_covid_impact.csv", index=False)

    print(f"\n  Figures temporelles sauvegardées dans: {fig_dir}")

    return results


# =============================================================================
# TESTS DU CHI2 (INDEPENDANCE ENTRE VARIABLES CATEGORIELLES)
# =============================================================================

def run_chi2_analysis():
    """
    Effectue des tests du Chi2 pour tester l'indépendance entre variables catégorielles.

    Tests réalisés:
    1. Région vs Niveau de pollution (faible/moyen/élevé)
    2. Tendance (amélioration/dégradation) vs Région
    3. Dépassement seuils OMS vs Catégorie économique
    4. Impact COVID vs Région
    """
    print("\n" + "=" * 60)
    print("TESTS DU CHI2 (INDEPENDANCE)")
    print("=" * 60)

    # Charger les données OpenAQ multi-années
    openaq_path = DATA_RAW / "openaq_country_averages.csv"
    if not openaq_path.exists():
        print(f"ERREUR: {openaq_path} n'existe pas")
        return None

    df = pd.read_csv(openaq_path)

    fig_dir = REPORTS_DIR / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    results = []

    # Définir les régions
    regions = {
        'Europe': ['AD', 'AL', 'AT', 'BA', 'BE', 'BG', 'CH', 'CZ', 'DE', 'DK', 'ES', 'FI', 'FR', 'GB', 'GR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LV', 'MK', 'MT', 'NL', 'NO', 'PL', 'PT', 'RO', 'RS', 'SE', 'SI', 'SK', 'XK'],
        'Asie': ['BD', 'CN', 'HK', 'ID', 'IN', 'JP', 'KR', 'MN', 'MY', 'PH', 'SG', 'TH', 'TW', 'VN', 'TJ', 'TM', 'UZ', 'NP', 'LA', 'KH'],
        'Ameriques': ['AR', 'BR', 'CA', 'CL', 'CO', 'CR', 'EC', 'MX', 'PE', 'PR', 'US'],
        'Afrique': ['ET', 'GH', 'KE', 'NG', 'RW', 'SD', 'TD', 'UG', 'ZA', 'ML'],
        'Moyen-Orient': ['AE', 'BH', 'IL', 'IQ', 'KW', 'QA', 'SA', 'TR']
    }

    df['region'] = df['country_code'].apply(
        lambda x: next((r for r, codes in regions.items() if x in codes), 'Autre')
    )

    # Seuil OMS pour PM2.5 (annuel: 5 µg/m³)
    SEUIL_OMS_PM25 = 5

    # =========================================================================
    # TEST 1: Région vs Niveau de pollution PM2.5 (2023)
    # =========================================================================
    print("\n  Test 1: Region vs Niveau de pollution PM2.5")

    pm25_2023 = df[(df['parameter'] == 'pm25') & (df['year'] == 2023)].copy()

    if len(pm25_2023) > 10:
        # Catégoriser le niveau de pollution
        pm25_2023['niveau_pollution'] = pd.cut(
            pm25_2023['average'],
            bins=[0, 10, 25, 50, float('inf')],
            labels=['Faible (<10)', 'Modere (10-25)', 'Eleve (25-50)', 'Tres eleve (>50)']
        )

        # Filtrer les régions avec assez de données
        pm25_2023_filtered = pm25_2023[pm25_2023['region'] != 'Autre']

        if len(pm25_2023_filtered) > 10:
            # Tableau de contingence
            contingency = pd.crosstab(pm25_2023_filtered['region'], pm25_2023_filtered['niveau_pollution'])

            # Test du Chi2
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

            # V de Cramer (taille d'effet)
            n = contingency.sum().sum()
            min_dim = min(contingency.shape) - 1
            cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

            results.append({
                'test': 'Region vs Niveau pollution PM2.5',
                'chi2': round(chi2, 2),
                'p_value': round(p_value, 4),
                'dof': dof,
                'cramers_v': round(cramers_v, 3),
                'significatif': 'Oui' if p_value < 0.05 else 'Non',
                'interpretation': 'Dependance' if p_value < 0.05 else 'Independance'
            })

            print(f"    Chi2 = {chi2:.2f}, p = {p_value:.4f}, V de Cramer = {cramers_v:.3f}")
            print(f"    -> {'DEPENDANCE SIGNIFICATIVE' if p_value < 0.05 else 'Independance (non significatif)'}")

            # Visualisation
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))

            # Heatmap des effectifs observés
            ax = axes[0]
            sns.heatmap(contingency, annot=True, fmt='d', cmap='Blues', ax=ax)
            ax.set_title('Effectifs observes\nRegion vs Niveau de pollution PM2.5')
            ax.set_xlabel('Niveau de pollution')
            ax.set_ylabel('Region')

            # Barplot empilé
            ax = axes[1]
            contingency_pct = contingency.div(contingency.sum(axis=1), axis=0) * 100
            contingency_pct.plot(kind='bar', stacked=True, ax=ax, colormap='RdYlGn_r')
            ax.set_title(f'Repartition par region\n(Chi2={chi2:.1f}, p={p_value:.4f})')
            ax.set_xlabel('Region')
            ax.set_ylabel('Pourcentage (%)')
            ax.legend(title='Niveau', bbox_to_anchor=(1.02, 1))
            ax.tick_params(axis='x', rotation=45)

            plt.tight_layout()
            plt.savefig(fig_dir / "chi2_region_pollution.png", dpi=150, bbox_inches='tight')
            plt.close()

    # =========================================================================
    # TEST 2: Dépassement seuil OMS vs Région
    # =========================================================================
    print("\n  Test 2: Depassement seuil OMS vs Region")

    if len(pm25_2023) > 10:
        pm25_2023['depasse_oms'] = pm25_2023['average'] > SEUIL_OMS_PM25
        pm25_2023['depasse_oms_label'] = pm25_2023['depasse_oms'].map({True: 'Depasse', False: 'Conforme'})

        pm25_filtered = pm25_2023[pm25_2023['region'] != 'Autre']

        if len(pm25_filtered) > 10:
            contingency_oms = pd.crosstab(pm25_filtered['region'], pm25_filtered['depasse_oms_label'])

            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_oms)
            n = contingency_oms.sum().sum()
            min_dim = min(contingency_oms.shape) - 1
            cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

            results.append({
                'test': 'Depassement OMS vs Region',
                'chi2': round(chi2, 2),
                'p_value': round(p_value, 4),
                'dof': dof,
                'cramers_v': round(cramers_v, 3),
                'significatif': 'Oui' if p_value < 0.05 else 'Non',
                'interpretation': 'Dependance' if p_value < 0.05 else 'Independance'
            })

            print(f"    Chi2 = {chi2:.2f}, p = {p_value:.4f}, V de Cramer = {cramers_v:.3f}")
            print(f"    -> {'DEPENDANCE SIGNIFICATIVE' if p_value < 0.05 else 'Independance (non significatif)'}")

            # Visualisation
            fig, ax = plt.subplots(figsize=(10, 6))
            contingency_oms.plot(kind='bar', ax=ax, color=['green', 'red'])
            ax.set_title(f'Depassement seuil OMS par Region\n(Chi2={chi2:.1f}, p={p_value:.4f})')
            ax.set_xlabel('Region')
            ax.set_ylabel('Nombre de pays')
            ax.legend(title='Seuil OMS (5 ug/m3)')
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            plt.savefig(fig_dir / "chi2_oms_region.png", dpi=150)
            plt.close()

    # =========================================================================
    # TEST 3: Tendance (amelioration/degradation) vs Region
    # =========================================================================
    print("\n  Test 3: Tendance temporelle vs Region")

    # Calculer la tendance par pays
    tendances = []
    for country in df['country_code'].unique():
        country_pm25 = df[(df['country_code'] == country) & (df['parameter'] == 'pm25')]
        if len(country_pm25) >= 4:
            yearly = country_pm25.groupby('year')['average'].mean()
            if len(yearly) >= 4:
                slope, _, _, _, _ = stats.linregress(yearly.index, yearly.values)
                region = country_pm25['region'].iloc[0]
                tendances.append({
                    'country_code': country,
                    'region': region,
                    'pente': slope,
                    'tendance': 'Amelioration' if slope < -0.5 else ('Degradation' if slope > 0.5 else 'Stable')
                })

    df_tendances = pd.DataFrame(tendances)
    df_tendances_filtered = df_tendances[df_tendances['region'] != 'Autre']

    if len(df_tendances_filtered) > 10:
        contingency_trend = pd.crosstab(df_tendances_filtered['region'], df_tendances_filtered['tendance'])

        # Vérifier qu'on a au moins 2 colonnes et 2 lignes
        if contingency_trend.shape[0] >= 2 and contingency_trend.shape[1] >= 2:
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_trend)
            n = contingency_trend.sum().sum()
            min_dim = min(contingency_trend.shape) - 1
            cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

            results.append({
                'test': 'Tendance temporelle vs Region',
                'chi2': round(chi2, 2),
                'p_value': round(p_value, 4),
                'dof': dof,
                'cramers_v': round(cramers_v, 3),
                'significatif': 'Oui' if p_value < 0.05 else 'Non',
                'interpretation': 'Dependance' if p_value < 0.05 else 'Independance'
            })

            print(f"    Chi2 = {chi2:.2f}, p = {p_value:.4f}, V de Cramer = {cramers_v:.3f}")
            print(f"    -> {'DEPENDANCE SIGNIFICATIVE' if p_value < 0.05 else 'Independance (non significatif)'}")

            # Visualisation
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))

            ax = axes[0]
            sns.heatmap(contingency_trend, annot=True, fmt='d', cmap='RdYlGn', ax=ax)
            ax.set_title('Effectifs: Tendance vs Region')

            ax = axes[1]
            contingency_trend.plot(kind='bar', ax=ax, color=['green', 'orange', 'red'])
            ax.set_title(f'Tendance par Region (2018-2023)\n(Chi2={chi2:.1f}, p={p_value:.4f})')
            ax.set_xlabel('Region')
            ax.set_ylabel('Nombre de pays')
            ax.legend(title='Tendance')
            ax.tick_params(axis='x', rotation=45)

            plt.tight_layout()
            plt.savefig(fig_dir / "chi2_tendance_region.png", dpi=150)
            plt.close()

    # =========================================================================
    # TEST 4: Impact COVID (2019 vs 2020) vs Region
    # =========================================================================
    print("\n  Test 4: Impact COVID (variation 2019-2020) vs Region")

    covid_impacts = []
    for country in df['country_code'].unique():
        pm25_2019 = df[(df['country_code'] == country) & (df['year'] == 2019) & (df['parameter'] == 'pm25')]
        pm25_2020 = df[(df['country_code'] == country) & (df['year'] == 2020) & (df['parameter'] == 'pm25')]

        if not pm25_2019.empty and not pm25_2020.empty:
            val_2019 = pm25_2019['average'].values[0]
            val_2020 = pm25_2020['average'].values[0]
            if val_2019 > 0:
                variation = (val_2020 - val_2019) / val_2019 * 100
                region = pm25_2019['region'].values[0]
                covid_impacts.append({
                    'country_code': country,
                    'region': region,
                    'variation_pct': variation,
                    'impact': 'Baisse' if variation < -5 else ('Hausse' if variation > 5 else 'Stable')
                })

    df_covid = pd.DataFrame(covid_impacts)
    df_covid_filtered = df_covid[df_covid['region'] != 'Autre']

    if len(df_covid_filtered) > 10:
        contingency_covid = pd.crosstab(df_covid_filtered['region'], df_covid_filtered['impact'])

        if contingency_covid.shape[0] >= 2 and contingency_covid.shape[1] >= 2:
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_covid)
            n = contingency_covid.sum().sum()
            min_dim = min(contingency_covid.shape) - 1
            cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

            results.append({
                'test': 'Impact COVID vs Region',
                'chi2': round(chi2, 2),
                'p_value': round(p_value, 4),
                'dof': dof,
                'cramers_v': round(cramers_v, 3),
                'significatif': 'Oui' if p_value < 0.05 else 'Non',
                'interpretation': 'Dependance' if p_value < 0.05 else 'Independance'
            })

            print(f"    Chi2 = {chi2:.2f}, p = {p_value:.4f}, V de Cramer = {cramers_v:.3f}")
            print(f"    -> {'DEPENDANCE SIGNIFICATIVE' if p_value < 0.05 else 'Independance (non significatif)'}")

            # Visualisation
            fig, ax = plt.subplots(figsize=(10, 6))
            contingency_covid.plot(kind='bar', ax=ax, color=['green', 'red', 'gray'])
            ax.set_title(f'Impact COVID-19 par Region (2019 vs 2020)\n(Chi2={chi2:.1f}, p={p_value:.4f})')
            ax.set_xlabel('Region')
            ax.set_ylabel('Nombre de pays')
            ax.legend(title='Variation PM2.5')
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            plt.savefig(fig_dir / "chi2_covid_region.png", dpi=150)
            plt.close()

    # =========================================================================
    # TEST 5: Polluant dominant vs Region
    # =========================================================================
    print("\n  Test 5: Polluant dominant vs Region")

    # Pour chaque pays, déterminer quel polluant dépasse le plus les seuils
    seuils_oms = {'pm25': 5, 'pm10': 15, 'no2': 10, 'o3': 100, 'so2': 40}

    polluant_dominant = []
    for country in df['country_code'].unique():
        country_data = df[(df['country_code'] == country) & (df['year'] == 2023)]
        if country_data.empty:
            continue

        max_ratio = 0
        dominant = None
        region = country_data['region'].iloc[0]

        for param, seuil in seuils_oms.items():
            param_data = country_data[country_data['parameter'] == param]
            if not param_data.empty:
                ratio = param_data['average'].values[0] / seuil
                if ratio > max_ratio:
                    max_ratio = ratio
                    dominant = param.upper()

        if dominant:
            polluant_dominant.append({
                'country_code': country,
                'region': region,
                'polluant_dominant': dominant
            })

    df_polluant = pd.DataFrame(polluant_dominant)
    df_polluant_filtered = df_polluant[df_polluant['region'] != 'Autre']

    if len(df_polluant_filtered) > 10:
        contingency_pol = pd.crosstab(df_polluant_filtered['region'], df_polluant_filtered['polluant_dominant'])

        if contingency_pol.shape[0] >= 2 and contingency_pol.shape[1] >= 2:
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_pol)
            n = contingency_pol.sum().sum()
            min_dim = min(contingency_pol.shape) - 1
            cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

            results.append({
                'test': 'Polluant dominant vs Region',
                'chi2': round(chi2, 2),
                'p_value': round(p_value, 4),
                'dof': dof,
                'cramers_v': round(cramers_v, 3),
                'significatif': 'Oui' if p_value < 0.05 else 'Non',
                'interpretation': 'Dependance' if p_value < 0.05 else 'Independance'
            })

            print(f"    Chi2 = {chi2:.2f}, p = {p_value:.4f}, V de Cramer = {cramers_v:.3f}")
            print(f"    -> {'DEPENDANCE SIGNIFICATIVE' if p_value < 0.05 else 'Independance (non significatif)'}")

            # Visualisation
            fig, ax = plt.subplots(figsize=(12, 6))
            contingency_pol.plot(kind='bar', ax=ax, colormap='Set2')
            ax.set_title(f'Polluant dominant par Region\n(Chi2={chi2:.1f}, p={p_value:.4f})')
            ax.set_xlabel('Region')
            ax.set_ylabel('Nombre de pays')
            ax.legend(title='Polluant', bbox_to_anchor=(1.02, 1))
            ax.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            plt.savefig(fig_dir / "chi2_polluant_region.png", dpi=150, bbox_inches='tight')
            plt.close()

    # =========================================================================
    # RESUME DES RESULTATS
    # =========================================================================
    print("\n" + "-" * 60)
    print("RESUME DES TESTS CHI2")
    print("-" * 60)

    df_results = pd.DataFrame(results)
    if not df_results.empty:
        for _, row in df_results.iterrows():
            sig = "***" if row['p_value'] < 0.001 else ("**" if row['p_value'] < 0.01 else ("*" if row['p_value'] < 0.05 else ""))
            print(f"  {row['test']:40s} Chi2={row['chi2']:7.2f}  p={row['p_value']:.4f} {sig:3s}  V={row['cramers_v']:.3f}")

        # Sauvegarder
        df_results.to_csv(REPORTS_DIR / "chi2_results.csv", index=False)
        print(f"\n  Resultats sauvegardes: {REPORTS_DIR / 'chi2_results.csv'}")

    print(f"  Figures sauvegardees dans: {fig_dir}")

    return df_results


# =============================================================================
# ANALYSE EN COMPOSANTES PRINCIPALES (ACP)
# =============================================================================

def run_pca_analysis(df, target='pollution_pm25'):
    """
    Effectue une Analyse en Composantes Principales.
    """
    print("\n" + "=" * 60)
    print("ANALYSE EN COMPOSANTES PRINCIPALES (ACP)")
    print("=" * 60)

    X, y, df_analysis = prepare_data_for_analysis(df, target)

    if len(X) < 20:
        print("Trop peu de données pour l'ACP")
        return None

    # Standardisation
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ACP
    n_components = min(10, X.shape[1], X.shape[0] - 1)
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X_scaled)

    # Variance expliquée
    variance_ratio = pca.explained_variance_ratio_
    variance_cumulative = np.cumsum(variance_ratio)

    print(f"\n  Variance expliquée par composante:")
    for i, (var, cum) in enumerate(zip(variance_ratio, variance_cumulative)):
        print(f"    PC{i+1}: {var*100:.1f}% (cumul: {cum*100:.1f}%)")

    # Trouver le nombre de composantes pour 80% de variance
    n_80 = np.argmax(variance_cumulative >= 0.8) + 1
    print(f"\n  Composantes pour 80% de variance: {n_80}")

    # Contributions des variables
    loadings = pd.DataFrame(
        pca.components_.T,
        columns=[f'PC{i+1}' for i in range(n_components)],
        index=X.columns
    )

    print(f"\n  Top contributeurs à PC1:")
    top_pc1 = loadings['PC1'].abs().sort_values(ascending=False).head(10)
    for var, val in top_pc1.items():
        signe = '+' if loadings.loc[var, 'PC1'] > 0 else '-'
        print(f"    {signe} {var}: {val:.3f}")

    # Créer les visualisations
    fig_dir = REPORTS_DIR / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # 1. Scree plot
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.bar(range(1, n_components + 1), variance_ratio * 100)
    plt.xlabel('Composante Principale')
    plt.ylabel('Variance Expliquée (%)')
    plt.title('Scree Plot')

    plt.subplot(1, 2, 2)
    plt.plot(range(1, n_components + 1), variance_cumulative * 100, 'bo-')
    plt.axhline(y=80, color='r', linestyle='--', label='80%')
    plt.xlabel('Nombre de Composantes')
    plt.ylabel('Variance Cumulative (%)')
    plt.title('Variance Cumulative')
    plt.legend()

    plt.tight_layout()
    plt.savefig(fig_dir / "acp_scree_plot.png", dpi=150)
    plt.close()

    # 2. Biplot (PC1 vs PC2)
    plt.figure(figsize=(12, 10))

    # Points (pays)
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap='RdYlGn_r',
                         alpha=0.7, s=50)
    plt.colorbar(scatter, label=target)

    # Flèches (variables) - top 15
    top_vars = loadings['PC1'].abs().sort_values(ascending=False).head(15).index
    scale = 3
    for var in top_vars:
        plt.arrow(0, 0,
                 loadings.loc[var, 'PC1'] * scale,
                 loadings.loc[var, 'PC2'] * scale,
                 head_width=0.1, head_length=0.05, fc='blue', ec='blue', alpha=0.5)
        plt.text(loadings.loc[var, 'PC1'] * scale * 1.1,
                loadings.loc[var, 'PC2'] * scale * 1.1,
                var.split('_')[-1][:10], fontsize=8)

    plt.xlabel(f'PC1 ({variance_ratio[0]*100:.1f}%)')
    plt.ylabel(f'PC2 ({variance_ratio[1]*100:.1f}%)')
    plt.title(f'Biplot ACP - Coloré par {target}')
    plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    plt.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
    plt.tight_layout()
    plt.savefig(fig_dir / "acp_biplot.png", dpi=150)
    plt.close()

    # 3. Heatmap des loadings
    plt.figure(figsize=(12, max(8, len(X.columns) * 0.3)))
    sns.heatmap(loadings.iloc[:, :5], annot=True, fmt='.2f', cmap='RdBu_r', center=0)
    plt.title('Contributions des Variables aux 5 Premières Composantes')
    plt.tight_layout()
    plt.savefig(fig_dir / "acp_loadings.png", dpi=150)
    plt.close()

    # Sauvegarder les résultats
    loadings.to_csv(REPORTS_DIR / "acp_loadings.csv")

    results = {
        'n_components': n_components,
        'variance_explained': variance_ratio.tolist(),
        'variance_cumulative': variance_cumulative.tolist(),
        'n_for_80pct': n_80,
        'loadings': loadings
    }

    print(f"\nFigures ACP sauvegardées dans: {fig_dir}")

    return results

# =============================================================================
# MODÈLES PRÉDICTIFS
# =============================================================================

def run_predictive_models(df, target='pollution_pm25'):
    """
    Entraîne et compare plusieurs modèles prédictifs.
    """
    print("\n" + "=" * 60)
    print("MODÈLES PRÉDICTIFS")
    print("=" * 60)

    X, y, df_analysis = prepare_data_for_analysis(df, target)

    if len(X) < 30:
        print("Trop peu de données pour les modèles prédictifs")
        return None

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\n  Train: {len(X_train)} observations")
    print(f"  Test: {len(X_test)} observations")

    # Standardiser
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Définir les modèles
    models = {
        'Régression Linéaire': LinearRegression(),
        'Ridge': Ridge(alpha=1.0),
        'Lasso': Lasso(alpha=0.1),
        'Arbre de Décision': DecisionTreeRegressor(max_depth=5, random_state=42),
        'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
    }

    results = []

    for name, model in models.items():
        print(f"\n  Entraînement: {name}...")

        # Entraîner
        if name in ['Régression Linéaire', 'Ridge', 'Lasso']:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_pred_train = model.predict(X_train_scaled)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_pred_train = model.predict(X_train)

        # Métriques
        r2_train = r2_score(y_train, y_pred_train)
        r2_test = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)

        # Cross-validation
        if name in ['Régression Linéaire', 'Ridge', 'Lasso']:
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
        else:
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')

        results.append({
            'model': name,
            'r2_train': r2_train,
            'r2_test': r2_test,
            'rmse': rmse,
            'mae': mae,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        })

        print(f"    R² train: {r2_train:.3f}")
        print(f"    R² test: {r2_test:.3f}")
        print(f"    RMSE: {rmse:.2f}")
        print(f"    CV R²: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

    df_results = pd.DataFrame(results)

    # Afficher le classement
    print("\n" + "-" * 40)
    print("CLASSEMENT DES MODÈLES (par R² test):")
    print("-" * 40)
    df_sorted = df_results.sort_values('r2_test', ascending=False)
    for i, row in df_sorted.iterrows():
        print(f"  {row['model']:25} R²={row['r2_test']:.3f} RMSE={row['rmse']:.2f}")

    # Visualisations
    fig_dir = REPORTS_DIR / "figures"

    # 1. Comparaison des modèles
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    models_names = df_results['model']
    x = np.arange(len(models_names))
    width = 0.35

    plt.bar(x - width/2, df_results['r2_train'], width, label='Train', color='skyblue')
    plt.bar(x + width/2, df_results['r2_test'], width, label='Test', color='coral')
    plt.xlabel('Modèle')
    plt.ylabel('R²')
    plt.title('Performance des Modèles (R²)')
    plt.xticks(x, models_names, rotation=45, ha='right')
    plt.legend()
    plt.ylim(0, 1)

    plt.subplot(1, 2, 2)
    plt.bar(models_names, df_results['rmse'], color='lightgreen')
    plt.xlabel('Modèle')
    plt.ylabel('RMSE')
    plt.title('Erreur des Modèles (RMSE)')
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(fig_dir / "models_comparison.png", dpi=150)
    plt.close()

    # 2. Importance des variables (Random Forest)
    rf_model = models['Random Forest']
    importances = pd.DataFrame({
        'variable': X.columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)

    print("\n" + "-" * 40)
    print("VARIABLES LES PLUS IMPORTANTES (Random Forest):")
    print("-" * 40)
    for _, row in importances.head(15).iterrows():
        print(f"  {row['variable']:40} {row['importance']:.4f}")

    plt.figure(figsize=(10, 8))
    top_20 = importances.head(20)
    plt.barh(range(len(top_20)), top_20['importance'])
    plt.yticks(range(len(top_20)), top_20['variable'])
    plt.xlabel('Importance')
    plt.title('Top 20 Variables les Plus Importantes (Random Forest)')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(fig_dir / "feature_importance.png", dpi=150)
    plt.close()

    # 3. Arbre de décision simplifié
    plt.figure(figsize=(20, 10))
    dt_model = models['Arbre de Décision']
    plot_tree(dt_model, feature_names=X.columns, filled=True, rounded=True,
              fontsize=8, max_depth=3)
    plt.title('Arbre de Décision (3 premiers niveaux)')
    plt.tight_layout()
    plt.savefig(fig_dir / "decision_tree.png", dpi=150)
    plt.close()

    # Sauvegarder les résultats
    df_results.to_csv(REPORTS_DIR / "models_comparison.csv", index=False)
    importances.to_csv(REPORTS_DIR / "feature_importance.csv", index=False)

    print(f"\nRésultats sauvegardés dans: {REPORTS_DIR}")

    return df_results, importances

# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================

def run_analyses():
    """
    Exécute toutes les analyses avancées.
    """
    print("\n" + "=" * 70)
    print("   ANALYSES AVANCÉES")
    print("=" * 70)

    # 1. Analyse temporelle (ne nécessite pas la base fusionnée)
    temporal_results = run_temporal_analysis()

    # 2. Tests du Chi2 (indépendance entre variables catégorielles)
    chi2_results = run_chi2_analysis()

    # 3. Charger les données fusionnées pour ACP et modèles
    df = load_data()
    if df is None:
        print("\nBase fusionnée non disponible, analyses ACP/modèles ignorées")
    else:
        # ACP
        pca_results = run_pca_analysis(df)

        # Modèles prédictifs
        model_results = run_predictive_models(df)

    print("\n" + "=" * 70)
    print("   ANALYSES TERMINÉES")
    print("=" * 70)
    print(f"\nFichiers generes:")
    print(f"  - reports/temporal_*.csv (evolution 2018-2023)")
    print(f"  - reports/figures/temporal_*.png")
    print(f"  - reports/chi2_results.csv (tests d'independance)")
    print(f"  - reports/figures/chi2_*.png")
    if df is not None:
        print(f"  - reports/acp_loadings.csv")
        print(f"  - reports/models_comparison.csv")
        print(f"  - reports/feature_importance.csv")
        print(f"  - reports/figures/acp_*.png")
        print(f"  - reports/figures/models_*.png")

if __name__ == "__main__":
    run_analyses()
