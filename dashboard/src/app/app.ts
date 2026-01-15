import { Component, OnInit, ViewChild, inject, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { provideHttpClient } from '@angular/common/http';

import { NavbarComponent } from './components/navbar/navbar.component';
import { FilterBarComponent } from './components/filter-bar/filter-bar.component';
import { AccueilComponent } from './components/sections/accueil/accueil.component';
import { TendancesComponent } from './components/sections/tendances/tendances.component';
import { FacteursComponent } from './components/sections/facteurs/facteurs.component';
import { Chi2Component } from './components/sections/chi2/chi2.component';
import { AcpComponent } from './components/sections/acp/acp.component';
import { PredictionComponent } from './components/sections/prediction/prediction.component';
import { QualiteComponent } from './components/sections/qualite/qualite.component';
import { DataService } from './services/data.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    NavbarComponent,
    FilterBarComponent,
    AccueilComponent,
    TendancesComponent,
    FacteursComponent,
    Chi2Component,
    AcpComponent,
    PredictionComponent,
    QualiteComponent
  ],
  template: `
    @if (loading) {
      <div class="loading-screen">
        <div class="loader">
          <div class="loader-spinner"></div>
          <h2>Chargement du dashboard...</h2>
          <p>Analyse de la qualité de l'air mondiale</p>
        </div>
      </div>
    } @else {
      <app-navbar #navbar></app-navbar>

      <main class="main-content">
        <div class="hero-section">
          <h1>Analyse de la Qualité de l'Air</h1>
          <p>SAE S5.C.01 - Étude des facteurs urbains et socio-économiques</p>
          <p class="team">Equipe Piltdown</p>
        </div>

        <div class="filter-bar-container">
          <app-filter-bar></app-filter-bar>
        </div>

        <app-accueil></app-accueil>
        <app-tendances></app-tendances>
        <app-facteurs></app-facteurs>
        <app-chi2></app-chi2>
        <app-acp></app-acp>
        <app-prediction></app-prediction>
        <app-qualite></app-qualite>

        <footer class="footer">
          <p>Dashboard réalisé avec Angular & Chart.js | Données: OpenAQ & World Bank</p>
          <p>SAE S5.C.01 - Janvier 2026</p>
        </footer>
      </main>
    }
  `,
  styles: [`
    :host {
      display: block;
      min-height: 100vh;
      background: #f5f7fa;
    }

    .loading-screen {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9999;
    }

    .loader {
      text-align: center;
      color: white;
    }

    .loader-spinner {
      width: 60px;
      height: 60px;
      border: 4px solid rgba(255,255,255,0.3);
      border-top-color: white;
      border-radius: 50%;
      margin: 0 auto 24px;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .loader h2 {
      font-size: 1.5rem;
      margin-bottom: 8px;
    }

    .loader p {
      opacity: 0.8;
    }

    .main-content {
      padding-top: 64px;
      max-width: 1400px;
      margin: 0 auto;
    }

    .hero-section {
      background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
      color: white;
      padding: 48px 32px;
      text-align: center;
    }

    .filter-bar-container {
      position: sticky;
      top: 64px;
      z-index: 100;
      background: #f5f7fa;
      padding: 16px 24px;
      margin: 0 -24px;
      padding-left: 24px;
      padding-right: 24px;
    }

    .hero-section h1 {
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 8px;
    }

    .hero-section p {
      font-size: 1.1rem;
      opacity: 0.9;
    }

    .hero-section .team {
      margin-top: 16px;
      font-weight: 600;
      font-size: 1.2rem;
      opacity: 1;
    }

    .footer {
      text-align: center;
      padding: 32px;
      color: #666;
      font-size: 0.85rem;
      border-top: 1px solid #e0e0e0;
      margin-top: 48px;
    }

    .footer p {
      margin: 4px 0;
    }
  `]
})
export class App implements OnInit {
  @ViewChild('navbar') navbar!: NavbarComponent;

  private dataService = inject(DataService);
  loading = true;

  private sectionIds = ['accueil', 'tendances', 'facteurs', 'chi2', 'acp', 'prediction', 'qualite'];

  ngOnInit(): void {
    this.dataService.loadAllData().subscribe({
      next: () => {
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading data:', err);
        this.loading = false;
      }
    });
  }

  @HostListener('window:scroll')
  onScroll(): void {
    if (!this.navbar) return;

    const scrollPos = window.scrollY + 100;

    for (let i = this.sectionIds.length - 1; i >= 0; i--) {
      const section = document.getElementById(this.sectionIds[i]);
      if (section && section.offsetTop <= scrollPos) {
        this.navbar.setActiveSection(this.sectionIds[i]);
        break;
      }
    }
  }
}
