from src.thebot.core.logger import logger
"""
Tests unitaires pour OptimizedRSSPaginator - Phase 4
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from dash_modules.core.rss_paginator import OptimizedRSSPaginator


class TestOptimizedRSSPaginator:
    """Tests pour le paginateur RSS optimisé"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.paginator = OptimizedRSSPaginator(cache_ttl=60, default_page_size=10)

    def test_init(self):
        """Test initialisation du paginateur"""
        assert self.paginator.cache_ttl == 60
        assert self.paginator.default_page_size == 10
        assert self.paginator._feed_cache == {}
        assert self.paginator._stats["feeds_fetched"] == 0
        assert self.paginator._stats["cache_hits"] == 0
        assert self.paginator._stats["cache_misses"] == 0
        assert self.paginator._stats["parse_errors"] == 0
        assert self.paginator._session is not None

    def test_get_paginated_feed_invalid_page(self):
        """Test pagination avec numéro de page invalide"""
        with pytest.raises(ValueError, match="Numéro de page invalide"):
            self.paginator.get_paginated_feed("http://example.com/rss", page=0)

    def test_get_paginated_feed_invalid_page_size(self):
        """Test pagination avec taille de page invalide"""
        with pytest.raises(ValueError, match="Taille de page invalide"):
            self.paginator.get_paginated_feed("http://example.com/rss", page_size=0)

        with pytest.raises(ValueError, match="Taille de page invalide"):
            self.paginator.get_paginated_feed("http://example.com/rss", page_size=150)

    @patch('dash_modules.core.rss_paginator.feedparser.parse')
    def test_get_paginated_feed_success(self, mock_feedparser):
        """Test récupération réussie d'un flux paginé"""
        # Mock de la session
        mock_session = Mock()
        self.paginator._session = mock_session

        # Mock de la réponse HTTP
        mock_response = Mock()
        mock_response.content = b"<rss><channel><item><title>Test Item</title></item></channel></rss>"
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Mock feedparser
        mock_feed = Mock()
        mock_entry = Mock()
        mock_entry.title = "Test Item"
        mock_entry.link = "http://example.com"
        mock_entry.description = "Test description"
        mock_entry.id = "test-id"
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        result = self.paginator.get_paginated_feed("http://example.com/rss", page=1, page_size=5)

        assert len(result["items"]) == 1
        assert result["total_count"] == 1
        assert result["page"] == 1
        assert result["page_size"] == 5
        assert result["has_next"] is False
        assert result["has_previous"] is False
        assert "load_time" in result

    @patch('dash_modules.core.rss_paginator.feedparser.parse')
    def test_get_feed_items_cache_hit(self, mock_feedparser):
        """Test récupération depuis le cache"""
        # Pré-remplir le cache
        cache_key = "1ade8204c10992ac38d25354a392ec9f"  # MD5 de "http://example.com/rss"
        self.paginator._feed_cache[cache_key] = {
            'items': [{"title": "Cached Item"}],
            'timestamp': time.time()
        }

        # Appeler la méthode privée
        items = self.paginator._get_feed_items("http://example.com/rss")

        # Vérifier que le cache est utilisé
        assert len(items) == 1
        assert items[0]["title"] == "Cached Item"
        assert self.paginator._stats["cache_hits"] == 1
        assert self.paginator._stats["feeds_fetched"] == 0


    @patch('dash_modules.core.rss_paginator.feedparser.parse')
    def test_get_feed_items_cache_miss(self, mock_feedparser):
        """Test récupération avec cache miss"""
        # Mock de la session
        mock_session = Mock()
        self.paginator._session = mock_session

        # Mock de la réponse
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response

        # Mock feedparser
        mock_feed = Mock()
        mock_entry = Mock()
        mock_entry.title = "Fresh Item"
        mock_entry.link = "http://example.com"
        mock_entry.description = "Fresh description"
        mock_entry.id = "fresh-id"
        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        items = self.paginator._get_feed_items("http://example.com/rss")

        assert len(items) == 1
        assert items[0]["title"] == "Fresh Item"
        assert self.paginator._stats["cache_misses"] == 1
        assert self.paginator._stats["feeds_fetched"] == 1

    @patch('dash_modules.core.rss_paginator.feedparser.parse')
    @patch('dash_modules.core.rss_paginator.logger')
    def test_get_feed_items_parse_error(self, mock_logger, mock_feedparser):
        """Test gestion d'erreur de parsing"""
        # Mock de la session qui lève une exception
        mock_session = Mock()
        self.paginator._session = mock_session
        mock_session.get.side_effect = Exception("Network error")

        items = self.paginator._get_feed_items("http://example.com/rss")

        assert items == []
        assert self.paginator._stats["parse_errors"] == 1
        mock_logger.error.assert_called()

    def test_get_stats(self):
        """Test récupération des statistiques"""
        # Modifier les stats
        self.paginator._stats["feeds_fetched"] = 5
        self.paginator._stats["cache_hits"] = 3

        stats = self.paginator.get_stats()

        assert stats["feeds_fetched"] == 5
        assert stats["cache_hits"] == 3
        # Vérifier que c'est une copie
        assert stats is not self.paginator._stats
