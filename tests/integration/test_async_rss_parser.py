"""
Tests d'intégration async pour AsyncRSSParser
Validation du parsing RSS général avec aiohttp
"""

import pytest
import pytest_asyncio
import aiohttp
from unittest.mock import AsyncMock, patch
from datetime import datetime
from typing import List, Dict, Any


class TestAsyncRSSParserIntegration:
    """Tests d'intégration pour AsyncRSSParser"""

    @pytest_asyncio.fixture
    async def async_rss_parser(self):
        """Fixture pour AsyncRSSParser"""
        from src.thebot.core.rss import AsyncRSSParser
        parser = AsyncRSSParser()
        yield parser
        # Cleanup
        if hasattr(parser, '_session') and parser._session:
            await parser._session.close()

    @pytest.fixture
    def mock_news_rss_feed(self):
        """Mock RSS feed d'actualités"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Crypto News</title>
<item>
<title>Bitcoin reaches new high</title>
<description>Bitcoin price surges to new all-time high</description>
<pubDate>Wed, 16 Oct 2025 14:00:00 GMT</pubDate>
<category>bitcoin</category>
</item>
</channel>
</rss>"""

    @pytest.mark.asyncio
    async def test_rss_parsing_success(self, async_rss_parser, mock_news_rss_feed):
        """Test parsing RSS réussi"""
        with patch.object(async_rss_parser, '_ensure_session') as mock_ensure_session, \
             patch.object(async_rss_parser, '_session') as mock_session:
            
            # Mock de la réponse HTTP
            mock_session.get.return_value.__aenter__.return_value.status = 200
            mock_session.get.return_value.__aenter__.return_value.text = AsyncMock(return_value=mock_news_rss_feed)

            # Test de la méthode
            items = await async_rss_parser.parse_feed_async("https://crypto-news.com/rss")
            
            # Vérifications
            assert items is not None
            assert isinstance(items, list)
            assert len(items) > 0
            assert 'title' in items[0]
            assert 'description' in items[0]
            mock_session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_rss_parsing_network_error(self, async_rss_parser):
        """Test parsing RSS avec erreur réseau"""
        with patch.object(async_rss_parser, '_ensure_session') as mock_ensure_session, \
             patch.object(async_rss_parser, '_session') as mock_session:
            
            # Mock erreur réseau
            mock_session.get.side_effect = aiohttp.ClientError("Network error")

            # Test avec erreur
            items = await async_rss_parser.parse_feed_async("https://crypto-news.com/rss")
            
            # Devrait retourner liste vide en cas d'erreur
            assert items == []
