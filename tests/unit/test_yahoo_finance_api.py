"""
Tests pour YahooFinanceAPI - API Yahoo Finance THEBOT
Phase 3 - Expansion couverture de test THEBOT
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, Mock
from dash_modules.data_providers.yahoo_finance_api import YahooFinanceAPI


class TestYahooFinanceAPI:
    """Tests pour l'API Yahoo Finance"""

    def setup_method(self):
        """Initialisation avant chaque test"""
        self.api = YahooFinanceAPI()

    def test_initialization(self):
        """Test initialisation de YahooFinanceAPI"""
        assert isinstance(self.api.major_symbols, list)
        assert len(self.api.major_symbols) > 0
        assert "^GSPC" in self.api.major_symbols  # S&P 500
        assert isinstance(self.api.sectors, dict)
        assert "Technology" in self.api.sectors
        assert "Finance" in self.api.sectors
        assert self.api.rate_limit_calls == 0

    def test_rate_limit_check_under_limit(self):
        """Test vérification rate limit sous la limite"""
        self.api.rate_limit_calls = 10
        # Ne devrait pas attendre
        self.api._rate_limit_check()
        assert self.api.rate_limit_calls == 11

    @patch('time.sleep')
    def test_rate_limit_check_over_limit(self, mock_sleep):
        """Test vérification rate limit au-dessus de la limite"""
        self.api.rate_limit_calls = 50
        self.api._rate_limit_check()
        mock_sleep.assert_called_once()
        assert self.api.rate_limit_calls == 51

    @patch('yfinance.Ticker')
    def test_get_stock_data_success(self, mock_ticker_class):
        """Test récupération données d'actions réussie"""
        # Mock ticker
        mock_ticker = Mock()
        mock_hist = pd.DataFrame({
            'Open': [150.0, 151.0, 152.0],
            'High': [155.0, 156.0, 157.0],
            'Low': [149.0, 150.0, 151.0],
            'Close': [154.0, 155.0, 156.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2023-01-01', periods=3))
        mock_ticker.history.return_value = mock_hist
        mock_ticker_class.return_value = mock_ticker

        result = self.api.get_stock_data("AAPL", "1mo")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'open' in result.columns
        assert 'high' in result.columns
        assert 'low' in result.columns
        assert 'close' in result.columns
        assert 'volume' in result.columns
        assert 'timestamp' in result.columns
        mock_ticker_class.assert_called_once_with("AAPL")
        mock_ticker.history.assert_called_once_with(period="1mo")

    @patch('yfinance.Ticker')
    def test_get_stock_data_empty_result(self, mock_ticker_class):
        """Test récupération données d'actions avec résultat vide"""
        mock_ticker = Mock()
        mock_hist = pd.DataFrame()  # Empty DataFrame
        mock_ticker.history.return_value = mock_hist
        mock_ticker_class.return_value = mock_ticker

        result = self.api.get_stock_data("INVALID", "1mo")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch('yfinance.Ticker')
    def test_get_stock_data_error(self, mock_ticker_class):
        """Test récupération données d'actions avec erreur"""
        mock_ticker = Mock()
        mock_ticker.history.side_effect = Exception("API Error")
        mock_ticker_class.return_value = mock_ticker

        result = self.api.get_stock_data("AAPL", "1mo")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_get_forex_data_with_suffix(self):
        """Test récupération données forex avec suffixe =X"""
        with patch.object(self.api, 'get_stock_data') as mock_get_stock:
            mock_get_stock.return_value = pd.DataFrame({'test': [1, 2, 3]})

            result = self.api.get_forex_data("EURUSD=X", "1mo")

            mock_get_stock.assert_called_once_with("EURUSD=X", "1mo")

    def test_get_forex_data_without_suffix(self):
        """Test récupération données forex sans suffixe =X"""
        with patch.object(self.api, 'get_stock_data') as mock_get_stock:
            mock_get_stock.return_value = pd.DataFrame({'test': [1, 2, 3]})

            result = self.api.get_forex_data("EURUSD", "1mo")

            mock_get_stock.assert_called_once_with("EURUSD=X", "1mo")

    @patch('yfinance.Ticker')
    def test_get_quote_success(self, mock_ticker_class):
        """Test récupération cotations réussie"""
        # Mock ticker
        mock_ticker = Mock()
        mock_info = {
            'previousClose': 150.0,
            'marketCap': 2000000000000,
            'volume': 50000000,
            'averageVolume': 45000000
        }
        mock_hist = pd.DataFrame({
            'Close': [154.0, 155.0, 156.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2023-01-01', periods=3))
        mock_ticker.info = mock_info
        mock_ticker.history.return_value = mock_hist
        mock_ticker_class.return_value = mock_ticker

        result = self.api.get_quote(["AAPL"])

        assert isinstance(result, dict)
        assert "AAPL" in result
        quote = result["AAPL"]
        assert "price" in quote
        assert "change" in quote
        assert "change_percent" in quote
        assert "volume" in quote
        assert "market_cap" in quote
        assert quote["price"] == 156.0
        assert quote["change"] == 6.0  # 156 - 150
        assert quote["change_percent"] == 4.0  # (6/150)*100

    @patch('yfinance.Ticker')
    def test_get_quote_empty_history(self, mock_ticker_class):
        """Test récupération cotations avec historique vide"""
        mock_ticker = Mock()
        mock_hist = pd.DataFrame()  # Empty
        mock_ticker.history.return_value = mock_hist
        mock_ticker_class.return_value = mock_ticker

        result = self.api.get_quote(["AAPL"])

        assert isinstance(result, dict)
        assert len(result) == 0

    @patch('yfinance.Ticker')
    def test_get_quote_error(self, mock_ticker_class):
        """Test récupération cotations avec erreur"""
        mock_ticker = Mock()
        mock_ticker.history.side_effect = Exception("API Error")
        mock_ticker_class.return_value = mock_ticker

        result = self.api.get_quote(["AAPL"])

        assert isinstance(result, dict)
        assert len(result) == 0

    @patch('feedparser.parse')
    def test_get_economic_news_success(self, mock_feedparser):
        """Test récupération actualités économiques réussie"""
        # Note: This method generates synthetic news, not RSS feed data
        # The feedparser mock doesn't affect the result since it uses yfinance
        result = self.api.get_economic_news(10)

        assert isinstance(result, list)
        assert len(result) >= 2  # Should generate at least some news
        assert all(isinstance(item, dict) for item in result)

        # Check structure of first item
        first_item = result[0]
        required_keys = ['title', 'summary', 'url', 'published_at', 'source', 'category', 'sentiment', 'description']
        for key in required_keys:
            assert key in first_item, f"Missing key: {key}"

        assert first_item['source'] in ['Yahoo Finance', 'Yahoo Finance Economic Analysis', 'Yahoo Finance Market Data']
        assert first_item['category'] in ['Economic News', 'Market Updates']
        assert first_item['sentiment'] in ['neutral', 'positive', 'negative']

    @patch('feedparser.parse')
    def test_get_economic_news_feed_error(self, mock_feedparser):
        """Test récupération actualités économiques avec erreur de flux"""
        # Even with feedparser error, the method generates synthetic news
        mock_feedparser.side_effect = Exception("Feed parsing error")

        result = self.api.get_economic_news(10)

        assert isinstance(result, list)
        assert len(result) >= 2  # Should still generate synthetic news as fallback

    def test_get_news_alias(self):
        """Test que get_news est un alias pour get_economic_news"""
        with patch.object(self.api, 'get_economic_news') as mock_get_economic:
            mock_get_economic.return_value = [{"title": "Test News"}]

            result = self.api.get_news(10)

            mock_get_economic.assert_called_once_with(10)
            assert result == [{"title": "Test News"}]

    def test_period_mapping(self):
        """Test mapping des périodes"""
        period_map = {
            "1d": "1d",
            "5d": "5d",
            "1mo": "1mo",
            "3mo": "3mo",
            "6mo": "6mo",
            "1y": "1y",
            "2y": "2y",
            "5y": "5y",
            "10y": "10y",
            "max": "max",
        }

        # Test via get_stock_data avec différentes périodes
        for input_period, expected_period in period_map.items():
            with patch('yfinance.Ticker') as mock_ticker_class:
                mock_ticker = Mock()
                mock_hist = pd.DataFrame({
                    'Open': [150.0], 'High': [155.0], 'Low': [149.0],
                    'Close': [154.0], 'Volume': [1000000]
                }, index=pd.date_range('2023-01-01', periods=1))
                mock_ticker.history.return_value = mock_hist
                mock_ticker_class.return_value = mock_ticker

                self.api.get_stock_data("AAPL", input_period)

                mock_ticker.history.assert_called_with(period=expected_period)

    def test_major_symbols_coverage(self):
        """Test couverture des symboles majeurs"""
        expected_symbols = [
            "^GSPC", "^DJI", "^IXIC", "^VIX", "SPY", "QQQ", "IWM"
        ]

        for symbol in expected_symbols:
            assert symbol in self.api.major_symbols

    def test_sector_coverage(self):
        """Test couverture des secteurs"""
        expected_sectors = ["Technology", "Finance", "Healthcare", "Energy", "Consumer"]

        for sector in expected_sectors:
            assert sector in self.api.sectors
            assert isinstance(self.api.sectors[sector], list)
            assert len(self.api.sectors[sector]) > 0

    @patch('yfinance.Ticker')
    def test_get_quote_multiple_symbols(self, mock_ticker_class):
        """Test récupération cotations pour plusieurs symboles"""
        def ticker_side_effect(symbol):
            mock_ticker = Mock()
            mock_info = {'previousClose': 100.0}
            mock_hist = pd.DataFrame({
                'Close': [float(symbol.count('A')) * 100 + 50],  # Différents prix
                'Volume': [1000000]  # Add Volume column
            }, index=pd.date_range('2023-01-01', periods=1))
            mock_ticker.info = mock_info
            mock_ticker.history.return_value = mock_hist
            return mock_ticker

        mock_ticker_class.side_effect = ticker_side_effect

        result = self.api.get_quote(["AAPL", "MSFT", "GOOGL"])

        assert isinstance(result, dict)
        assert len(result) == 3
        assert "AAPL" in result
        assert "MSFT" in result
        assert "GOOGL" in result

    @patch('yfinance.Ticker')
    def test_test_connection_success(self, mock_ticker_class):
        """Test connexion réussie à Yahoo Finance"""
        mock_ticker = Mock()
        mock_ticker.info = {"symbol": "AAPL", "shortName": "Apple Inc."}
        mock_ticker_class.return_value = mock_ticker

        result = self.api.test_connection()

        assert isinstance(result, dict)
        assert result["connected"] is True
        assert result["error"] is None
        assert result["stocks"] is True
        assert result["forex"] is True
        assert "successfully" in result["message"]

    @patch('yfinance.Ticker')
    def test_test_connection_failure(self, mock_ticker_class):
        """Test échec de connexion à Yahoo Finance"""
        mock_ticker = Mock()
        mock_ticker.info = {}  # Empty info
        mock_ticker_class.return_value = mock_ticker

        result = self.api.test_connection()

        assert isinstance(result, dict)
        assert result["connected"] is False
        assert result["error"] == "No data received"
        assert result["stocks"] is False
        assert result["forex"] is False
        self.api.rate_limit_calls = 45
        original_reset = self.api.rate_limit_reset

        # Simulate time passage (more than 1 hour)
        self.api.rate_limit_reset = datetime.now() - timedelta(hours=2)

        self.api._rate_limit_check()

        # Should reset calls to 1 (after increment)
        assert self.api.rate_limit_calls == 1
        assert self.api.rate_limit_reset > original_reset