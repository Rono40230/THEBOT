from ..core.logger import logger
"""
Gestion unifiée des erreurs pour THEBOT
Système de gestion d'erreurs avec niveaux de sévérité et logging intégré
"""

import logging
import traceback
from typing import Any, Dict, Optional, Callable
from enum import Enum
from functools import wraps
import sys


class ErrorSeverity(Enum):
    """Niveaux de sévérité des erreurs"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ThebotException(Exception):
    """
    Exception de base pour THEBOT
    Toutes les exceptions personnalisées héritent de cette classe
    """

    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.ERROR,
                 context: Optional[Dict[str, Any]] = None, cause: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.context = context or {}
        self.cause = cause

    def __str__(self):
        context_str = f" | Context: {self.context}" if self.context else ""
        cause_str = f" | Cause: {self.cause}" if self.cause else ""
        return f"[{self.severity.value}] {self.message}{context_str}{cause_str}"


class ConfigurationError(ThebotException):
    """Erreur de configuration"""
    pass


class ValidationError(ThebotException):
    """Erreur de validation des données"""
    pass


class APIError(ThebotException):
    """Erreur d'API externe"""
    pass


class DatabaseError(ThebotException):
    """Erreur de base de données"""
    pass


class RateLimitError(ThebotException):
    """Erreur de limite de taux"""
    pass


class AuthenticationError(ThebotException):
    """Erreur d'authentification"""
    pass


class AuthorizationError(ThebotException):
    """Erreur d'autorisation"""
    pass


class ErrorHandler:
    """
    Gestionnaire unifié des erreurs
    Centralise la gestion et le logging des erreurs
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._error_counts: Dict[str, int] = {}
        self._setup_default_logging()

    def _setup_default_logging(self):
        """Configure le logging par défaut si nécessaire"""
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None,
                    severity: Optional[ErrorSeverity] = None) -> str:
        """
        Gère une erreur de manière unifiée

        Args:
            error: L'exception à gérer
            context: Contexte supplémentaire
            severity: Sévérité de l'erreur (auto-détectée si None)

        Returns:
            ID de l'erreur pour tracking
        """
        # Déterminer la sévérité
        if severity is None:
            if isinstance(error, ThebotException):
                severity = error.severity
            elif isinstance(error, (ValueError, TypeError)):
                severity = ErrorSeverity.WARNING
            elif isinstance(error, (ConnectionError, TimeoutError)):
                severity = ErrorSeverity.ERROR
            else:
                severity = ErrorSeverity.CRITICAL

        # Créer l'ID d'erreur
        error_id = f"{severity.value}_{id(error)}"

        # Compter les erreurs
        error_type = type(error).__name__
        self._error_counts[error_type] = self._error_counts.get(error_type, 0) + 1

        # Préparer le message
        context = context or {}
        if isinstance(error, ThebotException) and error.context:
            context.update(error.context)

        message = str(error)
        if context:
            message += f" | Context: {context}"

        # Logger selon la sévérité
        log_method = {
            ErrorSeverity.DEBUG: self.logger.debug,
            ErrorSeverity.INFO: self.logger.info,
            ErrorSeverity.WARNING: self.logger.warning,
            ErrorSeverity.ERROR: self.logger.error,
            ErrorSeverity.CRITICAL: self.logger.critical,
        }.get(severity, self.logger.error)

        log_method(f"[{error_id}] {message}")

        # Logger la traceback pour les erreurs critiques
        if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            self.logger.debug(f"[{error_id}] Traceback: {traceback.format_exc()}")

        return error_id

    def get_error_stats(self) -> Dict[str, int]:
        """
        Retourne les statistiques d'erreurs

        Returns:
            Dictionnaire avec les compteurs d'erreurs par type
        """
        return self._error_counts.copy()

    def reset_error_stats(self):
        """Remet à zéro les statistiques d'erreurs"""
        self._error_counts.clear()

    def create_error_response(self, error: Exception, error_id: str,
                            include_traceback: bool = False) -> Dict[str, Any]:
        """
        Crée une réponse d'erreur standardisée

        Args:
            error: L'exception
            error_id: ID de l'erreur
            include_traceback: Inclure la traceback (uniquement en développement)

        Returns:
            Réponse d'erreur formatée
        """
        response = {
            "error": {
                "id": error_id,
                "message": str(error),
                "type": type(error).__name__,
                "severity": ErrorSeverity.ERROR.value
            }
        }

        if isinstance(error, ThebotException):
            response["error"]["severity"] = error.severity.value
            if error.context:
                response["error"]["context"] = error.context

        if include_traceback:
            response["error"]["traceback"] = traceback.format_exc()

        return response


def handle_exception(severity: ErrorSeverity = ErrorSeverity.ERROR,
                    context: Optional[Dict[str, Any]] = None):
    """
    Décorateur pour gérer automatiquement les exceptions

    Args:
        severity: Sévérité de l'erreur
        context: Contexte supplémentaire

    Returns:
        Fonction décorée
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Obtenir l'instance globale du gestionnaire d'erreurs
                handler = ErrorHandler()
                error_id = handler.handle_error(e, context, severity)

                # Re-lever l'exception avec l'ID d'erreur
                if isinstance(e, ThebotException):
                    e.context = e.context or {}
                    e.context["error_id"] = error_id
                    raise e
                else:
                    # Wrapper dans une ThebotException
                    raise ThebotException(
                        str(e),
                        severity=severity,
                        context=context,
                        cause=e
                    ) from e

        return wrapper
    return decorator


# Instance globale du gestionnaire d'erreurs
error_handler = ErrorHandler()

# Fonction utilitaire pour logger une erreur
def log_error(error: Exception, severity: ErrorSeverity = ErrorSeverity.ERROR,
             context: Optional[Dict[str, Any]] = None) -> str:
    """
    Fonction utilitaire pour logger une erreur

    Args:
        error: L'exception à logger
        severity: Sévérité de l'erreur
        context: Contexte supplémentaire

    Returns:
        ID de l'erreur
    """
    return error_handler.handle_error(error, context, severity)
