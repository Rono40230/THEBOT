from src.thebot.core.logger import logger
"""
Data Service - Service générique pour l'accès aux données
Abstraction des différents data providers
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..data_providers.real_data_manager import real_data_manager

logger = logging.getLogger(__name__)


class DataService:
    """
    Service générique pour l'accès aux données de marché
    Abstraction des différents data providers (crypto, forex, stocks, etc.)
    """

    def __init__(self):
        self.real_data_manager = real_data_manager

    def get_crypto_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Récupère le prix d'une crypto-monnaie"""
        try:
            return self.real_data_manager.get_crypto_price(symbol)
        except Exception as e:
            logger.error(f"Erreur récupération prix crypto {symbol}: {e}")
            return None

    def get_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Récupère le prix d'une action"""
        try:
            return self.real_data_manager.get_stock_price(symbol)
        except Exception as e:
            logger.error(f"Erreur récupération prix action {symbol}: {e}")
            return None

    def get_forex_rate(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Récupère le taux de change forex"""
        try:
            return self.real_data_manager.get_forex_rate(symbol)
        except Exception as e:
            logger.error(f"Erreur récupération taux forex {symbol}: {e}")
            return None

    def get_market_data(self, symbol: str, provider: str = None) -> Optional[Dict[str, Any]]:
        """Récupère les données de marché génériques"""
        try:
            return self.real_data_manager.get_market_data(symbol, provider)
        except Exception as e:
            logger.error(f"Erreur récupération données marché {symbol}: {e}")
            return None

    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Recherche des symboles"""
        try:
            return self.real_data_manager.search_symbols(query)
        except Exception as e:
            logger.error(f"Erreur recherche symboles '{query}': {e}")
            return []

    def get_available_symbols(self) -> List[str]:
        """Récupère la liste des symboles disponibles"""
        try:
            return self.real_data_manager.get_available_symbols()
        except Exception as e:
            logger.error(f"Erreur récupération symboles disponibles: {e}")
            return []

    def get_economic_indicators(self) -> Dict[str, Any]:
        """Récupère les indicateurs économiques"""
        try:
            # Pour l'instant, retourner des valeurs par défaut
            # TODO: Intégrer un vrai provider d'indicateurs économiques
            return {
                "gdp": "2.1%",
                "inflation": "3.7%",
                "unemployment": "3.8%",
                "fed_rate": "5.25%",
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erreur récupération indicateurs économiques: {e}")
            return {}


# Instance globale du service
data_service = DataService()
