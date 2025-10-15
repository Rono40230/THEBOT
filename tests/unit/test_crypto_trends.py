"""
Tests pour le composant CryptoTrends
"""

import pytest

from dash_modules.components.crypto_trends import CryptoTrendsComponent


class TestCryptoTrendsComponent:
    """Tests pour CryptoTrendsComponent"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.component = CryptoTrendsComponent()

    def test_initialization(self):
        """Test initialisation du composant"""
        assert self.component is not None
        assert hasattr(self.component, 'cache_duration')
        assert hasattr(self.component, 'last_update')
        assert hasattr(self.component, 'cache')
        assert self.component.cache_duration == 60

    def test_create_trends_widget(self):
        """Test création du widget de tendances"""
        widget = self.component.create_trends_widget("test-widget")
        assert widget is not None
        # Vérifier que c'est un élément Dash
        assert hasattr(widget, 'children')

    def test_calculate_sentiment(self):
        """Test calcul du sentiment"""
        market_summary = {'avg_change': 2.1, 'total_volume': 50000}
        sentiment = self.component._calculate_sentiment(market_summary)
        assert isinstance(sentiment, str)

    def test_analyze_volume_trend(self):
        """Test analyse tendance volume"""
        market_summary = {'total_volume': 50000, 'avg_volume': 45000}
        trend = self.component._analyze_volume_trend(market_summary)
        assert isinstance(trend, str)