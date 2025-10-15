"""
Tests pour ProviderManager - Gestionnaire unifié des providers de données
Phase 3 - Expansion couverture de test THEBOT
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from dash_modules.data_providers.provider_manager import ProviderManager
from dash_modules.data_providers.provider_interfaces import (
    DataProviderInterface,
    NewsProviderInterface,
    EconomicProviderInterface
)


class TestProviderManager:
    """Tests pour le gestionnaire unifié des providers"""

    def setup_method(self):
        """Initialisation avant chaque test"""
        self.manager = ProviderManager()

    @patch('dash_modules.data_providers.provider_manager.ProviderFactory')
    def test_initialization(self, mock_factory):
        """Test initialisation du gestionnaire de providers"""
        # Mock factory
        mock_factory.get_available_providers.return_value = ['binance', 'yahoo']
        mock_factory.get_provider.side_effect = lambda name: Mock() if name in ['binance', 'yahoo'] else None

        # Réinitialise le manager pour déclencher l'initialisation
        manager = ProviderManager()

        assert isinstance(manager.providers, dict)
        assert len(manager.providers) == 2
        mock_factory.get_available_providers.assert_called_once()
        assert mock_factory.get_provider.call_count == 2

    @patch('dash_modules.data_providers.provider_manager.ProviderFactory')
    def test_initialize_providers_with_errors(self, mock_factory):
        """Test initialisation avec erreurs de providers"""
        # Mock factory qui échoue pour un provider
        mock_factory.get_available_providers.return_value = ['working', 'broken']
        mock_factory.get_provider.side_effect = lambda name: Mock() if name == 'working' else None

        manager = ProviderManager()

        assert 'working' in manager.providers
        assert 'broken' not in manager.providers
        assert len(manager.providers) == 1

    def test_get_data_provider(self):
        """Test récupération provider de données"""
        # Setup mock provider
        mock_provider = Mock(spec=DataProviderInterface)
        self.manager.providers['test_provider'] = mock_provider

        result = self.manager.get_data_provider('test_provider')

        assert result == mock_provider

    def test_get_data_provider_not_found(self):
        """Test récupération provider inexistant"""
        result = self.manager.get_data_provider('nonexistent')

        assert result is None

    def test_get_news_provider(self):
        """Test récupération provider d'actualités"""
        mock_provider = Mock(spec=NewsProviderInterface)
        self.manager.providers['news_provider'] = mock_provider

        result = self.manager.get_news_provider('news_provider')

        assert result == mock_provider

    def test_get_economic_provider(self):
        """Test récupération provider économique"""
        mock_provider = Mock(spec=EconomicProviderInterface)
        self.manager.providers['economic_provider'] = mock_provider

        result = self.manager.get_economic_provider('economic_provider')

        assert result == mock_provider

    def test_get_available_data_providers(self):
        """Test récupération liste providers de données disponibles"""
        # Setup mock providers
        data_provider = Mock(spec=DataProviderInterface)
        news_provider = Mock(spec=NewsProviderInterface)
        economic_provider = Mock(spec=EconomicProviderInterface)

        self.manager.providers = {
            'data1': data_provider,
            'news1': news_provider,
            'economic1': economic_provider,
            'data2': data_provider
        }

        result = self.manager.get_available_data_providers()

        assert len(result) == 2
        assert 'data1' in result
        assert 'data2' in result
        assert 'news1' not in result

    def test_get_available_news_providers(self):
        """Test récupération liste providers d'actualités disponibles"""
        # Setup mock providers
        data_provider = Mock(spec=DataProviderInterface)
        news_provider = Mock(spec=NewsProviderInterface)

        self.manager.providers = {
            'data1': data_provider,
            'news1': news_provider,
            'news2': news_provider
        }

        result = self.manager.get_available_news_providers()

        assert len(result) == 2
        assert 'news1' in result
        assert 'news2' in result
        assert 'data1' not in result

    def test_get_price_data_specific_provider(self):
        """Test récupération données de prix avec provider spécifique"""
        mock_provider = Mock(spec=DataProviderInterface)
        mock_provider.get_price_data.return_value = {'price': 50000}
        self.manager.providers['binance'] = mock_provider

        result = self.manager.get_price_data('BTCUSDT', provider='binance')

        assert result == {'price': 50000}
        mock_provider.get_price_data.assert_called_once_with('BTCUSDT', '1d', 100)

    def test_get_price_data_fallback_providers(self):
        """Test récupération données de prix avec fallback"""
        # Setup providers : premier échoue, deuxième réussit
        failing_provider = Mock(spec=DataProviderInterface)
        failing_provider.get_price_data.return_value = None

        success_provider = Mock(spec=DataProviderInterface)
        success_provider.get_price_data.return_value = {'price': 45000}

        self.manager.providers = {
            'provider1': failing_provider,
            'provider2': success_provider
        }

        result = self.manager.get_price_data('ETHUSDT')

        assert result == {'price': 45000}
        failing_provider.get_price_data.assert_called_once()
        success_provider.get_price_data.assert_called_once()

    def test_get_price_data_no_provider_available(self):
        """Test récupération données de prix sans provider disponible"""
        # Vide les providers pour ce test
        original_providers = self.manager.providers.copy()
        self.manager.providers = {}

        try:
            result = self.manager.get_price_data('BTCUSDT')
            assert result is None
        finally:
            # Restaure les providers
            self.manager.providers = original_providers

    def test_get_current_price_specific_provider(self):
        """Test récupération prix actuel avec provider spécifique"""
        mock_provider = Mock(spec=DataProviderInterface)
        mock_provider.get_current_price.return_value = 51000.0
        self.manager.providers['binance'] = mock_provider

        result = self.manager.get_current_price('BTCUSDT', provider='binance')

        assert result == 51000.0
        mock_provider.get_current_price.assert_called_once_with('BTCUSDT')

    def test_get_current_price_fallback(self):
        """Test récupération prix actuel avec fallback"""
        failing_provider = Mock(spec=DataProviderInterface)
        failing_provider.get_current_price.return_value = None

        success_provider = Mock(spec=DataProviderInterface)
        success_provider.get_current_price.return_value = 48000.0

        self.manager.providers = {
            'provider1': failing_provider,
            'provider2': success_provider
        }

        result = self.manager.get_current_price('BTCUSDT')

        assert result == 48000.0

    def test_get_market_info_specific_provider(self):
        """Test récupération informations marché avec provider spécifique"""
        mock_provider = Mock(spec=DataProviderInterface)
        market_info = {'symbol': 'BTCUSDT', 'base': 'BTC', 'quote': 'USDT'}
        mock_provider.get_market_info.return_value = market_info
        self.manager.providers['binance'] = mock_provider

        result = self.manager.get_market_info('BTCUSDT', provider='binance')

        assert result == market_info
        mock_provider.get_market_info.assert_called_once_with('BTCUSDT')

    def test_get_news_specific_provider(self):
        """Test récupération actualités avec provider spécifique"""
        mock_provider = Mock(spec=NewsProviderInterface)
        news_data = [{'title': 'Breaking News', 'content': 'Something happened'}]
        mock_provider.get_news.return_value = news_data
        self.manager.providers['crypto_panic'] = mock_provider

        result = self.manager.get_news(symbol='BTC', provider='crypto_panic', limit=10)

        assert result == news_data
        mock_provider.get_news.assert_called_once_with('BTC', 10)

    def test_get_news_multiple_providers(self):
        """Test récupération actualités depuis plusieurs providers"""
        provider1 = Mock(spec=NewsProviderInterface)
        provider1.get_news.return_value = [
            {'title': 'News 1', 'published': '2023-01-01'},
            {'title': 'News 2', 'published': '2023-01-02'}
        ]

        provider2 = Mock(spec=NewsProviderInterface)
        provider2.get_news.return_value = [
            {'title': 'News 3', 'published': '2023-01-03'}
        ]

        self.manager.providers = {
            'provider1': provider1,
            'provider2': provider2
        }

        result = self.manager.get_news(limit=5)

        assert len(result) == 3
        # Vérifie que c'est trié par date décroissante
        assert result[0]['title'] == 'News 3'
        assert result[1]['title'] == 'News 2'
        assert result[2]['title'] == 'News 1'

    def test_search_news_specific_provider(self):
        """Test recherche d'actualités avec provider spécifique"""
        mock_provider = Mock(spec=NewsProviderInterface)
        search_results = [{'title': 'Bitcoin News', 'relevance': 0.9}]
        mock_provider.search_news.return_value = search_results
        self.manager.providers['news_api'] = mock_provider

        result = self.manager.search_news('bitcoin', provider='news_api', limit=20)

        assert result == search_results
        mock_provider.search_news.assert_called_once_with('bitcoin', 20)

    def test_search_news_multiple_providers(self):
        """Test recherche d'actualités depuis plusieurs providers"""
        provider1 = Mock(spec=NewsProviderInterface)
        provider1.search_news.return_value = [{'title': 'Result 1'}]

        provider2 = Mock(spec=NewsProviderInterface)
        provider2.search_news.return_value = [{'title': 'Result 2'}, {'title': 'Result 3'}]

        self.manager.providers = {
            'provider1': provider1,
            'provider2': provider2
        }

        result = self.manager.search_news('crypto', limit=10)

        assert len(result) == 3

    def test_get_provider_status_specific_provider(self):
        """Test récupération statut d'un provider spécifique"""
        mock_provider = Mock()
        mock_provider.get_status.return_value = {'status': 'active', 'latency': 150}
        self.manager.providers['test_provider'] = mock_provider

        result = self.manager.get_provider_status('test_provider')

        assert result == {'status': 'active', 'latency': 150}
        mock_provider.get_status.assert_called_once()

    def test_get_provider_status_all_providers(self):
        """Test récupération statut de tous les providers"""
        provider1 = Mock()
        provider1.get_status.return_value = {'status': 'active'}

        provider2 = Mock()
        # Configure provider2 pour ne pas avoir get_status
        del provider2.get_status

        self.manager.providers = {
            'provider1': provider1,
            'provider2': provider2
        }

        result = self.manager.get_provider_status()

        assert 'provider1' in result
        assert 'provider2' in result
        assert result['provider1'] == {'status': 'active'}
        assert result['provider2'] == {'error': 'Status not available'}

    def test_get_provider_status_not_found(self):
        """Test récupération statut provider inexistant"""
        result = self.manager.get_provider_status('nonexistent')

        assert result == {'error': 'Provider nonexistent not found'}

    def test_validate_symbol_specific_provider(self):
        """Test validation symbole avec provider spécifique"""
        mock_provider = Mock(spec=DataProviderInterface)
        mock_provider.validate_symbol.return_value = True
        self.manager.providers['binance'] = mock_provider

        result = self.manager.validate_symbol('BTCUSDT', provider='binance')

        assert result is True
        mock_provider.validate_symbol.assert_called_once_with('BTCUSDT')

    def test_validate_symbol_fallback(self):
        """Test validation symbole avec fallback"""
        failing_provider = Mock(spec=DataProviderInterface)
        failing_provider.validate_symbol.return_value = False

        success_provider = Mock(spec=DataProviderInterface)
        success_provider.validate_symbol.return_value = True

        self.manager.providers = {
            'provider1': failing_provider,
            'provider2': success_provider
        }

        result = self.manager.validate_symbol('ETHUSDT')

        assert result is True

    def test_validate_symbol_invalid(self):
        """Test validation symbole invalide"""
        mock_provider = Mock(spec=DataProviderInterface)
        mock_provider.validate_symbol.return_value = False
        self.manager.providers['provider1'] = mock_provider

        result = self.manager.validate_symbol('INVALID')

        assert result is False

    def test_get_supported_markets_specific_provider(self):
        """Test récupération marchés supportés pour provider spécifique"""
        mock_provider = Mock(spec=DataProviderInterface)
        mock_provider.supported_markets = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        self.manager.providers['binance'] = mock_provider

        result = self.manager.get_supported_markets(provider='binance')

        assert result == ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']

    def test_get_supported_markets_all_providers(self):
        """Test récupération marchés supportés pour tous les providers"""
        provider1 = Mock(spec=DataProviderInterface)
        provider1.supported_markets = ['BTCUSDT', 'ETHUSDT']

        provider2 = Mock(spec=DataProviderInterface)
        provider2.supported_markets = ['ADAUSDT', 'DOTUSDT']

        non_data_provider = Mock()

        self.manager.providers = {
            'binance': provider1,
            'coinbase': provider2,
            'news_provider': non_data_provider
        }

        result = self.manager.get_supported_markets()

        assert 'binance' in result
        assert 'coinbase' in result
        assert 'news_provider' not in result
        assert result['binance'] == ['BTCUSDT', 'ETHUSDT']
        assert result['coinbase'] == ['ADAUSDT', 'DOTUSDT']

    def test_get_supported_markets_provider_not_found(self):
        """Test récupération marchés pour provider inexistant"""
        # Vide temporairement les providers
        original_providers = self.manager.providers.copy()
        self.manager.providers = {}

        try:
            result = self.manager.get_supported_markets(provider='nonexistent')
            assert result == []
        finally:
            # Restaure les providers
            self.manager.providers = original_providers