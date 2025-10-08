"""
Breakout Detector Configuration
Translation from NonoBot Rust implementation
"""

from decimal import Decimal
from typing import Dict, Any


class BreakoutConfig:
    """
    Configuration for Breakout Detector Indicator
    
    NonoBot logic:
    - Support/Resistance detection
    - Volume confirmation
    - Breakout strength analysis
    """
    
    def __init__(self,
                 lookback_period: int = 20,
                 strength_threshold: Decimal = Decimal("0.5"),
                 volume_multiplier: Decimal = Decimal("1.5"),
                 min_touches: int = 2,
                 breakout_threshold: Decimal = Decimal("0.002"),  # 0.2%
                 enable_signals: bool = True):
        
        self.lookback_period = lookback_period
        self.strength_threshold = Decimal(str(strength_threshold))
        self.volume_multiplier = Decimal(str(volume_multiplier))
        self.min_touches = min_touches
        self.breakout_threshold = Decimal(str(breakout_threshold))
        self.enable_signals = enable_signals
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "lookback_period": self.lookback_period,
            "strength_threshold": float(self.strength_threshold),
            "volume_multiplier": float(self.volume_multiplier),
            "min_touches": self.min_touches,
            "breakout_threshold": float(self.breakout_threshold),
            "enable_signals": self.enable_signals
        }
    
    def get_required_periods(self) -> int:
        return self.lookback_period + 5