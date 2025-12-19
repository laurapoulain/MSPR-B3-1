# ========================================
# Fichier: test-all.sh
# Script de test complet
# ========================================
#!/bin/bash

set -e

echo "╔════════════════════════════════════════╗"
echo "║     Tests NTL-SysToolbox           ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Activer l'environnement virtuel
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo " Environnement virtuel non trouvé"
    exit 1
fi

# Fonction pour afficher le résultat
check_result() {
    if [ $? -eq 0 ]; then
        echo "  ✅ $1"
    else
        echo "  ❌ $1"
        exit 1
    fi
}

echo " Tests des modules..."
echo ""

# Test 1: Module config
echo "1. Test du module config..."
python3 Dev/config.py > /dev/null 2>&1
check_result "Module config"

# Test 2: Module utils
echo "2. Test du module utils..."
python3 Dev/utils.py > /dev/null 2>&1
check_result "Module utils"

# Test 3: Module save (connexion)
echo "3. Test de connexion MySQL..."
python3 -c "
import sys
sys.path.insert(0, 'Dev')
from save import WMSBackup
backup = WMSBackup()
result = backup.test_connection()
sys.exit(0 if result['status'] == 'success' else 1)
" > /dev/null 2>&1
check_result "Connexion MySQL"

# Test 4: Liste des tables
echo "4. Test liste des tables..."
python3 -c "
import sys
sys.path.insert(0, 'Dev')
from save import WMSBackup
backup = WMSBackup()
result = backup.list_tables()
sys.exit(0 if result['status'] == 'success' else 1)
" > /dev/null 2>&1
check_result "Liste des tables"

# Test 5: Sauvegarde de test
echo "5. Test sauvegarde structure..."
python3 -c "
import sys
sys.path.insert(0, 'Dev')
from save import WMSBackup
backup = WMSBackup()
result = backup.backup_full_sql(include_data=False)
sys.exit(0 if result['status'] == 'success' else 1)
" > /dev/null 2>&1
check_result "Sauvegarde structure"

# Test 6: Export CSV
echo "6. Test export CSV..."
python3 -c "
import sys
sys.path.insert(0, 'Dev')
from save import WMSBackup
backup = WMSBackup()
result = backup.export_table_to_csv('warehouses', limit=5)
sys.exit(0 if result['status'] == 'success' else 1)
" > /dev/null 2>&1
check_result "Export CSV"

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   ✅  Tous les tests sont passés !    ║"
echo "╚════════════════════════════════════════╝"

# ========================================
# FIN DE test-all.sh
# ========================================