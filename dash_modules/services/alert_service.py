"""
Alert Service - Gestion des alertes de prix et notifications
Utilise la base de données SQLAlchemy pour la persistance
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models.base import get_db_session
from ..models.alerts import Alert, PriceAlert

logger = logging.getLogger(__name__)


class AlertService:
    """
    Service de gestion des alertes de prix et notifications
    Utilise SQLAlchemy pour la persistance des données
    """

    def __init__(self):
        """Initialise le service d'alertes"""
        self.logger = logging.getLogger(__name__)

    def create_alert(self, symbol: str, alert_type: str, condition: str, 
                    value: float, message: str = None, user_id: int = 1) -> Alert:
        """
        Crée une nouvelle alerte

        Args:
            symbol: Symbole de l'actif (ex: 'BTC/USD')
            alert_type: Type d'alerte ('price', 'volume', etc.)
            condition: Condition ('above', 'below', 'crosses')
            value: Valeur de déclenchement
            message: Message personnalisé
            user_id: ID de l'utilisateur

        Returns:
            Alert: L'alerte créée
        """
        try:
            with get_db_session() as session:
                alert = Alert(
                    symbol=symbol,
                    alert_type=alert_type,
                    condition=condition,
                    value=value,
                    message=message or f"Alerte {alert_type} sur {symbol}",
                    user_id=user_id,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                session.add(alert)
                session.commit()
                session.refresh(alert)
                self.logger.info(f"Alerte créée: {alert.id} - {symbol}")
                return alert
        except Exception as e:
            self.logger.error(f"Erreur création alerte: {e}")
            raise

    def get_all_alerts(self, user_id: int = 1) -> List[Alert]:
        """Récupère toutes les alertes actives d'un utilisateur"""
        try:
            with get_db_session() as session:
                alerts = session.query(Alert).filter_by(
                    user_id=user_id,
                    is_active=True
                ).all()
                return alerts
        except Exception as e:
            self.logger.error(f"Erreur récupération alertes: {e}")
            return []

    def get_alert_by_id(self, alert_id: int, user_id: int = 1) -> Optional[Alert]:
        """Récupère une alerte par son ID"""
        try:
            with get_db_session() as session:
                return session.query(Alert).filter_by(
                    id=alert_id,
                    user_id=user_id
                ).first()
        except Exception as e:
            self.logger.error(f"Erreur récupération alerte {alert_id}: {e}")
            return None

    def update_alert(self, alert_id: int, **kwargs) -> bool:
        """Met à jour une alerte"""
        try:
            with get_db_session() as session:
                alert = session.query(Alert).filter_by(id=alert_id).first()
                if not alert:
                    return False

                for key, value in kwargs.items():
                    if hasattr(alert, key):
                        setattr(alert, key, value)

                alert.updated_at = datetime.utcnow()
                session.commit()
                self.logger.info(f"Alerte mise à jour: {alert_id}")
                return True
        except Exception as e:
            self.logger.error(f"Erreur mise à jour alerte {alert_id}: {e}")
            return False

    def delete_alert(self, alert_id: int, user_id: int = 1) -> bool:
        """Supprime une alerte (soft delete)"""
        try:
            with get_db_session() as session:
                alert = session.query(Alert).filter_by(
                    id=alert_id,
                    user_id=user_id
                ).first()
                if not alert:
                    return False

                alert.is_active = False
                alert.updated_at = datetime.utcnow()
                session.commit()
                self.logger.info(f"Alerte supprimée: {alert_id}")
                return True
        except Exception as e:
            self.logger.error(f"Erreur suppression alerte {alert_id}: {e}")
            return False

    def check_alerts(self, symbol: str, current_price: float) -> List[Dict[str, Any]]:
        """
        Vérifie si des alertes doivent être déclenchées pour un symbole

        Args:
            symbol: Symbole à vérifier
            current_price: Prix actuel

        Returns:
            Liste des alertes déclenchées
        """
        triggered_alerts = []
        try:
            alerts = self.get_all_alerts()
            for alert in alerts:
                if alert.symbol != symbol or alert.alert_type != 'price':
                    continue

                triggered = False
                if alert.condition == 'above' and current_price >= alert.value:
                    triggered = True
                elif alert.condition == 'below' and current_price <= alert.value:
                    triggered = True

                if triggered:
                    triggered_alerts.append({
                        'alert': alert,
                        'current_price': current_price,
                        'trigger_time': datetime.utcnow()
                    })

                    # Marquer comme déclenchée
                    self.update_alert(alert.id, is_active=False)

        except Exception as e:
            self.logger.error(f"Erreur vérification alertes pour {symbol}: {e}")

        return triggered_alerts

    def get_alerts_by_symbol(self, symbol: str, user_id: int = 1) -> List[Alert]:
        """Récupère les alertes pour un symbole spécifique"""
        try:
            with get_db_session() as session:
                return session.query(Alert).filter_by(
                    symbol=symbol,
                    user_id=user_id,
                    is_active=True
                ).all()
        except Exception as e:
            self.logger.error(f"Erreur récupération alertes pour {symbol}: {e}")
            return []


# Instance globale du service
alert_service = AlertService()
