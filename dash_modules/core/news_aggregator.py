"""
News Aggregator - Agrégateur multi-sources pour THEBOT
Combine RSS, APIs existantes et fournit une interface unifiée
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..data_providers.rss_news_manager import rss_news_manager

logger = logging.getLogger(__name__)


class NewsAggregator:
    """Agrégateur intelligent de nouvelles multi-sources"""

    def __init__(self):
        """Initialise l'agrégateur"""
        self.rss_manager = rss_news_manager

        # Mapping catégories THEBOT → RSS
        self.category_mapping = {
            "economic": ["economic", "general"],
            "crypto": ["crypto"],
            "market": ["market", "general"],
            "forex": ["forex"],
            "general": ["general"],
        }

        logger.info("🔄 News Aggregator initialized")

    def get_aggregated_news(
        self,
        categories: List[str] = None,
        sources: List[str] = None,
        limit: int = 50,
        include_rss: bool = True,
        include_apis: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Agrège les nouvelles de toutes les sources disponibles

        Args:
            categories: Catégories à inclure
            sources: Sources spécifiques à inclure
            limit: Nombre maximum d'articles
            include_rss: Inclure les sources RSS
            include_apis: Inclure les APIs existantes

        Returns:
            Articles agrégés et triés
        """
        try:
            logger.info(
                f"📰 Aggregating news - Categories: {categories}, Limit: {limit}"
            )

            all_articles = []

            # Récupération parallèle des sources
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []

                # Source RSS
                if include_rss:
                    rss_categories = (
                        self._map_categories_to_rss(categories) if categories else None
                    )
                    future_rss = executor.submit(
                        self._get_rss_news, rss_categories, sources, limit
                    )
                    futures.append(("rss", future_rss))

                # Sources API existantes (transitoire)
                if include_apis:
                    future_apis = executor.submit(self._get_api_news, categories, limit)
                    futures.append(("api", future_apis))

                # Collecter les résultats
                for source_type, future in futures:
                    try:
                        articles = future.result(timeout=30)
                        if articles:
                            all_articles.extend(articles)
                            logger.debug(
                                f"✅ Got {len(articles)} articles from {source_type}"
                            )
                    except Exception as e:
                        logger.error(f"❌ Error getting {source_type} news: {e}")

            # Normalisation et tri
            normalized_articles = self._normalize_articles(all_articles)
            sorted_articles = self._sort_articles(normalized_articles)

            # Déduplication et limitation
            unique_articles = self._deduplicate_articles(sorted_articles)
            result = unique_articles[:limit]

            logger.info(
                f"✅ Aggregated {len(result)} unique articles from {len(all_articles)} total"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Error aggregating news: {e}")
            return []

    def _map_categories_to_rss(self, categories: List[str]) -> List[str]:
        """Mappe les catégories THEBOT vers les catégories RSS"""
        rss_categories = []
        for category in categories:
            mapped = self.category_mapping.get(category, [category])
            rss_categories.extend(mapped)
        return list(set(rss_categories))  # Dédupliquer

    def _get_rss_news(
        self, categories: List[str], sources: List[str], limit: int
    ) -> List[Dict[str, Any]]:
        """Récupère les nouvelles RSS"""
        try:
            return self.rss_manager.get_news(
                categories=categories,
                sources=sources,
                limit=limit * 2,  # Plus d'articles pour la déduplication
                use_cache=True,
            )
        except Exception as e:
            logger.error(f"❌ Error getting RSS news: {e}")
            return []

    def _get_api_news(self, categories: List[str], limit: int) -> List[Dict[str, Any]]:
        """
        Récupère les nouvelles des APIs existantes (mode transitoire)
        Cette fonction sera progressivement supprimée lors de la migration
        """
        try:
            # Import dynamique pour éviter les erreurs si APIs supprimées
            api_articles = []

            # Importer les APIs encore disponibles
            try:
                from ..data_providers.yahoo_finance_api import yahoo_finance_api

                yahoo_news = yahoo_finance_api.get_economic_news(limit=10)
                if yahoo_news:
                    # Normaliser au format RSS
                    for article in yahoo_news:
                        article.update(
                            {
                                "provider": "api",
                                "rss_source_name": "Yahoo Finance API",
                                "rss_category": "market",
                            }
                        )
                    api_articles.extend(yahoo_news)
                    logger.debug(
                        f"✅ Got {len(yahoo_news)} articles from Yahoo Finance API"
                    )
            except Exception as e:
                logger.debug(f"⚠️ Yahoo Finance API not available: {e}")

            # Twelve Data (si disponible)
            try:
                from ..data_providers.twelve_data_api import twelve_data_api

                td_news = twelve_data_api.get_financial_news(limit=5)
                if td_news:
                    for article in td_news:
                        article.update(
                            {
                                "provider": "api",
                                "rss_source_name": "Twelve Data API",
                                "rss_category": "market",
                            }
                        )
                    api_articles.extend(td_news)
                    logger.debug(f"✅ Got {len(td_news)} articles from Twelve Data API")
            except Exception as e:
                logger.debug(f"⚠️ Twelve Data API not available: {e}")

            return api_articles

        except Exception as e:
            logger.error(f"❌ Error getting API news: {e}")
            return []

    def _normalize_articles(
        self, articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Normalise tous les articles au même format"""
        normalized = []

        for article in articles:
            try:
                # Format de base requis
                normalized_article = {
                    "title": article.get("title", "").strip(),
                    "url": article.get("url", "").strip(),
                    "summary": article.get("summary", "").strip(),
                    "published_date": article.get(
                        "published_date", datetime.now(timezone.utc).isoformat()
                    ),
                    "source": article.get("source", "Unknown"),
                    "provider": article.get("provider", "unknown"),
                    "category": article.get("category", "general"),
                    "timestamp": article.get(
                        "timestamp", datetime.now(timezone.utc).isoformat()
                    ),
                }

                # Champs optionnels préservés
                optional_fields = [
                    "tags",
                    "language",
                    "feed_title",
                    "rss_source_name",
                    "rss_category",
                    "rss_description",
                ]
                for field in optional_fields:
                    if field in article:
                        normalized_article[field] = article[field]

                # Validation minimale
                if normalized_article["title"] and normalized_article["url"]:
                    normalized.append(normalized_article)

            except Exception as e:
                logger.debug(f"⚠️ Error normalizing article: {e}")
                continue

        return normalized

    def _sort_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Trie les articles par date de publication (plus récent en premier)"""
        try:
            return sorted(
                articles, key=lambda x: x.get("published_date", ""), reverse=True
            )
        except Exception as e:
            logger.error(f"❌ Error sorting articles: {e}")
            return articles

    def _deduplicate_articles(
        self, articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Déduplique les articles par URL et titre"""
        seen_urls = set()
        seen_titles = set()
        unique_articles = []

        for article in articles:
            url = article.get("url", "").strip().lower()
            title = article.get("title", "").strip().lower()

            # Clé de déduplication basée sur URL
            if url and url in seen_urls:
                continue

            # Clé de déduplication basée sur titre (mots significatifs)
            title_words = [w for w in title.split() if len(w) > 3]
            title_key = " ".join(sorted(title_words[:6]))  # 6 mots significatifs

            if title_key and title_key in seen_titles:
                continue

            if url:
                seen_urls.add(url)
            if title_key:
                seen_titles.add(title_key)

            unique_articles.append(article)

        logger.debug(
            f"🔄 Deduplicated {len(articles)} → {len(unique_articles)} articles"
        )
        return unique_articles

    def get_source_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques des sources"""
        try:
            # Stats RSS
            rss_stats = self.rss_manager.get_cache_stats()

            # Stats générales
            from ..data_providers.rss_sources_config import rss_sources_config

            stats = {
                "rss_sources": {
                    "total_configured": rss_sources_config.get_source_count(),
                    "active_sources": rss_sources_config.get_source_count(
                        active_only=True
                    ),
                    "categories": rss_sources_config.get_categories(),
                    "cache_stats": rss_stats,
                },
                "api_sources": {
                    "status": "transitioning",  # APIs en cours de migration
                    "available": self._get_available_apis(),
                },
                "aggregator": {
                    "category_mapping": self.category_mapping,
                    "last_update": datetime.now(timezone.utc).isoformat(),
                },
            }

            return stats

        except Exception as e:
            logger.error(f"❌ Error getting source statistics: {e}")
            return {}

    def _get_available_apis(self) -> List[str]:
        """Retourne la liste des APIs encore disponibles"""
        available = []

        # Test Yahoo Finance
        try:
            from ..data_providers.yahoo_finance_api import yahoo_finance_api

            available.append("yahoo_finance")
        except:
            pass

        # Test Twelve Data
        try:
            from ..data_providers.twelve_data_api import twelve_data_api

            available.append("twelve_data")
        except:
            pass

        # Test Binance
        try:
            from ..data_providers.binance_api import binance_api

            available.append("binance")
        except:
            pass

        return available

    def test_all_sources(self) -> Dict[str, Any]:
        """Teste toutes les sources disponibles"""
        logger.info("🧪 Testing all news sources")

        results = {"rss_test": {}, "api_test": {}, "summary": {}}

        try:
            # Test RSS
            results["rss_test"] = self.rss_manager.test_sources()

            # Test APIs (transitoire)
            api_results = {"successful": 0, "failed": 0, "details": []}

            for api_name in self._get_available_apis():
                try:
                    # Test simple de connectivité
                    if api_name == "yahoo_finance":
                        from ..data_providers.yahoo_finance_api import yahoo_finance_api

                        test_result = yahoo_finance_api.get_economic_news(limit=1)
                        status = "OK" if test_result else "FAILED"
                    else:
                        status = "AVAILABLE"

                    if status == "OK":
                        api_results["successful"] += 1
                    else:
                        api_results["failed"] += 1

                    api_results["details"].append({"name": api_name, "status": status})

                except Exception as e:
                    api_results["failed"] += 1
                    api_results["details"].append(
                        {"name": api_name, "status": "ERROR", "error": str(e)}
                    )

            results["api_test"] = api_results

            # Résumé
            results["summary"] = {
                "total_rss_sources": results["rss_test"].get("total_sources", 0),
                "successful_rss": results["rss_test"].get("successful", 0),
                "total_api_sources": len(self._get_available_apis()),
                "successful_apis": api_results["successful"],
                "overall_health": (
                    "good" if (results["rss_test"].get("successful", 0) > 0) else "poor"
                ),
            }

            logger.info(
                f"✅ Source test completed: RSS {results['summary']['successful_rss']}/{results['summary']['total_rss_sources']}, APIs {results['summary']['successful_apis']}/{results['summary']['total_api_sources']}"
            )

        except Exception as e:
            logger.error(f"❌ Error testing sources: {e}")
            results["error"] = str(e)

        return results


# Instance globale
news_aggregator = NewsAggregator()
