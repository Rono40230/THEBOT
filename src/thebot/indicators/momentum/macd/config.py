"""
Configuration pour l'indicateur MACD (Moving Average Convergence Divergence)
Module ultra-modulaire - Responsabilité unique : Validation des paramètres MACD
"""

from decimal import Decimal
from dataclasses import dataclass

from thebot.core.exceptions import ConfigurationError


@dataclass
class MACDConfig:
    """Configuration validée pour l'indicateur MACD"""
    
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9
    enable_signals: bool = True
    zero_line_sensitivity: Decimal = Decimal('0.001')  # Sensibilité ligne zéro
    use_decimal: bool = True
    store_history: bool = True
    
    def __post_init__(self):
        """Validation automatique des paramètres"""
        self.validate()
    
    def validate(self) -> None:
        """Validation complète des paramètres MACD"""
        
        # Validation périodes
        periods = ['fast_period', 'slow_period', 'signal_period']
        for period_name in periods:
            period_value = getattr(self, period_name)
            if not isinstance(period_value, int):
                raise ConfigurationError(f"{period_name} must be an integer")
            
            if period_value < 2:
                raise ConfigurationError(f"{period_name} must be at least 2")
            
            if period_value > 200:
                raise ConfigurationError(f"{period_name} must not exceed 200")
        
        # Validation cohérence des périodes
        if self.fast_period >= self.slow_period:
            raise ConfigurationError("fast_period must be < slow_period")
        
        # Validation sensibilité
        if not isinstance(self.zero_line_sensitivity, Decimal):
            try:
                self.zero_line_sensitivity = Decimal(str(self.zero_line_sensitivity))
            except (ValueError, TypeError):
                raise ConfigurationError("zero_line_sensitivity must be convertible to Decimal")
        
        if self.zero_line_sensitivity <= 0:
            raise ConfigurationError("zero_line_sensitivity must be positive")
    
    def to_dict(self) -> dict:
        """Export configuration vers dictionnaire"""
        return {
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
            'signal_period': self.signal_period,
            'enable_signals': self.enable_signals,
            'zero_line_sensitivity': float(self.zero_line_sensitivity),
            'use_decimal': self.use_decimal,
            'store_history': self.store_history
        }