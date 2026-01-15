import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, combineLatest, takeUntil } from 'rxjs';

import { DataService } from '../../../services/data.service';
import { FilterService } from '../../../services/filter.service';
import { KpiCardComponent } from '../../kpi-card/kpi-card.component';
import { BarChartComponent, BarChartData } from '../../charts/bar-chart/bar-chart.component';
import { LineChartComponent, LineChartSeries } from '../../charts/line-chart/line-chart.component';
import { CovidImpact, TemporalGlobal, POLLUTANTS } from '../../../models/types';

@Component({
  selector: 'app-tendances',
  standalone: true,
  imports: [CommonModule, KpiCardComponent, BarChartComponent, LineChartComponent],
  template: `
    <section class="section tendances" id="tendances">
      <h2 class="section-title">
        <span class="title-icon">📈</span>
        Tendances Temporelles
      </h2>
      <p class="section-subtitle">Évolution de la pollution et impact du COVID-19</p>

      <!-- KPIs -->
      <div class="kpi-grid">
        <app-kpi-card
          label="Variation COVID (2019→2020)"
          [value]="covidVariation"
          unit="%"
          icon="coronavirus"
          [trend]="covidVariation"
          [highlight]="covidVariation !== null && covidVariation < 0"
          [warning]="covidVariation !== null && covidVariation > 0"
          tooltip="Variation médiane du polluant entre 2019 et 2020">
        </app-kpi-card>

        <app-kpi-card
          label="Plus forte baisse COVID"
          [value]="biggestDrop?.country_name || '-'"
          icon="trending_down"
          [subtitle]="biggestDrop ? biggestDrop.variation_pct?.toFixed(1) + '%' : ''"
          [highlight]="true">
        </app-kpi-card>

        <app-kpi-card
          label="Plus forte hausse COVID"
          [value]="biggestRise?.country_name || '-'"
          icon="trending_up"
          [subtitle]="biggestRise ? '+' + biggestRise.variation_pct?.toFixed(1) + '%' : ''"
          [warning]="true">
        </app-kpi-card>

        <app-kpi-card
          label="Tendance globale"
          [value]="globalTrend"
          icon="show_chart"
          [subtitle]="trendPvalue"
          tooltip="Tendance annuelle moyenne du polluant">
        </app-kpi-card>
      </div>

      <!-- Charts -->
      <div class="charts-container">
        <div class="chart-card large">
          <h3 class="chart-title">Impact COVID-19 par pays ({{ selectedPollutantLabel }})</h3>
          <div class="covid-chart-container">
            <app-bar-chart
              [data]="covidImpactData"
              unit="%"
              [horizontal]="true">
            </app-bar-chart>
          </div>
          <p class="chart-note">Variation des concentrations entre 2019 et 2020</p>
        </div>

        <div class="chart-card">
          <h3 class="chart-title">Tendance globale par polluant</h3>
          <div class="trends-grid">
            @for (trend of allTrends; track trend.polluant) {
              <div class="trend-item" [class.positive]="trend.variation_pct < 0" [class.negative]="trend.variation_pct > 0">
                <span class="trend-pollutant">{{ getPollutantLabel(trend.polluant) }}</span>
                <span class="trend-value">{{ trend.variation_pct > 0 ? '+' : '' }}{{ trend.variation_pct.toFixed(1) }}%/an</span>
                <span class="trend-arrow">{{ trend.variation_pct < 0 ? '↓' : trend.variation_pct > 0 ? '↑' : '→' }}</span>
              </div>
            }
          </div>
        </div>
      </div>

      <!-- Top/Bottom COVID impact -->
      <div class="impact-lists">
        <div class="impact-list">
          <h4>🟢 Pays avec la plus forte baisse</h4>
          <div class="impact-items">
            @for (item of topDrops; track item.country_code) {
              <div class="impact-item positive">
                <span class="country">{{ item.country_name }}</span>
                <span class="value">{{ item.variation_pct?.toFixed(1) }}%</span>
              </div>
            }
          </div>
        </div>

        <div class="impact-list">
          <h4>🔴 Pays avec la plus forte hausse</h4>
          <div class="impact-items">
            @for (item of topRises; track item.country_code) {
              <div class="impact-item negative">
                <span class="country">{{ item.country_name }}</span>
                <span class="value">+{{ item.variation_pct?.toFixed(1) }}%</span>
              </div>
            }
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

    .charts-container {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 24px;
      margin-bottom: 20px;
    }

    .chart-card {
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .chart-card.large {
      min-height: 300px;
    }

    .chart-title {
      font-size: 1rem;
      font-weight: 600;
      color: #333;
      margin-bottom: 16px;
    }

    .chart-note {
      font-size: 0.8rem;
      color: #888;
      text-align: center;
      margin-top: 12px;
    }

    .covid-chart-container {
      height: 250px;
    }

    .trends-grid {
      display: grid;
      gap: 12px;
    }

    .trend-item {
      display: flex;
      align-items: center;
      padding: 12px 16px;
      border-radius: 8px;
      background: #f5f5f5;
    }

    .trend-item.positive {
      background: #e8f5e9;
      border-left: 4px solid #4caf50;
    }

    .trend-item.negative {
      background: #ffebee;
      border-left: 4px solid #f44336;
    }

    .trend-pollutant {
      font-weight: 600;
      flex: 1;
    }

    .trend-value {
      font-size: 0.9rem;
      margin-right: 8px;
    }

    .trend-arrow {
      font-size: 1.2rem;
    }

    .impact-lists {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }

    .impact-list {
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .impact-list h4 {
      font-size: 1rem;
      margin-bottom: 16px;
    }

    .impact-items {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .impact-item {
      display: flex;
      justify-content: space-between;
      padding: 8px 12px;
      border-radius: 6px;
    }

    .impact-item.positive {
      background: #e8f5e9;
    }

    .impact-item.negative {
      background: #ffebee;
    }

    .impact-item .country {
      font-weight: 500;
    }

    .impact-item .value {
      font-weight: 600;
    }

    .impact-item.positive .value {
      color: #2e7d32;
    }

    .impact-item.negative .value {
      color: #c62828;
    }

    @media (max-width: 1024px) {
      .charts-container, .impact-lists {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class TendancesComponent implements OnInit, OnDestroy {
  private dataService = inject(DataService);
  private filterService = inject(FilterService);
  private destroy$ = new Subject<void>();

  selectedPollutantLabel = 'PM2.5';
  covidVariation: number | null = null;
  biggestDrop: CovidImpact | null = null;
  biggestRise: CovidImpact | null = null;
  globalTrend = '';
  trendPvalue = '';

  covidImpactData: BarChartData[] = [];
  allTrends: TemporalGlobal[] = [];
  topDrops: CovidImpact[] = [];
  topRises: CovidImpact[] = [];

  ngOnInit(): void {
    combineLatest([
      this.dataService.covid$,
      this.dataService.temporal$,
      this.filterService.filters$
    ]).pipe(takeUntil(this.destroy$))
      .subscribe(([covid, temporal, filters]) => {
        const pollutant = filters.pollutant;
        const pollutantInfo = POLLUTANTS.find(p => p.code === pollutant);
        this.selectedPollutantLabel = pollutantInfo?.label || 'PM2.5';

        // Filter COVID data for selected pollutant
        const pollutantCovid = covid.filter(c =>
          c.parameter === pollutant && c.variation_pct !== null
        );

        // Calculate median variation
        if (pollutantCovid.length > 0) {
          const variations = pollutantCovid.map(c => c.variation_pct!).sort((a, b) => a - b);
          this.covidVariation = variations[Math.floor(variations.length / 2)];

          // Find biggest drop and rise
          this.biggestDrop = pollutantCovid.reduce((min, c) =>
            (c.variation_pct || 0) < (min?.variation_pct || 0) ? c : min, pollutantCovid[0]);
          this.biggestRise = pollutantCovid.reduce((max, c) =>
            (c.variation_pct || 0) > (max?.variation_pct || 0) ? c : max, pollutantCovid[0]);

          // Top drops and rises
          const sorted = [...pollutantCovid].sort((a, b) => (a.variation_pct || 0) - (b.variation_pct || 0));
          this.topDrops = sorted.slice(0, 5);
          this.topRises = sorted.slice(-5).reverse();

          // Chart data (show 20 countries with most extreme variations)
          const extreme = [...sorted.slice(0, 10), ...sorted.slice(-10)];
          this.covidImpactData = extreme.map(c => ({
            label: c.country_name,
            value: c.variation_pct || 0,
            color: (c.variation_pct || 0) < 0 ? 'rgba(76, 175, 80, 0.8)' : 'rgba(244, 67, 54, 0.8)'
          }));
        }

        // Global trends
        this.allTrends = temporal;
        const currentTrend = temporal.find(t => t.polluant === pollutant);
        if (currentTrend) {
          this.globalTrend = `${currentTrend.variation_pct > 0 ? '+' : ''}${currentTrend.variation_pct.toFixed(1)}%/an`;
          this.trendPvalue = currentTrend.significatif === 'oui' ? 'Significatif' : 'Non significatif';
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  getPollutantLabel(code: string): string {
    const pollutant = POLLUTANTS.find(p => p.code === code);
    return pollutant?.label || code;
  }
}
