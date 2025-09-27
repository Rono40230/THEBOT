"""
SMA Calculator Module  
Single responsibility: Pure calculation logic for Simple Moving Average
"""

from collections import deque
from typing import Optional, Deque
from decimal import Decimal
from datetime import datetime

from ....core.types import MarketData, IndicatorResult
from ....core.exceptions import InsufficientDataError, IndicatorError
from .config import SMAConfig


class SMACalculator:
    """
    Pure calculator for Simple Moving Average
    No state management, just calculation logic
    """
    
    def __init__(self, config: SMAConfig):
        self.config = config
        self._price_buffer: Deque[Decimal] = deque(maxlen=config.period)
        self._sum = Decimal('0')
    
    def add_price(self, price: Decimal) -> Optional[Decimal]:
        """
        Add new price and calculate SMA if possible
        
        Args:
            price: New close price
            
        Returns:
            SMA value if enough data, None otherwise
        """
        if price is None or price < 0:
            raise IndicatorError(
                f"Invalid price value: {price}",
                error_code="INVALID_PRICE",
                details={"price": str(price)}
            )
        
        # Use Decimal for precision if configured
        if self.config.use_decimal and not isinstance(price, Decimal):
            price = Decimal(str(price))
        
        # Handle buffer full case (remove oldest)
        if len(self._price_buffer) == self.config.period:
            oldest_price = self._price_buffer[0]
            self._sum -= oldest_price
        
        # Add new price
        self._price_buffer.append(price)
        self._sum += price
        
        # Calculate SMA if we have enough data
        if len(self._price_buffer) == self.config.period:
            return self._sum / self.config.period
        
        return None
    
    def calculate_from_data(self, data: MarketData) -> Optional[Decimal]:
        """Calculate SMA from market data"""
        return self.add_price(data.close)
    
    def get_current_sum(self) -> Decimal:
        """Get current sum (for debugging)"""
        return self._sum
    
    def get_buffer_size(self) -> int:
        """Get current buffer size"""
        return len(self._price_buffer)
    
    def is_ready(self) -> bool:
        """Check if calculator has enough data"""
        return len(self._price_buffer) == self.config.period
    
    def reset(self):
        """Reset calculator state"""
        self._price_buffer.clear()
        self._sum = Decimal('0')
    
    @staticmethod
    def calculate_batch(prices: list, period: int) -> list:
        """
        Calculate SMA for a batch of prices
        Static method for one-off calculations
        """
        if len(prices) < period:
            raise InsufficientDataError(
                f"Need at least {period} prices, got {len(prices)}",
                error_code="INSUFFICIENT_DATA_BATCH"
            )
        
        results = []
        for i in range(period - 1, len(prices)):
            window = prices[i - period + 1:i + 1]
            sma = sum(window) / period
            results.append(sma)
        
        return results