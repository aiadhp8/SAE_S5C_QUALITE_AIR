import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData } from 'chart.js';

export interface DoughnutData {
  label: string;
  value: number;
  color?: string;
}

@Component({
  selector: 'app-doughnut-chart',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  template: `
    <div class="chart-container">
      <canvas baseChart
        [data]="chartData"
        [options]="chartOptions"
        [type]="'doughnut'">
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
export class DoughnutChartComponent implements OnChanges {
  @Input() data: DoughnutData[] = [];
  @Input() title = '';
  @Input() centerText = '';

  chartData: ChartData<'doughnut'> = {
    labels: [],
    datasets: []
  };

  chartOptions: ChartConfiguration<'doughnut'>['options'] = {
    responsive: true,
    maintainAspectRatio: true,
    cutout: '60%',
    plugins: {
      legend: {
        display: true,
        position: 'right'
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
            const value = context.parsed;
            const pct = ((value / total) * 100).toFixed(1);
            return `${context.label}: ${value.toLocaleString()} (${pct}%)`;
          }
        }
      }
    }
  };

  private defaultColors = [
    '#1976d2', '#4caf50', '#ff9800', '#f44336',
    '#9c27b0', '#00bcd4', '#795548', '#607d8b',
    '#e91e63', '#3f51b5'
  ];

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['data']) {
      this.updateChart();
    }
  }

  private updateChart(): void {
    if (!this.data || this.data.length === 0) return;

    const colors = this.data.map((d, i) => d.color || this.defaultColors[i % this.defaultColors.length]);

    this.chartData = {
      labels: this.data.map(d => d.label),
      datasets: [{
        data: this.data.map(d => d.value),
        backgroundColor: colors,
        borderColor: colors.map(c => c),
        borderWidth: 2,
        hoverOffset: 8
      }]
    };
  }
}
