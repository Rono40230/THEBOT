from .logger import logger
"""
Gestionnaire des alertes de prix avec persistance
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class AlertsManager:
    """Gestionnaire des alertes avec sauvegarde automatique"""

    def __init__(self, config_dir: str = "dashboard_configs"):
        self.config_dir = config_dir
        self.alerts_file = os.path.join(config_dir, "price_alerts.json")
        self.alerts: List[Dict[str, Any]] = []
        self._ensure_config_dir()
        self.load_alerts()

    def _ensure_config_dir(self):
        """S'assurer que le répertoire de configuration existe"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)

    def load_alerts(self) -> List[Dict[str, Any]]:
        """Charger les alertes depuis le fichier JSON"""
        try:
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, "r", encoding="utf-8") as f:
                    self.alerts = json.load(f)
                logger.info(
                    f"✅ {len(self.alerts)} alertes chargées depuis {self.alerts_file}"
                )
            else:
                self.alerts = []
                logger.info(
                    f"📝 Aucun fichier d'alertes trouvé, initialisation avec une liste vide"
                )
        except Exception as e:
            logger.info(f"❌ Erreur lors du chargement des alertes: {e}")
            self.alerts = []

        return self.alerts

    def save_alerts(self) -> bool:
        """Sauvegarder les alertes dans le fichier JSON"""
        try:
            with open(self.alerts_file, "w", encoding="utf-8") as f:
                json.dump(self.alerts, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 {len(self.alerts)} alertes sauvegardées dans {self.alerts_file}")
            return True
        except Exception as e:
            logger.info(f"❌ Erreur lors de la sauvegarde des alertes: {e}")
            return False

    def add_alert(
        self, symbol: str, alert_type: str, price: float, message: str = ""
    ) -> Dict[str, Any]:
        """Ajouter une nouvelle alerte"""
        alert = {
            "id": len(self.alerts),
            "symbol": symbol,
            "type": alert_type,
            "price": price,
            "message": message,
            "created": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "active": True,
        }

        self.alerts.append(alert)
        self.save_alerts()  # Sauvegarde automatique
        logger.info(f"✅ Nouvelle alerte ajoutée: {symbol} {alert_type} {price}")
        return alert

    def get_all_alerts(self) -> List[Dict[str, Any]]:
        """Récupérer toutes les alertes"""
        return self.alerts

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Récupérer seulement les alertes actives"""
        return [alert for alert in self.alerts if alert.get("active", True)]

    def get_alerts_by_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """Récupérer les alertes pour un symbole spécifique"""
        return [
            alert
            for alert in self.alerts
            if alert["symbol"] == symbol and alert.get("active", True)
        ]

    def delete_alert(self, alert_id: int) -> bool:
        """Supprimer une alerte par son ID"""
        try:
            # Trouver l'alerte par ID
            alert_to_remove = None
            for alert in self.alerts:
                if alert["id"] == alert_id:
                    alert_to_remove = alert
                    break

            if alert_to_remove:
                self.alerts.remove(alert_to_remove)
                self.save_alerts()  # Sauvegarde automatique
                logger.info(f"✅ Alerte {alert_id} supprimée")
                return True
            else:
                logger.info(f"❌ Alerte {alert_id} non trouvée")
                return False
        except Exception as e:
            logger.info(f"❌ Erreur lors de la suppression de l'alerte {alert_id}: {e}")
            return False

    def update_alert(self, alert_id: int, **updates) -> bool:
        """Mettre à jour une alerte"""
        try:
            for alert in self.alerts:
                if alert["id"] == alert_id:
                    alert.update(updates)
                    self.save_alerts()  # Sauvegarde automatique
                    logger.info(f"✅ Alerte {alert_id} mise à jour")
                    return True

            logger.info(f"❌ Alerte {alert_id} non trouvée pour mise à jour")
            return False
        except Exception as e:
            logger.info(f"❌ Erreur lors de la mise à jour de l'alerte {alert_id}: {e}")
            return False

    def get_alerts_count(self) -> int:
        """Récupérer le nombre d'alertes actives"""
        return len(self.get_active_alerts())

    def clear_all_alerts(self) -> bool:
        """Supprimer toutes les alertes"""
        try:
            self.alerts = []
            self.save_alerts()
            logger.info("✅ Toutes les alertes ont été supprimées")
            return True
        except Exception as e:
            logger.info(f"❌ Erreur lors de la suppression de toutes les alertes: {e}")
            return False


# Instance globale du gestionnaire d'alertes
alerts_manager = AlertsManager()
