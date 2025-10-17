"""
Strategies Module - Migration Phase 2
Stub temporaire pour compatibilité
"""

import logging
from typing import Any, Dict, Optional

from dash import html
from src.thebot.core.base_module import BaseModule
from src.thebot.core.logger import logger


class StrategiesModule(BaseModule):
    """Stratégies de trading automatisées - Stub Phase 2"""

    def __init__(self, calculators=None):
        super().__init__("strategies")
        logger.info("🎯 StrategiesModule initialisé (stub Phase 2)")

    def get_layout(self) -> html.Div:
        """Layout temporaire en cours de migration"""
        return html.Div([
            html.H3("🎯 Strategies", style={"color": "#ffffff", "fontSize": "24px", "fontWeight": "bold"}),
            html.P("Stratégies de trading automatisées en cours de migration...",
                  style={"color": "#cccccc", "fontSize": "16px"}),
            html.P("🔄 Phase 2 - Migration UI", style={"color": "#ff6b35", "fontSize": "14px"})
        ], style={"padding": "20px", "backgroundColor": "#1a1a1a", "minHeight": "200px"})

    def setup_callbacks(self, app) -> None:
        """Configuration des callbacks - stub temporaire"""
        logger.info("🎯 Callbacks StrategiesModule configurés (stub Phase 2)")
        pass

    def get_status(self) -> Dict[str, Any]:
        """Statut du module"""
        return {
            "name": "strategies",
            "status": "migrating",
            "phase": "2_ui_migration"
        }


# Instance globale temporaire
strategies_module = StrategiesModule()
