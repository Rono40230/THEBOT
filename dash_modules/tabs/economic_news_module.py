"""
Economic News Module for THEBOT
News économiques exclusivement alimentées par RSS avec widgets AI
"""

import json
import re
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import ALL, Input, Output, State, callback, dcc, html
from plotly.subplots import make_subplots

# Import RSS News Manager
try:
    from ..data_providers.rss_news_manager import rss_news_manager

    RSS_AVAILABLE = True
except ImportError:
    print("⚠️ RSS News Manager non disponible")
    RSS_AVAILABLE = False

# Import AI Engine
try:
    from ..ai_engine.smart_ai_manager import smart_ai_manager

    AI_AVAILABLE = True
except ImportError:
    print("⚠️ Smart AI Manager non disponible")
    AI_AVAILABLE = False


class EconomicNewsModule:
    """Module News Économiques alimenté exclusivement par RSS avec widgets AI complets"""

    def __init__(self, calculators: Dict = None):
        self.calculators = calculators or {}
        self.news_cache = []
        self.sentiment_cache = {}
        self.trending_cache = []
        self.last_update = None

        # Configuration économique
        self.economic_keywords = [
            "économie",
            "économique",
            "finance",
            "financier",
            "banque",
            "bourse",
            "marché",
            "action",
            "obligation",
            "taux",
            "inflation",
            "croissance",
            "pib",
            "fed",
            "bce",
            "banque centrale",
            "politique monétaire",
            "commerce",
            "industrie",
            "emploi",
            "chômage",
            "consommation",
            "economy",
            "economic",
            "finance",
            "financial",
            "banking",
            "stock market",
            "market",
            "stock",
            "bond",
            "rate",
            "inflation",
            "growth",
            "gdp",
            "federal reserve",
            "central bank",
            "monetary policy",
            "trade",
            "industry",
            "employment",
            "unemployment",
            "consumption",
            "earnings",
            "revenue",
            "profit",
            "dividend",
            "treasury",
        ]

        self.exclude_keywords = [
            "bitcoin",
            "btc",
            "ethereum",
            "eth",
            "crypto",
            "cryptocurrency",
            "altcoin",
            "defi",
            "nft",
            "blockchain",
            "mining",
        ]

        print("✅ Economic News Module initialisé (RSS exclusif)")

    def translate_article_title(self, title: str) -> str:
        """Traduire titre d'article en français"""
        try:
            if not title or len(title.strip()) < 3:
                return title

            if AI_AVAILABLE:
                translated = smart_ai_manager.translate_to_french(title)
                if translated and len(translated.strip()) > 3 and translated != title:
                    return translated
                else:
                    return title
            return title
        except Exception as e:
            print(f"❌ Erreur traduction titre: {e}")
            return title

    def translate_article_summary(self, summary: str) -> str:
        """Traduire résumé d'article en français"""
        try:
            if not summary or len(summary.strip()) < 10:
                return summary

            if AI_AVAILABLE:
                translated = smart_ai_manager.translate_to_french(summary)
                if (
                    translated
                    and len(translated.strip()) > 10
                    and translated != summary
                ):
                    return translated
                else:
                    return summary
            return summary
        except Exception as e:
            print(f"❌ Erreur traduction résumé: {e}")
            return summary

    def _format_date(self, date_value):
        """Formater une date pour l'affichage - identique au module crypto"""
        if not date_value or date_value in ["N/A", "Unknown Date", ""]:
            return "Date inconnue"

        try:
            # Si c'est déjà une string formatée, la retourner
            if isinstance(date_value, str):
                # Essayer de parser différents formats
                from datetime import datetime

                try:
                    # Format ISO avec timezone
                    if "T" in date_value and ("+" in date_value or "Z" in date_value):
                        dt = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
                        return dt.strftime("%d/%m/%Y %H:%M")
                    # Format ISO simple
                    elif "T" in date_value:
                        dt = datetime.fromisoformat(date_value)
                        return dt.strftime("%d/%m/%Y %H:%M")
                    # Déjà formaté
                    else:
                        return date_value
                except:
                    return date_value
            # Si c'est un objet datetime
            elif hasattr(date_value, "strftime"):
                return date_value.strftime("%d/%m/%Y %H:%M")
            else:
                return str(date_value)
        except Exception as e:
            return "Date invalide"

    def get_rss_news(self, limit: int = 20) -> Dict:
        """Récupérer les news RSS économiques avec traduction"""
        try:
            if not RSS_AVAILABLE:
                return {"news": [], "total": 0, "source": "RSS indisponible"}

            # Récupérer news RSS (utiliser toutes les catégories disponibles)
            rss_news = rss_news_manager.get_news(
                categories=None, limit=limit  # Toutes les catégories
            )

            if not rss_news:
                return {"news": [], "total": 0, "source": "RSS"}

            # Normaliser le résultat RSS (peut être une liste ou un dict)
            if isinstance(rss_news, list):
                all_news = rss_news
            else:
                all_news = rss_news.get("articles", [])

            # Filtrer et enrichir pour économie
            economic_news = []

            for article in all_news:
                # Vérifier si pertinent pour économie
                title = (article.get("title", "") or "").lower()
                description = (article.get("description", "") or "").lower()
                content = f"{title} {description}"

                # Score de pertinence économique
                relevance_score = sum(
                    1 for keyword in self.economic_keywords if keyword in content
                )

                if relevance_score >= 1:  # Au moins 1 keyword économique
                    # Extraire données avec les bons champs RSS
                    original_title = (
                        article.get("title")
                        or article.get("headline")
                        or "Titre non disponible"
                    )

                    # Utiliser les champs RSS corrects
                    original_summary = (
                        article.get("summary")  # Champ RSS principal
                        or article.get("description")
                        or article.get("content")
                        or article.get("excerpt")
                        or "Résumé non disponible"
                    )

                    # Limiter la longueur du résumé
                    if len(original_summary) > 300:
                        original_summary = original_summary[:300] + "..."

                    # Source avec fallbacks - utiliser les champs RSS corrects
                    source = (
                        article.get("source")  # Champ RSS principal
                        or article.get("feed_title")  # Titre du feed RSS
                        or article.get("provider")
                        or article.get("site_name")
                        or article.get("author")
                        or "RSS Feed"
                    )

                    # Date avec champs RSS corrects
                    published_time = (
                        article.get("published_date")  # Champ RSS principal
                        or article.get("published_time")
                        or article.get("pubDate")
                        or "Récent"
                    )

                    # Traduire seulement si contenu valide
                    if (
                        len(original_title) > 5
                        and original_title != "Titre non disponible"
                    ):
                        translated_title = self.translate_article_title(original_title)
                    else:
                        translated_title = original_title

                    if (
                        len(original_summary) > 10
                        and original_summary != "Résumé non disponible"
                    ):
                        translated_summary = self.translate_article_summary(
                            original_summary
                        )
                    else:
                        translated_summary = original_summary

                    # Enrichir article
                    enriched_article = {
                        "title": translated_title,
                        "original_title": original_title,
                        "summary": translated_summary,
                        "original_summary": original_summary,
                        "source": source,
                        "published_time": published_time,
                        "url": article.get("url") or article.get("link") or "#",
                        "relevance_score": relevance_score,
                        "category": "economy",
                    }

                    # Analyser sentiment avec IA si disponible
                    if AI_AVAILABLE:
                        sentiment_result = smart_ai_manager.analyze_with_best_ai(
                            {
                                "news_articles": [
                                    original_title + " " + original_summary
                                ]
                            },
                            task_type="sentiment",
                        )

                        sentiment = sentiment_result.get("sentiment", "neutral")
                        if sentiment == "bullish":
                            enriched_article["sentiment"] = "positive"
                        elif sentiment == "bearish":
                            enriched_article["sentiment"] = "negative"
                        else:
                            enriched_article["sentiment"] = "neutral"

                        enriched_article["sentiment_confidence"] = sentiment_result.get(
                            "confidence", 50
                        )
                    else:
                        enriched_article["sentiment"] = "neutral"
                        enriched_article["sentiment_confidence"] = 50

                    economic_news.append(enriched_article)

            # Trier par pertinence puis par temps
            economic_news.sort(
                key=lambda x: (x["relevance_score"], x["published_time"]), reverse=True
            )

            print(
                f"✅ {len(economic_news)} news économiques RSS récupérées (traduites)"
            )

            return {
                "news": economic_news[:limit],
                "total": len(economic_news),
                "source": "RSS",
                "categories": ["economy", "business", "finance"],
            }

        except Exception as e:
            print(f"❌ Erreur récupération RSS économique: {e}")
            return {"news": [], "total": 0, "source": "RSS Error"}

    def _is_economic_news(self, article: Dict) -> bool:
        """Déterminer si un article est économique"""
        text_to_check = (
            f"{article.get('title', '')} {article.get('summary', '')}".lower()
        )

        # Vérifier présence de mots-clés économiques
        has_economic = any(
            keyword in text_to_check for keyword in self.economic_keywords
        )

        # Exclure crypto explicitement
        has_crypto = any(keyword in text_to_check for keyword in self.exclude_keywords)

        return has_economic and not has_crypto

    def _get_fallback_news(self) -> List[Dict]:
        """News simulées en cas d'échec RSS"""
        return [
            {
                "title": "Fed Maintains Interest Rates at 5.25%",
                "summary": "Federal Reserve keeps rates steady amid inflation concerns...",
                "published_time": datetime.now() - timedelta(hours=1),
                "source": "RSS Economic Feed",
                "url": "#",
                "sentiment": "neutral",
            },
            {
                "title": "EU Economic Growth Slows to 0.1% in Q3",
                "summary": "European economy shows signs of slowdown with GDP growth...",
                "published_time": datetime.now() - timedelta(hours=2),
                "source": "RSS Economic Feed",
                "url": "#",
                "sentiment": "negative",
            },
            {
                "title": "Tech Stocks Rally on AI Innovation",
                "summary": "Technology sector leads market gains as AI developments...",
                "published_time": datetime.now() - timedelta(hours=3),
                "source": "RSS Economic Feed",
                "url": "#",
                "sentiment": "positive",
            },
        ]

    def analyze_sentiment(self, articles: List[Dict]) -> Dict:
        """Analyser le sentiment des articles avec IA"""
        if not AI_AVAILABLE or not articles:
            return {"positive": 30, "neutral": 50, "negative": 20, "confidence": 0.6}

        try:
            # Analyser avec Smart AI Manager
            sentiments = []
            for article in articles[:20]:  # Limiter pour performance
                text = f"{article.get('title', '')} {article.get('summary', '')}"
                if len(text.strip()) > 10:
                    result = smart_ai_manager.analyze_with_best_ai(
                        {"text": text}, "sentiment"
                    )
                    sentiment = result.get("sentiment", "neutral")
                    sentiments.append(sentiment)

            if not sentiments:
                return {
                    "positive": 30,
                    "neutral": 50,
                    "negative": 20,
                    "confidence": 0.6,
                }

            # Calculer distribution
            sentiment_counts = Counter(sentiments)
            total = len(sentiments)

            result = {
                "positive": round(
                    (sentiment_counts.get("positive", 0) / total) * 100, 1
                ),
                "neutral": round((sentiment_counts.get("neutral", 0) / total) * 100, 1),
                "negative": round(
                    (sentiment_counts.get("negative", 0) / total) * 100, 1
                ),
                "confidence": 0.85,
            }

            self.sentiment_cache = result
            return result

        except Exception as e:
            print(f"❌ Erreur analyse sentiment: {e}")
            return {"positive": 30, "neutral": 50, "negative": 20, "confidence": 0.6}

    def extract_trending_topics(self, articles: List[Dict]) -> List[Dict]:
        """Extraire les sujets tendance avec IA"""
        if not articles:
            return []

        try:
            # Extraire mots-clés de tous les titres
            all_text = " ".join([article.get("title", "") for article in articles])

            # Compter les mots importants
            words = re.findall(r"\b[A-Za-zÀ-ÿ]{4,}\b", all_text.lower())
            word_counts = Counter(words)

            # Filtrer et créer sujets tendance
            trending = []
            for word, count in word_counts.most_common(10):
                if word in self.economic_keywords and count > 1:
                    trending.append(
                        {
                            "topic": word.title(),
                            "count": count,
                            "trend": "up" if count > 2 else "stable",
                        }
                    )

            self.trending_cache = trending[:8]  # Top 8
            return self.trending_cache

        except Exception as e:
            print(f"❌ Erreur trending topics: {e}")
            return []

    def calculate_fear_greed_index(self, articles: List[Dict], sentiment: Dict) -> Dict:
        """Calculer l'indice Fear & Greed pour l'économie"""
        try:
            # Facteurs économiques
            positive_pct = sentiment.get("positive", 30)
            negative_pct = sentiment.get("negative", 20)

            # Calcul basé sur sentiment et volume de news
            news_volume_factor = min(len(articles) / 20, 1.0)  # Normaliser
            sentiment_factor = (positive_pct - negative_pct) / 100

            # Score final (0-100)
            fear_greed_score = 50 + (sentiment_factor * 40) + (news_volume_factor * 10)
            fear_greed_score = max(0, min(100, fear_greed_score))

            # Classification
            if fear_greed_score >= 75:
                classification = "Extreme Greed"
                color = "#16a34a"
            elif fear_greed_score >= 55:
                classification = "Greed"
                color = "#22c55e"
            elif fear_greed_score >= 45:
                classification = "Neutral"
                color = "#eab308"
            elif fear_greed_score >= 25:
                classification = "Fear"
                color = "#f97316"
            else:
                classification = "Extreme Fear"
                color = "#dc2626"

            return {
                "score": round(fear_greed_score, 1),
                "classification": classification,
                "color": color,
                "confidence": sentiment.get("confidence", 0.7),
            }

        except Exception as e:
            print(f"❌ Erreur Fear & Greed: {e}")
            return {
                "score": 50.0,
                "classification": "Neutral",
                "color": "#eab308",
                "confidence": 0.5,
            }

    def get_layout(self) -> html.Div:
        """Layout principal avec widgets AI simplifiés"""
        return html.Div(
            [
                # Indicateurs Macro-Économiques (gardé)
                dbc.Row(
                    [
                        # Indicateurs Clés
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.I(
                                                    className="fas fa-chart-bar me-2"
                                                ),
                                                "Indicateurs Macro",
                                            ]
                                        ),
                                        dbc.CardBody(
                                            [
                                                html.Div(
                                                    [
                                                        # PIB, Inflation, Chômage, etc.
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        html.H6(
                                                                            "📈 PIB",
                                                                            className="text-center text-muted",
                                                                        ),
                                                                        html.H5(
                                                                            "2.1%",
                                                                            className="text-center text-success",
                                                                            id="gdp-indicator",
                                                                        ),
                                                                    ],
                                                                    width=3,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        html.H6(
                                                                            "🔥 Inflation",
                                                                            className="text-center text-muted",
                                                                        ),
                                                                        html.H5(
                                                                            "3.7%",
                                                                            className="text-center text-warning",
                                                                            id="inflation-indicator",
                                                                        ),
                                                                    ],
                                                                    width=3,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        html.H6(
                                                                            "💼 Chômage",
                                                                            className="text-center text-muted",
                                                                        ),
                                                                        html.H5(
                                                                            "3.8%",
                                                                            className="text-center text-info",
                                                                            id="unemployment-indicator",
                                                                        ),
                                                                    ],
                                                                    width=3,
                                                                ),
                                                                dbc.Col(
                                                                    [
                                                                        html.H6(
                                                                            "💰 Taux Fed",
                                                                            className="text-center text-muted",
                                                                        ),
                                                                        html.H5(
                                                                            "5.25%",
                                                                            className="text-center text-danger",
                                                                            id="fed-rate-indicator",
                                                                        ),
                                                                    ],
                                                                    width=3,
                                                                ),
                                                            ]
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ],
                            width=6,
                        ),
                        # Sentiment Global
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.I(
                                                    className="fas fa-globe-americas me-2"
                                                ),
                                                "Sentiment Global",
                                            ]
                                        ),
                                        dbc.CardBody(
                                            [
                                                dcc.Graph(
                                                    id="global-sentiment-gauge",
                                                    style={"height": "200px"},
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ],
                            width=6,
                        ),
                    ],
                    className="mb-4",
                ),
                # News Feed Principal
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.I(className="fas fa-rss me-2"),
                                                "Live RSS Economic News Feed",
                                                dbc.Button(
                                                    [
                                                        html.I(
                                                            className="fas fa-sync-alt"
                                                        )
                                                    ],
                                                    id="refresh-economic-news-btn",
                                                    color="info",
                                                    size="sm",
                                                    className="float-end ms-2",
                                                    style={"padding": "0.25rem 0.5rem"},
                                                ),
                                            ]
                                        ),
                                        dbc.CardBody(
                                            [
                                                html.Div(
                                                    id="economic-news-feed",
                                                    style={
                                                        "maxHeight": "600px",
                                                        "overflowY": "auto",
                                                    },
                                                )
                                            ]
                                        ),
                                    ]
                                )
                            ],
                            width=12,
                        )
                    ]
                ),
                # Store pour données
                dcc.Store(id="economic-news-store"),
                dcc.Store(id="economic-sentiment-store"),
                # Interval pour auto-refresh
                dcc.Interval(
                    id="economic-news-interval",
                    interval=60000,  # 1 minute
                    n_intervals=0,
                ),
            ],
            className="p-3",
        )

    def setup_callbacks(self, app):
        """Configurer les callbacks pour Economic News"""

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
            # Récupérer news RSS
            news_result = self.get_rss_news()
            articles = (
                news_result.get("news", []) if isinstance(news_result, dict) else []
            )

            # Analyser sentiment avec la liste d'articles
            sentiment = self.analyze_sentiment(articles)

            # Extraire trending topics avec la liste d'articles
            trending = self.extract_trending_topics(articles)

            # Calculer Fear & Greed avec la liste d'articles
            fear_greed = self.calculate_fear_greed_index(articles, sentiment)

            return {
                "news": articles,
                "trending": trending,
                "fear_greed": fear_greed,
                "timestamp": datetime.now().isoformat(),
            }, sentiment

        @app.callback(
            Output("economic-news-feed", "children"),
            [Input("economic-news-store", "data")],
        )
        def update_news_feed(news_data):
            """Mettre à jour le feed de news"""
            if not news_data or not news_data.get("news"):
                return dbc.Alert("Aucune news RSS disponible", color="warning")

            news_items = []
            for article in news_data["news"][:20]:
                # Déterminer couleur sentiment
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
                    border_color = "border-warning"
                    icon_color = "text-warning"
                    icon = "fas fa-minus"

                news_items.append(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.H6(
                                                        article.get(
                                                            "title", "No Title"
                                                        ),
                                                        className="mb-2",
                                                    ),
                                                    html.P(
                                                        article.get(
                                                            "summary",
                                                            "No summary available",
                                                        )[:200]
                                                        + "...",
                                                        className="text-muted small mb-2",
                                                    ),
                                                    html.Div(
                                                        [
                                                            dbc.Badge(
                                                                article.get(
                                                                    "source", "RSS"
                                                                ),
                                                                color="info",
                                                                className="me-2",
                                                            ),
                                                            html.Small(
                                                                [
                                                                    html.I(
                                                                        className="fas fa-clock me-1"
                                                                    ),
                                                                    self._format_date(
                                                                        article.get(
                                                                            "published_time",
                                                                            "N/A",
                                                                        )
                                                                    ),
                                                                ],
                                                                className="text-muted me-3",
                                                            ),
                                                            dbc.Button(
                                                                [
                                                                    html.I(
                                                                        className="fas fa-external-link-alt me-1"
                                                                    ),
                                                                    "Lire l'article",
                                                                ],
                                                                href=article.get(
                                                                    "url", "#"
                                                                ),
                                                                target="_blank",
                                                                color="primary",
                                                                size="sm",
                                                                outline=True,
                                                                className="ms-2",
                                                            ),
                                                        ],
                                                        className="d-flex align-items-center",
                                                    ),
                                                ],
                                                width=10,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.I(
                                                        className=f"{icon} {icon_color}",
                                                        style={"fontSize": "1.5rem"},
                                                    )
                                                ],
                                                width=2,
                                                className="text-center",
                                            ),
                                        ]
                                    )
                                ]
                            )
                        ],
                        className=f"mb-3 {border_color}",
                    )
                )

            return news_items

        # Nouveaux callbacks Phase 5 - Indicateurs Macro-Économiques
        @app.callback(
            [
                Output("gdp-indicator", "children"),
                Output("inflation-indicator", "children"),
                Output("unemployment-indicator", "children"),
                Output("fed-rate-indicator", "children"),
            ],
            [Input("economic-news-store", "data")],
        )
        def update_macro_indicators(news_data):
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

            return (
                indicators.get("gdp", "2.1%"),
                indicators.get("inflation", "3.7%"),
                indicators.get("unemployment", "3.8%"),
                indicators.get("fed_rate", "5.25%"),
            )

        @app.callback(
            Output("global-sentiment-gauge", "figure"),
            [Input("economic-news-store", "data")],
        )
        def update_global_sentiment_gauge(news_data):
            """Gauge de sentiment économique global"""
            # Calcul du sentiment basé sur les news
            sentiment_score = 65  # Valeur par défaut

            if news_data and news_data.get("sentiment_data"):
                sentiment_data = news_data["sentiment_data"]
                sentiment_score = sentiment_data.get("average_sentiment", 65)

            # Création du gauge
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=sentiment_score,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Sentiment Économique"},
                    delta={"reference": 50},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "bar": {
                            "color": (
                                "lightgreen"
                                if sentiment_score > 60
                                else "orange" if sentiment_score > 40 else "red"
                            )
                        },
                        "steps": [
                            {"range": [0, 40], "color": "lightgray"},
                            {"range": [40, 60], "color": "gray"},
                            {"range": [60, 100], "color": "lightgreen"},
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": 50,
                        },
                    },
                )
            )

            fig.update_layout(
                height=200,
                margin=dict(l=20, r=20, t=40, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
            )

            return fig


# ============================================================================
# FONCTION D'EXPORT POUR COMPATIBILITÉ
# ============================================================================


def get_economic_news_tab():
    """
    Fonction d'export pour compatibilité avec l'ancien système
    """
    module = EconomicNewsModule()
    return module.get_layout()
