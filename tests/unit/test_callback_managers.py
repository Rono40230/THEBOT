"""
Tests pour les gestionnaires de callbacks THEBOT
"""

import pytest
from unittest.mock import patch, MagicMock

from dash_modules.callbacks.base.callback_registry import CallbackRegistry


class TestCallbackRegistry:
    """Tests pour CallbackRegistry"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.registry = CallbackRegistry()

    def test_initialization(self):
        """Test initialisation du registry"""
        assert self.registry is not None
        assert hasattr(self.registry, '_managers')
        assert hasattr(self.registry, '_callbacks')
        assert hasattr(self.registry, '_inputs_outputs')

    def test_register_callback(self):
        """Test enregistrement d'un callback"""
        self.registry.register_callback(
            manager_name="test_manager",
            callback_id="test_callback",
            inputs=["input1"],
            outputs=["output1"],
            metadata={"type": "test"}
        )

        # Vérifier que quelque chose a été enregistré
        assert len(self.registry._callbacks) > 0

    def test_get_callbacks_by_manager(self):
        """Test récupération callbacks par manager"""
        self.registry.register_callback("manager1", "callback1", [], [])
        self.registry.register_callback("manager1", "callback2", [], [])
        self.registry.register_callback("manager2", "callback3", [], [])

        callbacks_m1 = self.registry.get_callbacks_by_manager("manager1")
        callbacks_m2 = self.registry.get_callbacks_by_manager("manager2")

        assert "callback1" in callbacks_m1
        assert "callback2" in callbacks_m1
        assert "callback3" in callbacks_m2
        assert len(callbacks_m1) == 2
        assert len(callbacks_m2) == 1

    def test_get_statistics(self):
        """Test récupération statistiques"""
        self.registry.register_callback("manager1", "callback1", [], [])
        self.registry.register_callback("manager2", "callback2", [], [])

        stats = self.registry.get_statistics()
        assert isinstance(stats, dict)
        assert "total_callbacks" in stats
        assert "callbacks_per_manager" in stats