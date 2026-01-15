import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

interface NavItem {
  id: string;
  label: string;
  icon: string;
}

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, MatToolbarModule, MatButtonModule, MatIconModule],
  template: `
    <mat-toolbar class="navbar">
      <div class="logo">
        <mat-icon>air</mat-icon>
        <span class="title">Air Quality Dashboard</span>
      </div>

      <nav class="nav-links">
        @for (item of navItems; track item.id) {
          <button mat-button
                  [class.active]="activeSection === item.id"
                  (click)="scrollTo(item.id)">
            <mat-icon>{{ item.icon }}</mat-icon>
            <span class="nav-label">{{ item.label }}</span>
          </button>
        }
      </nav>

      <div class="nav-info">
        <span class="badge">94 pays</span>
        <span class="badge">2018-2023</span>
      </div>
    </mat-toolbar>
  `,
  styles: [`
    .navbar {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 1000;
      background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
      color: white;
      padding: 0 24px;
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .logo mat-icon {
      font-size: 28px;
      width: 28px;
      height: 28px;
    }

    .title {
      font-size: 1.2rem;
      font-weight: 600;
      letter-spacing: 0.5px;
    }

    .nav-links {
      display: flex;
      gap: 4px;
    }

    .nav-links button {
      color: rgba(255,255,255,0.85);
      border-radius: 8px;
      transition: all 0.2s;
    }

    .nav-links button:hover {
      color: white;
      background: rgba(255,255,255,0.1);
    }

    .nav-links button.active {
      color: white;
      background: rgba(255,255,255,0.2);
    }

    .nav-links mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
      margin-right: 6px;
    }

    .nav-label {
      font-size: 0.85rem;
      text-transform: none;
    }

    .nav-info {
      display: flex;
      gap: 8px;
    }

    .badge {
      background: rgba(255,255,255,0.15);
      padding: 4px 12px;
      border-radius: 16px;
      font-size: 0.8rem;
      font-weight: 500;
    }

    @media (max-width: 1200px) {
      .nav-label {
        display: none;
      }
      .nav-links button {
        min-width: 40px;
        padding: 0 8px;
      }
    }

    @media (max-width: 768px) {
      .title {
        display: none;
      }
      .nav-info {
        display: none;
      }
    }
  `]
})
export class NavbarComponent {
  @Output() sectionChange = new EventEmitter<string>();

  activeSection = 'accueil';

  navItems: NavItem[] = [
    { id: 'accueil', label: 'Accueil', icon: 'dashboard' },
    { id: 'tendances', label: 'Tendances', icon: 'trending_up' },
    { id: 'facteurs', label: 'Facteurs', icon: 'analytics' },
    { id: 'chi2', label: 'Chi²', icon: 'grid_on' },
    { id: 'acp', label: 'ACP', icon: 'scatter_plot' },
    { id: 'prediction', label: 'Prédiction', icon: 'psychology' },
    { id: 'qualite', label: 'Qualité', icon: 'verified' }
  ];

  scrollTo(sectionId: string): void {
    this.activeSection = sectionId;
    this.sectionChange.emit(sectionId);

    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  setActiveSection(sectionId: string): void {
    this.activeSection = sectionId;
  }
}
