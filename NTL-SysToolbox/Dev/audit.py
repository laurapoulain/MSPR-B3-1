#!/usr/bin/env python3
"""
Module d'audit d'obsolescence pour NTL-SysToolbox
Scanne le réseau et identifie les systèmes obsolètes (EOL)
"""

import os
import sys
import json
import socket
import subprocess
import requests
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional

# Import des modules locaux
sys.path.insert(0, str(Path(__file__).parent))
from config import Config
from utils import (
    save_json_output, format_timestamp, get_iso_timestamp,
    create_result, print_success, print_error, print_warning,
    print_info, print_header, print_separator, validate_network
)


class NetworkAudit:
    """Classe pour l'audit réseau et obsolescence"""
    
    def __init__(self):
        """Initialise le module d'audit"""
        self.eol_cache = {}
    
    def ping_host(self, ip: str, timeout: int = 2) -> bool:
        """
        Ping un hôte pour vérifier s'il est accessible
        
        Args:
            ip: Adresse IP
            timeout: Timeout en secondes
        
        Returns:
            bool: True si accessible
        """
        try:
            # Commande ping selon l'OS
            param = '-n' if sys.platform.lower() == 'win32' else '-c'
            timeout_param = '-w' if sys.platform.lower() == 'win32' else '-W'
            
            command = ['ping', param, '1', timeout_param, str(timeout), ip]
            result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout + 1
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def scan_network_simple(self, network: str, max_hosts: int = 254) -> List[Dict]:
        """
        Scan réseau simple avec ping
        
        Args:
            network: Réseau CIDR (ex: 192.168.10.0/24)
            max_hosts: Nombre max d'hôtes à scanner
        
        Returns:
            list: Liste des hôtes trouvés
        """
        hosts_found = []
        
        # Parser le réseau CIDR
        if '/' not in network:
            print_error(f"Format réseau invalide: {network}")
            return hosts_found
        
        ip_base, mask = network.split('/')
        ip_parts = ip_base.split('.')
        
        if len(ip_parts) != 4:
            print_error(f"Adresse IP invalide: {ip_base}")
            return hosts_found
        
        # Scan simple pour /24
        if mask == '24':
            base = '.'.join(ip_parts[:3])
            print_info(f"Scan du réseau {network}...")
            
            for i in range(1, min(max_hosts + 1, 255)):
                ip = f"{base}.{i}"
                
                if i % 50 == 0:
                    print(f"  → Progression: {i}/{max_hosts} hôtes testés")
                
                if self.ping_host(ip, timeout=1):
                    hostname = self.get_hostname(ip)
                    os_info = self.detect_os_simple(ip)
                    
                    host_info = {
                        'ip': ip,
                        'hostname': hostname,
                        'os': os_info['os'],
                        'os_version': os_info.get('version', 'unknown')
                    }
                    hosts_found.append(host_info)
                    print_info(f"  ✓ Hôte trouvé: {ip} ({hostname})")
        else:
            print_warning(f"Scan limité au /24 pour le moment. Réseau: {network}")
        
        return hosts_found
    
    def get_hostname(self, ip: str) -> str:
        """
        Récupère le nom d'hôte d'une IP
        
        Args:
            ip: Adresse IP
        
        Returns:
            str: Nom d'hôte ou 'unknown'
        """
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except Exception:
            return 'unknown'
    
    def detect_os_simple(self, ip: str) -> Dict:
        """
        Détection OS simple via TTL
        
        Args:
            ip: Adresse IP
        
        Returns:
            dict: Informations OS détectées
        """
        os_info = {
            'os': 'unknown',
            'version': 'unknown',
            'method': 'ttl_detection'
        }
        
        try:
            # Utiliser TTL pour deviner l'OS
            param = '-n' if sys.platform.lower() == 'win32' else '-c'
            command = ['ping', param, '1', ip]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=3
            )
            
            output = result.stdout.lower()
            
            # Analyser le TTL
            if 'ttl=' in output:
                ttl_str = output.split('ttl=')[1].split()[0]
                ttl = int(ttl_str)
                
                # Heuristique basique sur TTL
                if ttl <= 64:
                    os_info['os'] = 'Linux/Unix'
                elif ttl <= 128:
                    os_info['os'] = 'Windows'
                elif ttl <= 255:
                    os_info['os'] = 'Cisco/Network Device'
                
        except Exception:
            pass
        
        return os_info
    
    def get_eol_info(self, product: str) -> Optional[Dict]:
        """
        Récupère les infos EOL depuis endoflife.date API
        
        Args:
            product: Nom du produit (ex: 'ubuntu', 'windows-server')
        
        Returns:
            dict: Infos EOL ou None
        """
        # Vérifier le cache
        if product in self.eol_cache:
            return self.eol_cache[product]
        
        try:
            url = f"{Config.EOL_DATA_SOURCE}{product}.json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.eol_cache[product] = data
                return data
            else:
                return None
        except Exception as e:
            print_warning(f"Erreur API EOL pour {product}: {e}")
            return None
    
    def check_eol_status(self, os_name: str, os_version: str) -> Dict:
        """
        Vérifie le statut EOL d'un système
        
        Args:
            os_name: Nom de l'OS
            os_version: Version de l'OS
        
        Returns:
            dict: Statut EOL
        """
        result = {
            'os': os_name,
            'version': os_version,
            'eol_date': None,
            'is_eol': False,
            'support_status': 'unknown',
            'days_until_eol': None
        }
        
        # Mapper les noms d'OS vers les produits endoflife.date
        os_mapping = {
            'ubuntu': 'ubuntu',
            'debian': 'debian',
            'centos': 'centos',
            'rhel': 'rhel',
            'windows server': 'windows-server',
            'windows': 'windows',
            'macos': 'macos'
        }
        
        # Trouver le produit correspondant
        product = None
        for key, value in os_mapping.items():
            if key in os_name.lower():
                product = value
                break
        
        if not product:
            result['support_status'] = 'unknown_product'
            return result
        
        # Récupérer les infos EOL
        eol_data = self.get_eol_info(product)
        
        if not eol_data:
            result['support_status'] = 'api_error'
            return result
        
        # Chercher la version correspondante
        for version_info in eol_data:
            if str(version_info.get('cycle', '')) == str(os_version):
                eol_date_str = version_info.get('eol')
                
                if eol_date_str and eol_date_str != False:
                    try:
                        eol_date = datetime.strptime(str(eol_date_str), '%Y-%m-%d').date()
                        result['eol_date'] = str(eol_date)
                        
                        today = date.today()
                        result['is_eol'] = eol_date < today
                        
                        if not result['is_eol']:
                            days_until = (eol_date - today).days
                            result['days_until_eol'] = days_until
                            
                            if days_until <= 90:
                                result['support_status'] = 'ending_soon'
                            else:
                                result['support_status'] = 'active'
                        else:
                            result['support_status'] = 'eol'
                    except Exception:
                        result['support_status'] = 'parse_error'
                
                break
        
        return result
    
    def generate_audit_report(self, hosts: List[Dict]) -> Dict:
        """
        Génère un rapport d'audit complet
        
        Args:
            hosts: Liste des hôtes scannés
        
        Returns:
            dict: Rapport d'audit
        """
        report = {
            'timestamp': get_iso_timestamp(),
            'total_hosts': len(hosts),
            'hosts': [],
            'summary': {
                'eol_systems': 0,
                'ending_soon': 0,
                'active_support': 0,
                'unknown_status': 0
            }
        }
        
        print_info("Génération du rapport d'audit...")
        
        for host in hosts:
            print(f"  → Analyse: {host['ip']} ({host['hostname']})")
            
            # Vérifier le statut EOL
            eol_status = self.check_eol_status(host['os'], host['os_version'])
            
            host_report = {
                'ip': host['ip'],
                'hostname': host['hostname'],
                'os': host['os'],
                'os_version': host['os_version'],
                'eol_info': eol_status
            }
            
            # Mettre à jour le résumé
            status = eol_status['support_status']
            if status == 'eol':
                report['summary']['eol_systems'] += 1
            elif status == 'ending_soon':
                report['summary']['ending_soon'] += 1
            elif status == 'active':
                report['summary']['active_support'] += 1
            else:
                report['summary']['unknown_status'] += 1
            
            report['hosts'].append(host_report)
        
        return report
    
    def run_full_audit(self, networks: List[str] = None) -> Dict:
        """
        Exécute un audit complet
        
        Args:
            networks: Liste des réseaux à scanner
        
        Returns:
            dict: Résultats de l'audit
        """
        if networks is None:
            networks = Config.SCAN_NETWORKS
        
        print_header("🧾 Audit d'Obsolescence", 70)
        
        all_hosts = []
        
        for network in networks:
            if not validate_network(network):
                print_error(f"Réseau invalide: {network}")
                continue
            
            print_separator("-", 70)
            hosts = self.scan_network_simple(network)
            all_hosts.extend(hosts)
            print_success(f"{len(hosts)} hôte(s) trouvé(s) sur {network}")
        
        # Générer le rapport
        print("\n")
        print_separator("-", 70)
        report = self.generate_audit_report(all_hosts)
        
        # Afficher le résumé
        print("\n")
        print_separator("=", 70)
        print_header("📊 Résumé de l'Audit", 70)
        print(f"\nHôtes scannés: {report['total_hosts']}")
        print(f"  🔴 Systèmes EOL: {report['summary']['eol_systems']}")
        print(f"  🟠 Support bientôt terminé: {report['summary']['ending_soon']}")
        print(f"  🟢 Support actif: {report['summary']['active_support']}")
        print(f"  ⚪ Statut inconnu: {report['summary']['unknown_status']}")
        
        return report


def list_available_os_products():
    """Liste les produits disponibles sur endoflife.date"""
    print_info("Récupération de la liste des produits...")
    
    try:
        url = f"{Config.EOL_DATA_SOURCE}all.json"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            products = response.json()
            print(f"\n{len(products)} produits disponibles:\n")
            
            # Afficher par catégories
            os_products = [p for p in products if any(x in p.lower() for x in ['ubuntu', 'debian', 'centos', 'windows', 'rhel', 'macos'])]
            
            print("Systèmes d'exploitation:")
            for product in sorted(os_products):
                print(f"  • {product}")
            
            return products
        else:
            print_error("Impossible de récupérer la liste")
            return []
    except Exception as e:
        print_error(f"Erreur: {e}")
        return []


def get_os_versions(product: str):
    """Affiche les versions EOL d'un produit"""
    print_info(f"Récupération des versions de {product}...")
    
    audit = NetworkAudit()
    eol_data = audit.get_eol_info(product)
    
    if not eol_data:
        print_error(f"Produit introuvable: {product}")
        return
    
    print(f"\nVersions de {product}:\n")
    print(f"{'Version':<15} {'EOL Date':<15} {'Support Status':<20}")
    print("-" * 50)
    
    for version in eol_data:
        cycle = str(version.get('cycle', 'N/A'))
        eol = str(version.get('eol', 'N/A'))
        
        # Déterminer le statut
        status = "N/A"
        if eol != 'N/A' and eol != 'False':
            try:
                eol_date = datetime.strptime(eol, '%Y-%m-%d').date()
                if eol_date < date.today():
                    status = "🔴 EOL"
                elif (eol_date - date.today()).days <= 90:
                    status = "🟠 Ending Soon"
                else:
                    status = "🟢 Active"
            except Exception:
                pass
        
        print(f"{cycle:<15} {eol:<15} {status:<20}")


def run_audit_interactive():
    """Mode interactif pour l'audit"""
    print_header("🧾 Module Audit d'Obsolescence", 70)
    
    audit = NetworkAudit()
    
    print("\nOptions disponibles:")
    print("1. Audit complet (scan tous les réseaux configurés)")
    print("2. Scanner un réseau spécifique")
    print("3. Lister les produits disponibles (EOL)")
    print("4. Afficher les versions EOL d'un produit")
    print("5. Vérifier le statut EOL d'un système")
    print("0. Retour")
    
    choice = input("\nVotre choix: ").strip()
    
    if choice == '1':
        print("\n")
        result = audit.run_full_audit()
        
        # Sauvegarder
        output_file = Config.AUDIT_DIR / f"audit_{format_timestamp()}.json"
        save_json_output(result, output_file)
        print(f"\n✅ Audit sauvegardé: {output_file}")
        
    elif choice == '2':
        network = input("\nRéseau CIDR (ex: 192.168.10.0/24): ").strip()
        if validate_network(network):
            print("\n")
            result = audit.run_full_audit([network])
            
            output_file = Config.AUDIT_DIR / f"audit_{format_timestamp()}.json"
            save_json_output(result, output_file)
            print(f"\n✅ Audit sauvegardé: {output_file}")
        else:
            print_error("Format réseau invalide")
    
    elif choice == '3':
        print("\n")
        list_available_os_products()
    
    elif choice == '4':
        product = input("\nNom du produit (ex: ubuntu, windows-server): ").strip()
        print("\n")
        get_os_versions(product)
    
    elif choice == '5':
        os_name = input("\nNom de l'OS: ").strip()
        os_version = input("Version: ").strip()
        print("\n")
        result = audit.check_eol_status(os_name, os_version)
        print(json.dumps(result, indent=2, ensure_ascii=False))


def run_audit_batch():
    """Mode batch pour l'audit"""
    audit = NetworkAudit()
    result = audit.run_full_audit()
    
    # Sauvegarder
    output_file = Config.AUDIT_DIR / f"audit_{format_timestamp()}.json"
    save_json_output(result, output_file)
    print(f"\n✅ Audit sauvegardé: {output_file}")
    
    return result


if __name__ == "__main__":
    run_audit_interactive()