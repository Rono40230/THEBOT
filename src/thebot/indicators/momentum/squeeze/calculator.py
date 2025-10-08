"""
Squeeze Momentum Calculator
Translation from NonoBot Rust implementation

Implements:
1. Bollinger Bands calculation
2. Keltner Channels calculation  
3. Squeeze detection (BB inside KC)
4. Momentum oscillator
5. Signal generation
"""

from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
import statistics
from collections import deque

from ....core.types import MarketData
from .config import SqueezeConfig


class SqueezeCalculator:
    """
    Squeeze Momentum calculation engine
    
    NonoBot Rust logic:
    - Track BB and KC bands
    - Detect squeeze conditions
    - Calculate momentum direction
    - Generate breakout signals
    """
    
    def __init__(self, config: SqueezeConfig):
        self.config = config
        self.data_history: deque = deque(maxlen=config.get_required_periods())
        self.bb_values: deque = deque(maxlen=50)  # BB history
        self.kc_values: deque = deque(maxlen=50)  # KC history
        self.momentum_values: deque = deque(maxlen=50)  # Momentum history
        
        # State tracking
        self.current_squeeze = False
        self.previous_squeeze = False
        self.squeeze_count = 0
    
    def add_data(self, data: MarketData) -> None:
        """Add new market data point"""
        self.data_history.append(data)
    
    def calculate_bollinger_bands(self) -> Optional[Tuple[Decimal, Decimal, Decimal]]:
        """
        Calculate Bollinger Bands (Middle, Upper, Lower)
        
        Returns:
            Tuple of (middle, upper, lower) or None if insufficient data
        """
        if len(self.data_history) < self.config.bollinger_period:
            return None
        
        # Get recent closes
        closes = [float(d.close) for d in list(self.data_history)[-self.config.bollinger_period:]]
        
        # Calculate SMA (middle band)
        sma = statistics.mean(closes)
        
        # Calculate standard deviation
        variance = sum((x - sma) ** 2 for x in closes) / len(closes)
        std_dev = variance ** 0.5
        
        # Calculate bands
        std_multiplier = float(self.config.bollinger_std)
        middle = Decimal(str(sma))
        upper = Decimal(str(sma + (std_dev * std_multiplier)))
        lower = Decimal(str(sma - (std_dev * std_multiplier)))
        
        return middle, upper, lower
    
    def calculate_atr(self, period: int) -> Optional[Decimal]:
        """
        Calculate Average True Range
        
        Args:
            period: ATR calculation period
            
        Returns:
            ATR value or None if insufficient data
        """
        if len(self.data_history) < period + 1:
            return None
        
        true_ranges = []
        data_list = list(self.data_history)
        
        for i in range(1, len(data_list)):
            current = data_list[i]
            previous = data_list[i-1]
            
            # True Range = max(high-low, |high-prev_close|, |low-prev_close|)
            tr1 = float(current.high - current.low)
            tr2 = abs(float(current.high - previous.close))
            tr3 = abs(float(current.low - previous.close))
            
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)
        
        # Take last 'period' true ranges
        if len(true_ranges) < period:
            return None
        
        recent_trs = true_ranges[-period:]
        atr = statistics.mean(recent_trs)
        
        return Decimal(str(atr))
    
    def calculate_keltner_channels(self) -> Optional[Tuple[Decimal, Decimal, Decimal]]:
        """
        Calculate Keltner Channels (Middle, Upper, Lower)
        
        Returns:
            Tuple of (middle, upper, lower) or None if insufficient data
        """
        if len(self.data_history) < self.config.keltner_period:
            return None
        
        # Calculate EMA of typical price
        typical_prices = []
        for data in list(self.data_history)[-self.config.keltner_period:]:
            typical = (data.high + data.low + data.close) / 3
            typical_prices.append(float(typical))
        
        # Simple average for middle line (can be EMA later)
        middle_value = statistics.mean(typical_prices)
        middle = Decimal(str(middle_value))
        
        # Calculate ATR
        atr = self.calculate_atr(self.config.keltner_period)
        if atr is None:
            return None
        
        # Calculate channels
        atr_multiplier = self.config.keltner_atr_multiplier
        upper = middle + (atr * atr_multiplier)
        lower = middle - (atr * atr_multiplier)
        
        return middle, upper, lower
    
    def calculate_momentum(self) -> Optional[Decimal]:
        """
        Calculate momentum oscillator
        
        Returns:
            Momentum value or None if insufficient data
        """
        if len(self.data_history) < self.config.momentum_length + 1:
            return None
        
        data_list = list(self.data_history)
        current = data_list[-1]
        
        # Linear regression of closes vs their positions
        closes = [float(d.close) for d in data_list[-self.config.momentum_length:]]
        positions = list(range(len(closes)))
        
        # Simple momentum: current close vs average close
        avg_close = statistics.mean(closes)
        momentum_raw = float(current.close) - avg_close
        
        # Normalize by ATR to make comparable across assets
        atr = self.calculate_atr(self.config.momentum_length)
        if atr and atr > 0:
            momentum_normalized = momentum_raw / float(atr)
        else:
            momentum_normalized = momentum_raw
        
        return Decimal(str(momentum_normalized))
    
    def detect_squeeze(self, bb_bands: Tuple[Decimal, Decimal, Decimal], 
                      kc_bands: Tuple[Decimal, Decimal, Decimal]) -> bool:
        """
        Detect squeeze condition (BB inside KC)
        
        Args:
            bb_bands: Bollinger Bands (middle, upper, lower)
            kc_bands: Keltner Channels (middle, upper, lower)
            
        Returns:
            True if squeeze detected
        """
        bb_middle, bb_upper, bb_lower = bb_bands
        kc_middle, kc_upper, kc_lower = kc_bands
        
        # Squeeze = BB upper < KC upper AND BB lower > KC lower
        squeeze_condition = (bb_upper < kc_upper) and (bb_lower > kc_lower)
        
        return squeeze_condition
    
    def calculate_from_data(self, data: MarketData) -> Optional[Dict[str, Any]]:
        """
        Calculate Squeeze Momentum for new data point
        
        Args:
            data: New market data
            
        Returns:
            Dictionary with squeeze analysis or None if insufficient data
        """
        self.add_data(data)
        
        # Calculate components
        bb_bands = self.calculate_bollinger_bands()
        kc_bands = self.calculate_keltner_channels()
        momentum = self.calculate_momentum()
        
        if not all([bb_bands, kc_bands, momentum]):
            return None
        
        # Detect squeeze
        self.previous_squeeze = self.current_squeeze
        self.current_squeeze = self.detect_squeeze(bb_bands, kc_bands)
        
        # Update squeeze counter
        if self.current_squeeze:
            self.squeeze_count += 1
        else:
            self.squeeze_count = 0
        
        # Detect squeeze release (breakout)
        squeeze_release = self.previous_squeeze and not self.current_squeeze
        
        # Store values for history
        bb_width = bb_bands[1] - bb_bands[2]  # Upper - Lower
        kc_width = kc_bands[1] - kc_bands[2]  # Upper - Lower
        
        self.bb_values.append(bb_width)
        self.kc_values.append(kc_width)
        self.momentum_values.append(momentum)
        
        return {
            'bollinger_bands': {
                'middle': bb_bands[0],
                'upper': bb_bands[1],
                'lower': bb_bands[2],
                'width': bb_width
            },
            'keltner_channels': {
                'middle': kc_bands[0],
                'upper': kc_bands[1],
                'lower': kc_bands[2],
                'width': kc_width
            },
            'momentum': momentum,
            'squeeze_active': self.current_squeeze,
            'squeeze_release': squeeze_release,
            'squeeze_count': self.squeeze_count,
            'squeeze_strength': bb_width / kc_width if kc_width > 0 else Decimal('1.0')
        }