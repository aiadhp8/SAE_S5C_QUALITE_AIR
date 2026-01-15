"""
Script 05 - Graphes de Similarité (Q19-Q21)
===========================================
Q19. Villes similaires géographiquement éloignées
Q20. Communautés détectées (k-NN)
Q21. Outliers dans le graphe
"""

import sys
sys.path.append(str(__file__).rsplit('scripts', 1)[0])

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.impute import SimpleImputer
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import pdist, squareform
import networkx as nx
from config import DATA_CLEANED

FIGURES_DIR = DATA_CLEANED.parent.parent / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    path = DATA_CLEANED / "base_analyse_complete.csv"
    if not path.exists():
        print("Exécutez d'abord 00_fusion_complete.py")
        return None
    return pd.read_csv(path)

def prepare_similarity_data(df):
    """Prépare les données pour l'analyse de similarité."""
    # Variables pour calculer la similarité
    vars_pollution = ['pollution_pm25', 'pollution_no2', 'pollution_pm10']
    vars_socioeco = ['NY.GDP.PCAP.CD', 'SP.URB.TOTL.IN.ZS', 'NV.IND.TOTL.ZS',
                     'IS.VEH.NVEH.P3', 'EN.ATM.CO2E.PC']

    all_vars = [v for v in vars_pollution + vars_socioeco if v in df.columns]

    # Garder les pays avec données suffisantes
    df_sim = df[['country_code', 'country_name', 'latitude_moyenne', 'longitude_moyenne'] + all_vars].copy()
    df_sim = df_sim.dropna(subset=all_vars[:2])  # Au moins PM2.5 et NO2

    print(f"Variables pour similarité: {len(all_vars)}")
    print(f"Pays: {len(df_sim)}")

    return df_sim, all_vars

# =============================================================================
# Q19: Pays similaires mais géographiquement éloignés
# =============================================================================
def analyse_q19_similarite_distance(df):
    """Identifie les pays similaires mais géographiquement éloignés."""
    print("\n" + "=" * 60)
    print("Q19: PAYS SIMILAIRES MAIS ÉLOIGNÉS GÉOGRAPHIQUEMENT")
    print("=" * 60)

    df_sim, vars_list = prepare_similarity_data(df)

    if len(df_sim) < 10:
        print("Pas assez de données")
        return

    # Calculer la matrice de similarité (profil socio-éco + pollution)
    X = df_sim[vars_list].values
    imputer = SimpleImputer(strategy='median')
    X_imputed = imputer.fit_transform(X)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    # Distance euclidienne dans l'espace des caractéristiques
    dist_features = squareform(pdist(X_scaled, metric='euclidean'))

    # Distance géographique (si coordonnées disponibles)
    if 'latitude_moyenne' in df_sim.columns and 'longitude_moyenne' in df_sim.columns:
        coords = df_sim[['latitude_moyenne', 'longitude_moyenne']].values
        # Remplacer NaN par médiane
        coords = SimpleImputer(strategy='median').fit_transform(coords)
        dist_geo = squareform(pdist(coords, metric='euclidean'))
    else:
        print("Coordonnées non disponibles")
        return

    # Trouver les paires : faible distance caractéristiques, grande distance géo
    n = len(df_sim)
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            pairs.append({
                'pays1': df_sim.iloc[i]['country_code'],
                'pays2': df_sim.iloc[j]['country_code'],
                'dist_profil': dist_features[i, j],
                'dist_geo': dist_geo[i, j]
            })

    df_pairs = pd.DataFrame(pairs)

    # Normaliser les distances
    df_pairs['dist_profil_norm'] = (df_pairs['dist_profil'] - df_pairs['dist_profil'].min()) / \
                                    (df_pairs['dist_profil'].max() - df_pairs['dist_profil'].min())
    df_pairs['dist_geo_norm'] = (df_pairs['dist_geo'] - df_pairs['dist_geo'].min()) / \
                                 (df_pairs['dist_geo'].max() - df_pairs['dist_geo'].min())

    # Score: profil similaire (faible) mais géo éloigné (élevé)
    df_pairs['score'] = (1 - df_pairs['dist_profil_norm']) * df_pairs['dist_geo_norm']

    # Top paires
    print("\n--- Paires les plus intéressantes (similaires mais éloignés) ---")
    top_pairs = df_pairs.nlargest(10, 'score')
    for _, row in top_pairs.iterrows():
        print(f"  {row['pays1']} - {row['pays2']}: profil={row['dist_profil']:.2f}, geo={row['dist_geo']:.0f}")

    # Visualisation
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df_pairs['dist_geo'], df_pairs['dist_profil'], alpha=0.3)

    # Mettre en évidence les paires intéressantes
    for _, row in top_pairs.head(5).iterrows():
        ax.scatter(row['dist_geo'], row['dist_profil'], color='red', s=100)
        ax.annotate(f"{row['pays1']}-{row['pays2']}",
                   (row['dist_geo'], row['dist_profil']), fontsize=8)

    ax.set_xlabel('Distance géographique')
    ax.set_ylabel('Distance de profil (caractéristiques)')
    ax.set_title('Q19: Similarité de profil vs Distance géographique')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q19_similarite_distance.png", dpi=150)
    plt.close()
    print(f"\n  Figure: q19_similarite_distance.png")

    return df_sim, X_scaled

# =============================================================================
# Q20: Communautés détectées (k-NN graph)
# =============================================================================
def analyse_q20_communautes(df):
    """Détecte les communautés dans un graphe k-NN."""
    print("\n" + "=" * 60)
    print("Q20: COMMUNAUTÉS DANS LE GRAPHE k-NN")
    print("=" * 60)

    df_sim, vars_list = prepare_similarity_data(df)

    if len(df_sim) < 10:
        print("Pas assez de données")
        return

    # Préparer les données
    X = df_sim[vars_list].values
    imputer = SimpleImputer(strategy='median')
    X_imputed = imputer.fit_transform(X)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    # Construire le graphe k-NN
    k = min(5, len(df_sim) - 1)
    nn = NearestNeighbors(n_neighbors=k+1, metric='euclidean')
    nn.fit(X_scaled)
    distances, indices = nn.kneighbors(X_scaled)

    # Créer le graphe NetworkX
    G = nx.Graph()
    for i, code in enumerate(df_sim['country_code']):
        G.add_node(code)

    for i in range(len(df_sim)):
        for j in range(1, k+1):  # Skip self (index 0)
            neighbor_idx = indices[i, j]
            weight = 1 / (1 + distances[i, j])
            G.add_edge(df_sim.iloc[i]['country_code'],
                      df_sim.iloc[neighbor_idx]['country_code'],
                      weight=weight)

    print(f"\n  Graphe k-NN: {G.number_of_nodes()} noeuds, {G.number_of_edges()} arêtes")

    # Détection de communautés (Louvain)
    try:
        from community import community_louvain
        partition = community_louvain.best_partition(G)
        n_communities = len(set(partition.values()))
        print(f"  Communautés détectées (Louvain): {n_communities}")

        # Afficher les communautés
        for comm in range(n_communities):
            members = [k for k, v in partition.items() if v == comm]
            print(f"\n  Communauté {comm+1}: {', '.join(members[:10])}")
            if len(members) > 10:
                print(f"    ... et {len(members)-10} autres")

    except ImportError:
        print("  Module 'python-louvain' non installé")
        print("  Installation: pip install python-louvain")
        partition = None

    # Visualisation du graphe
    fig, ax = plt.subplots(figsize=(14, 10))

    pos = nx.spring_layout(G, seed=42, k=2)

    if partition:
        colors = [partition[node] for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=colors, cmap=plt.cm.tab10,
                              node_size=300, alpha=0.8, ax=ax)
    else:
        nx.draw_networkx_nodes(G, pos, node_size=300, alpha=0.8, ax=ax)

    nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)

    ax.set_title('Q20: Graphe k-NN des pays')
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q20_graphe_knn.png", dpi=150)
    plt.close()
    print(f"\n  Figure: q20_graphe_knn.png")

    return G

# =============================================================================
# Q21: Outliers dans le graphe
# =============================================================================
def analyse_q21_outliers(df):
    """Identifie les outliers (pays atypiques)."""
    print("\n" + "=" * 60)
    print("Q21: OUTLIERS - PAYS ATYPIQUES")
    print("=" * 60)

    df_sim, vars_list = prepare_similarity_data(df)

    if len(df_sim) < 10:
        print("Pas assez de données")
        return

    # Préparer les données
    X = df_sim[vars_list].values
    imputer = SimpleImputer(strategy='median')
    X_imputed = imputer.fit_transform(X)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    # Méthode 1: Distance moyenne aux k plus proches voisins
    k = min(5, len(df_sim) - 1)
    nn = NearestNeighbors(n_neighbors=k+1)
    nn.fit(X_scaled)
    distances, _ = nn.kneighbors(X_scaled)
    mean_dist = distances[:, 1:].mean(axis=1)  # Exclure soi-même

    df_sim = df_sim.copy()
    df_sim['mean_knn_distance'] = mean_dist

    # Outliers = distance élevée
    threshold = np.percentile(mean_dist, 90)
    outliers = df_sim[df_sim['mean_knn_distance'] > threshold]

    print("\n--- Outliers (distance k-NN élevée) ---")
    for _, row in outliers.sort_values('mean_knn_distance', ascending=False).iterrows():
        print(f"  {row['country_code']}: distance moyenne = {row['mean_knn_distance']:.2f}")

    # Méthode 2: DBSCAN pour identifier les points isolés
    dbscan = DBSCAN(eps=1.5, min_samples=2)
    clusters = dbscan.fit_predict(X_scaled)
    noise_mask = clusters == -1

    print(f"\n--- DBSCAN ---")
    print(f"  Clusters trouvés: {len(set(clusters)) - (1 if -1 in clusters else 0)}")
    print(f"  Points isolés (bruit): {noise_mask.sum()}")

    if noise_mask.sum() > 0:
        print("\n  Pays isolés (DBSCAN):")
        for code in df_sim.loc[noise_mask, 'country_code']:
            print(f"    {code}")

    # Analyse des outliers
    print("\n--- Caractéristiques des outliers ---")
    for _, row in outliers.iterrows():
        code = row['country_code']
        print(f"\n  {code}:")
        for var in vars_list[:5]:
            if var in df_sim.columns and pd.notna(row[var]):
                val = row[var]
                median_val = df_sim[var].median()
                ratio = val / median_val if median_val != 0 else np.nan
                print(f"    {var}: {val:.2f} ({ratio:.1f}x médiane)")

    # Visualisation
    fig, ax = plt.subplots(figsize=(10, 6))

    # Utiliser les 2 premières composantes pour visualiser
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    ax.scatter(X_pca[:, 0], X_pca[:, 1], c=mean_dist, cmap='YlOrRd', alpha=0.7)
    plt.colorbar(ax.collections[0], label='Distance k-NN moyenne')

    # Annoter les outliers
    for i, row in df_sim.iterrows():
        if row['mean_knn_distance'] > threshold:
            idx = df_sim.index.get_loc(i)
            ax.annotate(row['country_code'], (X_pca[idx, 0], X_pca[idx, 1]),
                       fontsize=9, fontweight='bold')

    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')
    ax.set_title('Q21: Identification des outliers')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "q21_outliers.png", dpi=150)
    plt.close()
    print(f"\n  Figure: q21_outliers.png")

    print("\n--- CONCLUSION Q21 ---")
    print("  Les outliers peuvent s'expliquer par:")
    print("  - Économie atypique (ex: pays pétroliers)")
    print("  - Données manquantes ou erronées")
    print("  - Situation géographique unique")

def main():
    print("=" * 60)
    print("GRAPHES DE SIMILARITÉ (Q19-Q21)")
    print("=" * 60)

    df = load_data()
    if df is None:
        return

    analyse_q19_similarite_distance(df)
    analyse_q20_communautes(df)
    analyse_q21_outliers(df)

    print("\n" + "=" * 60)
    print("ANALYSE GRAPHES TERMINÉE")
    print("=" * 60)

if __name__ == "__main__":
    main()
