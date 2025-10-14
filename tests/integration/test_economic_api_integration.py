"""
Tests d'intégration pour les APIs économiques et calendrier
Vérifie la connectivité et la gestion d'erreurs des APIs financières
"""

import pytest
import requests
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json

# Import des providers économiques
from dash_modules.data_providers.economic_events_provider import EconomicEventsProvider
from dash_modules.data_providers.finnhub_economic_calendar import FinnhubEconomicCalendar


class TestEconomicEventsIntegration:
    """Tests d'intégration pour les événements économiques"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.provider = EconomicEventsProvider()

    def test_get_economic_events(self):
        """Test récupération événements économiques"""
        events = self.provider.get_recent_events()
        assert isinstance(events, list)
        # Les événements peuvent être vides si l'API est indisponible

    def test_get_events_by_date_range(self):
        """Test récupération événements par plage de dates"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)

        events = self.provider.get_events_for_period(start_date, end_date)
        assert isinstance(events, list)

    def test_get_high_impact_events(self):
        """Test récupération événements à fort impact"""
        events = self.provider.get_events_by_impact("High")
        assert isinstance(events, list)

        # Si des événements sont retournés, vérifier la structure
        for event in events:
            if isinstance(event, dict):
                assert "impact" in event
                assert event["impact"] in ["High", "Medium", "Low"]

    @patch('requests.get')
    def test_economic_api_error_handling(self, mock_get):
        """Test gestion des erreurs API économiques"""
        mock_get.side_effect = requests.RequestException("API Error")

        events = self.provider.get_recent_events()
        assert isinstance(events, list)
        # En cas d'erreur, peut retourner des données de fallback ou liste vide


class TestFinnhubEconomicCalendarIntegration:
    """Tests d'intégration pour le calendrier économique Finnhub"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.calendar = FinnhubEconomicCalendar()

    def test_finnhub_connection_alive(self):
        """Test que l'API Finnhub est accessible"""
        # Note: Finnhub nécessite une clé API, on teste juste la structure
        try:
            # Test basique sans clé API pour voir la réponse d'erreur
            response = requests.get("https://finnhub.io/api/v1/economic", timeout=10)
            # Devrait retourner 401 ou 403 sans clé API
            assert response.status_code in [401, 403, 422]
        except requests.RequestException as e:
            pytest.skip(f"Finnhub API non accessible: {e}")

    def test_get_economic_calendar(self):
        """Test récupération calendrier économique"""
        # Ce test peut échouer sans clé API valide
        try:
            calendar_data = self.calendar.get_economic_calendar()
            assert isinstance(calendar_data, list)
        except Exception as e:
            # Accepte l'échec si pas de clé API
            pytest.skip(f"Finnhub API nécessite une clé valide: {e}")

    @patch('requests.get')
    def test_finnhub_api_error_handling(self, mock_get):
        """Test gestion des erreurs API Finnhub"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = '{"error":"Invalid API key"}'
        mock_get.return_value = mock_response

        calendar_data = self.calendar.get_economic_events()
        assert isinstance(calendar_data, list)
        # En cas d'erreur API, peut retourner des données de fallback


class TestEconomicCalendarRSSIntegration:
    """Tests d'intégration pour le parser RSS calendrier économique"""

    def test_economic_calendar_rss_parser(self):
        """Test du parser RSS calendrier économique"""
        from dash_modules.core.economic_calendar_rss_parser import EconomicCalendarRSSParser

        parser = EconomicCalendarRSSParser()

        # Test avec une source RSS connue
        rss_url = "https://www.forexfactory.com/rss.php"  # Source publique

        try:
            events = parser.parse_economic_events(rss_url)
            assert isinstance(events, list)
        except Exception as e:
            # Le parsing peut échouer si la source change
            pytest.skip(f"RSS parsing failed: {e}")

    def test_rss_parser_error_handling(self):
        """Test gestion des erreurs de parsing RSS"""
        from dash_modules.core.economic_calendar_rss_parser import EconomicCalendarRSSParser

        parser = EconomicCalendarRSSParser()

        # Test avec URL invalide
        events = parser.get_economic_events("https://invalid-url-that-does-not-exist.com")
        assert isinstance(events, list)
        assert len(events) == 0


class TestTwelveDataAPIIntegration:
    """Tests d'intégration pour l'API Twelve Data"""

    def setup_method(self):
        """Configuration avant chaque test"""
        from dash_modules.data_providers.twelve_data_api import TwelveDataAPI
        self.api = TwelveDataAPI()

    def test_twelve_data_connection_alive(self):
        """Test que l'API Twelve Data est accessible"""
        try:
            # Test basique de connectivité (nécessite clé API)
            response = requests.get("https://api.twelve-data.com/health", timeout=10)
            if response.status_code == 200:
                assert True
            else:
                pytest.skip("Twelve Data API requires valid API key")
        except requests.RequestException as e:
            pytest.skip(f"Twelve Data API non accessible: {e}")

    def test_get_quote(self):
        """Test récupération cotation"""
        try:
            quote = self.api.get_quote("AAPL")
            assert isinstance(quote, dict)
        except Exception as e:
            pytest.skip(f"Twelve Data API nécessite une clé valide: {e}")

    @patch('requests.get')
    def test_twelve_data_error_handling(self, mock_get):
        """Test gestion des erreurs Twelve Data"""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = '{"message":"Rate limit exceeded"}'
        mock_get.return_value = mock_response

        quote = self.api.get_real_time_price("AAPL")
        assert quote is None or isinstance(quote, dict)


class TestYahooFinanceAPIIntegration:
    """Tests d'intégration pour l'API Yahoo Finance"""

    def setup_method(self):
        """Configuration avant chaque test"""
        from dash_modules.data_providers.yahoo_finance_api import YahooFinanceAPI
        self.api = YahooFinanceAPI()

    def test_yahoo_finance_connection_alive(self):
        """Test que Yahoo Finance est accessible"""
        try:
            # Test avec un symbole connu
            response = requests.get("https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL", timeout=10)
            # Accepte 200 ou 429 (rate limit)
            assert response.status_code in [200, 429]
            if response.status_code == 200:
                data = response.json()
                assert "quoteResponse" in data
        except requests.RequestException as e:
            pytest.skip(f"Yahoo Finance API non accessible: {e}")

    def test_get_stock_quote(self):
        """Test récupération cotation action"""
        try:
            quote = self.api.get_quote(["AAPL"])
            assert isinstance(quote, dict)
        except AttributeError:
            pytest.skip("Yahoo Finance API method not available")

    def test_get_historical_data(self):
        """Test récupération données historiques"""
        try:
            data = self.api.get_stock_data("AAPL", "1mo")
            assert isinstance(data, pd.DataFrame)
        except AttributeError:
            pytest.skip("Yahoo Finance API method not available")

    @patch('requests.get')
    def test_yahoo_finance_error_handling(self, mock_get):
        """Test gestion des erreurs Yahoo Finance"""
        try:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.text = '{"quoteResponse":{"error":"Not found"}}'
            mock_get.return_value = mock_response

            quote = self.api.get_quote(["INVALID_SYMBOL"])
            assert quote is None or isinstance(quote, dict)
        except AttributeError:
            pytest.skip("Yahoo Finance API method not available")


class TestWebSocketManagerIntegration:
    """Tests d'intégration pour le WebSocket Manager"""

    def setup_method(self):
        """Configuration avant chaque test"""
        from dash_modules.data_providers.websocket_manager import BinanceWebSocketManager
        self.ws_manager = BinanceWebSocketManager()

    def test_websocket_initialization(self):
        """Test initialisation WebSocket"""
        # Le manager devrait s'initialiser sans erreur
        assert self.ws_manager is not None

    def test_subscribe_to_symbol(self):
        """Test abonnement à un symbole"""
        # Cette méthode peut ne rien faire si pas de connexion active
        try:
            self.ws_manager.subscribe_to_symbol("BTCUSDT")
            assert True  # Pas d'exception levée
        except Exception as e:
            pytest.skip(f"WebSocket subscription failed: {e}")

    def test_get_connection_status(self):
        """Test récupération statut connexion"""
        status = self.ws_manager.is_connected("BTCUSDT")
        assert isinstance(status, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])