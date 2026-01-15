"""
Script 04 - Analyse en Composantes Principales (Q16-Q18)
========================================================
Q16. Axes principaux de variance
Q17. Regroupements naturels
Q18. Robustesse de l'ACP
"""

import sys
sys.path.append(str(__file__).rsplit('scripts', 1)[0])

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from config import DATA_CLEANED

FIGURES_DIR = DATA_CLEANED.parent.parent / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    path = DATA_CLEANED / "base_analyse_complete.csv"
    if not path.exists():
        print("Exécutez d'abord 00_fusion_complete.py")
        return None
    return pd.read_csv(path)

def prepare_data_for_pca(df):
    """Prépare les données pour l'ACP."""
    # Variables pour l'ACP - pollution
    vars_pollution = ['pollution_pm25', 'pollution_no2', 'pollution_pm10', 'pollution_o3', 'pollution_so2']

    # Variables socio-économiques - chercher avec différents préfixes
    vars_socioeco_candidates = [
        ('NY.GDP.PCAP.CD', 'eco_NY_GDP_PCAP_CD'),      # PIB/hab
        ('SP.URB.TOTL.IN.ZS', 'demo_SP_URB_TOTL_IN_ZS'),   # % urbain
        ('NV.IND.TOTL.ZS', 'eco_NV_IND_TOTL_ZS'),      # % industrie
        ('IS.VEH.NVEH.P3', 'transport_IS_VEH_NVEH_P3'),      # Véhicules
        ('EN.ATM.CO2E.PC', 'energie_EN_ATM_CO2E_PC'),      # CO2/hab
        ('EG.USE.PCAP.KG.OE', 'energie_EG_USE_PCAP_KG_OE'),   # Énergie/hab
        ('EN.POP.DNST', 'demo_EN_POP_DNST'),         # Densité
        ('SP.POP.TOTL', 'demo_SP_POP_TOTL')          # Population
    ]

    # Trouver les variables disponibles
    all_vars = []
    for v in vars_pollution:
        if v in df.columns:
            all_vars.append(v)

    for v1, v2 in vars_socioeco_candidates:
        if v1 in df.columns:
            all_vars.append(v1)
        elif v2 in df.columns:
            all_vars.append(v2)

    # Filtrer les variables qui ont au moins quelques données
    valid_vars = []
    for v in all_vars:
        n_valid = df[v].notna().sum()
        if n_valid >= 10:  # Au moins 10 observations
            valid_vars.append(v)
        else:
            print(f"  Variable {v} ignorée (seulement {n_valid} valeurs)")

    all_vars = valid_vars

    # Garder uniquement les pays avec suffisamment de données
    df_pca = df[['country_code', 'country_name'] + all_vars].copy()
    # Au moins quelques polluants présents
    pollution_in_vars = [v for v in all_vars if v.startswith('pollution_')]
    if pollution_in_vars:
        df_pca = df_pca.dropna(subset=pollution_in_vars[:min(3, len(pollution_in_vars))], how='all')

    print(f"Variables pour ACP: {len(all_vars)}")
    print(f"Pays: {len(df_pca)}")

    return df_pca, all_vars

# =============================================================================
# Q16: Axes principaux
# =============================================================================
def analyse_q16_axes_principaux(df):
    """Identifie les axes principaux de variance."""
    print("\n" + "=" * 60)
    print("Q16: AXES PRINCIPAUX DE VARIANCE")
    print("=" * 60)

    df_pca, vars_list = prepare_data_for_pca(df)

    if len(df_pca) < 10:
        print("Pas assez de données pour l'ACP")
        return None, None, None

    if len(vars_list) < 3:
        print(f"Pas assez de variables pour l'ACP ({len(vars_list)} < 3)")
        return None, None, None

    # Extraire les données numériques
    X = df_pca[vars_list].values

    # Identifier les colonnes avec au moins une valeur non-NaN
    valid_col_mask = ~np.all(np.isnan(X), axis=0)
    valid_vars = [v for v, valid in zip(vars_list, valid_col_mask) if valid]
    X = X[:, valid_col_mask]

    if len(valid_vars) < 3:
        print(f"Pas assez de variables valides pour l'ACP ({len(valid_vars)} < 3)")
        return None, None, None

    print(f"Variables retenues après filtrage: {len(valid_vars)}")

    # Imputer les valeurs manquantes
    imputer = SimpleImputer(strategy='median')
    X_imputed = imputer.fit_transform(X)

    # Standardiser
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    # ACP
    n_components = min(5, len(valid_vars), len(df_pca) - 1)
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X_scaled)

    # Variance expliquée
    print("\n--- Variance expliquée par composante ---")
    for i, var in enumerate(pca.explained_variance_ratio_):
        cumul = sum(pca.explained_variance_ratio_[:i+1])
        print(f"  PC{i+1}: {var*100:.1f}% (cumulé: {cumul*100:.1f}%)")

    # Contributions des variables
    print("\n--- Contribution des variables aux 3 premiers axes ---")

    # Renommer les variables pour lisibilité
    rename_map = {
        'pollution_pm25': 'PM2.5', 'pollution_no2': 'NO2', 'pollution_pm10': 'PM10',
        'pollution_o3': 'O3', 'pollution_so2': 'SO2',
        'NY.GDP.PCAP.CD': 'PIB/hab', 'SP.URB.TOTL.IN.ZS': '% Urbain',
        'NV.IND.TOTL.ZS': '% Industrie', 'IS.VEH.NVEH.P3': 'Véhicules',
        'EN.ATM.CO2E.PC': 'CO2/hab', 'EG.USE.PCAP.KG.OE': 'Énergie/hab',
        'EN.POP.DNST': 'Densité', 'SP.POP.TOTL': 'Population',
        'eco_NY_GDP_PCAP_CD': 'PIB/hab', 'demo_SP_URB_TOTL_IN_ZS': '% Urbain',
        'eco_NV_IND_TOTL_ZS': '% Industrie', 'transport_IS_VEH_NVEH_P3': 'Véhicules',
        'energie_EN_ATM_CO2E_PC': 'CO2/hab', 'energie_EG_USE_PCAP_KG_OE': 'Énergie/hab',
        'demo_EN_POP_DNST': 'Densité', 'demo_SP_POP_TOTL': 'Population'
    }
    var_names = [rename_map.get(v, v) for v in valid_vars]

    loadings = pd.DataFrame(
        pca.components_.T,
        index=var_names,
        columns=[f'PC{i+1}' for i in range(n_components)]
    )
    print(loadings.round(3).to_string())

    # Interprétation des axes
    print("\n--- Interprétation des axes ---")
    for i in range(min(3, n_components)):
        pc_loadings = loadings[f'PC{i+1}'].sort_values(key=abs, ascending=False)
        top_pos = pc_loadings[pc_loadings > 0.3].index.tolist()
        top_neg = pc_loadings[pc_loadings < -0.3].index.tolist()
        print(f"\n  PC{i+1} ({pca.explained_variance_ratio_[i]*100:.1f}%):")
        if top_pos:
            print(f"    Positif: {', '.join(top_pos)}")
        if top_neg:
            print(f"    Négatif: {', '.join(top_neg)}")

    # Visualisation: Scree plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    ax.bar(range(1, n_components+1), pca.explained_variance_ratio_ * 100)
    ax.plot(range(1, n_components+1), np.cumsum(pca.explained_variance_ratio_) * 100, 'ro-')
    ax.set_xlabel('Composante principale')
    ax.set_ylabel('Variance expliquée (%)')
    ax.set_title('Scree Plot')
    ax.axhline(y=80, color='g', linestyle='--', alpha=0.5)

    # Biplot
    ax = axes[1]
    ax.scatter(X_pca[:, 0], X_pca[:, 1], alpha=0.5)

    # Ajouter les vecteurs de chargement
    for i, (x, y) in enumerate(zip(pca.components_[0], pca.components_[1])):
        ax.arrow(0, 0, x*3, y*3, head_width=0.1, head_length=0.05, fc='red', ec='red')
        ax.text(x*3.2, y*3.2, var_names[i], fontsize=8, ha='center')

    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
    ax.set_title('Biplot ACP')
    ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax.axvline(x=0, color='gray', linestyle='-', alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q16_acp_axes.png", dpi=150)
    plt.close()
    print(f"\n  Figure: q16_acp_axes.png")

    # Retourner aussi les variables valides pour les autres fonctions
    df_pca['_valid_vars'] = str(valid_vars)  # Stocker pour référence
    return pca, X_pca, df_pca, valid_vars

# =============================================================================
# Q17: Regroupements naturels
# =============================================================================
def analyse_q17_regroupements(df, pca_result, X_pca, df_pca):
    """Analyse les regroupements naturels des pays."""
    print("\n" + "=" * 60)
    print("Q17: REGROUPEMENTS NATURELS")
    print("=" * 60)

    if X_pca is None:
        print("ACP non disponible")
        return

    # Ajouter les coordonnées PCA au dataframe
    df_pca = df_pca.copy()
    df_pca['PC1'] = X_pca[:, 0]
    df_pca['PC2'] = X_pca[:, 1]

    # Ajouter catégorie de revenu si disponible
    if 'categorie_revenu' in df.columns:
        df_pca = df_pca.merge(
            df[['country_code', 'categorie_revenu']],
            on='country_code',
            how='left'
        )

    # Visualisation par catégorie de revenu
    fig, ax = plt.subplots(figsize=(12, 8))

    if 'categorie_revenu' in df_pca.columns:
        colors = {'Faible': 'red', 'Moyen-inférieur': 'orange',
                  'Moyen-supérieur': 'yellow', 'Élevé': 'green'}
        for cat, color in colors.items():
            mask = df_pca['categorie_revenu'] == cat
            if mask.sum() > 0:
                ax.scatter(df_pca.loc[mask, 'PC1'], df_pca.loc[mask, 'PC2'],
                          c=color, label=cat, alpha=0.7, s=100)
    else:
        ax.scatter(df_pca['PC1'], df_pca['PC2'], alpha=0.7, s=100)

    # Annoter les pays
    for _, row in df_pca.iterrows():
        ax.annotate(row['country_code'], (row['PC1'], row['PC2']),
                   fontsize=8, alpha=0.7)

    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')
    ax.set_title('Regroupement des pays dans l\'espace ACP')
    ax.legend()
    ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax.axvline(x=0, color='gray', linestyle='-', alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q17_regroupements.png", dpi=150)
    plt.close()
    print(f"\n  Figure: q17_regroupements.png")

    # Identifier les clusters
    print("\n--- Pays par quadrant ---")
    q1 = df_pca[(df_pca['PC1'] > 0) & (df_pca['PC2'] > 0)]['country_code'].tolist()
    q2 = df_pca[(df_pca['PC1'] < 0) & (df_pca['PC2'] > 0)]['country_code'].tolist()
    q3 = df_pca[(df_pca['PC1'] < 0) & (df_pca['PC2'] < 0)]['country_code'].tolist()
    q4 = df_pca[(df_pca['PC1'] > 0) & (df_pca['PC2'] < 0)]['country_code'].tolist()

    print(f"  Q1 (PC1+, PC2+): {', '.join(q1[:10])}")
    print(f"  Q2 (PC1-, PC2+): {', '.join(q2[:10])}")
    print(f"  Q3 (PC1-, PC2-): {', '.join(q3[:10])}")
    print(f"  Q4 (PC1+, PC2-): {', '.join(q4[:10])}")

    print("\n--- CONCLUSION Q17 ---")
    print("  Les pays se regroupent principalement par niveau de développement")
    print("  Les outliers méritent une analyse spécifique")

# =============================================================================
# Q18: Robustesse de l'ACP
# =============================================================================
def analyse_q18_robustesse(df):
    """Teste la robustesse de l'ACP."""
    print("\n" + "=" * 60)
    print("Q18: ROBUSTESSE DE L'ACP")
    print("=" * 60)

    df_pca, vars_list = prepare_data_for_pca(df)

    if len(df_pca) < 10 or len(vars_list) < 4:
        print("Pas assez de données")
        return

    # Préparer les données
    X = df_pca[vars_list].values
    imputer = SimpleImputer(strategy='median')
    X_imputed = imputer.fit_transform(X)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    # ACP de référence
    pca_ref = PCA(n_components=3)
    pca_ref.fit(X_scaled)

    print("\n--- Test de stabilité (leave-one-out sur variables) ---")

    results = []
    for i, var in enumerate(vars_list):
        # ACP sans cette variable
        vars_subset = [v for j, v in enumerate(vars_list) if j != i]
        X_subset = df_pca[vars_subset].values
        X_sub_imp = SimpleImputer(strategy='median').fit_transform(X_subset)
        X_sub_scaled = StandardScaler().fit_transform(X_sub_imp)

        pca_sub = PCA(n_components=min(3, len(vars_subset)))
        pca_sub.fit(X_sub_scaled)

        # Comparer la variance expliquée
        var_exp_ref = sum(pca_ref.explained_variance_ratio_[:2])
        var_exp_sub = sum(pca_sub.explained_variance_ratio_[:2])

        results.append({
            'variable_exclue': var,
            'var_exp_2pc': var_exp_sub * 100,
            'delta': (var_exp_sub - var_exp_ref) * 100
        })

    df_results = pd.DataFrame(results)
    print(df_results.to_string(index=False))

    # Identifier les variables les plus influentes
    df_results = df_results.sort_values('delta', key=abs, ascending=False)
    print("\n--- Variables les plus influentes ---")
    print("  (retirer ces variables change le plus l'ACP)")
    for _, row in df_results.head(3).iterrows():
        print(f"  {row['variable_exclue']}: delta = {row['delta']:.2f}%")

    print("\n--- CONCLUSION Q18 ---")
    print("  L'ACP est relativement stable si delta < 5%")
    print("  Les variables avec gros delta sont critiques pour l'interprétation")

def main():
    print("=" * 60)
    print("ANALYSE EN COMPOSANTES PRINCIPALES (Q16-Q18)")
    print("=" * 60)

    df = load_data()
    if df is None:
        return

    result = analyse_q16_axes_principaux(df)

    if result[0] is not None:
        pca, X_pca, df_pca, valid_vars = result
        analyse_q17_regroupements(df, pca, X_pca, df_pca)
    else:
        print("\nACP non disponible - données insuffisantes")

    analyse_q18_robustesse(df)

    print("\n" + "=" * 60)
    print("ANALYSE ACP TERMINÉE")
    print("=" * 60)

if __name__ == "__main__":
    main()
