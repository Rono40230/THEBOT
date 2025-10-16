from src.thebot.core.logger import logger
"""
Base News Module for THEBOT
Contains common functionality for news modules
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import ALL, Input, Output, State, callback, dcc, html

from ..data_providers.real_data_manager import real_data_manager
from .base_market_module import BaseMarketModule

# Import pour la traduction
try:
    from googletrans import Translator

    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False
    logger.info("⚠️ Traduction non disponible: googletrans non installé")


class BaseNewsModule(BaseMarketModule):
    """Base class for news modules with common functionality"""

    def __init__(self, news_type: str, calculators: Dict = None):
        super().__init__(
            market_type=news_type,
            data_provider=real_data_manager,
            calculators=calculators,
        )

        self.news_type = news_type  # 'economic' or 'crypto'

        # Ajout pour compatibilité avec la nouvelle architecture
        self.translator = None
        if TRANSLATION_AVAILABLE:
            try:
                self.translator = Translator()
            except Exception as e:
                logger.info(f"⚠️ Erreur initialisation traducteur: {e}")

    def get_symbols_list(self) -> List[str]:
        """Get available news categories (required by BaseMarketModule)"""
        return ["All News", "Breaking News", "Market Analysis", "Industry News"]

    def get_default_symbol(self) -> str:
        """Get default news category"""
        return "All News"

    def load_market_data(
        self, category: str = "All News", time_range: str = "24h", limit: int = 50
    ) -> pd.DataFrame:
        """Load news data filtered by news type"""
        # Load the news data
        news_data = self.load_news_data(category, limit)

        # Apply time filtering
        if not news_data.empty and "time_published" in news_data.columns:
            news_data = self._filter_by_time_range(news_data, time_range)

        return news_data

    def load_news_data(
        self, category: str = "All News", limit: int = 50
    ) -> pd.DataFrame:
        """Load news data from multiple providers via real_data_manager"""
        try:
            logger.info(f"🔄 Loading {self.news_type} news data for category: {category}...")

            # Get news sources based on news type
            sources = self._get_news_sources()

            # Utiliser real_data_manager pour récupérer les news filtrées
            news_list = self.data_provider.get_news_data(sources=sources, limit=limit)

            # Filter by news type
            filtered_news = self._filter_news_by_type(news_list)

            if filtered_news and len(filtered_news) > 0:
                # Convert list of news items to DataFrame
                news_data = pd.DataFrame(filtered_news)

                logger.info(
                    f"✅ {self.news_type}: {len(news_data)} news articles loaded from filtered providers"
                )
                return news_data
            else:
                logger.info(f"❌ No {self.news_type} news data available from providers")
                return pd.DataFrame()

        except Exception as e:
            logger.info(f"❌ Error loading {self.news_type} news data: {e}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    def _get_news_sources(self) -> List[str]:
        """Get news sources based on news type - to be overridden by subclasses"""
        return ["binance", "crypto_panic", "coin_gecko", "yahoo", "fmp"]

    def _filter_news_by_type(self, news_list: List[Dict]) -> List[Dict]:
        """Filter news by type - to be overridden by subclasses"""
        return news_list

    def _filter_by_time_range(
        self, data: pd.DataFrame, time_range: str
    ) -> pd.DataFrame:
        """Filter news data by time range"""
        if time_range == "all" or not time_range:
            return data

        try:
            # Check for time_published or published_at column
            time_col = None
            if "time_published" in data.columns:
                time_col = "time_published"
            elif "published_at" in data.columns:
                time_col = "published_at"
            else:
                logger.info("⚠️ No time column found, returning unfiltered data")
                return data

            # Convert time column to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(data[time_col]):
                data[time_col] = pd.to_datetime(data[time_col], errors="coerce")

            # Calculate cutoff time
            now = datetime.now()
            if time_range == "6h":
                cutoff = now - timedelta(hours=6)
            elif time_range == "24h":
                cutoff = now - timedelta(hours=24)
            elif time_range == "3d":
                cutoff = now - timedelta(days=3)
            elif time_range == "7d":
                cutoff = now - timedelta(days=7)
            else:
                return data

            # Filter data
            filtered_data = data[data[time_col] >= cutoff]
            logger.info(
                f"📅 Time filter ({time_range}): {len(data)} → {len(filtered_data)} articles"
            )
            return filtered_data

        except Exception as e:
            logger.info(f"⚠️ Error filtering by time: {e}")
            return data

    def _calculate_time_ago(self, published_time: str) -> str:
        """Calculate human-readable time ago"""
        try:
            if pd.isna(published_time):
                return "Date inconnue"

            # Parse the time
            if isinstance(published_time, str):
                pub_time = pd.to_datetime(published_time, errors="coerce")
            else:
                pub_time = published_time

            if pd.isna(pub_time):
                return "Date inconnue"

            # Calculate difference
            now = datetime.now()
            if pub_time.tzinfo is not None:
                # Convert to naive datetime for comparison
                pub_time = pub_time.replace(tzinfo=None)

            diff = now - pub_time

            if diff.days > 0:
                return f"il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"il y a {hours}h"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"il y a {minutes}min"
            else:
                return "À l'instant"

        except Exception as e:
            logger.info(f"⚠️ Error calculating time ago: {e}")
            return "Date inconnue"

    def create_news_feed(
        self, news_data: pd.DataFrame, sentiment_filter: str = "all"
    ) -> tuple:
        """Create news feed HTML and return articles data"""
        if news_data.empty:
            return (
                html.Div(
                    [
                        html.P(
                            f"Aucune actualité {self.news_type} disponible pour le moment.",
                            className="text-muted text-center p-4",
                        )
                    ]
                ),
                [],
            )

        # Convert to list of dicts for easier processing
        articles_data = []
        for idx, article in news_data.iterrows():
            # Calculate time ago
            time_ago = self._calculate_time_ago(
                article.get("published_at", article.get("time_published", ""))
            )

            articles_data.append(
                {
                    "title": article.get("title", ""),
                    "summary": article.get("description", article.get("summary", "")),
                    "url": article.get("url", ""),
                    "source": article.get("source", "Unknown"),
                    "published_at": article.get(
                        "published_at", article.get("time_published", "")
                    ),
                    "sentiment": article.get("sentiment", "neutral"),
                    "time_ago": time_ago,
                }
            )

        # Apply sentiment filter
        if sentiment_filter != "all":
            articles_data = [
                a
                for a in articles_data
                if a.get("sentiment", "neutral") == sentiment_filter
            ]

        # Create news items HTML
        news_items = []
        for idx, article in enumerate(articles_data):
            # Time ago calculation
            time_ago = article["time_ago"]

            # Sentiment badge
            sentiment = article.get("sentiment", "neutral")
            # Handle case where sentiment might be NaN or None
            if pd.isna(sentiment) or sentiment is None or sentiment == "":
                sentiment = "neutral"
            # Ensure sentiment is a string
            sentiment = str(sentiment).lower()

            sentiment_colors = {
                "positive": "success",
                "negative": "danger",
                "neutral": "secondary",
            }
            sentiment_icons = {"positive": "😊", "negative": "😟", "neutral": "😐"}
            sentiment_badge = dbc.Badge(
                [sentiment_icons.get(sentiment, "😐"), f" {sentiment.title()}"],
                color=sentiment_colors.get(sentiment, "secondary"),
                className="me-2",
            )

            news_item = dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.Div(
                                [
                                    html.H6(
                                        article["title"], className="card-title mb-2"
                                    ),
                                    html.P(
                                        article.get(
                                            "description", article.get("summary", "")
                                        )[:200]
                                        + "...",
                                        className="card-text text-muted small",
                                    ),
                                    html.Div(
                                        [
                                            sentiment_badge,
                                            dbc.Badge(
                                                article.get("source", "Unknown"),
                                                color="light",
                                                text_color="dark",
                                                className="me-2",
                                            ),
                                            html.Small(
                                                time_ago, className="text-muted"
                                            ),
                                        ],
                                        className="d-flex align-items-center",
                                    ),
                                    html.Hr(className="my-2"),
                                    html.Div(
                                        [
                                            # Bouton pour lire l'article directement (lien externe)
                                            *(
                                                [
                                                    dbc.Button(
                                                        "📖 Lire l'article",
                                                        size="sm",
                                                        color="outline-primary",
                                                        href=article.get("url", "#"),
                                                        target="_blank",
                                                        className="me-2",
                                                    )
                                                ]
                                                if article.get("url")
                                                and article.get("url") != "#"
                                                and article.get("url").startswith(
                                                    ("http://", "https://")
                                                )
                                                else []
                                            ),
                                            # Bouton avec source et date
                                            dbc.Button(
                                                f"{article.get('source', 'Unknown')} • {time_ago}",
                                                size="sm",
                                                color="light",
                                                className="text-muted",
                                                style={
                                                    "cursor": "default",
                                                    "pointer-events": "none",
                                                },
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ]
                    )
                ],
                className="mb-3",
            )

            news_items.append(news_item)

        return html.Div(news_items), articles_data

    def create_market_impact_widget(self, news_data: pd.DataFrame) -> html.Div:
        """Create market impact analysis widget"""
        if news_data.empty:
            return html.Div(
                "Pas de données d'impact disponibles", className="text-muted"
            )

        try:
            # Simple market impact analysis
            total_articles = len(news_data)

            # Count sentiments if available
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            if "sentiment" in news_data.columns:
                sentiment_counts = news_data["sentiment"].value_counts().to_dict()

            # Create impact visualization
            return html.Div(
                [
                    html.H6("Analyse d'Impact", className="mb-3"),
                    html.Div(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.H4(
                                                str(total_articles),
                                                className="text-primary mb-0",
                                            ),
                                            html.Small(
                                                "Articles totaux",
                                                className="text-muted",
                                            ),
                                        ],
                                        width=12,
                                        className="text-center mb-3",
                                    )
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.H6("Sentiment", className="mb-2"),
                                            html.Div(
                                                [
                                                    dbc.Progress(
                                                        value=sentiment_counts.get(
                                                            "positive", 0
                                                        ),
                                                        color="success",
                                                        className="mb-1",
                                                        label=f"Positif: {sentiment_counts.get('positive', 0)}",
                                                    ),
                                                    dbc.Progress(
                                                        value=sentiment_counts.get(
                                                            "neutral", 0
                                                        ),
                                                        color="info",
                                                        className="mb-1",
                                                        label=f"Neutre: {sentiment_counts.get('neutral', 0)}",
                                                    ),
                                                    dbc.Progress(
                                                        value=sentiment_counts.get(
                                                            "negative", 0
                                                        ),
                                                        color="danger",
                                                        className="mb-1",
                                                        label=f"Négatif: {sentiment_counts.get('negative', 0)}",
                                                    ),
                                                ]
                                            ),
                                        ]
                                    )
                                ]
                            ),
                        ]
                    ),
                ]
            )

        except Exception as e:
            logger.info(f"⚠️ Error creating market impact widget: {e}")
            return html.Div("Erreur d'analyse d'impact", className="text-muted")

    def create_economic_calendar_widget(self) -> html.Div:
        """Create economic calendar widget"""
        # This is a placeholder - would need real economic calendar data
        return html.Div(
            [
                html.H6("Calendrier Économique", className="mb-3"),
                html.Div(
                    [
                        html.P(
                            "📅 Événements économiques à venir", className="text-muted"
                        ),
                        html.Small(
                            "Fonctionnalité en développement...", className="text-muted"
                        ),
                    ]
                ),
            ]
        )

    def translate_to_french(self, text: str) -> str:
        """Translate text to French using Google Translate"""
        if not TRANSLATION_AVAILABLE or not self.translator:
            return text

        try:
            if not text or len(text.strip()) == 0:
                return text

            # Don't translate if already in French (basic detection)
            french_words = [
                "le",
                "la",
                "les",
                "et",
                "est",
                "une",
                "des",
                "pour",
                "dans",
                "avec",
            ]
            if any(word in text.lower() for word in french_words):
                return text

            # Translate
            translated = self.translator.translate(text, dest="fr")
            return translated.text if translated.text else text

        except Exception as e:
            logger.info(f"⚠️ Erreur traduction: {e}")
            return text

    def setup_callbacks(self, app):
        """Setup callbacks for the news module - to be overridden by subclasses"""
        pass
