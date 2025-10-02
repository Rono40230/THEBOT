"""
Twelve Data API Provider for THEBOT
Professional financial data provider with stocks, forex, crypto, and news
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import logging

logger = logging.getLogger(__name__)

class TwelveDataAPI:
    """Twelve Data API client for financial data and news"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://api.twelvedata.com"
        self.session = requests.Session()
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
        if self.api_key:
            logger.info("✅ Twelve Data API initialized with key")
        else:
            logger.warning("⚠️ Twelve Data API initialized without key (limited access)")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make rate-limited API request"""
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last)
            
            # Prepare parameters
            if params is None:
                params = {}
            
            if self.api_key:
                params['apikey'] = self.api_key
            
            # Make request
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("❌ Twelve Data API rate limit exceeded")
                return None
            elif response.status_code == 401:
                logger.error("❌ Twelve Data API unauthorized - check API key")
                return None
            else:
                logger.error(f"❌ Twelve Data API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Twelve Data API request failed: {e}")
            return None
    
    def get_financial_news(self, limit: int = 10) -> List[Dict]:
        """Get financial news from Twelve Data"""
        try:
            news_list = []
            
            # Get general financial news
            data = self._make_request("/news", {
                "source": "Reuters,Bloomberg,CNBC,MarketWatch",
                "limit": limit
            })
            
            if data and 'data' in data:
                for item in data['data'][:limit]:
                    news_item = {
                        'title': item.get('title', 'Titre non disponible'),
                        'summary': item.get('content', item.get('description', 'Résumé non disponible'))[:500],
                        'description': item.get('content', item.get('description', 'Description non disponible')),
                        'url': item.get('url', '#'),
                        'source': item.get('source', 'Twelve Data'),
                        'category': 'Financial News',
                        'provider': 'twelve_data',
                        'time_ago': self._format_time(item.get('datetime')),
                        'sentiment': 'neutral'
                    }
                    news_list.append(news_item)
            
            logger.info(f"✅ Retrieved {len(news_list)} news items from Twelve Data")
            return news_list
            
        except Exception as e:
            logger.error(f"❌ Error fetching Twelve Data news: {e}")
            return []
    
    def get_stock_data(self, symbol: str, interval: str = "1day", outputsize: int = 100) -> pd.DataFrame:
        """Get stock price data"""
        try:
            data = self._make_request("/time_series", {
                "symbol": symbol,
                "interval": interval,
                "outputsize": outputsize,
                "format": "json"
            })
            
            if data and 'values' in data:
                df = pd.DataFrame(data['values'])
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                
                # Convert price columns to float
                price_columns = ['open', 'high', 'low', 'close', 'volume']
                for col in price_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                logger.info(f"✅ Retrieved {len(df)} data points for {symbol}")
                return df.sort_index()
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"❌ Error fetching stock data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_forex_data(self, symbol: str, interval: str = "1day", outputsize: int = 100) -> pd.DataFrame:
        """Get forex pair data"""
        try:
            data = self._make_request("/time_series", {
                "symbol": symbol,
                "interval": interval,
                "outputsize": outputsize,
                "format": "json"
            })
            
            if data and 'values' in data:
                df = pd.DataFrame(data['values'])
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                
                # Convert price columns to float
                price_columns = ['open', 'high', 'low', 'close']
                for col in price_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                logger.info(f"✅ Retrieved {len(df)} forex data points for {symbol}")
                return df.sort_index()
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"❌ Error fetching forex data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_crypto_data(self, symbol: str, interval: str = "1day", outputsize: int = 100) -> pd.DataFrame:
        """Get cryptocurrency data"""
        try:
            # Format crypto symbol for Twelve Data (e.g., BTC/USD)
            if 'USDT' in symbol:
                symbol = symbol.replace('USDT', '/USD')
            elif not '/' in symbol:
                symbol = f"{symbol}/USD"
            
            data = self._make_request("/time_series", {
                "symbol": symbol,
                "interval": interval,
                "outputsize": outputsize,
                "format": "json"
            })
            
            if data and 'values' in data:
                df = pd.DataFrame(data['values'])
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                
                # Convert price columns to float
                price_columns = ['open', 'high', 'low', 'close', 'volume']
                for col in price_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                logger.info(f"✅ Retrieved {len(df)} crypto data points for {symbol}")
                return df.sort_index()
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"❌ Error fetching crypto data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_real_time_price(self, symbol: str) -> Optional[Dict]:
        """Get real-time price for a symbol"""
        try:
            data = self._make_request("/price", {"symbol": symbol})
            
            if data and 'price' in data:
                return {
                    'symbol': symbol,
                    'price': float(data['price']),
                    'timestamp': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error fetching real-time price for {symbol}: {e}")
            return None
    
    def get_supported_stocks(self) -> List[Dict]:
        """Get list of supported stocks"""
        try:
            data = self._make_request("/stocks")
            
            if data and 'data' in data:
                return data['data']
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Error fetching supported stocks: {e}")
            return []
    
    def get_supported_forex_pairs(self) -> List[Dict]:
        """Get list of supported forex pairs"""
        try:
            data = self._make_request("/forex_pairs")
            
            if data and 'data' in data:
                return data['data']
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Error fetching supported forex pairs: {e}")
            return []
    
    def _format_time(self, datetime_str: str) -> str:
        """Format datetime string to relative time"""
        try:
            if not datetime_str:
                return "Il y a quelques instants"
            
            # Parse the datetime
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo)
            diff = now - dt
            
            if diff.days > 0:
                return f"Il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"Il y a {hours} heure{'s' if hours > 1 else ''}"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"Il y a {minutes} minute{'s' if minutes > 1 else ''}"
            else:
                return "Il y a quelques instants"
                
        except Exception:
            return "Il y a quelques instants"

# Global instance - sera configurée par RealDataManager
twelve_data_api = TwelveDataAPI("1f192cc6b3634b6bbb6777b8ef708b08")  # Clé directe depuis config