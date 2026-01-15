import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, combineLatest, takeUntil } from 'rxjs';

import { DataService } from '../../../services/data.service';
import { FilterService } from '../../../services/filter.service';
import { KpiCardComponent } from '../../kpi-card/kpi-card.component';
import { HeatmapComponent, HeatmapCell } from '../../charts/heatmap/heatmap.component';
import { ScatterChartComponent, ScatterPoint } from '../../charts/scatter-chart/scatter-chart.component';
import { Correlation, Country, POLLUTANTS, Pollutant, PollutantCorrelation } from '../../../models/types';

@Component({
  selector: 'app-facteurs',
  standalone: true,
  imports: [
    CommonModule,
    KpiCardComponent,
    HeatmapComponent,
    ScatterChartComponent
  ],
  template: `
    <section class="section facteurs" id="facteurs">
      <h2 class="section-title">
        <span class="title-icon">🔗</span>
        Facteurs Explicatifs
      </h2>
      <p class="section-subtitle">Corrélations entre pollution et indicateurs socio-économiques</p>

      <!-- KPIs -->
      <div class="kpi-grid">
        <app-kpi-card
          label="Variable la plus corrélée"
          [value]="topCorrelation ? formatIndicator(topCorrelation.indicator) : '-'"
          icon="link"
          [subtitle]="topCorrelation ? 'ρ = ' + topCorrelation.correlation?.toFixed(3) : ''">
        </app-kpi-card>

        <app-kpi-card
          label="Corrélations significatives"
          [value]="significantCount"
          icon="check_circle"
          [subtitle]="'sur ' + totalCorrelations + ' testées'"
          tooltip="p-value < 0.05">
        </app-kpi-card>

        <app-kpi-card
          label="Axe le plus corrélé"
          [value]="topAxis"
          icon="category"
          [subtitle]="topAxisCount + ' corrélations significatives'">
        </app-kpi-card>

        <app-kpi-card
          label="Couverture World Bank"
          [value]="'94 pays'"
          icon="public"
          tooltip="Nombre de pays avec des indicateurs World Bank disponibles">
        </app-kpi-card>
      </div>

      <!-- Pollutant Correlation Matrix -->
      <div class="pollutant-correlation-section">
        <div class="chart-card">
          <h3 class="chart-title">Corrélations entre polluants</h3>
          <p class="chart-subtitle">Matrice de corrélation de Spearman entre les 6 polluants mesurés</p>
          <app-heatmap
            [data]="pollutantHeatmapData"
            [rows]="pollutantHeatmapLabels"
            [columns]="pollutantHeatmapLabels"
            [highlightedRow]="selectedPollutantLabel"
            [grayDiagonal]="true"
            [centered]="true">
          </app-heatmap>
          <div class="correlation-insight" *ngIf="strongestPollutantCorrelation">
            <span class="insight-icon">💡</span>
            <span class="insight-text">
              Corrélation la plus forte : <strong>{{ strongestPollutantCorrelation.pair }}</strong>
              (ρ = {{ strongestPollutantCorrelation.value.toFixed(3) }})
            </span>
          </div>
        </div>
      </div>

      <!-- Charts -->
      <div class="charts-container">
        <div class="chart-card">
          <h3 class="chart-title">Matrice de corrélations (Indicateurs socio-économiques)</h3>
          <app-heatmap
            [data]="heatmapData"
            [rows]="heatmapRows"
            [columns]="heatmapColumns"
            [highlightedColumn]="selectedPollutantLabel"
            [rowLabelWidth]="180">
          </app-heatmap>
        </div>

        <div class="chart-card">
          <h3 class="chart-title">Top 10 corrélations - {{ selectedPollutantLabel }}</h3>
          <div class="correlations-list">
            @for (corr of topCorrelations; track corr.indicator; let i = $index) {
              <div class="correlation-item"
                   [class.positive]="(corr.correlation || 0) > 0"
                   [class.negative]="(corr.correlation || 0) < 0"
                   [class.selected]="selectedIndicator === corr.indicator"
                   (click)="selectIndicator(corr.indicator)">
                <span class="rank">{{ i + 1 }}</span>
                <span class="indicator">{{ formatIndicator(corr.indicator) }}</span>
                <span class="correlation-value">
                  ρ = {{ corr.correlation?.toFixed(3) }}
                </span>
                <span class="axis-badge">{{ corr.axis }}</span>
              </div>
            }
          </div>
        </div>
      </div>

      <!-- Scatter plot -->
      <div class="scatter-section">
        <div class="chart-card full-width">
          <h3 class="chart-title">
            {{ selectedPollutantLabel }} vs {{ formatIndicator(selectedIndicator) }}
            <span class="correlation-badge" *ngIf="selectedCorrelation">
              ρ = {{ selectedCorrelation.correlation?.toFixed(3) }}
              {{ selectedCorrelation.significant ? '✓' : '' }}
            </span>
          </h3>
          <div class="scatter-container">
            <app-scatter-chart
              [points]="scatterPoints"
              [xLabel]="formatIndicator(selectedIndicator)"
              [yLabel]="selectedPollutantLabel + ' (µg/m³)'"
              [showTrendline]="true">
            </app-scatter-chart>
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
      margin-bottom: 24px;
    }

    .charts-container {
      display: grid;
      grid-template-columns: 1.5fr 1fr;
      gap: 24px;
      margin-bottom: 24px;
    }

    .chart-card {
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .chart-card.full-width {
      grid-column: 1 / -1;
    }

    .chart-title {
      font-size: 1rem;
      font-weight: 600;
      color: #333;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .correlation-badge {
      font-size: 0.85rem;
      padding: 4px 12px;
      background: #e3f2fd;
      border-radius: 16px;
      font-weight: 500;
    }

    .correlations-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .correlation-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      border-radius: 8px;
      background: #f5f5f5;
      cursor: pointer;
      transition: all 0.2s;
    }

    .correlation-item:hover {
      background: #e0e0e0;
    }

    .correlation-item.selected {
      background: #e3f2fd;
      border: 2px solid #1976d2;
    }

    .correlation-item.positive {
      border-left: 4px solid #4caf50;
    }

    .correlation-item.negative {
      border-left: 4px solid #f44336;
    }

    .rank {
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #1976d2;
      color: white;
      border-radius: 50%;
      font-size: 0.75rem;
      font-weight: 600;
    }

    .indicator {
      flex: 1;
      font-size: 0.85rem;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .correlation-value {
      font-weight: 600;
      font-size: 0.85rem;
    }

    .axis-badge {
      font-size: 0.7rem;
      padding: 2px 8px;
      background: rgba(0,0,0,0.1);
      border-radius: 10px;
    }

    .scatter-section {
      margin-top: 24px;
    }

    .scatter-container {
      height: 300px;
    }

    .pollutant-correlation-section {
      margin-bottom: 24px;
    }

    .pollutant-correlation-section .chart-card {
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .chart-subtitle {
      color: #666;
      font-size: 0.9rem;
      margin-bottom: 16px;
      margin-top: -8px;
    }

    .correlation-insight {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 16px;
      padding: 12px;
      background: #e3f2fd;
      border-radius: 8px;
      font-size: 0.9rem;
    }

    .insight-icon {
      font-size: 1.2rem;
    }

    .insight-text strong {
      color: #1976d2;
    }

    @media (max-width: 1024px) {
      .charts-container {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class FacteursComponent implements OnInit, OnDestroy {
  private dataService = inject(DataService);
  private filterService = inject(FilterService);
  private destroy$ = new Subject<void>();

  selectedPollutantLabel = 'PM2.5';

  topCorrelation: Correlation | null = null;
  significantCount = 0;
  totalCorrelations = 0;
  topAxis = '';
  topAxisCount = 0;

  heatmapData: HeatmapCell[] = [];
  heatmapRows: string[] = [];
  heatmapColumns: string[] = [];

  // Pollutant correlation heatmap
  pollutantHeatmapData: HeatmapCell[] = [];
  pollutantHeatmapLabels: string[] = [];
  strongestPollutantCorrelation: { pair: string; value: number } | null = null;

  topCorrelations: Correlation[] = [];
  selectedIndicator = 'eco_NY_GDP_PCAP_CD';
  selectedCorrelation: Correlation | null = null;
  scatterPoints: ScatterPoint[] = [];

  private correlations: Correlation[] = [];
  private countries: Country[] = [];
  private currentPollutant: Pollutant = 'pm25';

  ngOnInit(): void {
    combineLatest([
      this.dataService.correlations$,
      this.dataService.countries$,
      this.filterService.filters$
    ]).pipe(takeUntil(this.destroy$))
      .subscribe(([correlations, countries, filters]) => {
        this.correlations = correlations;
        this.countries = countries;
        this.currentPollutant = filters.pollutant;

        const pollutantInfo = POLLUTANTS.find(p => p.code === filters.pollutant);
        this.selectedPollutantLabel = pollutantInfo?.label || 'PM2.5';

        this.updateData();
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  updateData(): void {
    let filtered = this.correlations.filter(c => c.pollutant === this.currentPollutant);

    // Sort by absolute correlation
    filtered.sort((a, b) => Math.abs(b.correlation || 0) - Math.abs(a.correlation || 0));

    this.topCorrelations = filtered.slice(0, 10);
    this.topCorrelation = this.topCorrelations[0] || null;

    // Stats
    const allForPollutant = this.correlations.filter(c => c.pollutant === this.currentPollutant);
    this.totalCorrelations = allForPollutant.length;
    this.significantCount = allForPollutant.filter(c => c.significant).length;

    // Top axis
    const axisCounts: { [key: string]: number } = {};
    allForPollutant.filter(c => c.significant).forEach(c => {
      axisCounts[c.axis] = (axisCounts[c.axis] || 0) + 1;
    });
    const topAxisEntry = Object.entries(axisCounts).sort((a, b) => b[1] - a[1])[0];
    this.topAxis = topAxisEntry?.[0] || '-';
    this.topAxisCount = topAxisEntry?.[1] || 0;

    // Heatmap (indicators as rows, just one column for selected pollutant)
    this.buildHeatmap(filtered);

    // Build pollutant correlation heatmap
    this.buildPollutantHeatmap();

    // Update scatter
    this.updateScatter();
  }

  private buildHeatmap(correlations: Correlation[]): void {
    // Use all pollutants as columns
    this.heatmapColumns = POLLUTANTS.map(p => p.label);

    // Get unique indicators from correlations, grouped by axis
    const axes = ['Économie', 'Énergie', 'Transport', 'Démographie', 'Santé'];
    const indicatorSet = new Set<string>();
    const cells: HeatmapCell[] = [];

    // Get top indicators per axis based on current pollutant
    axes.forEach(axis => {
      const axisCorrelations = correlations.filter(c => c.axis === axis).slice(0, 3);
      axisCorrelations.forEach(c => {
        indicatorSet.add(c.indicator);
      });
    });

    const indicators = Array.from(indicatorSet);

    // Build cells for all pollutants
    indicators.forEach(indicator => {
      POLLUTANTS.forEach(pollutant => {
        const corr = this.correlations.find(c =>
          c.pollutant === pollutant.code && c.indicator === indicator
        );
        cells.push({
          row: this.formatIndicator(indicator),
          col: pollutant.label,
          value: corr?.correlation ?? null,
          significant: corr?.significant || false
        });
      });
    });

    this.heatmapRows = indicators.map(i => this.formatIndicator(i));
    this.heatmapData = cells;
  }

  private buildPollutantHeatmap(): void {
    const pollutantCorrelations = this.dataService.getPollutantCorrelations();

    // Create labels (pollutant names)
    this.pollutantHeatmapLabels = POLLUTANTS.map(p => p.label);

    // Build cells for the heatmap
    const cells: HeatmapCell[] = [];
    let strongestCorr = { pair: '', value: 0 };

    for (const corr of pollutantCorrelations) {
      const pollutant1Info = POLLUTANTS.find(p => p.code === corr.pollutant1);
      const pollutant2Info = POLLUTANTS.find(p => p.code === corr.pollutant2);

      if (!pollutant1Info || !pollutant2Info) continue;

      cells.push({
        row: pollutant1Info.label,
        col: pollutant2Info.label,
        value: corr.correlation,
        significant: corr.significant
      });

      // Track strongest correlation (excluding self-correlations)
      if (corr.pollutant1 !== corr.pollutant2 && corr.correlation !== null) {
        if (Math.abs(corr.correlation) > Math.abs(strongestCorr.value)) {
          strongestCorr = {
            pair: `${pollutant1Info.label} / ${pollutant2Info.label}`,
            value: corr.correlation
          };
        }
      }
    }

    this.pollutantHeatmapData = cells;
    this.strongestPollutantCorrelation = strongestCorr.pair ? strongestCorr : null;
  }

  selectIndicator(indicator: string): void {
    this.selectedIndicator = indicator;
    this.selectedCorrelation = this.correlations.find(c =>
      c.pollutant === this.currentPollutant && c.indicator === indicator
    ) || null;
    this.updateScatter();
  }

  private updateScatter(): void {
    const pollutantKey = `pollution_${this.currentPollutant}` as keyof Country;

    this.scatterPoints = this.countries
      .filter(c => {
        const pollutionValue = c[pollutantKey];
        const indicatorValue = c[this.selectedIndicator as keyof Country];
        return pollutionValue !== null && indicatorValue !== null;
      })
      .map(c => ({
        x: c[this.selectedIndicator as keyof Country] as number,
        y: c[pollutantKey] as number,
        label: c.nom_pays,
        size: 6,
        color: 'rgba(25, 118, 210, 0.7)'
      }));
  }

  formatIndicator(indicator: string): string {
    const labels: { [key: string]: string } = {
      // Santé
      'sante_SP_DYN_LE00_IN': 'Espérance de vie',
      'sante_SH_XPD_CHEX_GD_ZS': 'Dép. santé (% PIB)',
      'sante_SH_XPD_CHEX_PC_CD': 'Dép. santé/hab',
      'sante_SH_STA_AIRP_P5': 'Décès pollution',
      'sante_EN_ATM_PM25_MC_M3': 'Exposition PM2.5',
      // Économie
      'eco_NY_GDP_PCAP_CD': 'PIB/habitant',
      'eco_NY_GDP_PCAP_PP_CD': 'PIB/hab (PPA)',
      'eco_NV_AGR_TOTL_ZS': 'Agriculture (% PIB)',
      'eco_NV_IND_TOTL_ZS': 'Industrie (% PIB)',
      'eco_NV_IND_MANF_ZS': 'Manufacture (% PIB)',
      'eco_NV_SRV_TOTL_ZS': 'Services (% PIB)',
      'eco_SL_AGR_EMPL_ZS': 'Emploi agriculture',
      'eco_SL_IND_EMPL_ZS': 'Emploi industrie',
      'eco_SL_SRV_EMPL_ZS': 'Emploi services',
      // Démographie
      'demo_SP_POP_TOTL': 'Population totale',
      'demo_SP_URB_TOTL': 'Pop. urbaine',
      'demo_SP_URB_TOTL_IN_ZS': 'Pop. urbaine (%)',
      'demo_SP_URB_GROW': 'Croiss. urbaine',
      'demo_EN_POP_DNST': 'Densité pop.',
      'demo_EN_URB_LCTY': 'Pop. grandes villes',
      'demo_EN_URB_LCTY_UR_ZS': 'Pop. grandes villes (%)',
      'demo_AG_LND_TOTL_K2': 'Superficie totale',
      'demo_AG_SRF_TOTL_K2': 'Surface terrestre',
      'demo_AG_LND_FRST_ZS': 'Couvert forestier',
      // Énergie
      'energie_EG_ELC_COAL_ZS': 'Élec. charbon (%)',
      'energie_EG_ELC_FOSL_ZS': 'Élec. fossiles (%)',
      'energie_EG_ELC_NGAS_ZS': 'Élec. gaz (%)',
      'energie_EG_ELC_NUCL_ZS': 'Élec. nucléaire (%)',
      'energie_EG_ELC_PETR_ZS': 'Élec. pétrole (%)',
      'energie_EG_ELC_RNWX_ZS': 'Élec. renouvelable (%)',
      'energie_EG_FEC_RNEW_ZS': 'Conso. renouvelable',
      'energie_EG_USE_ELEC_KH_PC': 'Conso. élec./hab',
      'energie_EG_USE_PCAP_KG_OE': 'Conso. énergie/hab',
      // Transport
      'transport_IS_AIR_DPRT': 'Départs aériens',
      'transport_IS_AIR_PSGR': 'Passagers aériens',
      'transport_IS_RRS_TOTL_KM': 'Réseau ferroviaire'
    };
    return labels[indicator] || indicator;
  }
}
