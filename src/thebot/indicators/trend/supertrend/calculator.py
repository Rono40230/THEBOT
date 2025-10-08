"""
SuperTrend Calculator - Single Responsibility: Calculate SuperTrend values
Translation from NonoBot Rust implementation
"""

from decimal import Decimal
from typing import List, Optional, Tuple
from collections import deque
from ...base.indicator import BaseIndicator
from ....core.types import MarketData
from .config import SuperTrendConfig


class SuperTrendCalculator:
    """
    SuperTrend Calculator  
    Pure calculation logic without orchestration
    """
    
    def __init__(self, config: SuperTrendConfig):
        self.config = config
        self._data_history: deque = deque(maxlen=config.atr_period * 2)
        self._atr_values: deque = deque(maxlen=config.atr_period)
        self._supertrend_value: Optional[Decimal] = None
        self._trend_direction: int = 1  # 1 = uptrend, -1 = downtrend
        self._upper_band: Optional[Decimal] = None
        self._lower_band: Optional[Decimal] = None
        
    def calculate(self, market_data: MarketData) -> Tuple[Decimal, int, Decimal, Decimal]:
        """
        Calculate SuperTrend for new market data
        
        Args:
            market_data: New OHLCV data
            
        Returns:
            Tuple of (supertrend_value, trend_direction, upper_band, lower_band)
        """
        self._data_history.append(market_data)
        
        if len(self._data_history) < 2:
            # Need at least 2 data points for ATR
            return Decimal('0'), 1, Decimal('0'), Decimal('0')
        
        # Calculate ATR
        atr = self._calculate_atr()
        self._atr_values.append(atr)
        
        if len(self._atr_values) < self.config.atr_period:
            return Decimal('0'), 1, Decimal('0'), Decimal('0')
        
        # Calculate basic bands
        hl2 = (market_data.high + market_data.low) / 2
        current_atr = sum(self._atr_values) / len(self._atr_values)
        
        basic_upper = hl2 + (self.config.multiplier * current_atr)
        basic_lower = hl2 - (self.config.multiplier * current_atr)
        
        # Calculate final bands with previous values
        if self._upper_band is None:
            final_upper = basic_upper
            final_lower = basic_lower
        else:
            # Upper band: if basic_upper < prev_upper OR prev_close > prev_upper, use basic_upper
            prev_close = self._data_history[-2].close if len(self._data_history) >= 2 else market_data.close
            
            final_upper = basic_upper if (basic_upper < self._upper_band or prev_close > self._upper_band) else self._upper_band
            final_lower = basic_lower if (basic_lower > self._lower_band or prev_close < self._lower_band) else self._lower_band
        
        # Determine trend and SuperTrend value
        if self._supertrend_value is None:
            # First calculation
            if market_data.close <= final_lower:
                self._trend_direction = -1
                self._supertrend_value = final_upper
            else:
                self._trend_direction = 1
                self._supertrend_value = final_lower
        else:
            # Update based on previous trend
            if self._trend_direction == 1:  # Was uptrend
                if market_data.close <= final_lower:
                    self._trend_direction = -1
                    self._supertrend_value = final_upper
                else:
                    self._supertrend_value = final_lower
            else:  # Was downtrend
                if market_data.close >= final_upper:
                    self._trend_direction = 1
                    self._supertrend_value = final_lower
                else:
                    self._supertrend_value = final_upper
        
        self._upper_band = final_upper
        self._lower_band = final_lower
        
        return self._supertrend_value, self._trend_direction, self._upper_band, self._lower_band
    
    def _calculate_atr(self) -> Decimal:
        """Calculate Average True Range for current period"""
        if len(self._data_history) < 2:
            return Decimal('0')
        
        current = self._data_history[-1]
        previous = self._data_history[-2]
        
        # True Range = max(high-low, |high-prev_close|, |low-prev_close|)
        tr1 = current.high - current.low
        tr2 = abs(current.high - previous.close)
        tr3 = abs(current.low - previous.close)
        
        true_range = max(tr1, tr2, tr3)
        return true_range
    
    def reset(self) -> None:
        """Reset calculator state"""
        self._data_history.clear()
        self._atr_values.clear()
        self._supertrend_value = None
        self._trend_direction = 1
        self._upper_band = None
        self._lower_band = None
    
    @property
    def current_value(self) -> Optional[Decimal]:
        """Get current SuperTrend value"""
        return self._supertrend_value
    
    @property
    def current_trend(self) -> int:
        """Get current trend direction (1=up, -1=down)"""
        return self._trend_direction
    
    def is_ready(self, data_count: int) -> bool:
        """Check if enough data for calculation"""
        return data_count >= self.config.atr_period + 1