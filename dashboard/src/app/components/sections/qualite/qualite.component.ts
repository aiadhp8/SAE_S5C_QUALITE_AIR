import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, takeUntil } from 'rxjs';

import { DataService } from '../../../services/data.service';
import { KpiCardComponent } from '../../kpi-card/kpi-card.component';
import { DoughnutChartComponent, DoughnutData } from '../../charts/doughnut-chart/doughnut-chart.component';
import { BarChartComponent, BarChartData } from '../../charts/bar-chart/bar-chart.component';
import { Completude } from '../../../models/types';

@Component({
  selector: 'app-qualite',
  standalone: true,
  imports: [CommonModule, KpiCardComponent, DoughnutChartComponent, BarChartComponent],
  template: `
    <section class="section qualite" id="qualite">
      <h2 class="section-title">
        <span class="title-icon">✅</span>
        Qualité des Données
      </h2>
      <p class="section-subtitle">Transparence sur les limites et la fiabilité des analyses</p>

      <!-- KPIs -->
      <div class="kpi-grid">
        <app-kpi-card
          label="Pays analysés (final)"
          [value]="94"
          icon="flag"
          subtitle="Après filtrage et nettoyage"
          [highlight]="true">
        </app-kpi-card>

        <app-kpi-card
          label="Complétude moyenne"
          [value]="avgCompletude"
          unit="%"
          icon="check_circle"
          [highlight]="avgCompletude > 80"
          tooltip="Pourcentage moyen de données complètes par axe">
        </app-kpi-card>

        <app-kpi-card
          label="Polluants avec données complètes"
          [value]="38"
          icon="science"
          subtitle="40% des pays"
          tooltip="Pays ayant des données pour les 6 polluants">
        </app-kpi-card>

        <app-kpi-card
          label="Période couverte"
          value="2018-2023"
          icon="date_range"
          subtitle="6 années de données">
        </app-kpi-card>
      </div>

      <!-- Data Pipeline -->
      <div class="pipeline-section">
        <h3 class="subsection-title">Pipeline de traitement des données</h3>
        <div class="pipeline">
          <div class="pipeline-step">
            <div class="step-icon">📥</div>
            <div class="step-content">
              <strong>Collecte</strong>
              <span>OpenAQ + World Bank</span>
              <span class="step-count">~200 pays</span>
            </div>
          </div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-step">
            <div class="step-icon">🧹</div>
            <div class="step-content">
              <strong>Nettoyage</strong>
              <span>Valeurs manquantes</span>
              <span class="step-count">~150 pays</span>
            </div>
          </div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-step">
            <div class="step-icon">🔗</div>
            <div class="step-content">
              <strong>Jointure</strong>
              <span>Fusion des sources</span>
              <span class="step-count">~120 pays</span>
            </div>
          </div>
          <div class="pipeline-arrow">→</div>
          <div class="pipeline-step">
            <div class="step-icon">📊</div>
            <div class="step-content">
              <strong>Filtrage</strong>
              <span>Outliers + QA</span>
              <span class="step-count highlight">94 pays</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts -->
      <div class="charts-container">
        <div class="chart-card">
          <h3 class="chart-title">Complétude par axe thématique</h3>
          <div class="completude-bars">
            @for (item of completudeData; track item.axe) {
              <div class="completude-item">
                <span class="axe-name">{{ item.axe }}</span>
                <div class="bar-wrapper">
                  <div class="bar-fill" [style.width.%]="item.pct_complets">
                    {{ item.pct_complets.toFixed(0) }}%
                  </div>
                </div>
                <span class="indicator-count">{{ item.nb_indicateurs }} indicateurs</span>
              </div>
            }
          </div>
        </div>

        <div class="chart-card">
          <h3 class="chart-title">Répartition des sources</h3>
          <app-doughnut-chart [data]="sourcesData"></app-doughnut-chart>
        </div>
      </div>

      <!-- Limitations -->
      <div class="limitations-section">
        <h3 class="subsection-title">Limites et biais identifiés</h3>
        <div class="limitations-grid">
          <div class="limitation-card">
            <div class="limitation-icon">🌍</div>
            <div class="limitation-content">
              <strong>Biais géographique</strong>
              <p>Sous-représentation de l'Afrique et de certaines régions d'Asie dans les données de pollution.</p>
            </div>
          </div>

          <div class="limitation-card">
            <div class="limitation-icon">📏</div>
            <div class="limitation-content">
              <strong>Hétérogénéité des mesures</strong>
              <p>Les méthodes de mesure varient selon les stations, affectant la comparabilité internationale.</p>
            </div>
          </div>

          <div class="limitation-card">
            <div class="limitation-icon">⏰</div>
            <div class="limitation-content">
              <strong>Couverture temporelle</strong>
              <p>Certains pays n'ont pas de données pour toutes les années (2018-2023).</p>
            </div>
          </div>

          <div class="limitation-card">
            <div class="limitation-icon">🔢</div>
            <div class="limitation-content">
              <strong>Agrégation nationale</strong>
              <p>Les moyennes nationales masquent les variations régionales importantes.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Methodology note -->
      <div class="methodology-note">
        <h4>Note méthodologique</h4>
        <p>
          Les analyses utilisent principalement la <strong>médiane</strong> plutôt que la moyenne pour
          réduire l'impact des valeurs extrêmes. Les tests de corrélation utilisent le coefficient de
          <strong>Spearman</strong> (rang) plutôt que Pearson pour être robustes aux distributions non-normales.
          La correction de <strong>Benjamini-Hochberg</strong> est appliquée pour contrôler le taux de faux positifs.
        </p>
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

    .subsection-title {
      font-size: 1.1rem;
      font-weight: 600;
      color: #333;
      margin-bottom: 16px;
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-bottom: 20px;
    }

    .pipeline-section {
      background: white;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      margin-bottom: 20px;
    }

    .pipeline {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 16px;
      flex-wrap: wrap;
    }

    .pipeline-step {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 16px 24px;
      background: #f5f5f5;
      border-radius: 12px;
      min-width: 140px;
    }

    .step-icon {
      font-size: 2rem;
      margin-bottom: 8px;
    }

    .step-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }

    .step-content strong {
      color: #333;
      margin-bottom: 4px;
    }

    .step-content span {
      font-size: 0.8rem;
      color: #666;
    }

    .step-count {
      margin-top: 4px;
      font-weight: 600;
    }

    .step-count.highlight {
      color: #1976d2;
      font-size: 0.9rem !important;
    }

    .pipeline-arrow {
      font-size: 1.5rem;
      color: #999;
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

    .completude-bars {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .completude-item {
      display: grid;
      grid-template-columns: 100px 1fr 100px;
      align-items: center;
      gap: 12px;
    }

    .axe-name {
      font-size: 0.85rem;
      font-weight: 500;
      text-transform: capitalize;
    }

    .bar-wrapper {
      height: 24px;
      background: #e0e0e0;
      border-radius: 12px;
      overflow: hidden;
    }

    .bar-fill {
      height: 100%;
      background: linear-gradient(90deg, #1976d2, #42a5f5);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      padding-right: 8px;
      color: white;
      font-size: 0.75rem;
      font-weight: 600;
    }

    .indicator-count {
      font-size: 0.75rem;
      color: #888;
    }

    .limitations-section {
      margin-bottom: 20px;
    }

    .limitations-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }

    .limitation-card {
      display: flex;
      gap: 12px;
      padding: 16px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      border-left: 4px solid #ff9800;
    }

    .limitation-icon {
      font-size: 1.5rem;
    }

    .limitation-content strong {
      display: block;
      color: #333;
      margin-bottom: 4px;
    }

    .limitation-content p {
      font-size: 0.85rem;
      color: #666;
      margin: 0;
      line-height: 1.4;
    }

    .methodology-note {
      background: #e8f5e9;
      border-radius: 12px;
      padding: 20px;
      border-left: 4px solid #4caf50;
    }

    .methodology-note h4 {
      margin: 0 0 8px 0;
      color: #2e7d32;
    }

    .methodology-note p {
      margin: 0;
      font-size: 0.9rem;
      color: #333;
      line-height: 1.6;
    }

    .methodology-note strong {
      color: #1b5e20;
    }

    @media (max-width: 1024px) {
      .charts-container {
        grid-template-columns: 1fr;
      }

      .pipeline {
        flex-direction: column;
      }

      .pipeline-arrow {
        transform: rotate(90deg);
      }
    }
  `]
})
export class QualiteComponent implements OnInit, OnDestroy {
  private dataService = inject(DataService);
  private destroy$ = new Subject<void>();

  avgCompletude = 0;
  completudeData: Completude[] = [];

  sourcesData: DoughnutData[] = [
    { label: 'OpenAQ (pollution)', value: 1804, color: '#1976d2' },
    { label: 'World Bank (économie)', value: 13049, color: '#4caf50' },
    { label: 'World Bank (démographie)', value: 14584, color: '#ff9800' },
    { label: 'World Bank (énergie)', value: 10471, color: '#9c27b0' },
    { label: 'World Bank (santé)', value: 5004, color: '#00bcd4' }
  ];

  ngOnInit(): void {
    this.dataService.completude$.pipe(takeUntil(this.destroy$))
      .subscribe(completude => {
        this.completudeData = completude;
        if (completude.length > 0) {
          this.avgCompletude = completude.reduce((sum, c) => sum + c.pct_complets, 0) / completude.length;
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
