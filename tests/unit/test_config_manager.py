"""
Tests pour ConfigManager - Gestionnaire de configuration unifié
"""

import pytest
from unittest.mock import patch, MagicMock

from dash_modules.core.config_manager import ConfigManager, get_global_config


class TestConfigManager:
    """Tests pour ConfigManager"""

    def test_singleton_pattern(self):
        """Test que ConfigManager suit le pattern singleton"""
        instance1 = ConfigManager()
        instance2 = ConfigManager()
        assert instance1 is instance2

    def test_get_global_config(self):
        """Test fonction utilitaire get_global_config"""
        config = get_global_config()
        assert isinstance(config, ConfigManager)

    def test_get_existing_config(self):
        """Test récupération de configuration existante"""
        config = get_global_config()
        app_name = config.get('app.name')
        assert app_name == 'THEBOT'

    def test_get_nested_config(self):
        """Test récupération de configuration imbriquée"""
        config = get_global_config()
        port = config.get('app.port')
        assert isinstance(port, int)
        assert port > 0

    def test_get_default_value(self):
        """Test valeur par défaut"""
        config = get_global_config()
        nonexistent = config.get('nonexistent.key', 'default')
        assert nonexistent == 'default'

    def test_set_config_value(self):
        """Test modification de configuration"""
        config = get_global_config()
        original = config.get('app.debug')

        config.set('app.debug', True)
        assert config.get('app.debug') is True

        # Restaurer valeur originale
        config.set('app.debug', original)

    def test_get_section(self):
        """Test récupération de section complète"""
        config = get_global_config()
        app_section = config.get_section('app')
        assert isinstance(app_section, dict)
        assert 'name' in app_section
        assert 'version' in app_section

    @patch('dash_modules.core.config_manager.THEBOT_CONFIG')
    def test_load_default_config(self, mock_config):
        """Test chargement configuration par défaut"""
        mock_config.__getitem__ = MagicMock(return_value={'test': 'value'})

        # Créer nouvelle instance pour test
        ConfigManager._instance = None
        config = ConfigManager()

        # Vérifier que la config est chargée
        assert hasattr(config, '_config')

    def test_get_all_config(self):
        """Test récupération de toute la configuration"""
        config = get_global_config()
        all_config = config.get_all_config()
        assert isinstance(all_config, dict)
        assert 'app' in all_config
        assert 'providers' in all_config

    @patch('builtins.open')
    @patch('json.load')
    @patch('pathlib.Path.exists')
    def test_load_from_files_with_api_config(self, mock_exists, mock_json_load, mock_open):
        """Test chargement depuis fichiers avec api_config.json"""
        mock_exists.return_value = True
        mock_json_load.return_value = {'test': 'api_value'}

        # Créer nouvelle instance
        ConfigManager._instance = None
        config = ConfigManager()

        # Simuler présence du fichier
        config._load_from_files()

        # Vérifier que json.load a été appelé
        mock_json_load.assert_called()

    @patch.dict('os.environ', {'THEBOT_DEBUG': 'true', 'THEBOT_PORT': '9090'})
    def test_load_env_variables(self):
        """Test chargement des variables d'environnement"""
        # Créer nouvelle instance
        ConfigManager._instance = None
        config = ConfigManager()

        # Simuler chargement env
        config._load_env_variables()

        # Les valeurs devraient être dans la config si elles existent
        # (dépend de THEBOT_CONFIG)

    def test_merge_config(self):
        """Test fusion de configurations"""
        config = get_global_config()

        base = {'a': 1, 'b': {'c': 2}}
        update = {'b': {'d': 3}, 'e': 4}

        config._merge_config(base, update)

        assert base['a'] == 1
        assert base['b']['c'] == 2
        assert base['b']['d'] == 3
        assert base['e'] == 4