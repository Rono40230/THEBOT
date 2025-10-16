from src.thebot.core.logger import logger
"""
Economic Alerts Service - Logique métier pour les alertes économiques
Extrait la logique métier de alerts_notifications.py pour respecter MVC
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import threading
import json

from .alert_service import AlertService

logger = logging.getLogger(__name__)


class EconomicAlertsService:
    """
    Service de logique métier pour les alertes économiques
    Gère la création, le monitoring et les notifications d'alertes économiques
    """

    def __init__(self):
        self.alert_service = AlertService()
        self._lock = threading.Lock()
        self.active_alerts = {}
        self.alert_history = []

    def create_economic_alert(
        self,
        alert_type: str,
        symbol: str,
        condition: str,
        threshold: float,
        message: str,
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Crée une nouvelle alerte économique

        Args:
            alert_type: Type d'alerte (price, volume, economic_indicator, etc.)
            symbol: Symbole ou indicateur concerné
            condition: Condition de déclenchement
            threshold: Seuil de déclenchement
            message: Message de notification
            user_id: ID utilisateur

        Returns:
            Dictionnaire de l'alerte créée
        """
        try:
            alert_data = {
                "type": alert_type,
                "symbol": symbol,
                "condition": condition,
                "threshold": threshold,
                "message": message,
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "is_active": True,
                "trigger_count": 0,
                "last_triggered": None
            }

            # Créer l'alerte via le service de base
            alert = self.alert_service.create_alert(
                symbol=symbol,
                alert_type=alert_type,
                condition=condition,
                value=threshold,
                message=message,
                user_id=int(user_id) if user_id.isdigit() else 1
            )

            # Convertir en dict pour cohérence
            alert_dict = {
                "id": alert.id,
                "type": alert.alert_type,
                "symbol": alert.symbol,
                "condition": alert.condition,
                "threshold": alert.value,
                "message": alert.message,
                "user_id": str(alert.user_id),
                "created_at": alert.created_at.isoformat() if alert.created_at else datetime.now().isoformat(),
                "is_active": alert.is_active,
                "trigger_count": 0,
                "last_triggered": None
            }

            # Ajouter aux alertes actives
            with self._lock:
                self.active_alerts[alert.id] = alert_dict

            logger.info(f"Alerte économique créée: {alert_type} pour {symbol}")
            return alert_dict

        except Exception as e:
            logger.error(f"Erreur création alerte économique: {e}")
            return {}

    def check_economic_alerts(self, market_data: Dict[str, Any], economic_indicators: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Vérifie les alertes économiques contre les données actuelles

        Args:
            market_data: Données de marché actuelles
            economic_indicators: Indicateurs économiques actuels

        Returns:
            Liste des alertes déclenchées
        """
        triggered_alerts = []

        try:
            with self._lock:
                for alert_id, alert in self.active_alerts.items():
                    if not alert.get("is_active", False):
                        continue

                    if self._check_alert_condition(alert, market_data, economic_indicators):
                        # Marquer comme déclenchée
                        alert["trigger_count"] += 1
                        alert["last_triggered"] = datetime.now().isoformat()

                        # Ajouter à l'historique
                        self.alert_history.append({
                            "alert_id": alert_id,
                            "triggered_at": alert["last_triggered"],
                            "market_data": market_data,
                            "economic_indicators": economic_indicators
                        })

                        triggered_alerts.append(alert.copy())

                        # Désactiver si alerte ponctuelle
                        if alert.get("type") in ["one_time", "threshold_reached"]:
                            alert["is_active"] = False

            return triggered_alerts

        except Exception as e:
            logger.error(f"Erreur vérification alertes économiques: {e}")
            return []

    def get_active_alerts(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """Récupère les alertes actives pour un utilisateur"""
        try:
            with self._lock:
                return [
                    alert for alert in self.active_alerts.values()
                    if alert.get("user_id") == user_id and alert.get("is_active", False)
                ]
        except Exception as e:
            logger.error(f"Erreur récupération alertes actives: {e}")
            return []

    def get_alert_statistics(self, user_id: str = "default") -> Dict[str, Any]:
        """Récupère les statistiques des alertes"""
        try:
            with self._lock:
                user_alerts = [
                    alert for alert in self.active_alerts.values()
                    if alert.get("user_id") == user_id
                ]

                total_alerts = len(user_alerts)
                active_alerts = sum(1 for alert in user_alerts if alert.get("is_active", False))
                total_triggers = sum(alert.get("trigger_count", 0) for alert in user_alerts)

                return {
                    "total_alerts": total_alerts,
                    "active_alerts": active_alerts,
                    "inactive_alerts": total_alerts - active_alerts,
                    "total_triggers": total_triggers,
                    "last_updated": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Erreur récupération statistiques alertes: {e}")
            return {}


# Instance globale du service
economic_alerts_service = EconomicAlertsService()
