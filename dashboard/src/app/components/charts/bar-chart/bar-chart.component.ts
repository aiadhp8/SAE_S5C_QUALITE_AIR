import { Component, Input, OnChanges, SimpleChanges, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData } from 'chart.js';

export interface BarChartData {
  label: string;
  value: number;
  color?: string;
}

@Component({
  selector: 'app-bar-chart',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  template: `
    <div class="chart-container">
      <canvas baseChart
        [data]="chartData"
        [options]="chartOptions"
        [type]="'bar'">
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
export class BarChartComponent implements OnChanges {
  @Input() data: BarChartData[] = [];
  @Input() title = '';
  @Input() horizontal = true;
  @Input() unit = '';
  @Input() showValues = true;

  chartData: ChartData<'bar'> = {
    labels: [],
    datasets: []
  };

  chartOptions: ChartConfiguration<'bar'>['options'] = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const value = context.parsed.x ?? context.parsed.y ?? 0;
            return `${value.toFixed(1)} ${this.unit}`;
          }
        }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        grid: {
          display: true,
          color: 'rgba(0,0,0,0.05)'
        }
      },
      y: {
        grid: {
          display: false
        }
      }
    }
  };

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['data'] || changes['horizontal']) {
      this.updateChart();
    }
  }

  private updateChart(): void {
    if (!this.data || this.data.length === 0) return;

    const labels = this.data.map(d => d.label);
    const values = this.data.map(d => d.value);
    const colors = this.data.map(d => d.color || this.getColorForValue(d.value));

    this.chartData = {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderColor: colors.map(c => c.replace('0.8', '1')),
        borderWidth: 1,
        borderRadius: 4,
        barThickness: 20
      }]
    };

    this.chartOptions = {
      ...this.chartOptions,
      indexAxis: this.horizontal ? 'y' : 'x'
    };
  }

  private getColorForValue(value: number): string {
    // Gradient de couleurs basé sur la valeur
    const maxValue = Math.max(...this.data.map(d => d.value));
    const ratio = value / maxValue;

    if (ratio < 0.25) return 'rgba(76, 175, 80, 0.8)';    // Vert
    if (ratio < 0.5) return 'rgba(255, 235, 59, 0.8)';    // Jaune
    if (ratio < 0.75) return 'rgba(255, 152, 0, 0.8)';    // Orange
    return 'rgba(244, 67, 54, 0.8)';                       // Rouge
  }
}
