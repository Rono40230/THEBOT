"""
Trading Modal Manager - Contrôleur MVC pour les opérations de trading
Gère les callbacks en utilisant MarketDataService et AlertService pour la logique métier
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html
from dash.dependencies import ALL

from ..base.callback_manager import CallbackManager
from ...services import market_data_service, alert_service
from ...core.price_formatter import format_crypto_price_adaptive

logger = logging.getLogger(__name__)


class TradingModalManager(CallbackManager):
    """
    Contrôleur pour les opérations de trading.
    Gère tous les callbacks liés au trading en utilisant les services métier.
    """

    def __init__(self, app):
        super().__init__(app, "TradingModalManager")

    def register_all_callbacks(self) -> None:
        """Enregistre tous les callbacks des opérations de trading"""
        logger.info("🔄 Enregistrement des callbacks modal trading...")

        self._register_trading_analysis_callbacks()

        self.log_callback_registration()
        logger.info("✅ Callbacks modal trading enregistrés")

    def _register_trading_analysis_callbacks(self) -> None:
        """Enregistre les callbacks d'analyse de trading"""

        # Note: Le callback du modal AI trading est géré par TradingCallbacks
        # Ici nous ajoutons les callbacks d'analyse et signaux de trading

        @self.app.callback(
            Output("trading-analysis-output", "children"),
            [Input("run-trading-analysis-btn", "n_clicks")],
            [
                State("crypto-symbol-search", "value"),
                State("crypto-timeframe-selector", "value"),
                State("crypto-ai-engine-dropdown", "value"),
                State("crypto-ai-confidence-slider", "value"),
            ],
            prevent_initial_call=False,
        )
        def run_trading_analysis(n_clicks, symbol, timeframe, ai_engine, confidence_threshold):
            """Exécute l'analyse de trading en utilisant les services"""
            try:
                if not n_clicks or not symbol:
                    return html.Div("Sélectionnez un symbole pour lancer l'analyse", className="alert alert-info")

                # Récupérer les données de marché depuis le service
                market_data = market_data_service.get_market_data(symbol.upper())
                if not market_data:
                    return html.Div(f"Impossible de récupérer les données pour {symbol}", className="alert alert-warning")

                # Récupérer les alertes actives pour ce symbole
                active_alerts = alert_service.get_alerts_for_symbol(symbol.upper())
                active_alerts = [alert for alert in active_alerts if not alert.triggered]

                # Créer l'analyse de trading
                analysis = self._generate_trading_analysis(
                    market_data,
                    active_alerts,
                    timeframe or "1h",
                    ai_engine or "smart",
                    confidence_threshold or 70
                )

                return analysis

            except Exception as e:
                logger.error(f"Erreur analyse trading: {e}")
                return html.Div(f"Erreur lors de l'analyse: {str(e)}", className="alert alert-danger")

        @self.app.callback(
            Output("trading-signals-table", "children"),
            [Input("refresh-trading-signals-btn", "n_clicks")],
            [State("trading-signals-limit", "value")],
            prevent_initial_call=False,
        )
        def refresh_trading_signals(n_clicks, limit):
            """Actualise les signaux de trading"""
            try:
                limit = limit or 10

                # Simuler des signaux de trading (à remplacer par vraie logique)
                signals = self._generate_mock_trading_signals(limit)

                # Créer le tableau
                table_header = html.Tr([
                    html.Th("Symbol"),
                    html.Th("Signal"),
                    html.Th("Price"),
                    html.Th("Confidence"),
                    html.Th("Timestamp"),
                    html.Th("Action"),
                ])

                table_rows = [table_header]

                for signal in signals:
                    row = html.Tr([
                        html.Td(signal["symbol"]),
                        html.Td(
                            signal["signal"],
                            className=f"signal-{signal['signal'].lower()}"
                        ),
                        html.Td(format_crypto_price_adaptive(signal["price"])),
                        html.Td(f"{signal['confidence']}%"),
                        html.Td(signal["timestamp"]),
                        html.Td(html.Button(
                            "Trade",
                            id={"type": "trade-signal-btn", "symbol": signal["symbol"], "signal": signal["signal"]},
                            className="btn btn-sm btn-success"
                        )),
                    ])
                    table_rows.append(row)

                return html.Table(table_rows, className="trading-signals-table")

            except Exception as e:
                logger.error(f"Erreur signaux trading: {e}")
                return html.Div("Erreur chargement signaux", className="alert alert-danger")

        @self.app.callback(
            Output("trading-alert", "children"),
            [Input({"type": "trade-signal-btn", "symbol": ALL, "signal": ALL}, "n_clicks")],
            prevent_initial_call=False,
        )
        def execute_trade_signal(button_clicks):
            """Exécute un ordre de trading basé sur un signal"""
            try:
                import dash

                ctx = dash.callback_context
                if not ctx.triggered:
                    return ""

                # Identifier le bouton cliqué
                triggered_id = ctx.triggered[0]["prop_id"]
                if not triggered_id.startswith('{"type":"trade-signal-btn"'):
                    return ""

                # Parser l'ID du bouton
                import json
                button_data = json.loads(triggered_id.split(".")[0])
                symbol = button_data["symbol"]
                signal = button_data["signal"]

                # Simuler l'exécution du trade (à remplacer par vraie logique)
                trade_result = self._execute_mock_trade(symbol, signal)

                return html.Div(trade_result, className="alert alert-success")

            except Exception as e:
                logger.error(f"Erreur exécution trade: {e}")
                return html.Div(f"Erreur exécution trade: {str(e)}", className="alert alert-danger")

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

    def _generate_trading_analysis(self, market_data, active_alerts, timeframe, ai_engine, confidence_threshold):
        """Génère une analyse de trading complète"""
        analysis = html.Div([
            html.H4(f"📊 Analyse Trading - {market_data.symbol}", className="mb-4"),

            # Résumé du marché
            html.Div([
                html.H5("🏛️ Résumé Marché"),
                html.P(f"Prix actuel: {format_crypto_price_adaptive(market_data.current_price)}"),
                html.P(f"Variation 24h: {market_data.price_change_percent_24h:.2f}%"),
                html.P(f"Volume 24h: ${market_data.volume_24h:,.0f}" if market_data.volume_24h else "Volume: N/A"),
            ], className="market-summary mb-4"),

            # Alertes actives
            html.Div([
                html.H5("🚨 Alertes Actives"),
                html.P(f"{len(active_alerts)} alerte(s) active(s) pour ce symbole"),
                html.Ul([html.Li(f"{alert.alert_type.value.upper()} à ${alert.price}") for alert in active_alerts[:3]])
                if active_alerts else html.P("Aucune alerte active"),
            ], className="alerts-summary mb-4"),

            # Recommandation IA
            html.Div([
                html.H5(f"🤖 Recommandation {ai_engine.upper()}"),
                html.P(f"Timeframe: {timeframe}"),
                html.P(f"Seuil confiance: {confidence_threshold}%"),
                html.Div([
                    html.Strong("Signal: "),
                    html.Span("HOLD", className="badge bg-warning"),
                    html.Span(f" (Confiance: {confidence_threshold + 10}%)", className="ms-2")
                ], className="mt-3"),
                html.P("Raison: Marché en consolidation, attendre confirmation du signal", className="mt-2 text-muted"),
            ], className="ai-recommendation"),

            html.Hr(),
            html.P(f"Analyse générée le {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", className="text-muted text-end"),
        ])

        return analysis

    def _generate_mock_trading_signals(self, limit):
        """Génère des signaux de trading fictifs pour démonstration"""
        signals = []
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]

        for i in range(min(limit, len(symbols))):
            signal_type = ["BUY", "SELL", "HOLD"][i % 3]
            confidence = 65 + (i * 5)  # 65%, 70%, 75%, etc.

            signal = {
                "symbol": symbols[i],
                "signal": signal_type,
                "price": 50000 + (i * 1000),  # Prix fictifs
                "confidence": confidence,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            signals.append(signal)

        return signals

    def _execute_mock_trade(self, symbol, signal):
        """Simule l'exécution d'un trade"""
        return f"✅ Trade simulé exécuté: {signal} {symbol} à {datetime.now().strftime('%H:%M:%S')}"