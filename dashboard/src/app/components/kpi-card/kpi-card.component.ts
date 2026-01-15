import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

@Component({
  selector: 'app-kpi-card',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, MatTooltipModule],
  template: `
    <mat-card class="kpi-card" [class.highlight]="highlight" [class.warning]="warning">
      <div class="kpi-header">
        <mat-icon *ngIf="icon" class="kpi-icon">{{ icon }}</mat-icon>
        <span class="kpi-label">{{ label }}</span>
        <mat-icon *ngIf="tooltip" class="info-icon" [matTooltip]="tooltip">info_outline</mat-icon>
      </div>
      <div class="kpi-value">
        <span class="value">{{ formattedValue }}</span>
        <span class="unit" *ngIf="unit">{{ unit }}</span>
      </div>
      <div class="kpi-subtitle" *ngIf="subtitle">{{ subtitle }}</div>
      <div class="kpi-trend" *ngIf="trend !== null">
        <mat-icon [class.positive]="trend > 0" [class.negative]="trend < 0">
          {{ trend > 0 ? 'trending_up' : trend < 0 ? 'trending_down' : 'trending_flat' }}
        </mat-icon>
        <span [class.positive]="trend > 0" [class.negative]="trend < 0">
          {{ trend > 0 ? '+' : '' }}{{ trend | number:'1.1-1' }}%
        </span>
      </div>
    </mat-card>
  `,
  styles: [`
    .kpi-card {
      padding: 16px 20px;
      border-radius: 12px;
      background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
      border-left: 4px solid #1976d2;
      transition: transform 0.2s, box-shadow 0.2s;
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    .kpi-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .kpi-card.highlight {
      border-left-color: #4caf50;
      background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%);
    }

    .kpi-card.warning {
      border-left-color: #f44336;
      background: linear-gradient(135deg, #ffebee 0%, #fce4ec 100%);
    }

    .kpi-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
    }

    .kpi-icon {
      color: #1976d2;
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .kpi-label {
      font-size: 0.85rem;
      color: #666;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      flex: 1;
    }

    .info-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
      color: #999;
      cursor: help;
    }

    .kpi-value {
      display: flex;
      align-items: baseline;
      gap: 6px;
      margin-bottom: 4px;
    }

    .value {
      font-size: 2rem;
      font-weight: 700;
      color: #1a1a1a;
      line-height: 1.2;
    }

    .unit {
      font-size: 0.9rem;
      color: #666;
      font-weight: 500;
    }

    .kpi-subtitle {
      font-size: 0.8rem;
      color: #888;
      margin-top: auto;
    }

    .kpi-trend {
      display: flex;
      align-items: center;
      gap: 4px;
      margin-top: 8px;
      font-size: 0.85rem;
      font-weight: 500;
    }

    .kpi-trend mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
    }

    .positive {
      color: #4caf50;
    }

    .negative {
      color: #f44336;
    }
  `]
})
export class KpiCardComponent {
  @Input() label = '';
  @Input() value: number | string | null = null;
  @Input() unit = '';
  @Input() icon = '';
  @Input() subtitle = '';
  @Input() tooltip = '';
  @Input() trend: number | null = null;
  @Input() highlight = false;
  @Input() warning = false;
  @Input() decimals = 1;

  get formattedValue(): string {
    if (this.value === null || this.value === undefined) {
      return '-';
    }
    if (typeof this.value === 'string') {
      return this.value;
    }
    if (Number.isInteger(this.value)) {
      return this.value.toLocaleString('fr-FR');
    }
    return this.value.toLocaleString('fr-FR', {
      minimumFractionDigits: this.decimals,
      maximumFractionDigits: this.decimals
    });
  }
}
