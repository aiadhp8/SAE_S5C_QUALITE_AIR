import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTooltipModule } from '@angular/material/tooltip';

export interface HeatmapCell {
  row: string;
  col: string;
  value: number | null;
  significant?: boolean;
}

@Component({
  selector: 'app-heatmap',
  standalone: true,
  imports: [CommonModule, MatTooltipModule],
  template: `
    <div class="heatmap-container">
      <div class="heatmap-wrapper">
        <!-- Column headers -->
        <div class="heatmap-row header-row">
          <div class="heatmap-cell row-label"></div>
          @for (col of columns; track col) {
            <div class="heatmap-cell col-header"
                 [title]="col"
                 [class.highlighted]="col === highlightedColumn">
              {{ truncateLabel(col) }}
            </div>
          }
        </div>

        <!-- Data rows -->
        @for (row of rows; track row) {
          <div class="heatmap-row">
            <div class="heatmap-cell row-label" [title]="row">{{ truncateLabel(row) }}</div>
            @for (col of columns; track col) {
              <div class="heatmap-cell data-cell"
                   [style.background-color]="getCellColor(row, col)"
                   [matTooltip]="getCellTooltip(row, col)"
                   [class.significant]="isCellSignificant(row, col)"
                   [class.highlighted]="col === highlightedColumn">
                {{ formatCellValue(row, col) }}
              </div>
            }
          </div>
        }
      </div>

      <!-- Legend -->
      <div class="heatmap-legend">
        <span class="legend-label">-1</span>
        <div class="legend-gradient"></div>
        <span class="legend-label">+1</span>
      </div>
    </div>
  `,
  styles: [`
    .heatmap-container {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .heatmap-wrapper {
      overflow-x: auto;
    }

    .heatmap-row {
      display: flex;
    }

    .heatmap-cell {
      min-width: 60px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.75rem;
      border: 1px solid #e0e0e0;
    }

    .row-label {
      min-width: 120px;
      justify-content: flex-end;
      padding-right: 8px;
      background: #fafafa;
      font-weight: 500;
      color: #333;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .col-header {
      writing-mode: vertical-rl;
      text-orientation: mixed;
      transform: rotate(180deg);
      height: 80px;
      min-width: 36px;
      background: #fafafa;
      font-weight: 500;
      color: #333;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .header-row .heatmap-cell:first-child {
      min-width: 120px;
    }

    .data-cell {
      min-width: 36px;
      color: white;
      font-weight: 500;
      text-shadow: 0 1px 2px rgba(0,0,0,0.3);
      transition: transform 0.2s;
      cursor: pointer;
    }

    .data-cell:hover {
      transform: scale(1.1);
      z-index: 1;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    .data-cell.significant {
      border: 2px solid #333;
    }

    .data-cell.highlighted {
      outline: 3px solid #000;
      outline-offset: -3px;
      z-index: 2;
    }

    .col-header.highlighted {
      background: #333;
      color: white;
      font-weight: 700;
    }

    .heatmap-legend {
      display: flex;
      align-items: center;
      gap: 8px;
      justify-content: center;
    }

    .legend-label {
      font-size: 0.8rem;
      color: #666;
    }

    .legend-gradient {
      width: 200px;
      height: 16px;
      border-radius: 4px;
      background: linear-gradient(to right,
        #d32f2f 0%,
        #ff9800 25%,
        #fff9c4 50%,
        #4caf50 75%,
        #1b5e20 100%
      );
    }
  `]
})
export class HeatmapComponent implements OnChanges {
  @Input() data: HeatmapCell[] = [];
  @Input() rows: string[] = [];
  @Input() columns: string[] = [];
  @Input() highlightedColumn: string = '';

  private dataMap = new Map<string, HeatmapCell>();

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['data']) {
      this.buildDataMap();
    }
  }

  private buildDataMap(): void {
    this.dataMap.clear();
    this.data.forEach(cell => {
      this.dataMap.set(`${cell.row}|${cell.col}`, cell);
    });
  }

  private getCell(row: string, col: string): HeatmapCell | undefined {
    return this.dataMap.get(`${row}|${col}`);
  }

  getCellColor(row: string, col: string): string {
    const cell = this.getCell(row, col);
    if (!cell || cell.value === null) return '#e0e0e0';

    const value = cell.value;
    // Échelle de couleurs: rouge négatif, jaune neutre, vert positif
    if (value < -0.5) return '#d32f2f';
    if (value < -0.25) return '#ff9800';
    if (value < 0.25) return '#fff9c4';
    if (value < 0.5) return '#4caf50';
    return '#1b5e20';
  }

  formatCellValue(row: string, col: string): string {
    const cell = this.getCell(row, col);
    if (!cell || cell.value === null) return '-';
    return cell.value.toFixed(2);
  }

  getCellTooltip(row: string, col: string): string {
    const cell = this.getCell(row, col);
    if (!cell || cell.value === null) return 'Données non disponibles';
    const sig = cell.significant ? ' (significatif)' : '';
    return `${row} × ${col}: ρ = ${cell.value.toFixed(3)}${sig}`;
  }

  isCellSignificant(row: string, col: string): boolean {
    const cell = this.getCell(row, col);
    return cell?.significant || false;
  }

  truncateLabel(label: string): string {
    if (label.length > 15) {
      return label.substring(0, 12) + '...';
    }
    return label;
  }
}
