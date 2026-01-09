#!/bin/bash
echo "=== Installation de NTL-SysToolbox ==="

# Mise à jour et dépendances
sudo apt update -y
sudo apt install -y mysql-client python3-venv nmap


# Création environnement virtuel
python3 -m venv ~/venv_ntl
source ~/venv_ntl/bin/activate

# Installation des dépendances
pip install --upgrade pip
pip install -r .requirements.txt

# Message de confirmation
echo "=== Installation terminée ==="
echo "Environnement virtuel activé."

# Lancement automatique du menu principal
echo "Lancement du menu CLI..."
#python3 Dev/main.py
# le module 3 nécessite des droits root pour certaines commandes, donc on lance le  script avec sudo, en forçant sudo à utiliser le python de l'environnement virtuel
sudo $(which python3) Dev/main.py

# Fin du script
echo "=== Fin du script setup ==="
