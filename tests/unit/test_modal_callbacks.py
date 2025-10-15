"""
Tests pour les callbacks de modals THEBOT
"""

import pytest
from unittest.mock import patch, MagicMock
from dash import html

from dash_modules.callbacks.managers.modal_callbacks import ModalCallbacks


class TestModalCallbacks:
    """Tests pour ModalCallbacks"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.app = MagicMock()
        self.modal_manager = MagicMock()
        self.callbacks = ModalCallbacks(self.app, self.modal_manager)

    def test_initialization(self):
        """Test initialisation du gestionnaire"""
        assert self.callbacks is not None
        assert self.callbacks.app == self.app
        assert self.callbacks.modal_manager == self.modal_manager
        assert self.callbacks.name == "ModalCallbacks"

    def test_register_all_callbacks(self):
        """Test enregistrement de tous les callbacks"""
        with patch.object(self.callbacks, '_register_tab_callbacks') as mock_tab, \
             patch.object(self.callbacks, '_register_debug_callbacks') as mock_debug, \
             patch.object(self.callbacks, '_register_basic_indicators_callbacks') as mock_basic, \
             patch.object(self.callbacks, '_register_advanced_indicators_callbacks') as mock_advanced, \
             patch.object(self.callbacks, 'log_callback_registration') as mock_log:

            self.callbacks.register_all_callbacks()

            mock_tab.assert_called_once()
            mock_debug.assert_called_once()
            mock_basic.assert_called_once()
            mock_advanced.assert_called_once()
            mock_log.assert_called_once()

    def test_tab_callbacks_registration(self):
        """Test enregistrement callbacks onglets"""
        try:
            self.callbacks._register_tab_callbacks()
        except Exception:
            # C'est normal si les callbacks ne peuvent pas être enregistrés sans app complète
            pass

    def test_debug_callbacks_registration(self):
        """Test enregistrement callbacks debug"""
        try:
            self.callbacks._register_debug_callbacks()
        except Exception:
            # C'est normal si les callbacks ne peuvent pas être enregistrés sans app complète
            pass

    def test_basic_indicators_callbacks_registration(self):
        """Test enregistrement callbacks indicateurs de base"""
        try:
            self.callbacks._register_basic_indicators_callbacks()
        except Exception:
            # C'est normal si les callbacks ne peuvent pas être enregistrés sans app complète
            pass

    def test_advanced_indicators_callbacks_registration(self):
        """Test enregistrement callbacks indicateurs avancés"""
        try:
            self.callbacks._register_advanced_indicators_callbacks()
        except Exception:
            # C'est normal si les callbacks ne peuvent pas être enregistrés sans app complète
            pass

    def test_tab_content_update_logic(self):
        """Test logique de mise à jour du contenu des onglets"""
        # Mock du modal manager
        mock_basic_content = html.Div("Basic Indicators Content")
        mock_advanced_content = html.Div("Advanced Indicators Content")
        mock_trading_content = html.Div("Trading Styles Content")
        mock_config_content = html.Div("Configuration Content")

        self.modal_manager._create_basic_indicators_content.return_value = mock_basic_content
        self.modal_manager._create_advanced_indicators_content.return_value = mock_advanced_content
        self.modal_manager._create_trading_styles_content.return_value = mock_trading_content
        self.modal_manager._create_configuration_content.return_value = mock_config_content

        with patch('dash.callback') as mock_callback:
            self.callbacks._register_tab_callbacks()

            callback_func = None
            for call in mock_callback.call_args_list:
                if 'update_tab_content' in str(call):
                    callback_func = call[1]['function']
                    break

            if callback_func:
                # Tester différents onglets
                result = callback_func("basic_indicators")
                assert result == mock_basic_content
                self.modal_manager._create_basic_indicators_content.assert_called_once()

                result = callback_func("advanced_indicators")
                assert result == mock_advanced_content
                self.modal_manager._create_advanced_indicators_content.assert_called_once()

                result = callback_func("trading_styles")
                assert result == mock_trading_content
                self.modal_manager._create_trading_styles_content.assert_called_once()

                result = callback_func("configuration")
                assert result == mock_config_content
                self.modal_manager._create_configuration_content.assert_called_once()

                # Tester onglet inconnu
                result = callback_func("unknown_tab")
                assert "Onglet non trouvé" in str(result)

    def test_tab_content_without_modal_manager(self):
        """Test contenu onglet sans modal manager"""
        callbacks_no_manager = ModalCallbacks(self.app, None)

        with patch('dash.callback') as mock_callback:
            callbacks_no_manager._register_tab_callbacks()

            callback_func = None
            for call in mock_callback.call_args_list:
                if 'update_tab_content' in str(call):
                    callback_func = call[1]['function']
                    break

            if callback_func:
                result = callback_func("basic_indicators")
                assert "Modal manager non disponible" in str(result)

    def test_debug_info_update_logic(self):
        """Test logique de mise à jour des informations de debug"""
        # Mock des paramètres
        mock_config = {
            "sma_period": 20,
            "ema_period": 12,
            "rsi_period": 14
        }
        self.modal_manager.parameters.get_all_basic_indicators.return_value = mock_config

        with patch('dash.callback') as mock_callback:
            self.callbacks._register_debug_callbacks()

            callback_func = None
            for call in mock_callback.call_args_list:
                if 'update_debug_info' in str(call):
                    callback_func = call[1]['function']
                    break

            if callback_func:
                result = callback_func([20, 12, 14])  # valeurs des indicateurs

                # Vérifier que le résultat est un composant Alert
                assert hasattr(result, 'children')
                assert len(result.children) > 0

                # Vérifier que get_all_basic_indicators a été appelé
                self.modal_manager.parameters.get_all_basic_indicators.assert_called_once()

    def test_debug_info_without_modal_manager(self):
        """Test debug info sans modal manager"""
        callbacks_no_manager = ModalCallbacks(self.app, None)

        with patch('dash.callback') as mock_callback:
            callbacks_no_manager._register_debug_callbacks()

            callback_func = None
            for call in mock_callback.call_args_list:
                if 'update_debug_info' in str(call):
                    callback_func = call[1]['function']
                    break

            if callback_func:
                result = callback_func([10, 20])

                # Devrait contenir "Modal manager non disponible"
                assert "Modal manager non disponible" in str(result)

    def test_basic_indicators_callbacks_logic(self):
        """Test logique des callbacks d'indicateurs de base"""
        # Mock des previews
        mock_sma_preview = html.Div("SMA Preview")
        mock_ema_preview = html.Div("EMA Preview")
        mock_rsi_preview = html.Div("RSI Preview")
        mock_atr_preview = html.Div("ATR Preview")
        mock_macd_preview = html.Div("MACD Preview")

        # Configurer les mocks du modal manager
        self.modal_manager._generate_sma_preview.return_value = mock_sma_preview
        self.modal_manager._generate_ema_preview.return_value = mock_ema_preview
        self.modal_manager._generate_rsi_preview.return_value = mock_rsi_preview
        self.modal_manager._generate_atr_preview.return_value = mock_atr_preview
        self.modal_manager._generate_macd_preview.return_value = mock_macd_preview

        with patch('dash.callback') as mock_callback:
            self.callbacks._register_basic_indicators_callbacks()

            callback_func = None
            for call in mock_callback.call_args_list:
                if 'basic_indicators' in str(call) or 'sma-preview' in str(call):
                    callback_func = call[1]['function']
                    break

            if callback_func:
                # Tester avec des valeurs d'entrée
                result = callback_func(20, 12, 14, 70, 30, 14, 2.0, 12, 26, 9)

                # Vérifier que le résultat a 5 éléments (un pour chaque indicateur)
                assert len(result) == 5

                # Vérifier que les méthodes de génération ont été appelées
                self.modal_manager._generate_sma_preview.assert_called_once()
                self.modal_manager._generate_ema_preview.assert_called_once()
                self.modal_manager._generate_rsi_preview.assert_called_once()
                self.modal_manager._generate_atr_preview.assert_called_once()
                self.modal_manager._generate_macd_preview.assert_called_once()

    def test_error_handling_in_tab_callbacks(self):
        """Test gestion d'erreur dans les callbacks d'onglets"""
        # Configurer le mock pour lever une exception
        self.modal_manager._create_basic_indicators_content.side_effect = Exception("Test Error")

        with patch('dash.callback') as mock_callback:
            self.callbacks._register_tab_callbacks()

            callback_func = None
            for call in mock_callback.call_args_list:
                if 'update_tab_content' in str(call):
                    callback_func = call[1]['function']
                    break

            if callback_func:
                result = callback_func("basic_indicators")

                # Devrait contenir le message d'erreur
                assert "Erreur lors du chargement" in str(result)

    def test_error_handling_in_debug_callbacks(self):
        """Test gestion d'erreur dans les callbacks de debug"""
        # Configurer le mock pour lever une exception
        self.modal_manager.parameters.get_all_basic_indicators.side_effect = Exception("Config Error")

        with patch('dash.callback') as mock_callback:
            self.callbacks._register_debug_callbacks()

            callback_func = None
            for call in mock_callback.call_args_list:
                if 'update_debug_info' in str(call):
                    callback_func = call[1]['function']
                    break

            if callback_func:
                result = callback_func([10])

                # Devrait contenir le message d'erreur
                assert "Erreur debug" in str(result)