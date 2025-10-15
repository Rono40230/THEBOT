"""
Tests pour Binance API provider
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, Mock
from dash_modules.data_providers.binance_api import BinanceProvider


class TestBinanceAPI:
    """Tests pour BinanceProvider"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.api = BinanceProvider()

    def test_initialization(self):
        """Test initialisation de l'API"""
        assert self.api is not None
        assert hasattr(self.api, 'name')
        assert self.api.name == "binance"
        assert self.api.base_url == "https://api.binance.com"
        assert isinstance(self.api.popular_symbols, list)

    def test_supported_markets(self):
        """Test marchés supportés"""
        markets = self.api.supported_markets
        assert isinstance(markets, list)
        assert len(markets) > 0
        assert "BTCUSDT" in markets

    def test_rate_limit_info(self):
        """Test informations rate limit"""
        info = self.api.rate_limit_info
        assert isinstance(info, dict)
        assert "requests_per_minute" in info
        assert info["has_free_tier"] is True

    def test_validate_symbol(self):
        """Test validation symbole"""
        assert self.api.validate_symbol('BTCUSDT') is True
        assert self.api.validate_symbol('ETHUSDT') is True
        assert self.api.validate_symbol('INVALID') is False
        assert self.api.validate_symbol('') is False
        assert self.api.validate_symbol(None) is False

    @patch('requests.get')
    def test_make_request_success(self, mock_get):
        """Test requête HTTP réussie"""
        mock_response = Mock()
        mock_response.json.return_value = {"symbol": "BTCUSDT", "price": "50000.00"}
        mock_get.return_value = mock_response

        result = self.api._make_request("api/v3/ticker/price", {"symbol": "BTCUSDT"})

        assert result == {"symbol": "BTCUSDT", "price": "50000.00"}
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_make_request_error(self, mock_get):
        """Test requête HTTP avec erreur"""
        mock_get.side_effect = Exception("Network error")

        result = self.api._make_request("api/v3/ticker/price")

        assert result is None

    @patch('dash_modules.data_providers.binance_api.BinanceProvider._make_request')
    def test_get_price_data_success(self, mock_make_request):
        """Test récupération données de prix réussie"""
        mock_data = [
            [1640995200000, "50000.00", "51000.00", "49000.00", "50500.00", "100.0", 1641081600000, "5000000.00", 100, "50.0", "2500000.00", "0"]
        ]
        mock_make_request.return_value = mock_data

        result = self.api.get_price_data("BTCUSDT", "1d", 100)

        assert isinstance(result, dict)
        assert "symbol" in result
        assert "data" in result
        assert len(result["data"]) == 1

    @patch('dash_modules.data_providers.binance_api.BinanceProvider._make_request')
    def test_get_price_data_error(self, mock_make_request):
        """Test récupération données de prix avec erreur"""
        mock_make_request.return_value = None

        result = self.api.get_price_data("BTCUSDT")

        assert result is None

    @patch('dash_modules.data_providers.binance_api.BinanceProvider._make_request')
    def test_get_current_price_success(self, mock_make_request):
        """Test récupération prix actuel réussi"""
        mock_data = {"symbol": "BTCUSDT", "price": "50000.00"}
        mock_make_request.return_value = mock_data

        result = self.api.get_current_price("BTCUSDT")

        assert result == 50000.00

    @patch('dash_modules.data_providers.binance_api.BinanceProvider._make_request')
    def test_get_current_price_error(self, mock_make_request):
        """Test récupération prix actuel avec erreur"""
        mock_make_request.return_value = None

        result = self.api.get_current_price("BTCUSDT")

        assert result is None

    @patch('dash_modules.data_providers.binance_api.BinanceProvider._make_request')
    def test_get_market_info_success(self, mock_make_request):
        """Test récupération info marché réussie"""
        mock_data = {
            "symbol": "BTCUSDT",
            "priceChange": "1000.00",
            "priceChangePercent": "2.00",
            "weightedAvgPrice": "50000.00",
            "prevClosePrice": "49000.00",
            "lastPrice": "50000.00",
            "bidPrice": "49999.00",
            "askPrice": "50001.00",
            "openPrice": "49000.00",
            "highPrice": "51000.00",
            "lowPrice": "48000.00",
            "volume": "1000.00",
            "quoteVolume": "50000000.00",
            "openTime": 1640995200000,
            "closeTime": 1641081600000,
            "firstId": 1,
            "lastId": 100,
            "count": 100
        }
        mock_make_request.return_value = mock_data

        result = self.api.get_market_info("BTCUSDT")

        assert isinstance(result, dict)
        assert result["symbol"] == "BTCUSDT"
        assert result["current_price"] == 50000.00
        assert result["change_24h"] == 1000.00
        assert result["change_percent_24h"] == 2.00

    @patch('dash_modules.data_providers.binance_api.BinanceProvider._make_request')
    def test_get_market_info_error(self, mock_make_request):
        """Test récupération info marché avec erreur"""
        mock_make_request.return_value = None

        result = self.api.get_market_info("BTCUSDT")

        assert result is None

    def test_is_available(self):
        """Test vérification disponibilité"""
        # Test avec mock pour éviter les appels réseau réels
        with patch.object(self.api, 'get_current_price') as mock_get_price:
            mock_get_price.return_value = 50000.00
            assert self.api.is_available() is True

            mock_get_price.return_value = None
            assert self.api.is_available() is False

    def test_get_status(self):
        """Test récupération statut"""
        status = self.api.get_status()

        assert isinstance(status, dict)
        assert "available" in status
        assert "name" in status
        assert "rate_limit" in status

    @patch('dash_modules.data_providers.binance_api.BinanceProvider._make_request')
    def test_get_ticker_price_success(self, mock_make_request):
        """Test récupération ticker price réussi"""
        mock_data = {"symbol": "BTCUSDT", "price": "50000.00"}
        mock_make_request.return_value = mock_data

        result = self.api.get_ticker_price("BTCUSDT")

        assert isinstance(result, dict)
        assert result["symbol"] == "BTCUSDT"
        assert result["price"] == "50000.00"

    @patch('dash_modules.data_providers.binance_api.BinanceProvider._make_request')
    def test_get_ticker_24hr_success(self, mock_make_request):
        """Test récupération ticker 24h réussi"""
        mock_data = {
            "symbol": "BTCUSDT",
            "priceChange": "1000.00",
            "priceChangePercent": "2.00",
            "weightedAvgPrice": "50000.00",
            "prevClosePrice": "49000.00",
            "lastPrice": "50000.00",
            "bidPrice": "49999.00",
            "askPrice": "50001.00",
            "openPrice": "49000.00",
            "highPrice": "51000.00",
            "lowPrice": "48000.00",
            "volume": "1000.00",
            "quoteVolume": "50000000.00",
            "openTime": 1640995200000,
            "closeTime": 1641081600000,
            "firstId": 1,
            "lastId": 100,
            "count": 100
        }
        mock_make_request.return_value = mock_data

        result = self.api.get_ticker_24hr("BTCUSDT")

        assert isinstance(result, dict)
        assert result["symbol"] == "BTCUSDT"
        assert result["priceChange"] == "1000.00"

    @patch('dash_modules.data_providers.binance_api.BinanceProvider._make_request')
    def test_get_klines_success(self, mock_make_request):
        """Test récupération klines réussi"""
        mock_data = [
            [1640995200000, "50000.00", "51000.00", "49000.00", "50500.00", "100.0", 1641081600000, "5000000.00", 100, "50.0", "2500000.00", "0"]
        ]
        mock_make_request.return_value = mock_data

        result = self.api.get_klines("BTCUSDT", "1d", 100)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "open" in result.columns
        assert "close" in result.columns
        assert "volume" in result.columns
        assert result.iloc[0]["close"] == 50500.00

    @patch('dash_modules.data_providers.binance_api.BinanceProvider._make_request')
    def test_get_exchange_info_success(self, mock_make_request):
        """Test récupération info exchange réussi"""
        mock_data = {
            "timezone": "UTC",
            "serverTime": 1641081600000,
            "rateLimits": [],
            "exchangeFilters": [],
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "status": "TRADING",
                    "baseAsset": "BTC",
                    "quoteAsset": "USDT"
                }
            ]
        }
        mock_make_request.return_value = mock_data

        result = self.api.get_exchange_info()

        assert isinstance(result, dict)
        assert "symbols" in result
        assert len(result["symbols"]) == 1

    @patch('dash_modules.data_providers.binance_api.BinanceProvider._make_request')
    def test_get_all_tickers_success(self, mock_make_request):
        """Test récupération tous les tickers réussi"""
        mock_data = [
            {"symbol": "BTCUSDT", "price": "50000.00"},
            {"symbol": "ETHUSDT", "price": "3000.00"}
        ]
        mock_make_request.return_value = mock_data

        result = self.api.get_all_tickers()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["symbol"] == "BTCUSDT"

    def test_get_popular_symbols(self):
        """Test récupération symboles populaires"""
        result = self.api.get_popular_symbols()

        assert isinstance(result, list)
        assert len(result) > 0
        assert "BTCUSDT" in result

    @patch('dash_modules.data_providers.binance_api.BinanceProvider._make_request')
    def test_get_all_symbols_success(self, mock_make_request):
        """Test récupération tous les symboles réussi"""
        mock_data = {
            "symbols": [
                {"symbol": "BTCUSDT", "status": "TRADING"},
                {"symbol": "ETHUSDT", "status": "TRADING"}
            ]
        }
        mock_make_request.return_value = mock_data

        result = self.api.get_all_symbols()

        assert isinstance(result, list)
        assert len(result) == 2
        assert "BTCUSDT" in result

    def test_search_symbols(self):
        """Test recherche de symboles"""
        result = self.api.search_symbols("BTC")

        assert isinstance(result, list)
        # Should find BTC related symbols
        btc_symbols = [s for s in result if "BTC" in s.upper()]
        assert len(btc_symbols) > 0

    @patch('dash_modules.data_providers.binance_api.BinanceProvider._make_request')
    def test_get_market_summary_success(self, mock_make_request):
        """Test récupération résumé marché réussi"""
        mock_data = [
            {"symbol": "BTCUSDT", "price": "50000.00"},
            {"symbol": "ETHUSDT", "price": "3000.00"}
        ]
        mock_make_request.return_value = mock_data

        result = self.api.get_market_summary()

        assert isinstance(result, dict)
        assert "total_symbols" in result
        assert "top_gainers" in result
        assert "top_losers" in result

    @patch('dash_modules.data_providers.binance_api.BinanceProvider._make_request')
    def test_get_news_success(self, mock_make_request):
        """Test récupération actualités réussi"""
        # Binance n'a pas d'API news officielle, cette méthode retourne une liste vide
        mock_make_request.return_value = []

        result = self.api.get_news(10)

        assert isinstance(result, list)