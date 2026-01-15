import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';
import { FilterService } from '../../services/filter.service';
import { Pollutant, POLLUTANTS } from '../../models/types';

@Component({
  selector: 'app-filter-bar',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonToggleModule,
    MatSelectModule,
    MatFormFieldModule,
    MatIconModule,
    FormsModule
  ],
  template: `
    <div class="filter-bar">
      <div class="filter-group">
        <label class="filter-label">
          <mat-icon>science</mat-icon>
          Polluant
        </label>
        <mat-button-toggle-group
          [value]="filterService.currentFilters.pollutant"
          (change)="onPollutantChange($event.value)">
          @for (p of pollutants; track p.code) {
            <mat-button-toggle [value]="p.code">
              {{ p.label }}
            </mat-button-toggle>
          }
        </mat-button-toggle-group>
      </div>

      <div class="filter-group">
        <label class="filter-label">
          <mat-icon>calendar_today</mat-icon>
          Année
        </label>
        <mat-button-toggle-group
          [value]="filterService.currentFilters.year"
          (change)="onYearChange($event.value)">
          <mat-button-toggle value="all">Toutes</mat-button-toggle>
          @for (year of years; track year) {
            <mat-button-toggle [value]="year">{{ year }}</mat-button-toggle>
          }
        </mat-button-toggle-group>
      </div>

      <div class="filter-group">
        <label class="filter-label">
          <mat-icon>functions</mat-icon>
          Statistique
        </label>
        <mat-button-toggle-group
          [value]="filterService.currentFilters.stat"
          (change)="onStatChange($event.value)">
          <mat-button-toggle value="median">Médiane</mat-button-toggle>
          <mat-button-toggle value="average">Moyenne</mat-button-toggle>
        </mat-button-toggle-group>
      </div>
    </div>
  `,
  styles: [`
    .filter-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 24px;
      padding: 16px 24px;
      background: white;
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.12);
    }

    .filter-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .filter-label {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.8rem;
      color: #666;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .filter-label mat-icon {
      font-size: 16px;
      width: 16px;
      height: 16px;
    }

    mat-button-toggle-group {
      border-radius: 8px;
      overflow: hidden;
    }

    ::ng-deep .mat-button-toggle-appearance-standard {
      background: #f5f5f5;
    }

    ::ng-deep .mat-button-toggle-checked {
      background: #1976d2 !important;
      color: white !important;
    }

    ::ng-deep .mat-button-toggle-label-content {
      padding: 0 12px !important;
      font-size: 0.85rem;
    }

    @media (max-width: 768px) {
      .filter-bar {
        flex-direction: column;
        gap: 16px;
      }

      .filter-group {
        width: 100%;
      }

      mat-button-toggle-group {
        width: 100%;
        display: flex;
      }

      ::ng-deep .mat-button-toggle {
        flex: 1;
      }
    }
  `]
})
export class FilterBarComponent {
  filterService = inject(FilterService);

  pollutants = POLLUTANTS;
  years = [2018, 2019, 2020, 2021, 2022, 2023];

  onPollutantChange(pollutant: Pollutant): void {
    this.filterService.setPollutant(pollutant);
  }

  onYearChange(year: number | 'all'): void {
    this.filterService.setYear(year);
  }

  onStatChange(stat: 'median' | 'average'): void {
    this.filterService.setStat(stat);
  }
}
