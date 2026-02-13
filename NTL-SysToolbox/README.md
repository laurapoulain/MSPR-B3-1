# ========================================
# Fichier: README.md
# ========================================

# NTL-SysToolbox

Outil d'administration système pour **NordTransit Logistics**

## Description

NTL-SysToolbox est un outil CLI qui regroupe trois modules essentiels pour l'administration système:

1. **Module Diagnostic** 
   - Vérification des services AD/DNS
   - Test de connexion MySQL WMS
   - Contrôle des ressources serveurs (CPU, RAM, Disque)

2. **Module Sauvegarde WMS** 
   - Sauvegarde complète de la base MySQL
   - Export de tables au format CSV
   - Vérification d'intégrité des backups

3. **Module Audit d'obsolescence** 
   - Scan réseau pour détecter les équipements
   - Identification des OS et versions
   - Vérification des dates End-of-Life (EOL)

## Structure du projet

```
NTL-SysToolbox/
NTL-SysToolbox/
├── backups/                  # Stocke les sauvegardes de bases SQL et exports de table - Module 2
│
├── Data/
│   └── eol.json              # Base des dates de fin de vie (EOL) - Module 3
│
├── Dev/
│   ├── main.py               # Menu principal
│   ├── diagnostic.py         # Module 1 -  Diagnostic réseau/système 
│   ├── sauvegarde.py         # Module 2 - Sauvegarde MySQL
│   └── audit.py              # Module 3 - Audit d’obsolescence
│
├── outputs/                  # Stocke les rapports d'audits - Module 3
│   ├── audit_ubuntu.json     # Exemple de rapport Ubuntu
│   └── audit_ws2022.json     # Exemple de rapport Windows Server
│
├── .requirements.txt         # Dépendances Python
├── clean-outputs.sh          # ...
├── README.md                 # Ce fichier

├── setup.sh                  # Installation Linux
└── setup.bat                 # Installation Windows



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


## ⚙️ Configuration

Éditez le fichier `.env` avec vos paramètres:

```bash
# MySQL (obligatoire pour le module sauvegarde)
MYSQL_HOST=localhost
MYSQL_PORT=XXXX
MYSQL_USER=root
MYSQL_PASSWORD=votre_mot_de_passe
MYSQL_DATABASE=name_database

# Serveurs à monitorer
AD_SERVERS=192.168.x.x,192.168.x.x
AD_DOMAINS=domaine.local
DNS_SERVERS=192.168.x.x,192.168.x.x
WMS_DB_HOST=192.168.x.x
WMS_DB_PORT=XXXX

# Windows Server
WIN_HOST=192.168.x.x
WIN_USER=domaine\administrateur
WIN_PASS=votre_mot_de_passe

# Serveur Linux 
LINUX_HOST=192.168.x.x
LINUX_USER=user
LINUX_PASS=votre_mot_de_passe


#  Client Linux 
LINUX_CLIENT=192.168.x.x
LINUX_CLIENT_USER=user
LINUX_CLIENT_PASS=votre_mot_de_passe

# Réseaux à scanner
SCAN_NETWORKS=192.168.x.0/24,192.168.x.0/24
```


## 📚 Documentation

- Guide d'installation et d'utilisation : voir `Guide NTL-SysToolbox.pdf`
- Dossier explicatif : voir `Dossier technique.pdf`

## 👥 Équipe

Projet MSPR - Équipe de 4 étudiants
Durée: 19 heures de préparation

## 📄 Licence

Projet académique - Tous droits réservés

## 🆘 Support

Pour toute question ou problème:
1. Vérifier la configuration avec `python3 main.py` option 5
2. Consulter le guide utilisateur

---

**Version**: 1.0.0  
**Dernière mise à jour**: Février 2026

# ========================================
# FIN DE README.md
# ========================================
