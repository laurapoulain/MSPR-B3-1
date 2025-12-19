# ========================================
# Fichier: README.md
# ========================================

# 🧰 NTL-SysToolbox

Outil d'administration système pour **NordTransit Logistics**

## 📝 Description

NTL-SysToolbox est un outil CLI qui regroupe trois modules essentiels pour l'administration système:

1. **Module Diagnostic** 🔍
   - Vérification des services AD/DNS
   - Test de connexion MySQL WMS
   - Contrôle des ressources serveurs (CPU, RAM, Disque)

2. **Module Sauvegarde WMS** 💾
   - Sauvegarde complète de la base MySQL
   - Export de tables au format CSV
   - Vérification d'intégrité des backups

3. **Module Audit d'obsolescence** 🧾
   - Scan réseau pour détecter les équipements
   - Identification des OS et versions
   - Vérification des dates End-of-Life (EOL)

## 📁 Structure du projet

```
NTL-SysToolbox/
├── Dev/
│   ├── main.py          # Point d'entrée - Menu interactif
│   ├── config.py        # Configuration centralisée
│   ├── utils.py         # Fonctions utilitaires communes
│   ├── save.py          # Module Sauvegarde WMS ✅
│   ├── diag.py          # Module Diagnostic (à implémenter)
│   └── audit.py         # Module Audit (à implémenter)
├── out/                 # Répertoire de sortie (auto-généré)
│   ├── backups/         # Sauvegardes SQL/CSV
│   ├── diagnostics/     # Résultats diagnostics
│   └── audits/          # Rapports d'audit
├── .env                 # Configuration locale (NE PAS COMMITER!)
├── .env.example         # Template de configuration
├── .gitignore           # Fichiers à ignorer
├── requirements.txt     # Dépendances Python complètes
├── requirements-minimal.txt  # Dépendances minimales
├── setup.sh             # Script d'installation automatique
└── README.md            # Ce fichier

```

## 🚀 Installation

### Méthode 1: Installation automatique (recommandé)

```bash
# Rendre le script exécutable
chmod +x setup.sh

# Lancer l'installation
./setup.sh
```

Le script va:
- Vérifier Python 3 et MySQL
- Créer un environnement virtuel
- Installer les dépendances
- Créer le fichier .env
- Tester la connexion MySQL

### Méthode 2: Installation manuelle

```bash
# 1. Créer un environnement virtuel
python3 -m venv venv

# 2. Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Copier et configurer .env
cp .env.example .env
nano .env  # Éditer avec vos paramètres

# 5. Créer les répertoires
mkdir -p out/backups out/diagnostics out/audits
```

## ⚙️ Configuration

Éditez le fichier `.env` avec vos paramètres:

```bash
# MySQL (obligatoire pour le module sauvegarde)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=votre_mot_de_passe
MYSQL_DATABASE=wms_ntl

# Serveurs à monitorer
AD_SERVERS=192.168.10.10,192.168.10.11
DNS_SERVERS=192.168.10.10,192.168.10.11
WMS_DB_HOST=192.168.10.21

# Réseaux à scanner
SCAN_NETWORKS=192.168.10.0/24,192.168.20.0/24
```

## 📖 Utilisation

### Mode interactif (recommandé)

```bash
source venv/bin/activate
cd Dev
python3 main.py
```

Un menu vous permettra de choisir le module à exécuter.

### Mode batch (ligne de commande)

```bash
cd Dev

# Sauvegarde seulement
python3 main.py --mode sauvegarde

# Diagnostic seulement
python3 main.py --mode diagnostic

# Audit seulement
python3 main.py --mode audit

# Tous les modules
python3 main.py --mode all
```

### Exemples spécifiques

```bash
# Test du module sauvegarde seul
cd Dev
python3 save.py

# Afficher la configuration
python3 config.py

# Tester les utilitaires
python3 utils.py
```

## 📊 Outputs

Tous les résultats sont sauvegardés dans `out/`:

- **JSON horodaté**: Format structuré pour exploitation automatique
- **Fichiers SQL**: Sauvegardes complètes de la base
- **Fichiers CSV**: Exports de tables spécifiques
- **Rapports**: Résultats d'audit et diagnostic

### Exemple de sortie JSON

```json
{
  "timestamp": "2025-12-16T14:30:00",
  "status": "success",
  "message": "Sauvegarde créée avec succès",
  "filepath": "out/backups/wms_backup_20251216_143000.sql",
  "size_mb": 2.45
}
```

## 🧪 Tests

### Base de données de test

Un script SQL est fourni pour créer une base de test:

```bash
# Créer la base
mysql -u root -p -e "CREATE DATABASE wms_ntl;"

# Importer le schéma et les données
mysql -u root -p wms_ntl < wms_test_db.sql

# Vérifier
mysql -u root -p -e "USE wms_ntl; SHOW TABLES;"
```

### Tests unitaires

```bash
# Tester le module config
python3 Dev/config.py

# Tester les utilitaires
python3 Dev/utils.py

# Tester le module sauvegarde
python3 Dev/save.py
```

## 🔐 Sécurité

- ❌ **Ne jamais commiter le fichier `.env`**
- ✅ Utiliser des comptes avec permissions minimales
- ✅ Protéger les fichiers de sauvegarde (chiffrement recommandé)
- ✅ Restreindre l'accès au répertoire `out/`
- ✅ Nettoyer régulièrement les anciennes sauvegardes

## 🔧 Dépannage

### Erreur: "mysqldump not found"

```bash
# Ubuntu/Debian
sudo apt install mysql-client

# CentOS/RHEL
sudo yum install mysql

# macOS
brew install mysql-client
```

### Erreur: "Access denied for user"

```bash
# Vérifier les permissions MySQL
mysql -u root -p -e "SHOW GRANTS FOR 'votre_user'@'localhost';"

# Créer un utilisateur dédié
mysql -u root -p
CREATE USER 'ntl_backup'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT, LOCK TABLES ON wms_ntl.* TO 'ntl_backup'@'localhost';
FLUSH PRIVILEGES;
```

### Erreur: "Can't connect to MySQL server"

```bash
# Vérifier que MySQL est démarré
sudo systemctl status mysql

# Vérifier le port
sudo netstat -tlnp | grep 3306
```

## 📚 Documentation

- Guide de test complet: voir `test_guide.md`
- Cahier des charges: voir `Sujet_N°1.pdf`
- Documentation API: générée avec `pydoc`

## 👥 Équipe

Projet MSPR - Équipe de 4-5 étudiants
Durée: 19 heures de préparation

## 📄 Licence

Projet académique - Tous droits réservés

## 🆘 Support

Pour toute question ou problème:
1. Vérifier la configuration avec `python3 main.py` option 5
2. Consulter le guide de dépannage ci-dessus
3. Contacter l'encadrant pédagogique

---

**Version**: 1.0.0  
**Dernière mise à jour**: Décembre 2025

# ========================================
# FIN DE README.md
# ========================================