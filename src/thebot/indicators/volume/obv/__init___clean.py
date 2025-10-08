"""
OBV Indicator - Simple and Clean Implementation
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
        # Pas de signal pour l'instant - juste validation
        return None