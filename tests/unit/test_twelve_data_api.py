"""
Tests pour Twelve Data API provider
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, Mock
from dash_modules.data_providers.twelve_data_api import TwelveDataAPI


class TestTwelveDataAPI:
    """Tests pour TwelveDataAPI"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.api = TwelveDataAPI("test_api_key")

    def test_initialization(self):
        """Test initialisation de l'API"""
        assert self.api is not None
        assert hasattr(self.api, 'name')
        assert self.api.name == "twelve_data"
        assert self.api.api_key == "test_api_key"
        assert self.api.base_url == "https://api.twelvedata.com"

    def test_supported_markets(self):
        """Test marchés supportés"""
        markets = self.api.supported_markets
        assert isinstance(markets, list)
        assert len(markets) > 0
        assert "AAPL" in markets

    def test_rate_limit_info(self):
        """Test informations rate limit"""
        info = self.api.rate_limit_info
        assert isinstance(info, dict)
        assert "requests_per_minute" in info
        assert info["has_free_tier"] is True

    def test_validate_symbol(self):
        """Test validation symbole"""
        assert self.api.validate_symbol('AAPL') is True
        assert self.api.validate_symbol('BTC/USD') is True
        assert self.api.validate_symbol('INVALID') is False
        assert self.api.validate_symbol('') is False
        assert self.api.validate_symbol(None) is False

    @patch('requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test requête HTTP réussie"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok", "data": "test"}
        mock_get.return_value = mock_response

        result = self.api._make_request("test_endpoint", {"param": "value"})

        assert result == {"status": "ok", "data": "test"}
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_make_request_error(self, mock_get):
        """Test requête HTTP avec erreur"""
        mock_get.side_effect = Exception("Network error")

        result = self.api._make_request("test_endpoint")

        assert result is None

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_price_data_success(self, mock_make_request):
        """Test récupération données de prix réussie"""
        mock_data = {
            "meta": {"symbol": "AAPL", "interval": "1d"},
            "values": [
                {
                    "datetime": "2023-01-01",
                    "open": "150.00",
                    "high": "155.00",
                    "low": "149.00",
                    "close": "152.00",
                    "volume": "1000000"
                }
            ],
            "status": "ok"
        }
        mock_make_request.return_value = mock_data

        result = self.api.get_price_data("AAPL", "1d", 100)

        assert isinstance(result, dict)
        assert result["symbol"] == "AAPL"
        assert "data" in result
        assert len(result["data"]) == 1

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_price_data_error(self, mock_make_request):
        """Test récupération données de prix avec erreur"""
        mock_make_request.return_value = None

        result = self.api.get_price_data("AAPL")

        assert result is None

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_current_price_success(self, mock_make_request):
        """Test récupération prix actuel réussi"""
        mock_data = {"close": "152.50"}
        mock_make_request.return_value = mock_data

        result = self.api.get_current_price("AAPL")

        assert result == 152.50

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_current_price_error(self, mock_make_request):
        """Test récupération prix actuel avec erreur"""
        mock_make_request.return_value = None

        result = self.api.get_current_price("AAPL")

        assert result is None

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_market_info_success(self, mock_make_request):
        """Test récupération info marché réussie"""
        mock_data = {
            "name": "Apple Inc.",
            "close": "152.50",
            "open": "150.00",
            "high": "155.00",
            "low": "149.00",
            "volume": "1000000",
            "percent_change": "1.5"
        }
        mock_make_request.return_value = mock_data

        result = self.api.get_market_info("AAPL")

        assert isinstance(result, dict)
        assert result["symbol"] == "AAPL"
        assert result["name"] == "Apple Inc."
        assert result["current_price"] == "152.50"  # String as returned by API
        assert result["volume"] == "1000000"  # String as returned by API

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_market_info_error(self, mock_make_request):
        """Test récupération info marché avec erreur"""
        mock_make_request.return_value = None

        result = self.api.get_market_info("AAPL")

        assert result is None

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI.get_current_price')
    def test_is_available_with_key(self, mock_get_current_price):
        """Test disponibilité avec clé API"""
        mock_get_current_price.return_value = 152.50
        assert self.api.is_available() is True

    def test_is_available_without_key(self):
        """Test disponibilité sans clé API"""
        api_no_key = TwelveDataAPI("")
        assert api_no_key.is_available() is False

    def test_get_status(self):
        """Test récupération statut"""
        status = self.api.get_status()

        assert isinstance(status, dict)
        assert "available" in status
        assert "api_key_configured" in status
        assert "last_request_time" in status
        assert "name" in status

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_financial_news_success(self, mock_make_request):
        """Test récupération actualités financières réussie"""
        mock_data = {
            "data": [
                {
                    "title": "Market Update: Tech Stocks Rise",
                    "description": "Technology stocks showed strong performance today",
                    "url": "https://example.com/news1",
                    "date": "2023-01-01",
                    "time": "12:30:45"
                }
            ]
        }
        mock_make_request.return_value = mock_data

        result = self.api.get_financial_news(10)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Market Update: Tech Stocks Rise"
        assert result[0]["description"] == "Technology stocks showed strong performance today"
        assert "provider" in result[0]
        assert result[0]["provider"] == "twelve_data"

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_financial_news_error(self, mock_make_request):
        """Test récupération actualités financières avec erreur"""
        mock_make_request.return_value = None

        result = self.api.get_financial_news(10)

        assert isinstance(result, list)
        assert len(result) == 0

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_stock_data_success(self, mock_make_request):
        """Test récupération données d'actions réussie"""
        mock_data = {
            "meta": {"symbol": "AAPL", "interval": "1d"},
            "values": [
                {
                    "datetime": "2023-01-01",
                    "open": "150.00",
                    "high": "155.00",
                    "low": "149.00",
                    "close": "152.00",
                    "volume": "1000000"
                },
                {
                    "datetime": "2023-01-02",
                    "open": "152.00",
                    "high": "158.00",
                    "low": "151.00",
                    "close": "155.00",
                    "volume": "1200000"
                }
            ],
            "status": "ok"
        }
        mock_make_request.return_value = mock_data

        result = self.api.get_stock_data("AAPL", "1d", 100)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "open" in result.columns
        assert "close" in result.columns
        assert "volume" in result.columns
        assert result.iloc[0]["close"] == 152.00
        assert result.iloc[1]["close"] == 155.00

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_stock_data_error(self, mock_make_request):
        """Test récupération données d'actions avec erreur"""
        mock_make_request.return_value = None

        result = self.api.get_stock_data("AAPL")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_forex_data_success(self, mock_make_request):
        """Test récupération données forex réussie"""
        mock_data = {
            "meta": {"symbol": "EUR/USD", "interval": "1d"},
            "values": [
                {
                    "datetime": "2023-01-01",
                    "open": "1.0500",
                    "high": "1.0600",
                    "low": "1.0450",
                    "close": "1.0520",
                    "volume": "50000"
                }
            ],
            "status": "ok"
        }
        mock_make_request.return_value = mock_data

        result = self.api.get_forex_data("EUR/USD", "1d", 100)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["close"] == 1.0520

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_crypto_data_success(self, mock_make_request):
        """Test récupération données crypto réussie"""
        mock_data = {
            "meta": {"symbol": "BTC/USD", "interval": "1d"},
            "values": [
                {
                    "datetime": "2023-01-01",
                    "open": "20000.00",
                    "high": "21000.00",
                    "low": "19500.00",
                    "close": "20500.00",
                    "volume": "1000"
                }
            ],
            "status": "ok"
        }
        mock_make_request.return_value = mock_data

        result = self.api.get_crypto_data("BTC/USD", "1d", 100)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["close"] == 20500.00

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_real_time_price_success(self, mock_make_request):
        """Test récupération prix temps réel réussi"""
        mock_data = {
            "price": "152.50",
            "volume": "1000000",
            "timestamp": "1638360000"
        }
        mock_make_request.return_value = mock_data

        result = self.api.get_real_time_price("AAPL")

        assert isinstance(result, dict)
        assert result["symbol"] == "AAPL"
        assert result["price"] == 152.50

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_real_time_price_error(self, mock_make_request):
        """Test récupération prix temps réel avec erreur"""
        mock_make_request.return_value = None

        result = self.api.get_real_time_price("AAPL")

        assert result is None

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_supported_stocks_success(self, mock_make_request):
        """Test récupération actions supportées réussie"""
        mock_data = {
            "data": [
                {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
                {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"}
            ]
        }
        mock_make_request.return_value = mock_data

        result = self.api.get_supported_stocks()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["symbol"] == "AAPL"
        assert result[0]["name"] == "Apple Inc."

    @patch('dash_modules.data_providers.twelve_data_api.TwelveDataAPI._make_request')
    def test_get_supported_forex_pairs_success(self, mock_make_request):
        """Test récupération paires forex supportées réussie"""
        mock_data = {
            "data": [
                {"symbol": "EUR/USD", "name": "Euro/US Dollar"},
                {"symbol": "GBP/USD", "name": "British Pound/US Dollar"}
            ]
        }
        mock_make_request.return_value = mock_data

        result = self.api.get_supported_forex_pairs()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["symbol"] == "EUR/USD"

    def test_format_time(self):
        """Test formatage du temps"""
        datetime_str = "2023-01-01 12:30:45"
        result = self.api._format_time(datetime_str)

        assert isinstance(result, str)
        # Le format exact dépend de l'implémentation