"""
Configuration pour l'indicateur RSI (Relative Strength Index)
Module ultra-modulaire - Responsabilité unique : Validation des paramètres RSI
"""

from decimal import Decimal
from dataclasses import dataclass

from thebot.core.exceptions import ConfigurationError


@dataclass
class RSIConfig:
    """Configuration validée pour l'indicateur RSI"""
    
    period: int = 14
    overbought_level: Decimal = Decimal('70')  # Niveau de surachat
    oversold_level: Decimal = Decimal('30')    # Niveau de survente
    extreme_overbought: Decimal = Decimal('80') # Niveau extrême
    extreme_oversold: Decimal = Decimal('20')   # Niveau extrême
    smoothing_method: str = "ema"  # "ema" ou "sma"
    enable_signals: bool = True
    use_decimal: bool = True
    store_history: bool = True
    
    def __post_init__(self):
        """Validation automatique des paramètres"""
        self.validate()
    
    def validate(self) -> None:
        """Validation complète des paramètres RSI"""
        
        # Validation période
        if not isinstance(self.period, int):
            raise ConfigurationError("period must be an integer")
        
        if self.period < 2:
            raise ConfigurationError("period must be at least 2")
        
        if self.period > 100:
            raise ConfigurationError("period must not exceed 100")
        
        # Validation niveaux
        levels = ['overbought_level', 'oversold_level', 'extreme_overbought', 'extreme_oversold']
        for level_name in levels:
            level_value = getattr(self, level_name)
            if not isinstance(level_value, Decimal):
                try:
                    setattr(self, level_name, Decimal(str(level_value)))
                    level_value = getattr(self, level_name)
                except (ValueError, TypeError):
                    raise ConfigurationError(f"{level_name} must be convertible to Decimal")
            
            if not (0 <= level_value <= 100):
                raise ConfigurationError(f"{level_name} must be between 0 and 100")
        
        # Vérification cohérence des niveaux
        if self.oversold_level >= self.overbought_level:
            raise ConfigurationError("oversold_level must be < overbought_level")
        
        if self.extreme_oversold >= self.oversold_level:
            raise ConfigurationError("extreme_oversold must be < oversold_level")
        
        if self.extreme_overbought <= self.overbought_level:
            raise ConfigurationError("extreme_overbought must be > overbought_level")
        
        # Validation méthode de lissage
        if self.smoothing_method not in ["sma", "ema"]:
            raise ConfigurationError("smoothing_method must be 'sma' or 'ema'")
    
    def get_smoothing_alpha(self) -> Decimal:
        """Retourne alpha pour lissage EMA"""
        return Decimal('2') / (Decimal(str(self.period)) + 1)
    
    def to_dict(self) -> dict:
        """Export configuration vers dictionnaire"""
        return {
            'period': self.period,
            'overbought_level': float(self.overbought_level),
            'oversold_level': float(self.oversold_level),
            'extreme_overbought': float(self.extreme_overbought),
            'extreme_oversold': float(self.extreme_oversold),
            'smoothing_method': self.smoothing_method,
            'enable_signals': self.enable_signals,
            'use_decimal': self.use_decimal,
            'store_history': self.store_history
        }