"""
SMA Indicator Main Module
Single responsibility: Orchestrate SMA calculation and signal generation
"""

from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from ...base.indicator import BaseIndicator
from ....core.types import MarketData, Signal, IndicatorResult, SignalDirection, SignalStrength
from ....core.exceptions import IndicatorError

from .config import SMAConfig
from .calculator import SMACalculator


class SMAIndicator(BaseIndicator):
    """
    Simple Moving Average Indicator
    
    Translates NonoBot Rust SMA implementation to Python
    Ultra-modular design with separated concerns:
    - Configuration: config.py
    - Calculation: calculator.py  
    - Orchestration: This module
    - Plotting: plotter.py (future)
    """
    
    def __init__(self, config: SMAConfig = None):
        config = config or SMAConfig()
        super().__init__("SMA", config.to_dict())
        
        self.sma_config = config
        self.calculator = SMACalculator(config)
        self._previous_value: Optional[Decimal] = None
    
    def get_required_periods(self) -> int:
        """Return required number of periods"""
        return self.sma_config.period
    
    def calculate(self, data: MarketData) -> Optional[IndicatorResult]:
        """
        Calculate SMA for new data point
        
        Args:
            data: New market data
            
        Returns:
            IndicatorResult with SMA value or None if not enough data
        """
        try:
            sma_value = self.calculator.calculate_from_data(data)
            
            if sma_value is not None:
                # Store previous value for signal generation
                self._previous_value = self.current_value
                
                return IndicatorResult(
                    value=sma_value,
                    timestamp=data.timestamp,
                    indicator_name="SMA",
                    is_valid=True,
                    metadata={
                        "period": self.sma_config.period,
                        "symbol": data.symbol,
                        "timeframe": data.timeframe.value,
                        "price_used": str(data.close)
                    }
                )
            
            return None
            
        except Exception as e:
            raise IndicatorError(
                f"SMA calculation failed: {str(e)}",
                error_code="SMA_CALCULATION_ERROR",
                details={
                    "symbol": data.symbol,
                    "timestamp": data.timestamp.isoformat(),
                    "period": self.sma_config.period
                }
            ) from e
    
    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """
        Generate trading signal based on price vs SMA crossover
        
        Args:
            current_result: Current SMA calculation result
            
        Returns:
            Signal if crossover detected, None otherwise
        """
        if not self.sma_config.enable_signals:
            return None
        
        if not current_result.is_valid or not self._data_points:
            return None
        
        current_price = self._data_points[-1].close
        sma_value = current_result.value
        
        # Need previous data for crossover detection
        if len(self._data_points) < 2 or self._previous_value is None:
            return None
        
        previous_price = self._data_points[-2].close
        previous_sma = self._previous_value
        
        # Detect crossovers
        signal_direction = None
        signal_strength = SignalStrength.WEAK
        
        # Bullish crossover: price crosses above SMA
        if (previous_price <= previous_sma and 
            current_price > sma_value and
            abs(current_price - sma_value) / sma_value > self.sma_config.crossover_sensitivity):
            
            signal_direction = SignalDirection.BUY
            
            # Stronger signal if price moves significantly above SMA
            price_distance = (current_price - sma_value) / sma_value
            if price_distance > 0.01:  # 1%
                signal_strength = SignalStrength.MEDIUM
            if price_distance > 0.02:  # 2%
                signal_strength = SignalStrength.STRONG
        
        # Bearish crossover: price crosses below SMA
        elif (previous_price >= previous_sma and 
              current_price < sma_value and
              abs(current_price - sma_value) / sma_value > self.sma_config.crossover_sensitivity):
            
            signal_direction = SignalDirection.SELL
            
            # Stronger signal if price moves significantly below SMA
            price_distance = (sma_value - current_price) / sma_value
            if price_distance > 0.01:  # 1%
                signal_strength = SignalStrength.MEDIUM
            if price_distance > 0.02:  # 2%
                signal_strength = SignalStrength.STRONG
        
        if signal_direction:
            confidence = min(Decimal('0.8'), Decimal('0.5') + abs(current_price - sma_value) / sma_value * 10)
            
            return Signal(
                direction=signal_direction,
                strength=signal_strength,
                price=current_price,
                timestamp=current_result.timestamp,
                source=f"SMA({self.sma_config.period})",
                confidence=confidence,
                metadata={
                    "sma_value": str(sma_value),
                    "price_sma_diff": str(current_price - sma_value),
                    "crossover_type": "bullish" if signal_direction == SignalDirection.BUY else "bearish"
                }
            )
        
        return None
    
    def get_trend_direction(self) -> Optional[SignalDirection]:
        """
        Get current trend based on price vs SMA
        """
        if not self.is_ready or not self._data_points:
            return None
        
        current_price = self._data_points[-1].close
        sma_value = self.current_value
        
        if current_price > sma_value:
            return SignalDirection.BUY
        elif current_price < sma_value:
            return SignalDirection.SELL
        else:
            return SignalDirection.NEUTRAL
    
    def get_distance_from_sma(self) -> Optional[float]:
        """
        Get price distance from SMA as percentage
        """
        if not self.is_ready or not self._data_points:
            return None
        
        current_price = self._data_points[-1].close
        sma_value = self.current_value
        
        return float((current_price - sma_value) / sma_value * 100)