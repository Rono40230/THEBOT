"""
crypto_news_module - Migration Phase 2
Stub temporaire pour compatibilité
"""

import logging
from typing import Any, Dict, Optional

from dash import html
from src.thebot.core.base_module import BaseModule
from src.thebot.core.logger import logger


class CryptoNewsModule(BaseModule):
    """Actualités crypto et analyse sentiment - Stub Phase 2"""

    def __init__(self):
        super().__init__("crypto_news_module")
        logger.info("📰 CryptoNewsModule initialisé (stub Phase 2)")

    def get_layout(self) -> html.Div:
        """Layout temporaire en cours de migration"""
        return html.Div([
            html.H3("📰 📰 Crypto News", style={"color": "white"}),
            html.P("Actualités crypto et analyse sentiment en cours de migration...",
                  style={"color": "gray"}),
            html.P("🔄 Phase 2 - Migration UI", style={"color": "orange"})
        ], style={"padding": "20px"})

    def setup_callbacks(self, app) -> None:
        """Configuration des callbacks - stub temporaire"""
        logger.info("🔧 Callbacks configurés (stub Phase 2)")
        pass

    def get_status(self) -> Dict[str, Any]:
        """Statut du module"""
        return {
            "name": "crypto_news",
            "status": "migrating",
            "phase": "2_ui_migration"
        }
        return {
            "name": "crypto_news_module",
            "status": "migrating",
            "phase": "2_ui_migration"
        }


# Instance globale temporaire
crypto_news_module = CryptoNewsModule()
