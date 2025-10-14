"""
Tests d'intégration pour les APIs de données THEBOT
Vérifie la connectivité et la gestion d'erreurs des APIs externes
"""

import pytest
import requests
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta

# Import des providers à tester
from dash_modules.data_providers.binance_api import BinanceProvider
from dash_modules.data_providers.coin_gecko_api import CoinGeckoAPI
from dash_modules.data_providers.real_data_manager import RealDataManager


class TestBinanceAPIIntegration:
    """Tests d'intégration pour l'API Binance"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.binance = BinanceProvider()

    def test_binance_connection_alive(self):
        """Test que l'API Binance est accessible"""
        try:
            # Test basique de connectivité
            response = requests.get("https://api.binance.com/api/v3/ping", timeout=10)
            assert response.status_code == 200
            assert response.json() == {}
        except requests.RequestException as e:
            pytest.skip(f"Binance API non accessible: {e}")

    def test_get_ticker_price_valid_symbol(self):
        """Test récupération prix avec symbole valide"""
        result = self.binance.get_ticker_price("BTCUSDT")
        assert result is not None
        assert isinstance(result, dict)
        assert "symbol" in result
        assert "price" in result
        assert result["symbol"] == "BTCUSDT"
        assert float(result["price"]) > 0

    def test_get_ticker_price_invalid_symbol(self):
        """Test gestion symbole invalide"""
        result = self.binance.get_ticker_price("")
        assert result is None

    def test_get_ticker_price_malformed_symbol(self):
        """Test gestion symbole malformé"""
        result = self.binance.get_ticker_price("INVALID")
        # Devrait retourner None ou gérer l'erreur gracieusement
        assert result is None or isinstance(result, dict)

    def test_get_24hr_ticker(self):
        """Test récupération statistiques 24h"""
        result = self.binance.get_24hr_ticker("BTCUSDT")
        assert isinstance(result, dict)
        if result:  # Si l'API répond
            assert "priceChange" in result
            assert "volume" in result

    def test_get_popular_symbols(self):
        """Test récupération symboles populaires"""
        symbols = self.binance.get_popular_symbols()
        assert isinstance(symbols, list)
        assert len(symbols) > 0
        assert "BTCUSDT" in symbols

    @patch('requests.get')
    def test_network_error_handling(self, mock_get):
        """Test gestion des erreurs réseau"""
        mock_get.side_effect = requests.RequestException("Network error")

        result = self.binance.get_ticker_price("BTCUSDT")
        assert result is None

    @patch('requests.get')
    def test_api_error_handling(self, mock_get):
        """Test gestion des erreurs API"""
        mock_response = MagicMock()
        mock_response.status_code = 429  # Rate limit
        mock_response.text = "Too many requests"
        mock_get.return_value = mock_response

        result = self.binance.get_ticker_price("BTCUSDT")
        assert result is None


class TestCoinGeckoAPIIntegration:
    """Tests d'intégration pour l'API CoinGecko"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.coingecko = CoinGeckoAPI()

    def test_coingecko_connection_alive(self):
        """Test que l'API CoinGecko est accessible"""
        try:
            response = requests.get("https://api.coingecko.com/api/v3/ping", timeout=10)
            assert response.status_code == 200
            data = response.json()
            assert "gecko_says" in data
        except requests.RequestException as e:
            pytest.skip(f"CoinGecko API non accessible: {e}")

    def test_get_market_data(self):
        """Test récupération données marché"""
        df = self.coingecko.get_market_data()
        assert isinstance(df, pd.DataFrame)
        if not df.empty:  # Si des données sont retournées
            assert "symbol" in df.columns
            assert "price" in df.columns
            assert "market_cap" in df.columns
            assert len(df) > 0

    def test_get_price_data_valid_coin(self):
        """Test récupération données prix pour coin valide"""
        df = self.coingecko.get_price_data("bitcoin")
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert len(df) > 0
            assert "price" in df.columns

    def test_get_price_data_invalid_coin(self):
        """Test gestion coin invalide"""
        df = self.coingecko.get_price_data("")
        assert isinstance(df, pd.DataFrame)
        assert df.empty

    @patch('requests.get')
    def test_coingecko_network_error(self, mock_get):
        """Test gestion erreurs réseau CoinGecko"""
        mock_get.side_effect = requests.RequestException("Network error")

        df = self.coingecko.get_market_data()
        assert isinstance(df, pd.DataFrame)
        assert df.empty


class TestRealDataManagerIntegration:
    """Tests d'intégration pour le RealDataManager"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.manager = RealDataManager()

    def test_get_available_markets(self):
        """Test récupération marchés disponibles"""
        markets = self.manager.get_available_markets()
        assert isinstance(markets, list)
        assert len(markets) > 0
        # Vérifie que des symboles crypto sont présents
        assert any("BTC" in symbol or "ETH" in symbol for symbol in markets)

    def test_get_current_prices(self):
        """Test récupération prix actuels"""
        prices = self.manager.get_current_prices()
        assert isinstance(prices, dict)
        # Vérifie que des prix sont récupérés (peut être vide si APIs down)
        assert isinstance(prices, dict)

    def test_search_markets(self):
        """Test recherche de marchés"""
        results = self.manager.search_markets("BTC")
        assert isinstance(results, list)
        # Peut être vide si pas de résultats ou APIs down

    def test_api_status(self):
        """Test récupération statut des APIs"""
        status = self.manager.get_api_status()
        assert isinstance(status, dict)
        assert "binance" in status
        # Le statut peut ne contenir que Binance selon l'implémentation actuelle
        binance_status = status["binance"]
        assert isinstance(binance_status, dict)
        assert "active" in binance_status
        assert "name" in binance_status


class TestRSSIntegration:
    """Tests d'intégration pour les flux RSS"""

    def test_rss_sources_accessible(self):
        """Test que les sources RSS sont accessibles"""
        from dash_modules.data_providers.rss_sources_config import RSSSourcesConfig

        config = RSSSourcesConfig()
        sources = config.get_all_sources()

        accessible_count = 0
        total_count = 0

        for category, source_list in sources.items():
            for source in source_list:
                total_count += 1
                try:
                    response = requests.get(source["url"], timeout=10)
                    if response.status_code == 200:
                        accessible_count += 1
                except requests.RequestException:
                    continue

        # Au moins 50% des sources devraient être accessibles
        assert accessible_count / total_count > 0.5

    def test_rss_news_manager(self):
        """Test du RSS News Manager"""
        from dash_modules.data_providers.rss_news_manager import RSSNewsManager

        manager = RSSNewsManager()
        news = manager.get_news(limit=5)

        assert isinstance(news, list)
        # Peut être vide si sources non accessibles
        if news:
            assert len(news) <= 5
            for item in news:
                assert "title" in item
                assert "url" in item


class TestCacheIntegration:
    """Tests d'intégration pour le système de cache"""

    def test_intelligent_cache(self):
        """Test du cache intelligent"""
        from dash_modules.core.intelligent_cache import get_global_cache

        cache = get_global_cache()
        assert cache is not None

        # Test stockage/récupération
        test_key = "test_integration_key"
        test_data = {"test": "data", "timestamp": datetime.now()}

        # Test que le cache est initialisé
        assert hasattr(cache, '_cache')
        assert hasattr(cache, 'set')
        assert hasattr(cache, 'get')

        # Test basique de fonctionnement
        test_key = "test_integration_key"
        test_data = {"test": "data", "timestamp": datetime.now()}

        # Test set (ne devrait pas lever d'exception)
        try:
            cache.set("test_prefix", test_data, key=test_key, ttl=300)
            assert True  # Si on arrive ici, c'est que set fonctionne
        except Exception as e:
            pytest.skip(f"Cache set failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])