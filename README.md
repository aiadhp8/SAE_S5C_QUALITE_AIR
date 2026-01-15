# SAE S5.C.01 - Analyse de la Qualite de l'Air

Projet d'analyse des facteurs urbains et socio-economiques influencant la qualite de l'air a travers le monde.

## Description

Ce projet repond a la question de recherche : **"Quels facteurs urbains et environnementaux influencent le plus la qualite de l'air dans differentes villes du monde ?"**

### Fonctionnalites

- Extraction de donnees de pollution (API OpenAQ)
- Collecte d'indicateurs World Bank (transport, energie, economie, demographie, sante)
- Analyses statistiques (correlations, ACP, graphes de similarite)
- Modeles predictifs (Random Forest, Gradient Boosting, Ridge, Lasso)
- Generation automatique de ~50 graphiques et rapports

## Prerequis

- Python 3.10+
- PostgreSQL (optionnel)

## Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd SAE_S5C
```

### 2. Creer un environnement virtuel

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Installer les dependances

```bash
pip install -r requirements.txt
```

### 4. Configuration (optionnel)

Creer un fichier `.env` a la racine :

```env
# Cle API OpenAQ (optionnel, ameliore les limites de requetes)
OPENAQ_API_KEY=votre_cle_api

# Configuration PostgreSQL (optionnel)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sae_qualite_air
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
```

## Utilisation

### Execution complete (recommande)

Le fichier `main.py` centralise toutes les operations :

```bash
python main.py
```

Options disponibles :
- `1` - Executer le pipeline complet (extraction + analyses)
- `2` - Extraction des donnees uniquement
- `3` - Analyses statistiques uniquement
- `4` - Afficher l'etat des donnees
- `5` - Nettoyer les donnees temporaires
- `0` - Quitter

### Execution rapide (tout automatique)

```bash
python main.py --all
```

### Execution par etape

```bash
# Extraction uniquement
python main.py --extract

# Analyses uniquement (necessite les donnees extraites)
python main.py --analyse

# Verifier l'etat des donnees
python main.py --status
```

## Structure du projet

```
SAE_S5C/
├── main.py                 # Point d'entree principal
├── config.py               # Configuration centralisee
├── requirements.txt        # Dependances Python
│
├── data/
│   ├── raw/                # Donnees brutes extraites
│   ├── cleaned/            # Donnees nettoyees
│   └── final/              # Donnees fusionnees
│
├── scripts/
│   ├── common/             # Extraction des donnees
│   │   ├── 01_extract_openaq.py
│   │   ├── 02_extract_world_cities.py
│   │   ├── 03_base_commune.py
│   │   └── worldbank_demo_data.py
│   │
│   ├── axes/               # Traitement par axe thematique
│   │   ├── axe_transport.py
│   │   ├── axe_energie.py
│   │   ├── axe_economie.py
│   │   ├── axe_demographie.py
│   │   └── axe_sante.py
│   │
│   └── analyse/            # Analyses statistiques
│       ├── 00_fusion_complete.py
│       ├── 01_methodologie.py
│       ├── 02_descriptives.py
│       ├── 03_correlations_socioeco.py
│       ├── 04_acp.py
│       ├── 05_graphes_similarite.py
│       ├── 06_modeles_predictifs.py
│       └── 07_qualite_limites.py
│
├── database/
│   ├── schema.sql          # Schema PostgreSQL
│   └── insert_data.py      # Insertion en base
│
└── reports/
    ├── figures/            # Graphiques generes
    └── *.csv               # Resultats d'analyses
```

## Donnees analysees

### Polluants (source: OpenAQ)
| Polluant | Description | Seuil OMS annuel |
|----------|-------------|------------------|
| PM2.5 | Particules fines < 2.5 microns | 5 ug/m3 |
| PM10 | Particules < 10 microns | 15 ug/m3 |
| NO2 | Dioxyde d'azote | 10 ug/m3 |
| O3 | Ozone | 100 ug/m3 (8h) |
| SO2 | Dioxyde de soufre | 40 ug/m3 (24h) |
| CO | Monoxyde de carbone | 4 mg/m3 |

### Indicateurs par axe (source: World Bank)

- **Transport** : Vehicules/1000 hab, reseau routier, transport aerien/ferroviaire
- **Energie** : Mix energetique, consommation, emissions CO2
- **Economie** : PIB/hab, structure sectorielle, emploi
- **Demographie** : Population urbaine, densite, couverture forestiere
- **Sante** : Exposition PM2.5, deces pollution, esperance de vie

## Resultats produits

Apres execution complete :

- `reports/figures/` : ~50 graphiques PNG
- `reports/base_analyse_complete.csv` : Base de donnees fusionnee
- `reports/correlations_*.csv` : Matrices de correlation
- `reports/acp_loadings.csv` : Resultats ACP
- `reports/feature_importance.csv` : Importance des variables (ML)
- `reports/models_comparison.csv` : Comparaison des modeles

## Questions de recherche

Le projet repond a 27 questions organisees en 7 themes :

1. **Methodologie** (Q1-Q3) : Selection des polluants, mesures statistiques
2. **Descriptives** (Q4-Q10) : Distributions, pays/regions pollues
3. **Correlations** (Q11-Q15) : Liens socio-economiques
4. **ACP** (Q16-Q18) : Analyse en composantes principales
5. **Graphes** (Q19-Q21) : Similarite entre pays
6. **Prediction** (Q22-Q24) : Modeles de machine learning
7. **Qualite** (Q25-Q27) : Limites et biais

## Technologies utilisees

- **Donnees** : pandas, numpy
- **Visualisation** : matplotlib, seaborn, plotly
- **Statistiques** : scipy, statsmodels
- **Machine Learning** : scikit-learn
- **APIs** : requests, aiohttp
- **Base de donnees** : psycopg2, sqlalchemy (optionnel)

## Auteurs

Projet realise dans le cadre de la SAE S5.C.01 - IUT Informatique

## Licence

Projet academique - Usage educatif uniquement
