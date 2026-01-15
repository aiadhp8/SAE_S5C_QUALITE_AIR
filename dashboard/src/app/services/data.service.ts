import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, forkJoin, map, tap, catchError, of } from 'rxjs';
import {
  Country,
  PollutionData,
  Correlation,
  PollutantCorrelation,
  TemporalGlobal,
  CovidImpact,
  ModelComparison,
  FeatureImportance,
  Completude,
  GlobalStats,
  AcpData,
  Chi2Result,
  Pollutant
} from '../models/types';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private http = inject(HttpClient);
  private basePath = 'assets/data';

  // Cache des données
  private countriesSubject = new BehaviorSubject<Country[]>([]);
  private pollutionSubject = new BehaviorSubject<PollutionData[]>([]);
  private correlationsSubject = new BehaviorSubject<Correlation[]>([]);
  private statsSubject = new BehaviorSubject<GlobalStats | null>(null);
  private covidSubject = new BehaviorSubject<CovidImpact[]>([]);
  private modelsSubject = new BehaviorSubject<ModelComparison[]>([]);
  private featuresSubject = new BehaviorSubject<FeatureImportance[]>([]);
  private completudeSubject = new BehaviorSubject<Completude[]>([]);
  private acpSubject = new BehaviorSubject<AcpData | null>(null);
  private temporalSubject = new BehaviorSubject<TemporalGlobal[]>([]);
  private chi2Subject = new BehaviorSubject<Chi2Result[]>([]);

  // Observables publics
  countries$ = this.countriesSubject.asObservable();
  pollution$ = this.pollutionSubject.asObservable();
  correlations$ = this.correlationsSubject.asObservable();
  stats$ = this.statsSubject.asObservable();
  covid$ = this.covidSubject.asObservable();
  models$ = this.modelsSubject.asObservable();
  features$ = this.featuresSubject.asObservable();
  completude$ = this.completudeSubject.asObservable();
  acp$ = this.acpSubject.asObservable();
  temporal$ = this.temporalSubject.asObservable();
  chi2$ = this.chi2Subject.asObservable();

  private loaded = false;

  loadAllData(): Observable<boolean> {
    if (this.loaded) {
      return new BehaviorSubject(true).asObservable();
    }

    return forkJoin({
      countries: this.http.get<Country[]>(`${this.basePath}/countries.json`),
      pollution: this.http.get<PollutionData[]>(`${this.basePath}/pollution.json`),
      correlations: this.http.get<Correlation[]>(`${this.basePath}/correlations.json`),
      stats: this.http.get<GlobalStats>(`${this.basePath}/stats.json`),
      covid: this.http.get<CovidImpact[]>(`${this.basePath}/covid_impact.json`),
      models: this.http.get<ModelComparison[]>(`${this.basePath}/models.json`),
      features: this.http.get<FeatureImportance[]>(`${this.basePath}/features.json`),
      completude: this.http.get<Completude[]>(`${this.basePath}/completude.json`),
      acp: this.http.get<AcpData>(`${this.basePath}/acp.json`),
      temporal: this.http.get<TemporalGlobal[]>(`${this.basePath}/temporal_global.json`),
      chi2: this.http.get<Chi2Result[]>(`${this.basePath}/chi2.json`).pipe(
        catchError(() => of([]))
      )
    }).pipe(
      tap(data => {
        this.countriesSubject.next(data.countries);
        this.pollutionSubject.next(data.pollution);
        this.correlationsSubject.next(data.correlations);
        this.statsSubject.next(data.stats);
        this.covidSubject.next(data.covid);
        this.modelsSubject.next(data.models);
        this.featuresSubject.next(data.features);
        this.completudeSubject.next(data.completude);
        this.acpSubject.next(data.acp);
        this.temporalSubject.next(data.temporal);
        this.chi2Subject.next(data.chi2);
        this.loaded = true;
      }),
      map(() => true)
    );
  }

  // Méthodes utilitaires

  /**
   * Get pollution value for a country using pollution.json data
   * Supports median/average stat and year filtering
   */
  getCountryPollutionByStat(
    countryCode: string,
    pollutant: Pollutant,
    stat: 'median' | 'average' = 'median',
    year: number | 'all' = 'all'
  ): number | null {
    const pollutionData = this.pollutionSubject.value.find(p => p.country_code === countryCode);
    if (!pollutionData) return null;

    const years = Object.keys(pollutionData.years).map(Number);
    if (years.length === 0) return null;

    if (year !== 'all') {
      // Single year
      const yearData = pollutionData.years[year];
      if (!yearData || !yearData[pollutant]) return null;
      return yearData[pollutant][stat];
    }

    // Aggregate across all years
    const values: number[] = [];
    for (const y of years) {
      const yearData = pollutionData.years[y];
      if (yearData && yearData[pollutant] && yearData[pollutant][stat] !== null) {
        values.push(yearData[pollutant][stat]!);
      }
    }

    if (values.length === 0) return null;

    // Return mean of the stat across years
    return values.reduce((a, b) => a + b, 0) / values.length;
  }

  /**
   * Get all countries with their pollution values for a given pollutant and stat
   */
  getCountriesWithPollution(
    pollutant: Pollutant,
    stat: 'median' | 'average' = 'median',
    year: number | 'all' = 'all'
  ): { country: Country; value: number }[] {
    const countries = this.countriesSubject.value;
    const result: { country: Country; value: number }[] = [];

    for (const country of countries) {
      const value = this.getCountryPollutionByStat(country.code_pays, pollutant, stat, year);
      if (value !== null) {
        result.push({ country, value });
      }
    }

    return result;
  }

  /**
   * Get top countries sorted by pollution value
   */
  getTopCountriesByStat(
    pollutant: Pollutant,
    stat: 'median' | 'average' = 'median',
    year: number | 'all' = 'all',
    count: number = 10,
    ascending: boolean = false
  ): { country: Country; value: number }[] {
    const countriesWithPollution = this.getCountriesWithPollution(pollutant, stat, year);

    countriesWithPollution.sort((a, b) => {
      return ascending ? a.value - b.value : b.value - a.value;
    });

    return countriesWithPollution.slice(0, count);
  }

  /**
   * Calculate global statistic (median or average) for a pollutant
   */
  getGlobalPollutionStat(
    pollutant: Pollutant,
    stat: 'median' | 'average' = 'median',
    year: number | 'all' = 'all'
  ): number | null {
    const countriesWithPollution = this.getCountriesWithPollution(pollutant, stat, year);
    if (countriesWithPollution.length === 0) return null;

    const values = countriesWithPollution.map(c => c.value);

    if (stat === 'median') {
      // Calculate median of all country values
      values.sort((a, b) => a - b);
      const mid = Math.floor(values.length / 2);
      return values.length % 2 !== 0
        ? values[mid]
        : (values[mid - 1] + values[mid]) / 2;
    } else {
      // Calculate average
      return values.reduce((a, b) => a + b, 0) / values.length;
    }
  }

  getCountryPollution(countryCode: string, pollutant: Pollutant, stat: 'median' | 'average' = 'median'): number | null {
    const country = this.countriesSubject.value.find(c => c.code_pays === countryCode);
    if (!country) return null;

    const key = `pollution_${pollutant}` as keyof Country;
    return country[key] as number | null;
  }

  getTopCountries(pollutant: Pollutant, count: number = 10, ascending: boolean = false): Country[] {
    const countries = this.countriesSubject.value
      .filter(c => {
        const key = `pollution_${pollutant}` as keyof Country;
        return c[key] !== null;
      })
      .sort((a, b) => {
        const key = `pollution_${pollutant}` as keyof Country;
        const valA = a[key] as number;
        const valB = b[key] as number;
        return ascending ? valA - valB : valB - valA;
      });

    return countries.slice(0, count);
  }

  getCorrelationsForPollutant(pollutant: string, significantOnly: boolean = false): Correlation[] {
    let correlations = this.correlationsSubject.value.filter(c => c.pollutant === pollutant);
    if (significantOnly) {
      correlations = correlations.filter(c => c.significant);
    }
    return correlations.sort((a, b) => Math.abs(b.correlation || 0) - Math.abs(a.correlation || 0));
  }

  getCovidImpactByPollutant(pollutant: string): CovidImpact[] {
    return this.covidSubject.value
      .filter(c => c.parameter === pollutant && c.variation_pct !== null)
      .sort((a, b) => (a.variation_pct || 0) - (b.variation_pct || 0));
  }

  getMedianPollution(pollutant: Pollutant): number | null {
    const stats = this.statsSubject.value;
    return stats?.median_values[pollutant] ?? null;
  }

  getAboveWhoPercentage(pollutant: Pollutant): number | null {
    const stats = this.statsSubject.value;
    return stats?.above_who_pct[pollutant] ?? null;
  }

  getWhoLimit(pollutant: Pollutant): number {
    const stats = this.statsSubject.value;
    return stats?.who_limits[pollutant] ?? 0;
  }

  getBestModel(): ModelComparison | null {
    const models = this.modelsSubject.value;
    if (models.length === 0) return null;
    // Random Forest est généralement le meilleur
    return models.find(m => m.model === 'Random Forest') || models[0];
  }

  getTopFeatures(count: number = 10): FeatureImportance[] {
    return this.featuresSubject.value.slice(0, count);
  }

  /**
   * Calculate Spearman correlation between pollutants
   * Returns a matrix of correlations between all pollutant pairs
   */
  getPollutantCorrelations(): PollutantCorrelation[] {
    const pollutants: Pollutant[] = ['pm25', 'pm10', 'no2', 'o3', 'so2', 'co'];
    const countries = this.countriesSubject.value;
    const correlations: PollutantCorrelation[] = [];

    for (const pollutant1 of pollutants) {
      for (const pollutant2 of pollutants) {
        const key1 = `pollution_${pollutant1}` as keyof Country;
        const key2 = `pollution_${pollutant2}` as keyof Country;

        // Get paired values (only where both pollutants have data)
        const pairs = countries
          .filter(c => c[key1] !== null && c[key2] !== null)
          .map(c => ({
            x: c[key1] as number,
            y: c[key2] as number
          }));

        if (pairs.length < 10) {
          correlations.push({
            pollutant1,
            pollutant2,
            correlation: null,
            n_observations: pairs.length,
            significant: false
          });
          continue;
        }

        // Calculate Spearman correlation (rank-based)
        const correlation = this.calculateSpearmanCorrelation(
          pairs.map(p => p.x),
          pairs.map(p => p.y)
        );

        // Approximate significance test (p < 0.05 for n > 10)
        const t = correlation * Math.sqrt((pairs.length - 2) / (1 - correlation * correlation));
        const significant = Math.abs(t) > 1.96;

        correlations.push({
          pollutant1,
          pollutant2,
          correlation,
          n_observations: pairs.length,
          significant
        });
      }
    }

    return correlations;
  }

  private calculateSpearmanCorrelation(x: number[], y: number[]): number {
    const n = x.length;
    if (n === 0) return 0;

    // Rank the values
    const rankX = this.rankArray(x);
    const rankY = this.rankArray(y);

    // Calculate Spearman correlation using ranked values
    const meanX = rankX.reduce((a, b) => a + b, 0) / n;
    const meanY = rankY.reduce((a, b) => a + b, 0) / n;

    let numerator = 0;
    let denomX = 0;
    let denomY = 0;

    for (let i = 0; i < n; i++) {
      const dx = rankX[i] - meanX;
      const dy = rankY[i] - meanY;
      numerator += dx * dy;
      denomX += dx * dx;
      denomY += dy * dy;
    }

    const denominator = Math.sqrt(denomX * denomY);
    if (denominator === 0) return 0;

    return numerator / denominator;
  }

  private rankArray(arr: number[]): number[] {
    const sorted = arr.map((val, idx) => ({ val, idx }))
      .sort((a, b) => a.val - b.val);

    const ranks = new Array(arr.length);
    let i = 0;

    while (i < sorted.length) {
      let j = i;
      // Find all elements with the same value (ties)
      while (j < sorted.length && sorted[j].val === sorted[i].val) {
        j++;
      }
      // Average rank for ties
      const avgRank = (i + j + 1) / 2;
      for (let k = i; k < j; k++) {
        ranks[sorted[k].idx] = avgRank;
      }
      i = j;
    }

    return ranks;
  }
}
