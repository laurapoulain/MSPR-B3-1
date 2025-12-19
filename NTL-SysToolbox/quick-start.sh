# ========================================
# Fichier: quick-start.sh
# Script de démarrage rapide
# ========================================
#!/bin/bash

echo "╔════════════════════════════════════════╗"
echo "║   NTL-SysToolbox - Quick Start   ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "Environnement virtuel non trouvé"
    echo "   Lancez: make install"
    exit 1
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier la configuration
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé"
    echo "   Copie de .env.example vers .env..."
    cp .env.example .env
    echo "   ⚠️  N'oubliez pas de configurer .env avant d'utiliser l'outil"
fi

# Lancer l'application
cd Dev
python3 main.py

