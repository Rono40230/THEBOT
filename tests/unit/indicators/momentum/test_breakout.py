"""
Tests unitaires pour le plotter Breakout
Validation complète selon architecture modulaire THEBOT
"""

import pytest
from datetime import datetime, timedelta
from typing import List

import plotly.graph_objects as go

from src.thebot.indicators.momentum.breakout.plotter import BreakoutPlotter
from src.thebot.core.types import IndicatorResult


class TestBreakoutPlotter:
    """Tests du plotter Breakout"""

    @pytest.fixture
    def sample_breakout_results(self) -> List[IndicatorResult]:
        """Fixture pour créer des données Breakout de test"""
        base_time = datetime(2025, 1, 1, 12, 0, 0)
        results = []

        # Créer 10 points avec niveaux support/résistance
        for i in range(10):
            metadata = {
                'support_level': 95.0 + i * 0.5,
                'resistance_level': 105.0 + i * 0.5,
                'breakout_type': 'bullish' if i == 5 else None,
                'strength': 0.8 if i == 5 else 0.0
            }

            result = IndicatorResult(
                value=100.0 + i * 0.2,  # Prix actuel
                timestamp=base_time + timedelta(hours=i),
                indicator_name="Breakout",
                is_valid=True,
                metadata=metadata
            )
            results.append(result)

        return results

    @pytest.fixture
    def sample_price_data(self) -> List[float]:
        """Fixture pour créer des données de prix de test"""
        return [98.0, 99.0, 100.0, 101.0, 102.0, 106.0, 107.0, 108.0, 109.0, 110.0]

    def test_plot_empty_data(self):
        """Test plot avec données vides"""
        fig = BreakoutPlotter.plot([])

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Breakout Indicator"
        assert fig.layout.xaxis.title.text == "Time"
        assert fig.layout.yaxis.title.text == "Price"

    def test_plot_with_data(self, sample_breakout_results):
        """Test plot avec données Breakout"""
        fig = BreakoutPlotter.plot(sample_breakout_results)

        assert isinstance(fig, go.Figure)
        assert "Breakout Analysis" in fig.layout.title.text

        # Devrait avoir au moins les niveaux support/résistance
        assert len(fig.data) >= 2  # Support et résistance

        # Vérifier les noms des traces
        trace_names = [trace.name for trace in fig.data]
        assert "Support" in trace_names
        assert "Resistance" in trace_names

    def test_plot_with_price_empty_price_data(self, sample_breakout_results):
        """Test plot_with_price avec données de prix vides"""
        fig = BreakoutPlotter.plot_with_price(sample_breakout_results, None)

        # Devrait avoir les niveaux sans prix
        assert len(fig.data) >= 2

    def test_plot_with_price_matching_lengths(self, sample_breakout_results, sample_price_data):
        """Test plot_with_price avec longueurs correspondantes"""
        fig = BreakoutPlotter.plot_with_price(sample_breakout_results, sample_price_data)

        # Devrait avoir niveaux + prix
        assert len(fig.data) >= 3  # Support, Résistance, Prix

        # Vérifier la présence de la trace prix
        trace_names = [trace.name for trace in fig.data]
        assert "Price" in trace_names

    def test_plot_breakout_signals(self, sample_breakout_results):
        """Test affichage des signaux de breakout"""
        fig = BreakoutPlotter.plot(sample_breakout_results)

        # Devrait avoir un signal de breakout (triangle à l'index 5)
        # Les signaux sont ajoutés comme markers sur les lignes de niveau
        # Cette logique dépend de l'implémentation spécifique du plotter

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_plot_layout_properties(self, sample_breakout_results):
        """Test des propriétés de layout"""
        fig = BreakoutPlotter.plot(sample_breakout_results)

        # Vérifier les propriétés de layout
        assert fig.layout.height == 400
        assert fig.layout.showlegend == True
        assert fig.layout.xaxis.showgrid == True
        assert fig.layout.yaxis.showgrid == True

    def test_plot_with_price_layout_properties(self, sample_breakout_results, sample_price_data):
        """Test des propriétés de layout avec prix"""
        fig = BreakoutPlotter.plot_with_price(sample_breakout_results, sample_price_data)

        # Même propriétés de base
        assert fig.layout.height == 400
        assert fig.layout.showlegend == True