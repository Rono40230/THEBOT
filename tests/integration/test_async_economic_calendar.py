"""
Tests d'intégration async pour AsyncEconomicCalendarRSSParser
Validation du parsing RSS économique avec aiohttp
"""

import pytest
import pytest_asyncio
import aiohttp
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
from typing import List, Dict, Any


class TestAsyncEconomicCalendarIntegration:
    """Tests d'intégration pour AsyncEconomicCalendarRSSParser"""

    @pytest_asyncio.fixture
    async def async_economic_parser(self):
        """Fixture pour AsyncEconomicCalendarRSSParser"""
        from src.thebot.core.economic import AsyncEconomicCalendarRSSParser
        parser = AsyncEconomicCalendarRSSParser()
        yield parser
        # Cleanup
        if hasattr(parser, '_session') and parser._session:
            await parser._session.close()

    @pytest.fixture
    def mock_rss_feed(self):
        """Mock RSS feed économique"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Economic Calendar</title>
<item>
<title>Federal Reserve Interest Rate Decision</title>
<description>FOMC meeting on interest rates</description>
<pubDate>Wed, 16 Oct 2025 14:00:00 GMT</pubDate>
<category>interest_rate</category>
</item>
</channel>
</rss>"""

    @pytest.mark.asyncio
    async def test_rss_parsing_success(self, async_economic_parser, mock_rss_feed):
        """Test parsing RSS économique réussi"""
        with patch.object(async_economic_parser, '_ensure_session') as mock_ensure_session, \
             patch.object(async_economic_parser, '_session') as mock_session:
            
            # Mock de la réponse HTTP
            mock_session.get.return_value.__aenter__.return_value.status = 200
            mock_session.get.return_value.__aenter__.return_value.text = AsyncMock(return_value=mock_rss_feed)

            # Test de la méthode
            events = await async_economic_parser.get_economic_events_async("https://example.com/economic-feed")
            
            # Vérifications
            assert events is not None
            assert isinstance(events, list)
            assert len(events) > 0
            assert 'title' in events[0]
            assert 'description' in events[0]
            mock_session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_rss_parsing_network_error(self, async_economic_parser):
        """Test parsing RSS avec erreur réseau"""
        with patch.object(async_economic_parser, '_ensure_session') as mock_ensure_session, \
             patch.object(async_economic_parser, '_session') as mock_session:
            
            # Mock erreur réseau
            mock_session.get.side_effect = aiohttp.ClientError("Network error")

            # Test avec erreur
            events = await async_economic_parser.get_economic_events_async("https://example.com/economic-feed")
            
            # Devrait retourner liste vide en cas d'erreur
            assert events == []
