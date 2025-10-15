"""
Interfaces communes pour les providers de données THEBOT
Architecture modulaire avec pattern Adapter/Factory
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class DataProviderInterface(ABC):
    """
    Interface abstraite pour tous les providers de données THEBOT.

    Cette interface définit le contrat commun que tous les providers doivent respecter,
    permettant une interchangeabilité et une maintenance facilitée.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom du provider (ex: 'binance', 'coin_gecko', 'twelve_data')"""
        pass

    @property
    @abstractmethod
    def supported_markets(self) -> List[str]:
        """Liste des marchés/symboles supportés par ce provider"""
        pass

    @property
    @abstractmethod
    def rate_limit_info(self) -> Dict[str, Any]:
        """Informations sur les limites de taux du provider"""
        pass

    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """
        Valide si un symbole est supporté par ce provider.

        Args:
            symbol: Symbole à valider (ex: 'BTCUSDT', 'AAPL')

        Returns:
            bool: True si le symbole est valide, False sinon
        """
        pass

    @abstractmethod
    def get_price_data(self, symbol: str, interval: str = "1d", limit: int = 100) -> Optional[Dict[str, Any]]:
        """
        Récupère les données de prix historiques pour un symbole.

        Args:
            symbol: Symbole du marché (ex: 'BTCUSDT')
            interval: Intervalle de temps (ex: '1m', '1h', '1d')
            limit: Nombre maximum de points de données

        Returns:
            Dict contenant les données de prix ou None si erreur
        """
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Récupère le prix actuel pour un symbole.

        Args:
            symbol: Symbole du marché

        Returns:
            Prix actuel ou None si erreur
        """
        pass

    @abstractmethod
    def get_market_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations générales sur un marché/symbole.

        Args:
            symbol: Symbole du marché

        Returns:
            Dict avec informations sur le marché ou None si erreur
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Vérifie si le provider est disponible et fonctionnel.

        Returns:
            bool: True si le provider est opérationnel
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Retourne le statut détaillé du provider.

        Returns:
            Dict avec informations sur l'état du provider
        """
        pass


class NewsProviderInterface(ABC):
    """
    Interface abstraite pour les providers de données d'actualités.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom du provider d'actualités"""
        pass

    @abstractmethod
    def get_news(self, symbol: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Récupère les actualités, optionnellement filtrées par symbole.

        Args:
            symbol: Symbole pour filtrer les actualités (optionnel)
            limit: Nombre maximum d'articles

        Returns:
            Liste d'articles d'actualité
        """
        pass

    @abstractmethod
    def search_news(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Recherche d'actualités par requête.

        Args:
            query: Terme de recherche
            limit: Nombre maximum de résultats

        Returns:
            Liste d'articles correspondant à la recherche
        """
        pass


class EconomicProviderInterface(ABC):
    """
    Interface abstraite pour les providers de données économiques.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom du provider économique"""
        pass

    @abstractmethod
    def get_economic_events(self, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les événements économiques dans une période donnée.

        Args:
            from_date: Date de début (format YYYY-MM-DD)
            to_date: Date de fin (format YYYY-MM-DD)

        Returns:
            Liste d'événements économiques
        """
        pass

    @abstractmethod
    def get_economic_calendar(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Récupère le calendrier économique pour les prochains jours.

        Args:
            days_ahead: Nombre de jours à couvrir

        Returns:
            Liste d'événements économiques à venir
        """
        pass


class ProviderFactory:
    """
    Factory pour créer et gérer les instances de providers.
    Implémente le pattern Singleton pour éviter les duplications.
    """

    _instances: Dict[str, Any] = {}

    @classmethod
    def get_provider(cls, provider_type: str, **kwargs) -> Optional[Any]:
        """
        Récupère ou crée une instance de provider.

        Args:
            provider_type: Type de provider ('binance', 'coin_gecko', etc.)
            **kwargs: Arguments pour l'initialisation du provider

        Returns:
            Instance du provider ou None si non disponible
        """
        if provider_type not in cls._instances:
            try:
                cls._instances[provider_type] = cls._create_provider(provider_type, **kwargs)
                logger.info(f"✅ Provider {provider_type} créé et mis en cache")
            except Exception as e:
                logger.error(f"❌ Erreur création provider {provider_type}: {e}")
                return None

        return cls._instances[provider_type]

    @classmethod
    def _create_provider(cls, provider_type: str, **kwargs) -> Any:
        """
        Méthode interne pour créer une instance de provider spécifique.
        """
        if provider_type == "binance":
            from .binance_api import BinanceProvider
            return BinanceProvider()
        elif provider_type == "coin_gecko":
            from .coin_gecko_api import CoinGeckoAPI
            return CoinGeckoAPI(**kwargs)
        elif provider_type == "twelve_data":
            from .twelve_data_api import TwelveDataAPI
            return TwelveDataAPI(**kwargs)
        elif provider_type == "rss_news":
            from .rss_news_manager import rss_news_manager
            return rss_news_manager
        else:
            raise ValueError(f"Provider type '{provider_type}' not supported")

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Retourne la liste des types de providers disponibles.

        Returns:
            Liste des types de providers supportés
        """
        return ["binance", "coin_gecko", "twelve_data", "rss_news"]

    @classmethod
    def clear_cache(cls) -> None:
        """
        Vide le cache des instances de providers.
        Utile pour les tests ou les reconnexions.
        """
        cls._instances.clear()
        logger.info("🧹 Cache des providers vidé")
