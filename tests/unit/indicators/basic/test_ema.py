"""
Tests unitaires pour le plotter EMA
Validation complète selon architecture modulaire THEBOT
"""

import pytest
from datetime import datetime, timedelta
from typing import List

import plotly.graph_objects as go

from src.thebot.indicators.basic.ema.plotter import EMAPlotter
from src.thebot.core.types import IndicatorResult


class TestEMAPlotter:
    """Tests du plotter EMA"""

    @pytest.fixture
    def sample_ema_results(self) -> List[IndicatorResult]:
        """Fixture pour créer des données EMA de test"""
        base_time = datetime(2025, 1, 1, 12, 0, 0)
        results = []

        # Créer 10 points EMA
        for i in range(10):
            result = IndicatorResult(
                value=100.0 + i * 1.5,  # EMA values: 100, 101.5, 103, ...
                timestamp=base_time + timedelta(hours=i),
                indicator_name="EMA",
                is_valid=True,
                metadata={"period": 20}
            )
            results.append(result)

        return results

    @pytest.fixture
    def sample_price_data(self) -> List[float]:
        """Fixture pour créer des données de prix de test"""
        return [98.0, 101.0, 103.0, 105.0, 107.0, 109.0, 111.0, 113.0, 115.0, 117.0]

    def test_plot_empty_data(self):
        """Test plot avec données vides"""
        fig = EMAPlotter.plot([])

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "EMA Indicator"
        assert fig.layout.xaxis.title.text == "Time"
        assert fig.layout.yaxis.title.text == "EMA Value"

    def test_plot_with_data(self, sample_ema_results):
        """Test plot avec données EMA"""
        fig = EMAPlotter.plot(sample_ema_results)

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Exponential Moving Average (EMA)"

        # Vérifier qu'il y a une trace (la ligne EMA)
        assert len(fig.data) == 1
        trace = fig.data[0]
        assert trace.name == "EMA"
        assert trace.mode == "lines"
        assert len(trace.x) == 10  # 10 points
        assert len(trace.y) == 10  # 10 valeurs

        # Vérifier les valeurs
        assert trace.y[0] == 100.0
        assert trace.y[-1] == 113.5  # Valeur calculée selon l'algorithme EMA

    def test_plot_dual_ema(self, sample_ema_results):
        """Test plot_dual_ema avec données EMA"""
        # Créer des données pour EMA rapide et lente
        fast_ema = sample_ema_results
        slow_ema = [
            IndicatorResult(
                value=result.value - 5.0,  # EMA lente légèrement plus basse
                timestamp=result.timestamp,
                indicator_name="EMA_Slow",
                is_valid=True,
                metadata={"period": 50}
            )
            for result in sample_ema_results
        ]

        fig = EMAPlotter.plot_dual_ema(fast_ema, slow_ema)

        assert isinstance(fig, go.Figure)
        assert "EMA Crossover" in fig.layout.title.text

        # Devrait avoir 2 traces: Fast EMA et Slow EMA
        assert len(fig.data) == 2
        assert fig.data[0].name == "Fast EMA"
        assert fig.data[1].name == "Slow EMA"

    def test_plot_dual_ema_empty_data(self):
        """Test plot_dual_ema avec données vides"""
        fig = EMAPlotter.plot_dual_ema([], [])

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 0

    def test_plot_with_price_empty_price_data(self, sample_ema_results):
        """Test plot_with_price avec données de prix vides"""
        fig = EMAPlotter.plot_with_price(sample_ema_results, None)

        # Devrait retourner la même figure que plot()
        assert len(fig.data) == 1
        assert fig.data[0].name == "EMA"

    def test_plot_with_price_matching_lengths(self, sample_ema_results, sample_price_data):
        """Test plot_with_price avec longueurs correspondantes"""
        fig = EMAPlotter.plot_with_price(sample_ema_results, sample_price_data)

        # Devrait avoir 2 traces: EMA et Price
        assert len(fig.data) == 2
        assert fig.data[0].name == "EMA"
        assert fig.data[1].name == "Price"

        # Vérifier la ligne de prix
        price_trace = fig.data[1]
        assert price_trace.mode == "lines"
        assert len(price_trace.y) == 10

    def test_plot_layout_properties(self, sample_ema_results):
        """Test des propriétés de layout"""
        fig = EMAPlotter.plot(sample_ema_results)

        # Vérifier les propriétés de layout
        assert fig.layout.height == 400
        assert fig.layout.showlegend == True
        assert fig.layout.xaxis.showgrid == True
        assert fig.layout.yaxis.showgrid == True