"""
Crypto Module - Migration Phase 2
Stub temporaire pour compatibilité
"""

import logging
from typing import Any, Dict, Optional

from dash import html
from src.thebot.core.base_module import BaseModule
from src.thebot.core.logger import logger


class CryptoModule(BaseModule):
    """Module crypto - Stub Phase 2"""

    def __init__(self):
        super().__init__("crypto")
        logger.info("₿ CryptoModule initialisé (stub Phase 2)")

    def get_layout(self) -> html.Div:
        """Layout temporaire en cours de migration"""
        return html.Div([
            html.H3("₿ Module Crypto", style={"color": "white"}),
            html.P("Trading crypto avec indicateurs avancés en cours de migration...",
                  style={"color": "gray"}),
            html.P("🔄 Phase 2 - Migration UI", style={"color": "orange"})
        ], style={"padding": "20px"})

    def setup_callbacks(self, app) -> None:
        """Configuration des callbacks - stub temporaire"""
        logger.info("🔧 Callbacks CryptoModule configurés (stub Phase 2)")
        pass


# Instance globale temporaire
crypto_module = CryptoModule()