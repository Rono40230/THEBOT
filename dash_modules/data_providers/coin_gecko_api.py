"""
CoinGecko API Module for THEBOT
Provides comprehensive cryptocurrency market data
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
import requests


class CoinGeckoAPI:
    """CoinGecko API client for cryptocurrency market data"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if api_key:
            self.base_url = "https://pro-api.coingecko.com/api/v3"
        else:
            self.base_url = "https://api.coingecko.com/api/v3"

        self.rate_limit_calls = 0
        self.rate_limit_reset = datetime.now()

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with rate limiting"""
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
                print(f"⏱️ CoinGecko rate limit: waiting {wait_time}s...")
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
                return response.json()
            else:
                print(f"❌ CoinGecko API error: {response.status_code}")
                return {}

        except Exception as e:
            print(f"❌ CoinGecko request error: {e}")
            return {}

    def get_market_data(
        self, coin_ids: List[str] = None, vs_currency: str = "usd"
    ) -> pd.DataFrame:
        """Get market data for cryptocurrencies"""
        print(f"📊 Fetching CoinGecko market data...")

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
                print("❌ No CoinGecko market data received")
                return pd.DataFrame()

            # Convert to DataFrame
            df_data = []
            for coin in data:
                df_data.append(
                    {
                        "id": coin.get("id", ""),
                        "symbol": coin.get("symbol", "").upper(),
                        "name": coin.get("name", ""),
                        "price": coin.get("current_price", 0),
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
            print(f"✅ Retrieved market data for {len(df)} cryptocurrencies")
            return df

        except Exception as e:
            print(f"❌ CoinGecko market data error: {e}")
            return pd.DataFrame()

    def get_price_data(self, coin_id: str, days: int = 7) -> pd.DataFrame:
        """Get historical price data for a specific coin"""
        print(f"📈 Fetching price history for {coin_id}...")

        try:
            params = {
                "vs_currency": "usd",
                "days": days,
                "interval": "hourly" if days <= 7 else "daily",
            }

            data = self._make_request(f"/coins/{coin_id}/market_chart", params)

            if not data or "prices" not in data:
                print(f"❌ No price data for {coin_id}")
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
            print(f"✅ Retrieved {len(df)} price points for {coin_id}")
            return df

        except Exception as e:
            print(f"❌ Error getting price data for {coin_id}: {e}")
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

            print(f"✅ Retrieved {len(trending)} trending coins")
            return trending

        except Exception as e:
            print(f"❌ Error getting trending coins: {e}")
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
            print(f"❌ Error searching coins: {e}")
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

            print(f"✅ Generated {len(news_items)} market updates from CoinGecko")
            return news_items[:limit]

        except Exception as e:
            print(f"❌ CoinGecko news error: {e}")
            return []


# Global instance
coin_gecko_api = CoinGeckoAPI()
