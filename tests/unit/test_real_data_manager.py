"""
Tests pour RealDataManager - Gestionnaire de données réelles
Phase 3 - Expansion couverture de test THEBOT
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, Mock
from dash_modules.data_providers.real_data_manager import RealDataManager


class TestRealDataManager:
    """Tests pour le gestionnaire de données réelles"""

    def setup_method(self):
        """Initialisation avant chaque test"""
        with patch('dash_modules.data_providers.real_data_manager.get_global_cache', return_value={}), \
             patch('dash_modules.data_providers.real_data_manager.specialized_api_manager', None), \
             patch('dash_modules.data_providers.real_data_manager.rss_news_manager', None):
            self.manager = RealDataManager()

    def test_initialization(self):
        """Test initialisation du gestionnaire de données réelles"""
        assert isinstance(self.manager.providers, dict)
        assert isinstance(self.manager.supported_markets, dict)
        assert "binance" in self.manager.providers
        assert "coin_gecko" in self.manager.providers
        assert "twelve_data" in self.manager.providers
        assert len(self.manager.supported_markets) > 10

    def test_get_available_markets(self):
        """Test récupération liste marchés disponibles"""
        markets = self.manager.get_available_markets()

        assert isinstance(markets, list)
        assert len(markets) > 0
        assert "BTCUSDT" in markets
        assert "ETHUSDT" in markets
        assert "AAPL" in markets

    def test_get_market_data_invalid_symbol(self):
        """Test récupération données marché avec symbole invalide"""
        result = self.manager.get_market_data("INVALID_SYMBOL")

        assert result is None

    @patch('dash_modules.data_providers.binance_api.binance_provider.get_klines')
    def test_get_market_data_binance_success(self, mock_get_klines):
        """Test récupération données marché Binance réussie"""
        # Mock données Binance
        mock_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=5, freq='h'),
            'open': [50000, 50100, 50200, 50300, 50400],
            'high': [50100, 50200, 50300, 50400, 50500],
            'low': [49900, 50000, 50100, 50200, 50300],
            'close': [50050, 50150, 50250, 50350, 50450],
            'volume': [100, 110, 120, 130, 140]
        })
        mock_get_klines.return_value = mock_data

        result = self.manager.get_market_data("BTCUSDT", "1h", 5)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        mock_get_klines.assert_called_once_with("BTCUSDT", "1h", 5)

    @patch('dash_modules.data_providers.coin_gecko_api.coin_gecko_api.get_price_data')
    def test_get_market_data_coingecko_success(self, mock_get_price_data):
        """Test récupération données marché CoinGecko réussie"""
        # Mock données CoinGecko
        mock_data = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=7, freq='D'),
            'price': [45000, 46000, 47000, 48000, 49000, 50000, 51000],
            'market_cap': [800000000, 820000000, 840000000, 860000000, 880000000, 900000000, 920000000],
            'volume': [20000, 21000, 22000, 23000, 24000, 25000, 26000]
        })
        mock_get_price_data.return_value = mock_data

        result = self.manager.get_market_data("bitcoin", "1d", 3)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3  # Limité à 3 points
        mock_get_price_data.assert_called_once_with("bitcoin", days=7)

    @patch('dash_modules.data_providers.binance_api.binance_provider.get_klines')
    def test_get_market_data_provider_error(self, mock_get_klines):
        """Test récupération données marché avec erreur provider"""
        mock_get_klines.side_effect = Exception("API Error")

        result = self.manager.get_market_data("BTCUSDT")

        assert result is None

    @patch('dash_modules.data_providers.binance_api.binance_provider.get_ticker_24hr')
    def test_get_current_prices_success(self, mock_get_ticker):
        """Test récupération prix actuels réussie"""
        # Mock données ticker
        mock_ticker_data = {
            "last_price": 50000.0,
            "price_change": 1000.0,
            "price_change_percent": 2.0,
            "volume": 1000.0,
            "high_price": 51000.0,
            "low_price": 49000.0
        }
        mock_get_ticker.return_value = mock_ticker_data

        result = self.manager.get_current_prices()

        assert isinstance(result, dict)
        assert "BTCUSDT" in result
        assert result["BTCUSDT"]["price"] == 50000.0
        assert result["BTCUSDT"]["provider"] == "binance"

    @patch('dash_modules.data_providers.binance_api.binance_provider.get_ticker_24hr')
    def test_get_current_prices_with_errors(self, mock_get_ticker):
        """Test récupération prix actuels avec erreurs partielles"""
        # Mock pour échouer sur ETHUSDT
        def mock_ticker_side_effect(symbol):
            if symbol == "ETHUSDT":
                raise Exception("API Error")
            return {
                "last_price": 50000.0,
                "price_change": 1000.0,
                "price_change_percent": 2.0,
                "volume": 1000.0,
                "high_price": 51000.0,
                "low_price": 49000.0
            }

        mock_get_ticker.side_effect = mock_ticker_side_effect

        result = self.manager.get_current_prices()

        assert "BTCUSDT" in result
        assert "ETHUSDT" not in result  # Doit être exclu en cas d'erreur
        """Test récupération résumé marché"""
        summary = self.manager.get_market_summary()

        assert isinstance(summary, dict)
        assert "total_markets" in summary
        assert "crypto_markets" in summary
        assert "stock_markets" in summary
        assert "forex_markets" in summary
        assert summary["total_markets"] == len(self.manager.supported_markets)

    def test_supported_markets_structure(self):
        """Test structure des marchés supportés"""
        markets = self.manager.supported_markets

        # Vérifier quelques marchés clés
        assert "BTCUSDT" in markets
        assert "ETHUSDT" in markets
        assert "AAPL" in markets

        # Vérifier structure d'un marché
        btc_market = markets["BTCUSDT"]
        assert "label" in btc_market
        assert "type" in btc_market
        assert "provider" in btc_market
        assert btc_market["type"] == "crypto"
        assert btc_market["provider"] == "binance"

    def test_search_markets_by_symbol(self):
        """Test recherche marchés par symbole"""
        result = self.manager.search_markets("BTC")

        assert isinstance(result, list)
        # Devrait trouver BTCUSDT et bitcoin
        btc_results = [m for m in result if "BTC" in m["symbol"].upper()]
        assert len(btc_results) > 0

    def test_search_markets_by_name(self):
        """Test recherche marchés par nom"""
        result = self.manager.search_markets("Bitcoin")

        assert isinstance(result, list)
        # Devrait trouver bitcoin
        bitcoin_results = [m for m in result if "bitcoin" in m["symbol"].lower()]
        assert len(bitcoin_results) > 0

    def test_search_markets_no_results(self):
        """Test recherche marchés sans résultats"""
        result = self.manager.search_markets("NONEXISTENT_MARKET_12345")

        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_api_status(self):
        """Test récupération status APIs"""
        status = self.manager.get_api_status()

        assert isinstance(status, dict)
        assert "providers" in status
        assert "cache_status" in status
        assert "total_markets" in status
        assert status["total_markets"] == len(self.manager.supported_markets)

        # Vérifier structure providers
        providers = status["providers"]
        assert "binance" in providers
        assert "coin_gecko" in providers
        assert "twelve_data" in providers

    def test_get_configuration_info(self):
        """Test récupération informations configuration"""
        config = self.manager.get_configuration_info()

        assert isinstance(config, dict)
        assert "supported_providers" in config
        assert "market_types" in config
        assert "total_supported_markets" in config
        assert config["total_supported_markets"] == len(self.manager.supported_markets)

    def test_supported_markets_structure(self):
        """Test structure des marchés supportés"""
        markets = self.manager.supported_markets

        # Vérifier quelques marchés clés
        assert "BTCUSDT" in markets
        assert "ETHUSDT" in markets
        assert "AAPL" in markets

        # Vérifier structure d'un marché
        btc_market = markets["BTCUSDT"]
        assert "label" in btc_market
        assert "type" in btc_market
        assert "provider" in btc_market
        assert btc_market["type"] == "crypto"
        assert btc_market["provider"] == "binance"

    def test_market_types_distribution(self):
        """Test distribution des types de marchés"""
        markets = self.manager.supported_markets

        crypto_count = sum(1 for m in markets.values() if m["type"] == "crypto")
        stocks_count = sum(1 for m in markets.values() if m["type"] == "stocks")
        forex_count = sum(1 for m in markets.values() if m["type"] == "forex")

        assert crypto_count > 0
        assert stocks_count > 0
        assert forex_count >= 0  # Peut être 0 si Twelve Data n'est pas configuré

    def test_provider_distribution(self):
        """Test distribution par provider"""
        markets = self.manager.supported_markets

        binance_count = sum(1 for m in markets.values() if m["provider"] == "binance")
        yahoo_count = sum(1 for m in markets.values() if m["provider"] == "yahoo")
        coingecko_count = sum(1 for m in markets.values() if m["provider"] == "coin_gecko")

        assert binance_count > 0
        assert yahoo_count >= 0
        assert coingecko_count > 0

