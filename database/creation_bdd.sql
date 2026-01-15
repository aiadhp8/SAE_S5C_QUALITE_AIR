-- =============================================================================
-- SAE S5.C.01 - Analyse de la Qualité de l'Air Mondiale
-- Script de Création de la Base de Données PostgreSQL
-- =============================================================================
-- Auteur: Équipe SAE S5.C.01
-- Date: Janvier 2026
-- Description: Création du schéma complet pour l'analyse des relations entre
--              caractéristiques urbaines/socio-économiques et qualité de l'air
-- =============================================================================

-- Configuration de l'encodage
SET client_encoding = 'UTF8';

-- =============================================================================
-- SUPPRESSION DES OBJETS EXISTANTS
-- =============================================================================

-- Suppression des vues
DROP VIEW IF EXISTS v_pollution_pays_annee CASCADE;
DROP VIEW IF EXISTS v_indicateurs_recents CASCADE;
DROP VIEW IF EXISTS v_synthese_pays CASCADE;
DROP VIEW IF EXISTS v_analyse_correlation CASCADE;
DROP VIEW IF EXISTS v_depassements_oms CASCADE;
DROP VIEW IF EXISTS v_evolution_temporelle CASCADE;

-- Suppression des fonctions
DROP FUNCTION IF EXISTS get_pollution_moyenne CASCADE;
DROP FUNCTION IF EXISTS count_pays_depassement_oms CASCADE;
DROP FUNCTION IF EXISTS get_tendance_pollution CASCADE;
DROP FUNCTION IF EXISTS get_correlation_indicateur_pollution CASCADE;

-- Suppression des tables (ordre inverse des dépendances)
DROP TABLE IF EXISTS mesure_pays_annee CASCADE;
DROP TABLE IF EXISTS mesure_pollution CASCADE;
DROP TABLE IF EXISTS indicateur_pays CASCADE;
DROP TABLE IF EXISTS indicateur CASCADE;
DROP TABLE IF EXISTS station CASCADE;
DROP TABLE IF EXISTS ville CASCADE;
DROP TABLE IF EXISTS pays CASCADE;
DROP TABLE IF EXISTS polluant CASCADE;
DROP TABLE IF EXISTS categorie_indicateur CASCADE;
DROP TABLE IF EXISTS region CASCADE;

-- =============================================================================
-- TABLE: region
-- Description: Régions géographiques mondiales
-- =============================================================================
CREATE TABLE region (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE region IS 'Régions géographiques mondiales';

INSERT INTO region (code, nom) VALUES
('europe', 'Europe'),
('asie', 'Asie'),
('amerique_nord', 'Amérique du Nord'),
('amerique_sud', 'Amérique du Sud'),
('afrique', 'Afrique'),
('oceanie', 'Océanie'),
('moyen_orient', 'Moyen-Orient');

-- =============================================================================
-- TABLE: pays
-- Description: Informations sur les pays
-- =============================================================================
CREATE TABLE pays (
    id SERIAL PRIMARY KEY,
    code_iso2 VARCHAR(2) UNIQUE NOT NULL,
    code_iso3 VARCHAR(3) UNIQUE,
    nom VARCHAR(100) NOT NULL,
    nom_fr VARCHAR(100),
    region_id INTEGER REFERENCES region(id),
    nb_villes INTEGER DEFAULT 0,
    population_urbaine_totale BIGINT,
    latitude_moyenne DECIMAL(10, 6),
    longitude_moyenne DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE pays IS 'Table des pays avec codes ISO et statistiques urbaines';
COMMENT ON COLUMN pays.code_iso2 IS 'Code ISO 3166-1 alpha-2';
COMMENT ON COLUMN pays.code_iso3 IS 'Code ISO 3166-1 alpha-3';
COMMENT ON COLUMN pays.nb_villes IS 'Nombre de villes répertoriées dans le pays';
COMMENT ON COLUMN pays.population_urbaine_totale IS 'Population urbaine totale (somme des villes)';

CREATE INDEX idx_pays_region ON pays(region_id);
CREATE INDEX idx_pays_code_iso3 ON pays(code_iso3);

-- =============================================================================
-- TABLE: ville
-- Description: Informations sur les villes
-- =============================================================================
CREATE TABLE ville (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    nom_ascii VARCHAR(100),
    pays_id INTEGER REFERENCES pays(id) ON DELETE CASCADE,
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    population BIGINT,
    categorie_taille VARCHAR(20) CHECK (categorie_taille IN (
        'megapole', 'metropole', 'grande_ville', 'ville_moyenne', 'petite_ville'
    )),
    est_capitale BOOLEAN DEFAULT FALSE,
    region_admin VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(nom, pays_id)
);

COMMENT ON TABLE ville IS 'Table des villes avec données géographiques et démographiques';
COMMENT ON COLUMN ville.categorie_taille IS 'megapole (>10M), metropole (1-10M), grande_ville (500K-1M), ville_moyenne (100K-500K), petite_ville (<100K)';

CREATE INDEX idx_ville_pays ON ville(pays_id);
CREATE INDEX idx_ville_population ON ville(population DESC);
CREATE INDEX idx_ville_categorie ON ville(categorie_taille);

-- =============================================================================
-- TABLE: polluant
-- Description: Types de polluants mesurés (référentiel OMS)
-- =============================================================================
CREATE TABLE polluant (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    nom VARCHAR(50) NOT NULL,
    formule_chimique VARCHAR(20),
    unite VARCHAR(20) DEFAULT 'µg/m³',
    seuil_oms_annuel DECIMAL(10, 2),
    seuil_oms_journalier DECIMAL(10, 2),
    seuil_oms_horaire DECIMAL(10, 2),
    description TEXT,
    sources_principales TEXT,
    effets_sante TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE polluant IS 'Référentiel des polluants atmosphériques avec seuils OMS 2021';
COMMENT ON COLUMN polluant.seuil_oms_annuel IS 'Seuil OMS pour la moyenne annuelle';
COMMENT ON COLUMN polluant.seuil_oms_journalier IS 'Seuil OMS pour la moyenne sur 24h';

-- Insertion des polluants avec seuils OMS 2021
INSERT INTO polluant (code, nom, formule_chimique, unite, seuil_oms_annuel, seuil_oms_journalier, seuil_oms_horaire, description, sources_principales, effets_sante) VALUES
('pm25', 'PM2.5', 'PM₂.₅', 'µg/m³', 5, 15, NULL,
 'Particules fines de diamètre aérodynamique inférieur à 2.5 micromètres',
 'Combustion (véhicules, chauffage, industrie), poussières naturelles',
 'Maladies cardiovasculaires, respiratoires, cancers pulmonaires'),

('pm10', 'PM10', 'PM₁₀', 'µg/m³', 15, 45, NULL,
 'Particules de diamètre aérodynamique inférieur à 10 micromètres',
 'Trafic routier, construction, agriculture, poussières naturelles',
 'Irritations respiratoires, aggravation asthme, maladies pulmonaires'),

('no2', 'Dioxyde d''azote', 'NO₂', 'µg/m³', 10, 25, 200,
 'Gaz brun-rouge à odeur âcre, indicateur de pollution liée au trafic',
 'Trafic routier (moteurs diesel), centrales thermiques, industrie',
 'Inflammation des voies respiratoires, diminution fonction pulmonaire'),

('o3', 'Ozone', 'O₃', 'µg/m³', NULL, 100, NULL,
 'Polluant secondaire formé par réaction photochimique (seuil sur 8h max)',
 'Formé par réaction entre NOx et COV sous rayonnement solaire',
 'Irritation des yeux et voies respiratoires, crises asthme'),

('so2', 'Dioxyde de soufre', 'SO₂', 'µg/m³', NULL, 40, NULL,
 'Gaz incolore à odeur piquante, marqueur de combustion fossile',
 'Centrales thermiques au charbon, raffineries, industrie métallurgique',
 'Irritation respiratoire, aggravation maladies pulmonaires'),

('co', 'Monoxyde de carbone', 'CO', 'mg/m³', NULL, 4, NULL,
 'Gaz incolore et inodore, produit de combustion incomplète',
 'Trafic routier, chauffage défectueux, industrie',
 'Intoxication, maux de tête, troubles cognitifs, décès à forte dose');

-- =============================================================================
-- TABLE: station
-- Description: Stations de mesure OpenAQ
-- =============================================================================
CREATE TABLE station (
    id SERIAL PRIMARY KEY,
    openaq_id VARCHAR(50) UNIQUE,
    nom VARCHAR(200),
    ville_id INTEGER REFERENCES ville(id) ON DELETE SET NULL,
    pays_id INTEGER REFERENCES pays(id) ON DELETE CASCADE NOT NULL,
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    altitude DECIMAL(8, 2),
    type_zone VARCHAR(30) CHECK (type_zone IN ('urbain', 'periurbain', 'rural', 'industriel', 'trafic')),
    est_reference BOOLEAN DEFAULT FALSE,
    date_premiere_mesure DATE,
    date_derniere_mesure DATE,
    nb_mesures_total INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE station IS 'Stations de mesure de qualité de l''air (source OpenAQ)';

CREATE INDEX idx_station_ville ON station(ville_id);
CREATE INDEX idx_station_pays ON station(pays_id);
CREATE INDEX idx_station_type ON station(type_zone);
CREATE INDEX idx_station_coords ON station(latitude, longitude);

-- =============================================================================
-- TABLE: mesure_pollution
-- Description: Mesures de pollution agrégées (données OpenAQ)
-- =============================================================================
CREATE TABLE mesure_pollution (
    id SERIAL PRIMARY KEY,
    station_id INTEGER REFERENCES station(id) ON DELETE CASCADE,
    pays_id INTEGER REFERENCES pays(id) ON DELETE CASCADE NOT NULL,
    polluant_id INTEGER REFERENCES polluant(id) ON DELETE CASCADE NOT NULL,
    annee INTEGER NOT NULL CHECK (annee BETWEEN 2015 AND 2030),
    mois INTEGER CHECK (mois BETWEEN 1 AND 12),
    valeur_moyenne DECIMAL(10, 2),
    valeur_mediane DECIMAL(10, 2),
    valeur_min DECIMAL(10, 2),
    valeur_max DECIMAL(10, 2),
    ecart_type DECIMAL(10, 2),
    nb_mesures INTEGER DEFAULT 0,
    depasse_seuil_oms BOOLEAN,
    ratio_depassement DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(station_id, polluant_id, annee, mois)
);

COMMENT ON TABLE mesure_pollution IS 'Mesures de pollution agrégées par station/mois';
COMMENT ON COLUMN mesure_pollution.ratio_depassement IS 'Ratio valeur/seuil OMS';

CREATE INDEX idx_mesure_annee ON mesure_pollution(annee);
CREATE INDEX idx_mesure_annee_mois ON mesure_pollution(annee, mois);
CREATE INDEX idx_mesure_pays ON mesure_pollution(pays_id);
CREATE INDEX idx_mesure_polluant ON mesure_pollution(polluant_id);
CREATE INDEX idx_mesure_station ON mesure_pollution(station_id);

-- =============================================================================
-- TABLE: mesure_pays_annee
-- Description: Agrégation des mesures au niveau pays-année (pour analyses)
-- =============================================================================
CREATE TABLE mesure_pays_annee (
    id SERIAL PRIMARY KEY,
    pays_id INTEGER REFERENCES pays(id) ON DELETE CASCADE NOT NULL,
    polluant_id INTEGER REFERENCES polluant(id) ON DELETE CASCADE NOT NULL,
    annee INTEGER NOT NULL CHECK (annee BETWEEN 2015 AND 2030),
    moyenne DECIMAL(10, 2),
    mediane DECIMAL(10, 2),
    minimum DECIMAL(10, 2),
    maximum DECIMAL(10, 2),
    ecart_type DECIMAL(10, 2),
    nb_mesures INTEGER DEFAULT 0,
    nb_stations INTEGER DEFAULT 0,
    depasse_seuil_oms BOOLEAN,
    ratio_seuil_oms DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(pays_id, polluant_id, annee)
);

COMMENT ON TABLE mesure_pays_annee IS 'Mesures de pollution agrégées au niveau pays-année';

CREATE INDEX idx_mpa_pays ON mesure_pays_annee(pays_id);
CREATE INDEX idx_mpa_polluant ON mesure_pays_annee(polluant_id);
CREATE INDEX idx_mpa_annee ON mesure_pays_annee(annee);

-- =============================================================================
-- TABLE: categorie_indicateur
-- Description: Catégories d'indicateurs socio-économiques (World Bank)
-- =============================================================================
CREATE TABLE categorie_indicateur (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    nom_fr VARCHAR(100),
    description TEXT,
    icone VARCHAR(50),
    ordre_affichage INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE categorie_indicateur IS 'Catégories thématiques des indicateurs World Bank';

-- Insertion des catégories avec descriptions détaillées
INSERT INTO categorie_indicateur (code, nom, nom_fr, description, ordre_affichage) VALUES
('transport', 'Transport', 'Transport',
 'Indicateurs liés au transport, à la mobilité et aux infrastructures routières', 1),
('energie', 'Energy', 'Énergie',
 'Indicateurs liés à la consommation, production et mix énergétique', 2),
('economie', 'Economy', 'Économie',
 'Indicateurs économiques : PIB, industrie, emploi', 3),
('demographie', 'Demographics', 'Démographie',
 'Indicateurs démographiques : population, urbanisation, densité', 4),
('sante', 'Health', 'Santé',
 'Indicateurs de santé publique et exposition environnementale', 5);

-- =============================================================================
-- TABLE: indicateur
-- Description: Référentiel des indicateurs World Bank
-- =============================================================================
CREATE TABLE indicateur (
    id SERIAL PRIMARY KEY,
    code_wb VARCHAR(50) UNIQUE NOT NULL,
    nom VARCHAR(200) NOT NULL,
    nom_fr VARCHAR(200),
    categorie_id INTEGER REFERENCES categorie_indicateur(id),
    unite VARCHAR(50),
    description TEXT,
    description_fr TEXT,
    source VARCHAR(100) DEFAULT 'World Bank',
    url_source VARCHAR(500),
    annee_debut INTEGER,
    annee_fin INTEGER,
    couverture_pays DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE indicateur IS 'Référentiel des indicateurs socio-économiques World Bank';
COMMENT ON COLUMN indicateur.code_wb IS 'Code officiel World Bank (ex: NY.GDP.PCAP.CD)';
COMMENT ON COLUMN indicateur.couverture_pays IS 'Pourcentage de pays avec données disponibles';

CREATE INDEX idx_indicateur_categorie ON indicateur(categorie_id);
CREATE INDEX idx_indicateur_code ON indicateur(code_wb);

-- Insertion des indicateurs utilisés dans l'analyse
-- TRANSPORT
INSERT INTO indicateur (code_wb, nom, nom_fr, categorie_id, unite, description_fr) VALUES
('IS.VEH.NVEH.P3', 'Motor vehicles (per 1,000 people)', 'Véhicules motorisés (pour 1000 hab.)',
 (SELECT id FROM categorie_indicateur WHERE code='transport'), 'pour 1000 hab.',
 'Nombre de véhicules motorisés pour 1000 habitants'),
('IS.VEH.PCAR.P3', 'Passenger cars (per 1,000 people)', 'Voitures particulières (pour 1000 hab.)',
 (SELECT id FROM categorie_indicateur WHERE code='transport'), 'pour 1000 hab.',
 'Nombre de voitures particulières pour 1000 habitants'),
('IS.ROD.TOTL.KM', 'Roads, total network (km)', 'Réseau routier total (km)',
 (SELECT id FROM categorie_indicateur WHERE code='transport'), 'km',
 'Longueur totale du réseau routier'),
('IS.ROD.PAVE.ZS', 'Roads, paved (% of total roads)', 'Routes goudronnées (%)',
 (SELECT id FROM categorie_indicateur WHERE code='transport'), '%',
 'Pourcentage de routes goudronnées'),
('IS.AIR.PSGR', 'Air transport, passengers carried', 'Transport aérien, passagers',
 (SELECT id FROM categorie_indicateur WHERE code='transport'), 'passagers',
 'Nombre de passagers transportés par avion'),
('IS.AIR.DPRT', 'Air transport, registered carrier departures worldwide', 'Départs aériens',
 (SELECT id FROM categorie_indicateur WHERE code='transport'), 'départs',
 'Nombre de départs de vols enregistrés'),
('IS.RRS.TOTL.KM', 'Rail lines (total route-km)', 'Lignes ferroviaires (km)',
 (SELECT id FROM categorie_indicateur WHERE code='transport'), 'km',
 'Longueur totale des lignes ferroviaires');

-- ENERGIE
INSERT INTO indicateur (code_wb, nom, nom_fr, categorie_id, unite, description_fr) VALUES
('EG.USE.PCAP.KG.OE', 'Energy use (kg of oil equivalent per capita)', 'Consommation énergie par habitant',
 (SELECT id FROM categorie_indicateur WHERE code='energie'), 'kg eq. pétrole/hab.',
 'Consommation d''énergie primaire par habitant en équivalent pétrole'),
('EG.USE.ELEC.KH.PC', 'Electric power consumption (kWh per capita)', 'Consommation électricité par habitant',
 (SELECT id FROM categorie_indicateur WHERE code='energie'), 'kWh/hab.',
 'Consommation d''électricité par habitant'),
('EG.ELC.FOSL.ZS', 'Electricity production from fossil fuels (% of total)', 'Électricité fossile (%)',
 (SELECT id FROM categorie_indicateur WHERE code='energie'), '%',
 'Part de l''électricité produite à partir de combustibles fossiles'),
('EG.ELC.RNWX.ZS', 'Renewable electricity output (% of total)', 'Électricité renouvelable (%)',
 (SELECT id FROM categorie_indicateur WHERE code='energie'), '%',
 'Part de l''électricité produite à partir de sources renouvelables'),
('EG.ELC.NUCL.ZS', 'Electricity production from nuclear sources (% of total)', 'Électricité nucléaire (%)',
 (SELECT id FROM categorie_indicateur WHERE code='energie'), '%',
 'Part de l''électricité produite à partir du nucléaire'),
('EN.ATM.CO2E.PC', 'CO2 emissions (metric tons per capita)', 'Émissions CO2 par habitant',
 (SELECT id FROM categorie_indicateur WHERE code='energie'), 't/hab.',
 'Émissions de CO2 par habitant en tonnes métriques'),
('EN.ATM.CO2E.KT', 'CO2 emissions (kt)', 'Émissions CO2 totales',
 (SELECT id FROM categorie_indicateur WHERE code='energie'), 'kt',
 'Émissions totales de CO2 en kilotonnes'),
('EN.ATM.METH.KT.CE', 'Methane emissions (kt of CO2 equivalent)', 'Émissions méthane',
 (SELECT id FROM categorie_indicateur WHERE code='energie'), 'kt eq. CO2',
 'Émissions de méthane en équivalent CO2'),
('EN.ATM.NOXE.KT.CE', 'Nitrous oxide emissions (kt of CO2 equivalent)', 'Émissions protoxyde azote',
 (SELECT id FROM categorie_indicateur WHERE code='energie'), 'kt eq. CO2',
 'Émissions de protoxyde d''azote en équivalent CO2');

-- ECONOMIE
INSERT INTO indicateur (code_wb, nom, nom_fr, categorie_id, unite, description_fr) VALUES
('NY.GDP.PCAP.CD', 'GDP per capita (current US$)', 'PIB par habitant (USD)',
 (SELECT id FROM categorie_indicateur WHERE code='economie'), 'USD',
 'Produit intérieur brut par habitant en dollars courants'),
('NY.GDP.PCAP.PP.CD', 'GDP per capita, PPP (current international $)', 'PIB par habitant (PPA)',
 (SELECT id FROM categorie_indicateur WHERE code='economie'), 'USD PPA',
 'PIB par habitant en parité de pouvoir d''achat'),
('NV.IND.TOTL.ZS', 'Industry (including construction), value added (% of GDP)', 'Industrie (% PIB)',
 (SELECT id FROM categorie_indicateur WHERE code='economie'), '% PIB',
 'Part de l''industrie dans le PIB'),
('NV.IND.MANF.ZS', 'Manufacturing, value added (% of GDP)', 'Manufacture (% PIB)',
 (SELECT id FROM categorie_indicateur WHERE code='economie'), '% PIB',
 'Part de la manufacture dans le PIB'),
('NV.SRV.TOTL.ZS', 'Services, value added (% of GDP)', 'Services (% PIB)',
 (SELECT id FROM categorie_indicateur WHERE code='economie'), '% PIB',
 'Part des services dans le PIB'),
('NV.AGR.TOTL.ZS', 'Agriculture, value added (% of GDP)', 'Agriculture (% PIB)',
 (SELECT id FROM categorie_indicateur WHERE code='economie'), '% PIB',
 'Part de l''agriculture dans le PIB'),
('SL.IND.EMPL.ZS', 'Employment in industry (% of total employment)', 'Emploi industriel (%)',
 (SELECT id FROM categorie_indicateur WHERE code='economie'), '%',
 'Part de l''emploi dans l''industrie'),
('SL.AGR.EMPL.ZS', 'Employment in agriculture (% of total employment)', 'Emploi agricole (%)',
 (SELECT id FROM categorie_indicateur WHERE code='economie'), '%',
 'Part de l''emploi dans l''agriculture'),
('SL.SRV.EMPL.ZS', 'Employment in services (% of total employment)', 'Emploi services (%)',
 (SELECT id FROM categorie_indicateur WHERE code='economie'), '%',
 'Part de l''emploi dans les services');

-- DEMOGRAPHIE
INSERT INTO indicateur (code_wb, nom, nom_fr, categorie_id, unite, description_fr) VALUES
('SP.POP.TOTL', 'Population, total', 'Population totale',
 (SELECT id FROM categorie_indicateur WHERE code='demographie'), 'habitants',
 'Population totale du pays'),
('SP.URB.TOTL', 'Urban population', 'Population urbaine',
 (SELECT id FROM categorie_indicateur WHERE code='demographie'), 'habitants',
 'Population vivant en zone urbaine'),
('SP.URB.TOTL.IN.ZS', 'Urban population (% of total population)', 'Taux urbanisation (%)',
 (SELECT id FROM categorie_indicateur WHERE code='demographie'), '%',
 'Pourcentage de la population vivant en zone urbaine'),
('SP.URB.GROW', 'Urban population growth (annual %)', 'Croissance urbaine annuelle',
 (SELECT id FROM categorie_indicateur WHERE code='demographie'), '%/an',
 'Taux de croissance annuel de la population urbaine'),
('EN.POP.DNST', 'Population density (people per sq. km)', 'Densité population',
 (SELECT id FROM categorie_indicateur WHERE code='demographie'), 'hab./km²',
 'Densité de population'),
('AG.LND.TOTL.K2', 'Land area (sq. km)', 'Superficie totale',
 (SELECT id FROM categorie_indicateur WHERE code='demographie'), 'km²',
 'Superficie terrestre totale'),
('EN.URB.LCTY', 'Population in largest city', 'Population plus grande ville',
 (SELECT id FROM categorie_indicateur WHERE code='demographie'), 'habitants',
 'Population de la plus grande ville'),
('EN.URB.LCTY.UR.ZS', 'Population in largest city (% of urban population)', 'Primatie urbaine (%)',
 (SELECT id FROM categorie_indicateur WHERE code='demographie'), '%',
 'Part de la plus grande ville dans la population urbaine'),
('AG.LND.FRST.ZS', 'Forest area (% of land area)', 'Couverture forestière (%)',
 (SELECT id FROM categorie_indicateur WHERE code='demographie'), '%',
 'Pourcentage de la superficie couverte de forêts');

-- SANTE
INSERT INTO indicateur (code_wb, nom, nom_fr, categorie_id, unite, description_fr) VALUES
('EN.ATM.PM25.MC.M3', 'PM2.5 air pollution, mean annual exposure', 'Exposition PM2.5 moyenne',
 (SELECT id FROM categorie_indicateur WHERE code='sante'), 'µg/m³',
 'Exposition moyenne annuelle aux PM2.5 (estimation satellite)'),
('EN.ATM.PM25.MC.ZS', 'PM2.5 pollution, population exposed to levels exceeding WHO guideline', 'Population exposée PM2.5 (%)',
 (SELECT id FROM categorie_indicateur WHERE code='sante'), '%',
 'Part de la population exposée à des niveaux de PM2.5 supérieurs aux recommandations OMS'),
('SH.STA.AIRP.P5', 'Mortality rate attributed to air pollution (per 100,000)', 'Mortalité pollution air',
 (SELECT id FROM categorie_indicateur WHERE code='sante'), 'pour 100 000',
 'Taux de mortalité attribuable à la pollution de l''air'),
('SP.DYN.LE00.IN', 'Life expectancy at birth, total (years)', 'Espérance de vie',
 (SELECT id FROM categorie_indicateur WHERE code='sante'), 'années',
 'Espérance de vie à la naissance'),
('SH.XPD.CHEX.PC.CD', 'Current health expenditure per capita (current US$)', 'Dépenses santé par habitant',
 (SELECT id FROM categorie_indicateur WHERE code='sante'), 'USD/hab.',
 'Dépenses de santé courantes par habitant'),
('SH.XPD.CHEX.GD.ZS', 'Current health expenditure (% of GDP)', 'Dépenses santé (% PIB)',
 (SELECT id FROM categorie_indicateur WHERE code='sante'), '% PIB',
 'Part des dépenses de santé dans le PIB');

-- =============================================================================
-- TABLE: indicateur_pays
-- Description: Valeurs des indicateurs par pays et année
-- =============================================================================
CREATE TABLE indicateur_pays (
    id SERIAL PRIMARY KEY,
    pays_id INTEGER REFERENCES pays(id) ON DELETE CASCADE NOT NULL,
    indicateur_id INTEGER REFERENCES indicateur(id) ON DELETE CASCADE NOT NULL,
    annee INTEGER NOT NULL CHECK (annee BETWEEN 2000 AND 2030),
    valeur DECIMAL(20, 4),
    est_estimation BOOLEAN DEFAULT FALSE,
    source_specifique VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(pays_id, indicateur_id, annee)
);

COMMENT ON TABLE indicateur_pays IS 'Valeurs des indicateurs World Bank par pays et année';

CREATE INDEX idx_ind_pays_pays ON indicateur_pays(pays_id);
CREATE INDEX idx_ind_pays_indicateur ON indicateur_pays(indicateur_id);
CREATE INDEX idx_ind_pays_annee ON indicateur_pays(annee);
CREATE INDEX idx_ind_pays_valeur ON indicateur_pays(valeur);

-- =============================================================================
-- VUES ANALYTIQUES
-- =============================================================================

-- Vue: Moyennes de pollution par pays et année
CREATE OR REPLACE VIEW v_pollution_pays_annee AS
SELECT
    p.id AS pays_id,
    p.code_iso2,
    p.code_iso3,
    p.nom AS pays,
    r.nom AS region,
    pol.code AS polluant,
    pol.nom AS polluant_nom,
    pol.seuil_oms_annuel,
    mpa.annee,
    mpa.moyenne,
    mpa.mediane,
    mpa.minimum,
    mpa.maximum,
    mpa.ecart_type,
    mpa.nb_mesures,
    mpa.nb_stations,
    mpa.depasse_seuil_oms,
    mpa.ratio_seuil_oms,
    CASE
        WHEN pol.seuil_oms_annuel IS NOT NULL AND mpa.moyenne > pol.seuil_oms_annuel
        THEN ROUND((mpa.moyenne / pol.seuil_oms_annuel)::numeric, 1)
        ELSE NULL
    END AS facteur_depassement
FROM mesure_pays_annee mpa
JOIN pays p ON mpa.pays_id = p.id
LEFT JOIN region r ON p.region_id = r.id
JOIN polluant pol ON mpa.polluant_id = pol.id;

COMMENT ON VIEW v_pollution_pays_annee IS 'Vue agrégée de la pollution par pays et année avec seuils OMS';

-- Vue: Indicateurs les plus récents par pays
CREATE OR REPLACE VIEW v_indicateurs_recents AS
SELECT DISTINCT ON (ip.pays_id, ip.indicateur_id)
    p.code_iso2,
    p.code_iso3,
    p.nom AS pays,
    i.code_wb,
    i.nom_fr AS indicateur,
    c.nom_fr AS categorie,
    i.unite,
    ip.annee,
    ip.valeur
FROM indicateur_pays ip
JOIN pays p ON ip.pays_id = p.id
JOIN indicateur i ON ip.indicateur_id = i.id
LEFT JOIN categorie_indicateur c ON i.categorie_id = c.id
WHERE ip.valeur IS NOT NULL
ORDER BY ip.pays_id, ip.indicateur_id, ip.annee DESC;

COMMENT ON VIEW v_indicateurs_recents IS 'Dernières valeurs disponibles des indicateurs par pays';

-- Vue: Synthèse complète par pays
CREATE OR REPLACE VIEW v_synthese_pays AS
SELECT
    p.code_iso2,
    p.code_iso3,
    p.nom AS pays,
    r.nom AS region,
    p.nb_villes,
    p.population_urbaine_totale,
    COUNT(DISTINCT s.id) AS nb_stations,
    COUNT(DISTINCT mpa.id) AS nb_mesures_agregees,
    COUNT(DISTINCT mpa.annee) AS nb_annees_donnees,
    MIN(mpa.annee) AS premiere_annee,
    MAX(mpa.annee) AS derniere_annee
FROM pays p
LEFT JOIN region r ON p.region_id = r.id
LEFT JOIN station s ON s.pays_id = p.id
LEFT JOIN mesure_pays_annee mpa ON mpa.pays_id = p.id
GROUP BY p.id, p.code_iso2, p.code_iso3, p.nom, r.nom, p.nb_villes, p.population_urbaine_totale;

COMMENT ON VIEW v_synthese_pays IS 'Synthèse des données disponibles par pays';

-- Vue: Dépassements des seuils OMS
CREATE OR REPLACE VIEW v_depassements_oms AS
SELECT
    p.code_iso2,
    p.nom AS pays,
    r.nom AS region,
    pol.code AS polluant,
    pol.seuil_oms_annuel AS seuil_oms,
    mpa.annee,
    mpa.moyenne AS valeur_mesuree,
    ROUND((mpa.moyenne / pol.seuil_oms_annuel * 100)::numeric, 1) AS pct_seuil,
    CASE
        WHEN mpa.moyenne <= pol.seuil_oms_annuel THEN 'Conforme'
        WHEN mpa.moyenne <= pol.seuil_oms_annuel * 2 THEN 'Dépassement modéré'
        WHEN mpa.moyenne <= pol.seuil_oms_annuel * 5 THEN 'Dépassement important'
        ELSE 'Dépassement critique'
    END AS niveau_alerte
FROM mesure_pays_annee mpa
JOIN pays p ON mpa.pays_id = p.id
LEFT JOIN region r ON p.region_id = r.id
JOIN polluant pol ON mpa.polluant_id = pol.id
WHERE pol.seuil_oms_annuel IS NOT NULL
ORDER BY mpa.annee DESC, pct_seuil DESC;

COMMENT ON VIEW v_depassements_oms IS 'Analyse des dépassements des seuils OMS par pays';

-- Vue: Évolution temporelle de la pollution
CREATE OR REPLACE VIEW v_evolution_temporelle AS
SELECT
    p.code_iso2,
    p.nom AS pays,
    pol.code AS polluant,
    mpa.annee,
    mpa.moyenne,
    LAG(mpa.moyenne) OVER (PARTITION BY p.id, pol.id ORDER BY mpa.annee) AS moyenne_annee_prec,
    CASE
        WHEN LAG(mpa.moyenne) OVER (PARTITION BY p.id, pol.id ORDER BY mpa.annee) IS NOT NULL
        THEN ROUND(((mpa.moyenne - LAG(mpa.moyenne) OVER (PARTITION BY p.id, pol.id ORDER BY mpa.annee))
             / LAG(mpa.moyenne) OVER (PARTITION BY p.id, pol.id ORDER BY mpa.annee) * 100)::numeric, 2)
        ELSE NULL
    END AS variation_pct
FROM mesure_pays_annee mpa
JOIN pays p ON mpa.pays_id = p.id
JOIN polluant pol ON mpa.polluant_id = pol.id
ORDER BY p.code_iso2, pol.code, mpa.annee;

COMMENT ON VIEW v_evolution_temporelle IS 'Évolution temporelle de la pollution avec variations annuelles';

-- Vue: Corrélation pollution-indicateurs (données pour analyse)
CREATE OR REPLACE VIEW v_analyse_correlation AS
SELECT
    p.code_iso2,
    p.nom AS pays,
    mpa.annee,
    pol.code AS polluant,
    mpa.moyenne AS pollution,
    i.code_wb,
    i.nom_fr AS indicateur,
    c.nom_fr AS categorie,
    ip.valeur AS valeur_indicateur
FROM mesure_pays_annee mpa
JOIN pays p ON mpa.pays_id = p.id
JOIN polluant pol ON mpa.polluant_id = pol.id
JOIN indicateur_pays ip ON ip.pays_id = p.id AND ip.annee = mpa.annee
JOIN indicateur i ON ip.indicateur_id = i.id
LEFT JOIN categorie_indicateur c ON i.categorie_id = c.id
WHERE mpa.moyenne IS NOT NULL AND ip.valeur IS NOT NULL
ORDER BY p.code_iso2, mpa.annee, pol.code, i.code_wb;

COMMENT ON VIEW v_analyse_correlation IS 'Données jointes pollution-indicateurs pour analyses de corrélation';

-- =============================================================================
-- FONCTIONS ANALYTIQUES
-- =============================================================================

-- Fonction: Obtenir la moyenne de pollution pour un pays, polluant et année
CREATE OR REPLACE FUNCTION get_pollution_moyenne(
    p_pays_code VARCHAR(3),
    p_polluant VARCHAR(10),
    p_annee INTEGER
) RETURNS DECIMAL AS $$
DECLARE
    v_moyenne DECIMAL;
BEGIN
    SELECT mpa.moyenne INTO v_moyenne
    FROM mesure_pays_annee mpa
    JOIN pays p ON mpa.pays_id = p.id
    JOIN polluant pol ON mpa.polluant_id = pol.id
    WHERE (p.code_iso2 = p_pays_code OR p.code_iso3 = p_pays_code)
    AND pol.code = p_polluant
    AND mpa.annee = p_annee;

    RETURN v_moyenne;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_pollution_moyenne IS 'Retourne la moyenne de pollution pour un pays/polluant/année';

-- Fonction: Compter les pays dépassant le seuil OMS
CREATE OR REPLACE FUNCTION count_pays_depassement_oms(
    p_polluant VARCHAR(10),
    p_annee INTEGER
) RETURNS TABLE(
    total_pays INTEGER,
    pays_conforme INTEGER,
    pays_depassement INTEGER,
    pct_depassement DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    WITH stats AS (
        SELECT
            COUNT(DISTINCT mpa.pays_id) AS total,
            COUNT(DISTINCT CASE WHEN mpa.moyenne <= pol.seuil_oms_annuel THEN mpa.pays_id END) AS conforme,
            COUNT(DISTINCT CASE WHEN mpa.moyenne > pol.seuil_oms_annuel THEN mpa.pays_id END) AS depassement
        FROM mesure_pays_annee mpa
        JOIN polluant pol ON mpa.polluant_id = pol.id
        WHERE pol.code = p_polluant
        AND mpa.annee = p_annee
        AND pol.seuil_oms_annuel IS NOT NULL
    )
    SELECT
        s.total::INTEGER,
        s.conforme::INTEGER,
        s.depassement::INTEGER,
        ROUND((s.depassement::DECIMAL / NULLIF(s.total, 0) * 100), 1)
    FROM stats s;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION count_pays_depassement_oms IS 'Statistiques de dépassement OMS pour un polluant et une année';

-- Fonction: Calculer la tendance de pollution sur une période
CREATE OR REPLACE FUNCTION get_tendance_pollution(
    p_pays_code VARCHAR(3),
    p_polluant VARCHAR(10),
    p_annee_debut INTEGER DEFAULT 2018,
    p_annee_fin INTEGER DEFAULT 2023
) RETURNS TABLE(
    annee_debut INTEGER,
    annee_fin INTEGER,
    valeur_debut DECIMAL,
    valeur_fin DECIMAL,
    variation_absolue DECIMAL,
    variation_pct DECIMAL,
    tendance VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    WITH bornes AS (
        SELECT
            MIN(mpa.annee) AS an_debut,
            MAX(mpa.annee) AS an_fin,
            (SELECT mpa2.moyenne FROM mesure_pays_annee mpa2
             JOIN pays p2 ON mpa2.pays_id = p2.id
             JOIN polluant pol2 ON mpa2.polluant_id = pol2.id
             WHERE (p2.code_iso2 = p_pays_code OR p2.code_iso3 = p_pays_code)
             AND pol2.code = p_polluant
             ORDER BY mpa2.annee ASC LIMIT 1) AS val_debut,
            (SELECT mpa3.moyenne FROM mesure_pays_annee mpa3
             JOIN pays p3 ON mpa3.pays_id = p3.id
             JOIN polluant pol3 ON mpa3.polluant_id = pol3.id
             WHERE (p3.code_iso2 = p_pays_code OR p3.code_iso3 = p_pays_code)
             AND pol3.code = p_polluant
             ORDER BY mpa3.annee DESC LIMIT 1) AS val_fin
        FROM mesure_pays_annee mpa
        JOIN pays p ON mpa.pays_id = p.id
        JOIN polluant pol ON mpa.polluant_id = pol.id
        WHERE (p.code_iso2 = p_pays_code OR p.code_iso3 = p_pays_code)
        AND pol.code = p_polluant
        AND mpa.annee BETWEEN p_annee_debut AND p_annee_fin
    )
    SELECT
        b.an_debut,
        b.an_fin,
        b.val_debut,
        b.val_fin,
        ROUND((b.val_fin - b.val_debut)::numeric, 2),
        ROUND(((b.val_fin - b.val_debut) / NULLIF(b.val_debut, 0) * 100)::numeric, 2),
        CASE
            WHEN b.val_fin < b.val_debut * 0.9 THEN 'Amélioration'
            WHEN b.val_fin > b.val_debut * 1.1 THEN 'Dégradation'
            ELSE 'Stable'
        END
    FROM bornes b;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_tendance_pollution IS 'Calcule la tendance de pollution pour un pays sur une période';

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Trigger: Mise à jour automatique du champ updated_at
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_pays_updated
    BEFORE UPDATE ON pays
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Trigger: Calcul automatique du dépassement OMS lors de l'insertion
CREATE OR REPLACE FUNCTION check_seuil_oms()
RETURNS TRIGGER AS $$
DECLARE
    v_seuil DECIMAL;
BEGIN
    SELECT seuil_oms_annuel INTO v_seuil
    FROM polluant WHERE id = NEW.polluant_id;

    IF v_seuil IS NOT NULL AND NEW.moyenne IS NOT NULL THEN
        NEW.depasse_seuil_oms := NEW.moyenne > v_seuil;
        NEW.ratio_seuil_oms := ROUND((NEW.moyenne / v_seuil)::numeric, 2);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_mesure_check_oms
    BEFORE INSERT OR UPDATE ON mesure_pays_annee
    FOR EACH ROW
    EXECUTE FUNCTION check_seuil_oms();

-- =============================================================================
-- COMMENTAIRES FINAUX
-- =============================================================================
COMMENT ON SCHEMA public IS 'Base de données SAE S5.C.01 - Analyse de la Qualité de l''Air Mondiale';

-- =============================================================================
-- FIN DU SCRIPT DE CRÉATION
-- =============================================================================
