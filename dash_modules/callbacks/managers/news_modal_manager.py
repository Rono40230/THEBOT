from src.thebot.core.logger import logger
"""
News Modal Manager - Contrôleur MVC pour les actualités
Gère les callbacks en utilisant NewsService pour la logique métier
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html

from ..base.callback_manager import CallbackManager
from ...services import news_service
from ...core.price_formatter import format_crypto_price_adaptive

logger = logging.getLogger(__name__)


class NewsModalManager(CallbackManager):
    """
    Contrôleur pour les actualités.
    Gère tous les callbacks liés aux actualités en utilisant NewsService.
    """

    def __init__(self, app):
        super().__init__(app, "NewsModalManager")

    def register_all_callbacks(self) -> None:
        """Enregistre tous les callbacks des actualités"""
        logger.info("🔄 Enregistrement des callbacks modal news...")

        self._register_news_data_callbacks()

        self.log_callback_registration()
        logger.info("✅ Callbacks modal news enregistrés")

    def _register_news_data_callbacks(self) -> None:
        """Enregistre les callbacks des actualités"""

        @self.app.callback(
            [
                Output("news-store", "data"),
                Output("news-articles-list", "children"),
                Output("news-summary-stats", "children"),
            ],
            [
                Input("news-refresh-interval", "n_intervals"),
                Input("news-refresh-btn", "n_clicks"),
            ],
            [
                State("news-symbol-filter", "value"),
                State("news-limit-input", "value"),
            ],
            prevent_initial_call=False,
        )
        def update_news_data(n_intervals, refresh_clicks, symbol_filter, limit):
            """Met à jour les actualités depuis NewsService"""
            try:
                # Paramètres par défaut
                symbol = symbol_filter.strip() if symbol_filter else None
                limit = limit or 50

                # Récupérer les actualités depuis le service
                news_articles = news_service.get_news(symbol=symbol, limit=limit)

                # Préparer les données pour le store
                store_data = [article.to_dict() for article in news_articles]

                # Créer la liste d'articles
                articles_list = []
                for article in news_articles:
                    article_card = html.Div([
                        html.H5(article.title, className="news-title"),
                        html.P(
                            article.summary[:200] + "..." if article.summary and len(article.summary) > 200 else article.summary,
                            className="news-summary"
                        ),
                        html.Div([
                            html.Span(f"Source: {article.source}", className="news-source"),
                            html.Span(f"Publié: {article.published.strftime('%d/%m/%Y %H:%M') if article.published else 'N/A'}",
                                    className="news-date"),
                        ], className="news-meta"),
                        html.Div([
                            html.A("Lire l'article", href=article.url, target="_blank",
                                 className="btn btn-sm btn-primary"),
                        ], className="news-actions"),
                    ], className="news-article-card")
                    articles_list.append(article_card)

                if not articles_list:
                    articles_list = [html.Div("Aucune actualité trouvée", className="no-news-message")]

                # Créer les statistiques
                total_articles = len(news_articles)
                sources = set(article.source for article in news_articles if article.source)
                categories = []
                for article in news_articles:
                    if article.categories:
                        categories.extend(article.categories)
                unique_categories = set(categories)

                stats = html.Div([
                    html.H4("📊 Statistiques Actualités"),
                    html.P(f"Total articles: {total_articles}"),
                    html.P(f"Sources: {len(sources)} ({', '.join(list(sources)[:3])}{'...' if len(sources) > 3 else ''})"),
                    html.P(f"Catégories: {len(unique_categories)}"),
                    html.P(f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}"),
                ], className="news-stats")

                return store_data, articles_list, stats

            except Exception as e:
                logger.error(f"Erreur callback news data: {e}")
                return [], [html.Div("Erreur chargement actualités", className="error-message")], html.Div("Erreur statistiques")

        @self.app.callback(
            Output("news-search-results", "children"),
            [Input("news-search-input", "value")],
            prevent_initial_call=False,
        )
        def search_news_articles(search_query):
            """Recherche d'actualités par requête"""
            try:
                if not search_query or len(search_query) < 3:
                    return html.Div("Entrez au moins 3 caractères pour rechercher")

                # Utiliser le service pour rechercher
                results = news_service.search_news(search_query, limit=20)

                if not results:
                    return html.Div("Aucune actualité trouvée pour cette recherche")

                # Créer la liste des résultats
                result_items = []
                for article in results[:10]:  # Limiter à 10 résultats affichés
                    item = html.Div([
                        html.H6(article.title, className="search-result-title"),
                        html.P(
                            article.summary[:100] + "..." if article.summary and len(article.summary) > 100 else article.summary,
                            className="search-result-summary"
                        ),
                        html.Div([
                            html.Span(f"Source: {article.source}", className="search-result-source"),
                            html.A("Lire", href=article.url, target="_blank",
                                 className="btn btn-xs btn-outline-primary ms-2"),
                        ], className="search-result-meta"),
                    ], className="search-result-item")
                    result_items.append(item)

                return html.Div(result_items, className="search-results-container")

            except Exception as e:
                logger.error(f"Erreur callback news search: {e}")
                return html.Div("Erreur lors de la recherche")

        @self.app.callback(
            Output("news-filtered-store", "data"),
            [
                Input("news-category-filter", "value"),
                Input("news-source-filter", "value"),
            ],
            [State("news-store", "data")],
            prevent_initial_call=False,
        )
        def filter_news_articles(selected_categories, selected_sources, all_news):
            """Filtre les actualités par catégorie et source"""
            try:
                if not all_news:
                    return []

                filtered_news = []
                for article_data in all_news:
                    # Filtre par catégories
                    if selected_categories:
                        article_categories = article_data.get("categories", [])
                        if not any(cat in article_categories for cat in selected_categories):
                            continue

                    # Filtre par sources
                    if selected_sources:
                        article_source = article_data.get("source", "")
                        if article_source not in selected_sources:
                            continue

                    filtered_news.append(article_data)

                return filtered_news

            except Exception as e:
                logger.error(f"Erreur callback news filter: {e}")
                return all_news or []

        @self.app.callback(
            Output("news-sentiment-analysis", "children"),
            [Input("news-store", "data")],
            prevent_initial_call=False,
        )
        def analyze_news_sentiment(all_news):
            """Analyse le sentiment des actualités"""
            try:
                if not all_news:
                    return html.Div("Aucune donnée pour l'analyse")

                # Analyse basique du sentiment (à améliorer avec NLP)
                positive_words = ["hausse", "monte", "gagne", "positif", "optimiste", "bull", "rally"]
                negative_words = ["baisse", "descend", "pertes", "négatif", "pessimiste", "bear", "crash"]

                positive_count = 0
                negative_count = 0
                neutral_count = 0

                for article_data in all_news:
                    title = article_data.get("title", "").lower()
                    summary = article_data.get("summary", "").lower()

                    text = title + " " + summary

                    pos_score = sum(1 for word in positive_words if word in text)
                    neg_score = sum(1 for word in negative_words if word in text)

                    if pos_score > neg_score:
                        positive_count += 1
                    elif neg_score > pos_score:
                        negative_count += 1
                    else:
                        neutral_count += 1

                total = len(all_news)
                sentiment_indicator = "Neutre"
                sentiment_color = "secondary"

                if positive_count > negative_count:
                    sentiment_indicator = "Positif"
                    sentiment_color = "success"
                elif negative_count > positive_count:
                    sentiment_indicator = "Négatif"
                    sentiment_color = "danger"

                analysis = html.Div([
                    html.H5("🧠 Analyse de Sentiment"),
                    html.Div([
                        html.Span(f"Articles positifs: {positive_count} ({positive_count/total*100:.1f}%)",
                                className="sentiment-positive"),
                        html.Span(f"Articles négatifs: {negative_count} ({negative_count/total*100:.1f}%)",
                                className="sentiment-negative"),
                        html.Span(f"Articles neutres: {neutral_count} ({neutral_count/total*100:.1f}%)",
                                className="sentiment-neutral"),
                    ], className="sentiment-breakdown"),
                    html.Div([
                        html.Strong("Sentiment général: "),
                        html.Span(sentiment_indicator, className=f"badge bg-{sentiment_color}"),
                    ], className="sentiment-overall"),
                ], className="sentiment-analysis")

                return analysis

            except Exception as e:
                logger.error(f"Erreur callback sentiment analysis: {e}")
                return html.Div("Erreur analyse sentiment")