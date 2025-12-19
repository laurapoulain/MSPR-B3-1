import os
import mysql.connector
import subprocess
from datetime import datetime
import csv
from dotenv import load_dotenv
load_dotenv()

# ==========================
# CONFIGURATION
# ==========================
DB_HOST = os.getenv("MYSQL_HOST", "192.168.10.21")     # Adresse du serveur MySQL
DB_USER = os.getenv("MYSQL_USER")           # Utilisateur MySQL
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")     # Mot de passe MySQL
DB_NAME = os.getenv("MYSQL_DATABASE")            # Nom de la base à sauvegarder
EXPORT_TABLE = "products"     # Table à exporter en CSV
BACKUP_DIR = "./backups"  # Dossier de sauvegarde

# ==========================
# 1. SAUVEGARDE SQL
# ==========================
def sauvegarde_sql():
    """Effectue une sauvegarde complète de la base MySQL au format .sql"""
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        # Nom du fichier avec horodatage
        backup_file = os.path.join(
            BACKUP_DIR, f"{DB_NAME}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        )

        print(f"[+] Sauvegarde de la base {DB_NAME} en cours...")
        cmd = [
            "mysqldump",
            f"-h{DB_HOST}",
            f"-u{DB_USER}",
            f"-p{DB_PASSWORD}",
            DB_NAME,
        ]

        with open(backup_file, "w", encoding="utf-8") as f:
            subprocess.run(cmd, stdout=f, check=True)

        print(f"[OK] Sauvegarde SQL enregistrée dans : {backup_file}\n")

    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Échec de la sauvegarde SQL : {e}")
    except Exception as e:
        print(f"[ERREUR] Problème inattendu : {e}")

# ==========================
# 2. EXPORT CSV D’UNE TABLE
# ==========================
def export_table_csv(table_name=None):
    """Exporte une table MySQL au format CSV"""
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        # Si la table n’est pas fournie, on demande à l’utilisateur
        if not table_name:
            table_name = input("Entrez le nom de la table à exporter : ").strip()

        if not table_name:
            print("[ERREUR] Nom de table vide. Export annulé.\n")
            return

        csv_file = os.path.join(
            BACKUP_DIR, f"{table_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        print(f"[+] Export de la table '{table_name}' en CSV...")

        # Connexion à MySQL
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]

        # Écriture dans le fichier CSV
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        print(f"[OK] Export CSV enregistré dans : {csv_file}\n")

    except mysql.connector.Error as err:
        print(f"[ERREUR] MySQL : {err}")
    except Exception as e:
        print(f"[ERREUR] Problème inattendu : {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()


# ==========================
# 3. MAIN
# ==========================
if __name__ == "__main__":
    print("===== MODULE DE SAUVEGARDE WMS =====\n")
    sauvegarde_sql()
    export_table_csv()
    print("=== Sauvegarde WMS terminée ===")
