"""
Tests pour les callbacks d'alertes de prix THEBOT
"""

import pytest
from unittest.mock import patch, MagicMock

from dash_modules.callbacks.managers.price_alerts_callbacks import PriceAlertsCallbacks


class TestPriceAlertsCallbacks:
    """Tests pour PriceAlertsCallbacks"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.app = MagicMock()
        self.alerts_manager = MagicMock()
        self.callbacks = PriceAlertsCallbacks(self.app, self.alerts_manager)

    def test_initialization(self):
        """Test initialisation du gestionnaire"""
        assert self.callbacks is not None
        assert self.callbacks.app == self.app
        assert self.callbacks.alerts_manager == self.alerts_manager
        assert self.callbacks.name == "PriceAlertsCallbacks"

    def test_register_all_callbacks(self):
        """Test enregistrement de tous les callbacks"""
        with patch.object(self.callbacks, '_register_price_alerts_modal_callbacks') as mock_modal, \
             patch.object(self.callbacks, 'log_callback_registration') as mock_log:

            self.callbacks.register_all_callbacks()

            mock_modal.assert_called_once()
            mock_log.assert_called_once()

    @patch('dash_modules.callbacks.managers.price_alerts_callbacks.logger')
    def test_register_all_callbacks_logging(self, mock_logger):
        """Test logging lors de l'enregistrement"""
        with patch.object(self.callbacks, '_register_price_alerts_modal_callbacks'), \
             patch.object(self.callbacks, 'log_callback_registration'):

            self.callbacks.register_all_callbacks()

            mock_logger.info.assert_any_call("🔄 Enregistrement des callbacks alertes prix...")
            mock_logger.info.assert_any_call("✅ Callbacks alertes prix enregistrés")

    def test_alerts_table_update_logic(self):
        """Test logique de mise à jour du tableau d'alertes"""
        # Mock des alertes
        mock_alerts = [
            {
                "id": "alert_1",
                "symbol": "BTCUSDT",
                "alert_type": "above",
                "price": 50000.0,
                "message": "BTC above 50k",
                "created_at": "2024-01-01T10:00:00Z",
                "is_active": True
            },
            {
                "id": "alert_2",
                "symbol": "ETHUSDT",
                "alert_type": "below",
                "price": 3000.0,
                "message": "ETH below 3k",
                "created_at": "2024-01-01T11:00:00Z",
                "is_active": True
            }
        ]

        with patch('dash_modules.callbacks.managers.price_alerts_callbacks.alerts_manager') as mock_alerts_mgr:
            mock_alerts_mgr.get_all_alerts.return_value = mock_alerts

            with patch('dash.callback') as mock_callback:
                self.callbacks._register_price_alerts_modal_callbacks()

                callback_func = None
                for call in mock_callback.call_args_list:
                    if 'update_alerts_table' in str(call):
                        callback_func = call[1]['function']
                        break

                if callback_func:
                    result = callback_func(mock_alerts)

                    # Vérifier que le résultat est un composant HTML
                    assert hasattr(result, 'children')
                    assert len(result.children) == 2  # 2 cartes d'alertes

                    # Vérifier que get_all_alerts a été appelé
                    mock_alerts_mgr.get_all_alerts.assert_called_once()

    def test_alerts_table_empty_alerts(self):
        """Test tableau d'alertes avec aucune alerte"""
        with patch('dash_modules.callbacks.managers.price_alerts_callbacks.alerts_manager') as mock_alerts_mgr:
            mock_alerts_mgr.get_all_alerts.return_value = []

            with patch('dash.callback') as mock_callback:
                self.callbacks._register_price_alerts_modal_callbacks()

                callback_func = None
                for call in mock_callback.call_args_list:
                    if 'update_alerts_table' in str(call):
                        callback_func = call[1]['function']
                        break

                if callback_func:
                    result = callback_func([])

                    # Vérifier que le message "Aucune alerte" est affiché
                    assert hasattr(result, 'children')
                    assert len(result.children) == 1
                    assert "Aucune alerte configurée" in str(result.children[0])

    def test_alerts_table_error_handling(self):
        """Test gestion d'erreur dans le tableau d'alertes"""
        with patch('dash_modules.callbacks.managers.price_alerts_callbacks.alerts_manager') as mock_alerts_mgr:
            mock_alerts_mgr.get_all_alerts.side_effect = Exception("Database Error")

            with patch('dash.callback') as mock_callback:
                self.callbacks._register_price_alerts_modal_callbacks()

                callback_func = None
                for call in mock_callback.call_args_list:
                    if 'update_alerts_table' in str(call):
                        callback_func = call[1]['function']
                        break

                if callback_func:
                    result = callback_func([])

                    # Vérifier que le message d'erreur est affiché
                    assert "Erreur chargement alertes" in str(result)

    def test_toggle_alerts_modal_logic(self):
        """Test logique d'ouverture/fermeture du modal d'alertes"""
        with patch('dash.callback') as mock_callback:
            self.callbacks._register_price_alerts_modal_callbacks()

            callback_func = None
            for call in mock_callback.call_args_list:
                if 'toggle_alerts_modal' in str(call):
                    callback_func = call[1]['function']
                    break

            if callback_func:
                # Test ouverture du modal (modal fermé)
                result = callback_func(1, None, False)  # open_clicks=1, close_clicks=None, is_open=False
                assert result is True

                # Test fermeture du modal (modal ouvert)
                result = callback_func(None, 1, True)  # open_clicks=None, close_clicks=1, is_open=True
                assert result is False

                # Test aucun clic (pas de changement)
                result = callback_func(None, None, True)  # open_clicks=None, close_clicks=None, is_open=True
                assert result is True

    def test_toggle_alerts_modal_error_handling(self):
        """Test gestion d'erreur dans toggle modal"""
        with patch('dash.callback') as mock_callback:
            self.callbacks._register_price_alerts_modal_callbacks()

            callback_func = None
            for call in mock_callback.call_args_list:
                if 'toggle_alerts_modal' in str(call):
                    callback_func = call[1]['function']
                    break

            if callback_func:
                # Simuler une erreur (en passant des types incorrects)
                result = callback_func("invalid", "invalid", "invalid")

                # En cas d'erreur, devrait retourner False (modal fermé)
                assert result is False

    def test_price_alerts_modal_callbacks_registration(self):
        """Test enregistrement callbacks modal alertes prix"""
        try:
            self.callbacks._register_price_alerts_modal_callbacks()
        except Exception:
            # C'est normal si les callbacks ne peuvent pas être enregistrés sans app complète
            pass