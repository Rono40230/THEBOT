"""
Modèles pour les données de marché THEBOT
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, String

from .base import BaseModel


class MarketData(BaseModel):
    """
    Données générales sur un marché/symbole.
    Stocke les informations statiques sur les marchés supportés.
    """
    __tablename__ = "market_data"

    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    type = Column(String(20), nullable=False, default="crypto")  # crypto, stock, forex, etc.
    provider = Column(String(50), nullable=False)  # binance, coin_gecko, twelve_data, etc.
    base_currency = Column(String(10), nullable=True)
    quote_currency = Column(String(10), nullable=True)
    is_active = Column(Integer, default=1, nullable=False)  # 1=actif, 0=inactif

    # Métadonnées
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<MarketData(symbol='{self.symbol}', provider='{self.provider}')>"


class PriceHistory(BaseModel):
    """
    Historique des prix pour un symbole.
    Stocke les données OHLCV (Open, High, Low, Close, Volume).
    """
    __tablename__ = "price_history"

    symbol = Column(String(20), index=True, nullable=False)
    provider = Column(String(50), nullable=False)
    interval = Column(String(10), nullable=False, default="1d")  # 1m, 5m, 1h, 1d, etc.

    # Prix OHLCV
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)

    # Timestamp du marché (pas de la DB)
    market_timestamp = Column(DateTime, nullable=False, index=True)

    # Métadonnées
    data_quality = Column(String(20), default="good")  # good, partial, missing

    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

    def __repr__(self) -> str:
        return f"<PriceHistory(symbol='{self.symbol}', timestamp='{self.market_timestamp}', close={self.close_price})>"

    @property
    def timestamp(self) -> datetime:
        """Alias pour market_timestamp pour compatibilité"""
        return self.market_timestamp

    @classmethod
    def from_ohlcv_data(cls, symbol: str, provider: str, interval: str,
                       ohlcv_data: dict, timestamp: datetime) -> 'PriceHistory':
        """
        Crée un objet PriceHistory à partir de données OHLCV.

        Args:
            symbol: Symbole du marché
            provider: Nom du provider
            interval: Intervalle de temps
            ohlcv_data: Dict avec clés 'open', 'high', 'low', 'close', 'volume'
            timestamp: Timestamp du marché

        Returns:
            Instance de PriceHistory
        """
        return cls(
            symbol=symbol,
            provider=provider,
            interval=interval,
            open_price=ohlcv_data.get('open', 0.0),
            high_price=ohlcv_data.get('high', 0.0),
            low_price=ohlcv_data.get('low', 0.0),
            close_price=ohlcv_data.get('close', 0.0),
            volume=ohlcv_data.get('volume'),
            market_timestamp=timestamp
        )
