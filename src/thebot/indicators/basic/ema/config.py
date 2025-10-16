"""
Configuration pour l'indicateur EMA (Exponential Moving Average)
Module ultra-modulaire - Responsabilité unique : Validation des paramètres EMA
"""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator

from ....core.exceptions import ConfigurationError


class EMAConfig(BaseModel):
    """Configuration validée pour l'indicateur EMA avec Pydantic"""

    period: int = Field(20, gt=1, le=200, description="EMA calculation period")
    smoothing_factor: Optional[Decimal] = Field(None, description="Smoothing factor (auto-calculated if None)")
    enable_signals: bool = Field(True, description="Enable signal generation")
    crossover_sensitivity: Decimal = Field(Decimal("0.005"), gt=0, description="Crossover sensitivity (0.5%)")
    use_decimal: bool = Field(True, description="Use Decimal for precision")
    store_history: bool = Field(True, description="Store calculation history")

    class Config:
        """Pydantic configuration"""
        validate_assignment = True
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        # Auto-calcul du smoothing factor si non fourni
        if self.smoothing_factor is None:
            self.smoothing_factor = Decimal("2") / (Decimal(str(self.period)) + 1)

    @validator('smoothing_factor', pre=True, always=True)
    def validate_smoothing_factor(cls, v, values):
        """Validate and convert smoothing factor"""
        if v is None:
            return v
        if not isinstance(v, Decimal):
            try:
                return Decimal(str(v))
            except (ValueError, TypeError):
                raise ValueError("smoothing_factor must be convertible to Decimal")
        return v

    def validate_config(self) -> None:
        """Legacy validation method for compatibility"""
        # Pydantic handles validation automatically
        pass

    def get_alpha(self) -> Decimal:
        """Retourne le facteur de lissage (alpha) pour le calcul EMA"""
        if self.smoothing_factor is None:
            return Decimal("2") / (Decimal(str(self.period)) + 1)
        return self.smoothing_factor

    def get_one_minus_alpha(self) -> Decimal:
        """Retourne (1 - alpha) pour optimiser les calculs"""
        alpha = self.get_alpha()
        return Decimal("1") - alpha

    def to_dict(self) -> dict:
        """Export configuration vers dictionnaire"""
        return self.dict()

    @classmethod
    def from_dict(cls, data: dict) -> "EMAConfig":
        """Create from dictionary"""
        return cls(**data)
