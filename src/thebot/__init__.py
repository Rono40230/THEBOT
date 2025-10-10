"""
THEBOT - Trading Bot Indicators Package
Indicateurs techniques ultra-modulaires traduits depuis NonoBot Rust

Version: 2.0.0
Architecture: Factory Pattern + Modular Design
Translation source: https://github.com/Rono40230/NonoBot
"""

__version__ = "2.0.0"
__author__ = "THEBOT Team"

__author__ = "THEBOT Team"

# Export API principale
from .core.types import MarketData, Signal, IndicatorResult, SignalDirection, SignalStrength
from .core.exceptions import IndicatorError, ConfigurationError
from .base.indicator import BaseIndicator

# Export indicateurs disponibles
try:
    from .indicators.basic.sma import SMAIndicator, SMAConfig
    from .indicators.basic.ema import EMAIndicator, EMAConfig  
    from .indicators.oscillators.rsi import RSIIndicator, RSIConfig
    from .indicators.volatility.atr import ATRIndicator, ATRConfig
    from .indicators.volume.obv import OBVIndicator, OBVConfig
    from .indicators.trend.supertrend import SuperTrendIndicator, SuperTrendConfig
    from .indicators.momentum.macd import MACD as MACDIndicator, MACDConfig
    INDICATORS_LOADED = True
except ImportError as e:
    print(f"⚠️ Some indicators not loaded: {e}")
    INDICATORS_LOADED = False

# Indicators disponibles
AVAILABLE_INDICATORS = [
    'SMA', 'EMA', 'RSI', 'ATR', 'OBV', 'SuperTrend', 'MACD',
    'SqueezeIndicator', 'BreakoutDetector', 'CandlePatternsIndicator', 
    'VolumeProfileIndicator', 'SupportResistanceIndicator',
    'FibonacciIndicator', 'PivotPointsIndicator',
    'OrderBlocksIndicator', 'FairValueGapsIndicator'
]

# Public API
__all__ = [
    # Version info
    "__version__",
    "__author__",
    
    # Core types
    "MarketData",
    "Signal", 
    "IndicatorResult",
    "SignalDirection",
    "SignalStrength",
    
    # Exceptions
    "IndicatorError",
    "ConfigurationError",
    
    # Base
    "BaseIndicator",
    
    # Constants
    "AVAILABLE_INDICATORS",
    "INDICATORS_LOADED"
]

if INDICATORS_LOADED:
    __all__.extend([
        # Basic Indicators
        "SMAIndicator", "SMAConfig",
        "EMAIndicator", "EMAConfig",
        "RSIIndicator", "RSIConfig", 
        "ATRIndicator", "ATRConfig",
        
        # Advanced Indicators
        "OBVIndicator", "OBVConfig",
        "SuperTrendIndicator", "SuperTrendConfig",
        "MACDIndicator", "MACDConfig",
    ])