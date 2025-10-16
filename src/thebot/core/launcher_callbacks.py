"""
Launcher Callbacks - Gestion Centralisée des Callbacks du Launcher
Architecture MVC - Couche CONTROLLER conforme .clinerules
"""

import logging
from typing import Any, Dict, List, Optional

from src.thebot.core.logger import logger

# Stub temporaire pour la migration - sera complété dans Phase 2
class LauncherCallbacks:
    """
    Gestionnaire centralisé des callbacks du launcher
    Version temporaire pour migration Phase 2
    """

    def __init__(self, app=None):
        self.app = app
        logger.info("🔧 LauncherCallbacks initialisé (stub Phase 2)")

    def register_callbacks(self):
        """Enregistrer tous les callbacks - stub temporaire"""
        logger.info("📝 Callbacks enregistrés (stub Phase 2)")
        pass

    def get_status(self) -> Dict[str, Any]:
        """Statut du launcher"""
        return {
            "status": "initializing",
            "callbacks_registered": False,
            "phase": "2_migration"
        }


# Instance globale temporaire
launcher_callbacks = LauncherCallbacks()