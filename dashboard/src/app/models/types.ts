// Types pour le dashboard de qualité de l'air

export type Pollutant = 'pm25' | 'pm10' | 'no2' | 'o3' | 'so2' | 'co';

export interface PollutantInfo {
  code: Pollutant;
  label: string;
  unit: string;
  whoLimit: number;
}

export const POLLUTANTS: PollutantInfo[] = [
  { code: 'pm25', label: 'PM2.5', unit: 'µg/m³', whoLimit: 5 },
  { code: 'pm10', label: 'PM10', unit: 'µg/m³', whoLimit: 15 },
  { code: 'no2', label: 'NO₂', unit: 'µg/m³', whoLimit: 10 },
  { code: 'o3', label: 'O₃', unit: 'µg/m³', whoLimit: 100 },
  { code: 'so2', label: 'SO₂', unit: 'µg/m³', whoLimit: 40 },
  { code: 'co', label: 'CO', unit: 'µg/m³', whoLimit: 4000 }
];

export interface Country {
  code_pays: string;
  nom_pays: string;
  code_pays_iso3: string;
  nb_villes: number;
  population_urbaine_totale: number | null;
  population_ville_max: number | null;
  population_ville_moyenne: number | null;
  latitude_moyenne: number | null;
  longitude_moyenne: number | null;
  pollution_co: number | null;
  pollution_no2: number | null;
  pollution_o3: number | null;
  pollution_pm10: number | null;
  pollution_pm25: number | null;
  pollution_so2: number | null;
  nb_polluants_disponibles: number;
  donnees_completes: boolean;
  score_qualite: number | null;
  // Transport
  transport_IS_AIR_DPRT: number | null;
  transport_IS_AIR_PSGR: number | null;
  transport_IS_RRS_TOTL_KM: number | null;
  // Énergie
  energie_EG_ELC_COAL_ZS: number | null;
  energie_EG_ELC_FOSL_ZS: number | null;
  energie_EG_ELC_NGAS_ZS: number | null;
  energie_EG_ELC_NUCL_ZS: number | null;
  energie_EG_ELC_PETR_ZS: number | null;
  energie_EG_ELC_RNWX_ZS: number | null;
  energie_EG_FEC_RNEW_ZS: number | null;
  energie_EG_USE_ELEC_KH_PC: number | null;
  energie_EG_USE_PCAP_KG_OE: number | null;
  // Économie
  eco_NV_AGR_TOTL_ZS: number | null;
  eco_NV_IND_MANF_ZS: number | null;
  eco_NV_IND_TOTL_ZS: number | null;
  eco_NV_SRV_TOTL_ZS: number | null;
  eco_NY_GDP_PCAP_CD: number | null;
  eco_NY_GDP_PCAP_PP_CD: number | null;
  eco_SL_AGR_EMPL_ZS: number | null;
  eco_SL_IND_EMPL_ZS: number | null;
  eco_SL_SRV_EMPL_ZS: number | null;
  // Démographie
  demo_AG_LND_FRST_ZS: number | null;
  demo_AG_LND_TOTL_K2: number | null;
  demo_AG_SRF_TOTL_K2: number | null;
  demo_EN_POP_DNST: number | null;
  demo_EN_URB_LCTY: number | null;
  demo_EN_URB_LCTY_UR_ZS: number | null;
  demo_SP_POP_TOTL: number | null;
  demo_SP_URB_GROW: number | null;
  demo_SP_URB_TOTL: number | null;
  demo_SP_URB_TOTL_IN_ZS: number | null;
  // Santé
  sante_EN_ATM_PM25_MC_M3: number | null;
  sante_SH_STA_AIRP_P5: number | null;
  sante_SH_XPD_CHEX_GD_ZS: number | null;
  sante_SH_XPD_CHEX_PC_CD: number | null;
  sante_SP_DYN_LE00_IN: number | null;
}

export interface PollutionMeasurement {
  average: number | null;
  median: number | null;
  min: number | null;
  max: number | null;
  std: number | null;
  measurement_count: number | null;
  unit: string;
}

export interface PollutionByYear {
  [pollutant: string]: PollutionMeasurement;
}

export interface PollutionData {
  country_code: string;
  country_name: string;
  years: { [year: number]: PollutionByYear };
}

export interface Correlation {
  pollutant: string;
  indicator: string;
  axis: string;
  correlation: number | null;
  p_value: number | null;
  significant: boolean;
  very_significant: boolean;
  n_observations: number | null;
  strength: string;
}

export interface PollutantCorrelation {
  pollutant1: Pollutant;
  pollutant2: Pollutant;
  correlation: number | null;
  n_observations: number;
  significant: boolean;
}

export interface TemporalGlobal {
  polluant: string;
  pente_annuelle: number;
  variation_pct: number;
  r2: number;
  p_value: number;
  tendance: string;
  significatif: string;
}

export interface CovidImpact {
  country_code: string;
  country_name: string;
  parameter: string;
  val_2019: number | null;
  val_2020: number | null;
  variation_pct: number | null;
}

export interface ModelComparison {
  model: string;
  r2_train: number;
  r2_test: number;
  rmse: number;
  mae: number;
  cv_mean: number;
  cv_std: number;
}

export interface FeatureImportance {
  variable: string;
  importance: number;
}

export interface Completude {
  axe: string;
  nb_indicateurs: number;
  pays_complets: number;
  pays_partiels: number;
  pct_complets: number;
  pct_partiels: number;
}

export interface GlobalStats {
  total_countries: number;
  total_measurements: number;
  period: { start: number; end: number };
  pollutants: Pollutant[];
  pollutant_labels: { [key: string]: string };
  who_limits: { [key: string]: number };
  units: { [key: string]: string };
  median_values: { [key: string]: number };
  above_who_pct: { [key: string]: number };
}

export interface AcpData {
  loadings: { [key: string]: number }[];
  variables: string[];
}

// Filtres
export interface FilterState {
  pollutant: Pollutant;
  year: number | 'all';
  stat: 'median' | 'average';
}
