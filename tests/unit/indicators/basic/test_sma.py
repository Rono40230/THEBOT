"""
Tests unitaires pour le plotter SMA
Validation complète selon architecture modulaire THEBOT
"""

import pytest
from datetime import datetime, timedelta
from typing import List

import plotly.graph_objects as go

from src.thebot.indicators.basic.sma.plotter import SMAPlotter
from src.thebot.core.types import IndicatorResult


class TestSMAPlotter:
    """Tests du plotter SMA"""

    @pytest.fixture
    def sample_sma_results(self) -> List[IndicatorResult]:
        """Fixture pour créer des données SMA de test"""
        base_time = datetime(2025, 1, 1, 12, 0, 0)
        results = []

        # Créer 10 points SMA
        for i in range(10):
            result = IndicatorResult(
                value=100.0 + i * 2.0,  # SMA values: 100, 102, 104, ...
                timestamp=base_time + timedelta(hours=i),
                indicator_name="SMA",
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
        fig = SMAPlotter.plot([])

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "SMA Indicator"
        assert fig.layout.xaxis.title.text == "Time"
        assert fig.layout.yaxis.title.text == "SMA Value"

    def test_plot_with_data(self, sample_sma_results):
        """Test plot avec données SMA"""
        fig = SMAPlotter.plot(sample_sma_results)

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Simple Moving Average (SMA)"

        # Vérifier qu'il y a une trace (la ligne SMA)
        assert len(fig.data) == 1
        trace = fig.data[0]
        assert trace.name == "SMA"
        assert trace.mode == "lines"
        assert len(trace.x) == 10  # 10 points
        assert len(trace.y) == 10  # 10 valeurs

        # Vérifier les valeurs
        assert trace.y[0] == 100.0
        assert trace.y[-1] == 118.0  # 100 + 9*2

    def test_plot_with_price_empty_price_data(self, sample_sma_results):
        """Test plot_with_price avec données de prix vides"""
        fig = SMAPlotter.plot_with_price(sample_sma_results, None)

        # Devrait retourner la même figure que plot()
        assert len(fig.data) == 1
        assert fig.data[0].name == "SMA"

    def test_plot_with_price_mismatched_lengths(self, sample_sma_results):
        """Test plot_with_price avec longueurs différentes"""
        short_price_data = [100.0, 102.0]  # Seulement 2 points au lieu de 10

        fig = SMAPlotter.plot_with_price(sample_sma_results, short_price_data)

        # Ne devrait pas ajouter la ligne de prix si longueurs différentes
        assert len(fig.data) == 1
        assert fig.data[0].name == "SMA"

    def test_plot_with_price_matching_lengths(self, sample_sma_results, sample_price_data):
        """Test plot_with_price avec longueurs correspondantes"""
        fig = SMAPlotter.plot_with_price(sample_sma_results, sample_price_data)

        # Devrait avoir 2 traces: SMA et Price
        assert len(fig.data) == 2
        assert fig.data[0].name == "SMA"
        assert fig.data[1].name == "Price"

        # Vérifier la ligne de prix
        price_trace = fig.data[1]
        assert price_trace.mode == "lines"
        assert len(price_trace.y) == 10
        assert price_trace.y[0] == 98.0
        assert price_trace.y[-1] == 117.0

    def test_plot_layout_properties(self, sample_sma_results):
        """Test des propriétés de layout"""
        fig = SMAPlotter.plot(sample_sma_results)

        # Vérifier les propriétés de layout
        assert fig.layout.height == 400
        assert fig.layout.showlegend == True
        assert fig.layout.xaxis.showgrid == True
        assert fig.layout.yaxis.showgrid == True

        # Vérifier la légende
        legend = fig.layout.legend
        assert legend.orientation == "h"
        assert legend.yanchor == "bottom"
        assert legend.y == 1.02

    def test_plot_with_price_layout_properties(self, sample_sma_results, sample_price_data):
        """Test des propriétés de layout avec prix"""
        fig = SMAPlotter.plot_with_price(sample_sma_results, sample_price_data)

        # Même propriétés de base
        assert fig.layout.height == 400
        assert fig.layout.showlegend == True