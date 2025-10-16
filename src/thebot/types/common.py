"""
Types communs unifiés pour THEBOT
Fusion des types dataclasses et Pydantic pour compatibilité universelle
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class SignalDirection(Enum):
    """Direction d'un signal de trading (version unifiée)"""
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


class SignalType(Enum):
    """Type de signal de trading (version étendue)"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"


class TimeFrame(Enum):
    """Intervals de temps supportés"""
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    DAY_1 = "1d"
    WEEK_1 = "1w"
    MONTH_1 = "1M"


@dataclass
class MarketData:
    """Données de marché standardisées"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self):
        """Validation des données OHLC"""
        if self.high < max(self.open, self.close) or self.low > min(self.open, self.close):
            raise ValueError("Invalid OHLC data")


@dataclass
class IndicatorResult:
    """Résultat d'un calcul d'indicateur"""
    value: Any
    timestamp: datetime
    indicator_name: str
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TradingSignal:
    """Signal de trading unifié"""
    symbol: str
    signal_type: SignalType
    direction: SignalDirection
    confidence: float
    indicators: Dict[str, Any]
    timestamp: datetime
    reasoning: Optional[str] = None

    def __post_init__(self):
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        if self.indicators is None:
            self.indicators = {}
