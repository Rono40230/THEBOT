from src.thebot.core.logger import logger
"""
Module Binance API - GRATUIT et ILLIMITÉ
Données de marché crypto en temps réel
Architecture modulaire THEBOT
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import requests

from .provider_interfaces import DataProviderInterface
from src.thebot.core.cache import get_global_cache

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BinanceProvider(DataProviderInterface):
    """Fournisseur de données Binance - GRATUIT et ILLIMITÉ - Implémente DataProviderInterface"""

    @property
    def name(self) -> str:
        return "binance"

    @property
    def supported_markets(self) -> List[str]:
        return self.popular_symbols

    @property
    def rate_limit_info(self) -> Dict[str, Any]:
        return {
            "requests_per_minute": 1200,
            "requests_per_second": 20,
            "has_free_tier": True,
            "free_tier_limits": "Illimité pour les données de marché de base"
        }

    def validate_symbol(self, symbol: str) -> bool:
        """Valide si un symbole est supporté par Binance"""
        if not isinstance(symbol, str) or not symbol.strip():
            return False
        return symbol.upper().strip() in [s.upper() for s in self.supported_markets]

    def get_price_data(self, symbol: str, interval: str = "1d", limit: int = 100) -> Optional[Dict[str, Any]]:
        """Récupère les données de prix historiques - Implémentation DataProviderInterface"""
        df = self.get_klines(symbol, interval, limit)
        if df is None:
            return None

        return {
            "symbol": symbol,
            "interval": interval,
            "data": df.to_dict('records'),
            "count": len(df),
            "provider": self.name,
            "timestamp": datetime.now()
        }

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Récupère le prix actuel - Implémentation DataProviderInterface"""
        ticker_data = self.get_24hr_ticker(symbol)
        if ticker_data and "lastPrice" in ticker_data:
            return float(ticker_data["lastPrice"])
        return None

    def get_market_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations sur le marché - Implémentation DataProviderInterface"""
        return self.get_24hr_ticker(symbol)

    def is_available(self) -> bool:
        """Vérifie si Binance est disponible - Implémentation DataProviderInterface"""
        try:
            # Test avec un symbole populaire
            return self.get_current_price("BTCUSDT") is not None
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du provider - Implémentation DataProviderInterface"""
        return {
            "name": self.name,
            "available": self.is_available(),
            "supported_markets_count": len(self.supported_markets),
            "rate_limit_info": self.rate_limit_info,
            "last_request_time": datetime.fromtimestamp(self.last_request_time) if self.last_request_time > 0 else None
        }

    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.cache = get_global_cache()  # Utiliser le cache intelligent global
        self.last_request_time = 0
        self.request_delay = 0.1  # Binance permet 1200 req/min = 20 req/sec

        # Symboles populaires Binance
        self.popular_symbols = [
            "BTCUSDT",
            "ETHUSDT",
            "BNBUSDT",
            "ADAUSDT",
            "SOLUSDT",
            "DOTUSDT",
            "LINKUSDT",
            "LTCUSDT",
            "AVAXUSDT",
            "MATICUSDT",
            "ATOMUSDT",
            "XRPUSDT",
        ]

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Any]:
        """Effectue une requête HTTP vers l'API Binance avec gestion d'erreurs et cache"""
        try:
            # Vérifier le cache d'abord
            cache_key = f"binance_{endpoint}"
            cached_result = self.cache.get(cache_key, endpoint=endpoint, params=params or {})
            if cached_result is not None:
                logger.debug(f"📋 Cache hit pour {endpoint}")
                return cached_result

            # Respecter le rate limit
            current_time = time.time()
            if current_time - self.last_request_time < self.request_delay:
                time.sleep(self.request_delay - (current_time - self.last_request_time))

            url = f"{self.base_url}/{endpoint}"
            logger.debug(f"🌐 Requête Binance: {url}")

            response = requests.get(url, params=params, timeout=10)
            self.last_request_time = time.time()

            if response.status_code == 200:
                result = response.json()
                # Mettre en cache le résultat
                self.cache.set(cache_key, result, endpoint=endpoint, params=params or {})
                return result
            else:
                logger.error(
                    f"Erreur HTTP Binance: {response.status_code} - {response.text}"
                )
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur requête Binance: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur inattendue Binance: {e}")
            return None

    def get_ticker_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Récupérer prix actuel d'un symbole"""
        # Validation du symbole
        if not isinstance(symbol, str) or not symbol.strip():
            logger.error(f"❌ Symbole invalide: {symbol}")
            return None

        symbol = symbol.upper().strip()
        cache_key = f"{symbol}_price"

        # Cache très court (5 secondes) pour prix en temps réel
        cached_data = self.cache.get("crypto_prices", symbol=symbol)
        if cached_data is not None:
            return cached_data

        endpoint = "ticker/price"
        params = {"symbol": symbol}

        response = self._make_request(endpoint, params)
        if response:
            price_data = {
                "symbol": response["symbol"],
                "price": float(response["price"]),
                "timestamp": datetime.now(),
            }
            self.cache.set("crypto_prices", price_data, symbol=symbol)
            return price_data

        return None

    def get_ticker_24hr(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Récupérer statistiques 24h d'un symbole"""
        # Validation du symbole
        if not isinstance(symbol, str) or not symbol.strip():
            logger.error(f"❌ Symbole invalide: {symbol}")
            return None

        symbol = symbol.upper().strip()
        cache_key = f"{symbol}_24hr"

        # Cache 30 secondes pour stats 24h
        cached_data = self.cache.get("crypto_ohlcv", symbol=symbol, timeframe="24h")
        if cached_data is not None:
            return cached_data

        endpoint = "ticker/24hr"
        params = {"symbol": symbol}

        response = self._make_request(endpoint, params)
        if response:
            # Format compatible avec les callbacks (clés comme l'API Binance originale)
            ticker_data = {
                "symbol": response["symbol"],
                "priceChange": response["priceChange"],
                "priceChangePercent": response["priceChangePercent"],
                "weightedAvgPrice": response["weightedAvgPrice"],
                "prevClosePrice": response["prevClosePrice"],
                "lastPrice": response["lastPrice"],  # Clé compatible
                "bidPrice": response["bidPrice"],
                "askPrice": response["askPrice"],
                "openPrice": response["openPrice"],
                "highPrice": response["highPrice"],
                "lowPrice": response["lowPrice"],
                "volume": response["volume"],
                "quoteVolume": response["quoteVolume"],
                "count": response["count"],
                "timestamp": datetime.now(),
            }
            self.cache.set("crypto_ohlcv", ticker_data, symbol=symbol, timeframe="24h")
            return ticker_data

        return None

    def get_klines(
        self, symbol: str, interval: str = "1h", limit: int = 100
    ) -> Optional[pd.DataFrame]:
        """Récupérer données OHLCV (candlesticks)"""
        cache_key = f"{symbol}_{interval}_{limit}_klines"

        # Cache selon l'intervalle
        cache_duration = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "30m": 1800,
            "1h": 3600,
            "4h": 14400,
            "1d": 86400,
        }.get(interval, 3600)

        cached_data = self.cache.get("exchange_info")
        if cached_data is not None:
                return cached_data

        endpoint = "klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}

        response = self._make_request(endpoint, params)
        if not response:
            return None

        try:
            # Convertir réponse Binance en DataFrame
            df_data = []
            for kline in response:
                df_data.append(
                    {
                        "timestamp": pd.to_datetime(int(kline[0]), unit="ms"),
                        "open": float(kline[1]),
                        "high": float(kline[2]),
                        "low": float(kline[3]),
                        "close": float(kline[4]),
                        "volume": float(kline[5]),
                        "close_time": pd.to_datetime(int(kline[6]), unit="ms"),
                        "quote_asset_volume": float(kline[7]),
                        "number_of_trades": int(kline[8]),
                    }
                )

            df = pd.DataFrame(df_data)
            df.set_index("timestamp", inplace=True)

            self.cache.set("crypto_ohlcv", df, symbol=symbol, interval=interval, limit=limit)
            return df

        except Exception as e:
            logger.error(f"Erreur traitement klines {symbol}: {str(e)}")
            return None

    def get_exchange_info(self) -> Optional[Dict[str, Any]]:
        """Récupérer informations sur l'exchange"""
        cache_key = "exchange_info"

        # Cache 1 heure pour infos exchange
        cached_data = self.cache.get("exchange_info")
        if cached_data is not None:
                return cached_data

        endpoint = "exchangeInfo"
        response = self._make_request(endpoint)

        if response:
            self.cache.set("exchange_info", response)
            return response

        return None

    def get_all_tickers(self) -> List[Dict[str, Any]]:
        """Récupérer tous les prix (ATTENTION: requête lourde)"""
        cache_key = "all_tickers"

        # Cache 10 secondes pour tous les prix
        cached_data = self.cache.get("exchange_info")
        if cached_data is not None:
                return cached_data

        endpoint = "ticker/price"
        response = self._make_request(endpoint)

        if response:
            tickers = [
                {"symbol": ticker["symbol"], "price": float(ticker["price"])}
                for ticker in response
            ]
            self.cache.set("crypto_prices", tickers)
            return tickers

        return []

    def get_popular_symbols(self) -> List[str]:
        """Retourner symboles populaires"""
        return self.popular_symbols.copy()

    def get_all_symbols(self) -> List[str]:
        """Récupérer TOUS les symboles Binance actifs (USDT seulement)"""
        cache_key = "all_usdt_symbols"

        # Cache 1 heure pour la liste des symboles
        cached_data = self.cache.get("exchange_info")
        if cached_data is not None:
                return cached_data

        try:
            exchange_info = self.get_exchange_info()
            if not exchange_info:
                logger.warning(
                    "Impossible de récupérer exchange info - utilisation symboles populaires"
                )
                return self.popular_symbols.copy()

            # Filtrer symboles USDT actifs uniquement
            usdt_symbols = [
                s["symbol"]
                for s in exchange_info["symbols"]
                if (
                    s["status"] == "TRADING"
                    and s["symbol"].endswith("USDT")
                    and s["quoteAsset"] == "USDT"
                )
            ]

            # Trier alphabétiquement
            usdt_symbols.sort()

            self.cache.set("symbols_list", usdt_symbols)
            logger.info(f"✅ {len(usdt_symbols)} symboles USDT récupérés")

            return usdt_symbols

        except Exception as e:
            logger.error(f"Erreur récupération symboles: {str(e)}")
            return self.popular_symbols.copy()

    def search_symbols(self, query: str, limit: int = 15) -> List[str]:
        """Recherche intelligente de symboles"""
        if not query or len(query) < 2:
            return self.popular_symbols[:limit]

        try:
            all_symbols = self.get_all_symbols()
            query_upper = query.upper()

            # Recherche prioritaire : symboles qui commencent par la requête
            exact_start = [s for s in all_symbols if s.startswith(query_upper)]

            # Recherche secondaire : symboles qui contiennent la requête
            contains = [
                s for s in all_symbols if query_upper in s and s not in exact_start
            ]

            # Combiner et limiter
            results = exact_start + contains
            return results[:limit]

        except Exception as e:
            logger.error(f"Erreur recherche symboles: {str(e)}")
            return self.popular_symbols[:limit]

    def get_market_summary(self) -> Dict[str, Any]:
        """Résumé du marché avec symboles populaires"""
        summary = {
            "total_symbols": 0,
            "active_symbols": 0,
            "popular_prices": {},
            "last_updated": datetime.now(),
        }

        try:
            # Récupérer infos exchange
            exchange_info = self.get_exchange_info()
            if exchange_info:
                summary["total_symbols"] = len(exchange_info["symbols"])
                summary["active_symbols"] = len(
                    [s for s in exchange_info["symbols"] if s["status"] == "TRADING"]
                )

            # Prix des symboles populaires
            for symbol in self.popular_symbols[:5]:  # 5 premiers
                ticker = self.get_ticker_24hr(symbol)
                if ticker:
                    summary["popular_prices"][symbol] = {
                        "price": ticker["last_price"],
                        "change_percent": ticker["price_change_percent"],
                    }

        except Exception as e:
            logger.error(f"Erreur résumé marché: {str(e)}")

        return summary

    def get_news(self, limit: int = 20) -> List[Dict]:
        """Récupérer les annonces officielles Binance"""
        try:
            logger.info(f"📰 Fetching Binance official announcements...")

            # Note: Binance n'a pas d'API publique pour les news
            # On retourne des informations génériques sur Binance
            news_items = [
                {
                    "title": "Binance Trading Platform",
                    "description": "Binance is the world's leading cryptocurrency exchange platform providing real-time market data.",
                    "url": "https://www.binance.com",
                    "published_at": datetime.now().isoformat(),
                    "source": "Binance",
                    "category": "crypto",
                    "symbol": None,
                },
                {
                    "title": "Real-time Cryptocurrency Data",
                    "description": "Access to live cryptocurrency prices, trading volumes, and market movements through Binance API.",
                    "url": "https://www.binance.com/en/markets",
                    "published_at": (datetime.now() - timedelta(hours=1)).isoformat(),
                    "source": "Binance",
                    "category": "crypto",
                    "symbol": None,
                },
            ]

            logger.info(f"✅ Retrieved {len(news_items)} Binance information items")
            return news_items[:limit]

        except Exception as e:
            logger.error(f"❌ Erreur récupération news Binance: {e}")
            return []

    def get_24hr_ticker(self, symbol: str = None) -> Dict:
        """Récupère les statistiques 24h pour un symbole ou tous"""
        # Validation du symbole si fourni
        if symbol is not None:
            if not isinstance(symbol, str) or not symbol.strip():
                logger.error(f"❌ Symbole invalide: {symbol}")
                return {}
            symbol = symbol.upper().strip()

        try:
            endpoint = "/ticker/24hr"
            params = {}
            if symbol:
                params["symbol"] = symbol

            response = self._make_request(endpoint, params)

            if response is None:
                return {} if symbol else []

            if symbol:
                # Un seul ticker
                return {
                    "symbol": response.get("symbol"),
                    "price": float(response.get("lastPrice", 0)),
                    "priceChange": float(response.get("priceChange", 0)),
                    "priceChangePercent": float(response.get("priceChangePercent", 0)),
                    "volume": float(response.get("volume", 0)),
                    "quoteVolume": float(response.get("quoteVolume", 0)),
                    "high": float(response.get("highPrice", 0)),
                    "low": float(response.get("lowPrice", 0)),
                    "count": int(response.get("count", 0)),
                }
            else:
                # Tous les tickers
                if not isinstance(response, list):
                    return []

                return [
                    {
                        "symbol": ticker.get("symbol"),
                        "price": float(ticker.get("lastPrice", 0)),
                        "priceChange": float(ticker.get("priceChange", 0)),
                        "priceChangePercent": float(
                            ticker.get("priceChangePercent", 0)
                        ),
                        "volume": float(ticker.get("volume", 0)),
                        "quoteVolume": float(ticker.get("quoteVolume", 0)),
                        "high": float(ticker.get("highPrice", 0)),
                        "low": float(ticker.get("lowPrice", 0)),
                        "count": int(ticker.get("count", 0)),
                    }
                    for ticker in response[:100]  # Limiter pour éviter trop de données
                ]

        except Exception as e:
            logger.error(f"❌ Erreur récupération ticker 24h: {e}")
            return {} if symbol else []

    def get_top_symbols(self, limit: int = 20) -> List[str]:
        """Récupère les top symboles par volume"""
        try:
            all_tickers = self.get_24hr_ticker()
            if not all_tickers:
                return []

            # Filtrer les USDT pairs et trier par volume
            usdt_pairs = [
                ticker
                for ticker in all_tickers
                if ticker["symbol"].endswith("USDT") and ticker["quoteVolume"] > 0
            ]

            # Trier par volume de quote (USDT)
            usdt_pairs.sort(key=lambda x: x["quoteVolume"], reverse=True)

            return [ticker["symbol"] for ticker in usdt_pairs[:limit]]

        except Exception as e:
            logger.error(f"❌ Erreur récupération top symboles: {e}")
            return []

    def get_gainers_losers(self, limit: int = 10) -> Dict:
        """Récupère les top gainers et losers 24h"""
        try:
            all_tickers = self.get_24hr_ticker()
            if not all_tickers:
                return {"gainers": [], "losers": []}

            # Filtrer les USDT pairs avec volume significatif
            usdt_pairs = [
                ticker
                for ticker in all_tickers
                if ticker["symbol"].endswith("USDT")
                and ticker["quoteVolume"] > 100000  # 100k USDT minimum
            ]

            # Trier par pourcentage de changement
            gainers = sorted(
                usdt_pairs, key=lambda x: x["priceChangePercent"], reverse=True
            )[:limit]
            losers = sorted(usdt_pairs, key=lambda x: x["priceChangePercent"])[:limit]

            return {
                "gainers": [
                    {
                        "symbol": ticker["symbol"],
                        "price": ticker["price"],
                        "change_percent": ticker["priceChangePercent"],
                        "volume": ticker["quoteVolume"],
                    }
                    for ticker in gainers
                ],
                "losers": [
                    {
                        "symbol": ticker["symbol"],
                        "price": ticker["price"],
                        "change_percent": ticker["priceChangePercent"],
                        "volume": ticker["quoteVolume"],
                    }
                    for ticker in losers
                ],
            }

        except Exception as e:
            logger.error(f"❌ Erreur récupération gainers/losers: {e}")
            return {"gainers": [], "losers": []}

    def get_market_summary(self) -> Dict:
        """Récupère un résumé global du marché crypto"""
        try:
            all_tickers = self.get_24hr_ticker()
            if not all_tickers:
                return {}

            # Filtrer les USDT pairs
            usdt_pairs = [
                ticker for ticker in all_tickers if ticker["symbol"].endswith("USDT")
            ]

            if not usdt_pairs:
                return {}

            # Calculer statistiques globales
            total_volume = sum(ticker["quoteVolume"] for ticker in usdt_pairs)
            gainers_count = len([t for t in usdt_pairs if t["priceChangePercent"] > 0])
            losers_count = len([t for t in usdt_pairs if t["priceChangePercent"] < 0])
            avg_change = sum(
                ticker["priceChangePercent"] for ticker in usdt_pairs
            ) / len(usdt_pairs)

            # Top par volume
            top_by_volume = sorted(
                usdt_pairs, key=lambda x: x["quoteVolume"], reverse=True
            )[:5]

            return {
                "total_pairs": len(usdt_pairs),
                "total_volume_usdt": total_volume,
                "gainers_count": gainers_count,
                "losers_count": losers_count,
                "neutral_count": len(usdt_pairs) - gainers_count - losers_count,
                "average_change_percent": avg_change,
                "top_volume_pairs": [
                    {
                        "symbol": ticker["symbol"],
                        "volume": ticker["quoteVolume"],
                        "change_percent": ticker["priceChangePercent"],
                    }
                    for ticker in top_by_volume
                ],
            }

        except Exception as e:
            logger.error(f"❌ Erreur résumé marché: {e}")
            return {}


# Instance globale
binance_provider = BinanceProvider()
