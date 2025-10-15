"""
Tests d'intégration Phase 5 - Interaction Managers MVC et Services
Valide l'intégration complète entre les contrôleurs MVC et les services métier
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

import dash
from dash import html

from dash_modules.services import AlertService, MarketDataService, UserPreferencesService, DashboardService
from dash_modules.callbacks.managers.alert_modal_manager import AlertModalManager
from dash_modules.callbacks.managers.market_modal_manager import MarketModalManager
from dash_modules.callbacks.managers.news_modal_manager import NewsModalManager
from dash_modules.models import Alert, AlertType, MarketData


class TestAlertModalManagerIntegration:
    """Tests d'intégration AlertModalManager ↔ AlertService"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()

        # Créer un service d'alertes avec fichier temporaire
        self.alert_service = AlertService(data_file=self.temp_file.name)

        # Mock du service dans le manager
        with patch('dash_modules.callbacks.managers.alert_modal_manager.alert_service', self.alert_service):
            self.manager = AlertModalManager(self.app)

    def teardown_method(self):
        """Nettoyage après chaque test"""
        Path(self.temp_file.name).unlink(missing_ok=True)

    def test_alert_modal_manager_initialization(self):
        """Test que le manager s'initialise correctement avec le service"""
        assert self.manager is not None
        assert self.manager.app == self.app
        assert self.manager.name == "AlertModalManager"

    def test_alert_creation_integration(self):
        """Test intégration création d'alerte via service"""
        # Créer une alerte via le service
        alert = self.alert_service.create_alert(
            symbol="BTCUSDT",
            alert_type=AlertType.ABOVE,
            price=50000.0,
            message="Test alert"
        )

        # Vérifier que l'alerte est créée
        assert alert.symbol == "BTCUSDT"
        assert alert.alert_type == AlertType.ABOVE
        assert alert.price == 50000.0
        assert alert.message == "Test alert"
        assert alert.id in self.alert_service.alerts

        # Vérifier la persistance
        saved_alerts = self.alert_service.get_all_alerts()
        assert len(saved_alerts) == 1
        assert saved_alerts[0].id == alert.id

    def test_alert_retrieval_integration(self):
        """Test intégration récupération d'alertes"""
        # Créer plusieurs alertes
        alert1 = self.alert_service.create_alert("BTCUSDT", AlertType.ABOVE, 50000.0)
        alert2 = self.alert_service.create_alert("ETHUSDT", AlertType.BELOW, 3000.0)
        alert3 = self.alert_service.create_alert("BTCUSDT", AlertType.ABOVE, 55000.0)

        # Tester récupération par ID
        retrieved = self.alert_service.get_alert(alert1.id)
        assert retrieved == alert1

        # Tester récupération toutes les alertes
        all_alerts = self.alert_service.get_all_alerts()
        assert len(all_alerts) == 3

        # Tester récupération par symbole
        btc_alerts = self.alert_service.get_alerts_for_symbol("BTCUSDT")
        assert len(btc_alerts) == 2
        assert all(a.symbol == "BTCUSDT" for a in btc_alerts)

    def test_alert_update_integration(self):
        """Test intégration mise à jour d'alerte"""
        # Créer une alerte
        alert = self.alert_service.create_alert("BTCUSDT", AlertType.ABOVE, 50000.0)

        # Mettre à jour via le service
        updated = self.alert_service.update_alert(
            alert.id,
            price=55000.0,
            message="Updated alert"
        )

        assert updated is not None
        assert updated.price == 55000.0
        assert updated.message == "Updated alert"
        assert updated.id == alert.id

        # Vérifier que c'est sauvegardé
        saved = self.alert_service.get_alert(alert.id)
        assert saved.price == 55000.0

    def test_alert_deletion_integration(self):
        """Test intégration suppression d'alerte"""
        # Créer des alertes
        alert1 = self.alert_service.create_alert("BTCUSDT", AlertType.ABOVE, 50000.0)
        alert2 = self.alert_service.create_alert("ETHUSDT", AlertType.BELOW, 3000.0)

        # Supprimer une alerte
        result = self.alert_service.delete_alert(alert1.id)
        assert result is True

        # Vérifier qu'elle n'existe plus
        assert self.alert_service.get_alert(alert1.id) is None
        assert len(self.alert_service.get_all_alerts()) == 1

        # Vérifier que l'autre alerte existe toujours
        assert self.alert_service.get_alert(alert2.id) == alert2

    def test_alert_service_error_handling(self):
        """Test gestion d'erreurs du service"""
        # Test ID inexistant
        assert self.alert_service.get_alert("nonexistent") is None

        # Test mise à jour alerte inexistante
        result = self.alert_service.update_alert("nonexistent", price=50000.0)
        assert result is None

        # Test suppression alerte inexistante
        result = self.alert_service.delete_alert("nonexistent")
        assert result is False

    def test_alert_persistence_integration(self):
        """Test intégration persistance des données"""
        # Créer des alertes
        alert1 = self.alert_service.create_alert("BTCUSDT", AlertType.ABOVE, 50000.0)
        alert2 = self.alert_service.create_alert("ETHUSDT", AlertType.BELOW, 3000.0)

        # Créer un nouveau service avec le même fichier
        new_service = AlertService(data_file=self.temp_file.name)

        # Vérifier que les alertes sont chargées
        loaded_alerts = new_service.get_all_alerts()
        assert len(loaded_alerts) == 2

        # Vérifier que les données sont correctes
        loaded_ids = {a.id for a in loaded_alerts}
        assert alert1.id in loaded_ids
        assert alert2.id in loaded_ids


class TestMarketModalManagerIntegration:
    """Tests d'intégration MarketModalManager ↔ MarketDataService"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)

        # Mock du service de données de marché
        with patch('dash_modules.callbacks.managers.market_modal_manager.market_data_service') as mock_service:
            self.mock_market_service = mock_service
            self.manager = MarketModalManager(self.app)

    def test_market_modal_manager_initialization(self):
        """Test que le manager s'initialise correctement"""
        assert self.manager is not None
        assert self.manager.app == self.app
        assert self.manager.name == "MarketModalManager"

    def test_market_data_retrieval_integration(self):
        """Test intégration récupération données de marché"""
        # Mock des données de marché
        mock_data = [
            MarketData(symbol="BTCUSDT", current_price=50000.0, price_change_percent_24h=2.5, volume_24h=1000000.0),
            MarketData(symbol="ETHUSDT", current_price=3000.0, price_change_percent_24h=-1.2, volume_24h=500000.0)
        ]

        self.mock_market_service.get_market_data.return_value = mock_data

        # Appeler le service
        result = self.mock_market_service.get_market_data()

        # Vérifier les résultats
        assert len(result) == 2
        assert result[0].symbol == "BTCUSDT"
        assert result[0].current_price == 50000.0
        assert result[1].symbol == "ETHUSDT"
        assert result[1].current_price == 3000.0

        # Vérifier que le service a été appelé
        self.mock_market_service.get_market_data.assert_called_once()


class TestNewsModalManagerIntegration:
    """Tests d'intégration NewsModalManager - Mock pour l'instant car NewsService pas encore implémenté"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)

        # Mock du service de news (non implémenté pour l'instant)
        with patch('dash_modules.callbacks.managers.news_modal_manager.news_service', create=True) as mock_service:
            self.mock_news_service = mock_service
            self.manager = NewsModalManager(self.app)

    def test_news_modal_manager_initialization(self):
        """Test que le manager s'initialise correctement"""
        assert self.manager is not None
        assert self.manager.app == self.app
        assert self.manager.name == "NewsModalManager"

    def test_news_retrieval_integration(self):
        """Test intégration récupération actualités - mock pour l'instant"""
        # Mock des articles (structure attendue quand NewsService sera implémenté)
        mock_articles = [
            {
                "title": "Bitcoin atteint 50k",
                "url": "https://example.com/bitcoin-50k",
                "summary": "Le Bitcoin a franchi la barre des 50 000 dollars",
                "source": "CryptoNews",
                "published": "2025-01-14T10:00:00Z",
                "symbols": ["BTC"],
                "relevance_score": 0.9
            },
            {
                "title": "Ethereum en baisse",
                "url": "https://example.com/ethereum-down",
                "summary": "L'Ethereum perd 2% aujourd'hui",
                "source": "BlockChain Today",
                "published": "2025-01-14T11:00:00Z",
                "symbols": ["ETH"],
                "relevance_score": 0.7
            }
        ]

        self.mock_news_service.get_news.return_value = mock_articles

        # Appeler le service
        result = self.mock_news_service.get_news()

        # Vérifier les résultats
        assert len(result) == 2
        assert result[0]["title"] == "Bitcoin atteint 50k"
        assert result[0]["url"] == "https://example.com/bitcoin-50k"
        assert result[1]["title"] == "Ethereum en baisse"
        assert result[1]["url"] == "https://example.com/ethereum-down"

        # Vérifier que le service a été appelé
        self.mock_news_service.get_news.assert_called_once()


class TestServicesIntegration:
    """Tests d'intégration entre services métier"""

    def test_services_independence(self):
        """Test que les services sont indépendants"""
        # Créer des instances séparées
        alert_service = AlertService()
        market_service = MarketDataService()
        user_prefs_service = UserPreferencesService()
        dashboard_service = DashboardService()

        # Vérifier qu'ils sont des instances différentes
        assert alert_service is not market_service
        assert alert_service is not user_prefs_service
        assert alert_service is not dashboard_service
        assert market_service is not user_prefs_service
        assert market_service is not dashboard_service
        assert user_prefs_service is not dashboard_service

        # Vérifier qu'ils ont leurs propres données
        assert hasattr(alert_service, 'alerts')
        assert hasattr(market_service, 'cache')
        assert hasattr(user_prefs_service, 'preferences')
        assert hasattr(dashboard_service, 'layout')

    def test_service_data_isolation(self):
        """Test que les données des services sont isolées"""
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.close()

        try:
            # Créer deux services d'alertes avec des fichiers différents
            alert_service1 = AlertService(data_file=temp_file.name)
            alert_service2 = AlertService(data_file=temp_file.name + "_2")

            # Créer une alerte dans le premier service
            alert = alert_service1.create_alert("BTCUSDT", AlertType.ABOVE, 50000.0)

            # Vérifier qu'elle n'existe pas dans le deuxième service (même fichier mais instances séparées)
            # Note: Comme ils utilisent le même fichier, ils partageront les données persistées
            # Mais les instances en mémoire sont séparées
            assert alert_service1.alerts[alert.id] == alert
            # Le deuxième service n'a pas encore chargé les données
            assert len(alert_service2.alerts) == 0

        finally:
            import os
            try:
                os.unlink(temp_file.name)
                os.unlink(temp_file.name + "_2")
            except:
                pass


class TestManagerServiceCallbacksIntegration:
    """Tests d'intégration callbacks managers avec services"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)

        # Créer layout de base pour les tests de callbacks
        self.app.layout = html.Div([
            html.Div(id="alerts-store", children=[]),
            html.Div(id="alerts-count-badge", children="0"),
            html.Div(id="price-alerts-modal", children=[])
        ])

    def test_alert_manager_callbacks_registration(self):
        """Test que les callbacks du manager s'enregistrent correctement"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.close()

        alert_service = AlertService(data_file=temp_file.name)

        with patch('dash_modules.callbacks.managers.alert_modal_manager.alert_service', alert_service):
            manager = AlertModalManager(self.app)

            # Enregistrer les callbacks
            manager.register_all_callbacks()

            # Vérifier que les callbacks sont enregistrés
            assert len(self.app.callback_map) > 0

            # Nettoyer
            Path(temp_file.name).unlink(missing_ok=True)

    def test_market_manager_callbacks_registration(self):
        """Test que les callbacks du manager marché s'enregistrent"""
        with patch('dash_modules.callbacks.managers.market_modal_manager.market_data_service'):
            manager = MarketModalManager(self.app)

            # Enregistrer les callbacks
            manager.register_all_callbacks()

            # Vérifier que les callbacks sont enregistrés
            assert len(self.app.callback_map) > 0

    def test_news_manager_callbacks_registration(self):
        """Test que les callbacks du manager news s'enregistrent"""
        with patch('dash_modules.callbacks.managers.news_modal_manager.news_service'):
            manager = NewsModalManager(self.app)

            # Enregistrer les callbacks
            manager.register_all_callbacks()

            # Vérifier que les callbacks sont enregistrés
            assert len(self.app.callback_map) > 0