"""
Types de base pour les indicateurs techniques
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Optional


class SignalDirection(Enum):
    """Direction d'un signal de trading"""

    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


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
        """Validation des données"""
        if self.high < max(self.open, self.close) or self.low > min(
            self.open, self.close
        ):
            raise ValueError("Invalid OHLC data: high/low values inconsistent")


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
class Signal:
    """Signal de trading généré par un indicateur"""

    direction: SignalDirection
    strength: float  # 0.0 à 1.0
    message: str
    indicator_name: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

        # Validation de la force
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(
                f"Signal strength must be between 0.0 and 1.0, got {self.strength}"
            )

    @classmethod
    def neutral(cls, indicator_name: str, message: str, strength: float = 0.5):
        """Créer un signal neutre"""
        return cls(
            direction=SignalDirection.NEUTRAL,
            strength=strength,
            message=message,
            indicator_name=indicator_name,
            timestamp=datetime.now(),
        )
