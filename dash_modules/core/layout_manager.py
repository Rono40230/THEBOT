from src.thebot.core.logger import logger
"""
Layout Manager - Gestion Centralisée des Interfaces THEBOT
Architecture MVC - Couche VIEW conforme .clinerules
"""

import logging
from typing import Any, Dict, List, Optional, Union

import dash_bootstrap_components as dbc
from dash import dcc, html

# Imports des composants THEBOT
from ..components.market_status import market_status_manager
from ..components.symbol_search import default_symbol_search
from ..core.api_config import api_config

# Configuration du logging conforme .clinerules
logger = logging.getLogger(__name__)


class LayoutManager:
    """
    Gestionnaire centralisé des layouts et composants UI

    Responsabilités selon .clinerules :
    - Single Responsibility : Gestion de l'interface uniquement
    - Type hints obligatoires
    - Logging structuré
    - Séparation des préoccupations UI
    """

    def __init__(self) -> None:
        """Initialise le gestionnaire de layouts"""
        self.logger: logging.Logger = logging.getLogger("thebot.layout_manager")
        self.app_config: Dict[str, Any] = self._get_default_app_config()

        self.logger.info("🎨 LayoutManager initialisé")

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

    def create_header(self) -> dbc.Row:
        """
        Crée le header avec navigation modulaire

        Returns:
            dbc.Row: Header complet avec navigation et statuts
        """
        try:
            return dbc.Row(
                [
                    # Navigation principale - Onglets modulaires
                    dbc.Col(
                        [
                            dbc.Tabs(
                                [
                                    dbc.Tab(
                                        label="📰 News Éco", tab_id="economic_news"
                                    ),
                                    dbc.Tab(
                                        label="🪙 News Crypto", tab_id="crypto_news"
                                    ),
                                    dbc.Tab(
                                        label="📅 Calendrier",
                                        tab_id="announcements_calendar",
                                    ),
                                    dbc.Tab(label="₿ Crypto", tab_id="crypto"),
                                    dbc.Tab(label="💱 Forex", tab_id="forex"),
                                    dbc.Tab(label="📈 Stocks", tab_id="stocks"),
                                    dbc.Tab(label="🎯 Strategies", tab_id="strategies"),
                                ],
                                id="main-tabs",
                                active_tab="economic_news",
                                className="mb-0",
                            )
                        ],
                        width=7,
                    ),
                    # Indicateurs de marchés globaux et API Keys
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    # Utilisation du module market_status
                                    html.Div(
                                        market_status_manager.get_all_market_badges(),
                                        id="market-status-badges",
                                        className="d-inline-flex",
                                    ),
                                    dbc.Button(
                                        [
                                            html.I(className="fas fa-key me-1"),
                                            "🔑 API Keys",
                                        ],
                                        color="dark",
                                        size="sm",
                                        outline=True,
                                        className="ms-3",
                                        id="open-api-config-btn",
                                    ),
                                ],
                                className="d-flex justify-content-end align-items-center",
                            )
                        ],
                        width=5,
                    ),
                ],
                className="border-bottom border-secondary pb-2 mb-2",
            )

        except Exception as e:
            self.logger.error(f"❌ Erreur création header: {e}")
            return dbc.Row([html.Div("Header Error", className="text-danger")])

    def create_control_bar(self) -> dbc.Row:
        """
        Crée la barre de contrôle avec sélecteurs principaux

        Returns:
            dbc.Row: Barre de contrôle complète
        """
        try:
            return dbc.Row(
                [
                    # Composant de recherche de symbole
                    default_symbol_search.get_complete_layout(),
                    dbc.Col(
                        [
                            dbc.Label(
                                "Analysis Type", className="fw-bold text-light small"
                            ),
                            dcc.Dropdown(
                                id="analysis-selector",
                                options=[
                                    {
                                        "label": "🔧 Technical Only",
                                        "value": "technical",
                                    },
                                    {"label": "🧠 AI Enhanced", "value": "ai"},
                                    {
                                        "label": "📅 Economic Impact",
                                        "value": "economic",
                                    },
                                    {"label": "🎯 Full Spectrum", "value": "full"},
                                ],
                                value="technical",
                                className="dash-bootstrap",
                                style={
                                    "backgroundColor": "#2c2c2e",
                                    "color": "#ffffff",
                                },
                            ),
                        ],
                        width=2,
                    ),
                ],
                className="bg-dark p-3 rounded border border-secondary mb-3",
            )

        except Exception as e:
            self.logger.error(f"❌ Erreur création control bar: {e}")
            return dbc.Row([html.Div("Control Bar Error", className="text-danger")])

    # create_sidebar et méthodes associées supprimées - non demandées par l'utilisateur

    def create_footer(self) -> html.Footer:
        """
        Crée le footer de l'application

        Returns:
            html.Footer: Footer avec informations de statut
        """
        return html.Footer(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Small(
                                    [
                                        "THEBOT v2.0 | ",
                                        html.Span(
                                            id="connection-status",
                                            children="🟢 Connected",
                                        ),
                                        " | Last Update: ",
                                        html.Span(
                                            id="last-update-time", children="--:--:--"
                                        ),
                                    ],
                                    className="text-muted",
                                )
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                html.Small(
                                    [
                                        "Data Sources: Binance, CoinGecko | ",
                                        html.Span(
                                            id="data-quality", children="🟢 Good"
                                        ),
                                    ],
                                    className="text-muted text-end",
                                )
                            ],
                            width=6,
                        ),
                    ]
                )
            ],
            className="border-top border-secondary pt-2 mt-4",
        )

    # create_modular_content supprimé - conflit d'ID résolu

    def _get_default_module_content(self, modules: Dict = None) -> html.Div:
        """
        GÉNÈRE des contenus par défaut pour TOUS les modules
        """
        try:
            logger.info("🔄 GÉNÉRATION CONTENU PAR DÉFAUT POUR TOUS LES MODULES...")
            self.logger.info("🔄 Génération contenu par défaut - tous modules")

            # Créer le contenu du module economic_news (qui fonctionne déjà)
            if modules and "economic_news" in modules:
                module = modules["economic_news"]
                logger.info(f"✅ Module economic_news trouvé: {type(module)}")

                if hasattr(module, "get_layout"):
                    logger.info("✅ Layout economic_news chargé...")
                    layout = module.get_layout()
                    self.logger.info("✅ Layout economic_news chargé avec succès")
                    return layout

            # Si pas de module economic_news, fallback générique
            return html.Div(
                [
                    html.H4("📰 ACTUALITÉS ÉCONOMIQUES", className="text-primary mb-3"),
                    html.P(
                        "⚠️ Module en cours de chargement...", className="text-warning"
                    ),
                    html.Div(
                        [
                            html.H5("🔧 Status Application:", className="mb-2"),
                            html.Ul(
                                [
                                    html.Li("✅ Architecture MVC fonctionnelle"),
                                    html.Li("✅ 7 modules initialisés"),
                                    html.Li("✅ Navigation réparée"),
                                    html.Li("⚠️ Contenu en cours de chargement"),
                                ]
                            ),
                        ],
                        className="bg-light p-3 rounded mt-3",
                    ),
                ],
                className="p-4",
            )

        except Exception as e:
            self.logger.error(f"❌ Erreur génération contenu par défaut: {e}")
            logger.info(f"❌ ERREUR: {e}")
            return html.Div("Erreur chargement contenu", className="text-danger")

    def _generate_module_placeholder(self, module_name: str) -> html.Div:
        """Génère un placeholder simple pour un module"""
        return html.Div(
            [
                html.H2(
                    f"📊 Module {module_name.title()}", className="text-center mb-4"
                ),
                html.Div(
                    [
                        html.P(
                            f"✅ Module {module_name} chargé avec succès",
                            className="text-center mb-3",
                        ),
                        html.Div(
                            [
                                dbc.Badge(
                                    "🔄 Architecture MVC",
                                    color="success",
                                    className="me-2",
                                ),
                                dbc.Badge(
                                    "⚡ Callbacks actifs",
                                    color="info",
                                    className="me-2",
                                ),
                                dbc.Badge("📊 Données en temps réel", color="warning"),
                            ],
                            className="text-center",
                        ),
                    ],
                    className="p-4 bg-light rounded",
                ),
            ],
            className="container-fluid p-4",
        )

    def get_main_layout(
        self, all_symbols: List[str], default_data: Dict[str, Any], modules: Dict = None
    ) -> dbc.Container:
        """
        Crée le layout principal complet de l'application

        Args:
            all_symbols: Liste de tous les symboles disponibles
            default_data: Données par défaut pour les stores
            modules: Dictionnaire des modules disponibles

        Returns:
            dbc.Container: Layout principal complet
        """
        try:
            # Contenu par défaut : module economic_news
            default_content = self._get_default_module_content(modules)

            return dbc.Container(
                [
                    # ===== HEADER =====
                    self.create_header(),
                    # ===== CONTROL BAR (conditionnelle) =====
                    html.Div(id="control-bar-content"),
                    # ===== MAIN CONTENT =====
                    dbc.Row(
                        [
                            # Sidebar gauche (supprimée - non demandée)
                            dbc.Col(
                                [html.Div(id="sidebar-content", children=[])],
                                width=0,
                                className="pe-0",
                                id="sidebar-col",
                            ),  # Largeur 0 par défaut
                            # Zone principale modulaire
                            dbc.Col(
                                [
                                    html.Div(
                                        id="modular-content", children=default_content
                                    )
                                ],
                                width=12,
                                className="ps-2",
                                id="main-content-col",
                            ),  # Pleine largeur par défaut
                        ],
                        className="g-0 mt-3",
                    ),
                    # ===== FOOTER STATUS =====
                    self.create_footer(),
                    # ===== API CONFIGURATION MODAL =====
                    api_config.get_api_config_modal(),
                    # ===== SYSTÈME D'ALERTES =====
                    self._create_alerts_system(),
                    # ===== STORES ET INTERVALS =====
                    self._create_data_stores(all_symbols, default_data),
                ],
                fluid=True,
                className="dbc dbc-ag-grid",
                style={
                    "fontFamily": self.app_config["font_family"],
                    "backgroundColor": self.app_config["background_color"],
                    "minHeight": self.app_config["min_height"],
                },
            )

        except Exception as e:
            self.logger.error(f"❌ Erreur création layout principal: {e}")
            return dbc.Container(
                [
                    html.Div(
                        "Layout Error - Check logs",
                        className="text-danger text-center p-5",
                    )
                ]
            )

    def _create_alerts_system(self) -> html.Div:
        """Crée le système d'alertes"""
        return html.Div(
            [
                # Container pour les notifications d'alertes
                html.Div(
                    id="alerts-notification-container",
                    children=[],
                    style={
                        "position": "fixed",
                        "top": "20px",
                        "right": "20px",
                        "zIndex": "9999",
                        "width": "350px",
                        "maxHeight": "80vh",
                        "overflowY": "auto",
                    },
                ),
                # Store pour le statut du monitoring
                dcc.Store(
                    id="alerts-monitoring-status",
                    data={"active": False, "last_check": None},
                ),
                # Interval pour le système d'alertes
                dcc.Interval(
                    id="alerts-monitoring-interval",
                    interval=15 * 1000,  # 15 secondes
                    n_intervals=0,
                    disabled=False,
                ),
            ]
        )

    def _create_data_stores(
        self, all_symbols: List[str], default_data: Dict[str, Any]
    ) -> html.Div:
        """Crée les stores et intervals de données"""
        return html.Div(
            [
                # Stores pour données
                dcc.Store(
                    id="market-data-store", data=default_data.get("market_data", {})
                ),
                dcc.Store(id="indicators-store", data={}),
                dcc.Store(id="settings-store", data=default_data.get("settings", {})),
                dcc.Store(id="main-symbol-selected", data="BTCUSDT"),
                dcc.Store(id="symbols-cache-store", data=all_symbols),
                dcc.Store(id="realtime-data-store", data={}),
                # Intervals pour mises à jour
                dcc.Interval(
                    id="interval-component",
                    interval=60 * 1000,  # 60 secondes
                    n_intervals=0,
                ),
                dcc.Interval(
                    id="realtime-interval",
                    interval=5000,  # 5 secondes
                    n_intervals=0,
                    disabled=False,
                ),
            ]
        )

    def get_custom_css(self) -> str:
        """
        Retourne le CSS personnalisé

        Returns:
            str: Styles CSS pour l'application
        """
        return """
            /* CSS Custom THEBOT */
            .dash-bootstrap {
                font-family: 'Inter', sans-serif;
            }
            
            .crypto-dropdown-white .Select-control {
                background-color: #2c2c2e !important;
                border: 1px solid #6c757d !important;
                color: #ffffff !important;
            }
            
            .crypto-dropdown-white .Select-placeholder {
                color: #ffffff !important;
            }
            
            .crypto-dropdown-white .Select-value-label {
                color: #ffffff !important;
            }
            
            .crypto-dropdown-white div[class*="menu"] {
                background-color: #2c2c2e !important;
                border: 1px solid #6c757d !important;
            }
            
            .crypto-dropdown-white div[class*="option"] {
                background-color: #2c2c2e !important;
                color: #ffffff !important;
            }
            
            .crypto-dropdown-white div[class*="option"]:hover {
                background-color: #495057 !important;
                color: #ffffff !important;
            }
            
            /* Animations */
            .fade-in {
                animation: fadeIn 0.3s ease-in;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
        """

    def update_config(self, **kwargs) -> None:
        """
        Met à jour la configuration de l'interface

        Args:
            **kwargs: Options de configuration à mettre à jour
        """
        for key, value in kwargs.items():
            if key in self.app_config:
                self.app_config[key] = value
                self.logger.info(f"🔧 Config mise à jour: {key} = {value}")


# Instance globale singleton
layout_manager = LayoutManager()

# Export conforme .clinerules
__all__ = ["LayoutManager", "layout_manager"]
