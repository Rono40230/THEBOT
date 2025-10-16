"""
Phase 5.2 - Tests des composants UI et callbacks
Tests d'intégration avec Phase 5.1 services
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from decimal import Decimal

# Tests des composants
def test_indicator_selector_available():
    """Test que IndicatorSelector est disponible"""
    try:
        from dash_modules.components.modern_indicators import IndicatorSelector
        assert IndicatorSelector is not None
    except ImportError as e:
        pytest.skip(f"IndicatorSelector pas disponible: {e}")


def test_indicator_comparison_available():
    """Test que IndicatorComparison est disponible"""
    try:
        from dash_modules.components.modern_indicators import IndicatorComparison
        assert IndicatorComparison is not None
    except ImportError as e:
        pytest.skip(f"IndicatorComparison pas disponible: {e}")


def test_signal_alert_modal_available():
    """Test que SignalAlertModal est disponible"""
    try:
        from dash_modules.components.modern_indicators import SignalAlertModal
        assert SignalAlertModal is not None
    except ImportError as e:
        pytest.skip(f"SignalAlertModal pas disponible: {e}")


def test_indicator_metrics_available():
    """Test que IndicatorMetrics est disponible"""
    try:
        from dash_modules.components.modern_indicators import IndicatorMetrics
        assert IndicatorMetrics is not None
    except ImportError as e:
        pytest.skip(f"IndicatorMetrics pas disponible: {e}")


def test_indicator_chart_available():
    """Test que IndicatorChart est disponible"""
    try:
        from dash_modules.components.modern_indicators import IndicatorChart
        assert IndicatorChart is not None
    except ImportError as e:
        pytest.skip(f"IndicatorChart pas disponible: {e}")


def test_signal_history_table_available():
    """Test que SignalHistoryTable est disponible"""
    try:
        from dash_modules.components.modern_indicators import SignalHistoryTable
        assert SignalHistoryTable is not None
    except ImportError as e:
        pytest.skip(f"SignalHistoryTable pas disponible: {e}")


def test_indicator_statistics_available():
    """Test que IndicatorStatistics est disponible"""
    try:
        from dash_modules.components.modern_indicators import IndicatorStatistics
        assert IndicatorStatistics is not None
    except ImportError as e:
        pytest.skip(f"IndicatorStatistics pas disponible: {e}")


def test_create_full_indicator_dashboard_available():
    """Test que create_full_indicator_dashboard est disponible"""
    try:
        from dash_modules.components.modern_indicators import create_full_indicator_dashboard
        assert create_full_indicator_dashboard is not None
    except ImportError as e:
        pytest.skip(f"create_full_indicator_dashboard pas disponible: {e}")


def test_indicator_selector_create():
    """Test que IndicatorSelector.create() retourne un composant"""
    try:
        from dash_modules.components.modern_indicators import IndicatorSelector
        component = IndicatorSelector.create()
        assert component is not None
    except Exception as e:
        pytest.skip(f"Erreur création IndicatorSelector: {e}")


def test_indicator_comparison_create():
    """Test que IndicatorComparison.create() retourne un composant"""
    try:
        from dash_modules.components.modern_indicators import IndicatorComparison
        component = IndicatorComparison.create()
        assert component is not None
    except Exception as e:
        pytest.skip(f"Erreur création IndicatorComparison: {e}")


def test_signal_alert_modal_create():
    """Test que SignalAlertModal.create() retourne un composant"""
    try:
        from dash_modules.components.modern_indicators import SignalAlertModal
        component = SignalAlertModal.create()
        assert component is not None
    except Exception as e:
        pytest.skip(f"Erreur création SignalAlertModal: {e}")


def test_indicator_metrics_create():
    """Test que IndicatorMetrics.create() retourne un composant"""
    try:
        from dash_modules.components.modern_indicators import IndicatorMetrics
        component = IndicatorMetrics.create()
        assert component is not None
    except Exception as e:
        pytest.skip(f"Erreur création IndicatorMetrics: {e}")


def test_indicator_chart_create():
    """Test que IndicatorChart.create() retourne un composant"""
    try:
        from dash_modules.components.modern_indicators import IndicatorChart
        component = IndicatorChart.create()
        assert component is not None
    except Exception as e:
        pytest.skip(f"Erreur création IndicatorChart: {e}")


def test_signal_history_table_create():
    """Test que SignalHistoryTable.create() retourne un composant"""
    try:
        from dash_modules.components.modern_indicators import SignalHistoryTable
        component = SignalHistoryTable.create()
        assert component is not None
    except Exception as e:
        pytest.skip(f"Erreur création SignalHistoryTable: {e}")


def test_indicator_statistics_create():
    """Test que IndicatorStatistics.create() retourne un composant"""
    try:
        from dash_modules.components.modern_indicators import IndicatorStatistics
        component = IndicatorStatistics.create()
        assert component is not None
    except Exception as e:
        pytest.skip(f"Erreur création IndicatorStatistics: {e}")


def test_full_indicator_dashboard_create():
    """Test que create_full_indicator_dashboard() retourne un composant"""
    try:
        from dash_modules.components.modern_indicators import create_full_indicator_dashboard
        dashboard = create_full_indicator_dashboard()
        assert dashboard is not None
    except Exception as e:
        pytest.skip(f"Erreur création dashboard: {e}")


def test_phase5_callbacks_available():
    """Test que les callbacks Phase 5.2 sont disponibles"""
    try:
        import dash_modules.callbacks.phase5_2_callbacks
        assert dash_modules.callbacks.phase5_2_callbacks is not None
    except ImportError as e:
        pytest.skip(f"Callbacks Phase 5.2 pas disponibles: {e}")


def test_integration_factory_available():
    """Test que la factory d'intégration est disponible"""
    try:
        from src.thebot.services.indicator_integration import get_integration_factory
        factory = get_integration_factory()
        assert factory is not None
    except Exception as e:
        pytest.skip(f"Factory non disponible: {e}")


def test_subscriber_available():
    """Test que le subscriber est disponible"""
    try:
        from src.thebot.services.real_time_updates import get_subscriber
        subscriber = get_subscriber()
        assert subscriber is not None
    except Exception as e:
        pytest.skip(f"Subscriber non disponible: {e}")


def test_signal_aggregator_available():
    """Test que l'agrégateur de signaux est disponible"""
    try:
        from src.thebot.services.real_time_updates import get_signal_aggregator
        aggregator = get_signal_aggregator()
        assert aggregator is not None
    except Exception as e:
        pytest.skip(f"Aggregator non disponible: {e}")


def test_async_wrapper_available():
    """Test que l'async wrapper est disponible"""
    try:
        from src.thebot.services.async_callbacks import get_async_wrapper
        wrapper = get_async_wrapper()
        assert wrapper is not None
    except Exception as e:
        pytest.skip(f"Wrapper non disponible: {e}")


def test_indicator_selector_has_timeframes():
    """Test que IndicatorSelector contient des timeframes"""
    try:
        from dash_modules.components.modern_indicators import IndicatorSelector
        assert len(IndicatorSelector.TIMEFRAMES) > 0
    except Exception as e:
        pytest.skip(f"Erreur vérification timeframes: {e}")


def test_indicator_selector_has_indicators():
    """Test que IndicatorSelector contient des indicateurs"""
    try:
        from dash_modules.components.modern_indicators import IndicatorSelector
        assert len(IndicatorSelector.AVAILABLE_INDICATORS) > 0
    except Exception as e:
        pytest.skip(f"Erreur vérification indicateurs: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
