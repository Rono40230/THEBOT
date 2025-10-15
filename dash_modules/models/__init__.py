"""
Modèles de données THEBOT - Architecture de base de données unifiée
"""

from .base import Base
from .market_data import MarketData, PriceHistory
from .alerts import Alert, PriceAlert
from .news import NewsArticle
from .user import User, UserPreferences

__all__ = [
    'Base',
    'MarketData', 'PriceHistory',
    'Alert', 'PriceAlert',
    'NewsArticle',
    'User', 'UserPreferences'
]
