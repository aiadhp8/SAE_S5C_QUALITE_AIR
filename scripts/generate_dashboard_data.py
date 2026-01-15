"""
Script pour générer les fichiers JSON pour le dashboard Angular
"""
import pandas as pd
import json
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
OUTPUT_DIR = BASE_DIR / "dashboard" / "src" / "assets" / "data"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def save_json(data, filename):
    """Sauvegarde en JSON avec formatage"""
    with open(OUTPUT_DIR / filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {filename}")

# 1. PAYS ET DONNÉES DE BASE
print("Processing base_complete.csv...")
df_base = pd.read_csv(DATA_DIR / "final" / "base_complete.csv")
countries_data = df_base.to_dict(orient='records')

# Ajouter des infos supplémentaires
for country in countries_data:
    # Remplacer NaN par null
    for key, value in country.items():
        if pd.isna(value):
            country[key] = None

save_json(countries_data, "countries.json")

# 2. DONNÉES DE POLLUTION PAR ANNÉE
print("Processing openaq_country_averages.csv...")
df_pollution = pd.read_csv(DATA_DIR / "raw" / "openaq_country_averages.csv")

# Structurer par pays puis par année puis par polluant
pollution_data = {}
for _, row in df_pollution.iterrows():
    code = row['country_code']
    year = int(row['year'])
    param = row['parameter']

    if code not in pollution_data:
        pollution_data[code] = {"country_code": code, "country_name": row['country_name'], "years": {}}

    if year not in pollution_data[code]["years"]:
        pollution_data[code]["years"][year] = {}

    pollution_data[code]["years"][year][param] = {
        "average": row['average'] if not pd.isna(row['average']) else None,
        "median": row['median'] if not pd.isna(row['median']) else None,
        "min": row['min'] if not pd.isna(row['min']) else None,
        "max": row['max'] if not pd.isna(row['max']) else None,
        "std": row['std'] if not pd.isna(row['std']) else None,
        "measurement_count": int(row['measurement_count']) if not pd.isna(row['measurement_count']) else None,
        "unit": row['unit']
    }

save_json(list(pollution_data.values()), "pollution.json")

# 3. CORRÉLATIONS
print("Processing synthese_correlations.csv...")
df_corr = pd.read_csv(REPORTS_DIR / "synthese_correlations.csv")
correlations_data = []
for _, row in df_corr.iterrows():
    correlations_data.append({
        "pollutant": row['polluant'],
        "indicator": row['indicateur'],
        "axis": row['axe'],
        "correlation": row['correlation'] if not pd.isna(row['correlation']) else None,
        "p_value": row['p_value'] if not pd.isna(row['p_value']) else None,
        "significant": bool(row['significatif']) if not pd.isna(row['significatif']) else False,
        "very_significant": bool(row['tres_significatif']) if not pd.isna(row['tres_significatif']) else False,
        "n_observations": int(row['n_observations']) if not pd.isna(row['n_observations']) else None,
        "strength": row['force']
    })
save_json(correlations_data, "correlations.json")

# 4. DONNÉES TEMPORELLES - ÉVOLUTION GLOBALE
print("Processing temporal_evolution_globale.csv...")
df_temporal = pd.read_csv(REPORTS_DIR / "temporal_evolution_globale.csv")
temporal_global = df_temporal.to_dict(orient='records')
for item in temporal_global:
    for key, value in item.items():
        if pd.isna(value):
            item[key] = None
save_json(temporal_global, "temporal_global.json")

# 5. DONNÉES TEMPORELLES - IMPACT COVID
print("Processing temporal_covid_impact.csv...")
df_covid = pd.read_csv(REPORTS_DIR / "temporal_covid_impact.csv")
covid_data = []
for _, row in df_covid.iterrows():
    covid_data.append({
        "country_code": row['country_code'],
        "country_name": row['country_name'],
        "parameter": row['parameter'],
        "val_2019": row['val_2019'] if not pd.isna(row['val_2019']) else None,
        "val_2020": row['val_2020'] if not pd.isna(row['val_2020']) else None,
        "variation_pct": row['variation_pct'] if not pd.isna(row['variation_pct']) else None
    })
save_json(covid_data, "covid_impact.json")

# 6. ACP LOADINGS
print("Processing acp_loadings.csv...")
df_acp = pd.read_csv(REPORTS_DIR / "acp_loadings.csv")
acp_data = {
    "loadings": df_acp.to_dict(orient='records'),
    "variables": df_acp.iloc[:, 0].tolist() if df_acp.columns[0] == 'Unnamed: 0' else df_acp.columns[1:].tolist()
}
# Nettoyer les NaN
for item in acp_data["loadings"]:
    for key, value in item.items():
        if pd.isna(value):
            item[key] = None
save_json(acp_data, "acp.json")

# 7. MODÈLES ML
print("Processing models_comparison.csv...")
df_models = pd.read_csv(REPORTS_DIR / "models_comparison.csv")
models_data = df_models.to_dict(orient='records')
for item in models_data:
    for key, value in item.items():
        if pd.isna(value):
            item[key] = None
save_json(models_data, "models.json")

# 8. FEATURE IMPORTANCE
print("Processing feature_importance.csv...")
df_features = pd.read_csv(REPORTS_DIR / "feature_importance.csv")
features_data = []
for _, row in df_features.iterrows():
    if not pd.isna(row['variable']):
        features_data.append({
            "variable": row['variable'],
            "importance": row['importance'] if not pd.isna(row['importance']) else 0
        })
save_json(features_data, "features.json")

# 9. COMPLÉTUDE DES DONNÉES
print("Processing completude_donnees.csv...")
df_completude = pd.read_csv(REPORTS_DIR / "completude_donnees.csv")
completude_data = df_completude.to_dict(orient='records')
for item in completude_data:
    for key, value in item.items():
        if pd.isna(value):
            item[key] = None
save_json(completude_data, "completude.json")

# 10. STATISTIQUES GLOBALES POUR LES KPIs
print("Computing global statistics...")
stats = {
    "total_countries": len(df_base),
    "total_measurements": int(df_pollution['measurement_count'].sum()),
    "period": {"start": 2018, "end": 2023},
    "pollutants": ["pm25", "pm10", "no2", "o3", "so2", "co"],
    "pollutant_labels": {
        "pm25": "PM2.5",
        "pm10": "PM10",
        "no2": "NO\u2082",
        "o3": "O\u2083",
        "so2": "SO\u2082",
        "co": "CO"
    },
    "who_limits": {
        "pm25": 5,
        "pm10": 15,
        "no2": 10,
        "o3": 100,
        "so2": 40,
        "co": 4000
    },
    "units": {
        "pm25": "\u00b5g/m\u00b3",
        "pm10": "\u00b5g/m\u00b3",
        "no2": "\u00b5g/m\u00b3",
        "o3": "\u00b5g/m\u00b3",
        "so2": "\u00b5g/m\u00b3",
        "co": "\u00b5g/m\u00b3"
    },
    "median_values": {},
    "above_who_pct": {}
}

# Calculer les médianes et % au-dessus OMS pour chaque polluant
for pollutant in ["pm25", "pm10", "no2", "o3", "so2", "co"]:
    col = f"pollution_{pollutant}"
    if col in df_base.columns:
        values = df_base[col].dropna()
        if len(values) > 0:
            stats["median_values"][pollutant] = round(values.median(), 2)
            who_limit = stats["who_limits"][pollutant]
            above_who = (values > who_limit).sum()
            stats["above_who_pct"][pollutant] = round(100 * above_who / len(values), 1)

save_json(stats, "stats.json")

print("\n=== DONE ===")
print(f"All files saved to: {OUTPUT_DIR}")
