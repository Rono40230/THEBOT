"""
SuperTrend Indicator - Clean Implementation
"""

from decimal import Decimal
from typing import Optional

from ...base.indicator import BaseIndicator
from ....core.types import MarketData, IndicatorResult, Signal, SignalDirection, SignalStrength
from ....core.exceptions import IndicatorError
from .config import SuperTrendConfig
from .calculator import SuperTrendCalculator


class SuperTrendIndicator(BaseIndicator):
    """SuperTrend Indicator"""
    
    def __init__(self, config: SuperTrendConfig = None):
        config = config or SuperTrendConfig()
        super().__init__("SuperTrend", config.to_dict())
        
        self.supertrend_config = config
        self.calculator = SuperTrendCalculator(config)
    
    def get_required_periods(self) -> int:
        """Return required number of periods"""
        return self.supertrend_config.atr_period
    
    def calculate(self, data: MarketData) -> Optional[IndicatorResult]:
        """Calculate SuperTrend for new data point"""
        try:
            result = self.calculator.calculate_from_data(data)
            
            if result:
                supertrend_value, trend_direction = result
                
                signal_strength = Decimal('1.0') if trend_direction == 1 else Decimal('-1.0')
                trend_name = "UP" if trend_direction == 1 else "DOWN"
                
                return IndicatorResult(
                    value=supertrend_value,
                    signal_strength=signal_strength,
                    metadata={
                        'trend_direction': trend_direction,
                        'trend_name': trend_name,
                        'atr_period': self.supertrend_config.atr_period,
                        'multiplier': str(self.supertrend_config.multiplier)
                    }
                )
            
            return None
            
        except Exception as e:
            raise IndicatorError(f"SuperTrend calculation failed: {e}")
    
    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """Generate trading signal based on SuperTrend direction"""
        if not current_result or not current_result.metadata:
            return None
        
        trend_direction = current_result.metadata.get('trend_direction')
        if trend_direction is None:
            return None
        
        direction = SignalDirection.BUY if trend_direction == 1 else SignalDirection.SELL
        strength = SignalStrength.MEDIUM
        
        return Signal(
            direction=direction,
            strength=strength,
            confidence=abs(current_result.signal_strength),
            metadata={
                'indicator': 'SuperTrend',
                'trend_direction': trend_direction,
                'trend_name': current_result.metadata.get('trend_name', 'Unknown')
            }
        )

from decimal import Decimal
from typing import Optional, List
from ...base.indicator import BaseIndicator
from ....core.types import MarketData, IndicatorResult, Signal, SignalDirection
from ....core.exceptions import IndicatorError
from .config import SuperTrendConfig
from .calculator import SuperTrendCalculator


class SuperTrendIndicator(BaseIndicator):
    """
    SuperTrend Indicator
    Orchestration between configuration, calculation and signaling
    """
    
    def __init__(self, config: SuperTrendConfig = None):
        config = config or SuperTrendConfig()
        super().__init__("SuperTrend", config.to_dict())
        
        self.supertrend_config = config
        self.calculator = SuperTrendCalculator(config)
        

    
    def get_required_periods(self) -> int:
        """Return required number of periods"""
        return self.supertrend_config.atr_period
    
    def calculate(self, data: MarketData) -> Optional[IndicatorResult]:
        """
        Calculate SuperTrend for new data point
        
        Args:
            data: New market data
            
        Returns:
            IndicatorResult with SuperTrend value and trend direction
        """
        try:
            result = self.calculator.calculate_from_data(data)
            
            if result:
                supertrend_value, trend_direction = result
                
                # Map trend direction to signal strength
                signal_strength = Decimal('1.0') if trend_direction == 1 else Decimal('-1.0')
                trend_name = "UP" if trend_direction == 1 else "DOWN"
                
                return IndicatorResult(
                    value=supertrend_value,
                    signal_strength=signal_strength,
                    metadata={
                        'trend_direction': trend_direction,
                        'trend_name': trend_name,
                        'atr_period': self.supertrend_config.atr_period,
                        'multiplier': str(self.supertrend_config.multiplier)
                    }
                )
            
            return None
            
        except Exception as e:
            raise IndicatorError(f"SuperTrend calculation failed: {e}")
    
    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """
        Generate trading signal based on SuperTrend direction
        
        Args:
            current_result: Current SuperTrend calculation result
            
        Returns:
            Signal based on trend direction
        """
        if not current_result or not current_result.metadata:
            return None
        
        trend_direction = current_result.metadata.get('trend_direction')
        if trend_direction is None:
            return None
        
        # Signal basique selon la tendance
        from ....core.types import Signal, SignalDirection, SignalStrength
        
        direction = SignalDirection.BUY if trend_direction == 1 else SignalDirection.SELL
        strength = SignalStrength.MEDIUM  # Force moyenne par défaut
        
        return Signal(
            direction=direction,
            strength=strength,
            confidence=abs(current_result.signal_strength),
            metadata={
                'indicator': 'SuperTrend',
                'trend_direction': trend_direction,
                'trend_name': current_result.metadata.get('trend_name', 'Unknown')
            }
        )
    
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
        """Add new data and calculate SuperTrend"""
        self._data_history.append(market_data)
        
        # Keep reasonable history (memory management)
        if len(self._data_history) > 1000:
            self._data_history = self._data_history[-500:]
        
        # Calculate SuperTrend
        supertrend_value, trend_direction, upper_band, lower_band = self.calculator.calculate(market_data)
        
        if not self.is_ready:
            return None
        
        # Create result
        result = IndicatorResult(
            value=supertrend_value,
            timestamp=market_data.timestamp,
            indicator_name=self.name,
            metadata={
                'supertrend': float(supertrend_value),
                'trend_direction': trend_direction,
                'upper_band': float(upper_band),
                'lower_band': float(lower_band),
                'trend_name': "Uptrend" if trend_direction == 1 else "Downtrend",
                'atr_period': self.config.atr_period,
                'multiplier': float(self.config.multiplier),
                'price': float(market_data.close)
            }
        )
        
        return result
    
    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """
        Generate signal based on SuperTrend trend changes
        """
        if not self.is_ready or len(self._data_history) < 2:
            return None
        
        current_trend = self.calculator.current_trend
        
        # Check for trend change by looking at previous calculation
        if len(self._data_history) >= 2:
            # Recalculate for previous data to detect trend change
            prev_data = self._data_history[-2]
            temp_calc = SuperTrendCalculator(self.config)
            
            # Build up to previous state
            for data in self._data_history[:-1]:
                temp_calc.calculate(data)
            
            prev_trend = temp_calc.current_trend
            
            # Signal on trend change
            if prev_trend != current_trend:
                if current_trend == 1:  # Changed to uptrend
                    return Signal(
                        direction=SignalDirection.BUY,
                        strength=0.8,  # Strong signal
                        source=self.name,
                        reason=f"SuperTrend changed to uptrend (ATR:{self.config.atr_period}, Mult:{self.config.multiplier})"
                    )
                else:  # Changed to downtrend
                    return Signal(
                        direction=SignalDirection.SELL,
                        strength=0.8,
                        source=self.name,
                        reason=f"SuperTrend changed to downtrend (ATR:{self.config.atr_period}, Mult:{self.config.multiplier})"
                    )
        
        return None
    
    def get_trend_strength(self) -> Optional[str]:
        """
        Get trend strength based on price distance from SuperTrend
        """
        if not self.is_ready:
            return None
        
        current_data = self._data_history[-1]
        supertrend_val = self.calculator.current_value
        
        if supertrend_val is None:
            return None
        
        # Calculate distance as percentage
        distance_pct = abs(current_data.close - supertrend_val) / supertrend_val * 100
        
        if distance_pct < 0.5:
            return "weak"
        elif distance_pct < 2.0:
            return "moderate"
        else:
            return "strong"
    
    def is_price_above_supertrend(self) -> Optional[bool]:
        """Check if current price is above SuperTrend line"""
        if not self.is_ready:
            return None
        
        current_data = self._data_history[-1]
        supertrend_val = self.calculator.current_value
        
        if supertrend_val is None:
            return None
        
        return current_data.close > supertrend_val
    
    def get_support_resistance_level(self) -> Optional[Decimal]:
        """
        Get current SuperTrend value as dynamic support/resistance
        """
        if not self.is_ready:
            return None
        
        return self.calculator.current_value
    
    def reset(self) -> None:
        """Reset indicator state"""
        self.calculator.reset()
        self._data_history.clear()