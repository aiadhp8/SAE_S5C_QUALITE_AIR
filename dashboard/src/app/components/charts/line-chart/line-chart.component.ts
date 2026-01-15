import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData } from 'chart.js';

export interface LineChartSeries {
  label: string;
  data: number[];
  color?: string;
  fill?: boolean;
}

@Component({
  selector: 'app-line-chart',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  template: `
    <div class="chart-container">
      <canvas baseChart
        [data]="chartData"
        [options]="chartOptions"
        [type]="'line'">
      </canvas>
    </div>
  `,
  styles: [`
    .chart-container {
      position: relative;
      width: 100%;
      height: 250px;
    }
  `]
})
export class LineChartComponent implements OnChanges {
  @Input() labels: string[] = [];
  @Input() series: LineChartSeries[] = [];
  @Input() title = '';
  @Input() unit = '';
  @Input() showLegend = true;

  chartData: ChartData<'line'> = {
    labels: [],
    datasets: []
  };

  chartOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    maintainAspectRatio: true,
    interaction: {
      intersect: false,
      mode: 'index'
    },
    plugins: {
      legend: {
        display: true,
        position: 'top'
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            return `${context.dataset.label}: ${(context.parsed.y ?? 0).toFixed(1)} ${this.unit}`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        }
      },
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(0,0,0,0.05)'
        }
      }
    }
  };

  private defaultColors = [
    '#1976d2', '#4caf50', '#ff9800', '#f44336',
    '#9c27b0', '#00bcd4', '#795548', '#607d8b'
  ];

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['labels'] || changes['series']) {
      this.updateChart();
    }
  }

  private updateChart(): void {
    if (!this.series || this.series.length === 0) return;

    this.chartData = {
      labels: this.labels,
      datasets: this.series.map((s, i) => ({
        label: s.label,
        data: s.data,
        borderColor: s.color || this.defaultColors[i % this.defaultColors.length],
        backgroundColor: s.fill
          ? (s.color || this.defaultColors[i % this.defaultColors.length]).replace(')', ', 0.1)')
          : 'transparent',
        fill: s.fill || false,
        tension: 0.3,
        pointRadius: 4,
        pointHoverRadius: 6
      }))
    };

    this.chartOptions = {
      ...this.chartOptions,
      plugins: {
        ...this.chartOptions!.plugins,
        legend: {
          display: this.showLegend,
          position: 'top'
        }
      }
    };
  }
}
