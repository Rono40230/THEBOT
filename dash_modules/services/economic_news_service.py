from src.thebot.core.logger import logger
"""
Economic News Service - Logique métier pour les news économiques
Extrait la logique métier de economic_news_module.py pour respecter MVC
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import re

from .news_service import NewsService

logger = logging.getLogger(__name__)


class EconomicNewsService:
    """
    Service de logique métier pour les news économiques
    Gère le filtrage, l'analyse de sentiment et les calculs économiques
    """

    def __init__(self):
        self.news_service = NewsService()
        self.economic_keywords = [
            "économie", "économique", "finance", "financier", "banque", "bourse",
            "marché", "action", "obligation", "taux", "inflation", "croissance",
            "pib", "fed", "bce", "banque centrale", "politique monétaire",
            "commerce", "industrie", "emploi", "chômage", "consommation",
            "economy", "economic", "finance", "financial", "banking",
            "stock market", "market", "stock", "bond", "rate", "inflation",
            "growth", "gdp", "federal reserve", "central bank", "monetary policy",
            "trade", "industry", "employment", "unemployment", "consumption",
            "earnings", "revenue", "profit", "dividend", "treasury"
        ]

    def get_filtered_economic_news(
        self,
        country_filter: str = "all",
        sector_filter: str = "all", 
        impact_filter: str = "all",
        sentiment_filter: str = "all",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Récupère et filtre les news économiques selon les critères

        Args:
            country_filter: Filtre par pays
            sector_filter: Filtre par secteur
            impact_filter: Filtre par impact
            sentiment_filter: Filtre par sentiment
            limit: Nombre maximum d'articles

        Returns:
            Liste des articles filtrés
        """
        try:
            # Récupérer les news économiques de base
            raw_news = self.news_service.get_latest_news(limit * 2, "economic")

            # Filtrer et enrichir
            filtered_news = []
            for article in raw_news:
                if self._matches_filters(article, country_filter, sector_filter, impact_filter, sentiment_filter):
                    # Enrichir avec analyse économique
                    enriched_article = self._enrich_economic_article(article)
                    filtered_news.append(enriched_article)

                if len(filtered_news) >= limit:
                    break

            return filtered_news

        except Exception as e:
            logger.error(f"Erreur lors du filtrage des news économiques: {e}")
            return []

    def get_economic_indicators(self) -> Dict[str, Any]:
        """Récupère les indicateurs économiques actuels"""
        # Valeurs par défaut (pourraient être récupérées depuis une API économique)
        return {
            "gdp": "2.1%",
            "inflation": "3.7%",
            "unemployment": "3.8%",
            "fed_rate": "5.25%",
            "last_updated": datetime.now().isoformat()
        }
