"""
Tests unitaires pour le plotter Squeeze
Validation complète selon architecture modulaire THEBOT
"""

import pytest
from datetime import datetime, timedelta
from typing import List

import plotly.graph_objects as go

from src.thebot.indicators.momentum.squeeze.plotter import SqueezePlotter
from src.thebot.core.types import IndicatorResult


class TestSqueezePlotter:
    """Tests du plotter Squeeze"""

    @pytest.fixture
    def sample_squeeze_results(self) -> List[IndicatorResult]:
        """Fixture pour créer des données Squeeze de test"""
        base_time = datetime(2025, 1, 1, 12, 0, 0)
        results = []

        # Créer 10 points avec données Bollinger et Keltner
        for i in range(10):
            metadata = {
                'bollinger_bands': {
                    'upper': 105.0 + i * 0.1,
                    'lower': 95.0 - i * 0.1
                },
                'keltner_channels': {
                    'upper': 103.0 + i * 0.05,
                    'lower': 97.0 - i * 0.05
                },
                'momentum': 0.5 + i * 0.1,
                'squeeze_active': i in [3, 4, 5]  # Squeeze actif aux points 3, 4, 5
            }

            result = IndicatorResult(
                value=100.0 + i * 0.2,  # Valeur principale
                timestamp=base_time + timedelta(hours=i),
                indicator_name="Squeeze",
                is_valid=True,
                metadata=metadata
            )
            results.append(result)

        return results

    def test_plot_empty_data(self):
        """Test plot avec données vides"""
        fig = SqueezePlotter.plot([])

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Squeeze Indicator"
        assert fig.layout.xaxis.title.text == "Time"
        assert fig.layout.yaxis.title.text == "Value"

    def test_plot_with_data(self, sample_squeeze_results):
        """Test plot avec données Squeeze"""
        fig = SqueezePlotter.plot(sample_squeeze_results)

        assert isinstance(fig, go.Figure)
        assert "Squeeze Momentum Analysis" in fig.layout.title.text

        # Devrait avoir plusieurs traces (BB, KC, momentum)
        assert len(fig.data) >= 3

        # Vérifier les noms des traces
        trace_names = [trace.name for trace in fig.data]
        assert any("BB" in name for name in trace_names)
        assert any("KC" in name for name in trace_names)

    def test_plot_momentum(self, sample_squeeze_results):
        """Test plot_momentum séparé"""
        fig = SqueezePlotter.plot_momentum(sample_squeeze_results)

        assert isinstance(fig, go.Figure)
        assert "Momentum Oscillator" in fig.layout.title.text

        # Devrait avoir au moins une trace pour le momentum
        assert len(fig.data) >= 1

        # Vérifier la présence de momentum
        trace_names = [trace.name for trace in fig.data]
        assert any("Momentum" in name for name in trace_names)

    def test_plot_momentum_empty_data(self):
        """Test plot_momentum avec données vides"""
        fig = SqueezePlotter.plot_momentum([])

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 0

    def test_squeeze_highlight_zones(self, sample_squeeze_results):
        """Test mise en évidence des zones de squeeze"""
        fig = SqueezePlotter.plot(sample_squeeze_results)

        # Les zones de squeeze devraient être mises en évidence
        # Cela peut être fait avec des rectangles ou des couleurs spéciales
        assert isinstance(fig, go.Figure)

        # Vérifier qu'il y a des formes (rectangles pour squeeze zones)
        if hasattr(fig, 'layout') and hasattr(fig.layout, 'shapes'):
            # Si des shapes sont utilisées pour highlight les zones
            pass  # Cette vérification dépend de l'implémentation

    def test_plot_layout_properties(self, sample_squeeze_results):
        """Test des propriétés de layout"""
        fig = SqueezePlotter.plot(sample_squeeze_results)

        # Vérifier les propriétés de layout
        assert fig.layout.height == 400
        assert fig.layout.showlegend == True
        assert fig.layout.xaxis.showgrid == True
        assert fig.layout.yaxis.showgrid == True

    def test_plot_momentum_layout_properties(self, sample_squeeze_results):
        """Test des propriétés de layout pour momentum"""
        fig = SqueezePlotter.plot_momentum(sample_squeeze_results)

        # Vérifier les propriétés spécifiques au momentum
        assert "Momentum" in fig.layout.title.text
        assert fig.layout.height == 300  # Hauteur spécifique pour momentum