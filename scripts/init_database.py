#!/usr/bin/env python3
"""
Script d'initialisation de la base de données THEBOT
Crée les tables et insère les données initiales
"""

import logging
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from dash_modules.services.database_service import database_service

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Fonction principale d'initialisation"""
    try:
        logger.info("🚀 Initialisation de la base de données THEBOT...")

        # Initialiser la base de données
        database_service.initialize_database()

        # Afficher les statistiques
        stats = database_service.get_stats()
        logger.info("📊 Statistiques de la base de données:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")

        logger.info("✅ Base de données initialisée avec succès!")

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
