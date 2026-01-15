-- =============================================================================
-- SAE S5.C.01 - Analyse de la Qualité de l'Air Mondiale
-- Requêtes d'Analyse SQL
-- =============================================================================
-- Auteur: Équipe SAE S5.C.01
-- Date: Janvier 2026
-- Description: Requêtes SQL pour répondre aux questions de recherche du projet
-- =============================================================================

-- =============================================================================
-- SECTION 1: STATISTIQUES DESCRIPTIVES
-- =============================================================================

-- Q1: Nombre de pays et mesures par polluant
-- Objectif: Vue d'ensemble de la couverture des données
SELECT
    pol.code AS polluant,
    pol.nom AS nom_polluant,
    COUNT(DISTINCT mpa.pays_id) AS nb_pays,
    COUNT(*) AS nb_mesures_total,
    MIN(mpa.annee) AS premiere_annee,
    MAX(mpa.annee) AS derniere_annee
FROM mesure_pays_annee mpa
JOIN polluant pol ON mpa.polluant_id = pol.id
GROUP BY pol.code, pol.nom
ORDER BY nb_pays DESC;

-- Q2: Top 10 des pays les plus pollués (PM2.5, dernière année disponible)
-- Objectif: Identifier les pays prioritaires pour l'analyse
WITH derniere_annee AS (
    SELECT MAX(annee) AS annee FROM mesure_pays_annee
    WHERE polluant_id = (SELECT id FROM polluant WHERE code = 'pm25')
)
SELECT
    p.code_iso2,
    p.nom AS pays,
    r.nom AS region,
    ROUND(mpa.moyenne::numeric, 1) AS pm25_moyenne,
    pol.seuil_oms_annuel AS seuil_oms,
    ROUND((mpa.moyenne / pol.seuil_oms_annuel)::numeric, 1) AS ratio_oms,
    CASE
        WHEN mpa.moyenne <= pol.seuil_oms_annuel THEN 'Conforme OMS'
        WHEN mpa.moyenne <= pol.seuil_oms_annuel * 3 THEN 'Dépassement modéré'
        WHEN mpa.moyenne <= pol.seuil_oms_annuel * 10 THEN 'Dépassement élevé'
        ELSE 'Dépassement critique'
    END AS niveau_alerte
FROM mesure_pays_annee mpa
JOIN pays p ON mpa.pays_id = p.id
LEFT JOIN region r ON p.region_id = r.id
JOIN polluant pol ON mpa.polluant_id = pol.id
CROSS JOIN derniere_annee da
WHERE pol.code = 'pm25'
AND mpa.annee = da.annee
ORDER BY mpa.moyenne DESC
LIMIT 10;

-- Q3: Top 10 des pays les moins pollués (PM2.5)
WITH derniere_annee AS (
    SELECT MAX(annee) AS annee FROM mesure_pays_annee
    WHERE polluant_id = (SELECT id FROM polluant WHERE code = 'pm25')
)
SELECT
    p.code_iso2,
    p.nom AS pays,
    r.nom AS region,
    ROUND(mpa.moyenne::numeric, 1) AS pm25_moyenne,
    pol.seuil_oms_annuel AS seuil_oms,
    CASE WHEN mpa.moyenne <= pol.seuil_oms_annuel THEN 'OUI' ELSE 'NON' END AS conforme_oms
FROM mesure_pays_annee mpa
JOIN pays p ON mpa.pays_id = p.id
LEFT JOIN region r ON p.region_id = r.id
JOIN polluant pol ON mpa.polluant_id = pol.id
CROSS JOIN derniere_annee da
WHERE pol.code = 'pm25'
AND mpa.annee = da.annee
AND mpa.moyenne IS NOT NULL
ORDER BY mpa.moyenne ASC
LIMIT 10;

-- Q4: Statistiques par région géographique
SELECT
    r.nom AS region,
    COUNT(DISTINCT p.id) AS nb_pays,
    ROUND(AVG(mpa.moyenne)::numeric, 2) AS pm25_moyenne,
    ROUND(MIN(mpa.moyenne)::numeric, 2) AS pm25_min,
    ROUND(MAX(mpa.moyenne)::numeric, 2) AS pm25_max,
    ROUND(STDDEV(mpa.moyenne)::numeric, 2) AS pm25_ecart_type,
    SUM(CASE WHEN mpa.depasse_seuil_oms THEN 1 ELSE 0 END) AS nb_pays_depassement
FROM mesure_pays_annee mpa
JOIN pays p ON mpa.pays_id = p.id
JOIN region r ON p.region_id = r.id
JOIN polluant pol ON mpa.polluant_id = pol.id
WHERE pol.code = 'pm25'
AND mpa.annee = (SELECT MAX(annee) FROM mesure_pays_annee)
GROUP BY r.nom
ORDER BY pm25_moyenne DESC;

-- =============================================================================
-- SECTION 2: ANALYSE TEMPORELLE
-- =============================================================================

-- Q5: Évolution globale de la pollution PM2.5 (2018-2023)
SELECT
    mpa.annee,
    COUNT(DISTINCT mpa.pays_id) AS nb_pays,
    ROUND(AVG(mpa.moyenne)::numeric, 2) AS pm25_moyenne_mondiale,
    ROUND(MIN(mpa.moyenne)::numeric, 2) AS pm25_min,
    ROUND(MAX(mpa.moyenne)::numeric, 2) AS pm25_max,
    ROUND(AVG(CASE WHEN mpa.depasse_seuil_oms THEN 1 ELSE 0 END) * 100::numeric, 1) AS pct_depassement_oms
FROM mesure_pays_annee mpa
JOIN polluant pol ON mpa.polluant_id = pol.id
WHERE pol.code = 'pm25'
GROUP BY mpa.annee
ORDER BY mpa.annee;

-- Q6: Évolution par pays (tendances)
SELECT
    p.code_iso2,
    p.nom AS pays,
    COUNT(DISTINCT mpa.annee) AS nb_annees,
    ROUND(MIN(mpa.moyenne)::numeric, 2) AS pm25_min,
    ROUND(MAX(mpa.moyenne)::numeric, 2) AS pm25_max,
    ROUND(AVG(mpa.moyenne)::numeric, 2) AS pm25_moyenne,
    ROUND((
        (SELECT moyenne FROM mesure_pays_annee m2
         WHERE m2.pays_id = p.id AND m2.polluant_id = pol.id
         ORDER BY m2.annee DESC LIMIT 1) -
        (SELECT moyenne FROM mesure_pays_annee m3
         WHERE m3.pays_id = p.id AND m3.polluant_id = pol.id
         ORDER BY m3.annee ASC LIMIT 1)
    )::numeric, 2) AS variation_absolue,
    CASE
        WHEN (SELECT moyenne FROM mesure_pays_annee m2
              WHERE m2.pays_id = p.id AND m2.polluant_id = pol.id
              ORDER BY m2.annee DESC LIMIT 1) <
             (SELECT moyenne FROM mesure_pays_annee m3
              WHERE m3.pays_id = p.id AND m3.polluant_id = pol.id
              ORDER BY m3.annee ASC LIMIT 1) * 0.9
        THEN 'Amélioration'
        WHEN (SELECT moyenne FROM mesure_pays_annee m2
              WHERE m2.pays_id = p.id AND m2.polluant_id = pol.id
              ORDER BY m2.annee DESC LIMIT 1) >
             (SELECT moyenne FROM mesure_pays_annee m3
              WHERE m3.pays_id = p.id AND m3.polluant_id = pol.id
              ORDER BY m3.annee ASC LIMIT 1) * 1.1
        THEN 'Dégradation'
        ELSE 'Stable'
    END AS tendance
FROM mesure_pays_annee mpa
JOIN pays p ON mpa.pays_id = p.id
JOIN polluant pol ON mpa.polluant_id = pol.id
WHERE pol.code = 'pm25'
GROUP BY p.id, p.code_iso2, p.nom, pol.id
HAVING COUNT(DISTINCT mpa.annee) >= 3
ORDER BY variation_absolue ASC;

-- Q7: Impact COVID-19 (comparaison 2019 vs 2020)
SELECT
    p.code_iso2,
    p.nom AS pays,
    pol.code AS polluant,
    ROUND(m2019.moyenne::numeric, 2) AS moyenne_2019,
    ROUND(m2020.moyenne::numeric, 2) AS moyenne_2020,
    ROUND((m2020.moyenne - m2019.moyenne)::numeric, 2) AS variation_absolue,
    ROUND(((m2020.moyenne - m2019.moyenne) / m2019.moyenne * 100)::numeric, 1) AS variation_pct,
    CASE
        WHEN m2020.moyenne < m2019.moyenne * 0.95 THEN 'Amélioration'
        WHEN m2020.moyenne > m2019.moyenne * 1.05 THEN 'Dégradation'
        ELSE 'Stable'
    END AS impact_covid
FROM mesure_pays_annee m2019
JOIN mesure_pays_annee m2020
    ON m2019.pays_id = m2020.pays_id
    AND m2019.polluant_id = m2020.polluant_id
JOIN pays p ON m2019.pays_id = p.id
JOIN polluant pol ON m2019.polluant_id = pol.id
WHERE m2019.annee = 2019
AND m2020.annee = 2020
AND pol.code IN ('pm25', 'no2')
ORDER BY variation_pct ASC;

-- =============================================================================
-- SECTION 3: CORRÉLATIONS AVEC INDICATEURS SOCIO-ÉCONOMIQUES
-- =============================================================================

-- Q8: Relation PIB par habitant vs PM2.5
-- Objectif: Tester la courbe de Kuznets environnementale
WITH donnees_jointes AS (
    SELECT
        p.code_iso2,
        p.nom AS pays,
        mpa.moyenne AS pm25,
        ip.valeur AS pib_hab,
        mpa.annee
    FROM mesure_pays_annee mpa
    JOIN pays p ON mpa.pays_id = p.id
    JOIN polluant pol ON mpa.polluant_id = pol.id
    JOIN indicateur_pays ip ON ip.pays_id = p.id AND ip.annee = mpa.annee
    JOIN indicateur i ON ip.indicateur_id = i.id
    WHERE pol.code = 'pm25'
    AND i.code_wb = 'NY.GDP.PCAP.CD'
    AND mpa.moyenne IS NOT NULL
    AND ip.valeur IS NOT NULL
)
SELECT
    code_iso2,
    pays,
    annee,
    ROUND(pm25::numeric, 1) AS pm25,
    ROUND(pib_hab::numeric, 0) AS pib_habitant,
    CASE
        WHEN pib_hab < 4000 THEN 'Faible revenu'
        WHEN pib_hab < 12000 THEN 'Revenu intermédiaire'
        WHEN pib_hab < 40000 THEN 'Revenu élevé'
        ELSE 'Revenu très élevé'
    END AS categorie_revenu
FROM donnees_jointes
ORDER BY pib_hab;

-- Q9: Relation Urbanisation vs PM2.5
WITH donnees_jointes AS (
    SELECT
        p.code_iso2,
        p.nom AS pays,
        mpa.moyenne AS pm25,
        ip.valeur AS taux_urb
    FROM mesure_pays_annee mpa
    JOIN pays p ON mpa.pays_id = p.id
    JOIN polluant pol ON mpa.polluant_id = pol.id
    JOIN indicateur_pays ip ON ip.pays_id = p.id AND ip.annee = mpa.annee
    JOIN indicateur i ON ip.indicateur_id = i.id
    WHERE pol.code = 'pm25'
    AND i.code_wb = 'SP.URB.TOTL.IN.ZS'
    AND mpa.moyenne IS NOT NULL
    AND ip.valeur IS NOT NULL
    AND mpa.annee = (SELECT MAX(annee) FROM mesure_pays_annee)
)
SELECT
    code_iso2,
    pays,
    ROUND(taux_urb::numeric, 1) AS urbanisation_pct,
    ROUND(pm25::numeric, 1) AS pm25,
    CASE
        WHEN taux_urb < 50 THEN 'Peu urbanisé'
        WHEN taux_urb < 75 THEN 'Moyennement urbanisé'
        ELSE 'Très urbanisé'
    END AS niveau_urbanisation
FROM donnees_jointes
ORDER BY taux_urb DESC;

-- Q10: Relation Part industrie vs PM2.5
WITH donnees_jointes AS (
    SELECT
        p.code_iso2,
        p.nom AS pays,
        mpa.moyenne AS pm25,
        ip.valeur AS part_industrie
    FROM mesure_pays_annee mpa
    JOIN pays p ON mpa.pays_id = p.id
    JOIN polluant pol ON mpa.polluant_id = pol.id
    JOIN indicateur_pays ip ON ip.pays_id = p.id AND ip.annee = mpa.annee
    JOIN indicateur i ON ip.indicateur_id = i.id
    WHERE pol.code = 'pm25'
    AND i.code_wb = 'NV.IND.TOTL.ZS'
    AND mpa.moyenne IS NOT NULL
    AND ip.valeur IS NOT NULL
)
SELECT
    code_iso2,
    pays,
    ROUND(part_industrie::numeric, 1) AS industrie_pct_pib,
    ROUND(pm25::numeric, 1) AS pm25
FROM donnees_jointes
ORDER BY part_industrie DESC;

-- Q11: Relation Mix énergétique (fossile) vs PM2.5
WITH donnees_jointes AS (
    SELECT
        p.code_iso2,
        p.nom AS pays,
        mpa.moyenne AS pm25,
        ip.valeur AS elec_fossile
    FROM mesure_pays_annee mpa
    JOIN pays p ON mpa.pays_id = p.id
    JOIN polluant pol ON mpa.polluant_id = pol.id
    JOIN indicateur_pays ip ON ip.pays_id = p.id AND ip.annee = mpa.annee
    JOIN indicateur i ON ip.indicateur_id = i.id
    WHERE pol.code = 'pm25'
    AND i.code_wb = 'EG.ELC.FOSL.ZS'
    AND mpa.moyenne IS NOT NULL
    AND ip.valeur IS NOT NULL
)
SELECT
    code_iso2,
    pays,
    ROUND(elec_fossile::numeric, 1) AS electricite_fossile_pct,
    ROUND(pm25::numeric, 1) AS pm25,
    CASE
        WHEN elec_fossile < 30 THEN 'Mix propre'
        WHEN elec_fossile < 60 THEN 'Mix mixte'
        ELSE 'Mix fossile'
    END AS categorie_mix
FROM donnees_jointes
ORDER BY elec_fossile DESC;

-- Q12: Relation Espérance de vie vs PM2.5
WITH donnees_jointes AS (
    SELECT
        p.code_iso2,
        p.nom AS pays,
        mpa.moyenne AS pm25,
        ip.valeur AS esperance_vie
    FROM mesure_pays_annee mpa
    JOIN pays p ON mpa.pays_id = p.id
    JOIN polluant pol ON mpa.polluant_id = pol.id
    JOIN indicateur_pays ip ON ip.pays_id = p.id AND ip.annee = mpa.annee
    JOIN indicateur i ON ip.indicateur_id = i.id
    WHERE pol.code = 'pm25'
    AND i.code_wb = 'SP.DYN.LE00.IN'
    AND mpa.moyenne IS NOT NULL
    AND ip.valeur IS NOT NULL
)
SELECT
    code_iso2,
    pays,
    ROUND(esperance_vie::numeric, 1) AS esperance_vie_annees,
    ROUND(pm25::numeric, 1) AS pm25
FROM donnees_jointes
ORDER BY esperance_vie DESC;

-- =============================================================================
-- SECTION 4: ANALYSE DES DÉPASSEMENTS OMS
-- =============================================================================

-- Q13: Synthèse des dépassements par polluant
SELECT
    pol.code AS polluant,
    pol.nom AS nom_polluant,
    pol.seuil_oms_annuel AS seuil_oms,
    COUNT(*) AS nb_pays_mesures,
    SUM(CASE WHEN mpa.depasse_seuil_oms THEN 1 ELSE 0 END) AS nb_pays_depassement,
    ROUND(AVG(CASE WHEN mpa.depasse_seuil_oms THEN 1 ELSE 0 END) * 100::numeric, 1) AS pct_depassement,
    ROUND(AVG(mpa.moyenne)::numeric, 2) AS moyenne_globale,
    ROUND(AVG(CASE WHEN mpa.depasse_seuil_oms THEN mpa.moyenne END)::numeric, 2) AS moyenne_pays_depassement
FROM mesure_pays_annee mpa
JOIN polluant pol ON mpa.polluant_id = pol.id
WHERE pol.seuil_oms_annuel IS NOT NULL
AND mpa.annee = (SELECT MAX(annee) FROM mesure_pays_annee)
GROUP BY pol.code, pol.nom, pol.seuil_oms_annuel
ORDER BY pct_depassement DESC;

-- Q14: Pays en situation critique (dépassement >10x le seuil OMS)
SELECT
    p.code_iso2,
    p.nom AS pays,
    r.nom AS region,
    pol.code AS polluant,
    ROUND(mpa.moyenne::numeric, 1) AS valeur,
    pol.seuil_oms_annuel AS seuil_oms,
    ROUND((mpa.moyenne / pol.seuil_oms_annuel)::numeric, 1) AS facteur_depassement
FROM mesure_pays_annee mpa
JOIN pays p ON mpa.pays_id = p.id
LEFT JOIN region r ON p.region_id = r.id
JOIN polluant pol ON mpa.polluant_id = pol.id
WHERE pol.seuil_oms_annuel IS NOT NULL
AND mpa.moyenne > pol.seuil_oms_annuel * 10
AND mpa.annee = (SELECT MAX(annee) FROM mesure_pays_annee)
ORDER BY facteur_depassement DESC;

-- =============================================================================
-- SECTION 5: ANALYSES AVANCÉES
-- =============================================================================

-- Q15: Tableau de bord par pays (synthèse multi-indicateurs)
SELECT
    p.code_iso2,
    p.nom AS pays,
    r.nom AS region,
    p.population_urbaine_totale,
    -- Pollution PM2.5
    (SELECT ROUND(mpa.moyenne::numeric, 1)
     FROM mesure_pays_annee mpa
     JOIN polluant pol ON mpa.polluant_id = pol.id
     WHERE mpa.pays_id = p.id AND pol.code = 'pm25'
     ORDER BY mpa.annee DESC LIMIT 1) AS pm25_dernier,
    -- PIB par habitant
    (SELECT ROUND(ip.valeur::numeric, 0)
     FROM indicateur_pays ip
     JOIN indicateur i ON ip.indicateur_id = i.id
     WHERE ip.pays_id = p.id AND i.code_wb = 'NY.GDP.PCAP.CD'
     ORDER BY ip.annee DESC LIMIT 1) AS pib_habitant,
    -- Urbanisation
    (SELECT ROUND(ip.valeur::numeric, 1)
     FROM indicateur_pays ip
     JOIN indicateur i ON ip.indicateur_id = i.id
     WHERE ip.pays_id = p.id AND i.code_wb = 'SP.URB.TOTL.IN.ZS'
     ORDER BY ip.annee DESC LIMIT 1) AS urbanisation_pct,
    -- Espérance de vie
    (SELECT ROUND(ip.valeur::numeric, 1)
     FROM indicateur_pays ip
     JOIN indicateur i ON ip.indicateur_id = i.id
     WHERE ip.pays_id = p.id AND i.code_wb = 'SP.DYN.LE00.IN'
     ORDER BY ip.annee DESC LIMIT 1) AS esperance_vie
FROM pays p
LEFT JOIN region r ON p.region_id = r.id
WHERE EXISTS (SELECT 1 FROM mesure_pays_annee mpa WHERE mpa.pays_id = p.id)
ORDER BY p.nom;

-- Q16: Comparaison Europe vs Asie
SELECT
    r.nom AS region,
    COUNT(DISTINCT p.id) AS nb_pays,
    ROUND(AVG(mpa.moyenne)::numeric, 2) AS pm25_moyenne,
    ROUND(AVG(
        (SELECT ip.valeur FROM indicateur_pays ip
         JOIN indicateur i ON ip.indicateur_id = i.id
         WHERE ip.pays_id = p.id AND i.code_wb = 'NY.GDP.PCAP.CD'
         ORDER BY ip.annee DESC LIMIT 1)
    )::numeric, 0) AS pib_moyen,
    ROUND(AVG(
        (SELECT ip.valeur FROM indicateur_pays ip
         JOIN indicateur i ON ip.indicateur_id = i.id
         WHERE ip.pays_id = p.id AND i.code_wb = 'SP.URB.TOTL.IN.ZS'
         ORDER BY ip.annee DESC LIMIT 1)
    )::numeric, 1) AS urbanisation_moyenne,
    SUM(CASE WHEN mpa.depasse_seuil_oms THEN 1 ELSE 0 END) AS nb_pays_depassement_oms
FROM mesure_pays_annee mpa
JOIN pays p ON mpa.pays_id = p.id
JOIN region r ON p.region_id = r.id
JOIN polluant pol ON mpa.polluant_id = pol.id
WHERE pol.code = 'pm25'
AND r.code IN ('europe', 'asie')
AND mpa.annee = (SELECT MAX(annee) FROM mesure_pays_annee)
GROUP BY r.nom
ORDER BY pm25_moyenne;

-- Q17: Classement des pays selon un score composite
-- Score = moyenne pondérée (pollution=40%, PIB inversé=30%, urbanisation=30%)
WITH scores AS (
    SELECT
        p.code_iso2,
        p.nom AS pays,
        mpa.moyenne AS pm25,
        (SELECT ip.valeur FROM indicateur_pays ip
         JOIN indicateur i ON ip.indicateur_id = i.id
         WHERE ip.pays_id = p.id AND i.code_wb = 'NY.GDP.PCAP.CD'
         ORDER BY ip.annee DESC LIMIT 1) AS pib,
        (SELECT ip.valeur FROM indicateur_pays ip
         JOIN indicateur i ON ip.indicateur_id = i.id
         WHERE ip.pays_id = p.id AND i.code_wb = 'SP.URB.TOTL.IN.ZS'
         ORDER BY ip.annee DESC LIMIT 1) AS urb
    FROM mesure_pays_annee mpa
    JOIN pays p ON mpa.pays_id = p.id
    JOIN polluant pol ON mpa.polluant_id = pol.id
    WHERE pol.code = 'pm25'
    AND mpa.annee = (SELECT MAX(annee) FROM mesure_pays_annee)
)
SELECT
    code_iso2,
    pays,
    ROUND(pm25::numeric, 1) AS pm25,
    ROUND(pib::numeric, 0) AS pib_habitant,
    ROUND(urb::numeric, 1) AS urbanisation,
    ROUND((
        (1 - LEAST(pm25 / 100, 1)) * 0.4 +
        LEAST(pib / 80000, 1) * 0.3 +
        (urb / 100) * 0.3
    ) * 100::numeric, 1) AS score_developpement
FROM scores
WHERE pm25 IS NOT NULL AND pib IS NOT NULL AND urb IS NOT NULL
ORDER BY score_developpement DESC;

-- Q18: Données pour export CSV (analyse externe)
-- Génère un export plat pour analyses Python/R
SELECT
    p.code_iso2,
    p.code_iso3,
    p.nom AS pays,
    r.nom AS region,
    mpa.annee,
    pol.code AS polluant,
    mpa.moyenne AS pollution_moyenne,
    mpa.mediane AS pollution_mediane,
    mpa.depasse_seuil_oms,
    (SELECT ip.valeur FROM indicateur_pays ip
     JOIN indicateur i ON ip.indicateur_id = i.id
     WHERE ip.pays_id = p.id AND ip.annee = mpa.annee AND i.code_wb = 'NY.GDP.PCAP.CD') AS pib_habitant,
    (SELECT ip.valeur FROM indicateur_pays ip
     JOIN indicateur i ON ip.indicateur_id = i.id
     WHERE ip.pays_id = p.id AND ip.annee = mpa.annee AND i.code_wb = 'SP.URB.TOTL.IN.ZS') AS urbanisation,
    (SELECT ip.valeur FROM indicateur_pays ip
     JOIN indicateur i ON ip.indicateur_id = i.id
     WHERE ip.pays_id = p.id AND ip.annee = mpa.annee AND i.code_wb = 'NV.IND.TOTL.ZS') AS industrie_pct_pib,
    (SELECT ip.valeur FROM indicateur_pays ip
     JOIN indicateur i ON ip.indicateur_id = i.id
     WHERE ip.pays_id = p.id AND ip.annee = mpa.annee AND i.code_wb = 'SP.DYN.LE00.IN') AS esperance_vie
FROM mesure_pays_annee mpa
JOIN pays p ON mpa.pays_id = p.id
LEFT JOIN region r ON p.region_id = r.id
JOIN polluant pol ON mpa.polluant_id = pol.id
WHERE pol.code = 'pm25'
ORDER BY p.nom, mpa.annee;

-- =============================================================================
-- SECTION 6: REQUÊTES DE VALIDATION
-- =============================================================================

-- Q19: Vérification de la cohérence des données
SELECT
    'Pays' AS entite,
    COUNT(*) AS nb_enregistrements,
    COUNT(DISTINCT code_iso2) AS nb_uniques
FROM pays
UNION ALL
SELECT
    'Mesures pollution',
    COUNT(*),
    COUNT(DISTINCT CONCAT(pays_id, '-', polluant_id, '-', annee))
FROM mesure_pays_annee
UNION ALL
SELECT
    'Indicateurs pays',
    COUNT(*),
    COUNT(DISTINCT CONCAT(pays_id, '-', indicateur_id, '-', annee))
FROM indicateur_pays;

-- Q20: Couverture des données par pays
SELECT
    p.code_iso2,
    p.nom AS pays,
    COUNT(DISTINCT mpa.annee) AS nb_annees_pollution,
    COUNT(DISTINCT ip.indicateur_id) AS nb_indicateurs,
    STRING_AGG(DISTINCT pol.code, ', ' ORDER BY pol.code) AS polluants_disponibles
FROM pays p
LEFT JOIN mesure_pays_annee mpa ON p.id = mpa.pays_id
LEFT JOIN polluant pol ON mpa.polluant_id = pol.id
LEFT JOIN indicateur_pays ip ON p.id = ip.pays_id
GROUP BY p.code_iso2, p.nom
HAVING COUNT(DISTINCT mpa.annee) > 0
ORDER BY nb_annees_pollution DESC, nb_indicateurs DESC;

-- =============================================================================
-- FIN DES REQUÊTES D'ANALYSE
-- =============================================================================
