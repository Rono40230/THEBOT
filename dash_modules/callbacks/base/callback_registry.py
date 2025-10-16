from src.thebot.core.logger import logger
"""
Callback Registry - Registre centralisé de tous les callbacks
Gère l'enregistrement, le suivi et la validation des callbacks
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class CallbackRegistry:
    """
    Registre centralisé pour tous les callbacks de l'application.

    Fonctionnalités :
    - Enregistrement des callbacks avec métadonnées
    - Détection des conflits
    - Statistiques et monitoring
    - Validation de l'intégrité
    """

    def __init__(self):
        """Initialise le registre de callbacks."""
        self._callbacks: Dict[str, Dict[str, Any]] = {}
        self._managers: Dict[str, List[str]] = defaultdict(list)
        self._inputs_outputs: Dict[str, Dict[str, List[str]]] = defaultdict(dict)
        logger.info("🔧 CallbackRegistry initialisé")

    def register_callback(
        self,
        manager_name: str,
        callback_id: str,
        inputs: List[str],
        outputs: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Enregistre un callback dans le registre.

        Args:
            manager_name: Nom du gestionnaire
            callback_id: Identifiant unique du callback
            inputs: Liste des IDs d'entrée
            outputs: Liste des IDs de sortie
            metadata: Métadonnées optionnelles
        """
        full_id = f"{manager_name}.{callback_id}"

        if full_id in self._callbacks:
            logger.warning(f"⚠️ Callback déjà enregistré: {full_id}")
            return

        callback_info = {
            "manager": manager_name,
            "id": callback_id,
            "inputs": inputs,
            "outputs": outputs,
            "metadata": metadata or {},
            "registered_at": "now"  # TODO: utiliser datetime
        }

        self._callbacks[full_id] = callback_info
        self._managers[manager_name].append(callback_id)
        self._inputs_outputs[full_id]["inputs"] = inputs
        self._inputs_outputs[full_id]["outputs"] = outputs

        logger.debug(f"📝 Callback enregistré: {full_id}")

    def get_callback_info(self, manager_name: str, callback_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'un callback.

        Args:
            manager_name: Nom du gestionnaire
            callback_id: ID du callback

        Returns:
            Informations du callback ou None
        """
        full_id = f"{manager_name}.{callback_id}"
        return self._callbacks.get(full_id)

    def get_callbacks_by_manager(self, manager_name: str) -> List[str]:
        """
        Retourne tous les callbacks d'un gestionnaire.

        Args:
            manager_name: Nom du gestionnaire

        Returns:
            Liste des IDs de callbacks
        """
        return self._managers.get(manager_name, []).copy()

    def get_all_callbacks(self) -> Dict[str, Dict[str, Any]]:
        """
        Retourne tous les callbacks enregistrés.

        Returns:
            Dictionnaire de tous les callbacks
        """
        return self._callbacks.copy()

    def validate_no_conflicts(self) -> List[str]:
        """
        Valide qu'il n'y a pas de conflits entre callbacks.
        Un conflit existe si deux callbacks écrivent dans la même sortie.

        Returns:
            Liste des conflits détectés
        """
        output_to_callbacks: Dict[str, List[str]] = defaultdict(list)

        for full_id, info in self._callbacks.items():
            for output in info["outputs"]:
                output_to_callbacks[output].append(full_id)

        conflicts = []
        for output, callbacks in output_to_callbacks.items():
            if len(callbacks) > 1:
                conflicts.append(f"Conflit sur {output}: {callbacks}")

        if conflicts:
            logger.warning(f"⚠️ {len(conflicts)} conflits détectés")
            for conflict in conflicts:
                logger.warning(f"  - {conflict}")
        else:
            logger.debug("✅ Aucun conflit détecté")

        return conflicts

    def get_statistics(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du registre.

        Returns:
            Dictionnaire avec les statistiques
        """
        total_callbacks = len(self._callbacks)
        managers = list(self._managers.keys())
        conflicts = self.validate_no_conflicts()

        return {
            "total_callbacks": total_callbacks,
            "managers": managers,
            "manager_count": len(managers),
            "conflicts": conflicts,
            "conflict_count": len(conflicts),
            "callbacks_per_manager": {
                manager: len(callbacks)
                for manager, callbacks in self._managers.items()
            }
        }

    def clear(self) -> None:
        """Vide le registre (pour les tests)."""
        self._callbacks.clear()
        self._managers.clear()
        self._inputs_outputs.clear()
        logger.info("🧹 Registre vidé")


# Instance globale du registre
_callback_registry = None

def get_callback_registry() -> CallbackRegistry:
    """Retourne l'instance globale du registre."""
    global _callback_registry
    if _callback_registry is None:
        _callback_registry = CallbackRegistry()
    return _callback_registry
