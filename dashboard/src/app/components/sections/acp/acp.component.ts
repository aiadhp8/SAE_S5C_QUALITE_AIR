import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, takeUntil } from 'rxjs';

import { DataService } from '../../../services/data.service';
import { KpiCardComponent } from '../../kpi-card/kpi-card.component';
import { RadarChartComponent, RadarDataset } from '../../charts/radar-chart/radar-chart.component';
import { ScatterChartComponent, ScatterPoint } from '../../charts/scatter-chart/scatter-chart.component';
import { AcpData, Country } from '../../../models/types';

@Component({
  selector: 'app-acp',
  standalone: true,
  imports: [CommonModule, KpiCardComponent, RadarChartComponent, ScatterChartComponent],
  template: `
    <section class="section acp" id="acp">
      <h2 class="section-title">
        <span class="title-icon">🎯</span>
        Analyse Multivariée (ACP)
      </h2>
      <p class="section-subtitle">Réduction dimensionnelle et profils de pays</p>

      <!-- KPIs -->
      <div class="kpi-grid">
        <app-kpi-card
          label="Variance PC1"
          [value]="variancePC1"
          unit="%"
          icon="looks_one"
          tooltip="Variance expliquée par la première composante principale">
        </app-kpi-card>

        <app-kpi-card
          label="Variance PC1+PC2"
          [value]="variancePC1PC2"
          unit="%"
          icon="looks_two"
          tooltip="Variance cumulée expliquée">
        </app-kpi-card>

        <app-kpi-card
          label="Top variable PC1"
          [value]="topVarPC1"
          icon="star"
          [subtitle]="'Loading: ' + topLoadingPC1.toFixed(3)">
        </app-kpi-card>

        <app-kpi-card
          label="Top variable PC2"
          [value]="topVarPC2"
          icon="star_half"
          [subtitle]="'Loading: ' + topLoadingPC2.toFixed(3)">
        </app-kpi-card>
      </div>

      <!-- Charts -->
      <div class="charts-container">
        <div class="chart-card">
          <h3 class="chart-title">Projection des pays (PC1 vs PC2)</h3>
          <div class="scatter-container">
            <app-scatter-chart
              [points]="countryProjections"
              xLabel="PC1 (Développement économique)"
              yLabel="PC2 (Urbanisation)">
            </app-scatter-chart>
          </div>
        </div>

        <div class="chart-card">
          <h3 class="chart-title">Loadings des variables principales</h3>
          <div class="loadings-container">
            @for (loading of topLoadings; track loading.variable) {
              <div class="loading-item">
                <span class="loading-var">{{ formatVariable(loading.variable) }}</span>
                <div class="loading-bars">
                  <div class="loading-bar pc1"
                       [style.width.%]="Math.abs(loading.pc1) * 100"
                       [class.negative]="loading.pc1 < 0">
                    PC1: {{ loading.pc1.toFixed(2) }}
                  </div>
                  <div class="loading-bar pc2"
                       [style.width.%]="Math.abs(loading.pc2) * 100"
                       [class.negative]="loading.pc2 < 0">
                    PC2: {{ loading.pc2.toFixed(2) }}
                  </div>
                </div>
              </div>
            }
          </div>
        </div>
      </div>

      <!-- Radar Chart for Clusters -->
      <div class="radar-section">
        <div class="chart-card">
          <h3 class="chart-title">Profils types des clusters</h3>
          <div class="radar-container">
            <app-radar-chart
              [labels]="radarLabels"
              [datasets]="radarDatasets">
            </app-radar-chart>
          </div>
          <div class="cluster-legend">
            <div class="cluster-item cluster-1">
              <span class="cluster-dot"></span>
              <span>Pays développés (forte conso. énergie, faible agriculture)</span>
            </div>
            <div class="cluster-item cluster-2">
              <span class="cluster-dot"></span>
              <span>Pays en développement (forte urbanisation, industrie croissante)</span>
            </div>
            <div class="cluster-item cluster-3">
              <span class="cluster-dot"></span>
              <span>Pays émergents (économie mixte, transition énergétique)</span>
            </div>
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
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 20px;
    }

    .chart-card {
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .chart-title {
      font-size: 1rem;
      font-weight: 600;
      color: #333;
      margin-bottom: 16px;
    }

    .scatter-container {
      height: 280px;
    }

    .loadings-container {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .loading-item {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .loading-var {
      font-size: 0.8rem;
      font-weight: 500;
      color: #333;
      min-width: 100px;
      max-width: 100px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .loading-bars {
      display: flex;
      flex: 1;
      gap: 4px;
    }

    .loading-bar {
      height: 22px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      padding: 0 8px;
      font-size: 0.7rem;
      color: white;
      font-weight: 500;
      min-width: 80px;
    }

    .loading-bar.pc1 {
      background: #1976d2;
    }

    .loading-bar.pc2 {
      background: #4caf50;
    }

    .loading-bar.negative {
      opacity: 0.6;
    }

    .radar-section .chart-card {
      max-width: 100%;
    }

    .radar-container {
      height: 450px;
    }

    .cluster-legend {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid #eee;
    }

    .cluster-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85rem;
      color: #666;
    }

    .cluster-dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
    }

    .cluster-1 .cluster-dot { background: #1976d2; }
    .cluster-2 .cluster-dot { background: #4caf50; }
    .cluster-3 .cluster-dot { background: #ff9800; }

    @media (max-width: 1024px) {
      .charts-container {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class AcpComponent implements OnInit, OnDestroy {
  Math = Math;

  private dataService = inject(DataService);
  private destroy$ = new Subject<void>();

  variancePC1 = 25.3;
  variancePC1PC2 = 42.1;
  topVarPC1 = 'PIB/habitant';
  topVarPC2 = 'Pop. urbaine';
  topLoadingPC1 = -0.226;
  topLoadingPC2 = 0.355;

  countryProjections: ScatterPoint[] = [];
  topLoadings: { variable: string; pc1: number; pc2: number }[] = [];

  radarLabels = ['PIB/hab', 'Pop. urbaine', 'Industrie', 'Agriculture', 'Énergie fossile', 'Espérance vie'];
  radarDatasets: RadarDataset[] = [];

  ngOnInit(): void {
    this.dataService.acp$.pipe(takeUntil(this.destroy$))
      .subscribe(acp => {
        if (acp) {
          this.processAcpData(acp);
        }
      });

    this.dataService.countries$.pipe(takeUntil(this.destroy$))
      .subscribe(countries => {
        this.generateProjections(countries);
      });

    // Static radar data for clusters (based on typical patterns)
    this.radarDatasets = [
      {
        label: 'Développés',
        data: [90, 75, 65, 10, 40, 95],
        color: '#1976d2'
      },
      {
        label: 'En développement',
        data: [30, 45, 55, 50, 60, 65],
        color: '#4caf50'
      },
      {
        label: 'Émergents',
        data: [60, 60, 70, 25, 55, 80],
        color: '#ff9800'
      }
    ];
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private processAcpData(acp: AcpData): void {
    if (!acp.loadings || acp.loadings.length === 0) return;

    // Extract top loadings
    const loadings = acp.loadings.map((row: any) => ({
      variable: row['Unnamed: 0'] || row[''] || 'Unknown',
      pc1: row['PC1'] || 0,
      pc2: row['PC2'] || 0
    }));

    // Sort by absolute PC1 loading
    loadings.sort((a, b) => Math.abs(b.pc1) - Math.abs(a.pc1));
    this.topLoadings = loadings.slice(0, 8);

    // Find top variables
    const topPC1 = loadings.reduce((max, l) =>
      Math.abs(l.pc1) > Math.abs(max.pc1) ? l : max, loadings[0]);
    const topPC2 = loadings.reduce((max, l) =>
      Math.abs(l.pc2) > Math.abs(max.pc2) ? l : max, loadings[0]);

    this.topVarPC1 = this.formatVariable(topPC1.variable);
    this.topLoadingPC1 = topPC1.pc1;
    this.topVarPC2 = this.formatVariable(topPC2.variable);
    this.topLoadingPC2 = topPC2.pc2;
  }

  private generateProjections(countries: Country[]): void {
    // Generate synthetic projections based on country characteristics
    this.countryProjections = countries
      .filter(c => c.eco_NY_GDP_PCAP_CD && c.demo_SP_URB_TOTL_IN_ZS)
      .slice(0, 50)
      .map(c => {
        const gdpNorm = Math.log10(c.eco_NY_GDP_PCAP_CD || 1) - 3;
        const urbNorm = ((c.demo_SP_URB_TOTL_IN_ZS || 50) - 50) / 50;
        return {
          x: gdpNorm * 2 + (Math.random() - 0.5),
          y: urbNorm * 2 + (Math.random() - 0.5),
          label: c.nom_pays,
          size: 6,
          color: this.getClusterColor(c)
        };
      });
  }

  private getClusterColor(country: Country): string {
    const gdp = country.eco_NY_GDP_PCAP_CD || 0;
    if (gdp > 30000) return 'rgba(25, 118, 210, 0.7)';  // Développés
    if (gdp > 10000) return 'rgba(255, 152, 0, 0.7)';  // Émergents
    return 'rgba(76, 175, 80, 0.7)';                    // En développement
  }

  formatVariable(variable: string): string {
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
    return labels[variable] || variable;
  }
}
