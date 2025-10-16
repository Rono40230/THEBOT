"""
RSI Configuration Module
Single responsibility: Manage RSI-specific configuration with Pydantic validation
"""

from decimal import Decimal
from typing import Any, Dict

from pydantic import BaseModel, Field, field_validator

from ....core.exceptions import ConfigError


class RSIConfig(BaseModel):
    """Relative Strength Index configuration with Pydantic validation"""

    # Core parameters
    period: int = Field(14, gt=1, le=100, description="RSI calculation period")

    # RSI levels
    overbought_level: Decimal = Field(Decimal("70"), ge=0, le=100, description="Overbought threshold")
    oversold_level: Decimal = Field(Decimal("30"), ge=0, le=100, description="Oversold threshold")
    extreme_overbought: Decimal = Field(Decimal("80"), ge=0, le=100, description="Extreme overbought threshold")
    extreme_oversold: Decimal = Field(Decimal("20"), ge=0, le=100, description="Extreme oversold threshold")

    # Calculation options
    smoothing_method: str = Field("ema", description="Smoothing method: 'ema' or 'sma'")

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

    @field_validator('oversold_level', 'overbought_level', 'extreme_oversold', 'extreme_overbought')
    @classmethod
    def validate_levels(cls, v, info):
        """Validate level relationships"""
        field_name = info.field_name
        data = info.data

        if field_name == 'oversold_level' and 'overbought_level' in data:
            if v >= data['overbought_level']:
                raise ValueError("oversold_level must be < overbought_level")
        elif field_name == 'overbought_level' and 'oversold_level' in data:
            if v <= data['oversold_level']:
                raise ValueError("overbought_level must be > oversold_level")
        elif field_name == 'extreme_oversold' and 'oversold_level' in data:
            if v >= data['oversold_level']:
                raise ValueError("extreme_oversold must be < oversold_level")
        elif field_name == 'extreme_overbought' and 'overbought_level' in data:
            if v <= data['overbought_level']:
                raise ValueError("extreme_overbought must be > overbought_level")
        return v

    def get_smoothing_alpha(self) -> Decimal:
        """Return alpha for EMA smoothing"""
        return Decimal("2") / (Decimal(str(self.period)) + 1)

    def validate_config(self) -> None:
        """Legacy validation method for compatibility"""
        # Pydantic handles validation automatically
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RSIConfig":
        """Create from dictionary"""
        return cls(**data)
