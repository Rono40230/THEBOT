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
            html.H3("₿ Module Crypto", style={"color": "#ffffff", "fontSize": "24px", "fontWeight": "bold", "backgroundColor": "#333333", "padding": "10px", "border": "2px solid #ff6b35"}),
            html.P("Trading crypto avec indicateurs avancés en cours de migration...",
                  style={"color": "#00ff00", "fontSize": "16px", "backgroundColor": "#222222", "padding": "10px", "border": "1px solid #00ff00"}),
            html.P("🔄 Phase 2 - Migration UI", style={"color": "#ff6b35", "fontSize": "14px", "backgroundColor": "#444444", "padding": "10px", "border": "1px solid #ff6b35"})
        ], style={"padding": "20px", "backgroundColor": "#000000", "minHeight": "200px", "border": "3px solid #ffffff"})

    def setup_callbacks(self, app) -> None:
        """Configuration des callbacks - stub temporaire"""
        logger.info("🔧 Callbacks CryptoModule configurés (stub Phase 2)")
        pass


# Instance globale temporaire
crypto_module = CryptoModule()