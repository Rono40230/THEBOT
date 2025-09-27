"""
Configuration pour l'indicateur EMA (Exponential Moving Average)
Module ultra-modulaire - Responsabilité unique : Validation des paramètres EMA
"""

from decimal import Decimal
from typing import Optional
from dataclasses import dataclass

from thebot.core.exceptions import ConfigurationError


@dataclass
class EMAConfig:
    """Configuration validée pour l'indicateur EMA"""
    
    period: int
    smoothing_factor: Optional[Decimal] = None  # Auto-calculé si None
    enable_signals: bool = True
    crossover_sensitivity: Decimal = Decimal('0.005')  # 0.5%
    use_decimal: bool = True
    store_history: bool = True
    
    def __post_init__(self):
        """Validation automatique des paramètres"""
        self.validate()
        
        # Auto-calcul du smoothing factor si non fourni
        if self.smoothing_factor is None:
            self.smoothing_factor = Decimal('2') / (Decimal(str(self.period)) + 1)
    
    def validate(self) -> None:
        """Validation complète des paramètres EMA"""
        
        # Validation période
        if not isinstance(self.period, int):
            raise ConfigurationError("period must be an integer")
        
        if self.period < 2:
            raise ConfigurationError("period must be at least 2")
        
        if self.period > 200:
            raise ConfigurationError("period must not exceed 200")
        
        # Validation smoothing factor si fourni
        if self.smoothing_factor is not None:
            if not isinstance(self.smoothing_factor, Decimal):
                try:
                    self.smoothing_factor = Decimal(str(self.smoothing_factor))
                except (ValueError, TypeError):
                    raise ConfigurationError("smoothing_factor must be convertible to Decimal")
            
            if self.smoothing_factor <= 0 or self.smoothing_factor >= 1:
                raise ConfigurationError("smoothing_factor must be between 0 and 1 (exclusive)")
        
        # Validation crossover sensitivity
        if not isinstance(self.crossover_sensitivity, Decimal):
            try:
                self.crossover_sensitivity = Decimal(str(self.crossover_sensitivity))
            except (ValueError, TypeError):
                raise ConfigurationError("crossover_sensitivity must be convertible to Decimal")
        
        if self.crossover_sensitivity < 0 or self.crossover_sensitivity > Decimal('0.1'):
            raise ConfigurationError("crossover_sensitivity must be between 0 and 0.1 (10%)")
    
    def get_alpha(self) -> Decimal:
        """Retourne le facteur de lissage (alpha) pour le calcul EMA"""
        return self.smoothing_factor
    
    def get_one_minus_alpha(self) -> Decimal:
        """Retourne (1 - alpha) pour optimiser les calculs"""
        return Decimal('1') - self.smoothing_factor
    
    def to_dict(self) -> dict:
        """Export configuration vers dictionnaire"""
        return {
            'period': self.period,
            'smoothing_factor': float(self.smoothing_factor),
            'enable_signals': self.enable_signals,
            'crossover_sensitivity': float(self.crossover_sensitivity),
            'use_decimal': self.use_decimal,
            'store_history': self.store_history
        }