"""
Candle Patterns Configuration
Translation from NonoBot Rust implementation
"""

from decimal import Decimal
from typing import Dict, Any


class CandlePatternsConfig:
    """
    Configuration for Candle Patterns Indicator
    
    NonoBot patterns:
    - Doji, Hammer, Shooting Star
    - Engulfing, Harami patterns
    - Strength and confirmation logic
    """
    
    def __init__(self,
                 min_body_ratio: Decimal = Decimal("0.1"),
                 doji_threshold: Decimal = Decimal("0.05"),
                 wick_ratio_threshold: Decimal = Decimal("2.0"),
                 pattern_strength_threshold: Decimal = Decimal("0.7"),
                 enable_signals: bool = True):
        
        self.min_body_ratio = Decimal(str(min_body_ratio))
        self.doji_threshold = Decimal(str(doji_threshold))
        self.wick_ratio_threshold = Decimal(str(wick_ratio_threshold))
        self.pattern_strength_threshold = Decimal(str(pattern_strength_threshold))
        self.enable_signals = enable_signals
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_body_ratio": float(self.min_body_ratio),
            "doji_threshold": float(self.doji_threshold),
            "wick_ratio_threshold": float(self.wick_ratio_threshold),
            "pattern_strength_threshold": float(self.pattern_strength_threshold),
            "enable_signals": self.enable_signals
        }
    
    def get_required_periods(self) -> int:
        return 3  # Need at least 3 candles for patterns