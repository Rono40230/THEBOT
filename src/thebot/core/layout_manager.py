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

    def create_main_layout(self, modules: Optional[Dict[str, Any]] = None) -> html.Div:
        """Créer le layout principal avec onglets pour chaque module"""
        try:
            # Configuration de base
            tabs_content = []

            if modules:
                # Créer un onglet pour chaque module
                for module_name, module in modules.items():
                    if hasattr(module, 'get_layout'):
                        try:
                            module_layout = module.get_layout()
                            tab_label = self._get_tab_label(module_name)

                            tabs_content.append(
                                dcc.Tab(
                                    label=tab_label,
                                    value=module_name,  # Valeur unique pour chaque onglet
                                    children=module_layout,
                                    style={"padding": "10px"}
                                )
                            )
                        except Exception as e:
                            logger.error(f"❌ Erreur layout module {module_name}: {e}")
                            # Onglet d'erreur
                            tabs_content.append(
                                dcc.Tab(
                                    label=f"❌ {module_name}",
                                    children=html.Div([
                                        html.H4(f"Erreur module {module_name}"),
                                        html.P(f"Erreur: {str(e)}", style={"color": "red"})
                                    ], style={"padding": "20px"})
                                )
                            )
            else:
                # Layout temporaire si pas de modules
                tabs_content.append(
                    dcc.Tab(
                        label="🏠 Accueil",
                        children=html.Div([
                            html.H1("THEBOT - Phase 2 Migration", style={"color": "white", "textAlign": "center"}),
                            html.P("Application en cours de migration vers architecture unifiée...",
                                  style={"color": "gray", "textAlign": "center"})
                        ], style={"padding": "20px"})
                    )
                )

            # Layout principal avec onglets
            layout = html.Div([
                # En-tête
                html.Div([
                    html.H1("THEBOT v1.0.0-phase6", style={"color": "white", "textAlign": "center", "margin": "10px"}),
                    html.P("🚀 Performance optimisée - Debouncer, Cache, Circuit Breaker",
                          style={"color": "lightgreen", "textAlign": "center", "fontSize": "14px"})
                ], style={"backgroundColor": "#0d1117", "padding": "10px"}),

                # Onglets principaux
                html.Div([
                    dcc.Tabs(
                        id="main-tabs",
                        value="crypto",  # Onglet actif par défaut
                        children=[
                            dcc.Tab(label=self._get_tab_label(module_name), value=module_name)
                            for module_name, module in modules.items()
                            if hasattr(module, 'get_layout')
                        ],
                        style={
                            "backgroundColor": "#161b22",
                            "border": "1px solid #30363d"
                        },
                        colors={
                            "border": "#30363d",
                            "primary": "#58a6ff",
                            "background": "#0d1117"
                        }
                    ),
                    html.Div(id="tab-content", style={"padding": "20px", "minHeight": "300px"})
                ])
            ], style={
                "backgroundColor": self.app_config["background_color"],
                "minHeight": self.app_config["min_height"],
                "fontFamily": self.app_config["font_family"]
            })

            logger.info(f"✅ Layout créé avec {len(tabs_content)} onglets")
            return layout

        except Exception as e:
            logger.error(f"❌ Erreur création layout: {e}")
            # Layout d'urgence
            return html.Div([
                html.H1("❌ Erreur Layout THEBOT", style={"color": "red", "textAlign": "center"}),
                html.P(f"Erreur: {str(e)}", style={"color": "white", "textAlign": "center"})
            ], style={"backgroundColor": "#0d1117", "minHeight": "100vh"})

    def _get_tab_label(self, module_name: str) -> str:
        """Retourne le label d'onglet pour un module"""
        labels = {
            "crypto": "₿ Crypto",
            "forex": "💱 Forex",
            "stocks": "📊 Stocks",
            "economic_news": "📈 Economic News",
            "crypto_news": "📰 Crypto News",
            "announcements_calendar": "📅 Calendar",
            "strategies": "🎯 Strategies"
        }
        return labels.get(module_name, module_name.title())

    def get_status(self) -> Dict[str, Any]:
        """Statut du layout manager"""
        return {
            "status": "initializing",
            "phase": "2_migration",
            "config_loaded": bool(self.app_config)
        }


# Instance globale temporaire
layout_manager = LayoutManager()