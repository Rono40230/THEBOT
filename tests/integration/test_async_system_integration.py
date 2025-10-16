"""
Tests d'intégration système async pour THEBOT
Validation de l'interaction entre composants async
"""

import pytest
import pytest_asyncio
import asyncio
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List


class TestAsyncSystemIntegration:
    """Tests d'intégration système pour composants async"""

    @pytest_asyncio.fixture
    async def async_components(self):
        """Fixture pour tous les composants async"""
        from src.thebot.core.data import AsyncDataManager
        from src.thebot.core.economic import AsyncEconomicCalendarRSSParser
        from src.thebot.core.rss import AsyncRSSParser

        components = {
            'data_manager': AsyncDataManager(),
            'economic_parser': AsyncEconomicCalendarRSSParser(),
            'rss_parser': AsyncRSSParser()
        }

        yield components

        # Cleanup
        for component in components.values():
            if hasattr(component, '_session') and component._session:
                await component._session.close()

    @pytest.mark.asyncio
    async def test_full_async_workflow(self, async_components):
        """Test workflow complet async"""
        data_manager = async_components['data_manager']
        economic_parser = async_components['economic_parser']
        rss_parser = async_components['rss_parser']

        # Mock toutes les sessions
        with patch.object(data_manager, '_ensure_session') as mock_dm_ensure, \
             patch.object(data_manager, '_session') as mock_dm_session, \
             patch.object(economic_parser, '_ensure_session') as mock_ep_ensure, \
             patch.object(economic_parser, '_session') as mock_ep_session, \
             patch.object(rss_parser, '_ensure_session') as mock_rp_ensure, \
             patch.object(rss_parser, '_session') as mock_rp_session:

            # Mock données OHLCV
            mock_ohlcv_data = [
                [1640995200000, "50000.00", "51000.00", "49000.00", "50500.00", "100.0", 
                 1641081599999, "5000000.00", 1000, "50.0", "2500000.00", "0"]
            ]
            mock_dm_session.get.return_value.__aenter__.return_value.status = 200
            mock_dm_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_ohlcv_data)

            # Mock RSS économique
            mock_rss_economic = """<?xml version="1.0"?><rss><channel><item><title>Test Event</title></item></channel></rss>"""
            mock_ep_session.get.return_value.__aenter__.return_value.status = 200
            mock_ep_session.get.return_value.__aenter__.return_value.text = AsyncMock(return_value=mock_rss_economic)

            # Mock RSS news
            mock_rss_news = """<?xml version="1.0"?><rss><channel><item><title>Test News</title></item></channel></rss>"""
            mock_rp_session.get.return_value.__aenter__.return_value.status = 200
            mock_rp_session.get.return_value.__aenter__.return_value.text = AsyncMock(return_value=mock_rss_news)

            # Test workflow complet
            data_result = await data_manager.get_binance_data("BTCUSDT")
            economic_result = await economic_parser.get_economic_events_async("https://feed1.com/rss")
            rss_result = await rss_parser.parse_feed_async("https://feed2.com/rss")

            # Vérifications
            assert data_result is not None
            assert economic_result is not None
            assert rss_result is not None
            assert len(economic_result) >= 0
            assert len(rss_result) >= 0

    @pytest.mark.asyncio
    async def test_async_error_handling_integration(self, async_components):
        """Test gestion d'erreurs intégrée"""
        data_manager = async_components['data_manager']
        
        with patch.object(data_manager, '_ensure_session') as mock_ensure, \
             patch.object(data_manager, '_session') as mock_session:
            
            # Mock erreur réseau
            mock_session.get.side_effect = aiohttp.ClientError("Network error")

            # Test avec erreur
            result = await data_manager.get_binance_data("BTCUSDT")
            
            # Devrait gérer l'erreur gracieusement
            assert result is None
