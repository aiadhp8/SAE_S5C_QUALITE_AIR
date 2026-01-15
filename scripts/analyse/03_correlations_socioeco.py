"""
Script 03 - Corrélations Socio-économiques (Q11-Q15)
====================================================
Q11. Motorisation vs NO2
Q12. Industrie vs PM2.5/SO2
Q13. PIB vs qualité de l'air
Q14. Urbanisation vs PM2.5
Q15. CO2/hab vs pollution locale
"""

import sys
sys.path.append(str(__file__).rsplit('scripts', 1)[0])

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from config import DATA_CLEANED, get_label

FIGURES_DIR = DATA_CLEANED.parent.parent / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    path = DATA_CLEANED / "base_analyse_complete.csv"
    if not path.exists():
        print("Exécutez d'abord 00_fusion_complete.py")
        return None
    return pd.read_csv(path)

def compute_correlation(df, var1, var2):
    """Calcule la corrélation de Spearman entre deux variables."""
    data = df[[var1, var2]].dropna()
    if len(data) < 5:
        return np.nan, np.nan, 0
    corr, pval = stats.spearmanr(data[var1], data[var2])
    return corr, pval, len(data)

def plot_correlation(df, var_x, var_y, title, xlabel, ylabel, filename, log_x=False, log_y=False):
    """Crée un graphique de corrélation."""
    data = df[[var_x, var_y, 'country_code']].dropna()
    if len(data) < 5:
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.log1p(data[var_x]) if log_x else data[var_x]
    y = np.log1p(data[var_y]) if log_y else data[var_y]

    ax.scatter(x, y, alpha=0.6, s=50)

    # Ligne de tendance
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    x_sorted = np.sort(x)
    ax.plot(x_sorted, p(x_sorted), "r--", alpha=0.8, linewidth=2)

    # Corrélation
    corr, pval = stats.spearmanr(x, y)
    sig = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else ""

    ax.set_xlabel(xlabel + (" (log)" if log_x else ""))
    ax.set_ylabel(ylabel + (" (log)" if log_y else ""))
    ax.set_title(f"{title}\nSpearman r = {corr:.3f}{sig}")

    # Annotations pour quelques pays
    for _, row in data.nlargest(5, var_y).iterrows():
        x_val = np.log1p(row[var_x]) if log_x else row[var_x]
        y_val = np.log1p(row[var_y]) if log_y else row[var_y]
        ax.annotate(row['country_code'], (x_val, y_val), fontsize=8)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=150)
    plt.close()
    print(f"  Figure: {filename}")

# =============================================================================
# Q11: Transport vs NO2
# =============================================================================
def analyse_q11_motorisation_no2(df):
    """Relation entre transport et NO2."""
    print("\n" + "=" * 60)
    print("Q11: TRANSPORT VS NO2")
    print("=" * 60)

    # Indicateurs de motorisation (si disponibles) ou alternatives transport
    motor_cols = ['IS.VEH.NVEH.P3', 'IS.VEH.PCAR.P3']
    transport_cols = ['IS.AIR.PSGR', 'IS.AIR.DPRT', 'IS.RRS.TOTL.KM']
    pollution_cols = ['pollution_no2', 'pollution_pm25', 'pollution_pm10']

    # Vérifier quels indicateurs sont disponibles
    available_motor = [c for c in motor_cols if c in df.columns]
    available_transport = [c for c in transport_cols if c in df.columns]

    if not available_motor and not available_transport:
        print("  Aucun indicateur de transport disponible")
        return

    print("\n--- Corrélations (Spearman) ---")

    # D'abord les indicateurs de motorisation si disponibles
    for motor in available_motor:
        print(f"\n  {motor}:")
        for pol in pollution_cols:
            if pol not in df.columns:
                continue
            corr, pval, n = compute_correlation(df, motor, pol)
            sig = "*" if pval < 0.05 else ""
            print(f"    vs {pol.replace('pollution_','')}: r={corr:.3f} (p={pval:.3f}, n={n}){sig}")

    # Sinon utiliser les indicateurs de transport alternatifs
    if not available_motor:
        print("\n  Note: Données véhicules non disponibles, utilisation des données transport aérien/ferroviaire")

    for trans in available_transport:
        print(f"\n  {trans}:")
        for pol in pollution_cols:
            if pol not in df.columns:
                continue
            corr, pval, n = compute_correlation(df, trans, pol)
            sig = "*" if pval < 0.05 else ""
            print(f"    vs {pol.replace('pollution_','')}: r={corr:.3f} (p={pval:.3f}, n={n}){sig}")

    # Graphique principal - priorité aux véhicules, sinon transport aérien
    graph_created = False

    if 'IS.VEH.NVEH.P3' in df.columns and 'pollution_no2' in df.columns:
        plot_correlation(
            df, 'IS.VEH.NVEH.P3', 'pollution_no2',
            "Q11: Motorisation vs NO2",
            "Véhicules pour 1000 habitants",
            "NO2 moyen (µg/m³)",
            "q11_motorisation_no2.png"
        )
        graph_created = True

    if not graph_created and 'IS.AIR.PSGR' in df.columns and 'pollution_no2' in df.columns:
        plot_correlation(
            df, 'IS.AIR.PSGR', 'pollution_no2',
            "Q11: Transport aérien vs NO2",
            "Passagers aériens transportés",
            "NO2 moyen (µg/m³)",
            "q11_motorisation_no2.png",
            log_x=True
        )
        graph_created = True

    if not graph_created and 'IS.AIR.DPRT' in df.columns and 'pollution_no2' in df.columns:
        plot_correlation(
            df, 'IS.AIR.DPRT', 'pollution_no2',
            "Q11: Départs aériens vs NO2",
            "Départs de vols aériens",
            "NO2 moyen (µg/m³)",
            "q11_motorisation_no2.png",
            log_x=True
        )
        graph_created = True

    print("\n--- CONCLUSION Q11 ---")
    if available_motor:
        print("  Hypothèse: Plus de véhicules -> plus de NO2")
        print("  Résultat: La relation est souvent faible au niveau national")
        print("  Explication: Qualité du parc auto, régulations, densité routière")
    else:
        print("  Note: Analyse avec données transport aérien (véhicules non disponibles)")
        print("  Hypothèse: Plus de trafic aérien -> économie développée -> plus de NO2")
        print("  Résultat: Relation complexe car pays développés ont aussi meilleures normes")

# =============================================================================
# Q12: Industrie vs PM2.5/SO2
# =============================================================================
def analyse_q12_industrie_pollution(df):
    """Relation entre part d'industrie et pollution."""
    print("\n" + "=" * 60)
    print("Q12: INDUSTRIE VS PM2.5/SO2")
    print("=" * 60)

    indus_cols = ['NV.IND.TOTL.ZS', 'NV.IND.MANF.ZS', 'SL.IND.EMPL.ZS']
    pollution_cols = ['pollution_pm25', 'pollution_so2', 'pollution_pm10']

    print("\n--- Corrélations (Spearman) ---")
    for indus in indus_cols:
        if indus not in df.columns:
            continue
        print(f"\n  {indus}:")
        for pol in pollution_cols:
            if pol not in df.columns:
                continue
            corr, pval, n = compute_correlation(df, indus, pol)
            sig = "*" if pval < 0.05 else ""
            print(f"    vs {pol.replace('pollution_','')}: r={corr:.3f} (p={pval:.3f}, n={n}){sig}")

    # Graphique
    if 'NV.IND.TOTL.ZS' in df.columns and 'pollution_pm25' in df.columns:
        plot_correlation(
            df, 'NV.IND.TOTL.ZS', 'pollution_pm25',
            "Q12: Part industrie vs PM2.5",
            "Valeur ajoutée industrie (% PIB)",
            "PM2.5 moyen (µg/m³)",
            "q12_industrie_pm25.png"
        )

    print("\n--- CONCLUSION Q12 ---")
    print("  Hypothèse: Plus d'industrie -> plus de PM2.5/SO2")
    print("  Attention: Type d'industrie et technologies varient beaucoup")

# =============================================================================
# Q13: PIB vs qualité de l'air (Courbe de Kuznets)
# =============================================================================
def analyse_q13_pib_pollution(df):
    """Relation entre PIB et pollution (courbe environnementale de Kuznets)."""
    print("\n" + "=" * 60)
    print("Q13: PIB VS QUALITÉ DE L'AIR")
    print("=" * 60)

    # Chercher une colonne de PIB disponible
    pib_col = None
    for candidate in ['NY.GDP.PCAP.CD', 'eco_NY_GDP_PCAP_CD', 'NY.GDP.PCAP.PP.CD', 'eco_NY_GDP_PCAP_PP_CD']:
        if candidate in df.columns and df[candidate].notna().sum() >= 10:
            pib_col = candidate
            break

    if pib_col is None:
        print("Données PIB non disponibles ou insuffisantes")
        print("  Note: Les données World Bank sont stockées avec préfixe 'eco_'")

        # Créer une figure vide avec message
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        for ax in axes:
            ax.text(0.5, 0.5, 'Données PIB non disponibles\ndans ce dataset',
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
        plt.savefig(FIGURES_DIR / "q13_pib_pollution.png", dpi=150)
        plt.close()
        return

    print(f"  Utilisation de la colonne: {pib_col}")

    pollution_cols = ['pollution_pm25', 'pollution_no2', 'pollution_pm10']

    print("\n--- Corrélations linéaires (Spearman) ---")
    for pol in pollution_cols:
        if pol not in df.columns:
            continue
        corr, pval, n = compute_correlation(df, pib_col, pol)
        sig = "*" if pval < 0.05 else ""
        print(f"  PIB/hab vs {pol.replace('pollution_','')}: r={corr:.3f} (p={pval:.3f}, n={n}){sig}")

    # Test de la courbe en U inversé (Kuznets)
    print("\n--- Test courbe de Kuznets (U inversé) ---")
    for pol in ['pollution_pm25']:
        if pol not in df.columns:
            continue
        data = df[[pib_col, pol]].dropna()
        # Filtrer les valeurs <= 0 pour le log
        data = data[data[pib_col] > 0]
        if len(data) < 10:
            print(f"  {pol}: pas assez de données ({len(data)} < 10)")
            continue

        # Régression quadratique
        try:
            x = np.log(data[pib_col])
            y = data[pol]
            coeffs = np.polyfit(x, y, 2)

            print(f"  {pol}: coefficients polynôme degré 2 = {coeffs}")
            if coeffs[0] < 0:
                print("    -> Forme de U inversé possible (pollution augmente puis diminue)")
            else:
                print("    -> Pas de forme en U inversé claire")
        except Exception as e:
            print(f"  {pol}: erreur régression - {e}")

    # Graphique avec catégories de revenu
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Scatter plot
    if 'pollution_pm25' in df.columns:
        ax = axes[0]
        data = df[[pib_col, 'pollution_pm25', 'country_code']].dropna()
        data = data[data[pib_col] > 0]

        if len(data) >= 5:
            ax.scatter(np.log10(data[pib_col]), data['pollution_pm25'], alpha=0.6)
            ax.set_xlabel('PIB/habitant (log10, USD)')
            ax.set_ylabel('PM2.5 (µg/m³)')
            ax.set_title('Q13: PIB vs PM2.5')

            # Courbe de tendance polynomiale
            try:
                x = np.log10(data[pib_col])
                y = data['pollution_pm25']
                z = np.polyfit(x, y, 2)
                p = np.poly1d(z)
                x_smooth = np.linspace(x.min(), x.max(), 100)
                ax.plot(x_smooth, p(x_smooth), 'r-', linewidth=2, label='Tendance (poly2)')
                ax.legend()
            except Exception:
                pass  # Ignorer si polyfit échoue
        else:
            ax.text(0.5, 0.5, 'Pas assez de données', ha='center', va='center', transform=ax.transAxes)

    # Box plot par catégorie de revenu
    ax = axes[1]
    if 'categorie_revenu' in df.columns and 'pollution_pm25' in df.columns:
        order = ['Faible', 'Moyen-inférieur', 'Moyen-supérieur', 'Élevé']
        data = df[['categorie_revenu', 'pollution_pm25']].dropna()
        data = data[data['categorie_revenu'].isin(order)]
        if len(data) >= 5:
            sns.boxplot(data=data, x='categorie_revenu', y='pollution_pm25', order=order, ax=ax)
            ax.set_xlabel('Catégorie de revenu')
            ax.set_ylabel('PM2.5 (µg/m³)')
            ax.set_title('PM2.5 par catégorie de revenu')
            ax.tick_params(axis='x', rotation=45)
        else:
            ax.text(0.5, 0.5, 'Catégories de revenu\nnon disponibles', ha='center', va='center', transform=ax.transAxes)
    else:
        ax.text(0.5, 0.5, 'Catégories de revenu\nnon disponibles', ha='center', va='center', transform=ax.transAxes)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q13_pib_pollution.png", dpi=150)
    plt.close()
    print(f"\n  Figure: q13_pib_pollution.png")

    print("\n--- CONCLUSION Q13 ---")
    print("  Courbe de Kuznets environnementale:")
    print("  - Les pays à revenu moyen ont souvent la pire pollution")
    print("  - Les pays riches ont généralement une meilleure qualité de l'air")
    print("  - Les pays pauvres: pollution moindre (moins d'industrie) ou non mesurée")

# =============================================================================
# Q14: Urbanisation vs PM2.5
# =============================================================================
def analyse_q14_urbanisation_pollution(df):
    """Relation entre taux d'urbanisation et pollution."""
    print("\n" + "=" * 60)
    print("Q14: URBANISATION VS PM2.5")
    print("=" * 60)

    urban_cols = ['SP.URB.TOTL.IN.ZS', 'SP.URB.GROW', 'EN.POP.DNST']
    pollution_cols = ['pollution_pm25', 'pollution_no2']

    print("\n--- Corrélations (Spearman) ---")
    for urban in urban_cols:
        if urban not in df.columns:
            continue
        print(f"\n  {urban}:")
        for pol in pollution_cols:
            if pol not in df.columns:
                continue
            corr, pval, n = compute_correlation(df, urban, pol)
            sig = "*" if pval < 0.05 else ""
            print(f"    vs {pol.replace('pollution_','')}: r={corr:.3f} (p={pval:.3f}, n={n}){sig}")

    # Graphique
    if 'SP.URB.TOTL.IN.ZS' in df.columns and 'pollution_pm25' in df.columns:
        plot_correlation(
            df, 'SP.URB.TOTL.IN.ZS', 'pollution_pm25',
            "Q14: Taux d'urbanisation vs PM2.5",
            "Population urbaine (%)",
            "PM2.5 moyen (µg/m³)",
            "q14_urbanisation_pm25.png"
        )

    print("\n--- CONCLUSION Q14 ---")
    print("  Résultat souvent contre-intuitif:")
    print("  - Pays très urbanisés = souvent plus développés = meilleures normes")
    print("  - Pays en urbanisation rapide = souvent plus pollués")

# =============================================================================
# Q15: Émissions CO2 vs pollution locale
# =============================================================================
def analyse_q15_co2_pollution(df):
    """Relation entre émissions CO2 et pollution locale."""
    print("\n" + "=" * 60)
    print("Q15: ÉMISSIONS CO2 VS POLLUTION LOCALE")
    print("=" * 60)

    if 'EN.ATM.CO2E.PC' not in df.columns:
        print("Données CO2 non disponibles")
        return

    pollution_cols = ['pollution_pm25', 'pollution_no2', 'pollution_pm10']

    print("\n--- Corrélations (Spearman) ---")
    for pol in pollution_cols:
        if pol not in df.columns:
            continue
        corr, pval, n = compute_correlation(df, 'EN.ATM.CO2E.PC', pol)
        sig = "*" if pval < 0.05 else ""
        print(f"  CO2/hab vs {pol.replace('pollution_','')}: r={corr:.3f} (p={pval:.3f}, n={n}){sig}")

    # Graphique
    if 'pollution_pm25' in df.columns:
        plot_correlation(
            df, 'EN.ATM.CO2E.PC', 'pollution_pm25',
            "Q15: Émissions CO2 vs PM2.5",
            "CO2 par habitant (tonnes)",
            "PM2.5 moyen (µg/m³)",
            "q15_co2_pm25.png"
        )

    print("\n--- CONCLUSION Q15 ---")
    print("  CO2 et pollution locale sont souvent décorrélés car:")
    print("  - CO2 = combustion totale (y compris efficace)")
    print("  - PM/NO2 = combustion incomplète, filtration")
    print("  - Un pays peut avoir haut CO2 mais bonne filtration (ex: pays du Golfe)")

def create_correlation_matrix(df):
    """Crée une matrice de corrélation globale."""
    print("\n" + "=" * 60)
    print("MATRICE DE CORRÉLATION GLOBALE")
    print("=" * 60)

    # Sélectionner les variables clés
    vars_pollution = ['pollution_pm25', 'pollution_no2', 'pollution_pm10']
    vars_socioeco = ['NY.GDP.PCAP.CD', 'SP.URB.TOTL.IN.ZS', 'NV.IND.TOTL.ZS',
                     'IS.VEH.NVEH.P3', 'EN.ATM.CO2E.PC', 'EN.POP.DNST']

    all_vars = [v for v in vars_pollution + vars_socioeco if v in df.columns]

    if len(all_vars) < 4:
        print("Pas assez de variables pour la matrice")
        return

    # Calculer la matrice
    corr_matrix = df[all_vars].corr(method='spearman')

    # Renommer pour lisibilité
    rename_map = {
        'pollution_pm25': 'PM2.5',
        'pollution_no2': 'NO2',
        'pollution_pm10': 'PM10',
        'NY.GDP.PCAP.CD': 'PIB/hab',
        'SP.URB.TOTL.IN.ZS': '% Urbain',
        'NV.IND.TOTL.ZS': '% Industrie',
        'IS.VEH.NVEH.P3': 'Véhicules',
        'EN.ATM.CO2E.PC': 'CO2/hab',
        'EN.POP.DNST': 'Densité'
    }
    corr_matrix = corr_matrix.rename(index=rename_map, columns=rename_map)

    # Visualisation
    plt.figure(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f',
                cmap='RdBu_r', center=0, vmin=-1, vmax=1)
    plt.title('Matrice de corrélation (Spearman)')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "correlation_matrix.png", dpi=150)
    plt.close()
    print(f"\n  Figure: correlation_matrix.png")

def main():
    print("=" * 60)
    print("CORRÉLATIONS SOCIO-ÉCONOMIQUES (Q11-Q15)")
    print("=" * 60)

    df = load_data()
    if df is None:
        return

    analyse_q11_motorisation_no2(df)
    analyse_q12_industrie_pollution(df)
    analyse_q13_pib_pollution(df)
    analyse_q14_urbanisation_pollution(df)
    analyse_q15_co2_pollution(df)
    create_correlation_matrix(df)

    print("\n" + "=" * 60)
    print("ANALYSES CORRÉLATIONS TERMINÉES")
    print("=" * 60)

if __name__ == "__main__":
    main()
