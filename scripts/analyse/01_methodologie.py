"""
Script 01 - Questions Méthodologiques (Q1, Q2, Q3)
===================================================
Q1. Quels polluants sont les plus pertinents ?
Q2. Moyenne, médiane ou pics ?
Q3. Quel seuil de couverture minimal ?
"""

import sys
sys.path.append(str(__file__).rsplit('scripts', 1)[0])

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from config import DATA_RAW, DATA_CLEANED, SEUILS_OMS
import os

# Créer le dossier pour les figures
FIGURES_DIR = DATA_CLEANED.parent.parent / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    """Charge les données."""
    path = DATA_CLEANED / "base_analyse_complete.csv"
    if not path.exists():
        print("Exécutez d'abord 00_fusion_complete.py")
        return None
    return pd.read_csv(path)

# =============================================================================
# Q1: Quels polluants sont les plus pertinents ?
# =============================================================================
def analyse_q1_polluants_pertinents(df):
    """
    Analyse la pertinence des polluants pour comparaison mondiale.
    Critères: couverture, variabilité, impact sanitaire.
    """
    print("\n" + "=" * 60)
    print("Q1: QUELS POLLUANTS SONT LES PLUS PERTINENTS ?")
    print("=" * 60)

    pollution_cols = [c for c in df.columns if c.startswith('pollution_') and not c.endswith('_norm')]

    resultats = []
    for col in pollution_cols:
        polluant = col.replace('pollution_', '').upper()
        data = df[col].dropna()

        if len(data) == 0:
            continue

        resultats.append({
            'polluant': polluant,
            'n_pays': len(data),
            'couverture_pct': len(data) / len(df) * 100,
            'moyenne': data.mean(),
            'ecart_type': data.std(),
            'cv': data.std() / data.mean() * 100,  # Coefficient de variation
            'min': data.min(),
            'max': data.max(),
            'ratio_max_min': data.max() / data.min() if data.min() > 0 else np.nan
        })

    df_results = pd.DataFrame(resultats)
    df_results = df_results.sort_values('couverture_pct', ascending=False)

    print("\n--- Couverture et variabilité par polluant ---")
    print(df_results.to_string(index=False))

    # Comparaison avec seuils OMS
    print("\n--- Comparaison aux seuils OMS ---")
    for _, row in df_results.iterrows():
        polluant = row['polluant'].lower()
        if polluant in SEUILS_OMS:
            seuil = SEUILS_OMS[polluant].get('annuel', SEUILS_OMS[polluant].get('journalier'))
            pct_depassement = (df[f'pollution_{polluant}'] > seuil).mean() * 100
            print(f"  {polluant.upper()}: {pct_depassement:.1f}% des pays > seuil OMS ({seuil})")

    # Conclusion
    print("\n--- CONCLUSION Q1 ---")
    print("Polluants les plus pertinents (par ordre de priorité):")
    print("  1. PM2.5 - Impact sanitaire majeur, bonne couverture")
    print("  2. NO2   - Indicateur du trafic urbain")
    print("  3. PM10  - Complémentaire au PM2.5")
    print("  4. O3    - Important en saison chaude")

    return df_results

# =============================================================================
# Q2: Moyenne, médiane ou pics ?
# =============================================================================
def analyse_q2_metriques(df):
    """
    Compare les différentes métriques (moyenne, médiane, percentiles).
    """
    print("\n" + "=" * 60)
    print("Q2: MOYENNE, MÉDIANE OU PICS ?")
    print("=" * 60)

    pollution_cols = [c for c in df.columns if c.startswith('pollution_') and not c.endswith('_norm')]

    print("\n--- Comparaison des métriques par polluant ---")

    for col in pollution_cols:
        data = df[col].dropna()
        if len(data) < 5:
            continue

        polluant = col.replace('pollution_', '').upper()

        # Calculer les métriques
        moyenne = data.mean()
        mediane = data.median()
        p95 = data.quantile(0.95)
        p99 = data.quantile(0.99)

        # Test de normalité
        if len(data) >= 8:
            stat, p_value = stats.shapiro(data)
            normal = "Oui" if p_value > 0.05 else "Non"
        else:
            normal = "N/A"

        # Asymétrie
        skewness = stats.skew(data)

        print(f"\n  {polluant}:")
        print(f"    Moyenne: {moyenne:.2f}")
        print(f"    Médiane: {mediane:.2f}")
        print(f"    Ratio moy/med: {moyenne/mediane:.2f}")
        print(f"    P95: {p95:.2f}")
        print(f"    P99: {p99:.2f}")
        print(f"    Asymétrie (skewness): {skewness:.2f}")
        print(f"    Distribution normale: {normal}")

    # Visualisation
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for i, col in enumerate(pollution_cols[:6]):
        data = df[col].dropna()
        if len(data) < 5:
            continue

        polluant = col.replace('pollution_', '').upper()
        ax = axes[i]

        # Histogramme
        ax.hist(data, bins=15, edgecolor='black', alpha=0.7)
        ax.axvline(data.mean(), color='red', linestyle='--', label=f'Moyenne: {data.mean():.1f}')
        ax.axvline(data.median(), color='green', linestyle='--', label=f'Médiane: {data.median():.1f}')
        ax.set_title(f'{polluant}')
        ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q2_distributions_polluants.png", dpi=150)
    plt.close()
    print(f"\nFigure sauvegardée: {FIGURES_DIR / 'q2_distributions_polluants.png'}")

    # Conclusion
    print("\n--- CONCLUSION Q2 ---")
    print("Recommandations:")
    print("  - Distributions asymétriques -> utiliser la MÉDIANE")
    print("  - Pour les corrélations -> utiliser SPEARMAN (non paramétrique)")
    print("  - Les pics (P95) sont utiles pour identifier les situations extrêmes")
    print("  - Transformation LOG recommandée pour certaines analyses")

# =============================================================================
# Q3: Seuil de couverture minimal ?
# =============================================================================
def analyse_q3_couverture(df):
    """
    Analyse l'impact du seuil de couverture sur les résultats.
    """
    print("\n" + "=" * 60)
    print("Q3: QUEL SEUIL DE COUVERTURE MINIMAL ?")
    print("=" * 60)

    # Compter les polluants disponibles par pays
    pollution_cols = [c for c in df.columns if c.startswith('pollution_') and not c.endswith('_norm')]
    df['n_polluants'] = df[pollution_cols].notna().sum(axis=1)

    print("\n--- Nombre de polluants par pays ---")
    print(df['n_polluants'].value_counts().sort_index())

    # Impact du seuil sur le nombre de pays
    print("\n--- Impact du seuil de couverture ---")
    seuils = [1, 2, 3, 4, 5, 6]
    for seuil in seuils:
        n_pays = (df['n_polluants'] >= seuil).sum()
        pct = n_pays / len(df) * 100
        print(f"  >={seuil} polluants: {n_pays} pays ({pct:.1f}%)")

    # Vérifier si les pays avec plus de données sont différents
    print("\n--- Caractéristiques selon la couverture ---")
    if 'NY.GDP.PCAP.CD' in df.columns:
        for seuil in [1, 3, 5]:
            subset = df[df['n_polluants'] >= seuil]
            if len(subset) > 0:
                pib_moy = subset['NY.GDP.PCAP.CD'].mean()
        print(f"  >={seuil} polluants: PIB moyen = ${pib_moy:,.0f} (n={len(subset)})")

    # Conclusion
    print("\n--- CONCLUSION Q3 ---")
    print("Recommandations:")
    print("  - Seuil minimal: >=2 polluants (PM2.5 + NO2 ou PM10)")
    print("  - Seuil optimal: >=3 polluants pour analyses robustes")
    print("  - Attention: biais vers pays riches avec meilleure couverture")
    print("  - Documenter le nombre de pays exclus dans les analyses")

    return df

def main():
    print("=" * 60)
    print("ANALYSE MÉTHODOLOGIQUE (Q1-Q3)")
    print("=" * 60)

    df = load_data()
    if df is None:
        return

    # Q1: Polluants pertinents
    df_polluants = analyse_q1_polluants_pertinents(df)

    # Q2: Métriques
    analyse_q2_metriques(df)

    # Q3: Couverture
    df = analyse_q3_couverture(df)

    print("\n" + "=" * 60)
    print("ANALYSE MÉTHODOLOGIQUE TERMINÉE")
    print("=" * 60)

if __name__ == "__main__":
    main()
