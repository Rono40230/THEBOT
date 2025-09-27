"""
Core types for THEBOT trading platform
Ultra-modular design with single responsibility principle
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from decimal import Decimal


class TimeFrame(Enum):
    """Trading timeframes"""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MON1 = "1M"


class SignalDirection(Enum):
    """Signal direction"""
    BUY = "buy"
    SELL = "sell"
    NEUTRAL = "neutral"


class SignalStrength(Enum):
    """Signal strength levels"""
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


@dataclass
class MarketData:
    """Core market data structure"""
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    timeframe: TimeFrame
    symbol: str
    
    def __post_init__(self):
        """Validate data integrity"""
        if self.high < max(self.open, self.close):
            raise ValueError("High must be >= max(open, close)")
        if self.low > min(self.open, self.close):
            raise ValueError("Low must be <= min(open, close)")
        if self.volume < 0:
            raise ValueError("Volume cannot be negative")


@dataclass
class Signal:
    """Trading signal structure"""
    direction: SignalDirection
    strength: SignalStrength
    price: Decimal
    timestamp: datetime
    source: str
    confidence: float  # 0.0 to 1.0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate signal"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class IndicatorResult:
    """Generic indicator result"""
    value: Any
    timestamp: datetime
    indicator_name: str
    is_valid: bool = True
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PriceLevel:
    """Price level (support/resistance)"""
    price: Decimal
    timestamp: datetime
    strength: float  # 0.0 to 1.0
    touch_count: int = 0
    level_type: str = "unknown"  # support, resistance, pivot, etc.


@dataclass
class EconomicEvent:
    """Economic calendar event"""
    name: str
    country: str
    timestamp: datetime
    impact: str  # low, medium, high
    forecast: Optional[str] = None
    previous: Optional[str] = None
    actual: Optional[str] = None
    currency: Optional[str] = None