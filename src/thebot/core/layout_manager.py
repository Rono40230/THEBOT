"""
Layout Manager - Gestion Centralisée des Interfaces THEBOT
Architecture MVC - Couche VIEW conforme .clinerules
"""

import logging
from typing import Any, Dict, List, Optional, Union

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.thebot.core.logger import logger


class LayoutManager:
    """
    Gestionnaire centralisé des layouts et composants UI
    Version temporaire pour migration Phase 2
    """

    def __init__(self) -> None:
        """Initialise le gestionnaire de layouts"""
        self.app_config: Dict[str, Any] = self._get_default_app_config()
        logger.info("🎨 LayoutManager initialisé (Phase 2)")

    def _get_default_app_config(self) -> Dict[str, Any]:
        """Configuration par défaut de l'application"""
        return {
            "font_family": "Inter, sans-serif",
            "background_color": "#0d1117",
            "min_height": "100vh",
            "sidebar_width": 3,
            "main_content_width": 9,
            "default_tab": "economic_news",
        }

    def create_main_layout(self) -> html.Div:
        """Créer le layout principal - stub temporaire"""
        return html.Div([
            html.H1("THEBOT - Phase 2 Migration", style={"color": "white", "textAlign": "center"}),
            html.P("Application en cours de migration vers architecture unifiée...",
                  style={"color": "gray", "textAlign": "center"})
        ], style={"backgroundColor": self.app_config["background_color"], "minHeight": self.app_config["min_height"]})

    def get_status(self) -> Dict[str, Any]:
        """Statut du layout manager"""
        return {
            "status": "initializing",
            "phase": "2_migration",
            "config_loaded": bool(self.app_config)
        }


# Instance globale temporaire
layout_manager = LayoutManager()