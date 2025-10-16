"""
MACD Configuration Module
Single responsibility: Manage MACD-specific configuration with Pydantic validation
"""

from decimal import Decimal
from typing import Any, Dict

from pydantic import BaseModel, Field, field_validator

from ....core.exceptions import ConfigError


class MACDConfig(BaseModel):
    """Moving Average Convergence Divergence configuration with Pydantic validation"""

    # Core calculation parameters
    fast_period: int = Field(12, gt=1, le=200, description="Fast EMA period")
    slow_period: int = Field(26, gt=1, le=200, description="Slow EMA period")
    signal_period: int = Field(9, gt=1, le=200, description="Signal line EMA period")
    source: str = Field("close", description="Price source for calculation")

    # Visual parameters
    macd_color: str = Field("#2196F3", description="MACD line color")
    signal_color: str = Field("#FF5722", description="Signal line color")
    histogram_enabled: bool = Field(True, description="Enable histogram display")
    histogram_positive_color: str = Field("#4CAF50", description="Positive histogram color")
    histogram_negative_color: str = Field("#F44336", description="Negative histogram color")
    line_width: int = Field(2, ge=1, le=5, description="Line width")

    # Signal generation
    enable_signals: bool = Field(True, description="Enable signal generation")
    zero_line_sensitivity: Decimal = Field(Decimal("0.001"), gt=0, description="Zero line crossover sensitivity")
    zero_line_enabled: bool = Field(True, description="Enable zero line signals")
    crossover_signals: bool = Field(True, description="Enable MACD/signal crossover signals")

    # Performance options
    use_decimal: bool = Field(True, description="Use Decimal for precision")
    store_history: bool = Field(True, description="Store calculation history")

    class Config:
        """Pydantic configuration"""
        validate_assignment = True
        arbitrary_types_allowed = True

    @field_validator('source')
    @classmethod
    def validate_source(cls, v):
        """Validate price source"""
        valid_sources = ["open", "high", "low", "close", "typical", "weighted"]
        if v not in valid_sources:
            raise ValueError(f"source must be one of {valid_sources}")
        return v

    @field_validator('slow_period')
    @classmethod
    def validate_period_relationship(cls, v, info):
        """Validate period relationships"""
        data = info.data
        if 'fast_period' in data and v <= data['fast_period']:
            raise ValueError("slow_period must be > fast_period")
        return v

    def get_trading_style_config(self, style: str) -> "MACDConfig":
        """Return optimized configuration for trading style"""
        configs = {
            "scalping": {
                "fast_period": 8,
                "slow_period": 21,
                "signal_period": 5,
                "crossover_signals": True,
            },
            "day_trading": {
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9,
                "crossover_signals": True,
            },
            "swing_trading": {
                "fast_period": 12,
                "slow_period": 30,
                "signal_period": 12,
                "crossover_signals": False,
            },
            "position_trading": {
                "fast_period": 15,
                "slow_period": 35,
                "signal_period": 15,
                "crossover_signals": False,
            },
        }

        if style in configs:
            # Create new instance with modified parameters
            config_dict = self.model_dump()
            config_dict.update(configs[style])
            return MACDConfig(**config_dict)

        return self

    def validate_config(self) -> None:
        """Legacy validation method for compatibility"""
        # Pydantic handles validation automatically
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MACDConfig":
        """Create from dictionary"""
        return cls(**data)
