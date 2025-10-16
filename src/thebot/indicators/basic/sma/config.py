"""
SMA Configuration Module
Single responsibility: Manage SMA-specific configuration
"""

from pydantic import BaseModel, Field, validator
from typing import Any, Dict

from ....core.exceptions import ConfigError


class SMAConfig(BaseModel):
    """Simple Moving Average configuration with Pydantic validation"""

    # Core parameters
    period: int = Field(20, gt=0, le=1000, description="SMA calculation period")

    # Signal generation
    enable_signals: bool = Field(True, description="Enable signal generation")
    crossover_sensitivity: float = Field(0.001, gt=0, description="Minimum price change for signal")

    # Performance options
    use_decimal: bool = Field(True, description="Use Decimal for precision")
    store_history: bool = Field(True, description="Store calculation history")

    class Config:
        """Pydantic configuration"""
        validate_assignment = True
        arbitrary_types_allowed = True

    @validator('period')
    def validate_period(cls, v):
        """Additional validation for period"""
        if v < 2:
            raise ValueError('SMA period must be at least 2')
        return v

    def validate_config(self) -> None:
        """Legacy validation method for compatibility"""
        # Pydantic handles validation automatically
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SMAConfig":
        """Create from dictionary"""
        return cls(**data)

    def copy(self, **changes) -> "SMAConfig":
        """Create a copy with optional changes"""
        return self.copy(update=changes)
