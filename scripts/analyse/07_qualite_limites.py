"""
Script 07 - Analyse Qualité et Limites (Q25-Q27)
================================================
Q25. Impact du seuil de complétude
Q26. Représentativité des données OpenAQ
Q27. Problème d'agrégation pays vs ville
"""

import sys
sys.path.append(str(__file__).rsplit('scripts', 1)[0])

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from config import DATA_RAW, DATA_CLEANED

FIGURES_DIR = DATA_CLEANED.parent.parent / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    path = DATA_CLEANED / "base_analyse_complete.csv"
    if not path.exists():
        print("Exécutez d'abord 00_fusion_complete.py")
        return None
    return pd.read_csv(path)

# =============================================================================
# Q25: Impact du seuil de complétude
# =============================================================================
def analyse_q25_seuil_completude(df):
    """Analyse l'impact du seuil de complétude sur les résultats."""
    print("\n" + "=" * 60)
    print("Q25: IMPACT DU SEUIL DE COMPLÉTUDE")
    print("=" * 60)

    pollution_cols = ['pollution_pm25', 'pollution_no2', 'pollution_pm10',
                      'pollution_o3', 'pollution_so2', 'pollution_co']
    pollution_cols = [c for c in pollution_cols if c in df.columns]

    # Compter le nombre de polluants disponibles par pays
    df = df.copy()
    df['n_polluants'] = df[pollution_cols].notna().sum(axis=1)

    print("\n--- Distribution du nombre de polluants par pays ---")
    print(df['n_polluants'].value_counts().sort_index())

    # Analyser comment les résultats changent selon le seuil
    print("\n--- Impact du seuil sur les statistiques PM2.5 ---")

    if 'pollution_pm25' not in df.columns:
        print("PM2.5 non disponible")
        return

    results = []
    for seuil in range(1, len(pollution_cols) + 1):
        subset = df[df['n_polluants'] >= seuil]
        if len(subset) < 3:
            continue

        pm25_data = subset['pollution_pm25'].dropna()
        if len(pm25_data) < 3:
            continue

        results.append({
            'seuil': f'>={seuil} polluants',
            'n_pays': len(subset),
            'pm25_mean': pm25_data.mean(),
            'pm25_median': pm25_data.median(),
            'pm25_std': pm25_data.std()
        })

    df_results = pd.DataFrame(results)
    print(df_results.to_string(index=False))

    # Comparer les corrélations PIB-PM2.5 selon le seuil
    if 'NY.GDP.PCAP.CD' in df.columns:
        print("\n--- Corrélation PIB vs PM2.5 selon le seuil ---")
        for seuil in [1, 2, 3]:
            subset = df[(df['n_polluants'] >= seuil) &
                       df['pollution_pm25'].notna() &
                       df['NY.GDP.PCAP.CD'].notna()]
            if len(subset) >= 5:
                corr, pval = stats.spearmanr(subset['NY.GDP.PCAP.CD'], subset['pollution_pm25'])
                sig = "*" if pval < 0.05 else ""
                print(f"  >={seuil} polluants (n={len(subset)}): r={corr:.3f} (p={pval:.3f}){sig}")

    # Visualisation
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Barplot du nombre de pays
    ax = axes[0]
    seuils = list(range(1, len(pollution_cols) + 1))
    n_pays = [(df['n_polluants'] >= s).sum() for s in seuils]
    ax.bar([f'>={s}' for s in seuils], n_pays)
    ax.set_xlabel('Seuil de complétude')
    ax.set_ylabel('Nombre de pays')
    ax.set_title('Pays disponibles selon le seuil')

    # Boxplot PM2.5 selon complétude
    ax = axes[1]
    data_by_seuil = []
    labels = []
    for seuil in [1, 2, 3, 4]:
        subset = df[(df['n_polluants'] >= seuil) & df['pollution_pm25'].notna()]['pollution_pm25']
        if len(subset) >= 3:
            data_by_seuil.append(subset.values)
            labels.append(f'>={seuil}')

    if data_by_seuil:
        ax.boxplot(data_by_seuil, labels=labels)
        ax.set_xlabel('Seuil de complétude')
        ax.set_ylabel('PM2.5 (µg/m³)')
        ax.set_title('Distribution PM2.5 selon le seuil')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q25_seuil_completude.png", dpi=150)
    plt.close()
    print(f"\n  Figure: q25_seuil_completude.png")

    print("\n--- CONCLUSION Q25 ---")
    print("  - Un seuil plus élevé réduit le nombre de pays")
    print("  - Les résultats peuvent varier selon le seuil choisi")
    print("  - Recommandation: tester la sensibilité au seuil")

# =============================================================================
# Q26: Représentativité des données OpenAQ
# =============================================================================
def analyse_q26_representativite(df):
    """Analyse la représentativité des données OpenAQ."""
    print("\n" + "=" * 60)
    print("Q26: REPRÉSENTATIVITÉ DES DONNÉES OPENAQ")
    print("=" * 60)

    # Charger les données World Cities pour comparaison
    cities_path = DATA_RAW / "world_cities_by_country.csv"
    if cities_path.exists():
        all_countries = pd.read_csv(cities_path)
        n_total = len(all_countries)
    else:
        n_total = 200  # Approximation

    n_openaq = len(df)
    couverture = n_openaq / n_total * 100

    print(f"\n  Pays avec données OpenAQ: {n_openaq}")
    print(f"  Pays dans World Cities: {n_total}")
    print(f"  Couverture: {couverture:.1f}%")

    # Biais géographique
    print("\n--- Biais géographique ---")
    if 'latitude_moyenne' in df.columns:
        lat = df['latitude_moyenne'].dropna()
        print(f"  Latitude moyenne: {lat.mean():.1f}° (médiane: {lat.median():.1f}°)")
        print(f"  Min: {lat.min():.1f}°, Max: {lat.max():.1f}°")

        # Répartition hémisphères
        n_nord = (lat > 0).sum()
        n_sud = (lat < 0).sum()
        print(f"  Hémisphère Nord: {n_nord} pays ({n_nord/len(lat)*100:.0f}%)")
        print(f"  Hémisphère Sud: {n_sud} pays ({n_sud/len(lat)*100:.0f}%)")

    # Biais économique
    print("\n--- Biais économique ---")
    if 'NY.GDP.PCAP.CD' in df.columns:
        pib = df['NY.GDP.PCAP.CD'].dropna()
        print(f"  PIB/hab moyen (échantillon OpenAQ): ${pib.mean():,.0f}")
        print(f"  PIB/hab médian (échantillon OpenAQ): ${pib.median():,.0f}")
        print(f"  Note: Le PIB mondial moyen est ~$12,000")

        # Par catégorie de revenu
        if 'categorie_revenu' in df.columns:
            print("\n  Répartition par catégorie de revenu:")
            counts = df['categorie_revenu'].value_counts()
            for cat, n in counts.items():
                pct = n / len(df) * 100
                print(f"    {cat}: {n} pays ({pct:.0f}%)")

    # Régions représentées
    print("\n--- Pays présents dans l'échantillon ---")
    if 'country_code' in df.columns:
        codes = df['country_code'].tolist()
        print(f"  Codes: {', '.join(sorted(codes)[:30])}")
        if len(codes) > 30:
            print(f"  ... et {len(codes)-30} autres")

    # Visualisation
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Distribution géographique
    if 'latitude_moyenne' in df.columns and 'longitude_moyenne' in df.columns:
        ax = axes[0]
        ax.scatter(df['longitude_moyenne'], df['latitude_moyenne'], alpha=0.6, s=50)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title('Distribution géographique des pays OpenAQ')
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)

    # Distribution PIB
    if 'NY.GDP.PCAP.CD' in df.columns:
        ax = axes[1]
        ax.hist(df['NY.GDP.PCAP.CD'].dropna() / 1000, bins=20, edgecolor='black', alpha=0.7)
        ax.set_xlabel('PIB/habitant (milliers USD)')
        ax.set_ylabel('Nombre de pays')
        ax.set_title('Distribution économique des pays OpenAQ')
        ax.axvline(x=12, color='red', linestyle='--', label='Moyenne mondiale')
        ax.legend()

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q26_representativite.png", dpi=150)
    plt.close()
    print(f"\n  Figure: q26_representativite.png")

    print("\n--- CONCLUSION Q26 ---")
    print("  Biais potentiels identifiés:")
    print("  - Surreprésentation des pays développés (meilleure infrastructure)")
    print("  - Sous-représentation de l'Afrique et certaines régions d'Asie")
    print("  - Biais vers l'hémisphère Nord")
    print("  -> Les résultats ne sont pas généralisables à tous les pays")

# =============================================================================
# Q27: Problème d'agrégation pays vs ville
# =============================================================================
def analyse_q27_agregation(df):
    """Analyse le problème d'agrégation pays vs ville."""
    print("\n" + "=" * 60)
    print("Q27: PROBLÈME D'AGRÉGATION PAYS VS VILLE")
    print("=" * 60)

    print("\n--- Le problème fondamental ---")
    print("""
  Les données combinent deux niveaux différents:
  - OpenAQ: mesures au niveau VILLE (agrégées par pays)
  - World Bank: indicateurs au niveau PAYS
  - World Cities: données VILLE mais agrégées par pays

  Cela pose un problème d'interprétation car:
  1. La pollution varie énormément au sein d'un même pays
  2. Les indicateurs nationaux masquent les variations locales
  3. La corrélation pays-niveau peut être un artefact d'agrégation
    """)

    # Illustration avec World Cities
    cities_path = DATA_RAW / "world_cities_clean.csv"
    if cities_path.exists():
        cities = pd.read_csv(cities_path)

        print("\n--- Illustration: variabilité intra-pays ---")

        if 'population' in cities.columns and 'country' in cities.columns:
            # Calculer l'écart-type de la population par pays
            var_by_country = cities.groupby('country')['population'].agg(['mean', 'std', 'count'])
            var_by_country = var_by_country[var_by_country['count'] >= 5]
            var_by_country['cv'] = var_by_country['std'] / var_by_country['mean'] * 100

            print("\n  Pays avec la plus grande variabilité de population des villes:")
            for country, row in var_by_country.nlargest(5, 'cv').iterrows():
                print(f"    {country}: CV={row['cv']:.0f}% (n={row['count']:.0f} villes)")

    print("\n--- Limites de l'analyse ---")
    print("""
  1. ECOLOGICAL FALLACY (erreur écologique):
     Une corrélation au niveau pays n'implique PAS
     la même relation au niveau ville/individu.

  2. AGGREGATION BIAS:
     En moyennant les données par pays, on perd
     l'information sur la distribution interne.

  3. MODIFIABLE AREAL UNIT PROBLEM (MAUP):
     Les résultats dépendent du niveau d'agrégation choisi.
    """)

    print("\n--- Recommandations pour le rapport ---")
    print("""
  1. Clairement mentionner le niveau d'analyse (pays)
  2. Ne pas extrapoler aux villes individuelles
  3. Interpréter les corrélations avec prudence
  4. Suggérer des analyses futures au niveau ville
  5. Reconnaître que les données WB au niveau pays
     limitent la précision des conclusions
    """)

    # Visualisation conceptuelle
    fig, ax = plt.subplots(figsize=(10, 6))

    # Schéma conceptuel
    ax.text(0.5, 0.9, "PROBLÈME D'AGRÉGATION", fontsize=14, fontweight='bold',
            ha='center', transform=ax.transAxes)

    ax.text(0.2, 0.7, "Données VILLE\n(OpenAQ, Cities)", fontsize=11,
            ha='center', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='lightblue'))

    ax.text(0.8, 0.7, "Données PAYS\n(World Bank)", fontsize=11,
            ha='center', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='lightgreen'))

    ax.annotate('', xy=(0.5, 0.5), xytext=(0.2, 0.6),
                arrowprops=dict(arrowstyle='->', color='blue'),
                transform=ax.transAxes)
    ax.annotate('', xy=(0.5, 0.5), xytext=(0.8, 0.6),
                arrowprops=dict(arrowstyle='->', color='green'),
                transform=ax.transAxes)

    ax.text(0.5, 0.45, "Fusion au niveau PAYS", fontsize=11,
            ha='center', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='yellow'))

    ax.text(0.5, 0.25, "[\!] Perte d'information locale\n[\!] Risque d'erreur écologique",
            fontsize=10, ha='center', transform=ax.transAxes, color='red')

    ax.axis('off')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q27_agregation.png", dpi=150)
    plt.close()
    print(f"\n  Figure: q27_agregation.png")

def generate_summary_report(df):
    """Génère un rapport de synthèse des limites."""
    print("\n" + "=" * 60)
    print("SYNTHÈSE DES LIMITES ET PRÉCAUTIONS")
    print("=" * 60)

    n_pays = len(df)
    pollution_cols = [c for c in df.columns if c.startswith('pollution_') and not c.endswith('_norm')]
    n_polluants = len(pollution_cols)

    print(f"""
  [*] DONNÉES DISPONIBLES
  ----------------------
  - {n_pays} pays avec données pollution
  - {n_polluants} polluants mesurés
  - Sources: OpenAQ (pollution), World Bank (socio-éco), SimpleMaps (villes)

  [\!] LIMITES PRINCIPALES
  ----------------------
  1. Couverture géographique limitée ({n_pays} pays sur ~200)
  2. Biais vers les pays développés
  3. Données pollution = moyennes annuelles (pas de saisonnalité)
  4. Agrégation pays masque les variations locales
  5. Décalage temporel possible entre sources

  [?] PRÉCAUTIONS D'INTERPRÉTATION
  -------------------------------
  - Corrélation \!= Causalité
  - Résultats au niveau pays \!= résultats au niveau ville
  - Modèles prédictifs à utiliser avec prudence
  - Toujours mentionner les limitations dans le rapport

  [OK] POINTS FORTS
  ---------------
  - Données récentes (2023-2026)
  - Multiple polluants pour validation croisée
  - Indicateurs socio-éco standardisés (World Bank)
  - Méthodologie reproductible
    """)

def main():
    print("=" * 60)
    print("ANALYSE QUALITÉ ET LIMITES (Q25-Q27)")
    print("=" * 60)

    df = load_data()
    if df is None:
        return

    analyse_q25_seuil_completude(df)
    analyse_q26_representativite(df)
    analyse_q27_agregation(df)
    generate_summary_report(df)

    print("\n" + "=" * 60)
    print("ANALYSE QUALITÉ TERMINÉE")
    print("=" * 60)

if __name__ == "__main__":
    main()
