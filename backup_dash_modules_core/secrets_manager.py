from src.thebot.core.logger import logger
"""
Gestion des secrets et configuration sécurisée pour THEBOT
Utilise les variables d'environnement pour stocker les secrets
"""

import os
import logging
from typing import Any, Dict, Optional, Union
from pathlib import Path
import json

from thebot.services.error_handler import ConfigurationError, ErrorSeverity

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    Gestionnaire de secrets et configuration sécurisée
    Priorise les variables d'environnement, avec fallback sur les fichiers de config
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialise le gestionnaire de secrets

        Args:
            env_file: Chemin vers un fichier .env optionnel
        """
        self.logger = logging.getLogger(__name__)
        self._secrets: Dict[str, Any] = {}
        self._loaded = False

        # Charger le fichier .env s'il existe
        if env_file and Path(env_file).exists():
            self._load_env_file(env_file)

        # Charger les variables d'environnement
        self._load_environment_variables()

    def _load_env_file(self, env_file: str):
        """Charge un fichier .env"""
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            # Ne pas écraser les variables d'environnement existantes
                            if key not in os.environ:
                                os.environ[key] = value
            self.logger.info(f"Fichier .env chargé: {env_file}")
        except Exception as e:
            self.logger.warning(f"Erreur lors du chargement du fichier .env: {e}")

    def _load_environment_variables(self):
        """Charge les variables d'environnement pertinentes"""
        # Liste des secrets/clés à charger
        secret_keys = [
            # APIs externes
            'BINANCE_API_KEY', 'BINANCE_API_SECRET',
            'COINGECKO_API_KEY', 'COINGECKO_PRO_API_KEY',
            'TWELVE_DATA_API_KEY',
            'ALPHA_VANTAGE_API_KEY',
            'FINNHUB_API_KEY',
            'FMP_API_KEY',

            # Base de données
            'DATABASE_URL', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME',

            # Application
            'SECRET_KEY', 'JWT_SECRET_KEY',
            'ENCRYPTION_KEY',

            # Services externes
            'REDIS_URL', 'REDIS_PASSWORD',
            'SMTP_SERVER', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD',
            'SLACK_WEBHOOK_URL', 'DISCORD_WEBHOOK_URL',

            # Configuration
            'LOG_LEVEL', 'DEBUG_MODE',
            'MAX_WORKERS', 'REQUEST_TIMEOUT',
        ]

        for key in secret_keys:
            value = os.getenv(key)
            if value is not None:
                self._secrets[key] = value

        self._loaded = True
        self.logger.info(f"{len(self._secrets)} secrets chargés depuis les variables d'environnement")

    def get_secret(self, key: str, default: Any = None, required: bool = False) -> Any:
        """
        Récupère un secret

        Args:
            key: Clé du secret
            default: Valeur par défaut
            required: Si True, lève une exception si le secret n'existe pas

        Returns:
            Valeur du secret

        Raises:
            ConfigurationError: Si le secret est requis mais n'existe pas
        """
        value = self._secrets.get(key, os.getenv(key, default))

        if required and value is None:
            raise ConfigurationError(
                f"Secret requis manquant: {key}",
                severity=ErrorSeverity.CRITICAL,
                context={"secret_key": key}
            )

        return value

    def set_secret(self, key: str, value: Any, persist: bool = False):
        """
        Définit un secret

        Args:
            key: Clé du secret
            value: Valeur du secret
            persist: Si True, persiste dans les variables d'environnement
        """
        self._secrets[key] = value

        if persist:
            os.environ[key] = str(value)

        self.logger.debug(f"Secret défini: {key}")

    def get_database_config(self) -> Dict[str, Any]:
        """
        Retourne la configuration de base de données

        Returns:
            Configuration de base de données
        """
        return {
            'url': self.get_secret('DATABASE_URL', required=True),
            'user': self.get_secret('DB_USER'),
            'password': self.get_secret('DB_PASSWORD'),
            'host': self.get_secret('DB_HOST'),
            'port': int(self.get_secret('DB_PORT', 5432)),
            'database': self.get_secret('DB_NAME'),
        }

    def get_api_keys(self, provider: str) -> Dict[str, str]:
        """
        Retourne les clés API pour un provider

        Args:
            provider: Nom du provider

        Returns:
            Dictionnaire avec les clés API
        """
        provider_keys = {
            'binance': ['BINANCE_API_KEY', 'BINANCE_API_SECRET'],
            'coingecko': ['COINGECKO_API_KEY', 'COINGECKO_PRO_API_KEY'],
            'twelve_data': ['TWELVE_DATA_API_KEY'],
            'alpha_vantage': ['ALPHA_VANTAGE_API_KEY'],
            'finnhub': ['FINNHUB_API_KEY'],
            'fmp': ['FMP_API_KEY'],
        }

        keys = provider_keys.get(provider.lower(), [])
        return {key: self.get_secret(key) for key in keys if self.get_secret(key)}

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Valide la configuration et retourne un rapport

        Returns:
            Rapport de validation
        """
        report = {
            'valid': True,
            'missing_required': [],
            'warnings': [],
            'recommendations': []
        }

        # Vérifier les secrets requis
        required_secrets = ['DATABASE_URL', 'SECRET_KEY']

        for secret in required_secrets:
            if not self.get_secret(secret):
                report['valid'] = False
                report['missing_required'].append(secret)

        # Vérifications optionnelles mais recommandées
        recommended_secrets = [
            'JWT_SECRET_KEY',
            'ENCRYPTION_KEY',
            'REDIS_URL'
        ]

        for secret in recommended_secrets:
            if not self.get_secret(secret):
                report['recommendations'].append(f"Considérez définir {secret}")

        # Vérifier la sécurité des clés API
        api_keys = ['BINANCE_API_KEY', 'COINGECKO_API_KEY', 'TWELVE_DATA_API_KEY']
        found_api_keys = [key for key in api_keys if self.get_secret(key)]

        if not found_api_keys:
            report['warnings'].append("Aucune clé API configurée - fonctionnalités limitées")

        return report

    def mask_secret(self, value: str, visible_chars: int = 4) -> str:
        """
        Masque un secret pour l'affichage

        Args:
            value: Valeur à masquer
            visible_chars: Nombre de caractères visibles

        Returns:
            Valeur masquée
        """
        if not value or len(value) <= visible_chars:
            return "*" * len(value) if value else ""

        return value[:visible_chars] + "*" * (len(value) - visible_chars)

    def get_all_secrets_info(self) -> Dict[str, str]:
        """
        Retourne les informations sur tous les secrets (masqués)

        Returns:
            Dictionnaire avec les secrets masqués
        """
        return {key: self.mask_secret(str(value)) for key, value in self._secrets.items()}


# Instance globale du gestionnaire de secrets
secrets_manager = SecretsManager()

# Charger automatiquement le fichier .env s'il existe
env_file = Path('.env')
if env_file.exists():
    secrets_manager = SecretsManager(str(env_file))
