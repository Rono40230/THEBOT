"""
News Service - Gestion des actualités et news
Utilise la base de données SQLAlchemy et les data providers de news
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models.base import get_db_session
from ..models.news import NewsArticle
from ..data_providers.rss_news_manager import rss_news_manager

logger = logging.getLogger(__name__)


class NewsService:
    """
    Service de gestion des actualités et news
    Combine base de données et sources RSS externes
    """

    def __init__(self):
        """Initialise le service de news"""
        self.logger = logging.getLogger(__name__)

    def get_latest_news(self, limit: int = 50, category: str = None) -> List[Dict[str, Any]]:
        """
        Récupère les dernières actualités

        Args:
            limit: Nombre maximum d'articles
            category: Catégorie spécifique (crypto, economic, etc.)

        Returns:
            Liste des articles de news
        """
        try:
            # Essayer d'abord depuis la base de données
            cached_news = self._get_cached_news(limit, category)
            if cached_news:
                return cached_news

            # Sinon récupérer depuis les sources externes
            fresh_news = rss_news_manager.get_latest_news(limit, category)
            if fresh_news:
                # Mettre en cache
                self._cache_news_articles(fresh_news)
                return fresh_news

            return []

        except Exception as e:
            self.logger.error(f"Erreur récupération news: {e}")
            return []

    def get_news_by_symbol(self, symbol: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Récupère les news liées à un symbole spécifique

        Args:
            symbol: Symbole de l'actif
            limit: Nombre maximum d'articles

        Returns:
            Liste des articles liés au symbole
        """
        try:
            with get_db_session() as session:
                # Recherche dans le titre et le contenu
                articles = session.query(NewsArticle).filter(
                    (NewsArticle.title.contains(symbol)) |
                    (NewsArticle.content.contains(symbol))
                ).order_by(NewsArticle.published_at.desc()).limit(limit).all()

                return [{
                    'id': article.id,
                    'title': article.title,
                    'content': article.content,
                    'url': article.url,
                    'source': article.source,
                    'published_at': article.published_at,
                    'category': article.category
                } for article in articles]

        except Exception as e:
            self.logger.error(f"Erreur récupération news pour {symbol}: {e}")
            return []

    def search_news(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Recherche dans les actualités

        Args:
            query: Terme de recherche
            limit: Nombre maximum de résultats

        Returns:
            Liste des articles correspondants
        """
        try:
            with get_db_session() as session:
                articles = session.query(NewsArticle).filter(
                    (NewsArticle.title.contains(query)) |
                    (NewsArticle.content.contains(query))
                ).order_by(NewsArticle.published_at.desc()).limit(limit).all()

                return [{
                    'id': article.id,
                    'title': article.title,
                    'content': article.content,
                    'url': article.url,
                    'source': article.source,
                    'published_at': article.published_at,
                    'category': article.category
                } for article in articles]

        except Exception as e:
            self.logger.error(f"Erreur recherche news '{query}': {e}")
            return []

    def get_news_categories(self) -> List[str]:
        """Récupère la liste des catégories disponibles"""
        try:
            with get_db_session() as session:
                categories = session.query(NewsArticle.category).distinct().all()
                return [cat[0] for cat in categories if cat[0]]
        except Exception as e:
            self.logger.error(f"Erreur récupération catégories: {e}")
            return ['crypto', 'economic', 'general']

    def update_news_from_sources(self) -> int:
        """
        Met à jour les news depuis toutes les sources

        Returns:
            Nombre d'articles ajoutés
        """
        try:
            # Récupérer les nouvelles news
            fresh_news = rss_news_manager.get_latest_news(100)

            if not fresh_news:
                return 0

            # Filtrer les articles déjà en base
            new_articles = self._filter_new_articles(fresh_news)

            # Mettre en cache
            self._cache_news_articles(new_articles)

            self.logger.info(f"{len(new_articles)} nouvelles articles ajoutés")
            return len(new_articles)

        except Exception as e:
            self.logger.error(f"Erreur mise à jour news: {e}")
            return 0

    def _get_cached_news(self, limit: int, category: str = None) -> List[Dict[str, Any]]:
        """Récupère les news depuis le cache"""
        try:
            with get_db_session() as session:
                query = session.query(NewsArticle)

                if category:
                    query = query.filter(NewsArticle.category == category)

                # Articles des dernières 24h
                yesterday = datetime.utcnow() - timedelta(days=1)
                query = query.filter(NewsArticle.published_at >= yesterday)

                articles = query.order_by(NewsArticle.published_at.desc()).limit(limit).all()

                return [{
                    'id': article.id,
                    'title': article.title,
                    'content': article.content,
                    'url': article.url,
                    'source': article.source,
                    'published_at': article.published_at,
                    'category': article.category
                } for article in articles]

        except Exception as e:
            self.logger.error(f"Erreur récupération cache news: {e}")
            return []

    def _cache_news_articles(self, articles: List[Dict[str, Any]]) -> None:
        """Met en cache les articles de news"""
        try:
            with get_db_session() as session:
                for article_data in articles:
                    # Vérifier si l'article existe déjà
                    existing = session.query(NewsArticle).filter_by(
                        url=article_data.get('url')
                    ).first()

                    if existing:
                        continue

                    article = NewsArticle(
                        title=article_data.get('title', ''),
                        content=article_data.get('content', ''),
                        url=article_data.get('url', ''),
                        source=article_data.get('source', 'unknown'),
                        published_at=article_data.get('published_at', datetime.utcnow()),
                        category=article_data.get('category', 'general')
                    )
                    session.add(article)

                session.commit()

        except Exception as e:
            self.logger.error(f"Erreur mise en cache articles: {e}")

    def _filter_new_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtre les articles qui ne sont pas déjà en base"""
        try:
            with get_db_session() as session:
                urls = [article.get('url') for article in articles if article.get('url')]
                existing_urls = set()

                if urls:
                    existing = session.query(NewsArticle.url).filter(
                        NewsArticle.url.in_(urls)
                    ).all()
                    existing_urls = {url[0] for url in existing}

                return [article for article in articles
                       if article.get('url') and article.get('url') not in existing_urls]

        except Exception as e:
            self.logger.error(f"Erreur filtrage articles: {e}")
            return articles


# Instance globale du service
news_service = NewsService()
