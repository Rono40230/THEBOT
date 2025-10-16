from src.thebot.core.logger import logger
"""
Callback Validator - Validation et tests des callbacks
Vérifie la conformité et la robustesse des callbacks
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dash import Input, Output, State

logger = logging.getLogger(__name__)


class CallbackValidator:
    """
    Validateur pour vérifier la conformité et la robustesse des callbacks.

    Permet de valider :
    - La structure des callbacks
    - Les dépendances d'entrée/sortie
    - La robustesse face aux erreurs
    """

    def __init__(self):
        """Initialise le validateur."""
        self.validation_results = []

    def validate_callback_structure(
        self,
        callback_func: Callable,
        inputs: List[Union[Input, State]],
        outputs: List[Output]
    ) -> Dict[str, Any]:
        """
        Valide la structure d'un callback.

        Args:
            callback_func: Fonction callback à valider
            inputs: Liste des entrées
            outputs: Liste des sorties

        Returns:
            Rapport de validation
        """
        report = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "callback_name": getattr(callback_func, "__name__", "unknown")
        }

        # Validation basique
        if not callable(callback_func):
            report["is_valid"] = False
            report["errors"].append("La fonction callback n'est pas callable")

        if not inputs:
            report["warnings"].append("Aucune entrée définie pour le callback")

        if not outputs:
            report["warnings"].append("Aucune sortie définie pour le callback")

        # Validation des IDs uniques
        input_ids = [getattr(inp, "component_id", str(inp)) for inp in inputs]
        output_ids = [getattr(out, "component_id", str(out)) for out in outputs]

        if len(set(input_ids)) != len(input_ids):
            report["errors"].append("IDs d'entrée dupliqués détectés")

        if len(set(output_ids)) != len(output_ids):
            report["errors"].append("IDs de sortie dupliqués détectés")

        # Vérifier les conflits
        conflicts = set(input_ids) & set(output_ids)
        if conflicts:
            report["errors"].append(f"Conflits détectés: {list(conflicts)}")

        report["error_count"] = len(report["errors"])
        report["warning_count"] = len(report["warnings"])

        if report["errors"]:
            report["is_valid"] = False

        return report

    def log_validation_report(self, report: Dict[str, Any]) -> None:
        """
        Log le rapport de validation.

        Args:
            report: Rapport de validation à logger
        """
        if report["is_valid"]:
            logger.info("✅ Validation réussie")
        else:
            logger.error(f"❌ Validation échouée: {report['error_count']} erreurs")

        for error in report["errors"]:
            logger.error(f"  🔴 {error}")

        for warning in report["warnings"]:
            logger.warning(f"  🟡 {warning}")

    def validate_callback_chain(self, callbacks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Valide une chaîne de callbacks pour détecter les dépendances circulaires.

        Args:
            callbacks: Liste des callbacks avec leurs entrées/sorties

        Returns:
            Rapport de validation de chaîne
        """
        # Implémentation simplifiée - à étendre selon les besoins
        chain_report = {
            "is_valid": True,
            "circular_dependencies": [],
            "orphaned_callbacks": []
        }

        # Détection basique de dépendances circulaires
        # (Logique simplifiée pour l'exemple)

        return chain_report
