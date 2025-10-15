"""
Tests pour RSS News Manager
Tests complets avec couverture des fonctionnalités principales
"""

import pytest
import threading
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from dash_modules.data_providers.rss_news_manager import RSSNewsManager


class TestRSSNewsManager:
    """Tests pour RSSNewsManager"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.manager = RSSNewsManager(max_workers=2)
        # Mock du parser RSS pour éviter les appels réseau
        self.parser_mock = MagicMock()
        self.manager.parser = self.parser_mock

    def test_initialization(self):
        """Test initialisation du gestionnaire RSS"""
        assert self.manager is not None
        assert hasattr(self.manager, 'name')
        assert self.manager.name == "rss_news"
        assert self.manager.max_workers == 2
        assert isinstance(self.manager.cache, dict)
        assert isinstance(self.manager.cache_ttl, dict)
        assert hasattr(self.manager.lock, 'acquire')  # Vérifier que c'est un lock

    def test_initialization_default_workers(self):
        """Test initialisation avec nombre de workers par défaut"""
        manager = RSSNewsManager()
        assert manager.max_workers == 5

    def test_get_news_interface_method_no_symbol(self):
        """Test méthode get_news de l'interface sans symbole"""
        # Mock de la vraie méthode get_news (celle avec categories)
        with patch('dash_modules.data_providers.rss_news_manager.RSSNewsManager.get_news') as mock_main_get_news:
            mock_main_get_news.return_value = [{"title": "Test Article", "url": "http://test.com"}]

            result = self.manager.get_news(symbol=None, limit=10)

            assert len(result) == 1
            assert result[0]["title"] == "Test Article"

    def test_get_news_interface_method_crypto_symbol(self):
        """Test méthode get_news de l'interface avec symbole crypto"""
        with patch('dash_modules.data_providers.rss_news_manager.RSSNewsManager.get_news') as mock_main_get_news:
            mock_main_get_news.return_value = [{"title": "BTC News", "url": "http://test.com"}]

            result = self.manager.get_news(symbol="BTC", limit=5)

            assert len(result) == 1

    def test_get_news_interface_method_non_crypto_symbol(self):
        """Test méthode get_news de l'interface avec symbole non-crypto"""
        with patch('dash_modules.data_providers.rss_news_manager.RSSNewsManager.get_news') as mock_main_get_news:
            mock_main_get_news.return_value = [{"title": "Business News", "url": "http://test.com"}]

            result = self.manager.get_news(symbol="AAPL", limit=5)

            assert len(result) == 1

    def test_search_news_basic(self):
        """Test recherche d'actualités basique"""
        # Mock de get_news pour retourner des articles de test
        mock_articles = [
            {"title": "Bitcoin price surges", "description": "BTC reaches new highs"},
            {"title": "Apple announces new product", "description": "AAPL stock rises"},
            {"title": "Tesla earnings report", "description": "TSLA beats expectations"}
        ]

        with patch.object(self.manager, 'get_news') as mock_get_news:
            mock_get_news.return_value = mock_articles

            # Recherche pour "bitcoin"
            result = self.manager.search_news("bitcoin", limit=10)

            assert len(result) == 1
            assert "Bitcoin" in result[0]["title"]

    def test_search_news_case_insensitive(self):
        """Test recherche d'actualités insensible à la casse"""
        mock_articles = [
            {"title": "BITCOIN NEWS", "description": "btc update"},
            {"title": "apple news", "description": "AAPL"}
        ]

        with patch.object(self.manager, 'get_news') as mock_get_news:
            mock_get_news.return_value = mock_articles

            result = self.manager.search_news("bitcoin", limit=10)

            assert len(result) == 1
            assert result[0]["title"] == "BITCOIN NEWS"

    def test_search_news_limit(self):
        """Test limite de résultats dans la recherche"""
        mock_articles = [
            {"title": "Bitcoin news 1", "description": "BTC"},
            {"title": "Bitcoin news 2", "description": "BTC"},
            {"title": "Bitcoin news 3", "description": "BTC"}
        ]

        with patch.object(self.manager, 'get_news') as mock_get_news:
            mock_get_news.return_value = mock_articles

            result = self.manager.search_news("bitcoin", limit=2)

            assert len(result) == 2

    def test_get_news_main_method_no_sources(self):
        """Test méthode principale get_news sans sources disponibles"""
        with patch.object(self.manager, '_determine_target_sources') as mock_determine:
            mock_determine.return_value = []

            result = self.manager.get_news(categories=["crypto"], limit=10)

            assert result == []
            mock_determine.assert_called_once_with(["crypto"], None)

    def test_get_news_main_method_with_sources(self):
        """Test méthode principale get_news avec sources"""
        mock_sources = [
            {"name": "Test Source", "url": "http://test.com/rss", "category": "crypto"}
        ]
        mock_articles = [{"title": "Test Article", "url": "http://test.com/article"}]

        with patch.object(self.manager, '_determine_target_sources') as mock_determine, \
             patch.object(self.manager, '_fetch_source_articles') as mock_fetch, \
             patch.object(self.manager, '_deduplicate_articles') as mock_dedup:

            mock_determine.return_value = mock_sources
            mock_fetch.return_value = mock_articles
            mock_dedup.return_value = mock_articles

            result = self.manager.get_news(categories=["crypto"], limit=5)

            assert len(result) == 1
            assert result[0]["title"] == "Test Article"
            mock_fetch.assert_called_once_with(mock_sources[0], True)

    def test_determine_target_sources_specific_sources(self):
        """Test détermination des sources avec sources spécifiques"""
        mock_sources = [
            {"name": "Source1", "active": True},
            {"name": "Source2", "active": True},
            {"name": "Source3", "active": False}
        ]

        with patch('dash_modules.data_providers.rss_sources_config.rss_sources_config.get_all_sources') as mock_get_all:
            mock_get_all.return_value = {"crypto": mock_sources}

            result = self.manager._determine_target_sources(None, ["Source1", "Source3"])

            assert len(result) == 1
            assert result[0]["name"] == "Source1"

    def test_determine_target_sources_by_categories(self):
        """Test détermination des sources par catégories"""
        mock_sources = [
            {"name": "Crypto Source", "category": "crypto", "active": True}
        ]

        with patch('dash_modules.data_providers.rss_sources_config.rss_sources_config.get_active_sources') as mock_get_active:
            mock_get_active.return_value = mock_sources

            result = self.manager._determine_target_sources(["crypto"], None)

            assert len(result) == 1
            assert result[0]["category"] == "crypto"

    def test_determine_target_sources_all_active(self):
        """Test détermination de toutes les sources actives"""
        mock_sources = [
            {"name": "Source1", "active": True},
            {"name": "Source2", "active": True}
        ]

        with patch('dash_modules.data_providers.rss_sources_config.rss_sources_config.get_active_sources') as mock_get_active:
            mock_get_active.return_value = mock_sources

            result = self.manager._determine_target_sources(None, None)

            assert len(result) == 2

    def test_fetch_source_articles_with_cache(self):
        """Test récupération d'articles avec cache"""
        source = {"name": "Test Source", "url": "http://test.com/rss", "max_entries": 10}
        cached_articles = [{"title": "Cached Article"}]

        with patch.object(self.manager, '_get_from_cache') as mock_cache:
            mock_cache.return_value = cached_articles

            result = self.manager._fetch_source_articles(source, use_cache=True)

            assert result == cached_articles
            mock_cache.assert_called_once_with("http://test.com/rss")

    def test_fetch_source_articles_without_cache(self):
        """Test récupération d'articles sans cache"""
        source = {"name": "Test Source", "url": "http://test.com/rss", "max_entries": 10, "category": "crypto"}
        parsed_articles = [{"title": "Parsed Article", "url": "http://test.com/article"}]

        with patch.object(self.manager, '_get_from_cache') as mock_cache, \
             patch.object(self.manager.parser, 'parse_feed') as mock_parse, \
             patch.object(self.manager, '_put_in_cache') as mock_put_cache:

            mock_cache.return_value = None
            mock_parse.return_value = parsed_articles

            result = self.manager._fetch_source_articles(source, use_cache=True)

            assert len(result) == 1
            assert result[0]["title"] == "Parsed Article"
            assert result[0]["rss_source_name"] == "Test Source"
            mock_parse.assert_called_once_with("http://test.com/rss", 10)
            mock_put_cache.assert_called_once()

    def test_fetch_source_articles_parse_error(self):
        """Test récupération d'articles avec erreur de parsing"""
        source = {"name": "Test Source", "url": "http://test.com/rss"}

        with patch.object(self.manager, '_get_from_cache') as mock_cache, \
             patch.object(self.manager.parser, 'parse_feed') as mock_parse:

            mock_cache.return_value = None
            mock_parse.side_effect = Exception("Parse error")

            result = self.manager._fetch_source_articles(source, use_cache=True)

            assert result == []

    def test_get_from_cache_valid(self):
        """Test récupération du cache valide"""
        test_key = "test_key"
        test_data = [{"title": "Test"}]
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)

        self.manager.cache[test_key] = test_data
        self.manager.cache_ttl[test_key] = future_time

        result = self.manager._get_from_cache(test_key)

        assert result == test_data

    def test_get_from_cache_expired(self):
        """Test récupération du cache expiré"""
        test_key = "test_key"
        test_data = [{"title": "Test"}]
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)

        self.manager.cache[test_key] = test_data
        self.manager.cache_ttl[test_key] = past_time

        result = self.manager._get_from_cache(test_key)

        assert result is None
        assert test_key not in self.manager.cache
        assert test_key not in self.manager.cache_ttl

    def test_get_from_cache_missing(self):
        """Test récupération du cache manquant"""
        result = self.manager._get_from_cache("missing_key")
        assert result is None

    def test_put_in_cache(self):
        """Test mise en cache"""
        test_key = "test_key"
        test_data = [{"title": "Test"}]

        self.manager._put_in_cache(test_key, test_data, 300)

        assert test_key in self.manager.cache
        assert test_key in self.manager.cache_ttl
        assert self.manager.cache[test_key] == test_data

    def test_put_in_cache_cleanup(self):
        """Test mise en cache avec nettoyage automatique"""
        # Remplir le cache au maximum
        self.manager.max_cache_entries = 2

        self.manager._put_in_cache("key1", [{"title": "Test1"}], 300)
        self.manager._put_in_cache("key2", [{"title": "Test2"}], 300)

        # Ajouter une troisième entrée devrait déclencher le nettoyage
        with patch.object(self.manager, '_cleanup_cache') as mock_cleanup:
            self.manager._put_in_cache("key3", [{"title": "Test3"}], 300)
            mock_cleanup.assert_called_once()

    def test_cleanup_cache(self):
        """Test nettoyage du cache"""
        # Ajouter des entrées avec TTL expirées et valides
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)

        self.manager.cache = {"expired": "data1", "valid": "data2"}
        self.manager.cache_ttl = {"expired": past_time, "valid": future_time}

        self.manager._cleanup_cache()

        assert "expired" not in self.manager.cache
        assert "expired" not in self.manager.cache_ttl
        assert "valid" in self.manager.cache
        assert "valid" in self.manager.cache_ttl

    def test_deduplicate_articles_unique(self):
        """Test déduplication d'articles uniques"""
        articles = [
            {"title": "Article 1", "url": "http://test1.com"},
            {"title": "Article 2", "url": "http://test2.com"}
        ]

        result = self.manager._deduplicate_articles(articles)

        assert len(result) == 2

    def test_deduplicate_articles_duplicate_url(self):
        """Test déduplication d'articles avec URL dupliquée"""
        articles = [
            {"title": "Article 1", "url": "http://test.com"},
            {"title": "Article 2", "url": "http://test.com"}  # Même URL
        ]

        result = self.manager._deduplicate_articles(articles)

        assert len(result) == 1
        assert result[0]["title"] == "Article 1"

    def test_deduplicate_articles_similar_title(self):
        """Test déduplication d'articles avec titre similaire"""
        articles = [
            {"title": "Bitcoin price update news", "url": "http://test1.com"},
            {"title": "News update Bitcoin price", "url": "http://test2.com"}  # Titre similaire
        ]

        result = self.manager._deduplicate_articles(articles)

        assert len(result) == 1

    def test_clear_cache(self):
        """Test vidage du cache"""
        self.manager.cache = {"key1": "data1", "key2": "data2"}
        self.manager.cache_ttl = {"key1": datetime.now(timezone.utc), "key2": datetime.now(timezone.utc)}

        self.manager.clear_cache()

        assert len(self.manager.cache) == 0
        assert len(self.manager.cache_ttl) == 0

    def test_get_cache_stats(self):
        """Test statistiques du cache"""
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)

        self.manager.cache = {"valid": "data1", "expired": "data2"}
        self.manager.cache_ttl = {"valid": future_time, "expired": past_time}

        stats = self.manager.get_cache_stats()

        assert stats["total_entries"] == 2
        assert stats["valid_entries"] == 1
        assert stats["expired_entries"] == 1

    def test_test_sources_all_categories(self):
        """Test test des sources pour toutes les catégories"""
        mock_sources = [
            {"name": "Source1", "url": "http://test1.com", "category": "crypto"},
            {"name": "Source2", "url": "http://test2.com", "category": "business"}
        ]

        with patch('dash_modules.data_providers.rss_sources_config.rss_sources_config.get_active_sources') as mock_get_active, \
             patch.object(self.manager.parser, 'validate_feed') as mock_validate:

            mock_get_active.return_value = mock_sources
            mock_validate.return_value = True

            result = self.manager.test_sources()

            assert result["total_sources"] == 2
            assert result["successful"] == 2
            assert result["failed"] == 0
            assert len(result["details"]) == 2

    def test_test_sources_specific_categories(self):
        """Test test des sources pour catégories spécifiques"""
        mock_sources = [
            {"name": "Crypto Source", "url": "http://crypto.com", "category": "crypto"}
        ]

        with patch('dash_modules.data_providers.rss_sources_config.rss_sources_config.get_active_sources') as mock_get_active, \
             patch.object(self.manager.parser, 'validate_feed') as mock_validate:

            mock_get_active.return_value = mock_sources
            mock_validate.return_value = False

            result = self.manager.test_sources(categories=["crypto"])

            assert result["total_sources"] == 1
            assert result["successful"] == 0
            assert result["failed"] == 1

    def test_get_symbol_specific_news_crypto(self):
        """Test récupération d'actualités spécifiques à un symbole crypto"""
        mock_articles = [
            {"title": "Bitcoin surges to new highs", "summary": "BTC price update"},
            {"title": "Apple earnings report", "summary": "AAPL financial results"}
        ]

        with patch.object(self.manager, 'get_news') as mock_get_news:
            mock_get_news.return_value = mock_articles

            result = self.manager.get_symbol_specific_news("BTC", limit=5)

            assert len(result) == 1
            assert "Bitcoin" in result[0]["title"]
            mock_get_news.assert_called_once_with(categories=["crypto"], limit=15)  # limit * 3

    def test_get_symbol_specific_news_forex(self):
        """Test récupération d'actualités spécifiques à un symbole forex"""
        mock_articles = [
            {"title": "EUR/USD exchange rate", "summary": "Forex update"},
            {"title": "Stock market news", "summary": "Market update"}
        ]

        with patch.object(self.manager, 'get_news') as mock_get_news:
            mock_get_news.return_value = mock_articles

            result = self.manager.get_symbol_specific_news("EURUSD", limit=5)

            # Le filtre devrait trouver au moins l'article EUR/USD
            assert len(result) >= 1
            assert any("EUR/USD" in article["title"] for article in result)

    def test_get_symbol_specific_news_error(self):
        """Test gestion d'erreur dans get_symbol_specific_news"""
        with patch.object(self.manager, 'get_news') as mock_get_news:
            mock_get_news.side_effect = Exception("Test error")

            result = self.manager.get_symbol_specific_news("BTC", limit=5)

            assert result == []

    def test_interface_compliance(self):
        """Test conformité à l'interface NewsProviderInterface"""
        from dash_modules.data_providers.provider_interfaces import NewsProviderInterface

        # Vérifier que RSSNewsManager hérite de NewsProviderInterface
        assert isinstance(self.manager, NewsProviderInterface)

        # Vérifier que les méthodes requises existent
        assert hasattr(self.manager, 'get_news')
        assert hasattr(self.manager, 'search_news')

        # Vérifier les signatures des méthodes
        import inspect
        # La méthode get_news de l'interface (avec symbol)
        interface_get_news = getattr(NewsProviderInterface, 'get_news', None)
        search_news_sig = inspect.signature(self.manager.search_news)

        # search_news devrait accepter query et limit
        assert 'query' in search_news_sig.parameters
        assert 'limit' in search_news_sig.parameters

        # Vérifier que get_news (interface) existe et fonctionne
        assert callable(self.manager.get_news)