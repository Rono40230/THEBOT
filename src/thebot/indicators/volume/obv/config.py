"""
Configuration pour l'indicateur OBV (On-Balance Volume)
Module ultra-modulaire - Responsabilité unique : Validation des paramètres OBV
"""

from decimal import Decimal
from dataclasses import dataclass

from ....core.exceptions import ConfigError


@dataclass
class OBVConfig:
    """Configuration validée pour l'indicateur OBV"""
    
    enable_signals: bool = True
    signal_smoothing: int = 3  # Périodes pour lisser les signaux
    volume_threshold: Decimal = Decimal('0.1')  # Seuil volume significatif
    use_decimal: bool = True
    store_history: bool = True
    
    def __post_init__(self):
        """Validation automatique des paramètres"""
        self.validate()
    
    def validate(self) -> None:
        """Validation complète des paramètres OBV"""
        
        # Validation lissage signaux
        if not isinstance(self.signal_smoothing, int):
            raise ConfigurationError("signal_smoothing must be an integer")
        
        if self.signal_smoothing < 1:
            raise ConfigurationError("signal_smoothing must be at least 1")
        
        if self.signal_smoothing > 20:
            raise ConfigurationError("signal_smoothing should not exceed 20")
        
        # Validation seuil volume
        if not isinstance(self.volume_threshold, Decimal):
            try:
                self.volume_threshold = Decimal(str(self.volume_threshold))
            except (ValueError, TypeError):
                raise ConfigurationError("volume_threshold must be convertible to Decimal")
        
        if self.volume_threshold < 0:
            raise ConfigurationError("volume_threshold must be positive")
    
    def to_dict(self) -> dict:
        """Export configuration vers dictionnaire"""
        return {
            'enable_signals': self.enable_signals,
            'signal_smoothing': self.signal_smoothing,
            'volume_threshold': float(self.volume_threshold),
            'use_decimal': self.use_decimal,
            'store_history': self.store_history
        }