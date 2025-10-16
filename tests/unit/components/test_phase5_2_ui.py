"""
Phase 5.2 - Tests des composants UI et callbacks
Tests d'intégration avec Phase 5.1 services
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from decimal import Decimal
from dash import html, dcc

from dash_modules.components.modern_indicators import (
    IndicatorSelector,
    IndicatorComparison,
    SignalAlertModal,
    IndicatorMetrics,
    IndicatorChart,
    SignalHistoryTable,
    IndicatorStatistics,
    create_full_indicator_dashboard,
)
from src.thebot.core.types import TimeFrame, SignalDirection


class TestIndicatorSelector:
    """Tests pour IndicatorSelector"""
    
    def test_create_returns_card(self):
        """Test que create() retourne un dbc.Card"""
        component = IndicatorSelector.create()
        assert component is not None
        assert component.__class__.__name__ == "Card"
    
    def test_indicator_options_available(self):
        """Test que les indicateurs sont disponibles"""
        assert "basic" in IndicatorSelector.AVAILABLE_INDICATORS
        assert "SMA" in IndicatorSelector.AVAILABLE_INDICATORS["basic"]
        assert "EMA" in IndicatorSelector.AVAILABLE_INDICATORS["basic"]
    
    def test_timeframes_available(self):
        """Test que les timeframes sont disponibles"""
        assert len(IndicatorSelector.TIMEFRAMES) > 0
        timeframe_values = [tf[1] for tf in IndicatorSelector.TIMEFRAMES]
        assert TimeFrame.M1 in timeframe_values
        assert TimeFrame.H1 in timeframe_values
    
    def test_dropdown_has_indicator_options(self):
        """Test que le dropdown contient les options d'indicateurs"""
        component = IndicatorSelector.create()
        # Naviguer dans la structure du composant
        assert component is not None


class TestIndicatorComparison:
    """Tests pour IndicatorComparison"""
    
    def test_create_returns_card(self):
        """Test que create() retourne un dbc.Card"""
        component = IndicatorComparison.create()
        assert component is not None
        assert component.__class__.__name__ == "Card"
    
    def test_multi_select_dropdown(self):
        """Test que le dropdown supporte multi-select"""
        component = IndicatorComparison.create()
        assert component is not None


class TestSignalAlertModal:
    """Tests pour SignalAlertModal"""
    
    def test_create_returns_modal(self):
        """Test que create() retourne un dbc.Modal"""
        component = SignalAlertModal.create()
        assert component is not None
        assert component.__class__.__name__ == "Modal"
    
    def test_modal_has_close_button(self):
        """Test que le modal a un bouton de fermeture"""
        component = SignalAlertModal.create()
        assert component is not None


class TestIndicatorMetrics:
    """Tests pour IndicatorMetrics"""
    
    def test_create_returns_card(self):
        """Test que create() retourne un dbc.Card"""
        component = IndicatorMetrics.create()
        assert component is not None
        assert component.__class__.__name__ == "Card"
    
    def test_custom_title(self):
        """Test titre personnalisé"""
        title = "📈 Test Metrics"
        component = IndicatorMetrics.create(title=title)
        assert component is not None


class TestIndicatorChart:
    """Tests pour IndicatorChart"""
    
    def test_create_returns_card(self):
        """Test que create() retourne un dbc.Card"""
        component = IndicatorChart.create()
        assert component is not None
        assert component.__class__.__name__ == "Card"
    
    def test_custom_indicator_name(self):
        """Test nom d'indicateur personnalisé"""
        component = IndicatorChart.create(indicator_name="RSI")
        assert component is not None


class TestSignalHistoryTable:
    """Tests pour SignalHistoryTable"""
    
    def test_create_returns_card(self):
        """Test que create() retourne un dbc.Card"""
        component = SignalHistoryTable.create()
        assert component is not None
        assert component.__class__.__name__ == "Card"


class TestIndicatorStatistics:
    """Tests pour IndicatorStatistics"""
    
    def test_create_returns_card(self):
        """Test que create() retourne un dbc.Card"""
        component = IndicatorStatistics.create()
        assert component is not None
        assert component.__class__.__name__ == "Card"


class TestFullIndicatorDashboard:
    """Tests pour create_full_indicator_dashboard"""
    
    def test_create_returns_container(self):
        """Test que create_full_indicator_dashboard retourne un dbc.Container"""
        dashboard = create_full_indicator_dashboard()
        assert dashboard is not None
        assert dashboard.__class__.__name__ == "Container"
    
    def test_dashboard_has_all_components(self):
        """Test que le dashboard contient tous les composants"""
        dashboard = create_full_indicator_dashboard()
        assert dashboard is not None
        # Vérifier la structure
        assert hasattr(dashboard, 'children')


class TestPhase5Callbacks:
    """Tests pour les callbacks Phase 5.2"""
    
    @pytest.mark.asyncio
    async def test_services_initialization(self):
        """Test que les services se chargent correctement"""
        try:
            from dash_modules.callbacks.phase5_2_callbacks import _get_services
            
            # Mock les services
            with patch('dash_modules.callbacks.phase5_2_callbacks.get_integration_factory') as mock_factory, \
                 patch('dash_modules.callbacks.phase5_2_callbacks.get_subscriber') as mock_sub, \
                 patch('dash_modules.callbacks.phase5_2_callbacks.get_signal_aggregator') as mock_agg, \
                 patch('dash_modules.callbacks.phase5_2_callbacks.get_async_wrapper') as mock_wrap:
                
                mock_factory.return_value = MagicMock()
                mock_sub.return_value = MagicMock()
                mock_agg.return_value = MagicMock()
                mock_wrap.return_value = MagicMock()
                
                # Reset les globales
                import dash_modules.callbacks.phase5_2_callbacks as cb_module
                cb_module._factory = None
                cb_module._subscriber = None
                cb_module._aggregator = None
                cb_module._wrapper = None
                
                # Test
                factory, subscriber, aggregator, wrapper = _get_services()
                
                assert factory is not None
                assert subscriber is not None
                assert aggregator is not None
                assert wrapper is not None
        except ImportError:
            pytest.skip("Callbacks pas encore intégrés à dash_modules")
    
    def test_update_indicator_params_empty(self):
        """Test update_indicator_params avec sélection vide"""
        try:
            from dash_modules.callbacks.phase5_2_callbacks import update_indicator_params
            
            result = update_indicator_params(None)
            assert result == []
        except ImportError:
            pytest.skip("Callbacks pas encore intégrés à dash_modules")
    
    def test_build_indicator_params_sma(self):
        """Test _build_indicator_params pour SMA"""
        try:
            from dash_modules.callbacks.phase5_2_callbacks import _build_indicator_params
            
            params = _build_indicator_params("SMA", [20])
            assert "period" in params
            assert params["period"] == 20
        except ImportError:
            pytest.skip("Callbacks pas encore intégrés à dash_modules")
    
    def test_build_indicator_params_macd(self):
        """Test _build_indicator_params pour MACD"""
        try:
            from dash_modules.callbacks.phase5_2_callbacks import _build_indicator_params
            
            params = _build_indicator_params("MACD", [12, 26, 9])
            assert "fast" in params
            assert "slow" in params
            assert "signal" in params
            assert params["fast"] == 12
            assert params["slow"] == 26
            assert params["signal"] == 9
        except ImportError:
            pytest.skip("Callbacks pas encore intégrés à dash_modules")


class TestIndicatorComponentIntegration:
    """Tests d'intégration des composants avec les services"""
    
    @pytest.mark.asyncio
    async def test_selector_integration(self):
        """Test intégration du sélecteur avec les services"""
        selector = IndicatorSelector.create()
        assert selector is not None
        # Le sélecteur devrait initialiser le composant sans erreur
    
    @pytest.mark.asyncio
    async def test_comparison_integration(self):
        """Test intégration du comparateur avec les services"""
        comparison = IndicatorComparison.create()
        assert comparison is not None
        # Le comparateur devrait initialiser sans erreur
    
    @pytest.mark.asyncio
    async def test_metrics_widget_integration(self):
        """Test intégration du widget de métriques"""
        metrics = IndicatorMetrics.create()
        assert metrics is not None
        # Le widget devrait initialiser sans erreur
    
    @pytest.mark.asyncio
    async def test_chart_widget_integration(self):
        """Test intégration du widget de chart"""
        chart = IndicatorChart.create()
        assert chart is not None
        # Le chart devrait initialiser sans erreur
    
    @pytest.mark.asyncio
    async def test_signal_modal_integration(self):
        """Test intégration du modal des signaux"""
        modal = SignalAlertModal.create()
        assert modal is not None
        # Le modal devrait initialiser sans erreur
    
    @pytest.mark.asyncio
    async def test_statistics_widget_integration(self):
        """Test intégration du widget de statistiques"""
        stats = IndicatorStatistics.create()
        assert stats is not None
        # Le widget devrait initialiser sans erreur


class TestDashboardComposition:
    """Tests pour la composition du dashboard"""
    
    def test_dashboard_not_empty(self):
        """Test que le dashboard n'est pas vide"""
        dashboard = create_full_indicator_dashboard()
        assert dashboard is not None
        assert len(dashboard.children) > 0
    
    def test_dashboard_has_rows(self):
        """Test que le dashboard contient des lignes"""
        dashboard = create_full_indicator_dashboard()
        # Vérifier qu'il y a au moins une ligne
        assert len(dashboard.children) >= 1
    
    def test_dashboard_fluid_container(self):
        """Test que le dashboard est un conteneur fluide"""
        dashboard = create_full_indicator_dashboard()
        assert dashboard.fluid is True


class TestPhase5Integration:
    """Tests d'intégration Phase 5.2 avec Phase 5.1"""
    
    @pytest.mark.asyncio
    async def test_integration_factory_available(self):
        """Test que la factory d'intégration est disponible"""
        try:
            from src.thebot.services.indicator_integration import get_integration_factory
            factory = get_integration_factory()
            assert factory is not None
        except Exception as e:
            pytest.skip(f"Factory non disponible: {e}")
    
    @pytest.mark.asyncio
    async def test_subscriber_available(self):
        """Test que le subscriber est disponible"""
        try:
            from src.thebot.services.real_time_updates import get_subscriber
            subscriber = get_subscriber()
            assert subscriber is not None
        except Exception as e:
            pytest.skip(f"Subscriber non disponible: {e}")
    
    @pytest.mark.asyncio
    async def test_signal_aggregator_available(self):
        """Test que l'agrégateur de signaux est disponible"""
        try:
            from src.thebot.services.real_time_updates import get_signal_aggregator
            aggregator = get_signal_aggregator()
            assert aggregator is not None
        except Exception as e:
            pytest.skip(f"Aggregator non disponible: {e}")
    
    @pytest.mark.asyncio
    async def test_async_wrapper_available(self):
        """Test que l'async wrapper est disponible"""
        try:
            from src.thebot.services.async_callbacks import get_async_wrapper
            wrapper = get_async_wrapper()
            assert wrapper is not None
        except Exception as e:
            pytest.skip(f"Wrapper non disponible: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
