"""
OBV Indicator - Clean Implementation
"""

from decimal import Decimal
from typing import Optional

from ...base.indicator import BaseIndicator
from ....core.types import MarketData, IndicatorResult, Signal
from ....core.exceptions import IndicatorError
from .config import OBVConfig
from .calculator import OBVCalculator


class OBVIndicator(BaseIndicator):
    """On Balance Volume Indicator"""
    
    def __init__(self, config: OBVConfig = None):
        config = config or OBVConfig()
        super().__init__("OBV", config.to_dict())
        
        self.obv_config = config
        self.calculator = OBVCalculator(config)
    
    def get_required_periods(self) -> int:
        """Return required number of periods"""
        return 1
    
    def calculate(self, data: MarketData) -> Optional[IndicatorResult]:
        """Calculate OBV for new data point"""
        try:
            obv_value = self.calculator.calculate_from_data(data)
            
            if obv_value is not None:
                return IndicatorResult(
                    value=obv_value,
                    signal_strength=Decimal('0.0'),
                    metadata={
                        'volume': str(data.volume),
                        'price_change': str(data.close - data.open)
                    }
                )
            
            return None
            
        except Exception as e:
            raise IndicatorError(f"OBV calculation failed: {e}")
    
    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """Generate trading signal based on OBV trend"""
        return None

from decimal import Decimal
from typing import Optional, List
from ...base.indicator import BaseIndicator
from ....core.types import MarketData, IndicatorResult, Signal, SignalDirection
from ....core.exceptions import IndicatorError
from .config import OBVConfig
from .calculator import OBVCalculator


class OBVIndicator(BaseIndicator):
    """
    On Balance Volume Indicator
    Orchestration between configuration, calculation and signaling
    """
    
    def __init__(self, config: OBVConfig = None):
        config = config or OBVConfig()
        super().__init__("OBV", config.to_dict())
        
        self.obv_config = config
        self.calculator = OBVCalculator(config)
        self._data_history: List[MarketData] = []
    
    def get_required_periods(self) -> int:
        """Return required number of periods"""
        return 1  # OBV needs only current period
    
    def calculate(self, data: MarketData) -> Optional[IndicatorResult]:
        """
        Calculate OBV for new data point
        
        Args:
            data: New market data
            
        Returns:
            IndicatorResult with OBV value
        """
        try:
            obv_value = self.calculator.calculate_from_data(data)
            
            if obv_value is not None:
                return IndicatorResult(
                    value=obv_value,
                    signal_strength=Decimal('0.0'),
                    metadata={
                        'volume': str(data.volume),
                        'price_change': str(data.close - data.open)
                    }
                )
            
            return None
            
        except Exception as e:
            raise IndicatorError(f"OBV calculation failed: {e}")
    
    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """
        Generate trading signal based on OBV trend
        
        Args:
            current_result: Current OBV calculation result
            
        Returns:
            Signal based on volume trend, None if not enough data
        """
        # OBV signals basiques - peut être étendu
        if not current_result or not current_result.value:
            return None
        
        # Pas de signal pour l'instant - juste validation
        return None
    
    @property
    def is_ready(self) -> bool:
        return len(self._data_history) >= self.get_required_periods()
    
    @property
    def current_value(self) -> Optional[Decimal]:
        if not self.is_ready:
            return None
        return self.calculator.current_value
    
    @property
    def data_count(self) -> int:
        return len(self._data_history)
    
    def add_data(self, market_data: MarketData) -> Optional[IndicatorResult]:
        """Add new data and calculate OBV"""
        self._data_history.append(market_data)
        
        # Keep reasonable history (memory management)
        if len(self._data_history) > 1000:
            self._data_history = self._data_history[-500:]
        
        # Calculate OBV
        obv_value = self.calculator.calculate(market_data)
        
        if not self.is_ready:
            return None
        
        # Create result
        result = IndicatorResult(
            value=obv_value,
            timestamp=market_data.timestamp,
            indicator_name=self.name,
            metadata={
                'obv': float(obv_value),
                'volume': float(market_data.volume),
                'close': float(market_data.close),
                'trend': self._get_obv_trend()
            }
        )
        
        return result
    
    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """
        Generate signal based on OBV trend
        Simple implementation: OBV rising = bullish, falling = bearish
        """
        if not self.is_ready or len(self._data_history) < 3:
            return None
        
        trend = self._get_obv_trend()
        
        if trend == "bullish":
            return Signal(
                direction=SignalDirection.BUY,
                strength=0.6,  # Moderate strength
                source=self.name,
                reason=f"OBV trending upward - volume supporting price movement"
            )
        elif trend == "bearish":
            return Signal(
                direction=SignalDirection.SELL,
                strength=0.6,
                source=self.name,
                reason=f"OBV trending downward - volume not supporting price"
            )
        
        return None
    
    def _get_obv_trend(self) -> str:
        """
        Determine OBV trend based on recent values
        Simple implementation using last 3 periods
        """
        if len(self._data_history) < 3:
            return "neutral"
        
        # Get last 3 OBV calculations (simplified)
        recent_data = self._data_history[-3:]
        obv_values = []
        
        temp_calc = OBVCalculator(self.config)
        for data in recent_data:
            obv_val = temp_calc.calculate(data)
            obv_values.append(obv_val)
        
        if len(obv_values) >= 2:
            if obv_values[-1] > obv_values[-2]:
                return "bullish"
            elif obv_values[-1] < obv_values[-2]:
                return "bearish"
        
        return "neutral"
    
    def get_divergence_signal(self, price_trend: str) -> Optional[str]:
        """
        Check for price/OBV divergence
        price_trend: "up", "down", "neutral"
        """
        if not self.is_ready:
            return None
        
        obv_trend = self._get_obv_trend()
        
        # Bullish divergence: price down, OBV up
        if price_trend == "down" and obv_trend == "bullish":
            return "bullish_divergence"
        
        # Bearish divergence: price up, OBV down  
        if price_trend == "up" and obv_trend == "bearish":
            return "bearish_divergence"
        
        return None
    
    def reset(self) -> None:
        """Reset indicator state"""
        self.calculator.reset()
        self._data_history.clear()