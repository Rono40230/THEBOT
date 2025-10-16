"""
Alerts Manager - Version simplifiée pour compatibilité
Fournit les fonctions nécessaires aux modules UI restants
"""

from typing import Any, Dict, List, Optional
from src.thebot.core.logger import logger


class AlertsManager:
    """Gestionnaire d'alertes simplifié"""

    def __init__(self):
        self._alerts = []
        logger.info("AlertsManager simplifié initialisé")

    def add_alert(self, alert_type: str, message: str, **kwargs):
        """Ajoute une alerte"""
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": None,
            **kwargs
        }
        self._alerts.append(alert)
        logger.info(f"Alerte ajoutée: {alert_type} - {message}")

    def get_alerts(self, alert_type: str = None) -> List[Dict[str, Any]]:
        """Récupère les alertes"""
        if alert_type:
            return [a for a in self._alerts if a["type"] == alert_type]
        return self._alerts.copy()

    def clear_alerts(self, alert_type: str = None):
        """Efface les alertes"""
        if alert_type:
            self._alerts = [a for a in self._alerts if a["type"] != alert_type]
        else:
            self._alerts.clear()
        logger.info(f"Alertes effacées: {alert_type or 'toutes'}")


# Instance globale
alerts_manager = AlertsManager()