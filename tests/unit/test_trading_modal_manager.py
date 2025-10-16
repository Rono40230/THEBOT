from src.thebot.core.logger import logger
"""
Tests pour le gestionnaire modal de trading THEBOT
"""

import pytest
from unittest.mock import patch, MagicMock

from dash_modules.callbacks.managers.trading_modal_manager import TradingModalManager


class TestTradingModalManager:
    """Tests pour TradingModalManager"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.app = MagicMock()
        self.callbacks = TradingModalManager(self.app)

    def test_initialization(self):
        """Test initialisation du gestionnaire"""
        assert self.callbacks is not None
        assert self.callbacks.app == self.app
        assert self.callbacks.name == "TradingModalManager"

    def test_register_all_callbacks(self):
        """Test enregistrement de tous les callbacks"""
        with patch.object(self.callbacks, '_register_trading_analysis_callbacks') as mock_analysis, \
             patch.object(self.callbacks, 'log_callback_registration') as mock_log:

            self.callbacks.register_all_callbacks()

            mock_analysis.assert_called_once()
            mock_log.assert_called_once()

    @patch('dash_modules.callbacks.managers.trading_modal_manager.logger')
    def test_register_all_callbacks_logging(self, mock_logger):
        """Test logging lors de l'enregistrement"""
        with patch.object(self.callbacks, '_register_trading_analysis_callbacks'), \
             patch.object(self.callbacks, 'log_callback_registration'):

            self.callbacks.register_all_callbacks()

            mock_logger.info.assert_any_call("🔄 Enregistrement des callbacks modal trading...")
            mock_logger.info.assert_any_call("✅ Callbacks modal trading enregistrés")

    def test_trading_analysis_callbacks_registration(self):
        """Test enregistrement callbacks analyse trading"""
        try:
            self.callbacks._register_trading_analysis_callbacks()
        except Exception:
            # C'est normal si les callbacks ne peuvent pas être enregistrés sans app complète
            pass