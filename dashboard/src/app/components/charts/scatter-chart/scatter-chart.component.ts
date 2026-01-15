import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData, Point } from 'chart.js';

export interface ScatterPoint {
  x: number;
  y: number;
  label?: string;
  size?: number;
  color?: string;
}

@Component({
  selector: 'app-scatter-chart',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  template: `
    <div class="chart-container">
      <canvas baseChart
        [data]="chartData"
        [options]="chartOptions"
        [type]="'scatter'">
      </canvas>
    </div>
  `,
  styles: [`
    .chart-container {
      position: relative;
      width: 100%;
      height: 300px;
    }
  `]
})
export class ScatterChartComponent implements OnChanges {
  @Input() points: ScatterPoint[] = [];
  @Input() xLabel = 'X';
  @Input() yLabel = 'Y';
  @Input() title = '';
  @Input() showTrendline = false;

  chartData: ChartData<'scatter'> = {
    datasets: []
  };

  chartOptions: ChartConfiguration<'scatter'>['options'] = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const point = this.points[context.dataIndex];
            const label = point?.label || '';
            return `${label}: (${(context.parsed.x ?? 0).toFixed(1)}, ${(context.parsed.y ?? 0).toFixed(1)})`;
          }
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: ''
        },
        grid: {
          color: 'rgba(0,0,0,0.05)'
        }
      },
      y: {
        title: {
          display: true,
          text: ''
        },
        grid: {
          color: 'rgba(0,0,0,0.05)'
        }
      }
    }
  };

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['points'] || changes['xLabel'] || changes['yLabel']) {
      this.updateChart();
    }
  }

  private updateChart(): void {
    if (!this.points || this.points.length === 0) return;

    const datasets: ChartData<'scatter'>['datasets'] = [{
      data: this.points.map(p => ({ x: p.x, y: p.y })),
      pointBackgroundColor: this.points.map(p => p.color || 'rgba(25, 118, 210, 0.7)'),
      pointBorderColor: this.points.map(p => p.color?.replace('0.7', '1') || '#1976d2'),
      pointRadius: this.points.map(p => p.size || 6),
      pointHoverRadius: this.points.map(p => (p.size || 6) + 2)
    }];

    // Add trendline if requested
    if (this.showTrendline && this.points.length > 2) {
      const trendline = this.calculateTrendline();
      datasets.push({
        data: trendline,
        type: 'line' as any,
        borderColor: 'rgba(244, 67, 54, 0.5)',
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false
      } as any);
    }

    this.chartData = { datasets };

    this.chartOptions = {
      ...this.chartOptions,
      scales: {
        x: {
          ...this.chartOptions!.scales!['x'],
          title: {
            display: true,
            text: this.xLabel,
            font: { weight: 'bold' }
          }
        },
        y: {
          ...this.chartOptions!.scales!['y'],
          title: {
            display: true,
            text: this.yLabel,
            font: { weight: 'bold' }
          }
        }
      }
    };
  }

  private calculateTrendline(): Point[] {
    const n = this.points.length;
    const sumX = this.points.reduce((s, p) => s + p.x, 0);
    const sumY = this.points.reduce((s, p) => s + p.y, 0);
    const sumXY = this.points.reduce((s, p) => s + p.x * p.y, 0);
    const sumX2 = this.points.reduce((s, p) => s + p.x * p.x, 0);

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;

    const minX = Math.min(...this.points.map(p => p.x));
    const maxX = Math.max(...this.points.map(p => p.x));

    return [
      { x: minX, y: slope * minX + intercept },
      { x: maxX, y: slope * maxX + intercept }
    ];
  }
}
