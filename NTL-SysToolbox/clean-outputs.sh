#!/bin/bash
# ========================================
# Nettoie les anciens fichiers générés
# ========================================

echo "=== Nettoyage des outputs générés ==="

# Fonction de confirmation
confirm() {
    while true; do
        read -p "$1 [o/N] : " response
        case "$response" in
            [oO]|[oO][uU][iI])
                return 0
                ;;
            [nN]|"")
                return 1
                ;;
            *)
                echo "Réponse invalide. Tapez 'o' pour oui ou 'n' pour non."
                ;;
        esac
    done
}

# Dossiers utilisés
BACKUPS_DIR="backups"
OUTPUTS_DIR="outputs"

# Comptage des fichiers
backup_count=$(find "$BACKUPS_DIR" -type f 2>/dev/null | wc -l)
outputs_count=$(find "$OUTPUTS_DIR" -type f 2>/dev/null | wc -l)

echo ""
echo "Fichiers trouvés :"
echo "  - Sauvegardes MySQL : $backup_count"
echo "  - Rapports et exports : $outputs_count"
echo ""

# # Rien à faire ?
# if [[ "$backup_count" -eq 0 && "$outputs_count" -eq 0 ]]; then
#     echo "Aucun fichier à supprimer."
#     echo "=== Fin du nettoyage ==="
#     exit 0
# fi

# Confirmation
if confirm "Souhaitez-vous supprimer TOUS ces fichiers ?"; then
    [ -d "$BACKUPS_DIR" ] && rm -rf "$BACKUPS_DIR"/*
    [ -d "$OUTPUTS_DIR" ] && rm -rf "$OUTPUTS_DIR"/*
    echo "Outputs nettoyés avec succès."
else
    echo "Opération annulée."
fi

echo "=== Fin du nettoyage ==="
