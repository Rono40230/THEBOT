from src.thebot.core.logger import logger
"""
Provider Manager - Gestionnaire unifié des providers de données THEBOT
Utilise les interfaces communes pour une architecture modulaire
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .provider_interfaces import (
    DataProviderInterface,
    EconomicProviderInterface,
    NewsProviderInterface,
    ProviderFactory
)

logger = logging.getLogger(__name__)


class ProviderManager:
    """
    Gestionnaire unifié de tous les providers de données THEBOT.

    Cette classe centralise l'accès à tous les providers via leurs interfaces communes,
    permettant une architecture modulaire et maintenable.
    """

    def __init__(self):
        self.providers: Dict[str, Any] = {}
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialise tous les providers disponibles"""
        available_providers = ProviderFactory.get_available_providers()

        for provider_type in available_providers:
            try:
                provider = ProviderFactory.get_provider(provider_type)
                if provider:
                    self.providers[provider_type] = provider
                    logger.info(f"✅ Provider {provider_type} chargé: {provider.name}")
                else:
                    logger.warning(f"⚠️ Provider {provider_type} non disponible")
            except Exception as e:
                logger.error(f"❌ Erreur chargement provider {provider_type}: {e}")

        logger.info(f"🔧 ProviderManager initialisé avec {len(self.providers)} providers")

    def get_data_provider(self, provider_name: str) -> Optional[DataProviderInterface]:
        """Récupère un provider de données par nom"""
        return self.providers.get(provider_name)

    def get_news_provider(self, provider_name: str) -> Optional[NewsProviderInterface]:
        """Récupère un provider d'actualités par nom"""
        return self.providers.get(provider_name)

    def get_economic_provider(self, provider_name: str) -> Optional[EconomicProviderInterface]:
        """Récupère un provider économique par nom"""
        return self.providers.get(provider_name)

    def get_available_data_providers(self) -> List[str]:
        """Retourne la liste des providers de données disponibles"""
        return [name for name, provider in self.providers.items()
                if isinstance(provider, DataProviderInterface)]

    def get_available_news_providers(self) -> List[str]:
        """Retourne la liste des providers d'actualités disponibles"""
        return [name for name, provider in self.providers.items()
                if isinstance(provider, NewsProviderInterface)]

    def get_price_data(self, symbol: str, provider: str = None, interval: str = "1d", limit: int = 100) -> Optional[Dict[str, Any]]:
        """
        Récupère les données de prix pour un symbole.

        Args:
            symbol: Symbole du marché (ex: 'BTCUSDT')
            provider: Provider spécifique à utiliser (optionnel)
            interval: Intervalle de temps
            limit: Nombre maximum de points de données

        Returns:
            Données de prix ou None si erreur
        """
        if provider and provider in self.providers:
            data_provider = self.providers[provider]
            if isinstance(data_provider, DataProviderInterface):
                return data_provider.get_price_data(symbol, interval, limit)
        else:
            # Essaie tous les providers de données disponibles
            for data_provider in self.providers.values():
                if isinstance(data_provider, DataProviderInterface):
                    result = data_provider.get_price_data(symbol, interval, limit)
                    if result:
                        return result

        return None

    def get_current_price(self, symbol: str, provider: str = None) -> Optional[float]:
        """
        Récupère le prix actuel pour un symbole.

        Args:
            symbol: Symbole du marché
            provider: Provider spécifique à utiliser (optionnel)

        Returns:
            Prix actuel ou None si erreur
        """
        if provider and provider in self.providers:
            data_provider = self.providers[provider]
            if isinstance(data_provider, DataProviderInterface):
                return data_provider.get_current_price(symbol)
        else:
            # Essaie tous les providers de données disponibles
            for data_provider in self.providers.values():
                if isinstance(data_provider, DataProviderInterface):
                    result = data_provider.get_current_price(symbol)
                    if result is not None:
                        return result

        return None

    def get_market_info(self, symbol: str, provider: str = None) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations sur un marché.

        Args:
            symbol: Symbole du marché
            provider: Provider spécifique à utiliser (optionnel)

        Returns:
            Informations sur le marché ou None si erreur
        """
        if provider and provider in self.providers:
            data_provider = self.providers[provider]
            if isinstance(data_provider, DataProviderInterface):
                return data_provider.get_market_info(symbol)
        else:
            # Essaie tous les providers de données disponibles
            for data_provider in self.providers.values():
                if isinstance(data_provider, DataProviderInterface):
                    result = data_provider.get_market_info(symbol)
                    if result:
                        return result

        return None

    def get_news(self, symbol: Optional[str] = None, provider: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Récupère les actualités.

        Args:
            symbol: Symbole pour filtrer les actualités (optionnel)
            provider: Provider spécifique à utiliser (optionnel)
            limit: Nombre maximum d'articles

        Returns:
            Liste d'articles d'actualité
        """
        if provider and provider in self.providers:
            news_provider = self.providers[provider]
            if isinstance(news_provider, NewsProviderInterface):
                return news_provider.get_news(symbol, limit)
        else:
            # Essaie tous les providers d'actualités disponibles
            all_news = []
            for news_provider in self.providers.values():
                if isinstance(news_provider, NewsProviderInterface):
                    news = news_provider.get_news(symbol, limit)
                    all_news.extend(news)

            # Trie par date et limite
            all_news.sort(key=lambda x: x.get('published', ''), reverse=True)
            return all_news[:limit]

        return []

    def search_news(self, query: str, provider: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Recherche d'actualités par requête.

        Args:
            query: Terme de recherche
            provider: Provider spécifique à utiliser (optionnel)
            limit: Nombre maximum de résultats

        Returns:
            Liste d'articles correspondant à la recherche
        """
        if provider and provider in self.providers:
            news_provider = self.providers[provider]
            if isinstance(news_provider, NewsProviderInterface):
                return news_provider.search_news(query, limit)
        else:
            # Essaie tous les providers d'actualités disponibles
            all_results = []
            for news_provider in self.providers.values():
                if isinstance(news_provider, NewsProviderInterface):
                    results = news_provider.search_news(query, limit)
                    all_results.extend(results)

            # Trie par pertinence et limite
            return all_results[:limit]

        return []

    def get_provider_status(self, provider_name: str = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Récupère le statut d'un provider ou de tous les providers.

        Args:
            provider_name: Nom du provider (optionnel, tous si None)

        Returns:
            Statut du provider ou liste de statuts
        """
        if provider_name:
            provider = self.providers.get(provider_name)
            if provider and hasattr(provider, 'get_status'):
                return provider.get_status()
            return {"error": f"Provider {provider_name} not found"}
        else:
            return {name: provider.get_status() if hasattr(provider, 'get_status')
                   else {"error": "Status not available"}
                   for name, provider in self.providers.items()}

    def validate_symbol(self, symbol: str, provider: str = None) -> bool:
        """
        Valide si un symbole est supporté.

        Args:
            symbol: Symbole à valider
            provider: Provider spécifique à utiliser (optionnel)

        Returns:
            True si le symbole est valide
        """
        if provider and provider in self.providers:
            data_provider = self.providers[provider]
            if isinstance(data_provider, DataProviderInterface):
                return data_provider.validate_symbol(symbol)
        else:
            # Vérifie auprès de tous les providers
            for data_provider in self.providers.values():
                if isinstance(data_provider, DataProviderInterface):
                    if data_provider.validate_symbol(symbol):
                        return True

        return False

    def get_supported_markets(self, provider: str = None) -> Union[List[str], Dict[str, List[str]]]:
        """
        Récupère les marchés supportés.

        Args:
            provider: Provider spécifique (optionnel, tous si None)

        Returns:
            Liste de marchés ou dict par provider
        """
        if provider is not None:
            # Provider spécifique demandé
            if provider in self.providers:
                data_provider = self.providers[provider]
                if isinstance(data_provider, DataProviderInterface):
                    return data_provider.supported_markets
            # Provider n'existe pas ou n'est pas un DataProviderInterface
            return []
        else:
            # Tous les providers
            return {name: provider.supported_markets
                   for name, provider in self.providers.items()
                   if isinstance(provider, DataProviderInterface)}


# Instance globale
provider_manager = ProviderManager()