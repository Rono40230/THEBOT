"""
SuperTrend Configuration Module
Single responsibility: Manage SuperTrend-specific configuration with Pydantic validation
"""

from decimal import Decimal
from typing import Any, Dict

from pydantic import BaseModel, Field

from ....core.exceptions import ConfigError


class SuperTrendConfig(BaseModel):
    """SuperTrend configuration with Pydantic validation"""

    # Core parameters
    atr_period: int = Field(10, ge=2, le=50, description="ATR calculation period")
    multiplier: Decimal = Field(Decimal("3.0"), gt=0, le=10, description="ATR multiplier for bands")

    # Signal generation
    enable_signals: bool = Field(True, description="Enable signal generation")

    # Performance options
    use_decimal: bool = Field(True, description="Use Decimal for precision")
    store_history: bool = Field(True, description="Store calculation history")

    class Config:
        """Pydantic configuration"""
        validate_assignment = True
        arbitrary_types_allowed = True

    def validate_config(self) -> None:
        """Legacy validation method for compatibility"""
        # Pydantic handles validation automatically
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuperTrendConfig":
        """Create from dictionary"""
        return cls(**data)
