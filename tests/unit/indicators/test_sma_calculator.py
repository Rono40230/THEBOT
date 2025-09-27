"""
Test SMA Calculator Module
Ultra-focused testing for pure calculation logic
"""

import pytest
from decimal import Decimal
from datetime import datetime

from thebot.core.types import MarketData, TimeFrame
from thebot.core.exceptions import IndicatorError, InsufficientDataError
from thebot.indicators.basic.sma.config import SMAConfig
from thebot.indicators.basic.sma.calculator import SMACalculator


class TestSMACalculator:
    """Test SMA calculator in isolation"""
    
    def test_calculator_initialization(self):
        """Test calculator initialization"""
        config = SMAConfig(period=10)
        calc = SMACalculator(config)
        
        assert calc.config.period == 10
        assert calc.get_buffer_size() == 0
        assert not calc.is_ready()
        assert calc.get_current_sum() == Decimal('0')
    
    def test_add_price_insufficient_data(self):
        """Test adding prices before reaching required period"""
        config = SMAConfig(period=3)
        calc = SMACalculator(config)
        
        # Add first two prices
        result1 = calc.add_price(Decimal('10'))
        result2 = calc.add_price(Decimal('20'))
        
        assert result1 is None
        assert result2 is None
        assert not calc.is_ready()
        assert calc.get_buffer_size() == 2
    
    def test_add_price_sufficient_data(self):
        """Test SMA calculation when enough data available"""
        config = SMAConfig(period=3)
        calc = SMACalculator(config)
        
        # Add three prices
        calc.add_price(Decimal('10'))
        calc.add_price(Decimal('20'))
        result = calc.add_price(Decimal('30'))
        
        assert result is not None
        assert result == Decimal('20')  # (10+20+30)/3
        assert calc.is_ready()
        assert calc.get_buffer_size() == 3
    
    def test_rolling_calculation(self):
        """Test rolling SMA calculation"""
        config = SMAConfig(period=3)
        calc = SMACalculator(config)
        
        # Add initial data
        calc.add_price(Decimal('10'))
        calc.add_price(Decimal('20'))
        result1 = calc.add_price(Decimal('30'))  # SMA = 20
        
        # Add fourth price (should remove first)
        result2 = calc.add_price(Decimal('40'))  # SMA = (20+30+40)/3 = 30
        
        assert result1 == Decimal('20')
        assert result2 == Decimal('30')
        assert calc.get_buffer_size() == 3  # Buffer size stays at period
    
    def test_invalid_price(self):
        """Test handling of invalid prices"""
        config = SMAConfig(period=3)
        calc = SMACalculator(config)
        
        with pytest.raises(IndicatorError):
            calc.add_price(Decimal('-10'))  # Negative price
        
        with pytest.raises(IndicatorError):
            calc.add_price(None)  # None price
    
    def test_batch_calculation(self):
        """Test batch SMA calculation"""
        prices = [10, 20, 30, 40, 50]
        period = 3
        
        results = SMACalculator.calculate_batch(prices, period)
        
        expected = [
            (10 + 20 + 30) / 3,  # 20
            (20 + 30 + 40) / 3,  # 30  
            (30 + 40 + 50) / 3   # 40
        ]
        
        assert len(results) == 3
        assert results == expected
    
    def test_batch_insufficient_data(self):
        """Test batch calculation with insufficient data"""
        prices = [10, 20]  # Only 2 prices
        period = 3
        
        with pytest.raises(InsufficientDataError):
            SMACalculator.calculate_batch(prices, period)
    
    def test_reset(self):
        """Test calculator reset"""
        config = SMAConfig(period=2)
        calc = SMACalculator(config)
        
        # Add data
        calc.add_price(Decimal('10'))
        calc.add_price(Decimal('20'))
        
        assert calc.is_ready()
        assert calc.get_buffer_size() == 2
        
        # Reset
        calc.reset()
        
        assert not calc.is_ready()
        assert calc.get_buffer_size() == 0
        assert calc.get_current_sum() == Decimal('0')
    
    def test_market_data_integration(self):
        """Test integration with MarketData"""
        config = SMAConfig(period=2)
        calc = SMACalculator(config)
        
        # Create sample market data
        data1 = MarketData(
            timestamp=datetime.now(),
            open=Decimal('10'),
            high=Decimal('15'),
            low=Decimal('8'),
            close=Decimal('12'),
            volume=Decimal('1000'),
            timeframe=TimeFrame.M1,
            symbol="BTCUSDT"
        )
        
        data2 = MarketData(
            timestamp=datetime.now(),
            open=Decimal('12'),
            high=Decimal('18'),
            low=Decimal('11'),
            close=Decimal('16'),
            volume=Decimal('1200'),
            timeframe=TimeFrame.M1,
            symbol="BTCUSDT"
        )
        
        # Calculate SMA
        result1 = calc.calculate_from_data(data1)
        result2 = calc.calculate_from_data(data2)
        
        assert result1 is None  # Not enough data
        assert result2 == Decimal('14')  # (12+16)/2