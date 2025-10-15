"""
News Callbacks Manager - Gestionnaire centralisé des callbacks news
Regroupe tous les callbacks liés aux news (économiques et crypto)
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html
import plotly.graph_objects as go

from ..base.callback_manager import CallbackManager
from ..base.callback_registry import get_callback_registry
from ...components.fear_greed_gauge import fear_greed_gauge
from ...components.top_performers import top_performers
from ...components.crypto_trends import crypto_trends

logger = logging.getLogger(__name__)


class NewsCallbacks(CallbackManager):
    """
    Gestionnaire centralisé des callbacks pour les news.
    Regroupe les callbacks de :
    - crypto_news_module.py (5 callbacks)
    - economic_news_module.py (4 callbacks)
    - crypto_news_phase4_extensions.py (3 callbacks)
    """

    def __init__(self, app, crypto_news_module=None, economic_news_module=None):
        """
        Initialise le gestionnaire de callbacks news.

        Args:
            app: Instance de l'application Dash
            crypto_news_module: Instance du module crypto news
            economic_news_module: Instance du module economic news
        """
        super().__init__(app, "NewsCallbacks")
        self.crypto_news_module = crypto_news_module
        self.economic_news_module = economic_news_module
        self.registry = get_callback_registry()

    def register_all_callbacks(self) -> None:
        """Enregistre tous les callbacks news."""
        logger.info("🔄 Enregistrement des callbacks news...")

        # Callbacks crypto news
        if self.crypto_news_module:
            self._register_crypto_news_callbacks()

        # Callbacks economic news
        if self.economic_news_module:
            self._register_economic_news_callbacks()

        # Callbacks extensions phase 4
        self._register_phase4_callbacks()

        self.log_callback_registration()
        logger.info("✅ Callbacks news enregistrés")

    def _register_crypto_news_callbacks(self) -> None:
        """Enregistre les 5 callbacks du module crypto news."""
        app = self.app

        @app.callback(
            [
                Output("crypto-news-store", "data"),
                Output("crypto-sentiment-store", "data"),
            ],
            [
                Input("refresh-crypto-news-btn", "n_clicks"),
                Input("crypto-news-interval", "n_intervals"),
            ],
        )
        def update_crypto_news_data(refresh_clicks, interval_clicks):
            """Mettre à jour les données RSS crypto"""
            if not self.crypto_news_module:
                return {}, {}

            # Récupérer news RSS (retourne une liste d'articles)
            articles = self.crypto_news_module.get_rss_news()

            # Analyser sentiment crypto avec la liste
            sentiment = self.crypto_news_module.analyze_crypto_sentiment(articles)

            # Extraire trending coins avec la liste
            trending = self.crypto_news_module.extract_crypto_trending(articles)

            # Calculer Fear & Greed crypto avec la liste
            fear_greed = self.crypto_news_module.calculate_crypto_fear_greed(articles, sentiment)

            # Analyser impact prix avec la liste
            price_impact = self.crypto_news_module.analyze_price_impact(articles)

            # Format cohérent pour tous les widgets
            news_data = {
                "news": articles,  # Liste d'articles pour les widgets
                "trending": trending,
                "fear_greed": fear_greed,
                "price_impact": price_impact,
                "total": len(articles),
                "timestamp": datetime.now().isoformat(),
            }

            self.registry.register_callback(
                "NewsCallbacks", "update_crypto_news_data",
                ["refresh-crypto-news-btn.n_clicks", "crypto-news-interval.n_intervals"],
                ["crypto-news-store.data", "crypto-sentiment-store.data"]
            )

            return news_data, sentiment

        self.register_callback(update_crypto_news_data, "update_crypto_news_data")

        @app.callback(
            Output("crypto-news-feed", "children"),
            [Input("crypto-news-store", "data")]
        )
        def update_crypto_news_feed(news_data):
            """Mettre à jour le feed de news crypto"""
            if not news_data or not news_data.get("news"):
                return dbc.Alert("Aucune news crypto RSS disponible", color="warning")

            news_items = []
            for article in news_data["news"][:20]:
                # Déterminer couleur sentiment crypto
                sentiment = article.get("sentiment", "neutral")
                if sentiment in ["positive", "bullish"]:
                    border_color = "border-success"
                elif sentiment in ["negative", "bearish"]:
                    border_color = "border-danger"
                else:
                    border_color = "border-secondary"

                # Créer item news avec sentiment
                news_item = dbc.Card(
                    [
                        dbc.CardHeader(
                            html.A(
                                article.get("title", "Titre indisponible"),
                                href=article.get("link", "#"),
                                target="_blank",
                                className="text-decoration-none",
                            )
                        ),
                        dbc.CardBody(
                            [
                                html.P(
                                    article.get("description", "Description indisponible")[:200] + "...",
                                    className="card-text small",
                                ),
                                html.Small(
                                    f"📅 {article.get('published', 'Date inconnue')} | "
                                    f"🔍 Source: {article.get('source', 'Inconnue')}",
                                    className="text-muted",
                                ),
                            ]
                        ),
                    ],
                    className=f"mb-3 {border_color}",
                )
                news_items.append(news_item)

            self.registry.register_callback(
                "NewsCallbacks", "update_crypto_news_feed",
                ["crypto-news-store.data"], ["crypto-news-feed.children"]
            )

            return news_items

        self.register_callback(update_crypto_news_feed, "update_crypto_news_feed")

        @app.callback(
            Output("crypto-fear-greed-gauge", "figure"),
            [Input("crypto-news-store", "data")]
        )
        def update_crypto_fear_greed_gauge(news_data):
            """Gauge Fear & Greed crypto basé sur l'analyse des vraies news"""
            try:
                # Calcul du score basé sur les vraies données RSS
                if not news_data or not news_data.get("news"):
                    # Valeurs par défaut
                    fear_greed_score = 55
                else:
                    # Utiliser les données calculées du store
                    fear_greed_data = news_data.get("fear_greed", {})
                    fear_greed_score = fear_greed_data.get("score", 55)

                # Créer le gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=fear_greed_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Crypto Fear & Greed Index"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 20], 'color': "darkred"},
                            {'range': [20, 40], 'color': "orange"},
                            {'range': [40, 60], 'color': "yellow"},
                            {'range': [60, 80], 'color': "lightgreen"},
                            {'range': [80, 100], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': fear_greed_score
                        }
                    }
                ))

                fig.update_layout(
                    height=200,
                    margin=dict(l=20, r=20, t=40, b=20)
                )

                self.registry.register_callback(
                    "NewsCallbacks", "update_crypto_fear_greed_gauge",
                    ["crypto-news-store.data"], ["crypto-fear-greed-gauge.figure"]
                )

                return fig

            except Exception as e:
                logger.error(f"Erreur gauge Fear & Greed crypto: {e}")
                # Gauge d'erreur
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=50,
                    title={'text': "Erreur - Fear & Greed"},
                    gauge={'axis': {'range': [0, 100]}}
                ))
                return fig

        self.register_callback(update_crypto_fear_greed_gauge, "update_crypto_fear_greed_gauge")

        @app.callback(
            Output("crypto-trending-coins", "children"),
            [Input("crypto-news-store", "data")]
        )
        def update_crypto_trending_coins(news_data):
            """Widget coins tendance basé sur les mentions dans les news"""
            try:
                if not news_data or not news_data.get("trending"):
                    # Données de démonstration
                    return html.Div([
                        dbc.Row([
                            dbc.Col("BTC", width=4),
                            dbc.Col("$65,432", width=4, className="text-end"),
                            dbc.Col([
                                html.I(className="fas fa-arrow-up text-success")
                            ], width=4, className="text-end"),
                        ], className="mb-2"),
                        dbc.Row([
                            dbc.Col("ETH", width=4),
                            dbc.Col("$3,124", width=4, className="text-end"),
                            dbc.Col([
                                html.I(className="fas fa-arrow-up text-success")
                            ], width=4, className="text-end"),
                        ], className="mb-2"),
                        dbc.Row([
                            dbc.Col("SOL", width=4),
                            dbc.Col("$145", width=4, className="text-end"),
                            dbc.Col([
                                html.I(className="fas fa-arrow-down text-danger")
                            ], width=4, className="text-end"),
                        ])
                    ])

                # Utiliser les données calculées du store
                trending_coins = news_data.get("trending", [])[:5]

                if not trending_coins:
                    return html.Div("Aucune donnée tendance disponible")

                rows = []
                for coin_data in trending_coins:
                    coin = coin_data.get("coin", "N/A")
                    mentions = coin_data.get("mentions", 0)
                    trend = coin_data.get("trend", "stable")
                    sentiment = coin_data.get("sentiment", "neutral")

                    # Déterminer l'icône et la couleur
                    if trend == "up" or sentiment == "positive":
                        icon = html.I(className="fas fa-arrow-up text-success")
                    elif trend == "down" or sentiment == "negative":
                        icon = html.I(className="fas fa-arrow-down text-danger")
                    else:
                        icon = html.I(className="fas fa-minus text-warning")

                    rows.append(
                        dbc.Row([
                            dbc.Col(coin, width=4),
                            dbc.Col(f"{mentions} mentions", width=4, className="text-end"),
                            dbc.Col(icon, width=4, className="text-end"),
                        ], className="mb-2")
                    )

                self.registry.register_callback(
                    "NewsCallbacks", "update_crypto_trending_coins",
                    ["crypto-news-store.data"], ["crypto-trending-coins.children"]
                )

                return html.Div(rows)

            except Exception as e:
                logger.error(f"Erreur widget trending coins: {e}")
                return html.Div("Erreur de chargement des tendances")

        self.register_callback(update_crypto_trending_coins, "update_crypto_trending_coins")

        @app.callback(
            Output("crypto-price-impact-widget", "children"),
            [Input("crypto-news-store", "data")]
        )
        def update_crypto_trends_widget(news_data):
            """Widget tendances crypto basé sur l'analyse des news"""
            try:
                if not news_data or not news_data.get("price_impact"):
                    # Tendances génériques de démonstration
                    return html.Div([
                        html.Div([
                            html.H6("🚀 DeFi en hausse", className="mb-1"),
                            html.P("Les protocoles décentralisés attirent plus d'attention",
                                  className="small text-muted"),
                        ], className="mb-3"),
                        html.Div([
                            html.H6("📈 Adoption institutionnelle", className="mb-1"),
                            html.P("Les grandes entreprises s'intéressent aux cryptos",
                                  className="small text-muted"),
                        ], className="mb-3"),
                        html.Div([
                            html.H6("⚡ Layer 2 Solutions", className="mb-1"),
                            html.P("Les solutions de mise à l'échelle gagnent du terrain",
                                  className="small text-muted"),
                        ])
                    ])

                # Utiliser les données d'impact prix du store
                price_impact = news_data.get("price_impact", {})

                trends = []
                if price_impact.get("high", 0) > 30:
                    trends.append({
                        "icon": "🚨",
                        "title": "Impact Élevé",
                        "description": "Événements majeurs détectés (ETF, régulations, etc.)"
                    })
                if price_impact.get("medium", 0) > 40:
                    trends.append({
                        "icon": "📈",
                        "title": "Momentum Moyen",
                        "description": "Partenariats et annonces importantes"
                    })

                # Ajouter tendances par défaut si aucune détectée
                if not trends:
                    trends = [
                        {
                            "icon": "📊",
                            "title": "Analyse en cours",
                            "description": "Analyse des tendances crypto en temps réel"
                        }
                    ]

                trend_divs = []
                for trend in trends[:3]:  # Limiter à 3 tendances
                    trend_divs.append(
                        html.Div([
                            html.H6(f"{trend['icon']} {trend['title']}", className="mb-1"),
                            html.P(trend['description'], className="small text-muted"),
                        ], className="mb-3")
                    )

                self.registry.register_callback(
                    "NewsCallbacks", "update_crypto_trends_widget",
                    ["crypto-news-store.data"], ["crypto-price-impact-widget.children"]
                )

                return html.Div(trend_divs)

            except Exception as e:
                logger.error(f"Erreur widget tendances crypto: {e}")
                return html.Div("Erreur de chargement des tendances")

        self.register_callback(update_crypto_trends_widget, "update_crypto_trends_widget")

        # Continuer avec les autres callbacks crypto...
        # (Migration complète des 5 callbacks crypto)

    def _register_economic_news_callbacks(self) -> None:
        """Enregistre les 4 callbacks du module economic news."""
        app = self.app

        @app.callback(
            [
                Output("economic-news-store", "data"),
                Output("economic-sentiment-store", "data"),
            ],
            [
                Input("refresh-economic-news-btn", "n_clicks"),
                Input("economic-news-interval", "n_intervals"),
            ],
        )
        def update_economic_news_data(refresh_clicks, interval_clicks):
            """Mettre à jour les données RSS économiques"""
            if not self.economic_news_module:
                return {}, {}

            # Récupérer news RSS
            news_result = self.economic_news_module.get_rss_news()
            articles = (
                news_result.get("news", []) if isinstance(news_result, dict) else []
            )

            # Analyser sentiment avec la liste d'articles
            sentiment = self.economic_news_module.analyze_sentiment(articles)

            # Extraire trending topics avec la liste d'articles
            trending = self.economic_news_module.extract_trending_topics(articles)

            # Calculer Fear & Greed avec la liste d'articles
            fear_greed = self.economic_news_module.calculate_fear_greed(articles, sentiment)

            # Analyser impact économique avec la liste d'articles
            economic_impact = self.economic_news_module.analyze_economic_impact(articles)

            # Format cohérent pour tous les widgets économiques
            news_data = {
                "news": articles,  # Liste d'articles pour les widgets
                "trending": trending,
                "fear_greed": fear_greed,
                "economic_impact": economic_impact,
                "total": len(articles),
                "timestamp": datetime.now().isoformat(),
            }

            self.registry.register_callback(
                "NewsCallbacks", "update_economic_news_data",
                ["refresh-economic-news-btn.n_clicks", "economic-news-interval.n_intervals"],
                ["economic-news-store.data", "economic-sentiment-store.data"]
            )

            return news_data, sentiment

        self.register_callback(update_economic_news_data, "update_economic_news_data")

        @app.callback(
            Output("economic-news-feed", "children"),
            [Input("economic-news-store", "data")]
        )
        def update_economic_news_feed(news_data):
            """Mettre à jour le feed de news économiques"""
            if not news_data or not news_data.get("news"):
                return dbc.Alert("Aucune news économique RSS disponible", color="warning")

            news_items = []
            for article in news_data["news"][:20]:
                # Déterminer couleur sentiment économique
                sentiment = article.get("sentiment", "neutral")
                if sentiment == "positive":
                    border_color = "border-success"
                    icon_color = "text-success"
                    icon = "fas fa-arrow-up"
                elif sentiment == "negative":
                    border_color = "border-danger"
                    icon_color = "text-danger"
                    icon = "fas fa-arrow-down"
                else:
                    border_color = "border-secondary"
                    icon_color = "text-muted"
                    icon = "fas fa-minus"

                # Créer item news économique avec sentiment
                news_item = dbc.Card(
                    [
                        dbc.CardHeader(
                            html.A(
                                article.get("title", "Titre indisponible"),
                                href=article.get("link", "#"),
                                target="_blank",
                                className="text-decoration-none",
                            )
                        ),
                        dbc.CardBody(
                            [
                                html.P(
                                    article.get("description", "Description indisponible")[:200] + "...",
                                    className="card-text small",
                                ),
                                html.Small(
                                    f"📅 {article.get('published', 'Date inconnue')} | "
                                    f"🔍 Source: {article.get('source', 'Inconnue')} | "
                                    f"💰 Impact: {article.get('economic_impact', 'N/A')}",
                                    className="text-muted",
                                ),
                                html.Div(
                                    [
                                        html.I(className=f"{icon} me-1 {icon_color}"),
                                        html.Span(
                                            sentiment.upper(),
                                            className=f"small {icon_color}"
                                        )
                                    ],
                                    className="mt-1"
                                )
                            ]
                        ),
                    ],
                    className=f"mb-3 {border_color}",
                )
                news_items.append(news_item)

            self.registry.register_callback(
                "NewsCallbacks", "update_economic_news_feed",
                ["economic-news-store.data"], ["economic-news-feed.children"]
            )

            return news_items

        self.register_callback(update_economic_news_feed, "update_economic_news_feed")

        @app.callback(
            [
                Output("gdp-indicator", "children"),
                Output("inflation-indicator", "children"),
                Output("unemployment-indicator", "children"),
                Output("fed-rate-indicator", "children"),
            ],
            [Input("economic-news-store", "data")]
        )
        def update_economic_macro_indicators(news_data):
            """Mise à jour des indicateurs macro-économiques"""
            # Valeurs par défaut (pourraient être récupérées via API économique)
            default_indicators = {
                "gdp": "2.1%",
                "inflation": "3.7%",
                "unemployment": "3.8%",
                "fed_rate": "5.25%",
            }

            # En Phase 6, ces données pourraient être récupérées d'APIs économiques réelles
            if news_data and news_data.get("macro_indicators"):
                indicators = news_data["macro_indicators"]
            else:
                indicators = default_indicators

            # Créer les indicateurs avec formatage
            gdp_indicator = html.Div([
                html.H5("GDP Growth", className="text-primary mb-1"),
                html.H3(indicators.get("gdp", "N/A"), className="mb-0")
            ])

            inflation_indicator = html.Div([
                html.H5("Inflation Rate", className="text-warning mb-1"),
                html.H3(indicators.get("inflation", "N/A"), className="mb-0")
            ])

            unemployment_indicator = html.Div([
                html.H5("Unemployment", className="text-info mb-1"),
                html.H3(indicators.get("unemployment", "N/A"), className="mb-0")
            ])

            fed_rate_indicator = html.Div([
                html.H5("Fed Rate", className="text-danger mb-1"),
                html.H3(indicators.get("fed_rate", "N/A"), className="mb-0")
            ])

            self.registry.register_callback(
                "NewsCallbacks", "update_economic_macro_indicators",
                ["economic-news-store.data"],
                ["gdp-indicator.children", "inflation-indicator.children",
                 "unemployment-indicator.children", "fed-rate-indicator.children"]
            )

            return gdp_indicator, inflation_indicator, unemployment_indicator, fed_rate_indicator

        self.register_callback(update_economic_macro_indicators, "update_economic_macro_indicators")

        @app.callback(
            Output("global-sentiment-gauge", "figure"),
            [Input("economic-news-store", "data")]
        )
        def update_economic_sentiment_gauge(news_data):
            """Gauge de sentiment économique global"""
            # Calcul du sentiment basé sur les news
            sentiment_score = 65  # Valeur par défaut

            if news_data and news_data.get("sentiment_data"):
                sentiment_data = news_data["sentiment_data"]
                sentiment_score = sentiment_data.get("average_sentiment", 65)

            # Créer le gauge économique
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=sentiment_score,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Sentiment Économique Global"},
                    delta={"reference": 50},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "bar": {"color": "darkblue"},
                        "steps": [
                            {"range": [0, 25], "color": "darkred"},
                            {"range": [25, 50], "color": "orange"},
                            {"range": [50, 75], "color": "yellow"},
                            {"range": [75, 100], "color": "green"}
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": sentiment_score
                        }
                    }
                )
            )

            fig.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=50, b=20)
            )

            self.registry.register_callback(
                "NewsCallbacks", "update_economic_sentiment_gauge",
                ["economic-news-store.data"], ["global-sentiment-gauge.figure"]
            )

            return fig

        self.register_callback(update_economic_sentiment_gauge, "update_economic_sentiment_gauge")

    def _register_phase4_callbacks(self) -> None:
        """Enregistre les 3 callbacks des extensions phase 4."""
        app = self.app

        @callback(
            Output("crypto-fear-greed-compact", "children"),
            [Input("crypto-compact-interval", "n_intervals")],
            prevent_initial_call=False,
        )
        def update_fear_greed_compact(n_intervals):
            """Mettre à jour le widget compact Fear & Greed"""
            try:
                data = fear_greed_gauge.get_fear_greed_index()
                if not data:
                    return html.P("N/A", className="text-muted mb-0")

                value = data["value"]
                classification = data["value_classification"]

                # Couleur selon valeur
                if value <= 25:
                    color_class = "text-danger"
                    emoji = "😱"
                elif value <= 45:
                    color_class = "text-warning"
                    emoji = "😰"
                elif value <= 55:
                    color_class = "text-secondary"
                    emoji = "😐"
                elif value <= 75:
                    color_class = "text-info"
                    emoji = "😊"
                else:
                    color_class = "text-success"
                    emoji = "🤑"

                return html.Div(
                    [
                        html.H5(f"{emoji} {value}", className=f"{color_class} mb-1"),
                        html.P(classification, className="small text-muted mb-0"),
                    ]
                )

            except Exception as e:
                logger.error(f"Erreur mise à jour Fear & Greed compact: {e}")
                return html.P("Erreur", className="text-muted small mb-0")

        @callback(
            Output("crypto-gainers-compact", "children"),
            [Input("crypto-compact-interval", "n_intervals")],
            prevent_initial_call=False,
        )
        def update_gainers_compact(n_intervals):
            """Mettre à jour le widget compact Top Gainers"""
            try:
                gainers = top_performers.get_top_gainers(3)
                if not gainers:
                    return html.P("N/A", className="text-muted small mb-0")

                items = []
                for gainer in gainers:
                    symbol = gainer["symbol"].replace("USDT", "")
                    change_pct = gainer.get("priceChangePercent", 0)

                    items.append(
                        html.Div(
                            f"{symbol}: +{change_pct:.2f}%",
                            className="small text-success mb-1"
                        )
                    )

                return html.Div(items)

            except Exception as e:
                logger.error(f"Erreur mise à jour Gainers compact: {e}")
                return html.P("Erreur", className="text-muted small mb-0")

        @callback(
            Output("crypto-trends-compact", "children"),
            [Input("crypto-compact-interval", "n_intervals")],
            prevent_initial_call=False,
        )
        def update_trends_compact(n_intervals):
            """Mettre à jour le widget compact Market Trends"""
            try:
                # Volume analysis
                volume_analysis = crypto_trends.get_volume_analysis()
                if not volume_analysis:
                    return html.P("N/A", className="text-muted small mb-0")

                sentiment = volume_analysis.get("market_sentiment", "Unknown")
                gainers_count = volume_analysis.get("gainers_count", 0)
                losers_count = volume_analysis.get("losers_count", 0)

                # Tendance générale
                if gainers_count > losers_count:
                    trend_emoji = "📈"
                    trend_color = "text-success"
                elif losers_count > gainers_count:
                    trend_emoji = "📉"
                    trend_color = "text-danger"
                else:
                    trend_emoji = "➡️"
                    trend_color = "text-secondary"

                return html.Div(
                    [
                        html.P(
                            f"{trend_emoji} {sentiment}",
                            className=f"{trend_color} mb-1"
                        ),
                        html.P(
                            f"Gainers: {gainers_count} | Losers: {losers_count}",
                            className="small text-muted mb-0"
                        ),
                    ]
                )

            except Exception as e:
                logger.error(f"Erreur mise à jour Trends compact: {e}")
                return html.P("Erreur", className="text-muted small mb-0")