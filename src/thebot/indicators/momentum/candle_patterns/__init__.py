"""
Candle Patterns Indicator - Clean Implementation
Translation from NonoBot Rust implementation
"""

from decimal import Decimal
from typing import Optional

from ...base.indicator import BaseIndicator
from ....core.types import MarketData, IndicatorResult, Signal, SignalDirection, SignalStrength
from ....core.exceptions import IndicatorError
from .config import CandlePatternsConfig
from .calculator import CandlePatternsCalculator, PatternType


class CandlePatternsIndicator(BaseIndicator):
    """Candle Patterns Indicator"""
    
    def __init__(self, config: CandlePatternsConfig = None):
        config = config or CandlePatternsConfig()
        super().__init__("CandlePatterns", config.to_dict())
        
        self.patterns_config = config
        self.calculator = CandlePatternsCalculator(config)
    
    def get_required_periods(self) -> int:
        return self.patterns_config.get_required_periods()
    
    def calculate(self, data: MarketData) -> Optional[IndicatorResult]:
        """Calculate Candle Patterns for new data point"""
        try:
            result = self.calculator.calculate_from_data(data)
            
            if result:
                pattern = result['pattern']
                strength = result['strength']
                
                # Pattern strength as main value
                pattern_value = strength if pattern != PatternType.NONE else Decimal('0.0')
                
                # Signal strength based on pattern type and strength
                if result['is_bullish_pattern']:
                    signal_strength = strength
                elif result['is_bearish_pattern']:
                    signal_strength = -strength
                else:
                    signal_strength = Decimal('0.0')
                
                return IndicatorResult(
                    value=pattern_value,
                    signal_strength=signal_strength,
                    metadata={
                        'pattern': pattern.value,
                        'pattern_strength': str(strength),
                        'is_bullish': result['is_bullish_pattern'],
                        'is_bearish': result['is_bearish_pattern'],
                        'is_neutral': result['is_neutral_pattern'],
                        'body_ratio': str(result['metrics']['body_ratio']),
                        'upper_wick_ratio': str(result['metrics']['upper_wick_ratio']),
                        'lower_wick_ratio': str(result['metrics']['lower_wick_ratio'])
                    }
                )
            
            return None
            
        except Exception as e:
            raise IndicatorError(f"Candle Patterns calculation failed: {e}")
    
    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """Generate trading signal based on Candle Patterns"""
        if not current_result or not current_result.metadata:
            return None
        
        if not self.patterns_config.enable_signals:
            return None
        
        pattern = current_result.metadata.get('pattern')
        strength = Decimal(current_result.metadata.get('pattern_strength', '0.0'))
        
        if strength < self.patterns_config.pattern_strength_threshold:
            return None
        
        # Generate signals based on pattern
        if current_result.metadata.get('is_bullish', False):
            direction = SignalDirection.BUY
            signal_strength = SignalStrength.MEDIUM if pattern in ['hammer'] else SignalStrength.WEAK
        elif current_result.metadata.get('is_bearish', False):
            direction = SignalDirection.SELL
            signal_strength = SignalStrength.MEDIUM if pattern in ['shooting_star'] else SignalStrength.WEAK
        else:
            return None
        
        return Signal(
            direction=direction,
            strength=signal_strength,
            confidence=strength,
            metadata={
                'indicator': 'CandlePatterns',
                'pattern': pattern,
                'pattern_strength': str(strength)
            }
        )