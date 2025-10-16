from src.thebot.core.logger import logger
"""
Trading Callbacks Manager - Gestionnaire centralisé des callbacks trading
Regroupe tous les callbacks liés au trading et aux décisions d'investissement
"""

import logging
from typing import Any, Dict, List, Optional

from dash import Input, Output, State, callback, html

from ..base.callback_manager import CallbackManager
from ..base.callback_registry import get_callback_registry

logger = logging.getLogger(__name__)


class TradingCallbacks(CallbackManager):
    """
    Gestionnaire centralisé des callbacks pour le trading.
    Regroupe les callbacks liés aux décisions de trading et modaux de trading.
    """

    def __init__(self, app, trading_manager=None):
        """
        Initialise le gestionnaire de callbacks trading.

        Args:
            app: Instance de l'application Dash
            trading_manager: Gestionnaire de trading
        """
        super().__init__(app, "TradingCallbacks")
        self.trading_manager = trading_manager
        self.registry = get_callback_registry()

    def register_all_callbacks(self) -> None:
        """Enregistre tous les callbacks trading."""
        logger.info("🔄 Enregistrement des callbacks trading...")

        # Callbacks AI trading
        self._register_ai_trading_callbacks()

        # Callbacks signaux de trading
        self._register_trading_signals_callbacks()

        self.log_callback_registration()
        logger.info("✅ Callbacks trading enregistrés")

    def _register_ai_trading_callbacks(self) -> None:
        """Enregistre les callbacks du trading IA."""
        app = self.app

        @app.callback(
            [
                Output("ai-trading-modal", "is_open"),
                Output("ai-modal-content", "children"),
                Output("ai-modal-symbol", "children"),
                Output("ai-analysis-timestamp", "children"),
            ],
            [Input("ai-modal-close", "n_clicks"), Input("ai-modal-close-btn", "n_clicks")],
            [
                State("crypto-symbol-search", "value"),
                State("crypto-timeframe-selector", "value"),
                State("crypto-ai-engine-dropdown", "value"),
                State("crypto-ai-confidence-slider", "value"),
                State("ai-trading-modal", "is_open"),
            ],
        )
        def toggle_ai_trading_modal(
            close_clicks,
            close_btn_clicks,
            symbol,
            timeframe,
            ai_engine,
            confidence_threshold,
            is_open,
        ):
            """Toggle modal AI trading et génération d'analyse avec paramètres IA"""
            import dash

            ctx = dash.callback_context

            if not ctx.triggered:
                return False, self._create_placeholder_content(), "", ""

            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

            # Fermeture du modal
            if trigger_id in ["ai-modal-close", "ai-modal-close-btn"]:
                return False, self._create_placeholder_content(), "", ""

            # Le modal reste ouvert, contenu mis à jour
            return is_open, self._create_placeholder_content(), "", ""

        self.register_callback(toggle_ai_trading_modal, "toggle_ai_trading_modal")

        # Note: Le clientside_callback pour le drag & drop reste dans le composant original
        # car il nécessite l'accès direct au DOM et ne peut pas être centralisé facilement

    def _create_placeholder_content(self) -> html.Div:
        """Crée un contenu placeholder pour le modal AI trading."""
        return html.Div([
            html.H5("🤖 AI Trading Analysis", className="mb-3"),
            html.P("Analysis will be generated based on current market conditions...",
                  className="text-muted"),
            html.Div(className="text-center mt-4", children=[
                html.I(className="fas fa-robot fa-3x text-primary")
            ])
        ])

    def _register_trading_signals_callbacks(self) -> None:
        """Enregistre les callbacks des signaux de trading."""
        # TODO: Implémenter la migration des autres callbacks trading
        pass