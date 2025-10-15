"""
Modal Callbacks Manager - Gestionnaire centralisé des callbacks modaux
Regroupe tous les callbacks liés aux modaux et fenêtres popup
"""

import json
import logging
from typing import Any, Dict, List, Optional

import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, callback, html

from ..base.callback_manager import CallbackManager
from ..base.callback_registry import get_callback_registry

logger = logging.getLogger(__name__)


class ModalCallbacks(CallbackManager):
    """
    Gestionnaire centralisé des callbacks pour les modaux.
    Regroupe les callbacks de divers composants modaux.
    """

    def __init__(self, app, modal_manager=None):
        """
        Initialise le gestionnaire de callbacks modaux.

        Args:
            app: Instance de l'application Dash
            modal_manager: Gestionnaire de modaux
        """
        super().__init__(app, "ModalCallbacks")
        self.modal_manager = modal_manager
        self.registry = get_callback_registry()

    def register_all_callbacks(self) -> None:
        """Enregistre tous les callbacks modaux."""
        logger.info("🔄 Enregistrement des callbacks modaux...")

        # Callbacks de gestion des onglets
        self._register_tab_callbacks()

        # Callbacks de debug et monitoring
        self._register_debug_callbacks()

        # Callbacks des indicateurs de base
        self._register_basic_indicators_callbacks()

        # Callbacks des indicateurs avancés
        self._register_advanced_indicators_callbacks()

        self.log_callback_registration()
        logger.info("✅ Callbacks modaux enregistrés")

    def _register_tab_callbacks(self) -> None:
        """Enregistre les callbacks de gestion des onglets"""
        app = self.app

        @callback(
            Output("indicators-modal-content", "children"),
            Input("indicators-tabs", "active_tab"),
        )
        def update_tab_content(active_tab):
            """Mettre à jour le contenu selon l'onglet actif"""
            try:
                if self.modal_manager:
                    if active_tab == "basic_indicators":
                        return self.modal_manager._create_basic_indicators_content()
                    elif active_tab == "advanced_indicators":
                        return self.modal_manager._create_advanced_indicators_content()
                    elif active_tab == "trading_styles":
                        return self.modal_manager._create_trading_styles_content()
                    elif active_tab == "configuration":
                        return self.modal_manager._create_configuration_content()
                    else:
                        return html.Div("Onglet non trouvé", className="text-warning")
                else:
                    return html.Div("Modal manager non disponible", className="text-danger")

            except Exception as e:
                logger.error(f"Erreur mise à jour contenu onglet: {e}")
                return html.Div(
                    f"Erreur lors du chargement de l'onglet: {str(e)}",
                    className="text-danger"
                )

    def _register_debug_callbacks(self) -> None:
        """Enregistre les callbacks de debug et monitoring"""
        app = self.app

        @callback(
            Output("debug-info-container", "children"),
            [Input({"type": "indicator-control", "id": ALL}, "value")],
        )
        def update_debug_info(values):
            """Afficher les informations de debug"""
            if not values:
                return []

            try:
                # Récupérer la configuration actuelle depuis le modal manager
                if self.modal_manager:
                    current_config = self.modal_manager.parameters.get_all_basic_indicators()
                else:
                    current_config = {"error": "Modal manager non disponible"}

                debug_info = dbc.Alert(
                    [
                        html.H6("🔍 Debug Info", className="mb-2"),
                        html.Pre(
                            json.dumps(current_config, indent=2),
                            className="mb-0",
                            style={
                                "fontSize": "0.75rem",
                                "maxHeight": "150px",
                                "overflowY": "auto",
                            }
                        ),
                    ],
                    color="info",
                    className="mt-2"
                )

                return debug_info

            except Exception as e:
                logger.error(f"Erreur mise à jour debug info: {e}")
                return dbc.Alert(f"Erreur debug: {str(e)}", color="danger")

    def _register_basic_indicators_callbacks(self) -> None:
        """Enregistre les callbacks des indicateurs de base"""
        app = self.app

        @callback(
            [
                Output("sma-preview", "children"),
                Output("ema-preview", "children"),
                Output("rsi-preview", "children"),
                Output("atr-preview", "children"),
                Output("macd-preview", "children"),
            ],
            [
                Input("basic-sma-period", "value"),
                Input("basic-ema-period", "value"),
                Input("basic-rsi-period", "value"),
                Input("basic-rsi-overbought", "value"),
                Input("basic-rsi-oversold", "value"),
                Input("basic-atr-period", "value"),
                Input("basic-atr-multiplier", "value"),
                Input("basic-macd-fast", "value"),
                Input("basic-macd-slow", "value"),
                Input("basic-macd-signal", "value"),
            ],
        )
        def update_previews(
            sma_period,
            ema_period,
            rsi_period,
            rsi_ob,
            rsi_os,
            atr_period,
            atr_mult,
            macd_fast,
            macd_slow,
            macd_signal,
        ):
            """Mettre à jour les previews en temps réel"""
            try:
                # SMA Preview
                sma_preview = dbc.Badge(
                    f"SMA({sma_period or 20})", color="primary", className="me-2"
                )

                # EMA Preview
                ema_preview = dbc.Badge(
                    f"EMA({ema_period or 12})", color="warning", className="me-2"
                )

                # RSI Preview
                rsi_preview = html.Div(
                    [
                        dbc.Badge(
                            f"RSI({rsi_period or 14})", color="purple", className="me-2"
                        ),
                        dbc.Badge(f"OB: {rsi_ob or 70}", color="danger", className="me-1"),
                        dbc.Badge(f"OS: {rsi_os or 30}", color="success", className="me-1"),
                    ]
                )

                # ATR Preview
                atr_preview = html.Div(
                    [
                        dbc.Badge(
                            f"ATR({atr_period or 14})", color="success", className="me-2"
                        ),
                        dbc.Badge(f"x{atr_mult or 2.0}", color="info", className="me-1"),
                    ]
                )

                # MACD Preview
                macd_preview = html.Div(
                    [
                        dbc.Badge(
                            f"MACD({macd_fast or 12}, {macd_slow or 26})",
                            color="primary",
                            className="me-2",
                        ),
                        dbc.Badge(
                            f"Signal({macd_signal or 9})",
                            color="secondary",
                            className="me-1",
                        ),
                    ]
                )

                return sma_preview, ema_preview, rsi_preview, atr_preview, macd_preview

            except Exception as e:
                logger.error(f"Erreur mise à jour previews: {e}")
                return [dbc.Badge("Erreur", color="danger")] * 5

        @callback(
            Output("basic-indicators-status", "children"),
            [
                Input("basic-sma-enabled", "value"),
                Input("basic-ema-enabled", "value"),
                Input("basic-rsi-enabled", "value"),
                Input("basic-atr-enabled", "value"),
                Input("basic-macd-enabled", "value"),
            ],
        )
        def update_indicators_status(sma_enabled, ema_enabled, rsi_enabled, atr_enabled, macd_enabled):
            """Mettre à jour le statut global des indicateurs"""
            try:
                enabled_indicators = [sma_enabled, ema_enabled, rsi_enabled, atr_enabled, macd_enabled]
                enabled_count = sum(1 for enabled in enabled_indicators if enabled)
                total_indicators = len(enabled_indicators)

                if enabled_count == 0:
                    color = "secondary"
                    text = "Aucun indicateur activé"
                    icon = "fas fa-exclamation-triangle"
                elif enabled_count == total_indicators:
                    color = "success"
                    text = f"Tous les indicateurs activés ({enabled_count}/{total_indicators})"
                    icon = "fas fa-check-circle"
                else:
                    color = "warning"
                    text = f"Indicateurs partiellement activés ({enabled_count}/{total_indicators})"
                    icon = "fas fa-info-circle"

                return dbc.Alert(
                    [html.I(className=f"{icon} me-2"), text], color=color, className="mb-0"
                )

            except Exception as e:
                logger.error(f"Erreur mise à jour statut indicateurs: {e}")
                return dbc.Alert("Erreur de statut", color="danger", className="mb-0")

    def _register_advanced_indicators_callbacks(self) -> None:
        """Enregistre les callbacks des indicateurs avancés"""
        app = self.app

        @callback(
            [
                Output("sr-preview", "children"),
                Output("fibonacci-preview", "children"),
                Output("pivot-preview", "children"),
            ],
            [
                Input("advanced-sr-strength", "value"),
                Input("advanced-sr-lookback", "value"),
                Input("advanced-fibonacci-swing", "value"),
                Input("advanced-fibonacci-line-width", "value"),
                Input("advanced-pivot-timeframe", "value"),
            ],
        )
        def update_advanced_previews(sr_strength, sr_lookback, fib_swing, fib_width, pivot_timeframe):
            """Mettre à jour les previews des indicateurs avancés"""
            try:
                # Support/Résistance Preview
                sr_preview = dbc.Badge(
                    f"SR({sr_strength or 3}, {sr_lookback or 50})",
                    color="info",
                    className="me-2"
                )

                # Fibonacci Preview
                fib_preview = html.Div(
                    [
                        dbc.Badge(f"Fib({fib_swing or 'high'})", color="success", className="me-2"),
                        dbc.Badge(f"Width: {fib_width or 2}", color="secondary", className="me-1"),
                    ]
                )

                # Pivot Points Preview
                pivot_preview = dbc.Badge(
                    f"Pivot({pivot_timeframe or 'daily'})",
                    color="warning",
                    className="me-2"
                )

                return sr_preview, fib_preview, pivot_preview

            except Exception as e:
                logger.error(f"Erreur mise à jour previews avancés: {e}")
                return [dbc.Badge("Erreur", color="danger")] * 3

        @callback(
            Output("advanced-indicators-status", "children"),
            [
                Input("advanced-sr-enabled", "value"),
                Input("advanced-fibonacci-enabled", "value"),
                Input("advanced-pivot-enabled", "value"),
            ],
        )
        def update_advanced_status(sr_enabled, fib_enabled, pivot_enabled):
            """Mettre à jour le statut global des indicateurs avancés"""
            try:
                enabled_indicators = [sr_enabled, fib_enabled, pivot_enabled]
                enabled_count = sum(1 for enabled in enabled_indicators if enabled)
                total_indicators = len(enabled_indicators)

                if enabled_count == 0:
                    color = "secondary"
                    text = "Aucun indicateur avancé activé"
                    icon = "fas fa-exclamation-triangle"
                elif enabled_count == total_indicators:
                    color = "success"
                    text = f"Tous les indicateurs avancés activés ({enabled_count}/{total_indicators})"
                    icon = "fas fa-check-circle"
                else:
                    color = "warning"
                    text = f"Indicateurs avancés partiellement activés ({enabled_count}/{total_indicators})"
                    icon = "fas fa-info-circle"

                return dbc.Alert(
                    [html.I(className=f"{icon} me-2"), text], color=color, className="mb-0"
                )

            except Exception as e:
                logger.error(f"Erreur mise à jour statut indicateurs avancés: {e}")
                return dbc.Alert("Erreur de statut", color="danger", className="mb-0")