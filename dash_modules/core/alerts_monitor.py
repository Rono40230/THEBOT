"""
Alerts Monitor Compatibility Module - Phase 1 THEBOT
Stub module pour maintenir la compatibilité avec dash_modules.core.alerts_monitor
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class AlertsNotificationManager:
    """Gestionnaire simplifié des notifications d'alertes"""

    def __init__(self):
        self.pending_notifications = []
        self.notification_history = []

    def browser_notification(self, alert_data: Dict):
        """Notification simplifiée"""
        logger.info(f"🔔 Browser notification: {alert_data}")
        return {"id": "stub", "title": "Stub notification"}

    def console_notification(self, alert_data: Dict):
        """Notification console simplifiée"""
        logger.info(f"🔔 Console notification: {alert_data}")

    def get_pending_notifications(self) -> List[Dict]:
        """Récupérer les notifications en attente"""
        return self.pending_notifications.copy()

    def mark_notifications_displayed(self, notifications: List[Dict]):
        """Marquer comme affichées"""
        pass

    def add_pending_notification(self, alert, trigger_price, current_price):
        """Ajouter une notification"""
        notification = {
            "id": f"alert-{alert.get('id', 'unknown')}",
            "alert": alert,
            "trigger_price": trigger_price,
            "current_price": current_price
        }
        self.pending_notifications.append(notification)


class AlertsMonitor:
    """Moniteur d'alertes simplifié"""

    def __init__(self, check_interval: int = 15):
        self.check_interval = check_interval
        self.is_running = False
        self.triggered_alerts = set()

    def start_monitoring(self):
        """Démarrer la surveillance"""
        self.is_running = True
        logger.info("🚀 Surveillance d'alertes démarrée (stub)")

    def stop_monitoring(self):
        """Arrêter la surveillance"""
        self.is_running = False
        logger.info("🛑 Surveillance d'alertes arrêtée (stub)")

    def get_status(self) -> Dict:
        """Statut du moniteur"""
        return {
            "is_running": self.is_running,
            "check_interval": self.check_interval,
            "active_alerts_count": 0,
            "monitored_symbols": [],
            "current_prices_count": 0,
            "triggered_alerts_count": len(self.triggered_alerts)
        }


# Instances globales pour compatibilité
notification_manager = AlertsNotificationManager()
alerts_monitor = AlertsMonitor()

__all__ = ["AlertsMonitor", "AlertsNotificationManager", "alerts_monitor", "notification_manager"]