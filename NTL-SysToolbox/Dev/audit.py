#!/usr/bin/env python3
# ===========================================================
# Module Audit d'obsolescence - NTL-SysToolbox
# ===========================================================

import csv
import json
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any
import nmap  # pour le scan réseau

#visuel
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
import pyfiglet

console = Console()


def scan_network_simple(cidr: str) -> List[Dict[str, str]]:
    """
    Scanne une plage réseau (ex: '192.168.56.0/24') avec Nmap
    et renvoie une liste de machines au format:
    hostname, ip, os, version.
    """
    scanner = nmap.PortScanner()
    console.print(f"[bold cyan][INFO][/bold cyan] Scan réseau sur [white]{cidr}[/white] ...")
    scanner.scan(hosts=cidr, arguments='-O -T4')  # -O = détection OS

    components: List[Dict[str, str]] = []

    for host in scanner.all_hosts():
        ip = host
        hostname = scanner[host].hostname() or host

        detected_os = "Unknown"
        detected_version = "Unknown"

        if "osmatch" in scanner[host] and scanner[host]["osmatch"]:
            osmatch = scanner[host]["osmatch"][0]
            os_name = osmatch.get("name", "")
            detected_os = os_name or "Unknown"

        components.append(
            {
                "hostname": hostname,
                "ip": ip,
                "os": detected_os,
                "version": detected_version,
            }
        )

    return components


def parse_inventory_csv(csv_path: str) -> List[Dict[str, str]]:
    """
    Lit un CSV d’inventaire.
    Colonnes minimales : hostname, ip, os, version
    """
    components: List[Dict[str, str]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            components.append(row)
    return components


def load_eol_database(json_path: str) -> Dict[str, Dict[str, str]]:
    """
    Charge le référentiel EOL depuis un fichier JSON.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_os_and_version(os_name: str, version: str) -> tuple[str, str]:
    """
    Simplifie les noms d'OS détectés pour coller au référentiel EOL.
    Exemple :
      'Microsoft Windows Server 2022' -> ('Windows Server', '2022')
    """
    if not os_name:
        return os_name, version

    # Cas Windows Server
    if "Windows Server 2022" in os_name:
        return "Windows Server", "2022"
    if "Windows Server 2019" in os_name:
        return "Windows Server", "2019"
    if "Windows Server 2016" in os_name:
        return "Windows Server", "2016"
    if "Windows Server 2012" in os_name:
        return "Windows Server", "2012"

    return os_name, version


def classify_component(
    component: Dict[str, str],
    eol_db: Dict[str, Dict[str, str]],
    warning_months: int = 12,
) -> Dict[str, Any]:
    """
    Ajoute les infos EOL + statut à un composant.
    Statuts possibles : supported, warning, eol, unknown.
    """
    raw_os = component.get("os")
    raw_version = component.get("version")
    os_name, version = normalize_os_and_version(raw_os, raw_version)

    result: Dict[str, Any] = dict(component)

    eol_date_str = eol_db.get(os_name, {}).get(version)
    if not eol_date_str:
        result["eol_date"] = None
        result["status"] = "unknown"
        return result

    eol_date = datetime.strptime(eol_date_str, "%Y-%m-%d").date()
    today = date.today()
    result["eol_date"] = eol_date_str

    if eol_date < today:
        result["status"] = "eol"
    else:
        delta_warning_days = warning_months * 30
        if (eol_date - today).days <= delta_warning_days:
            result["status"] = "warning"
        else:
            result["status"] = "supported"

    return result


def evaluate_components(
    components: List[Dict[str, str]],
    eol_db: Dict[str, Dict[str, str]],
    warning_months: int = 12,
) -> List[Dict[str, Any]]:
    """
    Applique classify_component à toute la liste.
    """
    return [
        classify_component(c, eol_db, warning_months=warning_months)
        for c in components
    ]


def export_report_csv(components: List[Dict[str, Any]], output_path: str) -> None:
    """
    Exporte le rapport au format CSV.
    """
    if not components:
        console.print("[bold yellow][WARN][/bold yellow] Aucun composant à exporter (liste vide).")
        return

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(components[0].keys())
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(components)


def export_report_json(components: List[Dict[str, Any]], output_path: str) -> None:
    """
    Exporte le rapport au format JSON structuré.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "components": components,
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def list_os_versions(os_name: str, eol_db: Dict[str, Dict[str, str]]) -> None:
    """
    Affiche toutes les versions d'un OS et leurs dates EOL
    à partir de la base EOL.
    """
    versions = eol_db.get(os_name)
    if not versions:
        console.print(f"[bold yellow][WARN][/bold yellow] Aucun OS nommé '{os_name}' dans la base EOL.")
        return

    console.print(f"[bold cyan]Versions connues pour {os_name} :[/bold cyan]")
    for version, eol in versions.items():
        console.print(f"- [white]{os_name} {version}[/white] : EOL = [bold]{eol}[/bold]")


# ===========================================================
# Flows "métier" de l'audit
# ===========================================================

def run_csv_audit_flow() -> None:
    """Audit à partir d'un inventaire CSV."""
    inventory_path = console.input("Chemin du fichier CSV d'inventaire : ").strip()
    console.print("\n[bold cyan][INFO][/bold cyan] Lecture de l'inventaire...")
    components = parse_inventory_csv(inventory_path)

    eol_path = console.input("Chemin du fichier JSON EOL : ").strip()
    output_csv = console.input("Chemin du rapport CSV de sortie : ").strip()
    output_json = console.input("Chemin du rapport JSON de sortie : ").strip()
    warning_months_str = console.input(
        "Nombre de mois avant EOL pour passer en 'warning' (12 par défaut) : "
    ).strip()
    warning_months = int(warning_months_str) if warning_months_str else 12

    console.print("[bold cyan][INFO][/bold cyan] Chargement de la base EOL...")
    eol_db = load_eol_database(eol_path)

    console.print("[bold cyan][INFO][/bold cyan] Évaluation de l'obsolescence...")
    evaluated = evaluate_components(components, eol_db, warning_months=warning_months)

    console.print("[bold cyan][INFO][/bold cyan] Export des rapports...")
    export_report_csv(evaluated, output_csv)
    export_report_json(evaluated, output_json)

    console.print(f"\n[bold green]✔ Audit terminé. Rapports générés :[/bold green]")
    console.print(f"- [white]{output_csv}[/white]")
    console.print(f"- [white]{output_json}[/white]")


def run_scan_audit_flow() -> None:
    """Audit après scan réseau Nmap."""
    cidr = console.input("Plage réseau à scanner (ex: 192.168.56.0/24) : ").strip()
    components = scan_network_simple(cidr)
    console.print(f"[bold cyan][INFO][/bold cyan] {len(components)} machine(s) détectée(s).")

    eol_path = console.input("Chemin du fichier JSON EOL : ").strip()
    output_csv = console.input("Chemin du rapport CSV de sortie : ").strip()
    output_json = console.input("Chemin du rapport JSON de sortie : ").strip()
    warning_months_str = console.input(
        "Nombre de mois avant EOL pour passer en 'warning' (12 par défaut) : "
    ).strip()
    warning_months = int(warning_months_str) if warning_months_str else 12

    console.print("[bold cyan][INFO][/bold cyan] Chargement de la base EOL...")
    eol_db = load_eol_database(eol_path)

    console.print("[bold cyan][INFO][/bold cyan] Évaluation de l'obsolescence...")
    evaluated = evaluate_components(components, eol_db, warning_months=warning_months)

    console.print("[bold cyan][INFO][/bold cyan] Export des rapports...")
    export_report_csv(evaluated, output_csv)
    export_report_json(evaluated, output_json)

    console.print(f"\n[bold green]✔ Audit terminé. Rapports générés :[/bold green]")
    console.print(f"- [white]{output_csv}[/white]")
    console.print(f"- [white]{output_json}[/white]")


def run_eol_consult_flow() -> None:
    """Consultation des EOL pour un OS."""
    eol_path = console.input("Chemin du fichier JSON EOL : ").strip()
    eol_db = load_eol_database(eol_path)
    os_name = console.input("Nom de l'OS (ex: 'Windows Server' ou 'Ubuntu') : ").strip()
    console.print("")  # petite ligne vide
    list_os_versions(os_name, eol_db)


# ===========================================================
# Menu du module audit
# ===========================================================

def run_audit_obsolescence() -> None:
    """Menu interactif du module d'audit d'obsolescence."""
    while True:
        console.clear()

        banner = pyfiglet.figlet_format("AUDIT EOL", font="slant")
        console.print(f"[bold magenta]{banner}[/bold magenta]")

        console.print(Panel.fit(
            "[bold white]Module d'audit d'obsolescence - NTL-SysToolbox[/bold white]\n\n"
            "[cyan]1.[/cyan] Auditer un [bold]fichier CSV[/bold] d'inventaire\n"
            "[cyan]2.[/cyan] Scanner une [bold]plage IP[/bold] et auditer\n"
            "[cyan]3.[/cyan] Consulter les [bold]dates EOL[/bold] pour un OS\n"
            "[red]0.[/red] Retour au menu principal",
            border_style="magenta",
            title="[bold magenta]AUDIT D'OBSOLESCENCE[/bold magenta]",
            subtitle="[green]NTL-SysToolbox[/green]",
        ))

        mode = console.input("\n[bold cyan]Votre choix[/bold cyan] : ").strip() or "1"

        if mode == "1":
            console.clear()
            console.print(Rule("[bold cyan]Audit CSV d'inventaire[/bold cyan]"))
            run_csv_audit_flow()
            console.input("\n[dim]Appuyez sur Entrée pour revenir au menu Audit...[/dim]")
        elif mode == "2":
            console.clear()
            console.print(Rule("[bold cyan]Scan réseau + audit[/bold cyan]"))
            run_scan_audit_flow()
            console.input("\n[dim]Appuyez sur Entrée pour revenir au menu Audit...[/dim]")
        elif mode == "3":
            console.clear()
            console.print(Rule("[bold cyan]Consultation des dates EOL[/bold cyan]"))
            run_eol_consult_flow()
            console.input("\n[dim]Appuyez sur Entrée pour revenir au menu Audit...[/dim]")
        elif mode == "0":
            break
        else:
            console.print("\n[bold red]✖ Choix invalide. Merci de réessayer.[/bold red]")
            console.input("\n[dim]Appuyez sur Entrée pour continuer...[/dim]")


def main() -> None:
    """
    Point d’entrée utilisé par main.py :
    from audit import main as audit_main
    """
    run_audit_obsolescence()
