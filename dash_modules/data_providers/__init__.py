"""
Data Providers Package - THEBOT
Package pour les fournisseurs de données réelles (APIs externes) + RSS
"""

from .binance_api import binance_provider
from .coin_gecko_api import coin_gecko_api
from .real_data_manager import real_data_manager
from .rss_news_manager import rss_news_manager

# RSS Infrastructure (Phase 1)
from .rss_sources_config import rss_sources_config
from .twelve_data_api import twelve_data_api
from .yahoo_finance_api import yahoo_finance_api

__all__ = [
    "binance_provider",
    "coin_gecko_api",
    "yahoo_finance_api",
    "twelve_data_api",
    "real_data_manager",
    "rss_sources_config",
    "rss_news_manager",
]
