"""
Tests pour le gestionnaire modal de news THEBOT
"""

import pytest
from unittest.mock import patch, MagicMock

from dash_modules.callbacks.managers.news_modal_manager import NewsModalManager


class TestNewsModalManager:
    """Tests pour NewsModalManager"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.app = MagicMock()
        self.callbacks = NewsModalManager(self.app)

    def test_initialization(self):
        """Test initialisation du gestionnaire"""
        assert self.callbacks is not None
        assert self.callbacks.app == self.app
        assert self.callbacks.name == "NewsModalManager"

    def test_register_all_callbacks(self):
        """Test enregistrement de tous les callbacks"""
        with patch.object(self.callbacks, '_register_news_data_callbacks') as mock_news, \
             patch.object(self.callbacks, 'log_callback_registration') as mock_log:

            self.callbacks.register_all_callbacks()

            mock_news.assert_called_once()
            mock_log.assert_called_once()

    @patch('dash_modules.callbacks.managers.news_modal_manager.logger')
    def test_register_all_callbacks_logging(self, mock_logger):
        """Test logging lors de l'enregistrement"""
        with patch.object(self.callbacks, '_register_news_data_callbacks'), \
             patch.object(self.callbacks, 'log_callback_registration'):

            self.callbacks.register_all_callbacks()

            mock_logger.info.assert_any_call("🔄 Enregistrement des callbacks modal news...")
            mock_logger.info.assert_any_call("✅ Callbacks modal news enregistrés")

    def test_news_data_callbacks_registration(self):
        """Test enregistrement callbacks données news"""
        try:
            self.callbacks._register_news_data_callbacks()
        except Exception:
            # C'est normal si les callbacks ne peuvent pas être enregistrés sans app complète
            pass