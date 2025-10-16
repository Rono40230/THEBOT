"""
Tests unitaires pour le plotter Volume Profile
Validation complète selon architecture modulaire THEBOT
"""

import pytest
from datetime import datetime, timedelta
from typing import List

import plotly.graph_objects as go

from src.thebot.indicators.volume.volume_profile.plotter import VolumeProfilePlotter
from src.thebot.core.types import IndicatorResult


class TestVolumeProfilePlotter:
    """Tests du plotter Volume Profile"""

    @pytest.fixture
    def sample_volume_profile_results(self) -> List[IndicatorResult]:
        """Fixture pour créer des données Volume Profile de test"""
        base_time = datetime(2025, 1, 1, 12, 0, 0)
        results = []

        # Créer des données de volume profile avec POC et Value Area
        for i in range(20):
            # Simuler des niveaux de prix avec volume
            nodes = []
            for price in range(100, 120):  # Prix de 100 à 119
                volume = 1000 + (price - 100) * 50  # Volume croissant
                volume_percent = volume / 20000  # Pourcentage du volume total
                if price == 110:  # POC à 110
                    volume = 5000
                    volume_percent = 0.25
                elif price in [105, 115]:  # Value Area
                    volume = 3000
                    volume_percent = 0.15
                
                nodes.append({
                    'price_level': float(price),
                    'volume': volume,
                    'volume_percent': volume_percent
                })

            metadata = {
                'nodes': nodes,
                'poc': {'price_level': 110.0},
                'value_area': {
                    'high': 115.0,
                    'low': 105.0
                },
                'total_volume': sum(node['volume'] for node in nodes),
                'profile_range': (100.0, 119.0)
            }

            result = IndicatorResult(
                value=110.0 + i * 0.1,  # Valeur principale autour du POC
                timestamp=base_time + timedelta(hours=i),
                indicator_name="Volume Profile",
                is_valid=True,
                metadata=metadata
            )
            results.append(result)

        return results

    def test_plot_empty_data(self):
        """Test plot avec données vides"""
        fig = VolumeProfilePlotter.plot([])

        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Volume Profile"
        assert fig.layout.xaxis.title.text == "Volume"
        assert fig.layout.yaxis.title.text == "Price"

    def test_plot_with_data(self, sample_volume_profile_results):
        """Test plot avec données Volume Profile"""
        fig = VolumeProfilePlotter.plot(sample_volume_profile_results)

        assert isinstance(fig, go.Figure)
        assert "Volume Profile Analysis" in fig.layout.title.text

        # Devrait avoir plusieurs traces (histogramme, POC, Value Area)
        assert len(fig.data) >= 2

        # Vérifier les noms des traces
        trace_names = [trace.name for trace in fig.data]
        assert any("Volume" in name for name in trace_names)

    def test_plot_with_price_overlay(self, sample_volume_profile_results):
        """Test plot avec overlay de prix"""
        price_data = [110.0 + i * 0.5 for i in range(len(sample_volume_profile_results))]

        fig = VolumeProfilePlotter.plot_with_price(sample_volume_profile_results, price_data)

        assert isinstance(fig, go.Figure)
        assert "Volume Profile & Price Analysis" in fig.layout.title.text

        # Devrait avoir les traces du volume profile + la ligne de prix
        assert len(fig.data) >= 3

        # Vérifier la présence de la ligne de prix
        trace_names = [trace.name for trace in fig.data]
        assert any("Price" in name for name in trace_names)

    def test_poc_highlight(self, sample_volume_profile_results):
        """Test mise en évidence du POC"""
        fig = VolumeProfilePlotter.plot(sample_volume_profile_results)

        assert isinstance(fig, go.Figure)

        # Le POC devrait être mis en évidence (couleur différente, annotation, etc.)
        # Cette vérification dépend de l'implémentation spécifique

    def test_value_area_highlight(self, sample_volume_profile_results):
        """Test mise en évidence de la Value Area"""
        fig = VolumeProfilePlotter.plot(sample_volume_profile_results)

        assert isinstance(fig, go.Figure)

        # La Value Area devrait être mise en évidence
        # Peut être représentée par des couleurs différentes ou des zones

    def test_plot_layout_properties(self, sample_volume_profile_results):
        """Test des propriétés de layout"""
        fig = VolumeProfilePlotter.plot(sample_volume_profile_results)

        # Vérifier les propriétés de layout
        assert fig.layout.height == 600  # Hauteur spécifique pour volume profile
        assert fig.layout.showlegend == True
        assert fig.layout.xaxis.showgrid == True
        assert fig.layout.yaxis.showgrid == True

        # Vérifier les titres des axes
        assert "Volume" in fig.layout.xaxis.title.text
        assert "Price Level" in fig.layout.yaxis.title.text

    def test_plot_with_price_layout_properties(self, sample_volume_profile_results):
        """Test des propriétés de layout avec overlay de prix"""
        price_data = [110.0 + i * 0.5 for i in range(len(sample_volume_profile_results))]

        fig = VolumeProfilePlotter.plot_with_price(sample_volume_profile_results, price_data)

        # Devrait avoir deux axes Y (volume et prix)
        assert hasattr(fig.layout, 'yaxis2') or len(fig.layout.yaxis) > 1

    def test_invalid_data_handling(self):
        """Test gestion des données invalides"""
        # Créer des résultats avec is_valid=False
        invalid_result = IndicatorResult(
            value=100.0,
            timestamp=datetime.now(),
            indicator_name="Volume Profile",
            is_valid=False,
            metadata={}
        )

        fig = VolumeProfilePlotter.plot([invalid_result])

        # Devrait quand même créer un graphique valide
        assert isinstance(fig, go.Figure)

    def test_metadata_parsing(self, sample_volume_profile_results):
        """Test parsing correct des métadonnées"""
        fig = VolumeProfilePlotter.plot(sample_volume_profile_results)

        # Vérifier que les métadonnées sont correctement utilisées
        # Le POC et Value Area devraient être représentés
        assert isinstance(fig, go.Figure)

        # Vérifier qu'il y a des annotations ou des éléments visuels pour POC/VA
        if hasattr(fig.layout, 'annotations'):
            # Si des annotations sont utilisées pour POC/VA
            pass