from src.thebot.core.logger import logger
"""
Market Callbacks Manager - Gestionnaire centralisé des callbacks marché
Regroupe tous les callbacks liés aux données de marché et indicateurs
"""

import logging
from typing import Any, Dict, List, Optional

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html
import plotly.graph_objects as go

from ..base.callback_manager import CallbackManager
from ..base.callback_registry import get_callback_registry
from ...components.crypto_trends import crypto_trends
# from ...components.fear_greed_gauge import fear_greed_gauge  # Temporairement commenté pour éviter importation circulaire
from ...core.price_formatter import format_crypto_price_adaptive, format_percentage_change

# Stub temporaire pour éviter les erreurs
class FearGreedGaugeStub:
    def get_fear_greed_index(self):
        return {"value": 50, "value_classification": "Neutral"}
    def get_historical_data(self, period):
        return []
    def analyze_trends(self, data):
        return {}
    def setup_alerts(self, value):
        return []

fear_greed_gauge = FearGreedGaugeStub()

logger = logging.getLogger(__name__)


class MarketCallbacks(CallbackManager):
    """
    Gestionnaire centralisé des callbacks pour le marché.
    Regroupe les callbacks de :
    - announcements_calendar.py (2 callbacks)
    - crypto_trends.py (1 callback)
    - fear_greed_gauge.py (1 callback)
    """

    def __init__(self, app, market_data_manager=None):
        """
        Initialise le gestionnaire de callbacks marché.

        Args:
            app: Instance de l'application Dash
            market_data_manager: Gestionnaire de données de marché
        """
        super().__init__(app, "MarketCallbacks")
        self.market_data_manager = market_data_manager
        self.registry = get_callback_registry()

    def register_all_callbacks(self) -> None:
        """Enregistre tous les callbacks marché."""
        logger.info("🔄 Enregistrement des callbacks marché...")

        # Callbacks des tendances crypto
        self._register_crypto_trends_callbacks()

        # Callbacks Fear & Greed
        self._register_fear_greed_callbacks()

        self.log_callback_registration()
        logger.info("✅ Callbacks marché enregistrés")

    def _register_crypto_trends_callbacks(self) -> None:
        """Enregistre les callbacks des tendances crypto"""
        app = self.app

        @callback(
            [
                Output("crypto-trends-chart", "figure"),
                Output("crypto-trends-volume-chart", "figure"),
                Output("crypto-trends-table", "children"),
                Output("crypto-trends-indicators", "children"),
            ],
            [
                Input("crypto-trends-limit", "value"),
                Input("crypto-trends-interval", "n_intervals"),
            ],
        )
        def update_crypto_trends(limit, n_intervals):
            """Met à jour les données du widget crypto trends"""
            try:
                # Récupérer données
                trending_coins = crypto_trends.get_trending_coins(limit)
                volume_analysis = crypto_trends.get_volume_analysis()

                # Graphique prix et changements
                price_fig = go.Figure()

                if trending_coins:
                    symbols = [coin["symbol"].replace("USDT", "") for coin in trending_coins]
                    prices = [coin["price"] for coin in trending_coins]
                    changes = [coin["change_24h"] for coin in trending_coins]

                    # Barres colorées selon le changement
                    colors = ["green" if change > 0 else "red" for change in changes]

                    price_fig.add_trace(
                        go.Bar(
                            x=symbols,
                            y=changes,
                            marker_color=colors,
                            text=[format_crypto_price_adaptive(price) for price in prices],
                            textposition="outside",
                            name="Change 24h %",
                        )
                    )

                price_fig.update_layout(
                    title="Top Trending Cryptos - Change 24h (%)",
                    xaxis_title="Crypto",
                    yaxis_title="Change %",
                    height=300,
                    showlegend=False,
                )

                # Graphique volume
                volume_fig = go.Figure()

                if trending_coins:
                    volumes = [coin["volume_24h"] for coin in trending_coins]

                    volume_fig.add_trace(
                        go.Bar(x=symbols, y=volumes, marker_color="blue", name="Volume 24h")
                    )

                volume_fig.update_layout(
                    title="Volume 24h (USDT)",
                    xaxis_title="Crypto",
                    yaxis_title="Volume",
                    height=300,
                    showlegend=False,
                )

                # Tableau des données
                table_data = []
                if trending_coins:
                    table_data = [
                        html.Tr(
                            [
                                html.Th("Symbol"),
                                html.Th("Price"),
                                html.Th("Change 24h"),
                                html.Th("Volume"),
                                html.Th("Momentum"),
                            ]
                        )
                    ]

                    for coin in trending_coins[:10]:
                        row = html.Tr(
                            [
                                html.Td(coin["symbol"].replace("USDT", "")),
                                html.Td(format_crypto_price_adaptive(coin["price"])),
                                html.Td(
                                    format_percentage_change(coin["change_24h"]),
                                    style={
                                        "color": "green" if coin["change_24h"] > 0 else "red"
                                    },
                                ),
                                html.Td(f"${coin['volume_24h']:,.0f}"),
                                html.Td(coin["momentum"]),
                            ]
                        )
                        table_data.append(row)

                table = html.Table(table_data, className="trends-table")

                # Indicateurs
                indicators = []
                if volume_analysis:
                    indicators = [
                        html.Div(
                            [
                                html.H4("📊 Market Overview"),
                                html.P(
                                    f"Active Pairs: {volume_analysis.get('active_pairs', 0)}"
                                ),
                                html.P(
                                    f"Market Sentiment: {volume_analysis.get('market_sentiment', 'Unknown')}"
                                ),
                                html.P(
                                    f"Volume Trend: {volume_analysis.get('volume_trend', 'Unknown')}"
                                ),
                                html.P(
                                    f"Gainers: {volume_analysis.get('gainers_count', 0)} | "
                                    f"Losers: {volume_analysis.get('losers_count', 0)}"
                                ),
                            ],
                            className="market-indicators",
                        )
                    ]

                return price_fig, volume_fig, table, indicators

            except Exception as e:
                logger.error(f"Erreur callback crypto trends: {e}")

                # Retourner figures vides en cas d'erreur
                empty_fig = go.Figure()
                empty_fig.update_layout(title="Données non disponibles")

                return empty_fig, empty_fig, html.Div("Erreur chargement données"), html.Div()

    def _register_fear_greed_callbacks(self) -> None:
        """Enregistre les callbacks Fear & Greed"""
        app = self.app

        @callback(
            [
                Output("fear-greed-gauge-gauge", "figure"),
                Output("fear-greed-gauge-historical-chart", "figure"),
                Output("fear-greed-gauge-analysis", "children"),
                Output("fear-greed-gauge-alerts-panel", "children"),
            ],
            [
                Input("fear-greed-gauge-period", "value"),
                Input("fear-greed-gauge-alerts", "value"),
                Input("fear-greed-gauge-interval", "n_intervals"),
            ],
        )
        def update_fear_greed_gauge(period, alert_types, n_intervals):
            """Met à jour le widget Fear & Greed Gauge"""
            try:
                # Récupérer données actuelles et historiques
                current_data = fear_greed_gauge.get_fear_greed_index()
                historical_data = fear_greed_gauge.get_historical_data(period)

                # Jauge principale
                gauge_fig = go.Figure()

                if current_data:
                    value = current_data["value"]

                    gauge_fig.add_trace(
                        go.Indicator(
                            mode="gauge+number+delta",
                            value=value,
                            domain={"x": [0, 1], "y": [0, 1]},
                            title={
                                "text": f"Fear & Greed Index<br>{current_data.get('value_classification', '')}"
                            },
                            delta={"reference": 50},
                            gauge={
                                "axis": {"range": [0, 100]},
                                "bar": {"color": "darkblue"},
                                "steps": [
                                    {"range": [0, 25], "color": "red"},
                                    {"range": [25, 45], "color": "orange"},
                                    {"range": [45, 55], "color": "yellow"},
                                    {"range": [55, 75], "color": "lightgreen"},
                                    {"range": [75, 100], "color": "green"},
                                ],
                                "threshold": {
                                    "line": {"color": "red", "width": 4},
                                    "thickness": 0.75,
                                    "value": value,
                                },
                            },
                        )
                    )

                gauge_fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))

                # Graphique historique
                hist_fig = go.Figure()

                if historical_data:
                    dates = [
                        entry["date"] for entry in historical_data[::-1]
                    ]  # Inverser pour chronologique
                    values = [entry["value"] for entry in historical_data[::-1]]

                    hist_fig.add_trace(
                        go.Scatter(
                            x=dates,
                            y=values,
                            mode="lines+markers",
                            name="Fear & Greed Index",
                            line=dict(color="blue", width=2),
                            marker=dict(size=6),
                        )
                    )

                    # Ajouter zones colorées
                    hist_fig.add_hline(
                        y=25, line_dash="dash", line_color="red", annotation_text="Extreme Fear"
                    )
                    hist_fig.add_hline(
                        y=75,
                        line_dash="dash",
                        line_color="green",
                        annotation_text="Extreme Greed",
                    )
                    hist_fig.add_hrect(y0=0, y1=25, fillcolor="red", opacity=0.1)
                    hist_fig.add_hrect(y0=75, y1=100, fillcolor="green", opacity=0.1)

                hist_fig.update_layout(
                    title=f"Fear & Greed Index - Last {period} Days",
                    xaxis_title="Date",
                    yaxis_title="Index Value",
                    height=300,
                    yaxis=dict(range=[0, 100]),
                )

                # Analyse des tendances
                analysis_content = []
                if current_data and historical_data:
                    trends = fear_greed_gauge.analyze_trends(historical_data)
                    sentiment = current_data.get("sentiment", {})
                    recommendation = current_data.get("recommendation", {})

                    analysis_content = [
                        html.Div(
                            [
                                html.H4("📊 Analyse Actuelle"),
                                html.P(f"Valeur: {current_data['value']}/100"),
                                html.P(
                                    f"Niveau: {current_data.get('level', 'Unknown').replace('_', ' ').title()}"
                                ),
                                html.P(
                                    f"Sentiment: {sentiment.get('emoji', '')} {sentiment.get('description', '')}"
                                ),
                                html.P(
                                    f"État marché: {sentiment.get('market_state', 'Unknown')}"
                                ),
                            ],
                            className="analysis-current",
                        ),
                        (
                            html.Div(
                                [
                                    html.H4("📈 Tendances"),
                                    html.P(
                                        f"Direction: {trends.get('trend_direction', 'Unknown').title()}"
                                    ),
                                    html.P(f"Force: {trends.get('trend_strength', 0):.1f}"),
                                    html.P(f"Volatilité: {trends.get('volatility', 0):.1f}"),
                                    html.P(
                                        f"Durée zone: {trends.get('zone_duration', 0)} jours"
                                    ),
                                ],
                                className="analysis-trends",
                            )
                            if trends
                            else html.Div()
                        ),
                        html.Div(
                            [
                                html.H4("💡 Recommandation"),
                                html.P(f"Action: {recommendation.get('action', 'N/A')}"),
                                html.P(
                                    f"Description: {recommendation.get('description', 'N/A')}"
                                ),
                                html.P(f"Risque: {recommendation.get('risk', 'N/A')}"),
                                html.P(f"Horizon: {recommendation.get('timeframe', 'N/A')}"),
                            ],
                            className="analysis-recommendation",
                        ),
                    ]

                # Alertes
                alerts_content = []
                if current_data and alert_types:
                    alerts = fear_greed_gauge.setup_alerts(current_data["value"])

                    for alert in alerts:
                        if alert["type"] in ["opportunity"] and "opportunities" in alert_types:
                            alert_class = f"alert-{alert['level']}"
                        elif (
                            alert["type"] in ["warning", "caution"]
                            and "extremes" in alert_types
                        ):
                            alert_class = f"alert-{alert['level']}"
                        elif alert["type"] == "transition" and "transitions" in alert_types:
                            alert_class = "alert-info"
                        else:
                            continue

                        alert_div = html.Div(
                            [
                                html.P(alert["message"], className="alert-message"),
                                html.P(f"Action: {alert['action']}", className="alert-action"),
                                html.P(
                                    f"Confiance: {alert['confidence']}%",
                                    className="alert-confidence",
                                ),
                            ],
                            className=f"alert-item {alert_class}",
                        )

                        alerts_content.append(alert_div)

                if not alerts_content:
                    alerts_content = [html.P("Aucune alerte active", className="no-alerts")]

                return gauge_fig, hist_fig, analysis_content, alerts_content

            except Exception as e:
                logger.error(f"Erreur callback Fear & Greed Gauge: {e}")

                # Retourner vides en cas d'erreur
                empty_fig = go.Figure()
                empty_fig.update_layout(title="Données non disponibles")

                error_content = [html.P(f"Erreur: {str(e)}", className="error-message")]

                return empty_fig, empty_fig, error_content, error_content