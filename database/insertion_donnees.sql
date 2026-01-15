-- =============================================================================
-- SAE S5.C.01 - Analyse de la Qualité de l'Air Mondiale
-- Script d'Insertion des Données
-- =============================================================================
-- Auteur: Équipe SAE S5.C.01
-- Date: Janvier 2026
-- Description: Insertion des données depuis les fichiers CSV traités
-- Prérequis: Exécuter creation_bdd.sql avant ce script
-- =============================================================================

SET client_encoding = 'UTF8';

-- =============================================================================
-- 1. INSERTION DES PAYS
-- =============================================================================
-- Source: data/raw/world_cities_by_country.csv + base_complete.csv

INSERT INTO pays (code_iso2, code_iso3, nom, nb_villes, population_urbaine_totale, latitude_moyenne, longitude_moyenne, region_id)
VALUES
-- Europe
('AD', 'AND', 'Andorra', 8, 105348, 42.52, 1.53, (SELECT id FROM region WHERE code='europe')),
('AT', 'AUT', 'Austria', 106, 4967874, 47.67, 14.18, (SELECT id FROM region WHERE code='europe')),
('BE', 'BEL', 'Belgium', 398, 11351788, 50.87, 4.40, (SELECT id FROM region WHERE code='europe')),
('BG', 'BGR', 'Bulgaria', 98, 5311139, 42.68, 25.16, (SELECT id FROM region WHERE code='europe')),
('BA', 'BIH', 'Bosnia and Herzegovina', 73, 2605815, 44.19, 18.05, (SELECT id FROM region WHERE code='europe')),
('HR', 'HRV', 'Croatia', 76, 2505684, 45.42, 16.49, (SELECT id FROM region WHERE code='europe')),
('CY', 'CYP', 'Cyprus', 16, 961671, 34.93, 33.26, (SELECT id FROM region WHERE code='europe')),
('CZ', 'CZE', 'Czechia', 162, 5961889, 49.89, 15.65, (SELECT id FROM region WHERE code='europe')),
('DK', 'DNK', 'Denmark', 78, 3713495, 55.94, 10.78, (SELECT id FROM region WHERE code='europe')),
('EE', 'EST', 'Estonia', 34, 896449, 58.77, 25.51, (SELECT id FROM region WHERE code='europe')),
('FI', 'FIN', 'Finland', 132, 5911892, 62.04, 24.97, (SELECT id FROM region WHERE code='europe')),
('FR', 'FRA', 'France', 1157, 43756394, 47.19, 2.67, (SELECT id FROM region WHERE code='europe')),
('DE', 'DEU', 'Germany', 1733, 67874418, 50.66, 9.54, (SELECT id FROM region WHERE code='europe')),
('GR', 'GRC', 'Greece', 195, 6786342, 38.75, 23.16, (SELECT id FROM region WHERE code='europe')),
('HU', 'HUN', 'Hungary', 100, 5879624, 47.11, 19.39, (SELECT id FROM region WHERE code='europe')),
('IE', 'IRL', 'Ireland', 65, 2769875, 53.26, -8.12, (SELECT id FROM region WHERE code='europe')),
('IT', 'ITA', 'Italy', 1031, 35879946, 42.69, 12.26, (SELECT id FROM region WHERE code='europe')),
('LV', 'LVA', 'Latvia', 40, 1294553, 56.75, 24.72, (SELECT id FROM region WHERE code='europe')),
('LT', 'LTU', 'Lithuania', 52, 1852766, 55.40, 23.89, (SELECT id FROM region WHERE code='europe')),
('LU', 'LUX', 'Luxembourg', 13, 596182, 49.68, 6.10, (SELECT id FROM region WHERE code='europe')),
('MT', 'MLT', 'Malta', 6, 461673, 35.90, 14.44, (SELECT id FROM region WHERE code='europe')),
('NL', 'NLD', 'Netherlands', 342, 13548037, 52.19, 5.33, (SELECT id FROM region WHERE code='europe')),
('NO', 'NOR', 'Norway', 148, 4128706, 62.80, 9.79, (SELECT id FROM region WHERE code='europe')),
('PL', 'POL', 'Poland', 564, 22698988, 51.86, 19.07, (SELECT id FROM region WHERE code='europe')),
('PT', 'PRT', 'Portugal', 151, 6024805, 39.63, -8.00, (SELECT id FROM region WHERE code='europe')),
('RO', 'ROU', 'Romania', 266, 11056891, 45.49, 25.11, (SELECT id FROM region WHERE code='europe')),
('RS', 'SRB', 'Serbia', 113, 4286816, 44.00, 20.72, (SELECT id FROM region WHERE code='europe')),
('SK', 'SVK', 'Slovakia', 63, 2768093, 48.76, 19.35, (SELECT id FROM region WHERE code='europe')),
('SI', 'SVN', 'Slovenia', 39, 1079049, 46.12, 14.79, (SELECT id FROM region WHERE code='europe')),
('ES', 'ESP', 'Spain', 781, 46143259, 39.36, -2.97, (SELECT id FROM region WHERE code='europe')),
('SE', 'SWE', 'Sweden', 200, 8411811, 60.61, 15.94, (SELECT id FROM region WHERE code='europe')),
('CH', 'CHE', 'Switzerland', 200, 4447753, 47.07, 8.04, (SELECT id FROM region WHERE code='europe')),
('GB', 'GBR', 'United Kingdom', 1346, 64720863, 52.77, -1.68, (SELECT id FROM region WHERE code='europe')),
('UA', 'UKR', 'Ukraine', 413, 26848813, 49.05, 32.42, (SELECT id FROM region WHERE code='europe')),

-- Asie
('BD', 'BGD', 'Bangladesh', 102, 39941504, 23.68, 90.34, (SELECT id FROM region WHERE code='asie')),
('CN', 'CHN', 'China', 2116, 692476073, 34.04, 109.18, (SELECT id FROM region WHERE code='asie')),
('IN', 'IND', 'India', 2282, 399547085, 22.13, 79.94, (SELECT id FROM region WHERE code='asie')),
('ID', 'IDN', 'Indonesia', 509, 97421048, -3.76, 117.82, (SELECT id FROM region WHERE code='asie')),
('JP', 'JPN', 'Japan', 778, 93286671, 36.18, 138.31, (SELECT id FROM region WHERE code='asie')),
('KR', 'KOR', 'South Korea', 186, 37439946, 36.27, 127.79, (SELECT id FROM region WHERE code='asie')),
('MY', 'MYS', 'Malaysia', 103, 18934869, 4.06, 108.75, (SELECT id FROM region WHERE code='asie')),
('MN', 'MNG', 'Mongolia', 35, 2158002, 46.91, 103.75, (SELECT id FROM region WHERE code='asie')),
('PK', 'PAK', 'Pakistan', 350, 77316523, 30.09, 69.38, (SELECT id FROM region WHERE code='asie')),
('PH', 'PHL', 'Philippines', 430, 44925447, 12.57, 122.84, (SELECT id FROM region WHERE code='asie')),
('SG', 'SGP', 'Singapore', 1, 5745000, 1.35, 103.82, (SELECT id FROM region WHERE code='asie')),
('TW', 'TWN', 'Taiwan', 71, 18499693, 23.88, 120.96, (SELECT id FROM region WHERE code='asie')),
('TH', 'THA', 'Thailand', 176, 26051117, 15.03, 101.16, (SELECT id FROM region WHERE code='asie')),
('VN', 'VNM', 'Vietnam', 213, 31844816, 16.11, 107.03, (SELECT id FROM region WHERE code='asie')),

-- Amérique du Nord
('CA', 'CAN', 'Canada', 482, 39754239, 46.70, -86.33, (SELECT id FROM region WHERE code='amerique_nord')),
('US', 'USA', 'United States', 4827, 273523749, 38.13, -96.61, (SELECT id FROM region WHERE code='amerique_nord')),
('MX', 'MEX', 'Mexico', 804, 87568315, 23.47, -101.84, (SELECT id FROM region WHERE code='amerique_nord')),

-- Amérique du Sud
('AR', 'ARG', 'Argentina', 481, 47332368, -33.33, -61.87, (SELECT id FROM region WHERE code='amerique_sud')),
('BR', 'BRA', 'Brazil', 2855, 189333734, -15.69, -45.37, (SELECT id FROM region WHERE code='amerique_sud')),
('CL', 'CHL', 'Chile', 253, 21565501, -35.10, -71.65, (SELECT id FROM region WHERE code='amerique_sud')),
('CO', 'COL', 'Colombia', 399, 37447917, 4.80, -74.08, (SELECT id FROM region WHERE code='amerique_sud')),
('PE', 'PER', 'Peru', 232, 22056155, -10.82, -75.00, (SELECT id FROM region WHERE code='amerique_sud')),
('EC', 'ECU', 'Ecuador', 122, 10571671, -1.39, -78.63, (SELECT id FROM region WHERE code='amerique_sud')),
('VE', 'VEN', 'Venezuela', 221, 22714595, 8.12, -66.44, (SELECT id FROM region WHERE code='amerique_sud')),

-- Afrique
('ZA', 'ZAF', 'South Africa', 212, 32958681, -28.93, 26.23, (SELECT id FROM region WHERE code='afrique')),
('EG', 'EGY', 'Egypt', 187, 57754921, 29.27, 31.30, (SELECT id FROM region WHERE code='afrique')),
('NG', 'NGA', 'Nigeria', 541, 74654891, 9.00, 7.98, (SELECT id FROM region WHERE code='afrique')),
('KE', 'KEN', 'Kenya', 96, 10816361, -0.72, 37.52, (SELECT id FROM region WHERE code='afrique')),
('ET', 'ETH', 'Ethiopia', 141, 14902477, 9.36, 39.04, (SELECT id FROM region WHERE code='afrique')),
('GH', 'GHA', 'Ghana', 138, 11934124, 7.23, -1.33, (SELECT id FROM region WHERE code='afrique')),
('MA', 'MAR', 'Morocco', 215, 17638527, 31.56, -6.86, (SELECT id FROM region WHERE code='afrique')),
('DZ', 'DZA', 'Algeria', 552, 23927042, 35.35, 3.38, (SELECT id FROM region WHERE code='afrique')),
('TN', 'TUN', 'Tunisia', 90, 6890456, 35.36, 9.35, (SELECT id FROM region WHERE code='afrique')),
('UG', 'UGA', 'Uganda', 60, 7581936, 1.18, 32.18, (SELECT id FROM region WHERE code='afrique')),
('RW', 'RWA', 'Rwanda', 19, 1690708, -2.00, 29.67, (SELECT id FROM region WHERE code='afrique')),
('TD', 'TCD', 'Chad', 34, 2548214, 12.74, 17.52, (SELECT id FROM region WHERE code='afrique')),

-- Océanie
('AU', 'AUS', 'Australia', 271, 22831286, -30.43, 141.99, (SELECT id FROM region WHERE code='oceanie')),
('NZ', 'NZL', 'New Zealand', 43, 3615920, -40.43, 173.58, (SELECT id FROM region WHERE code='oceanie')),

-- Moyen-Orient
('AE', 'ARE', 'United Arab Emirates', 12, 7721368, 25.08, 55.52, (SELECT id FROM region WHERE code='moyen_orient')),
('SA', 'SAU', 'Saudi Arabia', 128, 28036313, 24.15, 43.90, (SELECT id FROM region WHERE code='moyen_orient')),
('IL', 'ISR', 'Israel', 63, 6948546, 31.72, 35.00, (SELECT id FROM region WHERE code='moyen_orient')),
('TR', 'TUR', 'Turkey', 475, 53697267, 39.06, 33.92, (SELECT id FROM region WHERE code='moyen_orient')),
('BH', 'BHR', 'Bahrain', 10, 1247814, 26.18, 50.54, (SELECT id FROM region WHERE code='moyen_orient')),
('IR', 'IRN', 'Iran', 392, 56648523, 33.19, 52.58, (SELECT id FROM region WHERE code='moyen_orient')),
('IQ', 'IRQ', 'Iraq', 114, 22741927, 33.45, 43.74, (SELECT id FROM region WHERE code='moyen_orient')),
('JO', 'JOR', 'Jordan', 24, 6698345, 31.58, 36.31, (SELECT id FROM region WHERE code='moyen_orient')),
('KW', 'KWT', 'Kuwait', 10, 3468168, 29.31, 47.64, (SELECT id FROM region WHERE code='moyen_orient')),
('LB', 'LBN', 'Lebanon', 30, 4006983, 33.89, 35.77, (SELECT id FROM region WHERE code='moyen_orient')),
('OM', 'OMN', 'Oman', 27, 2989312, 22.10, 57.53, (SELECT id FROM region WHERE code='moyen_orient')),
('QA', 'QAT', 'Qatar', 4, 2393213, 25.35, 51.23, (SELECT id FROM region WHERE code='moyen_orient'))
ON CONFLICT (code_iso2) DO UPDATE SET
    nom = EXCLUDED.nom,
    nb_villes = EXCLUDED.nb_villes,
    population_urbaine_totale = EXCLUDED.population_urbaine_totale,
    updated_at = CURRENT_TIMESTAMP;

-- =============================================================================
-- 2. INSERTION DES MESURES DE POLLUTION PAR PAYS ET ANNÉE
-- =============================================================================
-- Source: data/raw/openaq_country_averages.csv

-- PM2.5
INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT
    p.id,
    pol.id,
    2018, 84.40, 56.00, 5.00, 282.00, 67.66, 233
FROM pays p, polluant pol WHERE p.code_iso2 = 'BD' AND pol.code = 'pm25'
ON CONFLICT (pays_id, polluant_id, annee) DO UPDATE SET moyenne = EXCLUDED.moyenne, mediane = EXCLUDED.mediane;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2019, 87.18, 58.00, 6.00, 290.00, 68.20, 245
FROM pays p, polluant pol WHERE p.code_iso2 = 'BD' AND pol.code = 'pm25'
ON CONFLICT (pays_id, polluant_id, annee) DO UPDATE SET moyenne = EXCLUDED.moyenne;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2020, 80.13, 52.00, 4.00, 275.00, 65.50, 230
FROM pays p, polluant pol WHERE p.code_iso2 = 'BD' AND pol.code = 'pm25'
ON CONFLICT (pays_id, polluant_id, annee) DO UPDATE SET moyenne = EXCLUDED.moyenne;

-- Données PM2.5 pour pays sélectionnés (2018-2023)
-- Inde
INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2018, 83.50, 75.00, 12.00, 450.00, 58.30, 4520
FROM pays p, polluant pol WHERE p.code_iso2 = 'IN' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2019, 85.20, 77.00, 10.00, 465.00, 60.10, 5230
FROM pays p, polluant pol WHERE p.code_iso2 = 'IN' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2020, 78.40, 70.00, 8.00, 420.00, 55.80, 4890
FROM pays p, polluant pol WHERE p.code_iso2 = 'IN' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2021, 80.10, 72.00, 9.00, 435.00, 57.20, 5120
FROM pays p, polluant pol WHERE p.code_iso2 = 'IN' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2022, 82.30, 74.00, 11.00, 448.00, 58.90, 5340
FROM pays p, polluant pol WHERE p.code_iso2 = 'IN' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2023, 79.80, 71.00, 10.00, 430.00, 56.40, 5450
FROM pays p, polluant pol WHERE p.code_iso2 = 'IN' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

-- France
INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2018, 9.32, 8.50, 2.00, 45.00, 5.20, 2340
FROM pays p, polluant pol WHERE p.code_iso2 = 'FR' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2019, 8.85, 8.00, 1.80, 42.00, 4.90, 2450
FROM pays p, polluant pol WHERE p.code_iso2 = 'FR' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2020, 7.57, 7.00, 1.50, 38.00, 4.30, 2280
FROM pays p, polluant pol WHERE p.code_iso2 = 'FR' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2021, 7.80, 7.20, 1.60, 40.00, 4.50, 2380
FROM pays p, polluant pol WHERE p.code_iso2 = 'FR' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2022, 8.10, 7.50, 1.70, 41.00, 4.60, 2520
FROM pays p, polluant pol WHERE p.code_iso2 = 'FR' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2023, 7.45, 6.80, 1.40, 36.00, 4.10, 2610
FROM pays p, polluant pol WHERE p.code_iso2 = 'FR' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

-- Allemagne
INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2018, 10.77, 10.00, 3.00, 48.00, 5.80, 3450
FROM pays p, polluant pol WHERE p.code_iso2 = 'DE' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2019, 9.85, 9.20, 2.80, 44.00, 5.40, 3520
FROM pays p, polluant pol WHERE p.code_iso2 = 'DE' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2020, 8.00, 7.50, 2.20, 38.00, 4.60, 3280
FROM pays p, polluant pol WHERE p.code_iso2 = 'DE' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2021, 8.30, 7.80, 2.40, 40.00, 4.80, 3450
FROM pays p, polluant pol WHERE p.code_iso2 = 'DE' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2022, 8.50, 8.00, 2.50, 41.00, 4.90, 3580
FROM pays p, polluant pol WHERE p.code_iso2 = 'DE' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2023, 7.80, 7.20, 2.10, 37.00, 4.40, 3620
FROM pays p, polluant pol WHERE p.code_iso2 = 'DE' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

-- Pologne
INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2018, 15.20, 13.50, 4.00, 85.00, 12.30, 1890
FROM pays p, polluant pol WHERE p.code_iso2 = 'PL' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2019, 14.80, 13.00, 3.80, 82.00, 11.90, 1950
FROM pays p, polluant pol WHERE p.code_iso2 = 'PL' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2020, 12.50, 11.00, 3.20, 72.00, 10.50, 1820
FROM pays p, polluant pol WHERE p.code_iso2 = 'PL' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2021, 13.20, 11.80, 3.50, 75.00, 11.00, 1920
FROM pays p, polluant pol WHERE p.code_iso2 = 'PL' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2022, 13.50, 12.00, 3.60, 78.00, 11.20, 2010
FROM pays p, polluant pol WHERE p.code_iso2 = 'PL' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2023, 12.20, 10.80, 3.10, 70.00, 10.20, 2080
FROM pays p, polluant pol WHERE p.code_iso2 = 'PL' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

-- Tchad (très pollué)
INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2021, 164.00, 150.00, 45.00, 380.00, 78.50, 120
FROM pays p, polluant pol WHERE p.code_iso2 = 'TD' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2022, 158.00, 145.00, 42.00, 365.00, 75.20, 135
FROM pays p, polluant pol WHERE p.code_iso2 = 'TD' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2023, 160.00, 148.00, 44.00, 370.00, 76.80, 142
FROM pays p, polluant pol WHERE p.code_iso2 = 'TD' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

-- Mongolie
INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2018, 167.00, 155.00, 20.00, 520.00, 95.30, 890
FROM pays p, polluant pol WHERE p.code_iso2 = 'MN' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2019, 162.00, 150.00, 18.00, 505.00, 92.10, 920
FROM pays p, polluant pol WHERE p.code_iso2 = 'MN' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2020, 148.00, 135.00, 15.00, 480.00, 85.50, 850
FROM pays p, polluant pol WHERE p.code_iso2 = 'MN' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

-- États-Unis
INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2018, 8.50, 7.80, 1.50, 120.00, 8.20, 12500
FROM pays p, polluant pol WHERE p.code_iso2 = 'US' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2019, 8.20, 7.50, 1.40, 115.00, 7.90, 13200
FROM pays p, polluant pol WHERE p.code_iso2 = 'US' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2020, 9.80, 8.20, 1.60, 350.00, 15.50, 12800
FROM pays p, polluant pol WHERE p.code_iso2 = 'US' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2021, 8.90, 7.90, 1.50, 280.00, 12.30, 13500
FROM pays p, polluant pol WHERE p.code_iso2 = 'US' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2022, 8.40, 7.60, 1.45, 250.00, 11.20, 13800
FROM pays p, polluant pol WHERE p.code_iso2 = 'US' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2023, 10.20, 8.50, 1.70, 420.00, 18.50, 14100
FROM pays p, polluant pol WHERE p.code_iso2 = 'US' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

-- Canada
INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2018, 5.39, 4.70, 0.00, 19.40, 3.88, 1224
FROM pays p, polluant pol WHERE p.code_iso2 = 'CA' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2019, 5.12, 4.50, 0.00, 18.20, 3.65, 1340
FROM pays p, polluant pol WHERE p.code_iso2 = 'CA' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2020, 6.80, 5.20, 0.50, 85.00, 8.50, 1280
FROM pays p, polluant pol WHERE p.code_iso2 = 'CA' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2021, 7.50, 5.80, 0.60, 120.00, 12.30, 1420
FROM pays p, polluant pol WHERE p.code_iso2 = 'CA' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2022, 5.85, 5.10, 0.40, 55.00, 5.20, 1520
FROM pays p, polluant pol WHERE p.code_iso2 = 'CA' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2023, 8.90, 6.20, 0.80, 180.00, 15.80, 1580
FROM pays p, polluant pol WHERE p.code_iso2 = 'CA' AND pol.code = 'pm25'
ON CONFLICT DO NOTHING;

-- Australie
INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2018, 7.54, 7.10, 1.10, 16.80, 2.65, 3664
FROM pays p, polluant pol WHERE p.code_iso2 = 'AU' AND pol.code = 'pm10'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2019, 12.30, 8.50, 1.20, 185.00, 18.50, 3720
FROM pays p, polluant pol WHERE p.code_iso2 = 'AU' AND pol.code = 'pm10'
ON CONFLICT DO NOTHING;

INSERT INTO mesure_pays_annee (pays_id, polluant_id, annee, moyenne, mediane, minimum, maximum, ecart_type, nb_mesures)
SELECT p.id, pol.id, 2020, 8.20, 7.50, 1.00, 45.00, 5.80, 3580
FROM pays p, polluant pol WHERE p.code_iso2 = 'AU' AND pol.code = 'pm10'
ON CONFLICT DO NOTHING;

-- =============================================================================
-- 3. INSERTION DES INDICATEURS SOCIO-ÉCONOMIQUES
-- =============================================================================
-- Source: data/raw/worldbank_*.csv

-- Fonction helper pour insérer les indicateurs
CREATE OR REPLACE FUNCTION insert_indicateur_pays(
    p_code_pays VARCHAR(2),
    p_code_wb VARCHAR(50),
    p_annee INTEGER,
    p_valeur DECIMAL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO indicateur_pays (pays_id, indicateur_id, annee, valeur)
    SELECT p.id, i.id, p_annee, p_valeur
    FROM pays p, indicateur i
    WHERE p.code_iso2 = p_code_pays AND i.code_wb = p_code_wb
    ON CONFLICT (pays_id, indicateur_id, annee) DO UPDATE SET valeur = EXCLUDED.valeur;
END;
$$ LANGUAGE plpgsql;

-- Insertion des indicateurs pour la France (exemple complet)
-- Économie
SELECT insert_indicateur_pays('FR', 'NY.GDP.PCAP.CD', 2018, 41526.20);
SELECT insert_indicateur_pays('FR', 'NY.GDP.PCAP.CD', 2019, 40380.10);
SELECT insert_indicateur_pays('FR', 'NY.GDP.PCAP.CD', 2020, 38625.30);
SELECT insert_indicateur_pays('FR', 'NY.GDP.PCAP.CD', 2021, 43518.50);
SELECT insert_indicateur_pays('FR', 'NY.GDP.PCAP.CD', 2022, 40886.20);
SELECT insert_indicateur_pays('FR', 'NY.GDP.PCAP.CD', 2023, 44408.40);

SELECT insert_indicateur_pays('FR', 'NV.IND.TOTL.ZS', 2018, 19.50);
SELECT insert_indicateur_pays('FR', 'NV.IND.TOTL.ZS', 2019, 19.20);
SELECT insert_indicateur_pays('FR', 'NV.IND.TOTL.ZS', 2020, 17.80);
SELECT insert_indicateur_pays('FR', 'NV.IND.TOTL.ZS', 2021, 18.90);
SELECT insert_indicateur_pays('FR', 'NV.IND.TOTL.ZS', 2022, 19.10);

-- Démographie
SELECT insert_indicateur_pays('FR', 'SP.POP.TOTL', 2018, 66987244);
SELECT insert_indicateur_pays('FR', 'SP.POP.TOTL', 2019, 67248926);
SELECT insert_indicateur_pays('FR', 'SP.POP.TOTL', 2020, 67390000);
SELECT insert_indicateur_pays('FR', 'SP.POP.TOTL', 2021, 67750000);
SELECT insert_indicateur_pays('FR', 'SP.POP.TOTL', 2022, 68070000);
SELECT insert_indicateur_pays('FR', 'SP.POP.TOTL', 2023, 68170000);

SELECT insert_indicateur_pays('FR', 'SP.URB.TOTL.IN.ZS', 2018, 80.44);
SELECT insert_indicateur_pays('FR', 'SP.URB.TOTL.IN.ZS', 2019, 80.70);
SELECT insert_indicateur_pays('FR', 'SP.URB.TOTL.IN.ZS', 2020, 80.97);
SELECT insert_indicateur_pays('FR', 'SP.URB.TOTL.IN.ZS', 2021, 81.23);
SELECT insert_indicateur_pays('FR', 'SP.URB.TOTL.IN.ZS', 2022, 81.49);

SELECT insert_indicateur_pays('FR', 'EN.POP.DNST', 2018, 122.30);
SELECT insert_indicateur_pays('FR', 'EN.POP.DNST', 2019, 122.80);
SELECT insert_indicateur_pays('FR', 'EN.POP.DNST', 2020, 123.10);

-- Énergie
SELECT insert_indicateur_pays('FR', 'EG.ELC.FOSL.ZS', 2018, 10.20);
SELECT insert_indicateur_pays('FR', 'EG.ELC.FOSL.ZS', 2019, 9.80);
SELECT insert_indicateur_pays('FR', 'EG.ELC.FOSL.ZS', 2020, 9.50);

SELECT insert_indicateur_pays('FR', 'EG.ELC.NUCL.ZS', 2018, 71.70);
SELECT insert_indicateur_pays('FR', 'EG.ELC.NUCL.ZS', 2019, 70.60);
SELECT insert_indicateur_pays('FR', 'EG.ELC.NUCL.ZS', 2020, 67.10);

SELECT insert_indicateur_pays('FR', 'EN.ATM.CO2E.PC', 2018, 4.96);
SELECT insert_indicateur_pays('FR', 'EN.ATM.CO2E.PC', 2019, 4.81);
SELECT insert_indicateur_pays('FR', 'EN.ATM.CO2E.PC', 2020, 4.24);

-- Santé
SELECT insert_indicateur_pays('FR', 'SP.DYN.LE00.IN', 2018, 82.72);
SELECT insert_indicateur_pays('FR', 'SP.DYN.LE00.IN', 2019, 82.78);
SELECT insert_indicateur_pays('FR', 'SP.DYN.LE00.IN', 2020, 82.18);
SELECT insert_indicateur_pays('FR', 'SP.DYN.LE00.IN', 2021, 82.50);
SELECT insert_indicateur_pays('FR', 'SP.DYN.LE00.IN', 2022, 82.20);

SELECT insert_indicateur_pays('FR', 'EN.ATM.PM25.MC.M3', 2018, 11.40);
SELECT insert_indicateur_pays('FR', 'EN.ATM.PM25.MC.M3', 2019, 10.80);
SELECT insert_indicateur_pays('FR', 'EN.ATM.PM25.MC.M3', 2020, 9.50);

-- Allemagne
SELECT insert_indicateur_pays('DE', 'NY.GDP.PCAP.CD', 2018, 47939.00);
SELECT insert_indicateur_pays('DE', 'NY.GDP.PCAP.CD', 2019, 46794.90);
SELECT insert_indicateur_pays('DE', 'NY.GDP.PCAP.CD', 2020, 46208.40);
SELECT insert_indicateur_pays('DE', 'NY.GDP.PCAP.CD', 2021, 50795.50);
SELECT insert_indicateur_pays('DE', 'NY.GDP.PCAP.CD', 2022, 48636.00);
SELECT insert_indicateur_pays('DE', 'SP.URB.TOTL.IN.ZS', 2018, 77.31);
SELECT insert_indicateur_pays('DE', 'SP.URB.TOTL.IN.ZS', 2019, 77.41);
SELECT insert_indicateur_pays('DE', 'SP.URB.TOTL.IN.ZS', 2020, 77.51);
SELECT insert_indicateur_pays('DE', 'EG.ELC.FOSL.ZS', 2018, 50.50);
SELECT insert_indicateur_pays('DE', 'EG.ELC.FOSL.ZS', 2019, 44.30);
SELECT insert_indicateur_pays('DE', 'SP.DYN.LE00.IN', 2018, 81.02);
SELECT insert_indicateur_pays('DE', 'SP.DYN.LE00.IN', 2019, 81.26);
SELECT insert_indicateur_pays('DE', 'SP.DYN.LE00.IN', 2020, 80.94);

-- Inde
SELECT insert_indicateur_pays('IN', 'NY.GDP.PCAP.CD', 2018, 1998.20);
SELECT insert_indicateur_pays('IN', 'NY.GDP.PCAP.CD', 2019, 2100.75);
SELECT insert_indicateur_pays('IN', 'NY.GDP.PCAP.CD', 2020, 1913.17);
SELECT insert_indicateur_pays('IN', 'NY.GDP.PCAP.CD', 2021, 2238.11);
SELECT insert_indicateur_pays('IN', 'NY.GDP.PCAP.CD', 2022, 2389.00);
SELECT insert_indicateur_pays('IN', 'SP.URB.TOTL.IN.ZS', 2018, 34.03);
SELECT insert_indicateur_pays('IN', 'SP.URB.TOTL.IN.ZS', 2019, 34.47);
SELECT insert_indicateur_pays('IN', 'SP.URB.TOTL.IN.ZS', 2020, 34.93);
SELECT insert_indicateur_pays('IN', 'NV.IND.TOTL.ZS', 2018, 29.35);
SELECT insert_indicateur_pays('IN', 'NV.IND.TOTL.ZS', 2019, 27.58);
SELECT insert_indicateur_pays('IN', 'NV.IND.TOTL.ZS', 2020, 25.83);
SELECT insert_indicateur_pays('IN', 'SP.DYN.LE00.IN', 2018, 69.42);
SELECT insert_indicateur_pays('IN', 'SP.DYN.LE00.IN', 2019, 69.66);
SELECT insert_indicateur_pays('IN', 'SP.DYN.LE00.IN', 2020, 67.24);

-- Pologne
SELECT insert_indicateur_pays('PL', 'NY.GDP.PCAP.CD', 2018, 15468.50);
SELECT insert_indicateur_pays('PL', 'NY.GDP.PCAP.CD', 2019, 15692.80);
SELECT insert_indicateur_pays('PL', 'NY.GDP.PCAP.CD', 2020, 15656.30);
SELECT insert_indicateur_pays('PL', 'NY.GDP.PCAP.CD', 2021, 17999.90);
SELECT insert_indicateur_pays('PL', 'SP.URB.TOTL.IN.ZS', 2018, 60.05);
SELECT insert_indicateur_pays('PL', 'SP.URB.TOTL.IN.ZS', 2019, 60.03);
SELECT insert_indicateur_pays('PL', 'EG.ELC.FOSL.ZS', 2018, 89.50);
SELECT insert_indicateur_pays('PL', 'EG.ELC.FOSL.ZS', 2019, 87.20);
SELECT insert_indicateur_pays('PL', 'EG.ELC.FOSL.ZS', 2020, 83.10);
SELECT insert_indicateur_pays('PL', 'SP.DYN.LE00.IN', 2018, 77.71);
SELECT insert_indicateur_pays('PL', 'SP.DYN.LE00.IN', 2019, 77.84);
SELECT insert_indicateur_pays('PL', 'SP.DYN.LE00.IN', 2020, 75.55);

-- États-Unis
SELECT insert_indicateur_pays('US', 'NY.GDP.PCAP.CD', 2018, 63064.00);
SELECT insert_indicateur_pays('US', 'NY.GDP.PCAP.CD', 2019, 65279.50);
SELECT insert_indicateur_pays('US', 'NY.GDP.PCAP.CD', 2020, 63593.40);
SELECT insert_indicateur_pays('US', 'NY.GDP.PCAP.CD', 2021, 70219.50);
SELECT insert_indicateur_pays('US', 'NY.GDP.PCAP.CD', 2022, 76398.60);
SELECT insert_indicateur_pays('US', 'SP.URB.TOTL.IN.ZS', 2018, 82.46);
SELECT insert_indicateur_pays('US', 'SP.URB.TOTL.IN.ZS', 2019, 82.59);
SELECT insert_indicateur_pays('US', 'EG.ELC.FOSL.ZS', 2018, 63.50);
SELECT insert_indicateur_pays('US', 'EG.ELC.FOSL.ZS', 2019, 62.70);
SELECT insert_indicateur_pays('US', 'SP.DYN.LE00.IN', 2018, 78.54);
SELECT insert_indicateur_pays('US', 'SP.DYN.LE00.IN', 2019, 78.79);
SELECT insert_indicateur_pays('US', 'SP.DYN.LE00.IN', 2020, 77.00);

-- Bangladesh
SELECT insert_indicateur_pays('BD', 'NY.GDP.PCAP.CD', 2018, 1698.35);
SELECT insert_indicateur_pays('BD', 'NY.GDP.PCAP.CD', 2019, 1855.74);
SELECT insert_indicateur_pays('BD', 'NY.GDP.PCAP.CD', 2020, 1968.78);
SELECT insert_indicateur_pays('BD', 'SP.URB.TOTL.IN.ZS', 2018, 36.63);
SELECT insert_indicateur_pays('BD', 'SP.URB.TOTL.IN.ZS', 2019, 37.41);
SELECT insert_indicateur_pays('BD', 'SP.URB.TOTL.IN.ZS', 2020, 38.17);
SELECT insert_indicateur_pays('BD', 'NV.IND.TOTL.ZS', 2018, 30.08);
SELECT insert_indicateur_pays('BD', 'NV.IND.TOTL.ZS', 2019, 31.01);
SELECT insert_indicateur_pays('BD', 'SP.DYN.LE00.IN', 2018, 72.32);
SELECT insert_indicateur_pays('BD', 'SP.DYN.LE00.IN', 2019, 72.59);
SELECT insert_indicateur_pays('BD', 'EN.ATM.PM25.MC.M3', 2018, 76.18);
SELECT insert_indicateur_pays('BD', 'EN.ATM.PM25.MC.M3', 2019, 76.74);

-- Suppression de la fonction helper
DROP FUNCTION IF EXISTS insert_indicateur_pays;

-- =============================================================================
-- 4. VÉRIFICATION DES DONNÉES INSÉRÉES
-- =============================================================================

-- Statistiques d'insertion
DO $$
DECLARE
    v_nb_pays INTEGER;
    v_nb_mesures INTEGER;
    v_nb_indicateurs INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_nb_pays FROM pays;
    SELECT COUNT(*) INTO v_nb_mesures FROM mesure_pays_annee;
    SELECT COUNT(*) INTO v_nb_indicateurs FROM indicateur_pays;

    RAISE NOTICE '=== STATISTIQUES D''INSERTION ===';
    RAISE NOTICE 'Pays insérés: %', v_nb_pays;
    RAISE NOTICE 'Mesures pollution: %', v_nb_mesures;
    RAISE NOTICE 'Valeurs indicateurs: %', v_nb_indicateurs;
END $$;

-- =============================================================================
-- FIN DU SCRIPT D'INSERTION
-- =============================================================================
