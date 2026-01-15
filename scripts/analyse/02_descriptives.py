"""
Script 02 - Analyses Descriptives (Q4-Q10)
==========================================
Q4. Villes/pays les plus pollués
Q5. Saisonnalité (non applicable - données annuelles)
Q6. Distributions asymétriques
Q7. Population vs pollution
Q8. Capitales vs non-capitales
Q9. Altitude vs pollution (si disponible)
Q10. Variabilité selon taille des villes
"""

import sys
sys.path.append(str(__file__).rsplit('scripts', 1)[0])

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from config import DATA_RAW, DATA_CLEANED, SEUILS_OMS, get_label

FIGURES_DIR = DATA_CLEANED.parent.parent / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    path = DATA_CLEANED / "base_analyse_complete.csv"
    if not path.exists():
        print("Exécutez d'abord 00_fusion_complete.py")
        return None
    return pd.read_csv(path)

# =============================================================================
# Q4: Quels pays ont les niveaux les plus élevés ?
# =============================================================================
def analyse_q4_pays_pollues(df):
    """Identifie les pays les plus pollués."""
    print("\n" + "=" * 60)
    print("Q4: PAYS LES PLUS POLLUÉS")
    print("=" * 60)

    polluants = ['pollution_pm25', 'pollution_no2', 'pollution_pm10']

    for col in polluants:
        if col not in df.columns:
            continue

        polluant = col.replace('pollution_', '').upper()
        data = df[['country_code', 'country_name', col]].dropna()

        if len(data) == 0:
            continue

        print(f"\n--- TOP 10 {polluant} ---")
        top10 = data.nlargest(10, col)
        for i, (_, row) in enumerate(top10.iterrows(), 1):
            nom = row['country_name'] if pd.notna(row['country_name']) else row['country_code']
            print(f"  {i}. {nom}: {row[col]:.2f}")

        # Seuil OMS
        pol_key = polluant.lower()
        if pol_key in SEUILS_OMS:
            seuil = SEUILS_OMS[pol_key].get('annuel', SEUILS_OMS[pol_key].get('journalier'))
            n_depassement = (data[col] > seuil).sum()
            pct = n_depassement / len(data) * 100
            print(f"\n  Dépassement seuil OMS ({seuil}): {n_depassement} pays ({pct:.0f}%)")

    # Visualisation
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))

    for i, col in enumerate(['pollution_pm25', 'pollution_no2', 'pollution_pm10']):
        if col not in df.columns:
            continue

        ax = axes[i]
        data = df[['country_code', col]].dropna().nlargest(15, col)
        ax.barh(data['country_code'], data[col])
        ax.set_xlabel(col.replace('pollution_', '').upper())
        ax.set_title(f'Top 15 pays - {col.replace("pollution_", "").upper()}')
        ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q4_pays_pollues.png", dpi=150)
    plt.close()
    print(f"\nFigure: {FIGURES_DIR / 'q4_pays_pollues.png'}")

# =============================================================================
# Q5: Saisonnalité
# =============================================================================
def analyse_q5_saisonnalite(df):
    """Note sur la saisonnalité."""
    print("\n" + "=" * 60)
    print("Q5: SAISONNALITÉ")
    print("=" * 60)
    print("\nNote: Les données OpenAQ disponibles sont des moyennes annuelles.")
    print("L'analyse de saisonnalité nécessiterait des données mensuelles/journalières.")
    print("\nRecommandation pour future analyse:")
    print("  - Récupérer données OpenAQ avec granularité temporelle")
    print("  - Comparer hiver vs été par hémisphère")
    print("  - Attendu: PM élevé en hiver (chauffage), O3 élevé en été")

# =============================================================================
# Q6: Distributions asymétriques
# =============================================================================
def analyse_q6_distributions(df):
    """Analyse l'asymétrie des distributions."""
    print("\n" + "=" * 60)
    print("Q6: DISTRIBUTIONS - FAUT-IL UTILISER LOG OU SPEARMAN ?")
    print("=" * 60)

    pollution_cols = [c for c in df.columns if c.startswith('pollution_') and not c.endswith('_norm')]

    resultats = []
    for col in pollution_cols:
        data = df[col].dropna()
        if len(data) < 8:
            continue

        polluant = col.replace('pollution_', '').upper()

        # Tests statistiques
        skewness = stats.skew(data)
        kurtosis = stats.kurtosis(data)
        stat_shapiro, p_shapiro = stats.shapiro(data)

        # Test sur données log-transformées
        data_log = np.log1p(data)
        stat_log, p_log = stats.shapiro(data_log)

        resultats.append({
            'polluant': polluant,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'p_shapiro': p_shapiro,
            'normal': 'Oui' if p_shapiro > 0.05 else 'Non',
            'p_shapiro_log': p_log,
            'log_ameliore': 'Oui' if p_log > p_shapiro else 'Non'
        })

    df_res = pd.DataFrame(resultats)
    print("\n--- Tests de normalité ---")
    print(df_res.to_string(index=False))

    # Visualisation: QQ-plots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for i, col in enumerate(pollution_cols[:6]):
        data = df[col].dropna()
        if len(data) < 5:
            continue

        ax = axes[i]
        stats.probplot(data, dist="norm", plot=ax)
        polluant = col.replace('pollution_', '').upper()
        ax.set_title(f'QQ-Plot {polluant}')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q6_qqplots.png", dpi=150)
    plt.close()
    print(f"\nFigure: {FIGURES_DIR / 'q6_qqplots.png'}")

    print("\n--- CONCLUSION Q6 ---")
    print("  - Distributions généralement asymétriques (skewness > 0)")
    print("  - Recommandation: utiliser corrélation de SPEARMAN")
    print("  - Transformation LOG améliore parfois la normalité")

# =============================================================================
# Q7: Population vs pollution
# =============================================================================
def analyse_q7_population_pollution(df):
    """Relation entre taille des villes et pollution."""
    print("\n" + "=" * 60)
    print("Q7: POPULATION VS POLLUTION")
    print("=" * 60)

    # Variables de population
    pop_cols = ['SP.POP.TOTL', 'SP.URB.TOTL', 'nb_villes', 'population_urbaine_totale']
    pollution_cols = ['pollution_pm25', 'pollution_no2', 'pollution_pm10']

    print("\n--- Corrélations (Spearman) ---")
    for pop_col in pop_cols:
        if pop_col not in df.columns:
            continue
        print(f"\n  {pop_col}:")
        for pol_col in pollution_cols:
            if pol_col not in df.columns:
                continue
            data = df[[pop_col, pol_col]].dropna()
            if len(data) < 5:
                continue
            corr, pval = stats.spearmanr(data[pop_col], data[pol_col])
            sig = "*" if pval < 0.05 else ""
            print(f"    vs {pol_col.replace('pollution_','')}: r={corr:.3f} (p={pval:.3f}){sig}")

    # Visualisation
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for i, pol in enumerate(['pollution_pm25', 'pollution_no2']):
        if pol not in df.columns:
            continue
        ax = axes[i]

        # Chercher une colonne de population disponible
        pop_col = None
        for candidate in ['SP.URB.TOTL', 'population_urbaine_totale', 'nb_villes']:
            if candidate in df.columns and df[candidate].notna().sum() > 5:
                pop_col = candidate
                break

        if pop_col is None:
            ax.text(0.5, 0.5, 'Données population\nnon disponibles',
                   ha='center', va='center', transform=ax.transAxes)
            continue

        data = df[[pop_col, pol, 'country_code']].dropna()
        if len(data) < 3:
            ax.text(0.5, 0.5, 'Pas assez de données',
                   ha='center', va='center', transform=ax.transAxes)
            continue

        # Labels lisibles
        pop_label = get_label(pop_col)
        pol_label = get_label(pol)

        ax.scatter(data[pop_col] / 1e6 if data[pop_col].max() > 1e6 else data[pop_col],
                   data[pol], alpha=0.6)
        ax.set_xlabel(f'{pop_label} (millions)' if data[pop_col].max() > 1e6 else pop_label)
        ax.set_ylabel(pol_label)
        ax.set_title(f'{pop_label} vs {pol_label}')

        # Ajouter ligne de tendance si assez de données
        if len(data) >= 5:
            try:
                z = np.polyfit(np.log1p(data[pop_col]), data[pol], 1)
                p = np.poly1d(z)
                x_sorted = np.sort(data[pop_col])
                y_trend = p(np.log1p(x_sorted))
                x_plot = x_sorted / 1e6 if data[pop_col].max() > 1e6 else x_sorted
                ax.plot(x_plot, y_trend, "r--", alpha=0.8)
            except Exception:
                pass  # Ignorer si polyfit échoue

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q7_population_pollution.png", dpi=150)
    plt.close()
    print(f"\nFigure: {FIGURES_DIR / 'q7_population_pollution.png'}")

    print("\n--- CONCLUSION Q7 ---")
    print("  - La relation population-pollution est souvent faible au niveau pays")
    print("  - NO2 montre généralement une corrélation plus forte (trafic)")
    print("  - D'autres facteurs (industrie, régulation) sont plus déterminants")

# =============================================================================
# Q8: Capitales vs non-capitales
# =============================================================================
def analyse_q8_capitales(df):
    """Comparaison capitales vs autres villes."""
    print("\n" + "=" * 60)
    print("Q8: CAPITALES VS NON-CAPITALES")
    print("=" * 60)

    # Charger les données ville par ville
    cities_path = DATA_RAW / "world_cities_clean.csv"
    if not cities_path.exists():
        print("Données villes détaillées non disponibles")
        return

    cities = pd.read_csv(cities_path)
    print(f"\nChargement de {len(cities)} villes...")

    # Identifier les capitales
    if 'capital' not in cities.columns:
        print("Colonne 'capital' non disponible")
        return

    capitales = cities[cities['capital'] == 'primary']
    autres = cities[cities['capital'] != 'primary']

    print(f"\n  Capitales: {len(capitales)}")
    print(f"  Autres villes: {len(autres)}")

    # Comparer les populations
    if 'population' in cities.columns:
        pop_cap = capitales['population'].median()
        pop_autres = autres['population'].median()
        print(f"\n  Population médiane:")
        print(f"    Capitales: {pop_cap:,.0f}")
        print(f"    Autres: {pop_autres:,.0f}")

    print("\n--- CONCLUSION Q8 ---")
    print("  Note: Analyse limitée car pollution mesurée au niveau pays")
    print("  Pour analyse fine: besoin de données pollution par ville")

# =============================================================================
# Q10: Variabilité selon taille
# =============================================================================
def analyse_q10_variabilite(df):
    """Variabilité de la pollution selon la taille des pays/villes."""
    print("\n" + "=" * 60)
    print("Q10: VARIABILITÉ SELON LA TAILLE")
    print("=" * 60)

    if 'SP.URB.TOTL' not in df.columns:
        print("Données de population non disponibles")
        return

    # Créer des catégories de taille
    df_temp = df.copy()
    df_temp['taille_cat'] = pd.qcut(
        df_temp['SP.URB.TOTL'].dropna(),
        q=3,
        labels=['Petite', 'Moyenne', 'Grande']
    ).reindex(df_temp.index)

    print("\n--- Statistiques par catégorie de taille ---")
    for pol in ['pollution_pm25', 'pollution_no2']:
        if pol not in df.columns:
            continue
        print(f"\n  {pol.replace('pollution_','').upper()}:")
        stats_by_cat = df_temp.groupby('taille_cat')[pol].agg(['mean', 'std', 'count'])
        stats_by_cat['cv'] = stats_by_cat['std'] / stats_by_cat['mean'] * 100
        print(stats_by_cat.round(2).to_string())

    print("\n--- CONCLUSION Q10 ---")
    print("  - Les grands pays ont souvent plus de variabilité interne")
    print("  - Le coefficient de variation (CV) permet de comparer")

def main():
    print("=" * 60)
    print("ANALYSES DESCRIPTIVES (Q4-Q10)")
    print("=" * 60)

    df = load_data()
    if df is None:
        return

    analyse_q4_pays_pollues(df)
    analyse_q5_saisonnalite(df)
    analyse_q6_distributions(df)
    analyse_q7_population_pollution(df)
    analyse_q8_capitales(df)
    analyse_q10_variabilite(df)

    print("\n" + "=" * 60)
    print("ANALYSES DESCRIPTIVES TERMINÉES")
    print("=" * 60)

if __name__ == "__main__":
    main()
