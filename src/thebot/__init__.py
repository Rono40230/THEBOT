"""
THEBOT - Trading Analysis Platform

Ultra-modular architecture for crypto and forex analysis
with AI integration and professional backtesting.
"""

__version__ = "1.0.0"
__author__ = "Rono40230"
__description__ = "Advanced Trading Analysis Platform"

# Core imports
from .core.types import MarketData, Signal, IndicatorResult
from .core.exceptions import TheBotError, DataError, ConfigError

# Public API
__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__description__",
    
    # Core types
    "MarketData",
    "Signal", 
    "IndicatorResult",
    
    # Exceptions
    "TheBotError",
    "DataError",
    "ConfigError",
]