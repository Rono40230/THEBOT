"""
ATR Configuration Module
Single responsibility: Manage ATR-specific configuration with Pydantic validation
"""

from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

from ....core.exceptions import ConfigError


class ATRConfig(BaseModel):
    """Average True Range configuration with Pydantic validation"""

    # Core parameters
    period: int = Field(14, gt=1, le=100, description="ATR calculation period")

    # Calculation options
    smoothing_method: str = Field("sma", description="Smoothing method: 'sma' or 'ema'")

    # Volatility thresholds
    volatility_threshold_low: Decimal = Field(Decimal("0.5"), ge=0, description="Low volatility threshold (%)")
    volatility_threshold_high: Decimal = Field(Decimal("2.0"), gt=0, description="High volatility threshold (%)")

    # Signal generation
    enable_signals: bool = Field(True, description="Enable signal generation")

    # Performance options
    use_decimal: bool = Field(True, description="Use Decimal for precision")
    store_history: bool = Field(True, description="Store calculation history")

    class Config:
        """Pydantic configuration"""
        validate_assignment = True
        arbitrary_types_allowed = True

    @field_validator('smoothing_method')
    @classmethod
    def validate_smoothing_method(cls, v):
        """Validate smoothing method"""
        if v not in ["sma", "ema"]:
            raise ValueError("smoothing_method must be 'sma' or 'ema'")
        return v

    @field_validator('volatility_threshold_high')
    @classmethod
    def validate_volatility_thresholds(cls, v, info):
        """Validate volatility threshold relationships"""
        data = info.data
        if 'volatility_threshold_low' in data and v <= data['volatility_threshold_low']:
            raise ValueError("volatility_threshold_high must be > volatility_threshold_low")
        return v

    def get_smoothing_alpha(self) -> Optional[Decimal]:
        """Return alpha for EMA smoothing, None for SMA"""
        if self.smoothing_method == "ema":
            return Decimal("2") / (Decimal(str(self.period)) + 1)
        return None

    def validate_config(self) -> None:
        """Legacy validation method for compatibility"""
        # Pydantic handles validation automatically
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ATRConfig":
        """Create from dictionary"""
        return cls(**data)
