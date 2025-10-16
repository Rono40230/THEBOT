from src.thebot.core.logger import logger
"""
Alerts Callbacks Manager - Gestionnaire centralisé des callbacks alertes
Regroupe tous les callbacks liés aux alertes et notifications
"""

import logging
import time
from typing import Any, Dict, List, Optional

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html

from ..base.callback_manager import CallbackManager
from ..base.callback_registry import get_callback_registry
from ...core.alerts_monitor import alerts_monitor, notification_manager

logger = logging.getLogger(__name__)


class AlertsCallbacks(CallbackManager):
    """
    Gestionnaire centralisé des callbacks pour les alertes.
    Regroupe les callbacks de :
    - price_alerts_modal.py (6 callbacks)
    - alerts_notifications.py (3 callbacks)
    """

    def __init__(self, app, alerts_manager=None, price_alerts_modal=None):
        """
        Initialise le gestionnaire de callbacks alertes.

        Args:
            app: Instance de l'application Dash
            alerts_manager: Gestionnaire d'alertes
            price_alerts_modal: Modal d'alertes de prix
        """
        super().__init__(app, "AlertsCallbacks")
        self.alerts_manager = alerts_manager
        self.price_alerts_modal = price_alerts_modal
        self.registry = get_callback_registry()

    def register_all_callbacks(self) -> None:
        """Enregistre tous les callbacks alertes."""
        logger.info("🔄 Enregistrement des callbacks alertes...")

        # Callbacks des notifications
        self._register_notifications_callbacks()

        # Callbacks du monitoring
        self._register_monitoring_callbacks()

        self.log_callback_registration()
        logger.info("✅ Callbacks alertes enregistrés")

    def _register_notifications_callbacks(self) -> None:
        """Enregistre les callbacks des notifications"""
        app = self.app

        @callback(
            Output("notifications-store", "data"),
            Input("notifications-interval", "n_intervals"),
            State("notifications-store", "data"),
            prevent_initial_call=False,
        )
        def update_notifications_store(n_intervals, current_notifications):
            """Mettre à jour le store avec les nouvelles notifications"""
            try:
                # Récupérer les notifications récentes
                recent_notifications = notification_manager.get_recent_notifications(limit=5)

                # Convertir en format compatible avec Dash
                notifications_data = []
                for notif in recent_notifications:
                    if notif not in current_notifications:
                        notifications_data.append(
                            {
                                "id": notif["id"],
                                "title": notif["title"],
                                "message": notif["message"],
                                "timestamp": notif["timestamp"],
                                "show": True,
                            }
                        )

                # Garder les notifications existantes qui sont encore valides
                current_time = time.time()
                for notif in current_notifications or []:
                    # Garder les notifications de moins de 15 secondes
                    if notif.get("show", True):
                        notifications_data.append(notif)

                # Limiter à 3 notifications maximum
                return notifications_data[-3:]

            except Exception as e:
                logger.error(f"Erreur mise à jour store notifications: {e}")
                return current_notifications or []

        @callback(
            Output("notifications-container", "children"),
            Input("notifications-store", "data"),
            prevent_initial_call=False,
        )
        def update_notifications_display(notifications_data):
            """Mettre à jour l'affichage des notifications"""
            try:
                if not notifications_data:
                    return []

                notification_elements = []
                for notif in notifications_data:
                    if not notif.get("show", True):
                        continue

                    notification_element = html.Div(
                        [
                            html.Button(
                                "×",
                                className="alert-notification-close",
                                id={"type": "close-notification", "index": notif["id"]},
                            ),
                            html.Div(notif["title"], className="alert-notification-header"),
                            html.Div(notif["message"], className="alert-notification-body"),
                            html.Div(notif["timestamp"], className="alert-notification-time"),
                        ],
                        className="alert-notification",
                        id=f"notification-{notif['id']}",
                    )

                    notification_elements.append(notification_element)

                return notification_elements

            except Exception as e:
                logger.error(f"Erreur mise à jour affichage notifications: {e}")
                return []

    def _register_monitoring_callbacks(self) -> None:
        """Enregistre les callbacks du monitoring"""
        app = self.app

        @callback(
            [
                Output("monitoring-status-display", "children"),
                Output("monitoring-status-display", "className"),
            ],
            Input("monitoring-status-interval", "n_intervals"),
            prevent_initial_call=False,
        )
        def update_monitoring_status(n_intervals):
            """Mettre à jour le statut de surveillance"""
            try:
                status = alerts_monitor.get_status()

                if status["is_running"]:
                    status_text = (
                        f"🔔 Surveillance active ({status['active_alerts_count']} alertes)"
                    )
                    status_class = "monitoring-status"
                else:
                    status_text = "🔔 Surveillance inactive"
                    status_class = "monitoring-status inactive"

                return status_text, status_class

            except Exception as e:
                logger.error(f"Erreur mise à jour statut monitoring: {e}")
                return "❌ Erreur monitoring", "monitoring-status error"