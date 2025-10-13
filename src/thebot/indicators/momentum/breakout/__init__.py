"""
Breakout Detector Indicator - Clean Implementation
Translation from NonoBot Rust implementation
"""

from decimal import Decimal
from typing import Optional

from ....core.exceptions import IndicatorError
from ....core.types import (
    IndicatorResult,
    MarketData,
    Signal,
    SignalDirection,
    SignalStrength,
)
from ...base.indicator import BaseIndicator
from .calculator import BreakoutCalculator
from .config import BreakoutConfig


class BreakoutIndicator(BaseIndicator):
    """Breakout Detector Indicator"""

    def __init__(self, config: BreakoutConfig = None):
        config = config or BreakoutConfig()
        super().__init__("Breakout", config.to_dict())

        self.breakout_config = config
        self.calculator = BreakoutCalculator(config)

    def get_required_periods(self) -> int:
        return self.breakout_config.get_required_periods()

    def calculate(self, data: MarketData) -> Optional[IndicatorResult]:
        """Calculate Breakout analysis for new data point"""
        try:
            result = self.calculator.calculate_from_data(data)

            if result:
                breakout_detected = result["breakout_detected"]
                breakout_strength = result["breakout_strength"]
                breakout_type = result["breakout_type"]

                # Main value is breakout strength
                main_value = breakout_strength if breakout_detected else Decimal("0.0")

                # Signal strength based on breakout type and volume
                if breakout_detected:
                    if breakout_type == "resistance":
                        signal_strength = breakout_strength
                    elif breakout_type == "support":
                        signal_strength = -breakout_strength
                    else:
                        signal_strength = Decimal("0.0")

                    # Boost signal if volume confirmed
                    if result.get("volume_confirmed", False):
                        signal_strength *= Decimal("1.5")
                else:
                    signal_strength = Decimal("0.0")

                return IndicatorResult(
                    value=main_value,
                    signal_strength=signal_strength,
                    metadata={
                        "breakout_detected": breakout_detected,
                        "breakout_type": breakout_type or "none",
                        "breakout_strength": str(breakout_strength),
                        "volume_confirmed": result.get("volume_confirmed", False),
                        "resistance_level": str(result.get("resistance_level", "0.0")),
                        "support_level": str(result.get("support_level", "0.0")),
                        "current_price": str(result.get("current_price", "0.0")),
                    },
                )

            return None

        except Exception as e:
            raise IndicatorError(f"Breakout calculation failed: {e}")

    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """Generate trading signal based on Breakout detection"""
        if not current_result or not current_result.metadata:
            return None

        if not self.breakout_config.enable_signals:
            return None

        breakout_detected = current_result.metadata.get("breakout_detected", False)
        breakout_type = current_result.metadata.get("breakout_type")
        breakout_strength = Decimal(
            current_result.metadata.get("breakout_strength", "0.0")
        )
        volume_confirmed = current_result.metadata.get("volume_confirmed", False)

        if (
            not breakout_detected
            or breakout_strength < self.breakout_config.strength_threshold
        ):
            return None

        # Generate signals based on breakout type
        if breakout_type == "resistance":
            direction = SignalDirection.BUY
        elif breakout_type == "support":
            direction = SignalDirection.SELL
        else:
            return None

        # Signal strength based on breakout strength and volume
        if (
            volume_confirmed
            and breakout_strength > self.breakout_config.strength_threshold * 2
        ):
            strength = SignalStrength.STRONG
        elif volume_confirmed:
            strength = SignalStrength.MEDIUM
        else:
            strength = SignalStrength.WEAK

        return Signal(
            direction=direction,
            strength=strength,
            confidence=min(breakout_strength, Decimal("1.0")),
            metadata={
                "indicator": "Breakout",
                "breakout_type": breakout_type,
                "breakout_strength": str(breakout_strength),
                "volume_confirmed": volume_confirmed,
            },
        )
