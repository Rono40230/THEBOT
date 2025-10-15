"""
Market Data Service - Gestion des données de marché
Utilise la base de données SQLAlchemy et les data providers
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models.base import get_db_session
from ..models.market_data import MarketData, PriceHistory
from ..data_providers.real_data_manager import real_data_manager

logger = logging.getLogger(__name__)


class MarketDataService:
    """
    Service de gestion des données de marché
    Combine base de données et data providers externes
    """

    def __init__(self):
        """Initialise le service de données de marché"""
        self.logger = logging.getLogger(__name__)

    def get_market_data(self, symbol: str, provider: str = None) -> Optional[Dict[str, Any]]:
        """
        Récupère les données de marché pour un symbole

        Args:
            symbol: Symbole de l'actif
            provider: Provider spécifique (optionnel)

        Returns:
            Données de marché ou None si non trouvées
        """
        try:
            # Essayer d'abord depuis la base de données (cache)
            cached_data = self._get_cached_market_data(symbol)
            if cached_data:
                return cached_data

            # Sinon récupérer depuis les providers externes
            fresh_data = real_data_manager.get_market_data(symbol, provider)
            if fresh_data:
                # Mettre en cache
                self._cache_market_data(fresh_data)
                return fresh_data

            return None

        except Exception as e:
            self.logger.error(f"Erreur récupération données marché pour {symbol}: {e}")
            return None

    def get_price_history(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Récupère l'historique des prix pour un symbole

        Args:
            symbol: Symbole de l'actif
            days: Nombre de jours d'historique

        Returns:
            Liste des données historiques
        """
        try:
            with get_db_session() as session:
                since_date = datetime.utcnow() - timedelta(days=days)
                history = session.query(PriceHistory).filter(
                    PriceHistory.symbol == symbol,
                    PriceHistory.timestamp >= since_date
                ).order_by(PriceHistory.timestamp).all()

                return [{
                    'timestamp': h.timestamp,
                    'open': h.open_price,
                    'high': h.high_price,
                    'low': h.low_price,
                    'close': h.close_price,
                    'volume': h.volume
                } for h in history]

        except Exception as e:
            self.logger.error(f"Erreur récupération historique prix pour {symbol}: {e}")
            return []

    def update_price_history(self, symbol: str, price_data: Dict[str, Any]) -> bool:
        """
        Met à jour l'historique des prix

        Args:
            symbol: Symbole de l'actif
            price_data: Données de prix

        Returns:
            True si mise à jour réussie
        """
        try:
            with get_db_session() as session:
                history = PriceHistory(
                    symbol=symbol,
                    timestamp=price_data.get('timestamp', datetime.utcnow()),
                    open_price=price_data.get('open'),
                    high_price=price_data.get('high'),
                    low_price=price_data.get('low'),
                    close_price=price_data.get('close'),
                    volume=price_data.get('volume', 0)
                )
                session.add(history)
                session.commit()
                return True

        except Exception as e:
            self.logger.error(f"Erreur mise à jour historique prix pour {symbol}: {e}")
            return False

    def get_available_symbols(self) -> List[str]:
        """Récupère la liste des symboles disponibles"""
        try:
            return real_data_manager.get_available_symbols()
        except Exception as e:
            self.logger.error(f"Erreur récupération symboles disponibles: {e}")
            return []

    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Recherche des symboles"""
        try:
            return real_data_manager.search_symbols(query)
        except Exception as e:
            self.logger.error(f"Erreur recherche symboles '{query}': {e}")
            return []

    def _get_cached_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Récupère les données depuis le cache"""
        try:
            with get_db_session() as session:
                # Récupérer les données les plus récentes (moins de 5 minutes)
                five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
                data = session.query(MarketData).filter(
                    MarketData.symbol == symbol,
                    MarketData.last_updated >= five_minutes_ago
                ).first()

                if data:
                    return {
                        'symbol': data.symbol,
                        'price': data.price,
                        'change': data.change,
                        'change_percent': data.change_percent,
                        'volume': data.volume,
                        'market_cap': data.market_cap,
                        'last_updated': data.last_updated
                    }
                return None

        except Exception as e:
            self.logger.error(f"Erreur récupération cache pour {symbol}: {e}")
            return None

    def _cache_market_data(self, data: Dict[str, Any]) -> None:
        """Met en cache les données de marché"""
        try:
            with get_db_session() as session:
                market_data = MarketData(
                    symbol=data['symbol'],
                    price=data.get('price', 0),
                    change=data.get('change', 0),
                    change_percent=data.get('change_percent', 0),
                    volume=data.get('volume', 0),
                    market_cap=data.get('market_cap', 0),
                    last_updated=data.get('timestamp', datetime.utcnow())
                )
                session.add(market_data)
                session.commit()

        except Exception as e:
            self.logger.error(f"Erreur mise en cache pour {data.get('symbol', 'unknown')}: {e}")


# Instance globale du service
market_data_service = MarketDataService()
