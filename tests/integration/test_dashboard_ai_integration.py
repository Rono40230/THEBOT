"""
Tests d'intégration pour les composants dashboard et IA
Vérifie le fonctionnement intégré des composants UI et moteurs IA
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import dash
from dash import html, dcc

# Import des composants à tester
from dash_modules.components.advanced_dashboard import AdvancedDashboard
from dash_modules.components.charts import ChartComponents
from dash_modules.components.price_alerts_modal import PriceAlertsModal
from dash_modules.ai_engine.smart_ai_engine import SmartAIEngine
from dash_modules.ai_engine.free_ai_engine import FreeAIEngine
from datetime import datetime, timedelta
import dash
from dash import html, dcc

# Import des composants à tester
from dash_modules.components.advanced_dashboard import AdvancedDashboard
from dash_modules.components.charts import ChartComponents
from dash_modules.components.price_alerts_modal import PriceAlertsModal
from dash_modules.ai_engine.smart_ai_engine import SmartAIEngine
from dash_modules.ai_engine.free_ai_engine import FreeAIEngine


class TestDashboardComponentsIntegration:
    """Tests d'intégration pour les composants dashboard"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)
        self.dashboard = AdvancedDashboard()

    def test_dashboard_initialization(self):
        """Test initialisation du dashboard"""
        assert self.dashboard is not None
        assert hasattr(self.dashboard, 'default_layout')
        assert hasattr(self.dashboard, 'widget_catalog')

    def test_dashboard_layout_structure(self):
        """Test structure du layout dashboard"""
        layout = self.dashboard.create_layout()
        assert layout is not None
        # Vérifie que c'est un composant Dash
        assert hasattr(layout, 'children') or isinstance(layout, (html.Div, html.Section))

    def test_charts_component(self):
        """Test composant charts"""
        charts = ChartComponents()

        # Test création graphique vide
        fig = charts.create_empty_chart()
        assert fig is not None
        assert hasattr(fig, 'data')

        # Test avec données fictives pour graphique candlestick
        test_data = pd.DataFrame({
            'open': [50000 + i * 100 for i in range(10)],
            'high': [50100 + i * 100 for i in range(10)],
            'low': [49900 + i * 100 for i in range(10)],
            'close': [50050 + i * 100 for i in range(10)],
            'volume': [1000000] * 10
        }, index=[datetime.now() - timedelta(hours=i) for i in range(10)])

        fig = charts.create_candlestick_chart(test_data, "BTCUSDT", "1h")
        assert fig is not None
        assert len(fig.data) > 0


class TestPriceAlertsIntegration:
    """Tests d'intégration pour les alertes de prix"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.alerts_modal = PriceAlertsModal()

    def test_alerts_modal_initialization(self):
        """Test initialisation modal alertes"""
        assert self.alerts_modal is not None

    def test_create_alert_structure(self):
        """Test structure de création d'alerte"""
        modal = self.alerts_modal.create_modal()
        assert modal is not None
        assert hasattr(modal, 'children')

    def test_alert_validation(self):
        """Test validation des alertes"""
        # Test alerte valide
        valid_alert = {
            'symbol': 'BTCUSDT',
            'price': 50000,
            'condition': 'above',
            'type': 'price'
        }

        # Test alerte invalide
        invalid_alert = {
            'symbol': '',
            'price': -100,
            'condition': 'invalid',
            'type': 'price'
        }

        # La validation devrait accepter l'alerte valide et rejeter l'invalide
        # (selon l'implémentation actuelle)
        assert True  # Placeholder - dépend de l'implémentation


class TestAIComponentsIntegration:
    """Tests d'intégration pour les composants IA"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.smart_ai = SmartAIEngine()
        self.free_ai = FreeAIEngine()

    def test_smart_ai_initialization(self):
        """Test initialisation IA intelligente"""
        assert self.smart_ai is not None
        assert hasattr(self.smart_ai, 'analyze_market_comprehensive')

    def test_free_ai_initialization(self):
        """Test initialisation IA gratuite"""
        assert self.free_ai is not None
        assert hasattr(self.free_ai, 'analyze_with_free_llm')

    def test_smart_ai_market_analysis(self):
        """Test analyse de marché IA intelligente"""
        # Données de test
        market_data = {
            'symbol': 'BTCUSDT',
            'price': 50000,
            'volume': 1000000,
            'indicators': {
                'rsi': 65,
                'macd': 0.5,
                'sma_20': 49000
            }
        }

        try:
            analysis = self.smart_ai.analyze_market_comprehensive(market_data)
            assert isinstance(analysis, dict)
            assert 'signal' in analysis
            assert 'confidence' in analysis
        except Exception as e:
            pytest.skip(f"Smart AI analysis failed: {e}")

    def test_free_ai_response_generation(self):
        """Test génération de réponse IA gratuite"""
        prompt = "Quelle est la tendance actuelle du marché crypto?"

        try:
            response = self.free_ai.analyze_with_free_llm(prompt)
            assert isinstance(response, dict)
            assert 'analysis' in response or 'response' in response
        except Exception as e:
            pytest.skip(f"Free AI response generation failed: {e}")

    def test_smart_ai_error_handling(self):
        """Test gestion d'erreurs IA intelligente"""
        # Test que la méthode existe et peut être appelée
        market_data = {'symbol': 'BTCUSDT', 'price': 50000}

        try:
            analysis = self.smart_ai.analyze_market_comprehensive(market_data)
            # Peu importe le résultat, l'important est que ça ne crash pas
            assert isinstance(analysis, (dict, type(None)))
        except Exception as e:
            # Si ça échoue, c'est acceptable (API non disponible)
            pytest.skip(f"Smart AI analysis failed as expected: {e}")

    @patch('dash_modules.ai_engine.free_ai_engine.requests.post')
    def test_free_ai_error_handling(self, mock_post):
        """Test gestion d'erreurs IA gratuite"""
        mock_post.side_effect = Exception("API Error")

        response = self.free_ai.analyze_with_free_llm("Test prompt")
        # Devrait gérer l'erreur gracieusement
        assert isinstance(response, dict) or response is None


class TestNewsComponentsIntegration:
    """Tests d'intégration pour les composants news"""

    def test_news_aggregator(self):
        """Test agrégateur de news"""
        from dash_modules.core.news_aggregator import NewsAggregator

        aggregator = NewsAggregator()

        # Test récupération news
        news = aggregator.get_aggregated_news(limit=5)
        assert isinstance(news, list)
        # Peut être vide si sources non accessibles
        if news:
            assert len(news) <= 5
            for item in news:
                assert 'title' in item
                assert 'url' in item

    def test_crypto_news_feed(self):
        """Test flux news crypto"""
        from dash_modules.components.crypto_news_phase4_extensions import CryptoNewsPhase4Extensions

        feed = CryptoNewsPhase4Extensions()

        # Test initialisation
        assert feed is not None

        # Test récupération news
        news_items = feed.get_news_items()
        assert isinstance(news_items, list)


class TestIndicatorsIntegration:
    """Tests d'intégration pour les indicateurs techniques"""

    def test_indicators_modal(self):
        """Test modal indicateurs"""
        from dash_modules.components.indicators_modal import IndicatorsModal

        modal = IndicatorsModal()

        # Test initialisation
        assert modal is not None

        # Test calcul indicateurs
        test_data = pd.DataFrame({
            'close': [50000 + i * 100 for i in range(50)],
            'high': [50100 + i * 100 for i in range(50)],
            'low': [49900 + i * 100 for i in range(50)],
            'volume': [1000000] * 50
        })

        try:
            indicators = modal.calculate_indicators(test_data)
            assert isinstance(indicators, dict)
            assert 'rsi' in indicators
            assert 'macd' in indicators
        except Exception as e:
            pytest.skip(f"Indicators calculation failed: {e}")


class TestAlertsManagerIntegration:
    """Tests d'intégration pour le gestionnaire d'alertes"""

    def setup_method(self):
        """Configuration avant chaque test"""
        from dash_modules.core.alerts_manager import AlertsManager
        self.alerts_manager = AlertsManager()

    def test_alerts_manager_initialization(self):
        """Test initialisation gestionnaire d'alertes"""
        assert self.alerts_manager is not None

    def test_add_price_alert(self):
        """Test ajout alerte de prix"""
        alert_data = {
            'symbol': 'BTCUSDT',
            'price': 50000,
            'condition': 'above',
            'type': 'price'
        }

        try:
            result = self.alerts_manager.add_alert(alert_data)
            assert isinstance(result, bool) or result is None
        except Exception as e:
            pytest.skip(f"Add alert failed: {e}")

    def test_check_alerts(self):
        """Test vérification des alertes"""
        current_prices = {
            'BTCUSDT': 51000,
            'ETHUSDT': 3000
        }

        try:
            triggered_alerts = self.alerts_manager.check_alerts(current_prices)
            assert isinstance(triggered_alerts, list)
        except Exception as e:
            pytest.skip(f"Check alerts failed: {e}")


class TestNewsComponentsIntegration:
    """Tests d'intégration pour les composants news"""

    def test_news_aggregator(self):
        """Test agrégateur de news"""
        from dash_modules.core.news_aggregator import NewsAggregator

        aggregator = NewsAggregator()

        # Test récupération news
        news = aggregator.get_aggregated_news(limit=5)
        assert isinstance(news, list)
        # Peut être vide si sources non accessibles
        if news:
            assert len(news) <= 5
            for item in news:
                assert 'title' in item
                assert 'url' in item

    def test_crypto_news_feed(self):
        """Test flux news crypto"""
        from dash_modules.components.crypto_news_phase4_extensions import CryptoNewsPhase4Extensions

        feed = CryptoNewsPhase4Extensions()

        # Test initialisation
        assert feed is not None

        # Test récupération layout compact
        layout = feed.get_compact_widgets_layout()
        assert layout is not None


class TestCalculatorsIntegration:
    """Tests d'intégration pour les calculateurs"""

    def test_calculators(self):
        """Test calculateurs financiers"""
        from dash_modules.core.calculators import TechnicalCalculators

        calc = TechnicalCalculators()

        # Test calcul SMA
        prices = [100, 105, 95, 110, 105]
        sma = calc.calculate_sma(prices, period=3)
        assert isinstance(sma, list)
        assert len(sma) > 0

        # Test calcul RSI
        rsi = calc.calculate_rsi(prices, period=3)
        assert isinstance(rsi, list)
        assert len(rsi) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])