"""
Config Manager - Version simplifiée pour compatibilité
Fournit les fonctions nécessaires aux modules UI restants
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional


class GlobalConfig:
    """Configuration globale simplifiée"""

    def __init__(self):
        self._config = {
            "providers": {
                "crypto": "coingecko",
                "forex": "twelve_data",
                "stocks": "yahoo_finance"
            },
            "api_keys": {},
            "features": {
                "ai_trading": True,
                "news_aggregation": True,
                "alerts": True
            }
        }
        self._load_env_vars()

    def _load_env_vars(self):
        """Charge les variables d'environnement"""
        # API Keys
        api_keys = {}
        for key in ["BINANCE_API_KEY", "COINGECKO_API_KEY", "TWELVE_DATA_API_KEY"]:
            value = os.getenv(key)
            if value:
                api_keys[key.lower()] = value

        self._config["api_keys"] = api_keys

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

    def get_all_config(self) -> Dict[str, Any]:
        """Retourne toute la configuration"""
        return self._config.copy()


# Instance globale
_global_config = GlobalConfig()


def get_global_config() -> GlobalConfig:
    """Retourne l'instance globale de configuration"""
    return _global_config