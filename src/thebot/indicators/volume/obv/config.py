"""
OBV Configuration Module
Single responsibility: Manage OBV-specific configuration with Pydantic validation
"""

from decimal import Decimal
from typing import Any, Dict

from pydantic import BaseModel, Field

from ....core.exceptions import ConfigError


class OBVConfig(BaseModel):
    """On-Balance Volume configuration with Pydantic validation"""

    # Signal generation
    enable_signals: bool = Field(True, description="Enable signal generation")
    signal_smoothing: int = Field(3, ge=1, le=20, description="Periods for signal smoothing")

    # Volume parameters
    volume_threshold: Decimal = Field(Decimal("0.1"), ge=0, description="Significant volume threshold")

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
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OBVConfig":
        """Create from dictionary"""
        return cls(**data)
