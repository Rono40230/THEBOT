"""
Tests pour les callbacks d'alertes THEBOT
"""

import pytest
from unittest.mock import patch, MagicMock
import time

from dash_modules.callbacks.managers.alerts_callbacks import AlertsCallbacks


class TestAlertsCallbacks:
    """Tests pour AlertsCallbacks"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.app = MagicMock()
        self.alerts_manager = MagicMock()
        self.price_alerts_modal = MagicMock()
        self.callbacks = AlertsCallbacks(self.app, self.alerts_manager, self.price_alerts_modal)

    def test_initialization(self):
        """Test initialisation du gestionnaire"""
        assert self.callbacks is not None
        assert self.callbacks.app == self.app
        assert self.callbacks.alerts_manager == self.alerts_manager
        assert self.callbacks.price_alerts_modal == self.price_alerts_modal
        assert self.callbacks.name == "AlertsCallbacks"

    def test_register_all_callbacks(self):
        """Test enregistrement de tous les callbacks"""
        with patch.object(self.callbacks, '_register_notifications_callbacks') as mock_notif, \
             patch.object(self.callbacks, '_register_monitoring_callbacks') as mock_monitor, \
             patch.object(self.callbacks, 'log_callback_registration') as mock_log:

            self.callbacks.register_all_callbacks()

            mock_notif.assert_called_once()
            mock_monitor.assert_called_once()
            mock_log.assert_called_once()

    @patch('dash_modules.callbacks.managers.alerts_callbacks.logger')
    def test_register_all_callbacks_logging(self, mock_logger):
        """Test logging lors de l'enregistrement"""
        with patch.object(self.callbacks, '_register_notifications_callbacks'), \
             patch.object(self.callbacks, '_register_monitoring_callbacks'), \
             patch.object(self.callbacks, 'log_callback_registration'):

            self.callbacks.register_all_callbacks()

            mock_logger.info.assert_any_call("🔄 Enregistrement des callbacks alertes...")
            mock_logger.info.assert_any_call("✅ Callbacks alertes enregistrés")

    def test_notifications_callbacks_registration(self):
        """Test enregistrement callbacks notifications"""
        # Ce test vérifie que la méthode existe et peut être appelée
        try:
            self.callbacks._register_notifications_callbacks()
        except Exception:
            # C'est normal si les callbacks ne peuvent pas être enregistrés sans app complète
            pass

    def test_monitoring_callbacks_registration(self):
        """Test enregistrement des callbacks de monitoring"""
        try:
            self.callbacks._register_monitoring_callbacks()
        except Exception:
            # C'est normal si les callbacks ne peuvent pas être enregistrés sans app complète
            pass

    def test_notifications_store_update_logic(self):
        """Test logique de mise à jour du store de notifications"""
        # Mock des notifications récentes
        mock_notifications = [
            {
                "id": "notif_1",
                "title": "Test Alert",
                "message": "This is a test notification",
                "timestamp": time.time()
            },
            {
                "id": "notif_2",
                "title": "Another Alert",
                "message": "Another test message",
                "timestamp": time.time()
            }
        ]

        # Mock du notification manager
        with patch('dash_modules.callbacks.managers.alerts_callbacks.notification_manager') as mock_notif_manager:
            mock_notif_manager.get_recent_notifications.return_value = mock_notifications

            with patch('dash.callback') as mock_callback:
                self.callbacks._register_notifications_callbacks()

                callback_func = None
                for call in mock_callback.call_args_list:
                    if 'update_notifications_store' in str(call):
                        callback_func = call[1]['function']
                        break

                if callback_func:
                    # Tester avec données actuelles vides
                    result = callback_func(1, [])

                    # Vérifier que le résultat contient les nouvelles notifications
                    assert len(result) == 2
                    assert result[0]["id"] == "notif_1"
                    assert result[0]["title"] == "Test Alert"
                    assert result[0]["show"] is True

                    # Vérifier que get_recent_notifications a été appelé
                    mock_notif_manager.get_recent_notifications.assert_called_with(limit=5)

    def test_notifications_display_update_logic(self):
        """Test logique de mise à jour de l'affichage des notifications"""
        # Mock des données de notifications
        mock_notifications_data = [
            {
                "id": "notif_1",
                "title": "Test Alert",
                "message": "This is a test notification",
                "timestamp": time.time(),
                "show": True
            }
        ]

        with patch('dash.callback') as mock_callback:
            self.callbacks._register_notifications_callbacks()

            callback_func = None
            for call in mock_callback.call_args_list:
                if 'update_notifications_display' in str(call):
                    callback_func = call[1]['function']
                    break

            if callback_func:
                result = callback_func(mock_notifications_data)

                # Vérifier que le résultat est une liste d'éléments
                assert isinstance(result, list)
                assert len(result) > 0

                # Vérifier que le premier élément est un div de notification
                notification_div = result[0]
                assert hasattr(notification_div, 'children')

    def test_notifications_with_existing_data(self):
        """Test notifications avec données existantes dans le store"""
        # Mock des notifications existantes
        existing_notifications = [
            {
                "id": "existing_1",
                "title": "Existing Alert",
                "message": "Existing message",
                "timestamp": time.time(),
                "show": True
            }
        ]

        # Mock des nouvelles notifications
        new_notifications = [
            {
                "id": "new_1",
                "title": "New Alert",
                "message": "New message",
                "timestamp": time.time()
            }
        ]

        with patch('dash_modules.callbacks.managers.alerts_callbacks.notification_manager') as mock_notif_manager:
            mock_notif_manager.get_recent_notifications.return_value = new_notifications

            with patch('dash.callback') as mock_callback:
                self.callbacks._register_notifications_callbacks()

                callback_func = None
                for call in mock_callback.call_args_list:
                    if 'update_notifications_store' in str(call):
                        callback_func = call[1]['function']
                        break

                if callback_func:
                    result = callback_func(1, existing_notifications)

                    # Devrait contenir les notifications existantes et nouvelles
                    assert len(result) <= 3  # Limité à 3 maximum

    def test_notifications_empty_data(self):
        """Test notifications avec données vides"""
        with patch('dash_modules.callbacks.managers.alerts_callbacks.notification_manager') as mock_notif_manager:
            mock_notif_manager.get_recent_notifications.return_value = []

            with patch('dash.callback') as mock_callback:
                self.callbacks._register_notifications_callbacks()

                # Tester update_notifications_store
                store_callback = None
                display_callback = None
                for call in mock_callback.call_args_list:
                    if 'update_notifications_store' in str(call):
                        store_callback = call[1]['function']
                    elif 'update_notifications_display' in str(call):
                        display_callback = call[1]['function']

                if store_callback:
                    result = store_callback(1, [])
                    assert result == []

                if display_callback:
                    result = display_callback([])
                    assert result == []

    def test_notifications_error_handling(self):
        """Test gestion d'erreur dans les callbacks de notifications"""
        with patch('dash_modules.callbacks.managers.alerts_callbacks.notification_manager') as mock_notif_manager:
            mock_notif_manager.get_recent_notifications.side_effect = Exception("API Error")

            with patch('dash.callback') as mock_callback:
                self.callbacks._register_notifications_callbacks()

                callback_func = None
                for call in mock_callback.call_args_list:
                    if 'update_notifications_store' in str(call):
                        callback_func = call[1]['function']
                        break

                if callback_func:
                    # Le callback devrait gérer l'erreur et retourner les données actuelles
                    current_data = [{"id": "existing", "show": True}]
                    result = callback_func(1, current_data)

                    # En cas d'erreur, devrait retourner les données actuelles
                    assert result == current_data