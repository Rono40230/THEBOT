"""
Breakout Detector Calculator
Translation from NonoBot Rust implementation
"""

from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple
from collections import deque
import statistics

from ....core.types import MarketData
from .config import BreakoutConfig


class BreakoutCalculator:
    """
    Breakout detection engine
    
    NonoBot logic:
    - Track support/resistance levels
    - Monitor volume patterns
    - Detect breakout conditions
    """
    
    def __init__(self, config: BreakoutConfig):
        self.config = config
        self.data_history: deque = deque(maxlen=config.lookback_period + 10)
        self.volume_history: deque = deque(maxlen=config.lookback_period)
        
        # State tracking
        self.current_support = None
        self.current_resistance = None
        self.avg_volume = None
    
    def add_data(self, data: MarketData) -> None:
        self.data_history.append(data)
        self.volume_history.append(float(data.volume))
        
        # Update average volume
        if len(self.volume_history) >= 10:
            self.avg_volume = Decimal(str(statistics.mean(list(self.volume_history)[-10:])))
    
    def find_support_resistance(self) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Find current support and resistance levels"""
        if len(self.data_history) < self.config.lookback_period:
            return None, None
        
        data_list = list(self.data_history)[-self.config.lookback_period:]
        
        # Simple approach: highest high and lowest low
        highs = [float(d.high) for d in data_list]
        lows = [float(d.low) for d in data_list]
        
        resistance = Decimal(str(max(highs)))
        support = Decimal(str(min(lows)))
        
        return support, resistance
    
    def detect_breakout(self, current_data: MarketData) -> Dict[str, Any]:
        """Detect breakout conditions"""
        support, resistance = self.find_support_resistance()
        
        if not all([support, resistance]):
            return {
                'breakout_detected': False,
                'breakout_type': None,
                'breakout_strength': Decimal('0.0')
            }
        
        current_price = current_data.close
        current_volume = current_data.volume
        
        # Check for resistance breakout
        resistance_breakout = False
        support_breakout = False
        
        if current_price > resistance * (Decimal('1.0') + self.config.breakout_threshold):
            resistance_breakout = True
        elif current_price < support * (Decimal('1.0') - self.config.breakout_threshold):
            support_breakout = True
        
        # Volume confirmation
        volume_confirmed = False
        if self.avg_volume and current_volume > self.avg_volume * self.config.volume_multiplier:
            volume_confirmed = True
        
        # Calculate breakout strength
        breakout_strength = Decimal('0.0')
        breakout_type = None
        
        if resistance_breakout:
            breakout_type = 'resistance'
            strength_ratio = (current_price - resistance) / resistance
            breakout_strength = strength_ratio * (Decimal('2.0') if volume_confirmed else Decimal('1.0'))
        elif support_breakout:
            breakout_type = 'support'
            strength_ratio = (support - current_price) / support
            breakout_strength = strength_ratio * (Decimal('2.0') if volume_confirmed else Decimal('1.0'))
        
        return {
            'breakout_detected': resistance_breakout or support_breakout,
            'breakout_type': breakout_type,
            'breakout_strength': breakout_strength,
            'volume_confirmed': volume_confirmed,
            'resistance_level': resistance,
            'support_level': support,
            'current_price': current_price
        }
    
    def calculate_from_data(self, data: MarketData) -> Optional[Dict[str, Any]]:
        """Calculate breakout analysis for new data point"""
        self.add_data(data)
        
        if len(self.data_history) < self.config.lookback_period:
            return None
        
        breakout_analysis = self.detect_breakout(data)
        
        # Update internal state
        self.current_support = breakout_analysis.get('support_level')
        self.current_resistance = breakout_analysis.get('resistance_level')
        
        return breakout_analysis