#!/usr/bin/env python3
# LE bon fichier
"""
Module 1 - Diagnostic centralisé (NTL SysToolbox)
-------------------------------------------------
Vérifie la connectivité réseau, le DNS/AD, la base MySQL,
et exécute un diagnostic distant sur les serveurs Windows et Linux.

Les identifiants et IP sont chargés depuis le fichier .env.
"""

import os
import platform
import subprocess
import paramiko
import dns.resolver
import socket
import mysql.connector
import winrm
import requests_ntlm
from dotenv import load_dotenv

# ============================================================
# CHARGEMENT DU FICHIER .env
# ============================================================
load_dotenv()
print("Chargement du .env ...")
print("Windows server :", os.getenv("WIN_HOST"))

SERVER_DNS = os.getenv("SERVER_DNS", "192.168.10.10")
SERVER_AD = os.getenv("SERVER_DNS", "192.168.10.10")
SERVER_MYSQL = os.getenv("MYSQL_HOST", "192.168.10.21")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

WINDOWS_SERVER = os.getenv("WIN_HOST")
WINDOWS_USER = os.getenv("WIN_USER")
WINDOWS_PASS = os.getenv("WIN_PASS")

LINUX_SERVER = os.getenv("LINUX_HOST")
LINUX_USER = os.getenv("LINUX_USER")
LINUX_PASS = os.getenv("LINUX_PASS")

LINUX_CLIENT = os.getenv("LINUX_CLIENT")
LINUX_CLIENT_USER = os.getenv("LINUX_CLIENT_USER")
LINUX_CLIENT_PASS = os.getenv("LINUX_CLIENT_PASS")

print("===== DIAGNOSTIC CENTRALISÉ =====\n")

# ============================================================
# 1. Vérification de connectivité réseau
# ============================================================
def test_ping(ip):
    """Teste la connectivité par ping"""
    print(f"[+] Test de connexion vers {ip} ...")
    cmd = ["ping", "-c", "2", ip] if platform.system() != "Windows" else ["ping", "-n", "2", ip]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        print(f"  {ip} est joignable\n")
        return True
    else:
        print(f"  Échec de connexion vers {ip}\n")
        return False


# ============================================================
# 2. Vérification DNS 
# ============================================================
def test_dns(server_dns):
    """Teste la résolution DNS du domaine epsi.local"""
    print(f"[+] Vérification DNS du domaine epsi.local ({server_dns})...")
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [server_dns]
        answer = resolver.resolve('epsi.local', 'A')
        print(f"  Résolution DNS OK : {answer[0]}\n")
    except Exception as e:
        print("  Erreur DNS :", e, "\n")


# ============================================================
# 2. Vérification du services Active Directory
# ============================================================
def test_ad(ip):
    """Vérifie la disponibilité des services essentiels d'Active Directory"""
    print(f"[+] Vérification du service Active Directory sur epsi.local ({ip})...")

    # Liste des ports AD critiques
    ports = {
        389:  "LDAP",
        636:  "LDAP sécurisé (LDAPS)",
        88:   "Kerberos",
        # 135:  "RPC",
        445:  "NetLogon / SMB",
        # 3268: "Global Catalog (GC)",
        # 3269: "Global Catalog sécurisé (GC SSL)"
    }

    ad_ok = True

    for port, service in ports.items():
        try:
            sock = socket.create_connection((ip, port), timeout=3)
            print(f"  [OK] {service} (port {port}) est accessible.")
            sock.close()
        except Exception as e:
            print(f"  [ERREUR] {service} (port {port}) injoignable : {e}")
            ad_ok = False

    if ad_ok:
        print("Service Active Directory : tous les ports essentiels répondent.\n")
    else:
        print("Certains services AD sont inaccessibles. Vérifier la configuration ou le pare-feu.\n")



# ============================================================
# 3. Vérification du service MySQL
# ============================================================
def test_mysql():
    """Teste la connexion MySQL"""
    print(f"[+] Vérification de la base MySQL ({SERVER_MYSQL}) ...")
    try:
        conn = mysql.connector.connect(
            host=SERVER_MYSQL,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            connection_timeout=5
        )
        if conn.is_connected():
            print("  Connexion MySQL OK\n")
            conn.close()
    except Exception as e:
        print("  Erreur MySQL :", e, "\n")




# ============================================================
# 4. Diagnostic Windows via WinRM
# ============================================================

# ne pas afficher les erreurs persistantes
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def diagnostic_windows(ip, username, password):
    """Collecte des infos système sur le Windows Server via WinRM"""
    print(f"=== Diagnostic de Windows Server ({ip}) ===")
    if not test_ping(ip):
        print("  Serveur injoignable.\n")
        return

    try:
        session = winrm.Session(f'http://{ip}:5985/wsman', auth=(username, password), transport='ntlm')
        ps_script = """
        $os = Get-CimInstance Win32_OperatingSystem
        $cpu = Get-Counter '\\Processor(_Total)\\% Processor Time' | Select -ExpandProperty CounterSamples | Select -ExpandProperty CookedValue
        $ram = [math]::Round((($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize) * 100, 2)
        $disk = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'" | Select-Object Size,FreeSpace
        $diskUsed = [math]::Round((1 - ($disk.FreeSpace / $disk.Size)) * 100, 2)
        $uptime = (Get-Date) - $os.LastBootUpTime
        $hours = [math]::Floor($uptime.TotalHours)
        $minutes = $uptime.Minutes
        Write-Output ("OS : " + $os.Caption)
        Write-Output ("Uptime: up " + $hours + " hours, " + $minutes + " minutes")
        Write-Output ("CPU : " + [math]::Round($cpu,2) + " % ")
        Write-Output ("RAM : " + $ram + " % ")
        Write-Output ("Disk: " + $diskUsed + " % ")
        """
        result = session.run_ps(ps_script)
        output = result.std_out.decode().strip()
        if output:
            print(output)
        else:
            print("  Aucune donnée reçue via WinRM (vérifier configuration sur le serveur).")

    except Exception as e:
        print("  Erreur WinRM Windows :", e)
    print()


# ============================================================
# 5. Diagnostic Linux via SSH
# ============================================================
def diagnostic_linux(ip, username, password):
    """Collecte des infos système sur le serveur Linux via SSH"""
    print(f"=== Diagnostic d'Ubuntu ({ip}) ===")
    if not test_ping(ip):
        print("  Machine injoignable.\n")
        return
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=5)

        commands = {
            "OS": "lsb_release -d | cut -f2",
            "Uptime": "uptime -p",
            "CPU": "top -bn1 | grep 'Cpu(s)' | awk '{print $2+$4}'",
            "RAM": "free | awk '/Mem/ {print $3/$2 * 100.0}'",
            "DISK": "df -h / | awk 'NR==2 {print $5}'"
        }

        for key, cmd in commands.items():
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode().strip()
            print(f"  {key}: {output}")

        ssh.close()
    except Exception as e:
        print("  Erreur SSH Linux :", e)
    print()



# ============================================================
# SAUVEGARDE DU DIAGNOSTIC DANS UN RAPPORT CSV
# ============================================================
import csv
def save_csv(data, filename="rapport_diagnostic.csv"):
    """Sauvegarde un résumé des serveurs diagnostiqués"""
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["IP", "OS", "Uptime", "CPU", "RAM (%)", "Disque (%)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"📊 Rapport CSV enregistré dans {filename}")



# ============================================================
# EXÉCUTION DU DIAGNOSTIC
# ============================================================
def main():
    test_ping(SERVER_DNS)
    test_dns(SERVER_DNS)
    test_ad(SERVER_AD)
    test_mysql()
    diagnostic_windows(WINDOWS_SERVER, WINDOWS_USER, WINDOWS_PASS)
    diagnostic_linux(LINUX_SERVER, LINUX_USER, LINUX_PASS)
    diagnostic_linux(LINUX_CLIENT, LINUX_CLIENT_USER, LINUX_CLIENT_PASS)
    print("=== Diagnostic terminé ===")


# sans rapport généré - sortie normale
if __name__ == "__main__":
    main()

# optionnel : rapport de diagnostic
if __name__ == "__main__":    
    import sys

    # Lance le diagnostic et capture la sortie dans un fichier
    original_stdout = sys.stdout  # garde la sortie console normale
    with open("diagnostics/rapport_diagnostic.csv", "w", encoding="utf-8") as f:
        sys.stdout = f  # redirige tous les prints vers le fichier
        main()          # ta fonction principale (celle qui lance tout ton diagnostic)
        sys.stdout = original_stdout  # restaure la sortie console

    print("Rapport enregistré dans diagnostics/rapport_diagnostic.csv ")

