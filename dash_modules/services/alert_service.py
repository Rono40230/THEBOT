from src.thebot.core.logger import logger
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
from .service_interfaces import ServiceInterface

logger = logging.getLogger(__name__)


class AlertService(ServiceInterface):
    """
    Service de gestion des alertes de prix et notifications
    Utilise SQLAlchemy pour la persistance des données
    Implémente ServiceInterface pour la standardisation
    """

    def __init__(self):
        """Initialise le service d'alertes"""
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        self.alerts = {}

    @property
    def service_name(self) -> str:
        """Nom du service"""
        return "AlertService"

    @property
    def version(self) -> str:
        """Version du service"""
        return "1.0.0"

    def initialize(self) -> bool:
        """
        Initialise le service et ses dépendances.
        
        Returns:
            bool: True si l'initialisation a réussi
        """
        try:
            # Tester la connexion à la base de données
            with get_db_session() as session:
                session.execute("SELECT 1")
            self._initialized = True
            self.logger.info("AlertService initialisé avec succès")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation d'AlertService: {e}")
            return False

    def shutdown(self) -> bool:
        """
        Arrête proprement le service et libère les ressources.
        
        Returns:
            bool: True si l'arrêt s'est bien passé
        """
        try:
            self._initialized = False
            self.logger.info("AlertService arrêté proprement")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'arrêt d'AlertService: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie l'état de santé du service.
        
        Returns:
            Dict avec le statut et les métriques du service
        """
        try:
            with get_db_session() as session:
                # Compter les alertes actives
                active_alerts = session.query(Alert).filter(Alert.is_active == True).count()

            return {
                "status": "healthy" if self._initialized else "unhealthy",
                "service": self.service_name,
                "version": self.version,
                "active_alerts": active_alerts,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": self.service_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_service_info(self) -> Dict[str, Any]:
        """
        Retourne les informations générales sur le service.
        
        Returns:
            Dict avec les informations du service
        """
        return {
            "name": self.service_name,
            "version": self.version,
            "description": "Service de gestion des alertes de prix et notifications",
            "initialized": self._initialized,
            "features": ["price_alerts", "notification_management", "database_persistence"]
        }
