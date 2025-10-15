"""
Service de base de données THEBOT
Gestion centralisée des opérations de base de données
"""

import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy import and_, desc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)

T = TypeVar('T')


class DatabaseService:
    """
    Service centralisé pour toutes les opérations de base de données.
    Fournit une interface unifiée pour les opérations CRUD.
    """

    def __init__(self):
        self._initialized = False

    def initialize_database(self) -> None:
        """
        Initialise la base de données en créant toutes les tables.
        À appeler au démarrage de l'application.
        """
        if not self._initialized:
            try:
                logger.info("🏗️ Initialisation de la base de données...")
                create_tables()
                self._create_initial_data()
                self._initialized = True
                logger.info("✅ Base de données initialisée avec succès")
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
                raise

    def _create_initial_data(self) -> None:
        """Crée les données initiales si nécessaire"""
        with self.get_session() as session:
            # Créer les marchés populaires s'ils n'existent pas
            if session.query(MarketData).count() == 0:
                self._create_default_markets(session)

            # Créer les préférences par défaut si elles n'existent pas
            if session.query(UserPreferences).count() == 0:
                default_prefs = UserPreferences.get_default_preferences()
                session.add(default_prefs)
                session.commit()

    def _create_default_markets(self, session: Session) -> None:
        """Crée les marchés par défaut"""
        default_markets = [
            # Cryptos populaires
            MarketData(symbol="BTCUSDT", name="Bitcoin", type="crypto", provider="binance", base_currency="BTC", quote_currency="USDT"),
            MarketData(symbol="ETHUSDT", name="Ethereum", type="crypto", provider="binance", base_currency="ETH", quote_currency="USDT"),
            MarketData(symbol="BNBUSDT", name="Binance Coin", type="crypto", provider="binance", base_currency="BNB", quote_currency="USDT"),
            MarketData(symbol="ADAUSDT", name="Cardano", type="crypto", provider="binance", base_currency="ADA", quote_currency="USDT"),
            MarketData(symbol="SOLUSDT", name="Solana", type="crypto", provider="binance", base_currency="SOL", quote_currency="USDT"),

            # Actions populaires
            MarketData(symbol="AAPL", name="Apple Inc.", type="stock", provider="twelve_data", base_currency="AAPL", quote_currency="USD"),
            MarketData(symbol="GOOGL", name="Alphabet Inc.", type="stock", provider="twelve_data", base_currency="GOOGL", quote_currency="USD"),
            MarketData(symbol="MSFT", name="Microsoft Corp.", type="stock", provider="twelve_data", base_currency="MSFT", quote_currency="USD"),
            MarketData(symbol="TSLA", name="Tesla Inc.", type="stock", provider="twelve_data", base_currency="TSLA", quote_currency="USD"),
            MarketData(symbol="NVDA", name="Nvidia Corp.", type="stock", provider="twelve_data", base_currency="NVDA", quote_currency="USD"),
        ]

        for market in default_markets:
            session.add(market)
        session.commit()
        logger.info(f"✅ {len(default_markets)} marchés par défaut créés")

    @contextmanager
    def get_session(self):
        """Context manager pour obtenir une session de base de données"""
        db = next(get_db())
        try:
            yield db
        finally:
            db.close()

    # === MÉTHODES GÉNÉRIQUES CRUD ===

    def create(self, obj: T) -> T:
        """Crée un nouvel objet en base de données"""
        with self.get_session() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    def get_by_id(self, model_class: Type[T], id: int) -> Optional[T]:
        """Récupère un objet par son ID"""
        with self.get_session() as session:
            return session.query(model_class).filter(model_class.id == id).first()

    def get_all(self, model_class: Type[T], limit: int = 100, offset: int = 0) -> List[T]:
        """Récupère tous les objets d'un modèle avec pagination"""
        with self.get_session() as session:
            return session.query(model_class).limit(limit).offset(offset).all()

    def update(self, obj: T) -> T:
        """Met à jour un objet existant"""
        with self.get_session() as session:
            session.merge(obj)
            session.commit()
            return obj

    def delete(self, obj: T) -> bool:
        """Supprime un objet"""
        with self.get_session() as session:
            session.delete(obj)
            session.commit()
            return True

    # === MÉTHODES SPÉCIFIQUES AUX DONNÉES DE MARCHÉ ===

    def get_market_data(self, symbol: str) -> Optional["MarketData"]:
        """Récupère les informations sur un marché"""
        with self.get_session() as session:
            return session.query(MarketData).filter(MarketData.symbol == symbol).first()

    def get_price_history(self, symbol: str, provider: str = None, limit: int = 100) -> List["PriceHistory"]:
        """Récupère l'historique des prix pour un symbole"""
        with self.get_session() as session:
            query = session.query(PriceHistory).filter(PriceHistory.symbol == symbol)
            if provider:
                query = query.filter(PriceHistory.provider == provider)
            return query.order_by(desc(PriceHistory.market_timestamp)).limit(limit).all()

    def save_price_history(self, price_data: List[Dict[str, Any]], symbol: str, provider: str, interval: str) -> int:
        """
        Sauvegarde un historique de prix en base de données.
        Évite les doublons basés sur le timestamp.
        """
        saved_count = 0
        with self.get_session() as session:
            for data in price_data:
                # Vérifier si l'enregistrement existe déjà
                existing = session.query(PriceHistory).filter(
                    and_(
                        PriceHistory.symbol == symbol,
                        PriceHistory.provider == provider,
                        PriceHistory.interval == interval,
                        PriceHistory.market_timestamp == data.get('timestamp')
                    )
                ).first()

                if not existing:
                    price_record = PriceHistory.from_ohlcv_data(
                        symbol=symbol,
                        provider=provider,
                        interval=interval,
                        ohlcv_data=data,
                        timestamp=data.get('timestamp')
                    )
                    session.add(price_record)
                    saved_count += 1

            session.commit()
        return saved_count

    # === MÉTHODES SPÉCIFIQUES AUX ALERTES ===

    def get_active_alerts(self, category: str = None, limit: int = 50) -> List["Alert"]:
        """Récupère les alertes actives"""
        with self.get_session() as session:
            query = session.query(Alert).filter(Alert.is_active == 1)
            if category:
                query = query.filter(Alert.category == category)
            return query.order_by(desc(Alert.created_at)).limit(limit).all()

    def get_price_alerts(self, symbol: str = None, active_only: bool = True) -> List["PriceAlert"]:
        """Récupère les alertes de prix"""
        with self.get_session() as session:
            query = session.query(PriceAlert)
            if symbol:
                query = query.filter(PriceAlert.symbol == symbol)
            if active_only:
                query = query.filter(PriceAlert.is_active == 1)
            return query.all()

    def check_price_alerts(self, symbol: str, current_price: float) -> List["PriceAlert"]:
        """
        Vérifie quelles alertes de prix sont déclenchées pour un symbole.
        Met à jour automatiquement les alertes déclenchées.
        """
        triggered_alerts = []
        with self.get_session() as session:
            alerts = session.query(PriceAlert).filter(
                and_(
                    PriceAlert.symbol == symbol,
                    PriceAlert.is_active == 1,
                    PriceAlert.is_triggered == 0
                )
            ).all()

            for alert in alerts:
                if alert.check_condition(current_price):
                    alert.trigger()
                    triggered_alerts.append(alert)

            session.commit()
        return triggered_alerts

    # === MÉTHODES SPÉCIFIQUES AUX ACTUALITÉS ===

    def get_recent_news(self, limit: int = 50, category: str = None) -> List["NewsArticle"]:
        """Récupère les actualités récentes"""
        with self.get_session() as session:
            query = session.query(NewsArticle)
            if category:
                query = query.filter(NewsArticle.category == category)
            return query.order_by(desc(NewsArticle.published_at)).limit(limit).all()

    def search_news(self, query: str, limit: int = 50) -> List["NewsArticle"]:
        """Recherche dans les actualités"""
        with self.get_session() as session:
            # Recherche simple dans le titre et le résumé
            search_filter = f"%{query}%"
            return session.query(NewsArticle).filter(
                or_(
                    NewsArticle.title.like(search_filter),
                    NewsArticle.summary.like(search_filter)
                )
            ).order_by(desc(NewsArticle.published_at)).limit(limit).all()

    # === MÉTHODES UTILITAIRES ===

    def get_stats(self) -> Dict[str, int]:
        """Retourne des statistiques sur la base de données"""
        with self.get_session() as session:
            return {
                "markets": session.query(func.count(MarketData.id)).scalar(),
                "price_records": session.query(func.count(PriceHistory.id)).scalar(),
                "alerts": session.query(func.count(Alert.id)).scalar(),
                "price_alerts": session.query(func.count(PriceAlert.id)).scalar(),
                "news_articles": session.query(func.count(NewsArticle.id)).scalar(),
                "users": session.query(func.count(User.id)).scalar(),
            }

    def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """
        Nettoie les anciennes données.
        Supprime les données de plus de X jours.
        """
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        deleted_counts = {}
        with self.get_session() as session:
            # Supprimer les anciens historiques de prix (garder seulement les 90 derniers jours)
            result = session.query(PriceHistory).filter(PriceHistory.market_timestamp < cutoff_date).delete()
            deleted_counts["old_price_history"] = result

            # Archiver les anciennes alertes (plus de 30 jours)
            old_alerts = session.query(Alert).filter(
                and_(
                    Alert.created_at < cutoff_date,
                    Alert.is_active == 1
                )
            ).update({"is_active": 0})
            deleted_counts["archived_alerts"] = old_alerts

            session.commit()

        logger.info(f"🧹 Nettoyage terminé: {deleted_counts}")
        return deleted_counts


# Instance globale du service de base de données
database_service = DatabaseService()
