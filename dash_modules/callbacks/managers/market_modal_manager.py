"""
Market Modal Manager - Contrôleur MVC pour les données de marché
Gère les callbacks en utilisant MarketDataService pour la logique métier
"""

import logging
from typing import Any, Dict, List, Optional

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html
from dash.dependencies import ALL
import plotly.graph_objects as go

from ..base.callback_manager import CallbackManager
from ...services import market_data_service
from ...core.price_formatter import format_crypto_price_adaptive, format_percentage_change

logger = logging.getLogger(__name__)


class MarketModalManager(CallbackManager):
    """
    Contrôleur pour les données de marché.
    Gère tous les callbacks liés aux données de marché en utilisant MarketDataService.
    """

    def __init__(self, app):
        super().__init__(app, "MarketModalManager")

    def register_all_callbacks(self) -> None:
        """Enregistre tous les callbacks des données de marché"""
        logger.info("🔄 Enregistrement des callbacks modal marché...")

        self._register_market_data_callbacks()

        self.log_callback_registration()
        logger.info("✅ Callbacks modal marché enregistrés")

    def _register_market_data_callbacks(self) -> None:
        """Enregistre les callbacks des données de marché"""

        @self.app.callback(
            [
                Output("market-data-store", "data"),
                Output("market-overview-table", "children"),
                Output("market-indicators", "children"),
            ],
            [Input("market-refresh-interval", "n_intervals")],
            [State("market-symbols-input", "value")],
            prevent_initial_call=False,
        )
        def update_market_data(n_intervals, symbols_input):
            """Met à jour les données de marché depuis MarketDataService"""
            try:
                # Parser les symboles (séparés par des virgules)
                if not symbols_input:
                    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
                else:
                    symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

                # Récupérer les données depuis le service
                market_data_list = market_data_service.get_multiple_markets(symbols)

                # Préparer les données pour le store
                store_data = {}
                for market_data in market_data_list:
                    store_data[market_data.symbol] = market_data.to_dict()

                # Créer le tableau de données
                table_rows = [
                    html.Tr([
                        html.Th("Symbol"),
                        html.Th("Price"),
                        html.Th("Change 24h"),
                        html.Th("Volume 24h"),
                        html.Th("High 24h"),
                        html.Th("Low 24h"),
                    ])
                ]

                for market_data in market_data_list:
                    row = html.Tr([
                        html.Td(market_data.symbol.replace("USDT", "")),
                        html.Td(format_crypto_price_adaptive(market_data.current_price)),
                        html.Td(
                            format_percentage_change(market_data.price_change_percent_24h),
                            style={
                                "color": "green" if market_data.price_change_percent_24h > 0 else "red"
                            },
                        ),
                        html.Td(f"${market_data.volume_24h:,.0f}" if market_data.volume_24h else "N/A"),
                        html.Td(format_crypto_price_adaptive(market_data.high_24h) if market_data.high_24h else "N/A"),
                        html.Td(format_crypto_price_adaptive(market_data.low_24h) if market_data.low_24h else "N/A"),
                    ])
                    table_rows.append(row)

                table = html.Table(table_rows, className="market-table")

                # Créer les indicateurs de marché
                total_volume = sum(m.volume_24h for m in market_data_list if m.volume_24h)
                gainers = len([m for m in market_data_list if m.price_change_percent_24h > 0])
                losers = len([m for m in market_data_list if m.price_change_percent_24h < 0])

                indicators = html.Div([
                    html.H4("📊 Market Overview"),
                    html.P(f"Total Assets: {len(market_data_list)}"),
                    html.P(f"Total Volume: ${total_volume:,.0f}" if total_volume else "Volume: N/A"),
                    html.P(f"Gainers: {gainers} | Losers: {losers}"),
                    html.P(f"Market Sentiment: {'Bullish' if gainers > losers else 'Bearish'}"),
                ], className="market-indicators")

                return store_data, table, indicators

            except Exception as e:
                logger.error(f"Erreur callback market data: {e}")
                return {}, html.Div("Erreur chargement données marché"), html.Div("Erreur indicateurs")

        @self.app.callback(
            Output("market-price-chart", "figure"),
            [Input("market-data-store", "data")],
            prevent_initial_call=False,
        )
        def update_market_price_chart(store_data):
            """Met à jour le graphique des prix de marché"""
            try:
                if not store_data:
                    empty_fig = go.Figure()
                    empty_fig.update_layout(title="Aucune donnée disponible")
                    return empty_fig

                # Créer le graphique
                fig = go.Figure()

                symbols = []
                prices = []
                changes = []

                for symbol, data in store_data.items():
                    symbols.append(symbol.replace("USDT", ""))
                    prices.append(data.get("current_price", 0))
                    changes.append(data.get("price_change_percent_24h", 0))

                # Barres pour les prix
                fig.add_trace(go.Bar(
                    x=symbols,
                    y=prices,
                    name="Current Price",
                    marker_color="blue",
                ))

                fig.update_layout(
                    title="Market Prices Overview",
                    xaxis_title="Symbol",
                    yaxis_title="Price (USDT)",
                    height=400,
                    showlegend=False,
                )

                return fig

            except Exception as e:
                logger.error(f"Erreur callback market chart: {e}")
                empty_fig = go.Figure()
                empty_fig.update_layout(title="Erreur chargement graphique")
                return empty_fig

        @self.app.callback(
            Output("market-search-results", "children"),
            [Input("market-search-input", "value")],
            prevent_initial_call=False,
        )
        def search_market_symbols(search_query):
            """Recherche des symboles de marché"""
            try:
                if not search_query or len(search_query) < 2:
                    return html.Div("Entrez au moins 2 caractères pour rechercher")

                # Utiliser le service pour rechercher
                results = market_data_service.search_symbols(search_query, limit=10)

                if not results:
                    return html.Div("Aucun symbole trouvé")

                # Créer la liste des résultats
                result_items = []
                for symbol in results:
                    item = html.Li([
                        html.Span(symbol, className="symbol-name"),
                        html.Button(
                            "Ajouter",
                            id={"type": "add-symbol-btn", "symbol": symbol},
                            className="btn btn-sm btn-primary ms-2"
                        )
                    ], className="search-result-item")
                    result_items.append(item)

                return html.Ul(result_items, className="search-results-list")

            except Exception as e:
                logger.error(f"Erreur callback market search: {e}")
                return html.Div("Erreur lors de la recherche")

        @self.app.callback(
            Output("market-symbols-input", "value"),
            [Input({"type": "add-symbol-btn", "symbol": ALL}, "n_clicks")],
            [State("market-symbols-input", "value")],
            prevent_initial_call=False,
        )
        def add_symbol_to_list(button_clicks, current_symbols):
            """Ajoute un symbole à la liste des symboles surveillés"""
            try:
                # Identifier quel bouton a été cliqué
                ctx = callback_context
                if not ctx.triggered:
                    return current_symbols or ""

                triggered_id = ctx.triggered[0]["prop_id"]
                if not triggered_id.startswith('{"type":"add-symbol-btn"'):
                    return current_symbols or ""

                # Extraire le symbole du triggered_id
                import json
                button_data = json.loads(triggered_id.split(".")[0])
                symbol = button_data["symbol"]

                # Ajouter à la liste actuelle
                if not current_symbols:
                    return symbol
                else:
                    symbols_list = [s.strip() for s in current_symbols.split(",")]
                    if symbol not in symbols_list:
                        symbols_list.append(symbol)
                    return ", ".join(symbols_list)

            except Exception as e:
                logger.error(f"Erreur callback add symbol: {e}")
                return current_symbols or ""