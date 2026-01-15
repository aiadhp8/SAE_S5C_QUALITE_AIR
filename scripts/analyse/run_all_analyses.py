"""
Script Principal - Exécute toutes les analyses
===============================================
Lance tous les scripts d'analyse dans l'ordre.
"""

import sys
import os
sys.path.append(str(__file__).rsplit('scripts', 1)[0])

from pathlib import Path

def run_script(script_name):
    """Exécute un script d'analyse."""
    print("\n" + "#" * 70)
    print(f"# EXÉCUTION: {script_name}")
    print("#" * 70)

    script_path = Path(__file__).parent / script_name
    if script_path.exists():
        # Passer __file__ au contexte pour que les scripts puissent l'utiliser
        exec(open(script_path, encoding='utf-8').read(), {
            '__name__': '__main__',
            '__file__': str(script_path)
        })
        return True
    else:
        print(f"Script non trouvé: {script_path}")
        return False

def main():
    print("=" * 70)
    print("ANALYSE COMPLÈTE - QUALITÉ DE L'AIR")
    print("=" * 70)
    print("""
    Ce script exécute toutes les analyses dans l'ordre:
    1. Fusion des données
    2. Questions méthodologiques (Q1-Q3)
    3. Analyses descriptives (Q4-Q10)
    4. Corrélations socio-économiques (Q11-Q15)
    5. Analyse en Composantes Principales (Q16-Q18)
    6. Graphes de similarité (Q19-Q21)
    7. Modèles prédictifs (Q22-Q24)
    8. Qualité et limites (Q25-Q27)
    """)

    scripts = [
        "00_fusion_complete.py",
        "01_methodologie.py",
        "02_descriptives.py",
        "03_correlations_socioeco.py",
        "04_acp.py",
        "05_graphes_similarite.py",
        "06_modeles_predictifs.py",
        "07_qualite_limites.py"
    ]

    success = 0
    failed = 0

    for script in scripts:
        try:
            if run_script(script):
                success += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n[ERREUR] dans {script}: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print("RÉSUMÉ")
    print("=" * 70)
    print(f"  Scripts réussis: {success}/{len(scripts)}")
    print(f"  Scripts échoués: {failed}/{len(scripts)}")

    print("\n  Fichiers générés:")
    print("  - data/cleaned/base_analyse_complete.csv")
    print("  - data/cleaned/base_analyse_fr.csv")
    print("  - reports/figures/*.png")

    print("\n" + "=" * 70)
    print("ANALYSE TERMINÉE")
    print("=" * 70)

if __name__ == "__main__":
    main()
