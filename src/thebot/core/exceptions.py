"""
Custom exceptions for THEBOT platform
Modular exception hierarchy for precise error handling
"""

from typing import Optional, Dict, Any


class TheBotError(Exception):
    """Base exception for all THEBOT errors"""

    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.details = details or {}


class DataError(TheBotError):
    """Data-related errors"""

    pass


class ValidationError(DataError):
    """Data validation errors"""

    pass


class ConfigError(TheBotError):
    """Configuration errors"""

    pass


class ConfigurationError(ConfigError):
    """Alias for ConfigError - backward compatibility"""

    pass


class APIError(TheBotError):
    """API-related errors"""

    def __init__(self, message: str, status_code: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code


class RateLimitError(APIError):
    """Rate limiting errors"""

    pass


class IndicatorError(TheBotError):
    """Indicator calculation errors"""

    pass


class InsufficientDataError(IndicatorError):
    """Not enough data for calculation"""

    pass


class BacktestError(TheBotError):
    """Backtesting errors"""

    pass


class StrategyError(TheBotError):
    """Strategy execution errors"""

    pass


class DatabaseError(TheBotError):
    """Database operation errors"""

    pass


class AIError(TheBotError):
    """AI/ML related errors"""

    pass


class ModelError(AIError):
    """ML model errors"""

    pass
