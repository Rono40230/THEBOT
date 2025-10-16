"""
Data Manager Compatibility Module - Phase 1 THEBOT
Stub module pour maintenir la compatibilité avec dash_modules.core.data_manager
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DataManager:
    """Gestionnaire de données simplifié"""

    def __init__(self):
        self.data = {}
        logger.info("📊 DataManager initialisé (stub)")

    def get_data(self, key: str) -> Optional[Any]:
        """Récupérer des données"""
        return self.data.get(key)

    def set_data(self, key: str, value: Any):
        """Stocker des données"""
        self.data[key] = value

    def clear_data(self):
        """Vider les données"""
        self.data.clear()


# Instance globale
data_manager = DataManager()

__all__ = ["DataManager", "data_manager"]