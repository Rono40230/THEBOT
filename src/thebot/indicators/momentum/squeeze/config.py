"""
Squeeze Momentum Configuration
Translation from NonoBot Rust implementation

Squeeze Momentum combines:
- Bollinger Bands (volatility)
- Keltner Channels (ATR-based)
- Momentum oscillator for direction
"""

from decimal import Decimal
from typing import Dict, Any


class SqueezeConfig:
    """
    Configuration for Squeeze Momentum Indicator
    
    NonoBot Rust → THEBOT Python translation:
    - bollinger_period: BB calculation period
    - bollinger_std: Standard deviation multiplier
    - keltner_period: KC calculation period 
    - keltner_atr_multiplier: ATR multiplier for KC
    - momentum_length: Momentum oscillator length
    - enable_signals: Enable trading signals
    """
    
    def __init__(self,
                 bollinger_period: int = 20,
                 bollinger_std: Decimal = Decimal("2.0"),
                 keltner_period: int = 20,
                 keltner_atr_multiplier: Decimal = Decimal("1.5"),
                 momentum_length: int = 12,
                 enable_signals: bool = True,
                 signal_threshold: Decimal = Decimal("0.0")):
        
        # Validation
        assert 5 <= bollinger_period <= 200, "bollinger_period must be between 5 and 200"
        assert Decimal("0.5") <= bollinger_std <= Decimal("5.0"), "bollinger_std must be between 0.5 and 5.0"
        assert 5 <= keltner_period <= 200, "keltner_period must be between 5 and 200"
        assert Decimal("0.5") <= keltner_atr_multiplier <= Decimal("5.0"), "keltner_atr_multiplier must be between 0.5 and 5.0"
        assert 5 <= momentum_length <= 50, "momentum_length must be between 5 and 50"
        
        # Store validated values
        self.bollinger_period = bollinger_period
        self.bollinger_std = Decimal(str(bollinger_std))
        self.keltner_period = keltner_period
        self.keltner_atr_multiplier = Decimal(str(keltner_atr_multiplier))
        self.momentum_length = momentum_length
        self.enable_signals = enable_signals
        self.signal_threshold = Decimal(str(signal_threshold))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for BaseIndicator"""
        return {
            "bollinger_period": self.bollinger_period,
            "bollinger_std": float(self.bollinger_std),
            "keltner_period": self.keltner_period,
            "keltner_atr_multiplier": float(self.keltner_atr_multiplier),
            "momentum_length": self.momentum_length,
            "enable_signals": self.enable_signals,
            "signal_threshold": float(self.signal_threshold)
        }
    
    def get_required_periods(self) -> int:
        """Calculate required periods for all components"""
        return max(
            self.bollinger_period,
            self.keltner_period,
            self.momentum_length
        ) + 5  # Buffer for calculations