"""
Squeeze Momentum Indicator - Clean Implementation
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
from .calculator import SqueezeCalculator
from .config import SqueezeConfig


class SqueezeIndicator(BaseIndicator):
    """Squeeze Momentum Indicator"""

    def __init__(self, config: SqueezeConfig = None):
        config = config or SqueezeConfig()
        super().__init__("Squeeze", config.to_dict())

        self.squeeze_config = config
        self.calculator = SqueezeCalculator(config)
        self._previous_momentum = None

    def get_required_periods(self) -> int:
        """Return required number of periods"""
        return self.squeeze_config.get_required_periods()

    def calculate(self, data: MarketData) -> Optional[IndicatorResult]:
        """Calculate Squeeze Momentum for new data point"""
        try:
            result = self.calculator.calculate_from_data(data)

            if result:
                # Main value is momentum
                momentum = result["momentum"]

                # Signal strength based on momentum and squeeze state
                if result["squeeze_active"]:
                    # During squeeze, momentum strength is compressed
                    signal_strength = momentum * Decimal("0.5")
                elif result["squeeze_release"]:
                    # Squeeze release = strong signal
                    signal_strength = momentum * Decimal("2.0")
                else:
                    # Normal momentum
                    signal_strength = momentum

                # Store for trend detection
                self._previous_momentum = self.current_value

                return IndicatorResult(
                    value=momentum,
                    signal_strength=signal_strength,
                    metadata={
                        "squeeze_active": result["squeeze_active"],
                        "squeeze_release": result["squeeze_release"],
                        "squeeze_count": result["squeeze_count"],
                        "squeeze_strength": str(result["squeeze_strength"]),
                        "bb_width": str(result["bollinger_bands"]["width"]),
                        "kc_width": str(result["keltner_channels"]["width"]),
                        "bb_upper": str(result["bollinger_bands"]["upper"]),
                        "bb_lower": str(result["bollinger_bands"]["lower"]),
                        "kc_upper": str(result["keltner_channels"]["upper"]),
                        "kc_lower": str(result["keltner_channels"]["lower"]),
                    },
                )

            return None

        except Exception as e:
            raise IndicatorError(f"Squeeze calculation failed: {e}")

    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """Generate trading signal based on Squeeze Momentum"""
        if not current_result or not current_result.metadata:
            return None

        if not self.squeeze_config.enable_signals:
            return None

        metadata = current_result.metadata
        momentum = current_result.value
        squeeze_release = metadata.get("squeeze_release", False)
        squeeze_active = metadata.get("squeeze_active", False)

        # Strong signals on squeeze release
        if squeeze_release and abs(momentum) > self.squeeze_config.signal_threshold:
            direction = SignalDirection.BUY if momentum > 0 else SignalDirection.SELL
            strength = SignalStrength.STRONG
            confidence = min(abs(current_result.signal_strength), Decimal("1.0"))

            return Signal(
                direction=direction,
                strength=strength,
                confidence=confidence,
                metadata={
                    "indicator": "Squeeze",
                    "trigger": "squeeze_release",
                    "momentum": str(momentum),
                    "squeeze_count": metadata.get("squeeze_count", 0),
                },
            )

        # Medium signals on momentum change during non-squeeze
        if not squeeze_active and self._previous_momentum is not None:
            momentum_change = momentum - self._previous_momentum

            if abs(momentum_change) > self.squeeze_config.signal_threshold:
                direction = (
                    SignalDirection.BUY if momentum_change > 0 else SignalDirection.SELL
                )
                strength = SignalStrength.MEDIUM
                confidence = min(abs(momentum_change), Decimal("1.0"))

                return Signal(
                    direction=direction,
                    strength=strength,
                    confidence=confidence,
                    metadata={
                        "indicator": "Squeeze",
                        "trigger": "momentum_change",
                        "momentum": str(momentum),
                        "momentum_change": str(momentum_change),
                    },
                )

        return None
