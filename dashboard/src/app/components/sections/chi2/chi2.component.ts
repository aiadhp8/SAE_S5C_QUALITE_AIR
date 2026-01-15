import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, takeUntil } from 'rxjs';

import { DataService } from '../../../services/data.service';
import { KpiCardComponent } from '../../kpi-card/kpi-card.component';
import { Chi2Result } from '../../../models/types';

@Component({
  selector: 'app-chi2',
  standalone: true,
  imports: [CommonModule, KpiCardComponent],
  template: `
    <section class="section chi2" id="chi2">
      <h2 class="section-title">
        <span class="title-icon">📐</span>
        Tests d'Indépendance Chi²
      </h2>
      <p class="section-subtitle">Analyse des relations entre variables catégorielles</p>

      <!-- KPIs -->
      <div class="kpi-grid">
        <app-kpi-card
          label="Tests réalisés"
          [value]="totalTests"
          icon="science"
          subtitle="Tests d'indépendance">
        </app-kpi-card>

        <app-kpi-card
          label="Relations significatives"
          [value]="significantTests"
          icon="link"
          [subtitle]="'sur ' + totalTests + ' tests (p < 0.05)'"
          [highlight]="significantTests > 0">
        </app-kpi-card>

        <app-kpi-card
          label="Plus forte association"
          [value]="strongestAssociation"
          icon="trending_up"
          [subtitle]="'V de Cramér = ' + strongestV.toFixed(3)">
        </app-kpi-card>

        <app-kpi-card
          label="Seuil de significativité"
          value="α = 0.05"
          icon="rule"
          tooltip="Probabilité de rejeter H0 à tort">
        </app-kpi-card>
      </div>

      <!-- Explanation Card -->
      <div class="explanation-card">
        <h3>Qu'est-ce que le test du Chi² ?</h3>
        <p>
          Le test du Chi² (χ²) permet de déterminer si deux variables catégorielles sont
          <strong>indépendantes</strong> ou s'il existe une <strong>association significative</strong> entre elles.
        </p>
        <div class="formula">
          <span class="formula-text">H₀ : Les variables sont indépendantes</span>
          <span class="formula-text">H₁ : Les variables sont dépendantes</span>
        </div>
        <p>
          Si <strong>p-value &lt; 0.05</strong>, on rejette H₀ et on conclut qu'il existe une dépendance significative.
          Le <strong>V de Cramér</strong> mesure la force de l'association (0 = aucune, 1 = parfaite).
        </p>
      </div>

      <!-- Results Table -->
      <div class="results-section">
        <h3 class="results-title">Résultats des tests</h3>

        <div class="results-grid">
          @for (result of chi2Results; track result.test) {
            <div class="result-card" [class.significant]="result.significatif">
              <div class="result-header">
                <h4 class="result-test">{{ result.test }}</h4>
                <span class="result-badge" [class.significant]="result.significatif">
                  {{ result.interpretation }}
                </span>
              </div>

              <p class="result-description">{{ result.description }}</p>

              <div class="result-stats">
                <div class="stat-item">
                  <span class="stat-label">χ²</span>
                  <span class="stat-value">{{ result.chi2.toFixed(2) }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">p-value</span>
                  <span class="stat-value" [class.significant]="result.p_value < 0.05">
                    {{ formatPValue(result.p_value) }}
                  </span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">ddl</span>
                  <span class="stat-value">{{ result.dof }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">V de Cramér</span>
                  <span class="stat-value">{{ result.cramers_v.toFixed(3) }}</span>
                </div>
              </div>

              <div class="result-conclusion">
                <span class="conclusion-icon">{{ result.significatif ? '✓' : '○' }}</span>
                <span class="conclusion-text">{{ result.conclusion }}</span>
              </div>

              <!-- Cramér's V visualization -->
              <div class="cramer-bar">
                <div class="cramer-fill" [style.width.%]="result.cramers_v * 100"></div>
                <span class="cramer-label">Force de l'association</span>
              </div>
            </div>
          }
        </div>
      </div>

      <!-- Interpretation Guide -->
      <div class="guide-section">
        <h3 class="guide-title">Guide d'interprétation</h3>
        <div class="guide-grid">
          <div class="guide-item">
            <div class="guide-icon">📊</div>
            <h4>V de Cramér</h4>
            <ul>
              <li><strong>0.0 - 0.1</strong> : Négligeable</li>
              <li><strong>0.1 - 0.3</strong> : Faible</li>
              <li><strong>0.3 - 0.5</strong> : Modérée</li>
              <li><strong>&gt; 0.5</strong> : Forte</li>
            </ul>
          </div>
          <div class="guide-item">
            <div class="guide-icon">🎯</div>
            <h4>P-value</h4>
            <ul>
              <li><strong>&gt; 0.05</strong> : Non significatif</li>
              <li><strong>&lt; 0.05</strong> : Significatif *</li>
              <li><strong>&lt; 0.01</strong> : Très significatif **</li>
              <li><strong>&lt; 0.001</strong> : Hautement significatif ***</li>
            </ul>
          </div>
          <div class="guide-item">
            <div class="guide-icon">📈</div>
            <h4>Degrés de liberté (ddl)</h4>
            <p>ddl = (lignes - 1) × (colonnes - 1)</p>
            <p>Plus les ddl sont élevés, plus le χ² critique est grand pour rejeter H₀.</p>
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

    .explanation-card {
      background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
    }

    .explanation-card h3 {
      font-size: 1.1rem;
      font-weight: 600;
      color: #1565c0;
      margin-bottom: 12px;
    }

    .explanation-card p {
      color: #333;
      line-height: 1.6;
      margin-bottom: 12px;
    }

    .formula {
      display: flex;
      flex-direction: column;
      gap: 8px;
      background: white;
      padding: 16px;
      border-radius: 8px;
      margin: 16px 0;
      font-family: 'Courier New', monospace;
    }

    .formula-text {
      color: #1565c0;
      font-weight: 500;
    }

    .results-section {
      margin-bottom: 24px;
    }

    .results-title {
      font-size: 1.2rem;
      font-weight: 600;
      color: #333;
      margin-bottom: 16px;
    }

    .results-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 20px;
    }

    .result-card {
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      border-left: 4px solid #9e9e9e;
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .result-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }

    .result-card.significant {
      border-left-color: #4caf50;
    }

    .result-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      gap: 12px;
    }

    .result-test {
      font-size: 1rem;
      font-weight: 600;
      color: #1a1a1a;
      margin: 0;
    }

    .result-badge {
      padding: 4px 12px;
      border-radius: 16px;
      font-size: 0.75rem;
      font-weight: 600;
      background: #f5f5f5;
      color: #666;
      white-space: nowrap;
    }

    .result-badge.significant {
      background: #e8f5e9;
      color: #2e7d32;
    }

    .result-description {
      font-size: 0.85rem;
      color: #666;
      margin-bottom: 16px;
      line-height: 1.5;
    }

    .result-stats {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 16px;
    }

    .stat-item {
      text-align: center;
      padding: 8px;
      background: #f5f7fa;
      border-radius: 8px;
    }

    .stat-label {
      display: block;
      font-size: 0.7rem;
      color: #666;
      text-transform: uppercase;
      margin-bottom: 4px;
    }

    .stat-value {
      display: block;
      font-size: 0.95rem;
      font-weight: 600;
      color: #333;
    }

    .stat-value.significant {
      color: #2e7d32;
    }

    .result-conclusion {
      display: flex;
      align-items: flex-start;
      gap: 8px;
      padding: 12px;
      background: #fafafa;
      border-radius: 8px;
      margin-bottom: 12px;
    }

    .conclusion-icon {
      font-size: 1rem;
      color: #4caf50;
    }

    .result-card:not(.significant) .conclusion-icon {
      color: #9e9e9e;
    }

    .conclusion-text {
      font-size: 0.85rem;
      color: #333;
      line-height: 1.5;
    }

    .cramer-bar {
      position: relative;
      height: 8px;
      background: #e0e0e0;
      border-radius: 4px;
      overflow: hidden;
    }

    .cramer-fill {
      height: 100%;
      background: linear-gradient(90deg, #4caf50, #8bc34a);
      border-radius: 4px;
      transition: width 0.5s ease;
    }

    .cramer-label {
      position: absolute;
      right: 0;
      top: -18px;
      font-size: 0.65rem;
      color: #999;
    }

    .guide-section {
      background: white;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .guide-title {
      font-size: 1.1rem;
      font-weight: 600;
      color: #333;
      margin-bottom: 20px;
    }

    .guide-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 24px;
    }

    .guide-item {
      padding: 16px;
      background: #f5f7fa;
      border-radius: 8px;
    }

    .guide-icon {
      font-size: 1.5rem;
      margin-bottom: 8px;
    }

    .guide-item h4 {
      font-size: 0.95rem;
      font-weight: 600;
      color: #333;
      margin-bottom: 12px;
    }

    .guide-item ul {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    .guide-item li {
      font-size: 0.85rem;
      color: #666;
      padding: 4px 0;
    }

    .guide-item p {
      font-size: 0.85rem;
      color: #666;
      margin: 8px 0;
    }

    @media (max-width: 768px) {
      .results-grid {
        grid-template-columns: 1fr;
      }

      .result-stats {
        grid-template-columns: repeat(2, 1fr);
      }
    }
  `]
})
export class Chi2Component implements OnInit, OnDestroy {
  private dataService = inject(DataService);
  private destroy$ = new Subject<void>();

  chi2Results: Chi2Result[] = [];
  totalTests = 0;
  significantTests = 0;
  strongestAssociation = '';
  strongestV = 0;

  ngOnInit(): void {
    this.dataService.chi2$
      .pipe(takeUntil(this.destroy$))
      .subscribe(results => {
        this.chi2Results = results;
        this.totalTests = results.length;
        this.significantTests = results.filter(r => r.significatif).length;

        // Find strongest association
        const strongest = results.reduce((max, r) =>
          r.cramers_v > max.cramers_v ? r : max,
          { cramers_v: 0, test: '' } as Chi2Result
        );
        this.strongestAssociation = strongest.test?.split(' vs ')[0] || '-';
        this.strongestV = strongest.cramers_v || 0;
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  formatPValue(pValue: number): string {
    if (pValue < 0.001) return '< 0.001 ***';
    if (pValue < 0.01) return pValue.toFixed(4) + ' **';
    if (pValue < 0.05) return pValue.toFixed(4) + ' *';
    return pValue.toFixed(4);
  }
}
