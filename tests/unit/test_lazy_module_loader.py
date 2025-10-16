"""
Tests unitaires pour LazyModuleLoader - Phase 4
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dash_modules.core.lazy_module_loader import LazyModuleLoader


class TestLazyModuleLoader:
    """Tests pour le chargeur paresseux de modules"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.loader = LazyModuleLoader()

    @patch('dash_modules.core.lazy_module_loader.logger')
    def test_init_registers_module_classes(self, mock_logger):
        """Test que l'initialisation enregistre les classes de modules"""
        # Vérifier que les classes sont enregistrées
        assert len(self.loader._module_classes) > 0
        assert "crypto" in self.loader._module_classes

    @patch('dash_modules.core.lazy_module_loader.logger')
    def test_get_module_unknown_module(self, mock_logger):
        """Test récupération d'un module inconnu"""
        with pytest.raises(ValueError, match="Module 'unknown' non trouvé"):
            self.loader.get_module("unknown")

    def test_get_performance_metrics_empty(self):
        """Test métriques avec aucun module chargé"""
        metrics = self.loader.get_performance_metrics()

        assert metrics["loaded_modules_count"] == 0
        assert metrics["total_load_time"] == 0
        assert metrics["average_load_time"] == 0
        assert metrics["module_load_times"] == {}
