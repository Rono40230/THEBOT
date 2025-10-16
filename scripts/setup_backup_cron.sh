#!/bin/bash
# Script d'installation des tâches cron pour les sauvegardes - Phase 5

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_SCRIPT="$SCRIPT_DIR/backup_database.py"

echo "🔧 Configuration des sauvegardes automatiques THEBOT"

# Vérifier que le script de sauvegarde existe
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "❌ Script de sauvegarde non trouvé: $BACKUP_SCRIPT"
    exit 1
fi

# Demander la fréquence de sauvegarde
echo "Fréquence de sauvegarde:"
echo "1) Quotidienne (recommandé)"
echo "2) Hebdomadaire"
echo "3) Personnalisée"
read -p "Choix [1]: " choice
choice=${choice:-1}

case $choice in
    1)
        cron_schedule="0 2 * * *"
        echo "✅ Sauvegarde quotidienne à 2h00"
        ;;
    2)
        cron_schedule="0 2 * * 0"
        echo "✅ Sauvegarde hebdomadaire le dimanche à 2h00"
        ;;
    3)
        read -p "Expression cron (ex: '0 2 * * *' pour 2h00 tous les jours): " cron_schedule
        ;;
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac

# Créer la commande cron
cron_command="$cron_schedule cd $PROJECT_DIR && $BACKUP_SCRIPT --run >> /var/log/thebot_backup.log 2>&1"

# Vérifier si la tâche existe déjà
if crontab -l 2>/dev/null | grep -q "backup_database.py"; then
    echo "⚠️ Une tâche de sauvegarde existe déjà. Voulez-vous la remplacer?"
    read -p "Oui/Non [Non]: " replace
    if [[ $replace =~ ^[Oo][Uu][Ii]$ ]]; then
        # Supprimer l'ancienne tâche
        crontab -l 2>/dev/null | grep -v "backup_database.py" | crontab -
    else
        echo "✅ Annulé"
        exit 0
    fi
fi

# Ajouter la nouvelle tâche
(crontab -l 2>/dev/null; echo "$cron_command") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Tâche cron configurée avec succès"
    echo "📅 Prochaine exécution: $(date -d "now + 1 day" "+%Y-%m-%d") à 02:00"
    echo ""
    echo "Pour voir les tâches cron: crontab -l"
    echo "Pour modifier: crontab -e"
    echo "Logs: tail -f /var/log/thebot_backup.log"
else
    echo "❌ Erreur lors de la configuration de la tâche cron"
    exit 1
fi

# Créer le répertoire de logs si nécessaire
sudo mkdir -p /var/log
sudo touch /var/log/thebot_backup.log
sudo chmod 644 /var/log/thebot_backup.log

echo ""
echo "🎉 Configuration terminée!"
echo "Le script de sauvegarde s'exécutera automatiquement selon le planning défini."
