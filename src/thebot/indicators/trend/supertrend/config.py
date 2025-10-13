"""
Configuration pour l'indicateur SuperTrend
Module ultra-modulaire - Responsabilité unique : Validation des paramètres SuperTrend
"""

from dataclasses import dataclass
from decimal import Decimal

from ....core.exceptions import ConfigError


@dataclass
class SuperTrendConfig:
    """Configuration validée pour l'indicateur SuperTrend"""

    atr_period: int = 10
    multiplier: Decimal = Decimal("3.0")
    enable_signals: bool = True
    use_decimal: bool = True
    store_history: bool = True

    def __post_init__(self):
        """Validation automatique des paramètres"""
        self.validate()

    def validate(self) -> None:
        """Validation complète des paramètres SuperTrend"""

        # Validation période ATR
        if not isinstance(self.atr_period, int):
            raise ConfigError("atr_period must be an integer")

        if self.atr_period < 2:
            raise ConfigError("atr_period must be at least 2")

        if self.atr_period > 50:
            raise ConfigError("atr_period must not exceed 50")

        # Validation multiplicateur
        if not isinstance(self.multiplier, Decimal):
            try:
                self.multiplier = Decimal(str(self.multiplier))
            except (ValueError, TypeError):
                raise ConfigError("multiplier must be convertible to Decimal")

        if self.multiplier <= 0:
            raise ConfigError("multiplier must be positive")

        if self.multiplier > 10:
            raise ConfigError("multiplier should not exceed 10")

    def to_dict(self) -> dict:
        """Export configuration vers dictionnaire"""
        return {
            "atr_period": self.atr_period,
            "multiplier": float(self.multiplier),
            "enable_signals": self.enable_signals,
            "use_decimal": self.use_decimal,
            "store_history": self.store_history,
        }
