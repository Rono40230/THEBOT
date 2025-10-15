"""
Launcher Callbacks - Gestion Centralisée des Callbacks du Launcher
Architecture MVC - Couche CONTROLLER conforme .clinerules
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html, no_update

# Imports des composants THEBOT
from ..components.market_status import market_status_manager
from ..core.alerts_manager import alerts_manager
from ..core.api_config import api_config
from ..data_providers.websocket_manager import ws_manager

# Import des callbacks des modals
from ..components.indicators_modal import register_indicators_modal_callbacks

# Import des managers de callbacks
from ..callbacks.managers.alerts_callbacks import AlertsCallbacks
from ..callbacks.managers.alert_modal_manager import AlertModalManager
from ..callbacks.managers.market_callbacks import MarketCallbacks
from ..callbacks.managers.market_modal_manager import MarketModalManager
from ..callbacks.managers.news_callbacks import NewsCallbacks
from ..callbacks.managers.news_modal_manager import NewsModalManager
from ..callbacks.managers.price_alerts_callbacks import PriceAlertsCallbacks
from ..callbacks.managers.trading_callbacks import TradingCallbacks
from ..callbacks.managers.trading_modal_manager import TradingModalManager

# Configuration du logging conforme .clinerules
logger = logging.getLogger(__name__)


class LauncherCallbacks:
    """
    Gestionnaire centralisé des callbacks du launcher

    Responsabilités selon .clinerules :
    - Single Responsibility : Callbacks du launcher uniquement
    - Type hints obligatoires
    - Logging structuré
    - Séparation des préoccupations
    """

    def __init__(
        self, app, modules: Dict[str, Any], layout_manager, data_manager
    ) -> None:
        """
        Initialise le gestionnaire de callbacks

        Args:
            app: Instance de l'application Dash
            modules: Dictionnaire des modules disponibles
            layout_manager: Gestionnaire de layouts
            data_manager: Gestionnaire de données
        """
        self.app = app
        self.modules = modules
        self.layout_manager = layout_manager
        self.data_manager = data_manager
        self.current_tab: str = "economic_news"
        self.logger: logging.Logger = logging.getLogger("thebot.launcher_callbacks")

        # Initialiser les managers de callbacks spécialisés
        self.alerts_callbacks = AlertsCallbacks(app)
        self.alert_modal_manager = AlertModalManager(app)
        self.market_modal_manager = MarketModalManager(app)
        self.news_modal_manager = NewsModalManager(app)
        self.trading_modal_manager = TradingModalManager(app)
        self.market_callbacks = MarketCallbacks(app)
        self.news_callbacks = NewsCallbacks(app)
        self.price_alerts_callbacks = PriceAlertsCallbacks(app)
        self.trading_callbacks = TradingCallbacks(app)

        self.logger.info("🔗 LauncherCallbacks initialisé")

    def register_all_callbacks(self) -> None:
        """
        Enregistre tous les callbacks du launcher

        Note:
            Méthode principale à appeler pour configurer tous les callbacks
        """
        try:
            self._register_market_status_callbacks()
            self._register_realtime_data_callbacks()
            self._register_navigation_callbacks()
            self._register_control_bar_callbacks()
            
            # Enregistrer les callbacks des modals
            register_indicators_modal_callbacks(self.app)
            
                        # Enregistrer les callbacks des alertes
            self.alerts_callbacks.register_all_callbacks()
            
            # Enregistrer les callbacks du modal d'alertes (MVC)
            self.alert_modal_manager.register_all_callbacks()
            
            # Enregistrer les callbacks du modal de marché (MVC)
            self.market_modal_manager.register_all_callbacks()
            
            # Enregistrer les callbacks du modal de news (MVC)
            self.news_modal_manager.register_all_callbacks()
            
            # Enregistrer les callbacks du modal de trading (MVC)
            self.trading_modal_manager.register_all_callbacks()
            
            # Enregistrer les callbacks du marché
            self.market_callbacks.register_all_callbacks()
            
            # Enregistrer les callbacks des news
            self.news_callbacks.register_all_callbacks()
            
            # Enregistrer les callbacks de trading
            self.trading_callbacks.register_all_callbacks()
            
            # Enregistrer les callbacks des alertes de prix
            self.price_alerts_callbacks.register_all_callbacks()

            # CALLBACKS PROBLÉMATIQUES SUPPRIMÉS CAR ILS CASSAIENT L'APPLICATION
            # self._register_symbol_selection_callbacks()  # ❌ INPUTS MANQUANTS
            # self._register_api_config_callbacks()        # ❌ CALLBACKS COMPLEXES
            # self._register_alerts_callbacks()            # ❌ CALLBACKS OPTIONNELS

            self.logger.info(
                "✅ Callbacks launcher enregistrés (callbacks problématiques supprimés)"
            )

        except Exception as e:
            self.logger.error(f"❌ Erreur enregistrement callbacks: {e}")
            raise

    def _register_market_status_callbacks(self) -> None:
        """Enregistre les callbacks de statut des marchés"""

        @self.app.callback(
            Output("market-status-badges", "children"),
            [Input("interval-component", "n_intervals")],
        )
        def update_market_status(n_intervals: int) -> List[Any]:
            """Met à jour les badges de statut des marchés"""
            try:
                return market_status_manager.get_all_market_badges()
            except Exception as e:
                self.logger.error(f"❌ Erreur mise à jour statut marchés: {e}")
                return [html.Span("Market Status Error", className="text-danger")]

    def _register_realtime_data_callbacks(self) -> None:
        """Enregistre les callbacks de données temps réel"""

        @self.app.callback(
            Output("realtime-data-store", "data"),
            [Input("main-symbol-selected", "data")],
        )
        def update_realtime_data(selected_symbol: Optional[str]) -> Dict[str, Any]:
            """Met à jour les données temps réel via WebSocket"""
            try:
                if not selected_symbol:
                    self.logger.debug("Aucun symbole sélectionné pour WebSocket")
                    return {}

                # Gérer le changement de symbole WebSocket
                current_connections = list(ws_manager.connections.keys())
                if current_connections and selected_symbol not in current_connections:
                    # Déconnecter les anciens symboles
                    for old_symbol in current_connections:
                        self.logger.debug(f"Déconnexion WebSocket: {old_symbol}")
                        ws_manager.unsubscribe(old_symbol)

                # S'assurer que WebSocket est connecté pour le symbole actuel
                if not ws_manager.is_connected(selected_symbol):
                    self.logger.debug(f"Connexion WebSocket: {selected_symbol}")
                    ws_manager.subscribe(selected_symbol)

                # Récupérer dernières données
                latest_data = ws_manager.get_latest_data(selected_symbol)

                if latest_data:
                    return {
                        "symbol": selected_symbol,
                        "price": latest_data.get("price", 0),
                        "change": latest_data.get("change", 0),
                        "volume": latest_data.get("volume", 0),
                        "timestamp": datetime.now().isoformat(),
                    }

                return {"symbol": selected_symbol, "status": "connecting"}

            except Exception as e:
                self.logger.error(f"❌ Erreur données temps réel: {e}")
                return {"error": str(e)}

    def _register_navigation_callbacks(self) -> None:
        """CALLBACKS SIMPLIFIÉS QUI MARCHENT"""

        print("🔄 ENREGISTREMENT CALLBACKS SIMPLIFIÉS...")
        self.logger.info("🔄 Enregistrement callbacks simplifiés")

        # CALLBACK 1: Navigation simple
        @self.app.callback(
            Output("modular-content", "children"),
            [Input("main-tabs", "active_tab")],
            prevent_initial_call=False,
        )
        def handle_tab_switch(active_tab: str):
            """Gère le changement d'onglets avec support COMPLET de tous les modules"""
            try:
                print(f"🔥 CALLBACK MARCHE! Onglet: {active_tab}")
                self.logger.info(f"🔥 Navigation vers: {active_tab}")

                # GESTION COMPLÈTE DE TOUS LES ONGLETS
                if active_tab == "economic_news":
                    print("✅ CHARGEMENT ECONOMIC NEWS")
                    if "economic_news" in self.modules:
                        module = self.modules["economic_news"]
                        if hasattr(module, "get_layout"):
                            return module.get_layout()
                    return self.layout_manager._generate_module_placeholder(
                        "economic_news"
                    )

                elif active_tab == "crypto_news":
                    print("✅ CHARGEMENT CRYPTO NEWS")
                    if "crypto_news" in self.modules:
                        module = self.modules["crypto_news"]
                        if hasattr(module, "get_layout"):
                            return module.get_layout()
                    return self.layout_manager._generate_module_placeholder(
                        "crypto_news"
                    )

                elif active_tab == "announcements_calendar":
                    print("✅ CHARGEMENT CALENDAR")
                    if "announcements_calendar" in self.modules:
                        module = self.modules["announcements_calendar"]
                        if hasattr(module, "get_layout"):
                            return module.get_layout()
                    return self.layout_manager._generate_module_placeholder("calendar")

                elif active_tab == "crypto":
                    print("✅ CHARGEMENT CRYPTO")
                    if "crypto" in self.modules:
                        module = self.modules["crypto"]
                        if hasattr(module, "get_layout"):
                            return module.get_layout()
                    return self.layout_manager._generate_module_placeholder("crypto")

                elif active_tab == "forex":
                    print("✅ CHARGEMENT FOREX")
                    if "forex" in self.modules:
                        module = self.modules["forex"]
                        if hasattr(module, "get_layout"):
                            return module.get_layout()
                    return self.layout_manager._generate_module_placeholder("forex")

                elif active_tab == "stocks":
                    print("✅ CHARGEMENT STOCKS")
                    if "stocks" in self.modules:
                        module = self.modules["stocks"]
                        if hasattr(module, "get_layout"):
                            return module.get_layout()
                    return self.layout_manager._generate_module_placeholder("stocks")

                elif active_tab == "strategies":
                    print("✅ CHARGEMENT STRATEGIES")
                    if "strategies" in self.modules:
                        module = self.modules["strategies"]
                        if hasattr(module, "get_layout"):
                            return module.get_layout()
                    return self.layout_manager._generate_module_placeholder(
                        "strategies"
                    )

                else:
                    print(f"⚠️ Onglet inconnu: {active_tab}")
                    return html.Div(
                        [
                            html.H4(
                                f"📊 Module: {active_tab}", className="text-center"
                            ),
                            html.P(
                                "Module en cours de développement",
                                className="text-center text-muted",
                            ),
                        ],
                        className="p-4",
                    )

            except Exception as e:
                print(f"❌ Erreur callback navigation: {e}")
                self.logger.error(f"❌ Erreur navigation: {e}")
                return html.Div(f"❌ Erreur: {e}", className="text-danger p-4")

        print("✅ CALLBACK NAVIGATION COMPLET ENREGISTRÉ!")
        self.logger.info("✅ Callback navigation avec support de tous les modules")

    def _register_control_bar_callbacks(self) -> None:
        """Enregistre les callbacks de la barre de contrôle"""

        @self.app.callback(
            Output("control-bar-content", "children"),
            [Input("main-tabs", "active_tab")],
        )
        def update_control_bar(active_tab: str) -> Any:
            """Affiche la barre de contrôle seulement pour certains onglets"""
            try:
                if active_tab == "strategies":
                    return self.layout_manager.create_control_bar()
                else:
                    return html.Div()
            except Exception as e:
                self.logger.error(f"❌ Erreur control bar: {e}")
                return html.Div()


# TOUS LES CALLBACKS PROBLÉMATIQUES SUPPRIMÉS POUR RÉPARER L'APPLICATION
# _register_symbol_selection_callbacks, _register_api_config_callbacks, _register_alerts_callbacks
# CES MÉTHODES CASSAIENT L'APPLICATION AVEC DES INPUTS MANQUANTS

# Export conforme .clinerules
__all__ = ["LauncherCallbacks"]
