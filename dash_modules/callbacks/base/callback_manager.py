from src.thebot.core.logger import logger
"""
Callback Manager - Classe de base pour tous les gestionnaires de callbacks
Fournit l'interface commune et les fonctionnalités de base
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CallbackManager(ABC):
    """
    Classe de base abstraite pour tous les gestionnaires de callbacks.

    Fournit l'interface commune et les fonctionnalités de base :
    - Enregistrement des callbacks
    - Logging et statistiques
    - Validation des dépendances
    """

    def __init__(self, app, name: str):
        """
        Initialise le gestionnaire de callbacks.

        Args:
            app: Instance de l'application Dash
            name: Nom du gestionnaire (pour logging)
        """
        self.app = app
        self.name = name
        self._registered_callbacks: List[str] = []
        logger.info(f"🔧 {self.name} initialisé")

    @abstractmethod
    def register_all_callbacks(self) -> None:
        """
        Enregistre tous les callbacks gérés par cette classe.
        Doit être implémenté par chaque sous-classe.
        """
        pass

    def register_callback(self, callback_function, callback_id: str) -> None:
        """
        Enregistre un callback dans la liste des callbacks gérés.

        Args:
            callback_function: Fonction callback à enregistrer
            callback_id: Identifiant unique du callback
        """
        if callback_id not in self._registered_callbacks:
            self._registered_callbacks.append(callback_id)
            logger.debug(f"📝 Callback enregistré: {callback_id}")
        else:
            logger.warning(f"⚠️ Callback déjà enregistré: {callback_id}")

    def get_callback_count(self) -> int:
        """Retourne le nombre de callbacks enregistrés."""
        return len(self._registered_callbacks)

    def get_registered_callbacks(self) -> List[str]:
        """Retourne la liste des callbacks enregistrés."""
        return self._registered_callbacks.copy()

    def log_callback_registration(self) -> None:
        """Log l'état d'enregistrement des callbacks."""
        count = self.get_callback_count()
        logger.info(f"�� {self.name}: {count} callbacks enregistrés")

        if logger.isEnabledFor(logging.DEBUG):
            for callback_id in self._registered_callbacks:
                logger.debug(f"  - {callback_id}")

    def validate_dependencies(self) -> bool:
        """
        Valide que toutes les dépendances nécessaires sont disponibles.
        Peut être overriden par les sous-classes pour des validations spécifiques.

        Returns:
            True si toutes les dépendances sont valides
        """
        # Validation de base : vérifier que l'app Dash est disponible
        if not hasattr(self.app, 'callback'):
            logger.error(f"❌ {self.name}: Application Dash invalide")
            return False

        logger.debug(f"✅ {self.name}: Dépendances validées")
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du gestionnaire.

        Returns:
            Dictionnaire avec les statistiques
        """
        return {
            "name": self.name,
            "callback_count": self.get_callback_count(),
            "registered_callbacks": self.get_registered_callbacks(),
            "dependencies_valid": self.validate_dependencies()
        }
