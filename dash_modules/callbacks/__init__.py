"""
Callbacks Module - Architecture centralisée pour tous les callbacks Dash
Consolide les 29 callbacks éparpillés dans une structure maintenable
"""

from .base.callback_manager import CallbackManager
from .base.callback_registry import CallbackRegistry
from .managers.news_callbacks import NewsCallbacks
from .managers.alerts_callbacks import AlertsCallbacks
from .managers.modal_callbacks import ModalCallbacks
from .managers.market_callbacks import MarketCallbacks
from .managers.trading_callbacks import TradingCallbacks
from .utils.callback_factory import CallbackFactory
from .utils.callback_validator import CallbackValidator

__all__ = [
    'CallbackManager',
    'CallbackRegistry',
    'NewsCallbacks',
    'AlertsCallbacks',
    'ModalCallbacks',
    'MarketCallbacks',
    'TradingCallbacks',
    'CallbackFactory',
    'CallbackValidator'
]