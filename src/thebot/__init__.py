from .core.logger import logger
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

import logging

logger = logging.getLogger(__name__)

from .base.indicator import BaseIndicator
from .core.exceptions import ConfigurationError, IndicatorError

# Export API principale
from .core.types import (
    IndicatorResult,
    MarketData,
    Signal,
    SignalDirection,
    SignalStrength,
)

# Export indicateurs disponibles
try:
    from .indicators.basic.ema import EMAConfig, EMAIndicator
    from .indicators.basic.sma import SMAConfig, SMAIndicator
    from .indicators.momentum.macd import MACD as MACDIndicator
    from .indicators.momentum.macd import MACDConfig
    from .indicators.oscillators.rsi import RSIConfig, RSIIndicator
    from .indicators.trend.supertrend import SuperTrendConfig, SuperTrendIndicator
    from .indicators.volatility.atr import ATRConfig, ATRIndicator
    from .indicators.volume.obv import OBVConfig, OBVIndicator

    INDICATORS_LOADED = True
except ImportError as e:
    logger.warning(f"Some indicators not loaded: {e}")
    INDICATORS_LOADED = False

# Indicators disponibles
AVAILABLE_INDICATORS = [
    "SMA",
    "EMA",
    "RSI",
    "ATR",
    "OBV",
    "SuperTrend",
    "MACD",
    "SqueezeIndicator",
    "BreakoutDetector",
    "CandlePatternsIndicator",
    "VolumeProfileIndicator",
    "SupportResistanceIndicator",
    "FibonacciIndicator",
    "PivotPointsIndicator",
    "OrderBlocksIndicator",
    "FairValueGapsIndicator",
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
    "INDICATORS_LOADED",
]

if INDICATORS_LOADED:
    __all__.extend(
        [
            # Basic Indicators
            "SMAIndicator",
            "SMAConfig",
            "EMAIndicator",
            "EMAConfig",
            "RSIIndicator",
            "RSIConfig",
            "ATRIndicator",
            "ATRConfig",
            # Advanced Indicators
            "OBVIndicator",
            "OBVConfig",
            "SuperTrendIndicator",
            "SuperTrendConfig",
            "MACDIndicator",
            "MACDConfig",
        ]
    )
