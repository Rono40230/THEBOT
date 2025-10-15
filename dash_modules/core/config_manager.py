"""
Configuration Manager - Gestionnaire de configuration unifié THEBOT
Centralisation de toutes les configurations dans un système cohérent
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .thebot_config import THEBOT_CONFIG

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Gestionnaire de configuration unifié pour THEBOT
    Centralise tous les paramètres de configuration
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._config_dir = Path(__file__).parent.parent / "config"
        self._config_dir.mkdir(exist_ok=True)

        self._config = {}
        self._load_default_config()
        self._load_from_files()

        self._initialized = True

    def _load_default_config(self):
        """Charge la configuration par défaut depuis thebot_config.py"""
        self._config = THEBOT_CONFIG.copy()

    def _load_from_files(self):
        """Charge les configurations depuis les fichiers"""

        # Charger api_config.json si existe (pour compatibilité)
        api_config_path = Path(__file__).parent.parent / "api_config.json"
        if api_config_path.exists():
            try:
                with open(api_config_path, 'r', encoding='utf-8') as f:
                    api_config = json.load(f)
                    self._merge_config(self._config, {"api_config": api_config})
                    logger.debug("Configuration API chargée depuis api_config.json")
            except Exception as e:
                logger.warning(f"Erreur chargement api_config.json: {e}")

        # Charger .env si existe
        self._load_env_variables()

    def _load_env_variables(self):
        """Charge les variables d'environnement"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            logger.warning("python-dotenv non installé, variables d'environnement ignorées")

        # API Keys
        if os.getenv("COINGECKO_API_KEY"):
            self._config["providers"]["coingecko"]["api_key"] = os.getenv("COINGECKO_API_KEY")

        if os.getenv("TWELVE_DATA_API_KEY"):
            self._config["providers"]["twelve_data"]["api_key"] = os.getenv("TWELVE_DATA_API_KEY")
            self._config["providers"]["twelve_data"]["enabled"] = True

        if os.getenv("OPENAI_API_KEY"):
            self._config["ai"]["providers"]["openai"]["api_key"] = os.getenv("OPENAI_API_KEY")

        if os.getenv("ANTHROPIC_API_KEY"):
            self._config["ai"]["providers"]["anthropic"]["api_key"] = os.getenv("ANTHROPIC_API_KEY")

        # Application
        if os.getenv("THEBOT_DEBUG"):
            self._config["app"]["debug"] = os.getenv("THEBOT_DEBUG").lower() == "true"

        if os.getenv("THEBOT_PORT"):
            self._config["app"]["port"] = int(os.getenv("THEBOT_PORT"))

    def _merge_config(self, base: Dict, update: Dict) -> None:
        """Fusionne récursivement deux dictionnaires de configuration"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration"""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Définit une valeur de configuration"""
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_section(self, section: str) -> Dict[str, Any]:
        """Récupère une section complète de configuration"""
        return self._config.get(section, {})

    def save_to_file(self, filepath: str) -> None:
        """Sauvegarde la configuration actuelle dans un fichier"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration sauvegardée dans {filepath}")
        except Exception as e:
            logger.error(f"Erreur sauvegarde configuration: {e}")

    def reload(self) -> None:
        """Recharge la configuration"""
        self._config = {}
        self._load_default_config()
        self._load_from_files()
        logger.info("Configuration rechargée")

    def get_all_config(self) -> Dict[str, Any]:
        """Retourne toute la configuration (pour debugging)"""
        return self._config.copy()

    def get_provider(self, category: str, default_provider: str = None):
        """
        Méthode de compatibilité pour récupérer un provider
        Utilise le mapping des catégories vers les providers
        """
        # Mapping des catégories vers les providers dans la nouvelle config
        provider_mapping = {
            "crypto": "coingecko",
            "stocks": "twelve_data",
            "forex": "twelve_data",
            "news": "rss_news",
            "economic": "economic_calendar"
        }

        provider_name = provider_mapping.get(category, category)

        if self.get(f"providers.{provider_name}.enabled"):
            return provider_name
        elif default_provider:
            return default_provider

        return None


# Instance globale
global_config = ConfigManager()


def get_global_config() -> ConfigManager:
    """Retourne l'instance globale du gestionnaire de configuration"""
    return global_config


def get_config_value(key: str, default: Any = None) -> Any:
    """Fonction utilitaire pour récupérer une valeur de configuration"""
    return global_config.get(key, default)


def set_config_value(key: str, value: Any) -> None:
    """Fonction utilitaire pour définir une valeur de configuration"""
    global_config.set(key, value)
    def get_api_config_modal(self):
        """
        Retourne le modal de configuration des APIs
        Méthode utilisée par le layout manager pour afficher le modal de config
        """
        import dash_bootstrap_components as dbc
        from dash import html
        
        return dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Configuration des APIs")),
                dbc.ModalBody([
                    html.P("Configuration des clés API pour THEBOT", className="mb-3"),
                    html.Div([
                        html.Label("Clé API Binance:", className="form-label"),
                        dbc.Input(
                            type="password",
                            id="binance-api-key",
                            placeholder="Entrez votre clé API Binance",
                            className="mb-2"
                        ),
                        html.Label("Clé API Twelve Data:", className="form-label"),
                        dbc.Input(
                            type="password", 
                            id="twelve-data-api-key",
                            placeholder="Entrez votre clé API Twelve Data",
                            className="mb-2"
                        ),
                        html.Label("Clé API CoinGecko:", className="form-label"),
                        dbc.Input(
                            type="password",
                            id="coingecko-api-key", 
                            placeholder="Entrez votre clé API CoinGecko",
                            className="mb-2"
                        ),
                    ])
                ]),
                dbc.ModalFooter([
                    dbc.Button("Annuler", id="cancel-api-config", className="ms-auto"),
                    dbc.Button("Sauvegarder", id="save-api-config", color="primary"),
                ]),
            ],
            id="api-config-modal",
            size="lg",
            is_open=False,
        )
