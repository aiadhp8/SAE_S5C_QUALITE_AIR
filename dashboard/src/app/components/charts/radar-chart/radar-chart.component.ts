import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData } from 'chart.js';

export interface RadarDataset {
  label: string;
  data: number[];
  color?: string;
}

@Component({
  selector: 'app-radar-chart',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  template: `
    <div class="chart-container">
      <canvas baseChart
        [data]="chartData"
        [options]="chartOptions"
        [type]="'radar'">
      </canvas>
    </div>
  `,
  styles: [`
    .chart-container {
      position: relative;
      width: 100%;
      height: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    canvas {
      max-width: 100%;
      max-height: 100%;
    }
  `]
})
export class RadarChartComponent implements OnChanges {
  @Input() labels: string[] = [];
  @Input() datasets: RadarDataset[] = [];
  @Input() title = '';

  chartData: ChartData<'radar'> = {
    labels: [],
    datasets: []
  };

  chartOptions: ChartConfiguration<'radar'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          font: {
            size: 14
          }
        }
      }
    },
    scales: {
      r: {
        beginAtZero: true,
        ticks: {
          stepSize: 20,
          font: {
            size: 12
          }
        },
        pointLabels: {
          font: {
            size: 14
          }
        }
      }
    }
  };

  private defaultColors = [
    { bg: 'rgba(25, 118, 210, 0.2)', border: '#1976d2' },
    { bg: 'rgba(76, 175, 80, 0.2)', border: '#4caf50' },
    { bg: 'rgba(255, 152, 0, 0.2)', border: '#ff9800' },
    { bg: 'rgba(244, 67, 54, 0.2)', border: '#f44336' }
  ];

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['labels'] || changes['datasets']) {
      this.updateChart();
    }
  }

  private updateChart(): void {
    if (!this.datasets || this.datasets.length === 0) return;

    this.chartData = {
      labels: this.labels,
      datasets: this.datasets.map((ds, i) => {
        const colors = this.defaultColors[i % this.defaultColors.length];
        return {
          label: ds.label,
          data: ds.data,
          backgroundColor: ds.color ? `${ds.color}33` : colors.bg,
          borderColor: ds.color || colors.border,
          borderWidth: 2,
          pointBackgroundColor: ds.color || colors.border,
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: ds.color || colors.border
        };
      })
    };
  }
}
