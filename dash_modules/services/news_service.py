from src.thebot.core.logger import logger
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
from .service_interfaces import ServiceInterface

logger = logging.getLogger(__name__)


class NewsService(ServiceInterface):
    """
    Service de gestion des actualités et news
    Combine base de données et sources RSS externes
    Implémente ServiceInterface pour la standardisation
    """

    def __init__(self):
        """Initialise le service de news"""
        self.logger = logging.getLogger(__name__)
        self._initialized = False

    @property
    def service_name(self) -> str:
        """Nom du service"""
        return "NewsService"

    @property
    def version(self) -> str:
        """Version du service"""
        return "1.0.0"

    def initialize(self) -> bool:
        """
        Initialise le service et ses dépendances.
        
        Returns:
            bool: True si l'initialisation a réussi
        """
        try:
            # Tester la connexion à la base de données
            with get_db_session() as session:
                session.execute("SELECT 1")

            # Tester les sources RSS
            if not rss_news_manager.is_available():
                self.logger.warning("RSSNewsManager n'est pas disponible")

            self._initialized = True
            self.logger.info("NewsService initialisé avec succès")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation de NewsService: {e}")
            return False

    def shutdown(self) -> bool:
        """
        Arrête proprement le service et libère les ressources.
        
        Returns:
            bool: True si l'arrêt s'est bien passé
        """
        try:
            self._initialized = False
            self.logger.info("NewsService arrêté proprement")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'arrêt de NewsService: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie l'état de santé du service.
        
        Returns:
            Dict avec le statut et les métriques du service
        """
        try:
            with get_db_session() as session:
                # Compter les articles de news
                news_count = session.query(NewsArticle).count()

            rss_status = rss_news_manager.is_available()

            return {
                "status": "healthy" if self._initialized else "unhealthy",
                "service": self.service_name,
                "version": self.version,
                "news_articles_count": news_count,
                "rss_sources_available": rss_status,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": self.service_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_service_info(self) -> Dict[str, Any]:
        """
        Retourne les informations générales sur le service.
        
        Returns:
            Dict avec les informations du service
        """
        return {
            "name": self.service_name,
            "version": self.version,
            "description": "Service de gestion des actualités et news",
            "initialized": self._initialized,
            "features": ["news_aggregation", "rss_feed_processing", "news_caching", "category_filtering"]
        }

    def get_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les dernières actualités.
        
        Args:
            limit: Nombre maximum d'articles à retourner
            
        Returns:
            Liste des articles d'actualité
        """
        try:
            # Récupérer les news depuis la base de données
            with get_db_session() as session:
                articles = session.query(NewsArticle)\
                    .order_by(NewsArticle.published_at.desc())\
                    .limit(limit)\
                    .all()
                
                return [{
                    "id": article.id,
                    "title": article.title,
                    "content": article.content,
                    "url": article.url,
                    "source": article.source,
                    "published_at": article.published_at.isoformat() if article.published_at else None,
                    "category": article.category
                } for article in articles]
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des news: {e}")
            return []
