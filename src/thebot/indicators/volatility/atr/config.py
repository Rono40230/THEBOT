"""
Configuration pour l'indicateur ATR (Average True Range)
Module ultra-modulaire - Responsabilité unique : Validation des paramètres ATR
"""

from decimal import Decimal
from typing import Optional
from dataclasses import dataclass

from thebot.core.exceptions import ConfigurationError


@dataclass
class ATRConfig:
    """Configuration validée pour l'indicateur ATR"""
    
    period: int
    smoothing_method: str = "sma"  # "sma" ou "ema"
    enable_signals: bool = True
    volatility_threshold_low: Decimal = Decimal('0.5')  # % ATR faible
    volatility_threshold_high: Decimal = Decimal('2.0')  # % ATR élevé
    use_decimal: bool = True
    store_history: bool = True
    
    def __post_init__(self):
        """Validation automatique des paramètres"""
        self.validate()
    
    def validate(self) -> None:
        """Validation complète des paramètres ATR"""
        
        # Validation période
        if not isinstance(self.period, int):
            raise ConfigurationError("period must be an integer")
        
        if self.period < 2:
            raise ConfigurationError("period must be at least 2")
        
        if self.period > 100:
            raise ConfigurationError("period must not exceed 100")
        
        # Validation méthode de lissage
        if self.smoothing_method not in ["sma", "ema"]:
            raise ConfigurationError("smoothing_method must be 'sma' or 'ema'")
        
        # Validation seuils de volatilité
        if not isinstance(self.volatility_threshold_low, Decimal):
            try:
                self.volatility_threshold_low = Decimal(str(self.volatility_threshold_low))
            except (ValueError, TypeError):
                raise ConfigurationError("volatility_threshold_low must be convertible to Decimal")
        
        if not isinstance(self.volatility_threshold_high, Decimal):
            try:
                self.volatility_threshold_high = Decimal(str(self.volatility_threshold_high))
            except (ValueError, TypeError):
                raise ConfigurationError("volatility_threshold_high must be convertible to Decimal")
        
        if self.volatility_threshold_low < 0:
            raise ConfigurationError("volatility_threshold_low must be positive")
        
        if self.volatility_threshold_high <= self.volatility_threshold_low:
            raise ConfigurationError("volatility_threshold_high must be > volatility_threshold_low")
    
    def get_smoothing_alpha(self) -> Optional[Decimal]:
        """Retourne alpha pour EMA, None pour SMA"""
        if self.smoothing_method == "ema":
            return Decimal('2') / (Decimal(str(self.period)) + 1)
        return None
    
    def to_dict(self) -> dict:
        """Export configuration vers dictionnaire"""
        return {
            'period': self.period,
            'smoothing_method': self.smoothing_method,
            'enable_signals': self.enable_signals,
            'volatility_threshold_low': float(self.volatility_threshold_low),
            'volatility_threshold_high': float(self.volatility_threshold_high),
            'use_decimal': self.use_decimal,
            'store_history': self.store_history
        }