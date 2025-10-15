"""
Tests pour AI Engine Package - Module d'Intelligence Artificielle THEBOT
Tests se concentrant sur les imports et l'initialisation du package
"""

import pytest

from dash_modules.ai_engine import local_ai_engine, free_ai_engine, smart_ai_engine


class TestAIEnginePackage:
    """Tests pour le package ai_engine"""

    def test_imports(self):
        """Test que tous les moteurs d'IA peuvent être importés"""
        # Vérifier que les imports existent
        assert local_ai_engine is not None
        assert free_ai_engine is not None
        assert smart_ai_engine is not None

    def test_import_types(self):
        """Test que les imports sont des objets valides"""
        # Les objets importés devraient être des classes ou des instances
        # Pour l'instant, on vérifie juste qu'ils ne sont pas None
        assert local_ai_engine is not None
        assert free_ai_engine is not None
        assert smart_ai_engine is not None

    def test_all_exports(self):
        """Test que __all__ contient les bonnes exportations"""
        from dash_modules.ai_engine import __all__ as all_exports

        expected_exports = ["local_ai_engine", "free_ai_engine", "smart_ai_engine"]
        assert set(all_exports) == set(expected_exports)

    def test_module_structure(self):
        """Test que le module a la structure attendue"""
        import dash_modules.ai_engine as ai_engine_module

        # Vérifier que le module a les attributs attendus
        assert hasattr(ai_engine_module, 'local_ai_engine')
        assert hasattr(ai_engine_module, 'free_ai_engine')
        assert hasattr(ai_engine_module, 'smart_ai_engine')

        # Vérifier que les attributs ne sont pas None
        assert ai_engine_module.local_ai_engine is not None
        assert ai_engine_module.free_ai_engine is not None
        assert ai_engine_module.smart_ai_engine is not None