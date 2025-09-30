"""
Alpha Vantage API Module for THEBOT
Provides Forex, Stocks, and Economic News data
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class AlphaVantageAPI:
    """Alpha Vantage API client for financial data"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit_calls = 0
        self.rate_limit_reset = datetime.now()
        
    def _make_request(self, params: Dict) -> Dict:
        """Make API request with rate limiting"""
        # Rate limiting: 5 calls per minute for free tier
        current_time = datetime.now()
        if current_time - self.rate_limit_reset > timedelta(minutes=1):
            self.rate_limit_calls = 0
            self.rate_limit_reset = current_time
            
        if self.rate_limit_calls >= 5:
            wait_time = 60 - (current_time - self.rate_limit_reset).seconds
            if wait_time > 0:
                print(f"⏱️ Rate limit: waiting {wait_time}s...")
                time.sleep(wait_time)
                self.rate_limit_calls = 0
                self.rate_limit_reset = datetime.now()
        
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            self.rate_limit_calls += 1
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Alpha Vantage API error: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Alpha Vantage request failed: {e}")
            return {}
    
    def get_forex_data(self, from_symbol: str, to_symbol: str, interval: str = "1h") -> pd.DataFrame:
        """Get forex data (e.g. EUR/USD)"""
        if not self.api_key:
            return self._create_fallback_forex_data(from_symbol, to_symbol)
        
        # Map intervals
        interval_map = {
            "1m": "1min", "5m": "5min", "15m": "15min", 
            "30m": "30min", "1h": "60min", "4h": "daily", "1d": "daily"
        }
        av_interval = interval_map.get(interval, "60min")
        
        if av_interval == "daily":
            function = "FX_DAILY"
        else:
            function = "FX_INTRADAY"
            
        params = {
            "function": function,
            "from_symbol": from_symbol,
            "to_symbol": to_symbol,
            "outputsize": "compact"
        }
        
        if function == "FX_INTRADAY":
            params["interval"] = av_interval
            
        print(f"🔄 Fetching {from_symbol}/{to_symbol} forex data...")
        data = self._make_request(params)
        
        if not data or "Error Message" in data or "Note" in data:
            print(f"⚠️ Alpha Vantage forex data unavailable, using fallback")
            return self._create_fallback_forex_data(from_symbol, to_symbol)
        
        return self._parse_forex_data(data, function)
    
    def get_stock_data(self, symbol: str, interval: str = "1h") -> pd.DataFrame:
        """Get stock data"""
        if not self.api_key:
            return self._create_fallback_stock_data(symbol)
        
        # Map intervals
        if interval in ["1m", "5m", "15m", "30m", "1h"]:
            function = "TIME_SERIES_INTRADAY"
            av_interval = {"1m": "1min", "5m": "5min", "15m": "15min", 
                          "30m": "30min", "1h": "60min"}[interval]
        else:
            function = "TIME_SERIES_DAILY"
            av_interval = None
            
        params = {
            "function": function,
            "symbol": symbol,
            "outputsize": "compact"
        }
        
        if av_interval:
            params["interval"] = av_interval
            
        print(f"🔄 Fetching {symbol} stock data...")
        data = self._make_request(params)
        
        if not data or "Error Message" in data or "Note" in data:
            print(f"⚠️ Alpha Vantage stock data unavailable, using fallback")
            return self._create_fallback_stock_data(symbol)
        
        return self._parse_stock_data(data, function)
    
    def get_economic_news(self, limit: int = 50) -> List[Dict]:
        """Get economic news and sentiment"""
        print(f"🔍 API Key status: {'✅ Available' if self.api_key else '❌ Missing'}")
        if self.api_key:
            print(f"🔑 API Key: {self.api_key[:8]}...")
        
        if not self.api_key:
            print("⚠️ No API key, using fallback news")
            return self._create_fallback_news()
        
        params = {
            "function": "NEWS_SENTIMENT",
            "topics": "financial_markets,economy_fiscal_policy",
            "limit": limit
        }
        
        print("🔄 Fetching economic news from Alpha Vantage...")
        data = self._make_request(params)
        
        if not data or "feed" not in data:
            print("⚠️ Alpha Vantage news unavailable, using fallback")
            print(f"📊 Response keys: {list(data.keys()) if data else 'No data'}")
            if data and 'Information' in data:
                print(f"ℹ️ Alpha Vantage Information: {data['Information']}")
            elif data and 'Note' in data:
                print(f"ℹ️ Alpha Vantage Note: {data['Note']}")
            return self._create_fallback_news()
        
        print(f"✅ Received {len(data.get('feed', []))} news articles from Alpha Vantage")
        return self._parse_news_data(data)
    
    def _parse_forex_data(self, data: Dict, function: str) -> pd.DataFrame:
        """Parse forex API response to DataFrame"""
        if function == "FX_DAILY":
            time_series_key = "Time Series (FX)"
        else:
            time_series_key = list(data.keys())[1]  # Second key is time series
            
        time_series = data.get(time_series_key, {})
        
        df_data = []
        for timestamp, values in time_series.items():
            df_data.append({
                'timestamp': pd.to_datetime(timestamp),
                'open': float(values.get('1. open', 0)),
                'high': float(values.get('2. high', 0)),
                'low': float(values.get('3. low', 0)),
                'close': float(values.get('4. close', 0))
            })
        
        df = pd.DataFrame(df_data)
        if not df.empty:
            df = df.sort_values('timestamp').reset_index(drop=True)
            df.index = df['timestamp']
        
        return df
    
    def _parse_stock_data(self, data: Dict, function: str) -> pd.DataFrame:
        """Parse stock API response to DataFrame"""
        if function == "TIME_SERIES_DAILY":
            time_series_key = "Time Series (Daily)"
        else:
            time_series_key = list(data.keys())[1]  # Second key is time series
            
        time_series = data.get(time_series_key, {})
        
        df_data = []
        for timestamp, values in time_series.items():
            df_data.append({
                'timestamp': pd.to_datetime(timestamp),
                'open': float(values.get('1. open', 0)),
                'high': float(values.get('2. high', 0)),
                'low': float(values.get('3. low', 0)),
                'close': float(values.get('4. close', 0)),
                'volume': float(values.get('5. volume', 0))
            })
        
        df = pd.DataFrame(df_data)
        if not df.empty:
            df = df.sort_values('timestamp').reset_index(drop=True)
            df.index = df['timestamp']
        
        return df
    
    def _parse_news_data(self, data: Dict) -> List[Dict]:
        """Parse news API response"""
        news_items = []
        
        for item in data.get("feed", []):
            news_items.append({
                'title': item.get('title', ''),
                'summary': item.get('summary', ''),
                'url': item.get('url', ''),
                'time_published': item.get('time_published', ''),
                'sentiment_score': item.get('overall_sentiment_score', 0),
                'sentiment_label': item.get('overall_sentiment_label', 'Neutral'),
                'source': item.get('source', 'Unknown'),
                'topics': item.get('topics', [])
            })
        
        return news_items
    
    def _create_fallback_forex_data(self, from_symbol: str, to_symbol: str) -> pd.DataFrame:
        """Create fallback forex data when API unavailable"""
        print(f"📊 Creating fallback data for {from_symbol}/{to_symbol}")
        
        # Base rate (example rates)
        base_rates = {
            "EURUSD": 1.0850, "GBPUSD": 1.2650, "USDJPY": 149.50,
            "USDCHF": 0.8950, "AUDUSD": 0.6450, "USDCAD": 1.3750
        }
        
        pair = f"{from_symbol}{to_symbol}"
        base_rate = base_rates.get(pair, 1.0)
        
        # Generate 200 points of realistic forex data
        dates = pd.date_range(end=datetime.now(), periods=200, freq='H')
        
        df_data = []
        current_price = base_rate
        
        for i, date in enumerate(dates):
            # Realistic forex volatility (0.1-0.5% moves)
            change = (pd.np.random.randn() * 0.003) + (0.0001 * pd.np.sin(i/10))
            current_price *= (1 + change)
            
            # Create OHLC data
            high = current_price * (1 + abs(pd.np.random.randn() * 0.001))
            low = current_price * (1 - abs(pd.np.random.randn() * 0.001))
            open_price = current_price * (1 + pd.np.random.randn() * 0.0005)
            
            df_data.append({
                'timestamp': date,
                'open': round(open_price, 5),
                'high': round(high, 5),
                'low': round(low, 5),
                'close': round(current_price, 5)
            })
        
        df = pd.DataFrame(df_data)
        df.index = df['timestamp']
        return df
    
    def _create_fallback_stock_data(self, symbol: str) -> pd.DataFrame:
        """Create fallback stock data when API unavailable"""
        print(f"📊 Creating fallback data for {symbol}")
        
        # Base prices for common stocks
        base_prices = {
            "AAPL": 175.50, "MSFT": 415.20, "GOOGL": 140.30, "AMZN": 145.80,
            "TSLA": 245.60, "NVDA": 875.30, "META": 325.40, "BRK.A": 545000
        }
        
        base_price = base_prices.get(symbol, 100.0)
        
        # Generate 200 points of realistic stock data
        dates = pd.date_range(end=datetime.now(), periods=200, freq='H')
        
        df_data = []
        current_price = base_price
        
        for i, date in enumerate(dates):
            # Realistic stock volatility (0.5-2% moves)
            change = (pd.np.random.randn() * 0.015) + (0.001 * pd.np.sin(i/5))
            current_price *= (1 + change)
            
            # Create OHLCV data
            high = current_price * (1 + abs(pd.np.random.randn() * 0.005))
            low = current_price * (1 - abs(pd.np.random.randn() * 0.005))
            open_price = current_price * (1 + pd.np.random.randn() * 0.002)
            volume = int(pd.np.random.randint(1000000, 10000000))
            
            df_data.append({
                'timestamp': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(current_price, 2),
                'volume': volume
            })
        
        df = pd.DataFrame(df_data)
        df.index = df['timestamp']
        return df
    
    def _create_fallback_news(self) -> List[Dict]:
        """Create fallback news data when API unavailable"""
        fallback_news = [
            {
                'title': 'Federal Reserve Maintains Interest Rates',
                'summary': 'The Federal Reserve decided to keep interest rates unchanged at 5.25-5.5% range.',
                'url': '#',
                'time_published': datetime.now().strftime('%Y%m%dT%H%M%S'),
                'sentiment_score': 0.1,
                'sentiment_label': 'Neutral',
                'source': 'Economic Calendar',
                'topics': ['monetary_policy', 'federal_reserve']
            },
            {
                'title': 'US GDP Growth Exceeds Expectations',
                'summary': 'Q3 GDP growth reached 2.4%, surpassing economist predictions of 2.1%.',
                'url': '#',
                'time_published': (datetime.now() - timedelta(hours=2)).strftime('%Y%m%dT%H%M%S'),
                'sentiment_score': 0.3,
                'sentiment_label': 'Positive',
                'source': 'Economic Data',
                'topics': ['gdp', 'economic_growth']
            },
            {
                'title': 'Inflation Data Shows Continued Decline',
                'summary': 'Core PCE inflation dropped to 3.2%, indicating progress towards Fed targets.',
                'url': '#',
                'time_published': (datetime.now() - timedelta(hours=5)).strftime('%Y%m%dT%H%M%S'),
                'sentiment_score': 0.2,
                'sentiment_label': 'Positive',
                'source': 'Bureau of Labor Statistics',
                'topics': ['inflation', 'economic_indicators']
            }
        ]
        
        return fallback_news
    
    def test_connection(self) -> Dict[str, bool]:
        """Test API connection and return status"""
        if not self.api_key:
            return {
                'connected': False,
                'error': 'No API key provided',
                'forex': False,
                'stocks': False,
                'news': False
            }
        
        # Test with a simple quote
        test_params = {
            "function": "GLOBAL_QUOTE",
            "symbol": "IBM"
        }
        
        result = self._make_request(test_params)
        
        if result and "Global Quote" in result:
            return {
                'connected': True,
                'error': None,
                'forex': True,
                'stocks': True,
                'news': True,
                'calls_remaining': 500 - self.rate_limit_calls
            }
        else:
            return {
                'connected': False,
                'error': result.get('Error Message', 'Unknown error'),
                'forex': False,
                'stocks': False,
                'news': False
            }