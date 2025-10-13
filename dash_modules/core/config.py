"""
Configuration Module - THEBOT Dash
Gestion centralisée de la configuration de l'application
"""

from dataclasses import dataclass
from typing import Any, Dict, List

import dash_bootstrap_components as dbc


@dataclass
class DashConfig:
    """Configuration globale de l'application Dash"""

    # Configuration serveur
    host: str = "0.0.0.0"
    port: int = 8050
    debug: bool = True

    # Configuration thème
    theme = dbc.themes.CYBORG
    title: str = "🤖 THEBOT - Trading Intelligence Platform"

    # Configuration indicateurs par défaut
    default_periods: Dict[str, int] = None

    # Symboles par défaut pour l'analyse
    default_symbols: List[str] = None

    # Marchés supportés
    supported_markets: Dict[str, Dict] = None

    def __post_init__(self):
        if self.default_periods is None:
            self.default_periods = {"sma": 20, "ema": 12, "rsi": 14, "atr": 14}

        if self.default_symbols is None:
            self.default_symbols = ["AAPL", "GOOGL", "MSFT", "BTC-USD", "ETH-USD"]

        if self.supported_markets is None:
            self.supported_markets = {
                # Actions US (données réelles via API)
                "AAPL": {
                    "label": "🍎 AAPL - Apple Inc.",
                    "type": "stock",
                    "exchange": "NASDAQ",
                },
                "GOOGL": {
                    "label": "🔍 GOOGL - Alphabet Inc.",
                    "type": "stock",
                    "exchange": "NASDAQ",
                },
                "MSFT": {
                    "label": "🖥️ MSFT - Microsoft Corp.",
                    "type": "stock",
                    "exchange": "NASDAQ",
                },
                "TSLA": {
                    "label": "🚗 TSLA - Tesla Inc.",
                    "type": "stock",
                    "exchange": "NASDAQ",
                },
                "NVDA": {
                    "label": "💻 NVDA - NVIDIA Corp.",
                    "type": "stock",
                    "exchange": "NASDAQ",
                },
                # Crypto (données réelles via API)
                "BTC-USD": {
                    "label": "₿ Bitcoin",
                    "type": "crypto",
                    "exchange": "CRYPTO",
                },
                "ETH-USD": {
                    "label": "⟠ Ethereum",
                    "type": "crypto",
                    "exchange": "CRYPTO",
                },
                # Forex (données réelles via API)
                "EURUSD": {"label": "🇪🇺 EUR/USD", "type": "forex", "exchange": "FX"},
                "GBPUSD": {"label": "🇬🇧 GBP/USD", "type": "forex", "exchange": "FX"},
            }


@dataclass
class UIConfig:
    """Configuration de l'interface utilisateur"""

    # Hauteurs des composants
    main_chart_height: int = 500
    indicator_chart_height: int = 200

    # Couleurs des graphiques
    colors: Dict[str, str] = None

    # Options des dropdowns
    timeframes: List[Dict] = None
    analysis_types: List[Dict] = None

    def __post_init__(self):
        if self.colors is None:
            self.colors = {
                "bullish": "#00ff88",
                "bearish": "#ff4444",
                "sma": "orange",
                "ema": "cyan",
                "rsi": "purple",
                "atr": "darkorange",
                "volume": "rgba(100, 149, 237, 0.6)",
            }

        if self.timeframes is None:
            self.timeframes = [
                {"label": "🔥 1m - Scalping", "value": "1m"},
                {"label": "⚡ 5m - Quick Trades", "value": "5m"},
                {"label": "📊 15m - Short Term", "value": "15m"},
                {"label": "📈 1h - Day Trading", "value": "1h"},
                {"label": "📅 4h - Swing", "value": "4h"},
                {"label": "🏛️ 1D - Position", "value": "1d"},
            ]

        if self.analysis_types is None:
            self.analysis_types = [
                {"label": "🔧 Technical Only", "value": "technical"},
                {"label": "🧠 AI Enhanced", "value": "ai"},
                {"label": "📅 Economic Impact", "value": "economic"},
                {"label": "🎯 Full Spectrum", "value": "full"},
            ]


# Instances globales
dash_config = DashConfig()
ui_config = UIConfig()
