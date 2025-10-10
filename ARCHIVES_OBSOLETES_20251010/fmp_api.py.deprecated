"""
Financial Modeling Prep (FMP) API Module for THEBOT
Premium API for comprehensive financial data
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class FMPApi:
    """Financial Modeling Prep API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.base_url_v4 = "https://financialmodelingprep.com/api/v4"
        self.rate_limit_calls = 0
        self.rate_limit_reset = datetime.now()
        
    def _make_request(self, endpoint: str, params: Dict = None, version: str = "v3") -> Dict:
        """Make API request with rate limiting"""
        if not self.api_key:
            print("❌ FMP API key required")
            return {}
        
        # Rate limiting: 250 calls per minute for free tier
        current_time = datetime.now()
        if current_time - self.rate_limit_reset > timedelta(minutes=1):
            self.rate_limit_calls = 0
            self.rate_limit_reset = current_time
            
        if self.rate_limit_calls >= 240:  # Leave some margin
            wait_time = 60 - (current_time - self.rate_limit_reset).seconds
            if wait_time > 0:
                print(f"⏱️ FMP rate limit: waiting {wait_time}s...")
                time.sleep(min(wait_time, 30))  # Max 30 seconds wait
        
        try:
            if version == "v4":
                url = f"{self.base_url_v4}{endpoint}"
            else:
                url = f"{self.base_url}{endpoint}"
                
            if params is None:
                params = {}
            params['apikey'] = self.api_key
            
            response = requests.get(url, params=params, timeout=15)
            self.rate_limit_calls += 1
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print("⏱️ FMP rate limit reached")
                return {}
            else:
                print(f"❌ FMP API error: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ FMP request error: {e}")
            return {}
    
    def get_stock_data(self, symbol: str, period: str = "1day") -> pd.DataFrame:
        """Get stock historical data"""
        print(f"📊 Fetching FMP data for {symbol}...")
        
        endpoint = f"/historical-price-full/{symbol}"
        params = {
            "timeseries": 100  # Last 100 days
        }
        
        data = self._make_request(endpoint, params)
        
        if not data or "historical" not in data:
            print(f"❌ No FMP data received for {symbol}")
            return pd.DataFrame()
        
        return self._parse_stock_data(data, symbol)
    
    def get_forex_data(self, pair: str) -> pd.DataFrame:
        """Get forex historical data"""
        print(f"💱 Fetching FMP forex data for {pair}...")
        
        endpoint = f"/historical-price-full/{pair}"
        params = {
            "timeseries": 100
        }
        
        data = self._make_request(endpoint, params)
        
        if not data or "historical" not in data:
            print(f"❌ No FMP forex data for {pair}")
            return pd.DataFrame()
        
        return self._parse_stock_data(data, pair)
    
    def get_real_time_quote(self, symbols: List[str]) -> Dict:
        """Get real-time quotes"""
        print(f"💰 Fetching FMP quotes for {len(symbols)} symbols...")
        
        quotes = {}
        for symbol in symbols:
            endpoint = f"/quote/{symbol}"
            data = self._make_request(endpoint)
            
            if data and isinstance(data, list) and len(data) > 0:
                quote = data[0]
                quotes[symbol] = {
                    "price": quote.get("price", 0),
                    "change": quote.get("change", 0),
                    "change_percent": quote.get("changesPercentage", 0),
                    "volume": quote.get("volume", 0),
                    "market_cap": quote.get("marketCap", 0),
                    "name": quote.get("name", ""),
                    "currency": "USD"
                }
        
        return quotes
    
    def get_company_profile(self, symbol: str) -> Dict:
        """Get company profile data"""
        print(f"🏢 Fetching FMP company profile for {symbol}...")
        
        endpoint = f"/profile/{symbol}"
        data = self._make_request(endpoint)
        
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        
        return {}
    
    def get_financial_statements(self, symbol: str, statement_type: str = "income-statement") -> List[Dict]:
        """Get financial statements (income-statement, balance-sheet-statement, cash-flow-statement)"""
        print(f"📈 Fetching FMP {statement_type} for {symbol}...")
        
        endpoint = f"/{statement_type}/{symbol}"
        params = {
            "limit": 5  # Last 5 years
        }
        
        data = self._make_request(endpoint, params)
        
        if data and isinstance(data, list):
            return data
        
        return []
    
    def get_economic_calendar(self, from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get economic calendar events"""
        print("📅 Fetching FMP economic calendar...")
        
        if not from_date:
            from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        endpoint = "/economic_calendar"
        params = {
            "from": from_date,
            "to": to_date
        }
        
        data = self._make_request(endpoint, params)
        
        if data and isinstance(data, list):
            return data
        
        return []
    
    def get_crypto_data(self, symbol: str) -> pd.DataFrame:
        """Get cryptocurrency data"""
        print(f"₿ Fetching FMP crypto data for {symbol}...")
        
        endpoint = f"/historical-price-full/{symbol}"
        params = {
            "timeseries": 100
        }
        
        data = self._make_request(endpoint, params)
        
        if not data or "historical" not in data:
            return pd.DataFrame()
        
        return self._parse_stock_data(data, symbol)
    
    def search_companies(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for companies"""
        print(f"🔍 Searching FMP for: {query}")
        
        endpoint = "/search"
        params = {
            "query": query,
            "limit": limit
        }
        
        data = self._make_request(endpoint, params)
        
        if data and isinstance(data, list):
            return data
        
        return []
    
    def get_stock_screener(self, market_cap_more_than: int = 1000000000, limit: int = 50) -> List[Dict]:
        """Get stock screener results"""
        print("📊 Fetching FMP stock screener...")
        
        endpoint = "/stock-screener"
        params = {
            "marketCapMoreThan": market_cap_more_than,
            "limit": limit
        }
        
        data = self._make_request(endpoint, params)
        
        if data and isinstance(data, list):
            return data
        
        return []
    
    def get_forex_list(self) -> List[Dict]:
        """Get available forex pairs"""
        print("💱 Fetching FMP forex list...")
        
        endpoint = "/symbol/available-forex-currency-pairs"
        data = self._make_request(endpoint)
        
        if data and isinstance(data, list):
            return data
        
        return []
    
    def _parse_stock_data(self, data: Dict, symbol: str) -> pd.DataFrame:
        """Parse stock data response to DataFrame"""
        try:
            historical = data["historical"]
            
            df_data = []
            for item in historical:
                df_data.append({
                    'timestamp': pd.to_datetime(item["date"]),
                    'open': float(item.get("open", 0)),
                    'high': float(item.get("high", 0)),
                    'low': float(item.get("low", 0)),
                    'close': float(item.get("close", 0)),
                    'volume': int(item.get("volume", 0))
                })
            
            df = pd.DataFrame(df_data)
            if not df.empty:
                df = df.sort_values('timestamp').reset_index(drop=True)
                df.index = df['timestamp']
                print(f"✅ FMP: {len(df)} data points for {symbol}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error parsing FMP data: {e}")
            return pd.DataFrame()
    
    def test_connection(self) -> Dict[str, bool]:
        """Test API connection"""
        try:
            if not self.api_key:
                return {
                    'connected': False,
                    'error': 'API key required',
                    'stocks': False,
                    'forex': False,
                    'economic_calendar': False,
                    'message': 'FMP API key not configured'
                }
            
            # Test with a simple profile request
            data = self.get_company_profile("AAPL")
            
            if data and "symbol" in data:
                return {
                    'connected': True,
                    'error': None,
                    'stocks': True,
                    'forex': True,
                    'economic_calendar': True,
                    'message': 'FMP connected successfully'
                }
            else:
                return {
                    'connected': False,
                    'error': 'Invalid response',
                    'stocks': False,
                    'forex': False,
                    'economic_calendar': False,
                    'message': 'FMP connection failed'
                }
                
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'stocks': False,
                'forex': False,
                'economic_calendar': False,
                'message': f'FMP error: {e}'
            }
    
    def get_economic_news(self, limit: int = 50) -> List[Dict]:
        """Get financial news from FMP"""
        try:
            news_items = []
            
            # FMP has multiple news endpoints
            endpoints = [
                "/stock_news",  # General stock news
                "/general_news",  # General financial news
                "/press-releases",  # Press releases
            ]
            
            print("🔄 Fetching financial news from Financial Modeling Prep...")
            
            for endpoint in endpoints:
                try:
                    params = {'limit': limit // len(endpoints)}
                    data = self._make_request(endpoint, params)
                    
                    news_list = data if isinstance(data, list) else data.get('data', [])
                    
                    if isinstance(news_list, list):
                        for article in news_list:
                            
                            # Parse publication date
                            pub_date = None
                            if 'publishedDate' in article:
                                try:
                                    pub_date = datetime.strptime(article['publishedDate'], '%Y-%m-%d %H:%M:%S')
                                except:
                                    try:
                                        pub_date = datetime.strptime(article['publishedDate'][:19], '%Y-%m-%dT%H:%M:%S')
                                    except:
                                        pub_date = datetime.now()
                            else:
                                pub_date = datetime.now()
                            
                            # Determine category based on endpoint
                            category = "Market News"
                            if 'stock_news' in endpoint:
                                category = "Stocks"
                            elif 'press-releases' in endpoint:
                                category = "Earnings"
                            elif 'general_news' in endpoint:
                                category = "Financial"
                            
                            news_item = {
                                'title': article.get('title', 'No title'),
                                'summary': article.get('text', article.get('summary', article.get('title', ''))),
                                'url': article.get('url', ''),
                                'time_published': pub_date.strftime('%Y%m%dT%H%M%S'),
                                'source': article.get('site', 'Financial Modeling Prep'),
                                'category': category,
                                'overall_sentiment_score': 0.0,  # Neutral by default
                                'overall_sentiment_label': 'Neutral',
                                'ticker_sentiment': []
                            }
                            
                            # Add ticker information if available
                            if 'symbol' in article:
                                news_item['ticker_sentiment'] = [{
                                    'ticker': article['symbol'],
                                    'relevance_score': '1.0',
                                    'ticker_sentiment_score': '0.0',
                                    'ticker_sentiment_label': 'Neutral'
                                }]
                            
                            news_items.append(news_item)
                            
                            if len(news_items) >= limit:
                                break
                    
                    if len(news_items) >= limit:
                        break
                        
                except Exception as e:
                    print(f"⚠️ Error fetching from endpoint {endpoint}: {e}")
                    continue
            
            print(f"✅ Retrieved {len(news_items)} news articles from FMP")
            return news_items[:limit]
            
        except Exception as e:
            print(f"❌ FMP news error: {e}")
            return []


# Global instance
fmp_api = FMPApi()