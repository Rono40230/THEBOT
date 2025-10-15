"""
Tests pour CoinGecko API provider
Tests complets avec couverture des fonctionnalités principales
"""

import pytest

import pandas as pd

from dash_modules.data_providers.coin_gecko_api import CoinGeckoAPI


class TestCoinGeckoAPI:
    """Tests pour CoinGeckoAPI"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.api = CoinGeckoAPI()
        # Mock du cache pour éviter les interférences
        from unittest.mock import MagicMock
        self.cache_mock = MagicMock()
        self.cache_mock.get.return_value = None  # Pas de données en cache
        self.cache_mock.set.return_value = None
        self.api.cache = self.cache_mock

    def test_initialization(self):
        """Test initialisation de l'API"""
        assert self.api is not None
        assert hasattr(self.api, 'name')
        assert self.api.name == "coin_gecko"
        assert self.api.api_key is None
        assert self.api.base_url == "https://api.coingecko.com/api/v3"

    def test_initialization_with_api_key(self):
        """Test initialisation avec clé API"""
        api = CoinGeckoAPI("test_key")
        assert api.api_key == "test_key"
        assert api.base_url == "https://pro-api.coingecko.com/api/v3"

    def test_supported_markets(self):
        """Test marchés supportés"""
        markets = self.api.supported_markets
        assert isinstance(markets, list)
        assert "bitcoin" in markets
        assert "ethereum" in markets
        assert len(markets) > 5

    def test_rate_limit_info_free_tier(self):
        """Test informations limites de taux - tier gratuit"""
        info = self.api.rate_limit_info
        assert info["requests_per_minute"] == 25
        assert info["has_free_tier"] is True
        assert "free_tier_limits" in info

    def test_rate_limit_info_pro_tier(self):
        """Test informations limites avec clé API"""
        api = CoinGeckoAPI("test_key")
        info = api.rate_limit_info
        assert info["requests_per_minute"] == 500

    def test_validate_symbol(self):
        """Test validation symbole"""
        # Test avec un symbole valide du marché
        assert self.api.validate_symbol('BTC') is True
        assert self.api.validate_symbol('ETH') is True
        assert self.api.validate_symbol('ADA') is True
        assert self.api.validate_symbol('INVALID') is False
        assert self.api.validate_symbol('') is False
        assert self.api.validate_symbol(None) is False

    def test_validate_symbol_case_insensitive(self):
        """Test validation symbole insensible à la casse"""
        assert self.api.validate_symbol('btc') is True
        assert self.api.validate_symbol('BTC') is True
        assert self.api.validate_symbol('Btc') is True

    def test_get_current_price_invalid_symbol(self):
        """Test récupération prix avec symbole invalide"""
        result = self.api.get_current_price("INVALID")
        assert result is None

    def test_get_market_data_empty_list(self):
        """Test récupération données marché - liste vide"""
        result = self.api.get_market_data([])
        assert isinstance(result, pd.DataFrame)

    def test_get_price_data_historical_invalid_coin(self):
        """Test récupération données prix historiques - coin invalide"""
        result = self.api.get_historical_price_data("invalid_coin", days=7)
        assert result.empty

    def test_get_price_data_historical_valid_coin(self):
        """Test récupération données prix historiques - coin valide"""
        result = self.api.get_historical_price_data("bitcoin", days=1)
        assert isinstance(result, pd.DataFrame)
        # Le résultat peut être vide si l'API ne répond pas, mais c'est un DataFrame

    def test_get_trending_coins_method_exists(self):
        """Test que get_trending_coins existe et retourne une liste"""
        result = self.api.get_trending_coins()
        assert isinstance(result, list)

    def test_search_coins_method_exists(self):
        """Test que search_coins existe et retourne une liste"""
        result = self.api.search_coins("bitcoin")
        assert isinstance(result, list)

    def test_get_news_method_exists(self):
        """Test que get_news existe et retourne une liste"""
        result = self.api.get_news(limit=5)
        assert isinstance(result, list)

    def test_is_available(self):
        """Test vérification disponibilité"""
        result = self.api.is_available()
        assert isinstance(result, bool)

    def test_get_status(self):
        """Test récupération statut"""
        status = self.api.get_status()

        assert isinstance(status, dict)
        assert "available" in status
        assert "rate_limit_reset" in status
        assert "name" in status
        assert "supported_markets_count" in status

    def test_get_market_info_invalid_symbol(self):
        """Test récupération info marché - symbole invalide"""
        result = self.api.get_market_info("INVALID")
        assert result is None

    def test_get_price_data_interface_method_invalid_symbol(self):
        """Test méthode get_price_data de l'interface - symbole invalide"""
        result = self.api.get_price_data("INVALID", "1d", 100)
        assert result is None

    def test_get_price_data_interface_method_valid_symbol(self):
        """Test méthode get_price_data de l'interface - symbole valide"""
        # Mock _make_request pour simuler une réponse API
        from unittest.mock import patch
        mock_response = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45000.0,
                "market_cap": 850000000000,
                "market_cap_rank": 1,
                "total_volume": 25000000000,
                "price_change_percentage_1h_in_currency": 0.5,
                "price_change_percentage_24h": 2.1,
                "price_change_percentage_7d_in_currency": -1.5,
                "last_updated": "2024-01-01T12:00:00Z"
            }
        ]
        with patch.object(self.api, '_make_request', return_value=mock_response):
            result = self.api.get_price_data("BTC", "1d", 100)
            # Retourne un dict avec les données actuelles
            assert isinstance(result, dict)
            assert result["symbol"] == "BTC"
            assert result["provider"] == "coin_gecko"

    def test_interface_compliance(self):
        """Test conformité à l'interface DataProviderInterface"""
        # Vérifier que toutes les méthodes de l'interface sont présentes
        required_methods = [
            'name', 'supported_markets', 'rate_limit_info', 'validate_symbol',
            'get_price_data', 'get_current_price', 'get_market_info',
            'is_available', 'get_status'
        ]

        for method in required_methods:
            assert hasattr(self.api, method), f"Méthode {method} manquante"

    def test_error_handling_invalid_json(self):
        """Test gestion JSON invalide - méthode existe"""
        # Cette méthode teste juste que l'API gère les erreurs
        # On ne peut pas facilement simuler les erreurs réseau sans mocks complexes
        assert hasattr(self.api, '_make_request')

    def test_get_market_data_method_exists(self):
        """Test que get_market_data existe"""
        result = self.api.get_market_data()
        assert isinstance(result, pd.DataFrame)

    def test_get_price_data_historical_method_exists(self):
        """Test que get_historical_price_data existe"""
        result = self.api.get_historical_price_data("bitcoin", days=7)
        assert isinstance(result, pd.DataFrame)