"""
Base indicator interface - Ultra-modular design
Single responsibility: Define the contract for all indicators
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, List, Optional

from ...core.exceptions import IndicatorError, InsufficientDataError
from ...core.types import IndicatorResult, MarketData, Signal


class BaseIndicator(ABC):
    """
    Abstract base class for all technical indicators

    Ensures consistent interface across all indicators
    Implements common functionality once
    """

    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self._data_points: List[MarketData] = []
        self._results: List[IndicatorResult] = []
        self._is_ready = False

    @abstractmethod
    def calculate(self, data: MarketData) -> Optional[IndicatorResult]:
        """
        Calculate indicator value for new data point
        Must be implemented by each indicator
        """
        pass

    @abstractmethod
    def get_required_periods(self) -> int:
        """
        Return minimum number of periods needed
        Must be implemented by each indicator
        """
        pass

    @abstractmethod
    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """
        Generate trading signal from current result
        Must be implemented by each indicator
        """
        pass

    def add_data(self, data: MarketData) -> Optional[IndicatorResult]:
        """
        Add new market data and calculate indicator
        Common functionality for all indicators
        """
        self._data_points.append(data)

        # Keep only required data points for memory efficiency
        max_periods = self.get_required_periods() * 2  # Keep some buffer
        if len(self._data_points) > max_periods:
            self._data_points = self._data_points[-max_periods:]

        # Calculate if we have enough data
        if len(self._data_points) >= self.get_required_periods():
            self._is_ready = True
            result = self.calculate(data)
            if result:
                self._results.append(result)
                # Keep only recent results
                if len(self._results) > 1000:
                    self._results = self._results[-500:]
                return result

        return None

    @property
    def is_ready(self) -> bool:
        """Check if indicator has enough data"""
        return self._is_ready

    @property
    def current_value(self) -> Any:
        """Get current indicator value"""
        if not self._results:
            return None
        return self._results[-1].value

    @property
    def data_count(self) -> int:
        """Get number of data points"""
        return len(self._data_points)

    def get_last_n_results(self, n: int) -> List[IndicatorResult]:
        """Get last N results"""
        return self._results[-n:] if len(self._results) >= n else self._results

    def reset(self):
        """Reset indicator state"""
        self._data_points.clear()
        self._results.clear()
        self._is_ready = False

    def validate_config(self) -> bool:
        """
        Validate indicator configuration
        Can be overridden by specific indicators
        """
        return True

    def get_metadata(self) -> Dict[str, Any]:
        """Get indicator metadata"""
        return {
            "name": self.name,
            "config": self.config,
            "data_points": self.data_count,
            "is_ready": self.is_ready,
            "required_periods": self.get_required_periods(),
        }
