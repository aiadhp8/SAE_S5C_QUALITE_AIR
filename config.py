"""
Configuration commune du projet SAE S5.C.01
Qualité de l'air - Caractéristiques urbaines et sociales
"""

import os
from pathlib import Path

# =============================================================================
# CHEMINS DU PROJET
# =============================================================================
PROJECT_ROOT = Path(__file__).parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_CLEANED = PROJECT_ROOT / "data" / "cleaned"
DATA_FINAL = PROJECT_ROOT / "data" / "final"
DATABASE_DIR = PROJECT_ROOT / "database"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Créer les dossiers s'ils n'existent pas
for folder in [DATA_RAW, DATA_CLEANED, DATA_FINAL, DATABASE_DIR, REPORTS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# =============================================================================
# ANNEES D'ANALYSE
# =============================================================================
# On se concentre sur les années récentes pour avoir des données complètes
ANNEES_ANALYSE = list(range(2018, 2024))  # 2018-2023
ANNEE_REFERENCE = 2022  # Année principale pour les analyses

# =============================================================================
# POLLUANTS D'INTERET
# =============================================================================
POLLUANTS = {
    "pm25": "PM2.5",      # Particules fines < 2.5 microns
    "pm10": "PM10",       # Particules < 10 microns
    "no2": "NO2",         # Dioxyde d'azote
    "o3": "O3",           # Ozone
    "so2": "SO2",         # Dioxyde de soufre
    "co": "CO"            # Monoxyde de carbone
}

# =============================================================================
# INDICATEURS WORLD BANK PAR AXE THEMATIQUE
# =============================================================================

# Chaque membre travaille sur un axe de manière indépendante
# Format: "CODE_INDICATEUR": "Description courte"

AXE_TRANSPORT = {
    "IS.VEH.NVEH.P3": "Véhicules pour 1000 habitants",
    "IS.VEH.PCAR.P3": "Voitures particulières pour 1000 hab",
    "IS.VEH.ROAD.K1": "Véhicules par km de route",
    "IS.ROD.TOTL.KM": "Réseau routier total (km)",
    "IS.ROD.PAVE.ZS": "Routes pavées (%)",
    "IS.AIR.DPRT": "Départs de vols aériens",
    "IS.AIR.PSGR": "Passagers aériens transportés",
    "IS.RRS.TOTL.KM": "Réseau ferroviaire (km)",
}

AXE_ENERGIE = {
    "EG.USE.PCAP.KG.OE": "Consommation énergie (kg pétrole/hab)",
    "EG.USE.ELEC.KH.PC": "Consommation électricité (kWh/hab)",
    "EG.ELC.FOSL.ZS": "Électricité fossile (%)",
    "EG.ELC.COAL.ZS": "Électricité charbon (%)",
    "EG.ELC.NGAS.ZS": "Électricité gaz naturel (%)",
    "EG.ELC.PETR.ZS": "Électricité pétrole (%)",
    "EG.ELC.NUCL.ZS": "Électricité nucléaire (%)",
    "EG.ELC.RNWX.ZS": "Électricité renouvelable (%)",
    "EG.FEC.RNEW.ZS": "Consommation finale énergie renouvelable (%)",
    "EN.ATM.CO2E.PC": "Émissions CO2 (tonnes/hab)",
    "EN.ATM.CO2E.KT": "Émissions CO2 totales (kt)",
    "EN.ATM.METH.KT.CE": "Émissions méthane (kt CO2 eq)",
    "EN.ATM.NOXE.KT.CE": "Émissions NOx (kt CO2 eq)",
}

AXE_ECONOMIE_INDUSTRIE = {
    "NY.GDP.PCAP.CD": "PIB par habitant (USD)",
    "NY.GDP.PCAP.PP.CD": "PIB par habitant PPA (USD)",
    "NV.IND.TOTL.ZS": "Valeur ajoutée industrie (% PIB)",
    "NV.IND.MANF.ZS": "Valeur ajoutée manufacture (% PIB)",
    "NV.SRV.TOTL.ZS": "Valeur ajoutée services (% PIB)",
    "NV.AGR.TOTL.ZS": "Valeur ajoutée agriculture (% PIB)",
    "SL.IND.EMPL.ZS": "Emploi dans l'industrie (%)",
    "SL.AGR.EMPL.ZS": "Emploi dans l'agriculture (%)",
    "SL.SRV.EMPL.ZS": "Emploi dans les services (%)",
    "IC.BUS.EASE.XQ": "Facilité de faire des affaires (score)",
}

AXE_DEMOGRAPHIE_URBANISATION = {
    "SP.POP.TOTL": "Population totale",
    "SP.URB.TOTL": "Population urbaine",
    "SP.URB.TOTL.IN.ZS": "Population urbaine (%)",
    "SP.URB.GROW": "Croissance population urbaine (%)",
    "EN.URB.LCTY": "Population plus grande ville",
    "EN.URB.LCTY.UR.ZS": "Population plus grande ville (% urbain)",
    "EN.POP.DNST": "Densité population (hab/km²)",
    "AG.LND.TOTL.K2": "Superficie totale (km²)",
    "AG.SRF.TOTL.K2": "Superficie terre (km²)",
    "AG.LND.FRST.ZS": "Couverture forestière (%)",
}

AXE_SANTE_ENVIRONNEMENT = {
    "EN.ATM.PM25.MC.M3": "Exposition PM2.5 (µg/m³) - World Bank",
    "EN.ATM.PM25.MC.ZS": "Pop exposée PM2.5 > seuil OMS (%)",
    "SH.STA.AIRP.P5": "Décès pollution air (pour 100k hab)",
    "SP.DYN.LE00.IN": "Espérance de vie",
    "SH.XPD.CHEX.PC.CD": "Dépenses santé par habitant (USD)",
    "SH.XPD.CHEX.GD.ZS": "Dépenses santé (% PIB)",
}

# Tous les indicateurs combinés pour référence
TOUS_INDICATEURS = {
    **AXE_TRANSPORT,
    **AXE_ENERGIE,
    **AXE_ECONOMIE_INDUSTRIE,
    **AXE_DEMOGRAPHIE_URBANISATION,
    **AXE_SANTE_ENVIRONNEMENT
}

# Labels pour les polluants
LABELS_POLLUANTS = {
    "pollution_pm25": "PM2.5 (µg/m³)",
    "pollution_pm10": "PM10 (µg/m³)",
    "pollution_no2": "NO₂ (µg/m³)",
    "pollution_o3": "O₃ (µg/m³)",
    "pollution_so2": "SO₂ (µg/m³)",
    "pollution_co": "CO (µg/m³)",
    "pm25": "PM2.5 (µg/m³)",
    "pm10": "PM10 (µg/m³)",
    "no2": "NO₂ (µg/m³)",
    "o3": "O₃ (µg/m³)",
    "so2": "SO₂ (µg/m³)",
    "co": "CO (µg/m³)",
}

def get_label(code):
    """
    Retourne un label lisible en français pour un code World Bank ou un nom de colonne.

    Args:
        code: Code World Bank (ex: "SP.URB.TOTL") ou nom de colonne (ex: "pollution_pm25")

    Returns:
        Label en français ou le code original si non trouvé
    """
    # Nettoyer le code (enlever préfixes comme "transport_", "eco_", etc.)
    clean_code = code
    for prefix in ["transport_", "eco_", "energie_", "demo_", "sante_"]:
        if code.startswith(prefix):
            clean_code = code[len(prefix):].replace("_", ".")
            break

    # Chercher dans les indicateurs World Bank
    if clean_code in TOUS_INDICATEURS:
        return TOUS_INDICATEURS[clean_code]

    # Chercher dans les labels de polluants
    if code in LABELS_POLLUANTS:
        return LABELS_POLLUANTS[code]

    # Chercher le code original avec points remplacés par underscores
    code_with_dots = code.replace("_", ".")
    if code_with_dots in TOUS_INDICATEURS:
        return TOUS_INDICATEURS[code_with_dots]

    # Retourner le code original si non trouvé
    return code

# =============================================================================
# MAPPING CODES PAYS ISO
# =============================================================================
# Pour harmoniser entre les différentes sources de données
# (sera complété automatiquement lors du traitement)

# =============================================================================
# PARAMETRES BASE DE DONNEES
# =============================================================================
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "sae_qualite_air",
    "user": "postgres",
    "password": ""  # À configurer localement
}

# =============================================================================
# SEUILS OMS QUALITE DE L'AIR (2021)
# =============================================================================
SEUILS_OMS = {
    "pm25": {
        "annuel": 5,      # µg/m³
        "journalier": 15  # µg/m³
    },
    "pm10": {
        "annuel": 15,
        "journalier": 45
    },
    "no2": {
        "annuel": 10,
        "journalier": 25
    },
    "o3": {
        "8h": 100  # µg/m³ sur 8h
    },
    "so2": {
        "journalier": 40
    },
    "co": {
        "journalier": 4  # mg/m³
    }
}
