"""
SAE S5.C.01 - Analyse de la Qualite de l'Air
=============================================
Point d'entree principal du projet.

Usage:
    python main.py              # Menu interactif
    python main.py --all        # Execution complete automatique
    python main.py --extract    # Extraction des donnees uniquement
    python main.py --analyse    # Analyses statistiques uniquement
    python main.py --status     # Afficher l'etat des donnees
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Configuration des chemins
PROJECT_ROOT = Path(__file__).parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_CLEANED = PROJECT_ROOT / "data" / "cleaned"
DATA_FINAL = PROJECT_ROOT / "data" / "final"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Scripts d'extraction (Phase 1)
# Format: (chemin, description, fichier_a_verifier_ou_None)
EXTRACTION_SCRIPTS = [
    ("scripts/common/01_extract_openaq.py", "Extraction donnees pollution OpenAQ", DATA_RAW / "openaq_country_averages.csv"),
    ("scripts/common/02_extract_world_cities.py", "Extraction donnees villes mondiales", DATA_RAW / "world_cities_by_country.csv"),
    ("scripts/common/worldbank_demo_data.py", "Generation donnees World Bank", DATA_RAW / "worldbank_transport.csv"),
    ("scripts/common/03_base_commune.py", "Creation de la base commune", None),
]

# Scripts de traitement par axe (Phase 2)
AXES_SCRIPTS = [
    ("scripts/axes/axe_transport.py", "Traitement axe Transport", None),
    ("scripts/axes/axe_energie.py", "Traitement axe Energie", None),
    ("scripts/axes/axe_economie.py", "Traitement axe Economie", None),
    ("scripts/axes/axe_demographie.py", "Traitement axe Demographie", None),
    ("scripts/axes/axe_sante.py", "Traitement axe Sante", None),
]

# Scripts d'analyse (Phase 3)
ANALYSE_SCRIPTS = [
    ("scripts/analyse/00_fusion_complete.py", "Fusion complete des donnees", None),
    ("scripts/analyse/01_methodologie.py", "Analyses methodologiques (Q1-Q3)", None),
    ("scripts/analyse/02_descriptives.py", "Analyses descriptives (Q4-Q10)", None),
    ("scripts/analyse/03_correlations_socioeco.py", "Correlations socio-economiques (Q11-Q15)", None),
    ("scripts/analyse/04_acp.py", "Analyse en Composantes Principales (Q16-Q18)", None),
    ("scripts/analyse/05_graphes_similarite.py", "Graphes de similarite (Q19-Q21)", None),
    ("scripts/analyse/06_modeles_predictifs.py", "Modeles predictifs ML (Q22-Q24)", None),
    ("scripts/analyse/07_qualite_limites.py", "Qualite et limites (Q25-Q27)", None),
]


def print_header():
    """Affiche l'en-tete du programme."""
    print("\n" + "=" * 60)
    print("   SAE S5.C.01 - ANALYSE DE LA QUALITE DE L'AIR")
    print("   Facteurs urbains et socio-economiques")
    print("=" * 60)


def print_separator(title=""):
    """Affiche un separateur avec titre optionnel."""
    if title:
        print(f"\n{'─' * 60}")
        print(f"  {title}")
        print(f"{'─' * 60}")
    else:
        print(f"\n{'─' * 60}")


def run_script(script_path, description, skip_if_exists=None):
    """
    Execute un script Python et retourne True si succes.

    Args:
        script_path: Chemin relatif du script
        description: Description de l'etape
        skip_if_exists: Chemin d'un fichier - si existe, le script est ignore

    Returns:
        bool: True si execution reussie
    """
    # Verifier si on peut ignorer ce script
    if skip_if_exists and skip_if_exists.exists():
        print(f"\n  >> {description}")
        print(f"     [IGNORE] Fichier deja present: {skip_if_exists.name}")
        return True

    full_path = PROJECT_ROOT / script_path

    if not full_path.exists():
        print(f"  [ERREUR] Script non trouve: {script_path}")
        return False

    print(f"\n  >> {description}")
    print(f"     Fichier: {script_path}")

    try:
        result = subprocess.run(
            [sys.executable, str(full_path)],
            cwd=str(PROJECT_ROOT),
            capture_output=False,
            text=True
        )

        if result.returncode == 0:
            print(f"  [OK] {description}")
            return True
        else:
            print(f"  [ECHEC] {description} (code: {result.returncode})")
            return False

    except Exception as e:
        print(f"  [ERREUR] {description}: {e}")
        return False


def run_scripts_batch(scripts, batch_name):
    """
    Execute un lot de scripts.

    Args:
        scripts: Liste de tuples (chemin, description, skip_if_exists)
        batch_name: Nom du lot pour l'affichage

    Returns:
        tuple: (succes, echecs)
    """
    print_separator(batch_name)

    success = 0
    failed = 0

    for script_path, description, skip_if_exists in scripts:
        if run_script(script_path, description, skip_if_exists):
            success += 1
        else:
            failed += 1

    return success, failed


def check_data_status():
    """Verifie l'etat des donnees du projet."""
    print_separator("ETAT DES DONNEES")

    # Verifier les dossiers
    folders = [
        (DATA_RAW, "Donnees brutes"),
        (DATA_CLEANED, "Donnees nettoyees"),
        (DATA_FINAL, "Donnees finales"),
        (REPORTS_DIR, "Rapports"),
    ]

    print("\n  Dossiers:")
    for folder, name in folders:
        if folder.exists():
            files = list(folder.glob("*"))
            csv_files = list(folder.glob("*.csv"))
            png_files = list(folder.glob("**/*.png"))
            print(f"    {name}: {len(csv_files)} CSV, {len(png_files)} PNG")
        else:
            print(f"    {name}: [NON CREE]")

    # Fichiers cles
    print("\n  Fichiers cles:")
    key_files = [
        (DATA_RAW / "openaq_country_averages.csv", "Donnees OpenAQ"),
        (DATA_RAW / "world_cities_by_country.csv", "Donnees villes"),
        (DATA_RAW / "worldbank_transport.csv", "World Bank Transport"),
        (DATA_CLEANED / "base_analyse_complete.csv", "Base analyse complete"),
        (REPORTS_DIR / "figures", "Dossier figures"),
    ]

    for path, name in key_files:
        if path.exists():
            if path.is_file():
                size = path.stat().st_size / 1024
                print(f"    [OK] {name} ({size:.1f} KB)")
            else:
                count = len(list(path.glob("*.png")))
                print(f"    [OK] {name} ({count} fichiers)")
        else:
            print(f"    [--] {name}")

    return True


def run_extraction():
    """Execute toutes les etapes d'extraction."""
    print_header()
    print("\n  Mode: EXTRACTION DES DONNEES")

    s1, f1 = run_scripts_batch(EXTRACTION_SCRIPTS, "PHASE 1: EXTRACTION")
    s2, f2 = run_scripts_batch(AXES_SCRIPTS, "PHASE 2: TRAITEMENT PAR AXE")

    total_success = s1 + s2
    total_failed = f1 + f2
    total = total_success + total_failed

    print_separator("RESUME EXTRACTION")
    print(f"\n  Scripts executes: {total_success}/{total}")
    if total_failed > 0:
        print(f"  Scripts echoues: {total_failed}")

    return total_failed == 0


def run_analyses():
    """Execute toutes les analyses statistiques."""
    print_header()
    print("\n  Mode: ANALYSES STATISTIQUES")

    # Verifier que les donnees existent
    if not (DATA_RAW / "openaq_country_averages.csv").exists():
        print("\n  [ATTENTION] Donnees non trouvees!")
        print("  Executez d'abord: python main.py --extract")
        return False

    success, failed = run_scripts_batch(ANALYSE_SCRIPTS, "PHASE 3: ANALYSES")

    total = success + failed

    print_separator("RESUME ANALYSES")
    print(f"\n  Scripts executes: {success}/{total}")
    if failed > 0:
        print(f"  Scripts echoues: {failed}")

    print("\n  Fichiers generes:")
    print(f"    - {DATA_CLEANED / 'base_analyse_complete.csv'}")
    print(f"    - {REPORTS_DIR / 'figures/'} (graphiques)")

    return failed == 0


def run_all():
    """Execute le pipeline complet."""
    print_header()
    print("\n  Mode: PIPELINE COMPLET")
    print("  Cela peut prendre plusieurs minutes...")

    # Phase 1: Extraction
    s1, f1 = run_scripts_batch(EXTRACTION_SCRIPTS, "PHASE 1: EXTRACTION")

    # Phase 2: Axes
    s2, f2 = run_scripts_batch(AXES_SCRIPTS, "PHASE 2: TRAITEMENT PAR AXE")

    # Phase 3: Analyses
    s3, f3 = run_scripts_batch(ANALYSE_SCRIPTS, "PHASE 3: ANALYSES STATISTIQUES")

    total_success = s1 + s2 + s3
    total_failed = f1 + f2 + f3
    total = total_success + total_failed

    print_separator("RESUME FINAL")
    print(f"\n  Total scripts: {total}")
    print(f"  Reussis: {total_success}")
    print(f"  Echoues: {total_failed}")

    if total_failed == 0:
        print("\n  [SUCCES] Pipeline execute avec succes!")
    else:
        print(f"\n  [ATTENTION] {total_failed} script(s) ont echoue")

    print("\n  Resultats disponibles dans:")
    print(f"    - {DATA_CLEANED}")
    print(f"    - {REPORTS_DIR}")

    return total_failed == 0


def clean_temp_files():
    """Nettoie les fichiers temporaires."""
    print_separator("NETTOYAGE")

    # Fichiers temporaires a supprimer
    patterns = ["tmpclaude-*", "*.pyc", "__pycache__"]

    count = 0
    for pattern in patterns:
        for f in PROJECT_ROOT.glob(pattern):
            try:
                if f.is_file():
                    f.unlink()
                    count += 1
            except Exception:
                pass

    print(f"\n  {count} fichiers temporaires supprimes")
    return True


def interactive_menu():
    """Affiche le menu interactif."""
    while True:
        print_header()
        print("\n  Options disponibles:")
        print("    1. Executer le pipeline complet")
        print("    2. Extraction des donnees uniquement")
        print("    3. Analyses statistiques uniquement")
        print("    4. Afficher l'etat des donnees")
        print("    5. Nettoyer les fichiers temporaires")
        print("    0. Quitter")

        try:
            choice = input("\n  Votre choix [0-5]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Au revoir!")
            break

        if choice == "0":
            print("\n  Au revoir!")
            break
        elif choice == "1":
            run_all()
            input("\n  Appuyez sur Entree pour continuer...")
        elif choice == "2":
            run_extraction()
            input("\n  Appuyez sur Entree pour continuer...")
        elif choice == "3":
            run_analyses()
            input("\n  Appuyez sur Entree pour continuer...")
        elif choice == "4":
            check_data_status()
            input("\n  Appuyez sur Entree pour continuer...")
        elif choice == "5":
            clean_temp_files()
            input("\n  Appuyez sur Entree pour continuer...")
        else:
            print("\n  Choix invalide. Veuillez reessayer.")


def main():
    """Point d'entree principal."""
    parser = argparse.ArgumentParser(
        description="SAE S5.C.01 - Analyse de la Qualite de l'Air",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python main.py              # Menu interactif
  python main.py --all        # Pipeline complet
  python main.py --extract    # Extraction seulement
  python main.py --analyse    # Analyses seulement
  python main.py --status     # Etat des donnees
        """
    )

    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Executer le pipeline complet (extraction + analyses)"
    )
    parser.add_argument(
        "--extract", "-e",
        action="store_true",
        help="Executer uniquement l'extraction des donnees"
    )
    parser.add_argument(
        "--analyse", "-n",
        action="store_true",
        help="Executer uniquement les analyses statistiques"
    )
    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="Afficher l'etat des donnees"
    )
    parser.add_argument(
        "--clean", "-c",
        action="store_true",
        help="Nettoyer les fichiers temporaires"
    )

    args = parser.parse_args()

    # Execution selon les arguments
    if args.all:
        success = run_all()
        sys.exit(0 if success else 1)
    elif args.extract:
        success = run_extraction()
        sys.exit(0 if success else 1)
    elif args.analyse:
        success = run_analyses()
        sys.exit(0 if success else 1)
    elif args.status:
        check_data_status()
        sys.exit(0)
    elif args.clean:
        clean_temp_files()
        sys.exit(0)
    else:
        # Mode interactif par defaut
        interactive_menu()


if __name__ == "__main__":
    main()
