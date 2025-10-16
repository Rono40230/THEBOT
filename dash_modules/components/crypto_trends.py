from src.thebot.core.logger import logger
"""
Component Crypto Trends - Phase 4 THEBOT
Indicateurs de tendance crypto via Binance API
Architecture modulaire avec widgets Dash
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import dash
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from dash_modules.core.price_formatter import (
    format_crypto_price_adaptive,
    format_percentage_change,
)

# Import des providers THEBOT
from ..data_providers.binance_api import binance_provider
from ..data_providers.coin_gecko_api import coin_gecko_api

logger = logging.getLogger(__name__)


class CryptoTrendsComponent:
    """Composant d'analyse des tendances crypto"""

    def __init__(self):
        self.cache_duration = 60  # 1 minute
        self.last_update = {}
        self.cache = {}

    def get_trending_coins(self, limit: int = 10) -> List[Dict]:
        """Récupère les cryptos en tendance via volume et momentum"""
        try:
            cache_key = f"trending_coins_{limit}"
            now = datetime.now()

            # Vérifier cache
            if (
                cache_key in self.last_update
                and (now - self.last_update[cache_key]).seconds < self.cache_duration
            ):
                return self.cache.get(cache_key, [])

            # Données 24h de Binance
            tickers_24h = binance_provider.get_24hr_ticker()
            if not tickers_24h:
                return []

            # Filtrer USDT pairs avec volume significatif
            usdt_pairs = [
                ticker
                for ticker in tickers_24h
                if (
                    ticker["symbol"].endswith("USDT")
                    and ticker["quoteVolume"] > 1000000  # >1M USDT volume
                    and ticker["price"] > 0
                )
            ]

            # Calculer score de tendance (volume * |change%|)
            for ticker in usdt_pairs:
                volume_score = np.log10(ticker["quoteVolume"]) / 10  # Normaliser
                change_score = abs(ticker["priceChangePercent"]) / 100
                ticker["trend_score"] = volume_score * change_score

            # Trier par score de tendance
            trending = sorted(usdt_pairs, key=lambda x: x["trend_score"], reverse=True)[
                :limit
            ]

            # Enrichir avec données CoinGecko si possible
            result = []
            for ticker in trending:
                coin_data = {
                    "symbol": ticker["symbol"],
                    "price": ticker["price"],
                    "change_24h": ticker["priceChangePercent"],
                    "volume_24h": ticker["quoteVolume"],
                    "high_24h": ticker["high"],
                    "low_24h": ticker["low"],
                    "trend_score": ticker["trend_score"],
                    "momentum": self._calculate_momentum(ticker),
                }
                result.append(coin_data)

            # Mettre en cache
            self.cache[cache_key] = result
            self.last_update[cache_key] = now

            logger.info(f"✅ {len(result)} cryptos trending récupérées")
            return result

        except Exception as e:
            logger.error(f"❌ Erreur récupération trending coins: {e}")
            return []

    def get_volume_analysis(self) -> Dict:
        """Analyse du volume global crypto"""
        try:
            cache_key = "volume_analysis"
            now = datetime.now()

            if (
                cache_key in self.last_update
                and (now - self.last_update[cache_key]).seconds < self.cache_duration
            ):
                return self.cache.get(cache_key, {})

            # Récupérer résumé marché Binance
            market_summary = binance_provider.get_market_summary()
            if not market_summary:
                return {}

            # Données globales CoinGecko
            try:
                global_data = coin_gecko_api.get_global_data()
            except:
                global_data = {}

            analysis = {
                "total_volume_24h": market_summary.get("total_volume_usdt", 0),
                "active_pairs": market_summary.get("total_pairs", 0),
                "gainers_count": market_summary.get("gainers_count", 0),
                "losers_count": market_summary.get("losers_count", 0),
                "market_sentiment": self._calculate_sentiment(market_summary),
                "volume_trend": self._analyze_volume_trend(market_summary),
                "top_volume_pairs": market_summary.get("top_volume_pairs", [])[:5],
            }

            # Ajouter données CoinGecko si disponibles
            if global_data:
                analysis["total_market_cap"] = global_data.get(
                    "total_market_cap", {}
                ).get("usd", 0)
                analysis["btc_dominance"] = global_data.get(
                    "market_cap_percentage", {}
                ).get("btc", 0)
                analysis["24h_volume_change"] = global_data.get(
                    "market_cap_change_percentage_24h_usd", 0
                )

            self.cache[cache_key] = analysis
            self.last_update[cache_key] = now

            return analysis

        except Exception as e:
            logger.error(f"❌ Erreur analyse volume: {e}")
            return {}

    def get_price_changes(self, timeframes: List[str] = ["1h", "24h"]) -> Dict:
        """Analyse des changements de prix multi-timeframes"""
        try:
            cache_key = f"price_changes_{'_'.join(timeframes)}"
            now = datetime.now()

            if (
                cache_key in self.last_update
                and (now - self.last_update[cache_key]).seconds < self.cache_duration
            ):
                return self.cache.get(cache_key, {})

            # Pour l'instant, seulement 24h via Binance
            tickers_24h = binance_provider.get_24hr_ticker()
            if not tickers_24h:
                return {}

            # Filtrer et analyser USDT pairs
            usdt_pairs = [
                ticker
                for ticker in tickers_24h
                if ticker["symbol"].endswith("USDT") and ticker["quoteVolume"] > 500000
            ]

            changes_analysis = {
                "timeframes": ["24h"],  # Extension future pour 1h, 7d, etc.
                "total_pairs": len(usdt_pairs),
                "by_range": self._categorize_changes(usdt_pairs),
                "extremes": {
                    "biggest_gainer": max(
                        usdt_pairs, key=lambda x: x["priceChangePercent"], default={}
                    ),
                    "biggest_loser": min(
                        usdt_pairs, key=lambda x: x["priceChangePercent"], default={}
                    ),
                    "highest_volume": max(
                        usdt_pairs, key=lambda x: x["quoteVolume"], default={}
                    ),
                },
                "distribution": self._change_distribution(usdt_pairs),
            }

            self.cache[cache_key] = changes_analysis
            self.last_update[cache_key] = now

            return changes_analysis

        except Exception as e:
            logger.error(f"❌ Erreur analyse changements prix: {e}")
            return {}

    def create_trends_widget(self, widget_id: str = "crypto-trends") -> html.Div:
        """Crée le widget de tendances crypto"""
        return html.Div(
            [
                html.H3("🪙 Crypto Trends", className="widget-title"),
                # Contrôles
                html.Div(
                    [
                        html.Label("Nombre de cryptos:", className="control-label"),
                        dcc.Dropdown(
                            id=f"{widget_id}-limit",
                            options=[
                                {"label": "5", "value": 5},
                                {"label": "10", "value": 10},
                                {"label": "15", "value": 15},
                                {"label": "20", "value": 20},
                            ],
                            value=10,
                            className="control-dropdown",
                        ),
                    ],
                    className="widget-controls",
                ),
                # Graphiques
                html.Div(
                    [
                        dcc.Graph(id=f"{widget_id}-chart"),
                        dcc.Graph(id=f"{widget_id}-volume-chart"),
                    ],
                    className="widget-charts",
                ),
                # Tableaux de données
                html.Div(id=f"{widget_id}-table", className="widget-table"),
                # Indicateurs
                html.Div(id=f"{widget_id}-indicators", className="widget-indicators"),
                # Auto-refresh
                dcc.Interval(
                    id=f"{widget_id}-interval",
                    interval=60 * 1000,  # 1 minute
                    n_intervals=0,
                ),
            ],
            className="crypto-trends-widget dashboard-widget",
        )

    def _calculate_momentum(self, ticker: Dict) -> str:
        """Calcule le momentum basé sur price change et volume"""
        change = ticker["priceChangePercent"]
        volume = ticker["quoteVolume"]

        if change > 5 and volume > 10000000:
            return "🚀 Strong Bull"
        elif change > 2 and volume > 5000000:
            return "📈 Bull"
        elif change < -5 and volume > 10000000:
            return "📉 Strong Bear"
        elif change < -2 and volume > 5000000:
            return "🔻 Bear"
        else:
            return "➡️ Neutral"

    def _calculate_sentiment(self, market_summary: Dict) -> str:
        """Calcule le sentiment général du marché"""
        gainers = market_summary.get("gainers_count", 0)
        losers = market_summary.get("losers_count", 0)
        total = gainers + losers

        if total == 0:
            return "❓ Unknown"

        ratio = gainers / total
        if ratio > 0.65:
            return "😊 Very Bullish"
        elif ratio > 0.55:
            return "📈 Bullish"
        elif ratio < 0.35:
            return "😰 Very Bearish"
        elif ratio < 0.45:
            return "📉 Bearish"
        else:
            return "😐 Neutral"

    def _analyze_volume_trend(self, market_summary: Dict) -> str:
        """Analyse la tendance du volume"""
        # Approximation basée sur le volume actuel
        volume = market_summary.get("total_volume_usdt", 0)

        if volume > 50000000000:  # 50B USDT
            return "🔥 Very High"
        elif volume > 20000000000:  # 20B USDT
            return "📈 High"
        elif volume > 10000000000:  # 10B USDT
            return "➡️ Normal"
        else:
            return "📉 Low"

    def _categorize_changes(self, tickers: List[Dict]) -> Dict:
        """Catégorise les changements de prix"""
        ranges = {
            "extreme_pump": 0,  # >20%
            "strong_pump": 0,  # 10-20%
            "pump": 0,  # 5-10%
            "slight_up": 0,  # 0-5%
            "slight_down": 0,  # 0 to -5%
            "dump": 0,  # -5 to -10%
            "strong_dump": 0,  # -10 to -20%
            "extreme_dump": 0,  # <-20%
        }

        for ticker in tickers:
            change = ticker["priceChangePercent"]
            if change > 20:
                ranges["extreme_pump"] += 1
            elif change > 10:
                ranges["strong_pump"] += 1
            elif change > 5:
                ranges["pump"] += 1
            elif change > 0:
                ranges["slight_up"] += 1
            elif change > -5:
                ranges["slight_down"] += 1
            elif change > -10:
                ranges["dump"] += 1
            elif change > -20:
                ranges["strong_dump"] += 1
            else:
                ranges["extreme_dump"] += 1

        return ranges

    def _change_distribution(self, tickers: List[Dict]) -> Dict:
        """Calcule la distribution des changements"""
        changes = [ticker["priceChangePercent"] for ticker in tickers]

        return {
            "mean": np.mean(changes),
            "median": np.median(changes),
            "std": np.std(changes),
            "min": min(changes),
            "max": max(changes),
            "positive_count": len([c for c in changes if c > 0]),
            "negative_count": len([c for c in changes if c < 0]),
        }


# Instance globale
crypto_trends = CryptoTrendsComponent()


# Callbacks pour le widget - MIGRÉS vers MarketCallbacks manager
# Le callback update_crypto_trends a été déplacé dans dash_modules/callbacks/managers/market_callbacks.py
