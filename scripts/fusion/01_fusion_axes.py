"""
Script de Fusion des Axes
=========================
RESPONSABLE: Chef de projet

Ce script fusionne tous les résultats des différents axes thématiques
pour créer la base de données finale complète.

Il doit être exécuté APRÈS que tous les membres aient terminé leur axe.

Entrées:
    - data/final/base_transport.csv
    - data/final/base_energie.csv
    - data/final/base_economie.csv
    - data/final/base_demographie.csv
    - data/final/base_sante.csv

Sorties:
    - data/final/base_complete.csv
    - reports/synthese_correlations.csv
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

from config import DATA_FINAL, DATA_CLEANED, REPORTS_DIR, get_label

# =============================================================================
# CONFIGURATION
# =============================================================================
AXES = ['transport', 'energie', 'economie', 'demographie', 'sante']

# =============================================================================
# FONCTIONS DE FUSION
# =============================================================================

def check_axes_disponibles():
    """
    Vérifie quels axes ont été complétés.
    """
    print("=" * 60)
    print("VÉRIFICATION DES AXES DISPONIBLES")
    print("=" * 60)

    axes_ok = []
    axes_manquants = []

    for axe in AXES:
        path = DATA_FINAL / f"base_{axe}.csv"
        if path.exists():
            df = pd.read_csv(path)
            print(f"  [OK] {axe}: {len(df)} pays, {len(df.columns)} colonnes")
            axes_ok.append(axe)
        else:
            print(f"  [X]  {axe}: MANQUANT")
            axes_manquants.append(axe)

    print(f"\nAxes disponibles: {len(axes_ok)}/{len(AXES)}")

    if axes_manquants:
        print(f"\nAxes manquants: {axes_manquants}")
        print("Exécutez les scripts correspondants:")
        for axe in axes_manquants:
            print(f"  python scripts/axes/axe_{axe}.py")

    return axes_ok

def load_base_commune():
    """
    Charge la base commune (pollution + villes).
    """
    print("\n" + "=" * 60)
    print("CHARGEMENT DE LA BASE COMMUNE")
    print("=" * 60)

    path = DATA_CLEANED / "base_commune.csv"
    if not path.exists():
        print(f"ERREUR: {path} n'existe pas")
        return None

    df = pd.read_csv(path)
    print(f"Base commune: {len(df)} pays")
    return df

def load_axe_data(axe):
    """
    Charge les données d'un axe et extrait uniquement les colonnes spécifiques.
    """
    path = DATA_FINAL / f"base_{axe}.csv"
    df = pd.read_csv(path)

    # Identifier les colonnes propres à cet axe (pas les colonnes communes)
    prefixes = {
        'transport': 'transport_',
        'energie': 'energie_',
        'economie': 'eco_',
        'demographie': 'demo_',
        'sante': 'sante_'
    }

    prefix = prefixes.get(axe, f'{axe}_')
    axe_cols = [c for c in df.columns if c.startswith(prefix)]

    # Garder code_pays + colonnes de l'axe
    cols_to_keep = ['code_pays'] + axe_cols
    cols_to_keep = [c for c in cols_to_keep if c in df.columns]

    return df[cols_to_keep]

def fusion_tous_axes(axes_disponibles):
    """
    Fusionne tous les axes disponibles avec la base commune.
    """
    print("\n" + "=" * 60)
    print("FUSION DE TOUS LES AXES")
    print("=" * 60)

    # Charger la base commune
    df_base = load_base_commune()
    if df_base is None:
        return None

    df_final = df_base.copy()
    print(f"\nBase initiale: {len(df_final)} pays, {len(df_final.columns)} colonnes")

    # Fusionner chaque axe
    for axe in axes_disponibles:
        print(f"\n  Fusion axe {axe}...")
        df_axe = load_axe_data(axe)

        # Standardiser le code pays
        df_axe['code_pays'] = df_axe['code_pays'].str.upper()
        df_final['code_pays'] = df_final['code_pays'].str.upper()

        # Fusionner (left join pour garder tous les pays de la base)
        n_before = len(df_final)
        df_final = pd.merge(
            df_final,
            df_axe,
            on='code_pays',
            how='left'
        )

        axe_cols = [c for c in df_axe.columns if c != 'code_pays']
        n_with_data = df_final[axe_cols].notna().any(axis=1).sum()
        print(f"    {n_with_data} pays avec données {axe}")

    print(f"\nBase finale: {len(df_final)} pays, {len(df_final.columns)} colonnes")

    return df_final

def calculer_statistiques_completude(df):
    """
    Calcule des statistiques sur la complétude des données.
    """
    print("\n" + "=" * 60)
    print("STATISTIQUES DE COMPLÉTUDE")
    print("=" * 60)

    # Par axe
    prefixes = {
        'pollution': 'pollution_',
        'transport': 'transport_',
        'energie': 'energie_',
        'economie': 'eco_',
        'demographie': 'demo_',
        'sante': 'sante_'
    }

    stats_completude = []
    for nom, prefix in prefixes.items():
        cols = [c for c in df.columns if c.startswith(prefix)]
        if cols:
            n_complete = df[cols].notna().all(axis=1).sum()
            n_any = df[cols].notna().any(axis=1).sum()
            pct_complete = n_complete / len(df) * 100
            pct_any = n_any / len(df) * 100

            stats_completude.append({
                'axe': nom,
                'nb_indicateurs': len(cols),
                'pays_complets': n_complete,
                'pays_partiels': n_any,
                'pct_complets': pct_complete,
                'pct_partiels': pct_any
            })

            print(f"\n  {nom.upper()}:")
            print(f"    - {len(cols)} indicateurs")
            print(f"    - {n_complete} pays complets ({pct_complete:.1f}%)")
            print(f"    - {n_any} pays avec au moins une donnée ({pct_any:.1f}%)")

    return pd.DataFrame(stats_completude)

def synthese_correlations(df):
    """
    Crée une synthèse de toutes les corrélations significatives.
    """
    print("\n" + "=" * 60)
    print("SYNTHÈSE DES CORRÉLATIONS")
    print("=" * 60)

    # Identifier les colonnes par type
    pollution_cols = [c for c in df.columns if c.startswith('pollution_')]
    autres_cols = [c for c in df.columns if any(
        c.startswith(p) for p in ['transport_', 'energie_', 'eco_', 'demo_', 'sante_']
    )]

    print(f"Colonnes pollution: {len(pollution_cols)}")
    print(f"Colonnes explicatives: {len(autres_cols)}")

    if not pollution_cols or not autres_cols:
        print("Données insuffisantes pour l'analyse")
        return None

    # Calculer toutes les corrélations
    results = []
    for p_col in pollution_cols:
        for a_col in autres_cols:
            df_temp = df[[p_col, a_col]].dropna()
            n = len(df_temp)

            if n < 10:
                continue

            corr, p_value = stats.pearsonr(df_temp[p_col], df_temp[a_col])

            # Déterminer l'axe
            if a_col.startswith('transport_'):
                axe = 'Transport'
            elif a_col.startswith('energie_'):
                axe = 'Énergie'
            elif a_col.startswith('eco_'):
                axe = 'Économie'
            elif a_col.startswith('demo_'):
                axe = 'Démographie'
            elif a_col.startswith('sante_'):
                axe = 'Santé'
            else:
                axe = 'Autre'

            results.append({
                'polluant': p_col.replace('pollution_', ''),
                'indicateur': a_col,
                'axe': axe,
                'correlation': corr,
                'p_value': p_value,
                'significatif': p_value < 0.05,
                'tres_significatif': p_value < 0.01,
                'n_observations': n,
                'force': 'forte' if abs(corr) > 0.5 else 'moyenne' if abs(corr) > 0.3 else 'faible'
            })

    df_results = pd.DataFrame(results)

    # Vérifier si des corrélations ont été calculées
    if df_results.empty:
        print("\n  Aucune corrélation calculée (données insuffisantes)")
        return df_results

    # Afficher le top des corrélations
    print("\n" + "-" * 40)
    print("TOP 15 CORRÉLATIONS LES PLUS FORTES:")
    print("-" * 40)

    top_corr = df_results.nlargest(15, 'correlation', keep='first')
    for _, row in top_corr.iterrows():
        signif = "***" if row['tres_significatif'] else "**" if row['significatif'] else ""
        print(f"  {row['polluant']:8} - {row['indicateur']:40} r={row['correlation']:+.3f} {signif}")

    print("\n" + "-" * 40)
    print("TOP 15 CORRÉLATIONS NÉGATIVES:")
    print("-" * 40)

    bottom_corr = df_results.nsmallest(15, 'correlation', keep='first')
    for _, row in bottom_corr.iterrows():
        signif = "***" if row['tres_significatif'] else "**" if row['significatif'] else ""
        print(f"  {row['polluant']:8} - {row['indicateur']:40} r={row['correlation']:+.3f} {signif}")

    # Résumé par axe
    print("\n" + "-" * 40)
    print("RÉSUMÉ PAR AXE:")
    print("-" * 40)

    resume_axe = df_results.groupby('axe').agg({
        'correlation': ['mean', 'std'],
        'significatif': 'sum',
        'indicateur': 'count'
    }).round(3)
    print(resume_axe.to_string())

    return df_results

def creer_visualisations_globales(df):
    """
    Crée les visualisations de synthèse.
    """
    print("\n" + "=" * 60)
    print("CRÉATION DES VISUALISATIONS GLOBALES")
    print("=" * 60)

    fig_dir = REPORTS_DIR / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # 1. Grande heatmap de corrélations
    print("  Création grande heatmap...")

    pollution_cols = [c for c in df.columns if c.startswith('pollution_')]
    autres_cols = [c for c in df.columns if any(
        c.startswith(p) for p in ['transport_', 'energie_', 'eco_', 'demo_', 'sante_']
    )]

    # Limiter pour la lisibilité
    if len(autres_cols) > 25:
        # Prendre les plus corrélés avec PM2.5
        if 'pollution_pm25' in df.columns:
            corrs = df[autres_cols].corrwith(df['pollution_pm25']).abs().sort_values(ascending=False)
            autres_cols = corrs.head(25).index.tolist()

    all_cols = pollution_cols + autres_cols
    corr_matrix = df[all_cols].corr(method='spearman')

    # Dictionnaire de noms explicites en français
    noms_explicites = {
        # Polluants
        'pollution_pm25': 'PM2.5',
        'pollution_pm10': 'PM10',
        'pollution_no2': 'NO₂',
        'pollution_o3': 'Ozone (O₃)',
        'pollution_so2': 'SO₂',
        'pollution_co': 'CO',
        # Transport (codes World Bank)
        'transport_IS_AIR_DPRT': 'Départs aériens',
        'transport_IS_AIR_PSGR': 'Passagers aériens',
        'transport_IS_ROD_PAVE_ZS': '% Routes pavées',
        'transport_IS_ROD_TOTL_KM': 'Routes totales (km)',
        'transport_IS_RRS_TOTL_KM': 'Réseau ferré (km)',
        'transport_IS_VEH_NVEH_P3': 'Véhicules/1000 hab',
        'transport_IS_VEH_PCAR_P3': 'Voitures/1000 hab',
        # Énergie (codes World Bank)
        'energie_EG_ELC_FOSL_ZS': '% Électricité fossile',
        'energie_EG_ELC_NUCL_ZS': '% Électricité nucléaire',
        'energie_EG_ELC_RNWX_ZS': '% Électricité renouvelable',
        'energie_EG_USE_ELEC_KH_PC': 'Conso. élec./hab (kWh)',
        'energie_EG_USE_PCAP_KG_OE': 'Conso. énergie/hab',
        'energie_EN_ATM_CO2E_KT': 'Émissions CO₂ (kt)',
        'energie_EN_ATM_CO2E_PC': 'CO₂/habitant (t)',
        'energie_EN_ATM_METH_KT_CE': 'Émissions méthane',
        'energie_EN_ATM_NOXE_KT_CE': 'Émissions NOx',
        # Économie (codes World Bank)
        'eco_NV_AGR_TOTL_ZS': '% Agriculture (PIB)',
        'eco_NV_IND_MANF_ZS': '% Industrie manuf. (PIB)',
        'eco_NV_IND_TOTL_ZS': '% Industrie totale (PIB)',
        'eco_NV_SRV_TOTL_ZS': '% Services (PIB)',
        'eco_NY_GDP_PCAP_CD': 'PIB/habitant ($)',
        'eco_NY_GDP_PCAP_PP_CD': 'PIB/hab (PPA)',
        'eco_SL_AGR_EMPL_ZS': 'Emploi agricole (%)',
        'eco_SL_IND_EMPL_ZS': 'Emploi industriel (%)',
        'eco_SL_SRV_EMPL_ZS': 'Emploi services (%)',
        # Démographie (codes World Bank)
        'demo_AG_LND_FRST_ZS': '% Surface forestière',
        'demo_AG_LND_TOTL_K2': 'Superficie (km²)',
        'demo_EN_POP_DNST': 'Densité (hab/km²)',
        'demo_EN_URB_LCTY': 'Pop. grandes villes',
        'demo_EN_URB_LCTY_UR_ZS': '% Pop. grandes villes',
        'demo_SP_POP_TOTL': 'Population totale',
        'demo_SP_URB_GROW': 'Croissance urbaine (%)',
        'demo_SP_URB_TOTL': 'Population urbaine',
        'demo_SP_URB_TOTL_IN_ZS': '% Population urbaine',
        # Santé (codes World Bank)
        'sante_EN_ATM_PM25_MC_M3': 'PM2.5 (OMS)',
        'sante_EN_ATM_PM25_MC_ZS': '% Exposés pollution',
        'sante_SH_STA_AIRP_P5': 'Décès poll. air/100k',
        'sante_SH_XPD_CHEX_GD_ZS': 'Dépenses santé (% PIB)',
        'sante_SH_XPD_CHEX_PC_CD': 'Dépenses santé/hab ($)',
        'sante_SP_DYN_LE00_IN': 'Espérance de vie',
    }

    # Créer les labels avec noms explicites
    labels = []
    for c in all_cols:
        if c in noms_explicites:
            labels.append(noms_explicites[c])
        else:
            # Fallback: utiliser la fonction get_label de config.py
            labels.append(get_label(c))

    plt.figure(figsize=(20, 16))
    sns.heatmap(
        corr_matrix,
        annot=False,
        cmap='RdBu_r',
        center=0,
        xticklabels=labels,
        yticklabels=labels
    )
    plt.title('Matrice de Corrélation Globale\n(Corrélations de Spearman entre polluants et indicateurs socio-économiques)',
              fontsize=16, fontweight='bold', pad=20)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=9)
    plt.subplots_adjust(top=0.92, bottom=0.18, left=0.18)
    plt.savefig(fig_dir / "heatmap_global.png", dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Graphique en barres des corrélations moyennes par axe
    print("  Création barres corrélations...")

    if 'pollution_pm25' in df.columns:
        prefixes = {
            'Transport': 'transport_',
            'Énergie': 'energie_',
            'Économie': 'eco_',
            'Démographie': 'demo_',
            'Santé': 'sante_'
        }

        corr_moyennes = {}
        for nom, prefix in prefixes.items():
            cols = [c for c in df.columns if c.startswith(prefix)]
            if cols:
                corrs = df[cols].corrwith(df['pollution_pm25']).abs()
                corr_moyennes[nom] = corrs.mean()

        if corr_moyennes:
            plt.figure(figsize=(10, 6))
            axes_noms = list(corr_moyennes.keys())
            valeurs = list(corr_moyennes.values())
            colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(axes_noms)))

            bars = plt.bar(axes_noms, valeurs, color=colors)
            plt.ylabel('Corrélation moyenne (valeur absolue)')
            plt.title('Force de Corrélation avec PM2.5 par Axe')
            plt.ylim(0, max(valeurs) * 1.2)

            for bar, val in zip(bars, valeurs):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{val:.3f}', ha='center', va='bottom')

            plt.tight_layout()
            plt.savefig(fig_dir / "correlations_par_axe.png", dpi=150)
            plt.close()

    print(f"\nFigures sauvegardées dans: {fig_dir}")

# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================

def run_fusion():
    """
    Exécute le pipeline de fusion complet.
    """
    print("\n" + "=" * 70)
    print("   FUSION DES RÉSULTATS DE TOUS LES AXES")
    print("=" * 70)

    # 1. Vérifier les axes disponibles
    axes_disponibles = check_axes_disponibles()

    if not axes_disponibles:
        print("\nAucun axe disponible! Exécutez d'abord les scripts d'axes.")
        return

    # 2. Fusionner
    df_final = fusion_tous_axes(axes_disponibles)

    if df_final is None:
        print("\nFusion impossible!")
        return

    # 3. Sauvegarder la base complète
    output_path = DATA_FINAL / "base_complete.csv"
    df_final.to_csv(output_path, index=False)
    print(f"\nBase complète sauvegardée: {output_path}")

    # 4. Statistiques de complétude
    stats_df = calculer_statistiques_completude(df_final)
    stats_df.to_csv(REPORTS_DIR / "completude_donnees.csv", index=False)

    # 5. Synthèse des corrélations
    corr_df = synthese_correlations(df_final)
    if corr_df is not None:
        corr_df.to_csv(REPORTS_DIR / "synthese_correlations.csv", index=False)

    # 6. Visualisations
    creer_visualisations_globales(df_final)

    print("\n" + "=" * 70)
    print("   FUSION TERMINÉE AVEC SUCCÈS")
    print("=" * 70)
    print(f"\nFichiers générés:")
    print(f"  - data/final/base_complete.csv")
    print(f"  - reports/completude_donnees.csv")
    print(f"  - reports/synthese_correlations.csv")
    print(f"  - reports/figures/heatmap_global.png")
    print(f"  - reports/figures/correlations_par_axe.png")

if __name__ == "__main__":
    run_fusion()
