"""
Script 06 - Modèles Prédictifs (Q22-Q24)
========================================
Q22. Prédire PM2.5 à partir des variables urbaines/WB
Q23. Variables les plus déterminantes
Q24. Généralisation du modèle
"""

import sys
sys.path.append(str(__file__).rsplit('scripts', 1)[0])

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import cross_val_score, LeaveOneOut, train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')
from config import DATA_CLEANED

FIGURES_DIR = DATA_CLEANED.parent.parent / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    path = DATA_CLEANED / "base_analyse_complete.csv"
    if not path.exists():
        print("Exécutez d'abord 00_fusion_complete.py")
        return None
    return pd.read_csv(path)

def prepare_ml_data(df, target='pollution_pm25'):
    """Prépare les données pour le machine learning."""
    # Features avec alternatives (nom original, nom avec préfixe)
    feature_candidates = [
        ('NY.GDP.PCAP.CD', 'eco_NY_GDP_PCAP_CD'),      # PIB/hab
        ('SP.URB.TOTL.IN.ZS', 'demo_SP_URB_TOTL_IN_ZS'),   # % urbain
        ('NV.IND.TOTL.ZS', 'eco_NV_IND_TOTL_ZS'),      # % industrie
        ('IS.VEH.NVEH.P3', 'transport_IS_VEH_NVEH_P3'),      # Véhicules
        ('EN.ATM.CO2E.PC', 'energie_EN_ATM_CO2E_PC'),      # CO2/hab
        ('EG.USE.PCAP.KG.OE', 'energie_EG_USE_PCAP_KG_OE'),   # Énergie/hab
        ('EN.POP.DNST', 'demo_EN_POP_DNST'),         # Densité
        ('EG.ELC.FOSL.ZS', 'energie_EG_ELC_FOSL_ZS'),      # % électricité fossile
        ('nb_villes', None),           # Nombre de villes
        ('SP.POP.TOTL', 'demo_SP_POP_TOTL'),          # Population totale
        ('population_urbaine_totale', None),  # Population urbaine
    ]

    # Trouver les features disponibles
    available_features = []
    for v1, v2 in feature_candidates:
        if v1 in df.columns and df[v1].notna().sum() >= 5:
            available_features.append(v1)
        elif v2 is not None and v2 in df.columns and df[v2].notna().sum() >= 5:
            available_features.append(v2)

    if target not in df.columns:
        print(f"Variable cible {target} non disponible")
        return None, None, None, None

    if len(available_features) == 0:
        print("Aucune feature disponible")
        return None, None, None, None

    # Créer le dataset
    df_ml = df[['country_code'] + available_features + [target]].copy()
    df_ml = df_ml.dropna(subset=[target])

    # Features et target
    X = df_ml[available_features]
    y = df_ml[target]
    country_codes = df_ml['country_code']

    # Identifier les colonnes qui ont au moins une valeur non-NaN
    valid_features = []
    for col in available_features:
        if X[col].notna().sum() > 0:
            valid_features.append(col)
        else:
            print(f"  Feature {col} ignorée (aucune valeur)")

    if len(valid_features) == 0:
        print("Aucune feature valide après filtrage")
        return None, None, None, None

    X = X[valid_features]

    # Imputer les valeurs manquantes
    imputer = SimpleImputer(strategy='median')
    X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=valid_features, index=X.index)

    print(f"Features: {len(valid_features)}")
    print(f"Échantillons: {len(y)}")
    print(f"Target: {target}")

    return X_imputed, y.reset_index(drop=True), valid_features, country_codes.reset_index(drop=True)

# =============================================================================
# Q22: Prédire PM2.5
# =============================================================================
def analyse_q22_prediction_pm25(df):
    """Construit des modèles pour prédire PM2.5."""
    print("\n" + "=" * 60)
    print("Q22: PRÉDIRE PM2.5 À PARTIR DES VARIABLES URBAINES/WB")
    print("=" * 60)

    X, y, feature_names, _ = prepare_ml_data(df, target='pollution_pm25')

    if X is None or len(y) < 10:
        print("Pas assez de données")
        return None, None

    # Standardiser
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Modèles à tester
    models = {
        'Régression linéaire': LinearRegression(),
        'Ridge (L2)': Ridge(alpha=1.0),
        'Lasso (L1)': Lasso(alpha=0.1),
        'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
    }

    print("\n--- Performance des modèles (CV 5-fold) ---")
    results = []
    for name, model in models.items():
        # Cross-validation
        cv_scores = cross_val_score(model, X_scaled, y, cv=min(5, len(y)-1), scoring='r2')
        cv_mae = -cross_val_score(model, X_scaled, y, cv=min(5, len(y)-1), scoring='neg_mean_absolute_error')

        # Entraîner sur tout le dataset pour les coefficients
        model.fit(X_scaled, y)
        y_pred = model.predict(X_scaled)
        r2_train = r2_score(y, y_pred)

        results.append({
            'Modèle': name,
            'R² CV': cv_scores.mean(),
            'R² std': cv_scores.std(),
            'MAE CV': cv_mae.mean(),
            'R² train': r2_train
        })

        print(f"\n  {name}:")
        print(f"    R² (CV): {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
        print(f"    MAE (CV): {cv_mae.mean():.2f} µg/m³")
        print(f"    R² (train): {r2_train:.3f}")

    df_results = pd.DataFrame(results)

    # Meilleur modèle
    best_model_name = df_results.loc[df_results['R² CV'].idxmax(), 'Modèle']
    print(f"\n  Meilleur modèle: {best_model_name}")

    # Visualisation
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Barplot des R²
    ax = axes[0]
    ax.bar(df_results['Modèle'], df_results['R² CV'])
    ax.errorbar(df_results['Modèle'], df_results['R² CV'], yerr=df_results['R² std'],
                fmt='none', color='black', capsize=3)
    ax.set_ylabel('R² (CV)')
    ax.set_title('Performance des modèles')
    ax.tick_params(axis='x', rotation=45)
    ax.axhline(y=0, color='gray', linestyle='--')

    # Scatter prédit vs réel (meilleur modèle)
    ax = axes[1]
    best_model = models[best_model_name]
    best_model.fit(X_scaled, y)
    y_pred = best_model.predict(X_scaled)

    ax.scatter(y, y_pred, alpha=0.6)
    ax.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', linewidth=2)
    ax.set_xlabel('PM2.5 réel (µg/m³)')
    ax.set_ylabel('PM2.5 prédit (µg/m³)')
    ax.set_title(f'{best_model_name}: Prédit vs Réel')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q22_prediction_pm25.png", dpi=150)
    plt.close()
    print(f"\n  Figure: q22_prediction_pm25.png")

    return best_model, feature_names

# =============================================================================
# Q23: Variables les plus déterminantes
# =============================================================================
def analyse_q23_feature_importance(df):
    """Identifie les variables les plus importantes."""
    print("\n" + "=" * 60)
    print("Q23: VARIABLES LES PLUS DÉTERMINANTES")
    print("=" * 60)

    X, y, feature_names, _ = prepare_ml_data(df, target='pollution_pm25')

    if X is None or len(y) < 10:
        print("Pas assez de données")
        return

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Méthode 1: Coefficients de régression linéaire
    print("\n--- Méthode 1: Coefficients régression linéaire ---")
    lr = LinearRegression()
    lr.fit(X_scaled, y)

    coef_df = pd.DataFrame({
        'Variable': feature_names,
        'Coefficient': lr.coef_
    }).sort_values('Coefficient', key=abs, ascending=False)

    print(coef_df.to_string(index=False))

    # Méthode 2: Feature importance Random Forest
    print("\n--- Méthode 2: Importance Random Forest ---")
    rf = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    rf.fit(X_scaled, y)

    imp_df = pd.DataFrame({
        'Variable': feature_names,
        'Importance': rf.feature_importances_
    }).sort_values('Importance', ascending=False)

    print(imp_df.to_string(index=False))

    # Méthode 3: Permutation importance
    print("\n--- Méthode 3: Permutation importance ---")
    from sklearn.inspection import permutation_importance
    perm_imp = permutation_importance(rf, X_scaled, y, n_repeats=10, random_state=42)

    perm_df = pd.DataFrame({
        'Variable': feature_names,
        'Importance': perm_imp.importances_mean
    }).sort_values('Importance', ascending=False)

    print(perm_df.to_string(index=False))

    # Visualisation comparative
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Régression linéaire
    ax = axes[0]
    colors = ['green' if c > 0 else 'red' for c in coef_df['Coefficient']]
    ax.barh(coef_df['Variable'], coef_df['Coefficient'].abs(), color=colors)
    ax.set_xlabel('|Coefficient|')
    ax.set_title('Régression linéaire')
    ax.invert_yaxis()

    # Random Forest
    ax = axes[1]
    ax.barh(imp_df['Variable'], imp_df['Importance'])
    ax.set_xlabel('Importance')
    ax.set_title('Random Forest')
    ax.invert_yaxis()

    # Permutation
    ax = axes[2]
    ax.barh(perm_df['Variable'], perm_df['Importance'])
    ax.set_xlabel('Importance (permutation)')
    ax.set_title('Permutation Importance')
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q23_feature_importance.png", dpi=150)
    plt.close()
    print(f"\n  Figure: q23_feature_importance.png")

    # Synthèse
    print("\n--- SYNTHÈSE Q23 ---")
    print("  Variables généralement importantes:")

    # Compter le rang de chaque variable
    ranks = {}
    for var in feature_names:
        r1 = coef_df[coef_df['Variable'] == var].index[0] if len(coef_df[coef_df['Variable'] == var]) > 0 else 99
        r2 = imp_df[imp_df['Variable'] == var].index[0] if len(imp_df[imp_df['Variable'] == var]) > 0 else 99
        ranks[var] = (list(coef_df['Variable']).index(var) if var in list(coef_df['Variable']) else 99) + \
                     (list(imp_df['Variable']).index(var) if var in list(imp_df['Variable']) else 99)

    for var in sorted(ranks, key=ranks.get)[:5]:
        print(f"    - {var}")

# =============================================================================
# Q24: Généralisation du modèle
# =============================================================================
def analyse_q24_generalisation(df):
    """Évalue la capacité de généralisation du modèle."""
    print("\n" + "=" * 60)
    print("Q24: GÉNÉRALISATION DU MODÈLE")
    print("=" * 60)

    X, y, feature_names, country_codes = prepare_ml_data(df, target='pollution_pm25')

    if X is None or len(y) < 15:
        print("Pas assez de données pour évaluer la généralisation")
        return

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Test 1: Train/Test split classique
    print("\n--- Test 1: Train/Test split (80/20) ---")
    X_train, X_test, y_train, y_test, codes_train, codes_test = train_test_split(
        X_scaled, y, country_codes, test_size=0.2, random_state=42
    )

    models = {
        'Linear': LinearRegression(),
        'Ridge': Ridge(alpha=1.0),
        'RandomForest': RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    }

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)

        r2_train = r2_score(y_train, y_pred_train)
        r2_test = r2_score(y_test, y_pred_test)
        overfit = r2_train - r2_test

        print(f"  {name}: R2 train={r2_train:.3f}, R2 test={r2_test:.3f}, delta={overfit:.3f}")

    # Test 2: Leave-One-Out
    print("\n--- Test 2: Leave-One-Out Cross-Validation ---")
    loo = LeaveOneOut()

    for name, model in list(models.items())[:2]:  # Seulement LR et Ridge (plus rapide)
        y_pred_loo = np.zeros(len(y))
        for train_idx, test_idx in loo.split(X_scaled):
            model.fit(X_scaled[train_idx], y.iloc[train_idx])
            y_pred_loo[test_idx] = model.predict(X_scaled[test_idx])

        r2_loo = r2_score(y, y_pred_loo)
        mae_loo = mean_absolute_error(y, y_pred_loo)
        print(f"  {name}: R² LOO={r2_loo:.3f}, MAE LOO={mae_loo:.2f}")

    # Analyse des résidus
    print("\n--- Analyse des résidus ---")
    rf = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    rf.fit(X_scaled, y)
    y_pred = rf.predict(X_scaled)
    residuals = y - y_pred

    print(f"  Moyenne résidus: {residuals.mean():.2f}")
    print(f"  Écart-type résidus: {residuals.std():.2f}")

    # Pays avec grandes erreurs
    df_residuals = pd.DataFrame({
        'country_code': country_codes.values,
        'y_real': y.values,
        'y_pred': y_pred,
        'residual': residuals.values,
        'abs_residual': np.abs(residuals.values)
    })

    print("\n  Pays avec les plus grandes erreurs:")
    for _, row in df_residuals.nlargest(5, 'abs_residual').iterrows():
        print(f"    {row['country_code']}: réel={row['y_real']:.1f}, prédit={row['y_pred']:.1f}, erreur={row['residual']:.1f}")

    # Visualisation
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Distribution des résidus
    ax = axes[0]
    ax.hist(residuals, bins=15, edgecolor='black', alpha=0.7)
    ax.axvline(x=0, color='red', linestyle='--')
    ax.set_xlabel('Résidu (réel - prédit)')
    ax.set_ylabel('Fréquence')
    ax.set_title('Distribution des résidus')

    # Résidus vs valeurs prédites
    ax = axes[1]
    ax.scatter(y_pred, residuals, alpha=0.6)
    ax.axhline(y=0, color='red', linestyle='--')
    ax.set_xlabel('PM2.5 prédit')
    ax.set_ylabel('Résidu')
    ax.set_title('Résidus vs Valeurs prédites')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q24_generalisation.png", dpi=150)
    plt.close()
    print(f"\n  Figure: q24_generalisation.png")

    print("\n--- CONCLUSION Q24 ---")
    print("  - Si R² train >> R² test: surapprentissage")
    print("  - Modèles simples (Ridge) généralisent souvent mieux")
    print("  - Les grandes erreurs méritent investigation (données, outliers)")

def main():
    print("=" * 60)
    print("MODÈLES PRÉDICTIFS (Q22-Q24)")
    print("=" * 60)

    df = load_data()
    if df is None:
        return

    analyse_q22_prediction_pm25(df)
    analyse_q23_feature_importance(df)
    analyse_q24_generalisation(df)

    print("\n" + "=" * 60)
    print("MODÉLISATION TERMINÉE")
    print("=" * 60)

if __name__ == "__main__":
    main()
