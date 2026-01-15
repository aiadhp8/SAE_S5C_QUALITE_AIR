import { Component, inject, OnInit, OnDestroy, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, combineLatest, takeUntil } from 'rxjs';
import * as L from 'leaflet';

import { DataService } from '../../../services/data.service';
import { FilterService } from '../../../services/filter.service';
import { KpiCardComponent } from '../../kpi-card/kpi-card.component';
import { BarChartComponent, BarChartData } from '../../charts/bar-chart/bar-chart.component';
import { Country, POLLUTANTS, Pollutant } from '../../../models/types';

@Component({
  selector: 'app-accueil',
  standalone: true,
  imports: [CommonModule, KpiCardComponent, BarChartComponent],
  template: `
    <section class="section accueil" id="accueil">
      <h2 class="section-title">
        <span class="title-icon">📊</span>
        Air Quality Snapshot
      </h2>
      <p class="section-subtitle">Vue d'ensemble de la qualité de l'air mondiale</p>

      <!-- KPIs -->
      <div class="kpi-grid">
        <app-kpi-card
          label="Pays analysés"
          [value]="totalCountries"
          icon="public"
          subtitle="Après nettoyage des données"
          tooltip="Nombre de pays avec des données de pollution disponibles">
        </app-kpi-card>

        <app-kpi-card
          label="Polluant sélectionné"
          [value]="selectedPollutantLabel"
          icon="science"
          [subtitle]="'Seuil OMS: ' + whoLimit + ' ' + unit">
        </app-kpi-card>

        <app-kpi-card
          [label]="statLabel + ' mondiale'"
          [value]="globalStatValue"
          [unit]="unit"
          icon="analytics"
          [highlight]="globalStatValue !== null && globalStatValue <= whoLimit"
          [warning]="globalStatValue !== null && globalStatValue > whoLimit"
          [tooltip]="'Valeur ' + statLabel.toLowerCase() + ' du polluant sélectionné pour tous les pays'">
        </app-kpi-card>

        <app-kpi-card
          label="Au-dessus seuil OMS"
          [value]="aboveWhoPercent"
          unit="%"
          icon="warning"
          [warning]="aboveWhoPercent !== null && aboveWhoPercent > 50"
          tooltip="Pourcentage de pays dépassant les recommandations OMS">
        </app-kpi-card>
      </div>

      <!-- Map and Rankings -->
      <div class="map-ranking-container">
        <div class="map-container">
          <h3 class="chart-title">Carte mondiale - {{ selectedPollutantLabel }}</h3>
          <div #mapContainer class="leaflet-map"></div>
          <div class="map-legend">
            <span class="legend-item"><span class="color-box good"></span> Bon (&lt; seuil OMS)</span>
            <span class="legend-item"><span class="color-box moderate"></span> Modéré (1-2x seuil)</span>
            <span class="legend-item"><span class="color-box unhealthy"></span> Mauvais (2-3x seuil)</span>
            <span class="legend-item"><span class="color-box bad"></span> Très mauvais (&gt; 3x seuil)</span>
          </div>
        </div>

        <div class="rankings">
          <div class="ranking-chart">
            <h3 class="chart-title">Top 10 - Plus pollués</h3>
            <app-bar-chart
              [data]="topPolluted"
              [unit]="unit"
              [horizontal]="true">
            </app-bar-chart>
          </div>

          <div class="ranking-chart">
            <h3 class="chart-title">Top 10 - Moins pollués</h3>
            <app-bar-chart
              [data]="leastPolluted"
              [unit]="unit"
              [horizontal]="true">
            </app-bar-chart>
          </div>
        </div>
      </div>
    </section>
  `,
  styles: [`
    .section {
      padding: 24px;
      margin-bottom: 24px;
    }

    .section-title {
      font-size: 1.8rem;
      font-weight: 700;
      color: #1a1a1a;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .title-icon {
      font-size: 1.5rem;
    }

    .section-subtitle {
      color: #666;
      font-size: 1rem;
      margin-bottom: 24px;
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 20px;
      margin-bottom: 20px;
    }

    .map-ranking-container {
      display: grid;
      grid-template-columns: 1.5fr 1fr;
      gap: 24px;
    }

    .map-container {
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .leaflet-map {
      height: 300px;
      border-radius: 8px;
      overflow: hidden;
    }

    .map-legend {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      margin-top: 12px;
      justify-content: center;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.8rem;
      color: #666;
    }

    .color-box {
      width: 16px;
      height: 16px;
      border-radius: 4px;
    }

    .color-box.good { background: #4caf50; }
    .color-box.moderate { background: #ffeb3b; }
    .color-box.unhealthy { background: #ff9800; }
    .color-box.bad { background: #f44336; }

    .rankings {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .ranking-chart {
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      flex: 1;
    }

    .chart-title {
      font-size: 1rem;
      font-weight: 600;
      color: #333;
      margin-bottom: 16px;
    }

    @media (max-width: 1024px) {
      .map-ranking-container {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class AccueilComponent implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('mapContainer') mapContainer!: ElementRef;

  private dataService = inject(DataService);
  private filterService = inject(FilterService);
  private destroy$ = new Subject<void>();
  private map: L.Map | null = null;
  private markersLayer: L.LayerGroup | null = null;

  totalCountries = 0;
  selectedPollutantLabel = 'PM2.5';
  globalStatValue: number | null = null;
  aboveWhoPercent: number | null = null;
  whoLimit = 5;
  unit = 'µg/m³';
  statLabel = 'Médiane';

  topPolluted: BarChartData[] = [];
  leastPolluted: BarChartData[] = [];

  private countries: Country[] = [];
  private currentStat: 'median' | 'average' = 'median';
  private currentYear: number | 'all' = 'all';

  ngOnInit(): void {
    combineLatest([
      this.dataService.countries$,
      this.dataService.stats$,
      this.filterService.filters$
    ]).pipe(takeUntil(this.destroy$))
      .subscribe(([countries, stats, filters]) => {
        this.countries = countries;
        this.totalCountries = countries.length;
        this.currentStat = filters.stat;
        this.currentYear = filters.year;
        this.statLabel = filters.stat === 'median' ? 'Médiane' : 'Moyenne';

        const pollutantInfo = POLLUTANTS.find(p => p.code === filters.pollutant);
        this.selectedPollutantLabel = pollutantInfo?.label || 'PM2.5';
        this.unit = pollutantInfo?.unit || 'µg/m³';
        this.whoLimit = pollutantInfo?.whoLimit || 5;

        // Calculate global stat using the selected statistic type
        this.globalStatValue = this.dataService.getGlobalPollutionStat(
          filters.pollutant,
          filters.stat,
          filters.year
        );

        if (stats) {
          this.aboveWhoPercent = stats.above_who_pct[filters.pollutant] ?? null;
        }

        this.updateRankings(filters.pollutant, filters.stat, filters.year);
        this.updateMap(filters.pollutant, filters.stat, filters.year);
      });
  }

  ngAfterViewInit(): void {
    this.initMap();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    if (this.map) {
      this.map.remove();
    }
  }

  private initMap(): void {
    if (!this.mapContainer?.nativeElement) return;

    this.map = L.map(this.mapContainer.nativeElement, {
      center: [20, 0],
      zoom: 2,
      minZoom: 1,
      maxZoom: 6,
      zoomControl: true
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(this.map);

    this.markersLayer = L.layerGroup().addTo(this.map);
  }

  private updateMap(pollutant: Pollutant, stat: 'median' | 'average', year: number | 'all'): void {
    if (!this.map || !this.markersLayer) return;

    this.markersLayer.clearLayers();

    this.countries.forEach(country => {
      const value = this.dataService.getCountryPollutionByStat(country.code_pays, pollutant, stat, year);
      if (value === null || !country.latitude_moyenne || !country.longitude_moyenne) return;

      const color = this.getColorForValue(value, this.whoLimit);
      const radius = Math.min(Math.max(value / 2, 5), 25);

      const marker = L.circleMarker([country.latitude_moyenne, country.longitude_moyenne], {
        radius: radius,
        fillColor: color,
        color: '#fff',
        weight: 1,
        opacity: 1,
        fillOpacity: 0.7
      });

      marker.bindTooltip(`
        <strong>${country.nom_pays}</strong><br>
        ${this.selectedPollutantLabel} (${this.statLabel.toLowerCase()}): ${value.toFixed(1)} ${this.unit}
      `, { permanent: false });

      this.markersLayer!.addLayer(marker);
    });
  }

  private updateRankings(pollutant: Pollutant, stat: 'median' | 'average', year: number | 'all'): void {
    const topCountries = this.dataService.getTopCountriesByStat(pollutant, stat, year, 10, false);
    const bottomCountries = this.dataService.getTopCountriesByStat(pollutant, stat, year, 10, true);

    this.topPolluted = topCountries.map(c => ({
      label: c.country.nom_pays,
      value: c.value,
      color: this.getColorForValue(c.value, this.whoLimit)
    }));

    this.leastPolluted = bottomCountries.map(c => ({
      label: c.country.nom_pays,
      value: c.value,
      color: this.getColorForValue(c.value, this.whoLimit)
    }));
  }

  private getColorForValue(value: number, limit: number): string {
    const ratio = value / limit;
    if (ratio < 1) return '#4caf50';      // Vert
    if (ratio < 2) return '#ffeb3b';      // Jaune
    if (ratio < 3) return '#ff9800';      // Orange
    return '#f44336';                      // Rouge
  }
}
