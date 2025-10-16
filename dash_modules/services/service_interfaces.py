"""
Interfaces communes pour les services THEBOT
Architecture modulaire avec pattern Interface/Service
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ServiceInterface(ABC):
    """
    Interface abstraite pour tous les services THEBOT.

    Cette interface définit le contrat commun que tous les services doivent respecter,
    permettant une interchangeabilité et une maintenance facilitée.
    """

    @property
    @abstractmethod
    def service_name(self) -> str:
        """Nom du service"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version du service"""
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialise le service et ses dépendances.

        Returns:
            bool: True si l'initialisation a réussi
        """
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """
        Arrête proprement le service et libère les ressources.

        Returns:
            bool: True si l'arrêt s'est bien passé
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie l'état de santé du service.

        Returns:
            Dict avec le statut et les métriques du service
        """
        pass

    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """
        Retourne les informations générales sur le service.

        Returns:
            Dict avec les informations du service
        """
        pass
