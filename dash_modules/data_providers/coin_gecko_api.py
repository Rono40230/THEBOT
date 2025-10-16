from src.thebot.core.logger import logger
"""
CoinGecko API Module for THEBOT
Provides comprehensive cryptocurrency market data
"""

import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from .provider_interfaces import DataProviderInterface
from src.thebot.core.cache import get_global_cache


class CoinGeckoAPI(DataProviderInterface):
    """CoinGecko API client for cryptocurrency market data - Implémente DataProviderInterface"""

    @property
    def name(self) -> str:
        return "coin_gecko"

    @property
    def supported_markets(self) -> List[str]:
        # CoinGecko supporte tous les cryptos, mais on liste les principales
        return ["bitcoin", "ethereum", "binancecoin", "cardano", "solana", "polkadot", "chainlink",
                "litecoin", "avalanche-2", "polygon-pos", "cosmos", "ripple"]

    @property
    def rate_limit_info(self) -> Dict[str, Any]:
        return {
            "requests_per_minute": 25 if not self.api_key else 500,
            "has_free_tier": True,
            "free_tier_limits": "25 appels/minute",
            "pro_tier_limits": "500 appels/minute"
        }

    def validate_symbol(self, symbol: str) -> bool:
        """Valide si un symbole est supporté par CoinGecko"""
        if not isinstance(symbol, str) or not symbol.strip():
            return False
        # CoinGecko utilise des IDs (bitcoin, ethereum) plutôt que des symboles (BTC, ETH)
        # On fait une conversion basique
        symbol_mapping = {
            "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
            "ADA": "cardano", "SOL": "solana", "DOT": "polkadot",
            "LINK": "chainlink", "LTC": "litecoin", "AVAX": "avalanche-2",
            "MATIC": "polygon-pos", "ATOM": "cosmos", "XRP": "ripple"
        }
        coin_id = symbol_mapping.get(symbol.upper())
        return coin_id in self.supported_markets if coin_id else False

    def get_price_data(self, symbol: str, interval: str = "1d", limit: int = 100) -> Optional[Dict[str, Any]]:
        """Récupère les données de prix historiques - Implémentation DataProviderInterface"""
        # CoinGecko utilise des IDs, pas des symboles
        symbol_mapping = {
            "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
            "ADA": "cardano", "SOL": "solana", "DOT": "polkadot"
        }
        coin_id = symbol_mapping.get(symbol.upper())
        if not coin_id:
            return None

        # Pour les données historiques, on utilise une méthode simplifiée
        # CoinGecko n'a pas d'endpoint direct pour les OHLCV comme Binance
        current_data = self.get_current_price(symbol)
        if current_data is None:
            return None

        return {
            "symbol": symbol,
            "interval": interval,
            "data": [{"timestamp": datetime.now(), "close": current_data}],
            "count": 1,
            "provider": self.name,
            "timestamp": datetime.now(),
            "note": "CoinGecko fournit principalement des données actuelles, pas historiques complètes"
        }

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Récupère le prix actuel - Implémentation DataProviderInterface"""
        symbol_mapping = {
            "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
            "ADA": "cardano", "SOL": "solana", "DOT": "polkadot"
        }
        coin_id = symbol_mapping.get(symbol.upper())
        if not coin_id:
            return None

        data = self.get_market_data([coin_id])
        if data is not None and not data.empty and 'current_price' in data.columns:
            return float(data.iloc[0]['current_price'])
        return None

    def get_market_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations sur le marché - Implémentation DataProviderInterface"""
        symbol_mapping = {
            "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
            "ADA": "cardano", "SOL": "solana", "DOT": "polkadot"
        }
        coin_id = symbol_mapping.get(symbol.upper())
        if not coin_id:
            return None

        data = self.get_market_data([coin_id])
        if data is not None and not data.empty:
            row = data.iloc[0]
            return {
                "symbol": symbol,
                "name": row.get('name', ''),
                "current_price": row.get('current_price', 0),
                "market_cap": row.get('market_cap', 0),
                "price_change_24h": row.get('price_change_percentage_24h', 0),
                "provider": self.name,
                "timestamp": datetime.now()
            }
        return None

    def is_available(self) -> bool:
        """Vérifie si CoinGecko est disponible - Implémentation DataProviderInterface"""
        try:
            return self.get_current_price("BTC") is not None
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du provider - Implémentation DataProviderInterface"""
        return {
            "name": self.name,
            "available": self.is_available(),
            "supported_markets_count": len(self.supported_markets),
            "rate_limit_info": self.rate_limit_info,
            "api_key_configured": self.api_key is not None,
            "rate_limit_calls": self.rate_limit_calls,
            "rate_limit_reset": self.rate_limit_reset
        }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if api_key:
            self.base_url = "https://pro-api.coingecko.com/api/v3"
        else:
            self.base_url = "https://api.coingecko.com/api/v3"

        self.cache = get_global_cache()  # Utiliser le cache intelligent global
        self.rate_limit_calls = 0
        self.rate_limit_reset = datetime.now()

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with rate limiting and caching"""
        # Vérifier le cache d'abord
        cache_key = f"coingecko_{endpoint}"
        cached_result = self.cache.get(cache_key, endpoint=endpoint, params=params or {})
        if cached_result is not None:
            logger.info(f"📋 Cache hit pour CoinGecko {endpoint}")
            return cached_result

        # Rate limiting: 30 calls/minute for free tier, 500/minute for pro
        max_calls = 500 if self.api_key else 25  # Leave margin for free tier
        reset_period = timedelta(minutes=1)

        current_time = datetime.now()
        if current_time - self.rate_limit_reset > reset_period:
            self.rate_limit_calls = 0
            self.rate_limit_reset = current_time

        if self.rate_limit_calls >= max_calls:
            wait_time = 60 - (current_time - self.rate_limit_reset).seconds
            if wait_time > 0:
                logger.info(f"⏱️ CoinGecko rate limit: waiting {wait_time}s...")
                time.sleep(min(wait_time, 30))

        try:
            url = f"{self.base_url}{endpoint}"
            headers = {}

            if self.api_key:
                headers["x-cg-pro-api-key"] = self.api_key

            response = requests.get(
                url, params=params or {}, headers=headers, timeout=10
            )
            self.rate_limit_calls += 1

            if response.status_code == 200:
                try:
                    result = response.json()
                    # Mettre en cache le résultat
                    self.cache.set(cache_key, result, endpoint=endpoint, params=params or {})
                    return result
                except ValueError as e:
                    logger.info(f"❌ Erreur parsing JSON CoinGecko: {e}")
                    return {}
            else:
                logger.info(f"❌ CoinGecko API error: {response.status_code}")
                return {}

        except requests.RequestException as e:
            logger.info(f"❌ CoinGecko request error: {e}")
            return {}
        except Exception as e:
            logger.info(f"❌ CoinGecko unexpected error: {e}")
            return {}

    def get_market_data(
        self, coin_ids: List[str] = None, vs_currency: str = "usd"
    ) -> pd.DataFrame:
        """Get market data for cryptocurrencies"""
        logger.info(f"📊 Fetching CoinGecko market data...")

        try:
            params = {
                "vs_currency": vs_currency,
                "order": "market_cap_desc",
                "per_page": 100,
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "1h,24h,7d",
            }

            if coin_ids:
                params["ids"] = ",".join(coin_ids[:100])  # API limit

            data = self._make_request("/coins/markets", params)

            if not data:
                logger.info("❌ No CoinGecko market data received")
                return pd.DataFrame()

            # Convert to DataFrame
            df_data = []
            for coin in data:
                df_data.append(
                    {
                        "id": coin.get("id", ""),
                        "symbol": coin.get("symbol", "").upper(),
                        "name": coin.get("name", ""),
                        "current_price": coin.get("current_price", 0),
                        "market_cap": coin.get("market_cap", 0),
                        "market_cap_rank": coin.get("market_cap_rank", 0),
                        "volume_24h": coin.get("total_volume", 0),
                        "price_change_1h": coin.get(
                            "price_change_percentage_1h_in_currency", 0
                        ),
                        "price_change_24h": coin.get("price_change_percentage_24h", 0),
                        "price_change_7d": coin.get(
                            "price_change_percentage_7d_in_currency", 0
                        ),
                        "ath": coin.get("ath", 0),
                        "atl": coin.get("atl", 0),
                        "last_updated": coin.get(
                            "last_updated", datetime.now().isoformat()
                        ),
                    }
                )

            df = pd.DataFrame(df_data)
            logger.info(f"✅ Retrieved market data for {len(df)} cryptocurrencies")
            return df

        except Exception as e:
            logger.info(f"❌ CoinGecko market data error: {e}")
            return pd.DataFrame()

    def get_historical_price_data(self, coin_id: str, days: int = 7) -> pd.DataFrame:
        """Get historical price data for a specific coin"""
        # Validation du coin_id
        if not isinstance(coin_id, str) or not coin_id.strip():
            logger.info(f"❌ Coin ID invalide: {coin_id}")
            return pd.DataFrame()

        coin_id = coin_id.lower().strip()

        logger.info(f"📈 Fetching price history for {coin_id}...")

        try:
            params = {
                "vs_currency": "usd",
                "days": days,
                "interval": "hourly" if days <= 7 else "daily",
            }

            data = self._make_request(f"/coins/{coin_id}/market_chart", params)

            if not data or "prices" not in data:
                logger.info(f"❌ No price data for {coin_id}")
                return pd.DataFrame()

            # Convert to DataFrame
            timestamps = [
                datetime.fromtimestamp(price[0] / 1000) for price in data["prices"]
            ]
            prices = [price[1] for price in data["prices"]]
            volumes = [vol[1] for vol in data.get("total_volumes", [])]

            df = pd.DataFrame(
                {
                    "timestamp": timestamps,
                    "price": prices,
                    "volume": volumes[: len(prices)] if volumes else [0] * len(prices),
                }
            )

            df = df.set_index("timestamp")
            logger.info(f"✅ Retrieved {len(df)} price points for {coin_id}")
            return df

        except Exception as e:
            logger.info(f"❌ Error getting price data for {coin_id}: {e}")
            return pd.DataFrame()

    def get_trending_coins(self) -> List[Dict]:
        """Get trending cryptocurrencies"""
        try:
            data = self._make_request("/search/trending")

            if not data or "coins" not in data:
                return []

            trending = []
            for coin_data in data["coins"]:
                coin = coin_data.get("item", {})
                trending.append(
                    {
                        "id": coin.get("id", ""),
                        "symbol": coin.get("symbol", ""),
                        "name": coin.get("name", ""),
                        "market_cap_rank": coin.get("market_cap_rank", 0),
                        "score": coin.get("score", 0),
                    }
                )

            logger.info(f"✅ Retrieved {len(trending)} trending coins")
            return trending

        except Exception as e:
            logger.info(f"❌ Error getting trending coins: {e}")
            return []

    def search_coins(self, query: str) -> List[Dict]:
        """Search for cryptocurrencies"""
        try:
            params = {"query": query}
            data = self._make_request("/search", params)

            if not data or "coins" not in data:
                return []

            results = []
            for coin in data["coins"][:10]:  # Limit results
                results.append(
                    {
                        "id": coin.get("id", ""),
                        "symbol": coin.get("symbol", ""),
                        "name": coin.get("name", ""),
                        "market_cap_rank": coin.get("market_cap_rank", 0),
                    }
                )

            return results

        except Exception as e:
            logger.info(f"❌ Error searching coins: {e}")
            return []

    def get_news(self, limit: int = 20) -> List[Dict]:
        """Get cryptocurrency news from CoinGecko (limited data)"""
        # Note: CoinGecko doesn't have a dedicated news endpoint in free tier
        # This method provides general market information
        try:
            # Get global market data as "news"
            global_data = self._make_request("/global")
            trending_data = self.get_trending_coins()

            news_items = []

            if global_data and "data" in global_data:
                market = global_data["data"]
                news_items.append(
                    {
                        "title": "Global Cryptocurrency Market Update",
                        "description": f"Total market cap: ${market.get('total_market_cap', {}).get('usd', 0):,.0f}. "
                        f"Bitcoin dominance: {market.get('market_cap_percentage', {}).get('btc', 0):.1f}%. "
                        f"Active cryptocurrencies: {market.get('active_cryptocurrencies', 0):,}",
                        "url": "https://www.coingecko.com",
                        "published_at": datetime.now().isoformat(),
                        "source": "CoinGecko",
                        "category": "crypto",
                        "symbol": None,
                    }
                )

            # Add trending coins as "news"
            if trending_data:
                trending_names = [coin["name"] for coin in trending_data[:5]]
                news_items.append(
                    {
                        "title": "Trending Cryptocurrencies Today",
                        "description": f"Top trending coins: {', '.join(trending_names)}. "
                        "These cryptocurrencies are gaining significant attention in the market.",
                        "url": "https://www.coingecko.com/en/crypto-news",
                        "published_at": (
                            datetime.now() - timedelta(hours=1)
                        ).isoformat(),
                        "source": "CoinGecko",
                        "category": "crypto",
                        "symbol": None,
                    }
                )

            # Add fallback content
            if not news_items:
                news_items = [
                    {
                        "title": "CoinGecko - Cryptocurrency Market Data",
                        "description": "CoinGecko provides comprehensive cryptocurrency market data, rankings, and analysis.",
                        "url": "https://www.coingecko.com",
                        "published_at": datetime.now().isoformat(),
                        "source": "CoinGecko",
                        "category": "crypto",
                        "symbol": None,
                    }
                ]

            logger.info(f"✅ Generated {len(news_items)} market updates from CoinGecko")
            return news_items[:limit]

        except Exception as e:
            logger.info(f"❌ CoinGecko news error: {e}")
            return []


# Global instance
coin_gecko_api = CoinGeckoAPI()
