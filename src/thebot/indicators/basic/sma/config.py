"""
SMA Configuration Module
Single responsibility: Manage SMA-specific configuration
"""

from dataclasses import dataclass
from typing import Any, Dict

from ....core.exceptions import ConfigError


@dataclass
class SMAConfig:
    """Simple Moving Average configuration"""

    # Core parameters
    period: int = 20

    # Signal generation
    enable_signals: bool = True
    crossover_sensitivity: float = 0.001  # Minimum price change for signal

    # Performance options
    use_decimal: bool = True  # Use Decimal for precision
    store_history: bool = True  # Store calculation history

    def __post_init__(self):
        """Validate configuration after initialization"""
        self.validate()

    def validate(self) -> None:
        """Validate SMA configuration parameters"""

        if not isinstance(self.period, int) or self.period <= 0:
            raise ConfigError(
                "SMA period must be a positive integer",
                error_code="INVALID_PERIOD",
                details={"period": self.period},
            )

        if self.period < 2:
            raise ConfigError(
                "SMA period must be at least 2",
                error_code="PERIOD_TOO_SMALL",
                details={"period": self.period},
            )

        if self.period > 1000:
            raise ConfigError(
                "SMA period too large (max 1000)",
                error_code="PERIOD_TOO_LARGE",
                details={"period": self.period},
            )

        if not 0.0 <= self.crossover_sensitivity <= 1.0:
            raise ConfigError(
                "Crossover sensitivity must be between 0.0 and 1.0",
                error_code="INVALID_SENSITIVITY",
                details={"sensitivity": self.crossover_sensitivity},
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "period": self.period,
            "enable_signals": self.enable_signals,
            "crossover_sensitivity": self.crossover_sensitivity,
            "use_decimal": self.use_decimal,
            "store_history": self.store_history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SMAConfig":
        """Create from dictionary"""
        return cls(**data)

    def copy(self, **changes) -> "SMAConfig":
        """Create a copy with optional changes"""
        data = self.to_dict()
        data.update(changes)
        return self.from_dict(data)
