#!/usr/bin/env python3
# ===========================================================
# NTL-SysToolbox - Menu CLI interactif persistant
# ===========================================================

import os
from datetime import datetime

# Import des modules
from diagnostic import main as diagnostic_main
from sauvegarde import sauvegarde_sql, export_table_csv
from audit import main as audit_main



# ===========================================================
# Fonctions utilitaires
# ===========================================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    clear_screen()
    print("=" * 60)
    print("              NTL-SysToolbox - Menu CLI")
    print("=" * 60)
    print(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


# ===========================================================
# Sous-menu pour l'audit
# ===========================================================

def audit_menu():
    """Sous-menu module d'audit d'obsolescence."""
    while True:
        clear_screen()
        print("=" * 60)
        print("        MODULE AUDIT D'OBSOLESCENCE - NTL-SysToolbox")
        print("=" * 60)
        print("1. Lancer l'audit d'obsolescence")
        print("0. Retour au menu principal\n")

        choice = input("Votre choix : ").strip()

        if choice == "1":
            clear_screen()
            print("[INFO] Exécution du module Audit d'obsolescence...\n")
            audit_main()   #
            print("\n[OK] Module Audit terminé.\n")
            input("Appuyez sur Entrée pour revenir au menu Audit...")
        elif choice == "0":
            break
        else:
            print("\nChoix invalide. Réessayez.\n")
            input("Appuyez sur Entrée pour continuer...")


# ===========================================================
# Fonctions des modules
# ===========================================================

def module_diagnostic():
    print("[INFO] Exécution du module Diagnostic...\n")
    diagnostic_main()
    print("\n[OK] Module Diagnostic terminé.\n")
    input("Appuyez sur Entrée pour revenir au menu...")


def module_sauvegarde():
    print("[INFO] Exécution du module Sauvegarde WMS...\n")
    sauvegarde_sql()
    export_table_csv()
    print("\n[OK] Module Sauvegarde terminé.\n")
    input("Appuyez sur Entrée pour revenir au menu...")


def module_audit():
    """Pointe maintenant vers le sous-menu audit stylé."""
    audit_menu()


# ===========================================================
# Boucle principale du menu
# ===========================================================

def main_menu():
    while True:
        print_header()
        print("1. Diagnostic centralisé")
        print("2. Sauvegarde WMS")
        print("3. Audit d’obsolescence")
        print("0. Quitter\n")

        choice = input("Choisissez une option : ").strip()

        if choice == "1":
            clear_screen()
            module_diagnostic()
        elif choice == "2":
            clear_screen()
            module_sauvegarde()
        elif choice == "3":
            clear_screen()
            module_audit()
        elif choice == "0":
            print("\nFin du programme. À bientôt !")
            break
        else:
            print("\nChoix invalide. Réessayez.\n")
            input("Appuyez sur Entrée pour continuer...")


# ===========================================================
# Lancement du programme
# ===========================================================

if __name__ == "__main__":
    main_menu()
