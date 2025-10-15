"""
Tests pour le composant FearGreedGauge
"""

import pytest

from dash_modules.components.fear_greed_gauge import FearGreedGaugeComponent


class TestFearGreedGauge:
    """Tests pour FearGreedGaugeComponent"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.gauge = FearGreedGaugeComponent()

    def test_initialization(self):
        """Test initialisation du composant"""
        assert self.gauge is not None
        assert hasattr(self.gauge, 'api_url')

    def test_setup_alerts(self):
        """Test configuration des alertes"""
        alerts = self.gauge.setup_alerts(25)  # Valeur de peur extrême
        assert isinstance(alerts, list)
        assert len(alerts) > 0

        # Vérifier structure d'une alerte
        alert = alerts[0]
        assert 'level' in alert
        assert 'message' in alert
        assert 'action' in alert

    def test_create_gauge_widget(self):
        """Test création du widget gauge"""
        widget = self.gauge.create_gauge_widget("test-gauge")
        assert widget is not None
        assert hasattr(widget, 'children')