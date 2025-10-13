"""
OBV Calculator - Single Responsibility: Calculate On Balance Volume
Translation from NonoBot Rust implementation
"""

from decimal import Decimal
from typing import List, Optional

from ....core.types import IndicatorResult, MarketData
from ...base.indicator import BaseIndicator
from .config import OBVConfig


class OBVCalculator:
    """
    On Balance Volume Calculator
    Pure calculation logic without orchestration
    """

    def __init__(self, config: OBVConfig):
        self.config = config
        self._obv_value = Decimal("0")
        self._previous_close: Optional[Decimal] = None

    def calculate(self, market_data: MarketData) -> Decimal:
        """
        Calculate OBV for new market data

        Args:
            market_data: New OHLCV data

        Returns:
            Current OBV value
        """
        if self._previous_close is None:
            # First data point
            self._previous_close = market_data.close
            return self._obv_value

        # OBV Logic:
        # - If close > previous_close: OBV += volume
        # - If close < previous_close: OBV -= volume
        # - If close = previous_close: OBV unchanged

        if market_data.close > self._previous_close:
            self._obv_value += market_data.volume
        elif market_data.close < self._previous_close:
            self._obv_value -= market_data.volume
        # Equal prices: no change to OBV

        self._previous_close = market_data.close
        return self._obv_value

    def reset(self) -> None:
        """Reset calculator state"""
        self._obv_value = Decimal("0")
        self._previous_close = None

    @property
    def current_value(self) -> Decimal:
        """Get current OBV value"""
        return self._obv_value

    def is_ready(self, data_count: int) -> bool:
        """Check if enough data for calculation"""
        return data_count >= 2  # Need at least 2 data points
