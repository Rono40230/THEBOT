"""
Tests d'intégration async pour THEBOT
Validation des composants async modernes avec aiohttp
"""

import pytest
import pytest_asyncio
import asyncio
import aiohttp
import pandas as pd
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

from src.thebot.core.data import AsyncDataManager


class TestAsyncDataManagerIntegration:
    """Tests d'intégration pour AsyncDataManager"""

    @pytest_asyncio.fixture
    async def async_data_manager(self):
        """Fixture pour AsyncDataManager"""
        manager = AsyncDataManager()
        yield manager
        # Cleanup
        if hasattr(manager, '_session') and manager._session:
            await manager._session.close()

    @pytest.fixture
    def mock_ohlcv_data(self):
        """Mock données OHLCV Binance (klines)"""
        return [
            [1640995200000, "50000.00", "51000.00", "49000.00", "50500.00", "100.0", 
             1641081599999, "5000000.00", 1000, "50.0", "2500000.00", "0"]
        ]

    @pytest.mark.asyncio
    async def test_binance_api_integration_success(self, async_data_manager, mock_ohlcv_data):
        """Test récupération réussie des données Binance"""
        with patch.object(async_data_manager, '_ensure_session') as mock_ensure_session, \
             patch.object(async_data_manager, '_session') as mock_session:
            
            # Mock de la session
            mock_session.get.return_value.__aenter__.return_value.status = 200
            mock_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_ohlcv_data)
            
            # Test de la méthode
            result = await async_data_manager.get_binance_data("BTCUSDT")
            
            # Vérifications
            assert result is not None
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert 'open' in result.columns
            assert 'high' in result.columns
            assert 'low' in result.columns
            assert 'close' in result.columns
            assert 'volume' in result.columns
            mock_session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_binance_api_integration_timeout(self, async_data_manager):
        """Test intégration API Binance - timeout"""
        with patch.object(async_data_manager, '_ensure_session') as mock_ensure_session, \
             patch.object(async_data_manager, '_session') as mock_session:
            
            # Mock timeout
            mock_session.get.side_effect = asyncio.TimeoutError("Request timeout")

            # Test avec timeout
            result = await async_data_manager.get_binance_data("BTCUSDT")

            # Devrait retourner None en cas d'erreur
            assert result is None

    @pytest.mark.asyncio
    async def test_session_management(self, async_data_manager, mock_ohlcv_data):
        """Test gestion de session aiohttp"""
        with patch.object(async_data_manager, '_ensure_session') as mock_ensure_session, \
             patch.object(async_data_manager, '_session') as mock_session:
            
            # Mock de la réponse HTTP
            mock_session.get.return_value.__aenter__.return_value.status = 200
            mock_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_ohlcv_data)

            # Test de la méthode
            result = await async_data_manager.get_binance_data("BTCUSDT")
            
            # Vérifications
            assert result is not None
            assert hasattr(async_data_manager, '_session')
            mock_session.get.assert_called_once()
