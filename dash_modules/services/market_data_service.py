from src.thebot.core.logger import logger
"""
Market Data Service - Gestion des données de marché
Utilise la base de données SQLAlchemy et les data providers
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models.base import get_db_session
from ..models.market_data import MarketData, PriceHistory
from ..data_providers.real_data_manager import real_data_manager
from .service_interfaces import ServiceInterface

logger = logging.getLogger(__name__)


class MarketDataService(ServiceInterface):
    """
    Service de gestion des données de marché
    Combine base de données et data providers externes
    Implémente ServiceInterface pour la standardisation
    """

    def __init__(self):
        """Initialise le service de données de marché"""
        self.logger = logging.getLogger(__name__)
        self._initialized = False

    @property
    def service_name(self) -> str:
        """Nom du service"""
        return "MarketDataService"

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

            # Tester les data providers
            if not real_data_manager.is_available():
                self.logger.warning("RealDataManager n'est pas disponible")

            self._initialized = True
            self.logger.info("MarketDataService initialisé avec succès")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation de MarketDataService: {e}")
            return False

    def shutdown(self) -> bool:
        """
        Arrête proprement le service et libère les ressources.
        
        Returns:
            bool: True si l'arrêt s'est bien passé
        """
        try:
            self._initialized = False
            self.logger.info("MarketDataService arrêté proprement")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'arrêt de MarketDataService: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie l'état de santé du service.
        
        Returns:
            Dict avec le statut et les métriques du service
        """
        try:
            with get_db_session() as session:
                # Compter les entrées de données de marché
                market_data_count = session.query(MarketData).count()

            data_providers_status = real_data_manager.is_available()

            return {
                "status": "healthy" if self._initialized else "unhealthy",
                "service": self.service_name,
                "version": self.version,
                "market_data_count": market_data_count,
                "data_providers_available": data_providers_status,
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
            "description": "Service de gestion des données de marché",
            "initialized": self._initialized,
            "features": ["market_data_retrieval", "price_history", "data_caching", "multi_provider_support"]
        }
