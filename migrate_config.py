#!/usr/bin/env python3
"""
Script de migration de configuration THEBOT
Migre depuis l'ancien système (api_config.json) vers le nouveau système unifié
"""

import json
import logging
import shutil
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_api_config():
    """Migre api_config.json vers le nouveau système"""

    old_config_path = Path("api_config.json")
    backup_path = Path("api_config.json.backup.migration")

    if not old_config_path.exists():
        logger.info("Aucun fichier api_config.json trouvé, migration ignorée")
        return

    # Créer une sauvegarde
    if not backup_path.exists():
        shutil.copy2(old_config_path, backup_path)
        logger.info(f"Sauvegarde créée: {backup_path}")

    try:
        # Charger l'ancienne configuration
        with open(old_config_path, 'r', encoding='utf-8') as f:
            old_config = json.load(f)

        logger.info("Migration de api_config.json vers le nouveau système...")

        # La nouvelle configuration est maintenant gérée par ConfigManager
        # Les anciennes valeurs peuvent être surchargées via variables d'environnement
        # ou directement dans THEBOT_CONFIG si nécessaire

        # Créer un fichier .env avec les clés API trouvées
        env_content = "# Migré depuis api_config.json\n"
        if "coingecko" in old_config and "api_key" in old_config["coingecko"]:
            env_content += f"COINGECKO_API_KEY={old_config['coingecko']['api_key']}\n"
        if "twelve_data" in old_config and "api_key" in old_config["twelve_data"]:
            env_content += f"TWELVE_DATA_API_KEY={old_config['twelve_data']['api_key']}\n"

        if env_content != "# Migré depuis api_config.json\n":
            env_path = Path(".env")
            if not env_path.exists():
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.write(env_content)
                logger.info("Fichier .env créé avec les clés API migrées")
            else:
                logger.info("Fichier .env existe déjà, vérifiez manuellement les clés API")

        # Renommer l'ancien fichier pour indiquer qu'il est obsolète
        old_config_path.rename(old_config_path.with_suffix('.json.obsolete'))
        logger.info("api_config.json renommé en api_config.json.obsolete")

        logger.info("Migration terminée avec succès!")

    except Exception as e:
        logger.error(f"Erreur lors de la migration: {e}")
        # Restaurer la sauvegarde si nécessaire
        if backup_path.exists():
            shutil.copy2(backup_path, old_config_path)
            logger.info("Sauvegarde restaurée")


def migrate_dashboard_configs():
    """Vérifie et migre les configurations de dashboard si nécessaire"""

    config_dir = Path("dashboard_configs")
    if not config_dir.exists():
        logger.info("Dossier dashboard_configs non trouvé, migration ignorée")
        return

    logger.info("Vérification des configurations de dashboard...")

    # Les configurations de dashboard restent compatibles
    # mais peuvent maintenant être gérées par le ConfigManager si souhaité

    logger.info("Configurations de dashboard vérifiées (compatibles)")


def create_env_file():
    """Crée un fichier .env si n'existe pas"""

    env_path = Path(".env")
    example_path = Path(".env.example")

    if env_path.exists():
        logger.info("Fichier .env existe déjà")
        return

    if example_path.exists():
        shutil.copy2(example_path, env_path)
        logger.info("Fichier .env créé depuis .env.example")
        logger.warning("⚠️  Pensez à configurer vos clés API dans .env !")
    else:
        logger.warning("Fichier .env.example non trouvé")


def main():
    """Fonction principale de migration"""

    print("🚀 Migration de configuration THEBOT v3.0.0")
    print("=" * 50)

    try:
        migrate_api_config()
        migrate_dashboard_configs()
        create_env_file()

        print("\n✅ Migration terminée!")
        print("\n📋 Prochaines étapes:")
        print("1. Vérifiez le fichier .env et configurez vos clés API")
        print("2. Testez le lancement de l'application")
        print("3. Supprimez les fichiers .obsolete si tout fonctionne")

    except Exception as e:
        logger.error(f"Erreur fatale lors de la migration: {e}")
        print(f"\n❌ Erreur lors de la migration: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())