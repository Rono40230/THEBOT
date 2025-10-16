"""
Configuration et fixtures pour les tests d'intégration THEBOT
Fournit des utilitaires communs et données de test
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import MagicMock
import json
import os

# Import des modules principaux pour les fixtures
from dash_modules.data_providers.real_data_manager import RealDataManager
from dash_modules.core.intelligent_cache import get_global_cache
from dash_modules.core.alerts_manager import AlertsManager


@pytest.fixture(scope="session")
def sample_market_data():
    """Données de marché fictives pour les tests"""
    return pd.DataFrame({
        'timestamp': [datetime.now() - timedelta(hours=i) for i in range(100)],
        'open': [50000 + i * 10 for i in range(100)],
        'high': [50100 + i * 10 for i in range(100)],
        'low': [49900 + i * 10 for i in range(100)],
        'close': [50050 + i * 10 for i in range(100)],
        'volume': [1000000 + i * 10000 for i in range(100)]
    })


@pytest.fixture(scope="session")
def sample_crypto_symbols():
    """Liste de symboles crypto pour les tests"""
    return [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT",
        "DOTUSDT", "DOGEUSDT", "AVAXUSDT", "LTCUSDT", "MATICUSDT"
    ]


@pytest.fixture(scope="session")
def sample_price_alerts():
    """Alertes de prix fictives pour les tests"""
    return [
        {
            'id': 'alert_1',
            'symbol': 'BTCUSDT',
            'price': 50000,
            'condition': 'above',
            'type': 'price',
            'active': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'id': 'alert_2',
            'symbol': 'ETHUSDT',
            'price': 3000,
            'condition': 'below',
            'type': 'price',
            'active': True,
            'created_at': datetime.now().isoformat()
        }
    ]


@pytest.fixture(scope="function")
def mock_api_response():
    """Mock response API générique"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"test": "data"}
    mock_response.text = '{"test": "data"}'
    return mock_response


@pytest.fixture(scope="function")
def mock_binance_response():
    """Mock response spécifique à Binance"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "symbol": "BTCUSDT",
        "price": "50000.00",
        "priceChange": "1000.00",
        "priceChangePercent": "2.04",
        "volume": "12345678.90"
    }
    return mock_response


@pytest.fixture(scope="function")
def mock_coingecko_response():
    """Mock response spécifique à CoinGecko"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 50000,
            "market_cap": 950000000000,
            "price_change_24h": 1000,
            "price_change_percentage_24h": 2.04
        }
    ]
    return mock_response


@pytest.fixture(scope="function")
def real_data_manager():
    """Instance RealDataManager pour les tests"""
    return RealDataManager()


@pytest.fixture(scope="function")
def alerts_manager():
    """Instance AlertsManager pour les tests"""
    return AlertsManager()


@pytest.fixture(scope="function")
def intelligent_cache():
    """Instance du cache intelligent"""
    return get_global_cache()


@pytest.fixture(scope="function")
def temp_config_file(tmp_path):
    """Fichier de configuration temporaire pour les tests"""
    config_data = {
        "api_keys": {
            "binance": "test_key",
            "coingecko": "test_key",
            "finnhub": "test_key"
        },
        "cache_settings": {
            "ttl": 300,
            "max_size": 1000
        },
        "alerts_settings": {
            "max_alerts_per_user": 50,
            "check_interval": 60
        }
    }

    config_file = tmp_path / "test_config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    return str(config_file)


@pytest.fixture(scope="function")
def mock_requests_get(monkeypatch):
    """Mock pour requests.get qui retourne toujours une réponse réussie"""
    def mock_get(*args, **kwargs):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"status": "success"}
        response.text = '{"status": "success"}'
        return response

    monkeypatch.setattr("requests.get", mock_get)


@pytest.fixture(scope="function")
def mock_requests_post(monkeypatch):
    """Mock pour requests.post qui retourne toujours une réponse réussie"""
    def mock_post(*args, **kwargs):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"status": "success"}
        response.text = '{"status": "success"}'
        return response

    monkeypatch.setattr("requests.post", mock_post)


@pytest.fixture(scope="function")
def mock_network_error(monkeypatch):
    """Mock qui simule une erreur réseau"""
    import requests

    def mock_get_error(*args, **kwargs):
        raise requests.RequestException("Network error")

    def mock_post_error(*args, **kwargs):
        raise requests.RequestException("Network error")

    monkeypatch.setattr("requests.get", mock_get_error)
    monkeypatch.setattr("requests.post", mock_post_error)


@pytest.fixture(scope="function")
def mock_api_rate_limit(monkeypatch):
    """Mock qui simule une limite de taux API"""
    def mock_get_rate_limit(*args, **kwargs):
        response = MagicMock()
        response.status_code = 429
        response.text = '{"error": "Rate limit exceeded"}'
        return response

    monkeypatch.setattr("requests.get", mock_get_rate_limit)


@pytest.fixture(scope="function")
def mock_api_server_error(monkeypatch):
    """Mock qui simule une erreur serveur API"""
    def mock_get_server_error(*args, **kwargs):
        response = MagicMock()
        response.status_code = 500
        response.text = '{"error": "Internal server error"}'
        return response

    monkeypatch.setattr("requests.get", mock_get_server_error)


@pytest.fixture(scope="function")
def mock_empty_response(monkeypatch):
    """Mock qui retourne une réponse vide"""
    def mock_get_empty(*args, **kwargs):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {}
        response.text = '{}'
        return response

    monkeypatch.setattr("requests.get", mock_get_empty)


@pytest.fixture(scope="function")
def mock_malformed_json(monkeypatch):
    """Mock qui retourne du JSON malformé"""
    def mock_get_malformed(*args, **kwargs):
        response = MagicMock()
        response.status_code = 200
        response.json.side_effect = ValueError("Invalid JSON")
        response.text = '{invalid json'
        return response

    monkeypatch.setattr("requests.get", mock_get_malformed)


@pytest.fixture(scope="session")
def test_data_directory(tmp_path_factory):
    """Répertoire temporaire pour les données de test"""
    return tmp_path_factory.mktemp("test_data")


@pytest.fixture(scope="function")
def sample_news_items():
    """Éléments de news fictifs pour les tests"""
    return [
        {
            'title': 'Bitcoin atteint 50k$',
            'url': 'https://example.com/news1',
            'source': 'CryptoNews',
            'published_at': datetime.now().isoformat(),
            'summary': 'Le Bitcoin a franchi la barre des 50 000 dollars.'
        },
        {
            'title': 'Ethereum upgrade réussi',
            'url': 'https://example.com/news2',
            'source': 'BlockChainToday',
            'published_at': (datetime.now() - timedelta(hours=2)).isoformat(),
            'summary': 'La mise à niveau Ethereum s\'est déroulée avec succès.'
        }
    ]


@pytest.fixture(scope="function")
def sample_economic_events():
    """Événements économiques fictifs pour les tests"""
    return [
        {
            'title': 'Décision de taux FED',
            'country': 'USA',
            'impact': 'High',
            'timestamp': datetime.now() + timedelta(days=1),
            'forecast': '5.25%',
            'previous': '5.50%'
        },
        {
            'title': 'IPC Zone Euro',
            'country': 'EUR',
            'impact': 'Medium',
            'timestamp': datetime.now() + timedelta(days=2),
            'forecast': '2.8%',
            'previous': '2.9%'
        }
    ]


@pytest.fixture(scope="function")
def sample_ai_analysis_result():
    """Résultat d'analyse IA fictif"""
    return {
        'signal': 'BUY',
        'confidence': 0.85,
        'indicators': {
            'rsi': 45,
            'macd': -0.3,
            'sma_20': 49500,
            'sma_50': 48500
        },
        'analysis': 'Les indicateurs suggèrent une opportunité d\'achat à court terme.',
        'timestamp': datetime.now().isoformat()
    }


# Configuration pytest
def pytest_configure(config):
    """Configuration globale pour pytest"""
    # Marqueurs personnalisés
    config.addinivalue_line("markers", "integration: marque les tests d'intégration")
    config.addinivalue_line("markers", "api: marque les tests d'API externes")
    config.addinivalue_line("markers", "slow: marque les tests lents")
    config.addinivalue_line("markers", "network: marque les tests nécessitant le réseau")


def pytest_collection_modifyitems(config, items):
    """Modification automatique des tests"""
    for item in items:
        # Ajouter automatiquement le marqueur integration aux tests d'intégration
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Marquer les tests nécessitant le réseau
        if "api" in item.name.lower() or "network" in item.name.lower():
            item.add_marker(pytest.mark.network)


# Utilitaires de test
def assert_dataframe_not_empty(df, msg="DataFrame should not be empty"):
    """Assertion qu'un DataFrame n'est pas vide"""
    assert isinstance(df, pd.DataFrame), "Should be a DataFrame"
    assert not df.empty, msg


def assert_dict_has_keys(d, keys, msg="Dict should contain required keys"):
    """Assertion qu'un dictionnaire contient certaines clés"""
    assert isinstance(d, dict), "Should be a dict"
    for key in keys:
        assert key in d, f"{msg}: missing key '{key}'"


def assert_api_response_success(response, msg="API response should be successful"):
    """Assertion qu'une réponse API est réussie"""
    assert response is not None, msg
    if hasattr(response, 'status_code'):
        assert response.status_code == 200, f"{msg}: status {response.status_code}"


def wait_for_condition(condition_func, timeout=10, interval=0.1):
    """Attend qu'une condition soit vraie avec timeout"""
    import time
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    return False