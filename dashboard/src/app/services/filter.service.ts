import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { FilterState, Pollutant } from '../models/types';

@Injectable({
  providedIn: 'root'
})
export class FilterService {
  private filterState = new BehaviorSubject<FilterState>({
    pollutant: 'pm25',
    year: 'all',
    stat: 'median'
  });

  filters$ = this.filterState.asObservable();

  get currentFilters(): FilterState {
    return this.filterState.value;
  }

  setPollutant(pollutant: Pollutant): void {
    this.filterState.next({
      ...this.filterState.value,
      pollutant
    });
  }

  setYear(year: number | 'all'): void {
    this.filterState.next({
      ...this.filterState.value,
      year
    });
  }

  setStat(stat: 'median' | 'average'): void {
    this.filterState.next({
      ...this.filterState.value,
      stat
    });
  }

  setFilters(filters: Partial<FilterState>): void {
    this.filterState.next({
      ...this.filterState.value,
      ...filters
    });
  }
}
