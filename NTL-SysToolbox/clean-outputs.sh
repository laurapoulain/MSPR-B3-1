# ========================================
# Fichier: clean-outputs.sh
# Nettoie les anciens outputs
# ========================================
#!/bin/bash

echo "Nettoyage des anciens outputs..."

# Fonction pour demander confirmation
confirm() {
    read -p "$1 (o/N): " response
    case "$response" in
        [oO][uU][iI]|[oO])
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Compter les fichiers
backup_count=$(find out/backups -type f 2>/dev/null | wc -l)
diag_count=$(find out/diagnostics -type f 2>/dev/null | wc -l)
audit_count=$(find out/audits -type f 2>/dev/null | wc -l)

echo ""
echo "Fichiers trouvés:"
echo "  - Sauvegardes: $backup_count"
echo "  - Diagnostics: $diag_count"
echo "  - Audits: $audit_count"
echo ""

if confirm "Voulez-vous supprimer tous ces fichiers ?"; then
    rm -rf out/backups/*
    rm -rf out/diagnostics/*
    rm -rf out/audits/*
    echo "Outputs nettoyés"
else
    echo "Annulé"
fi

# ========================================
# FIN DE clean-outputs.sh
# ========================================