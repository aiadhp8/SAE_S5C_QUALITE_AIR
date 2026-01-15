import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, forkJoin, map, tap } from 'rxjs';
import {
  Country,
  PollutionData,
  Correlation,
  TemporalGlobal,
  CovidImpact,
  ModelComparison,
  FeatureImportance,
  Completude,
  GlobalStats,
  AcpData,
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
      temporal: this.http.get<TemporalGlobal[]>(`${this.basePath}/temporal_global.json`)
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
        this.loaded = true;
      }),
      map(() => true)
    );
  }

  // Méthodes utilitaires
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
}
