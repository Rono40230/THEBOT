"""
CryptoPanic API Module for THEBOT
Provides cryptocurrency news and sentiment analysis
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class CryptoPanicAPI:
    """CryptoPanic API client for crypto news and sentiment"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://cryptopanic.com/api/v1"
        self.rate_limit_calls = 0
        self.rate_limit_reset = datetime.now()
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with rate limiting"""
        # Rate limiting: 1000 calls per day for free tier
        current_time = datetime.now()
        if current_time - self.rate_limit_reset > timedelta(days=1):
            self.rate_limit_calls = 0
            self.rate_limit_reset = current_time
            
        if self.rate_limit_calls >= 950:  # Leave some margin
            print("⏱️ CryptoPanic rate limit reached for today")
            return {}
        
        try:
            url = f"{self.base_url}{endpoint}"
            if params is None:
                params = {}
            
            if self.api_key:
                params['auth_token'] = self.api_key
            
            response = requests.get(url, params=params, timeout=10)
            self.rate_limit_calls += 1
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ CryptoPanic API error: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ CryptoPanic request error: {e}")
            return {}
    
    def get_news(self, currencies: List[str] = None, limit: int = 20) -> List[Dict]:
        """Get cryptocurrency news from CryptoPanic"""
        print(f"📰 Fetching CryptoPanic news...")
        
        try:
            params = {
                'kind': 'news',
                'limit': min(limit, 50),  # API max limit
                'public': 'true'
            }
            
            # Add currency filter if specified
            if currencies:
                params['currencies'] = ','.join(currencies[:10])  # Limit to 10 currencies
            
            data = self._make_request('/posts/', params)
            
            if not data or 'results' not in data:
                print("❌ No CryptoPanic data received")
                return self._get_fallback_news(limit)
            
            news_items = []
            for post in data['results']:
                # Parse published date
                published_date = datetime.now()
                if post.get('published_at'):
                    try:
                        published_date = datetime.fromisoformat(
                            post['published_at'].replace('Z', '+00:00')
                        )
                    except:
                        pass
                
                # Extract currencies mentioned
                currencies_mentioned = []
                if post.get('currencies'):
                    currencies_mentioned = [c.get('code', '') for c in post['currencies']]
                
                news_item = {
                    'title': post.get('title', 'CryptoPanic News'),
                    'description': post.get('description', '')[:500] + '...' if len(post.get('description', '')) > 500 else post.get('description', ''),
                    'url': post.get('url', ''),
                    'published_at': published_date.isoformat(),
                    'source': post.get('source', {}).get('title', 'CryptoPanic'),
                    'category': 'crypto',
                    'symbol': currencies_mentioned[0] if currencies_mentioned else None,
                    'currencies': currencies_mentioned,
                    'sentiment': self._analyze_sentiment(post),
                    'votes': {
                        'negative': post.get('votes', {}).get('negative', 0),
                        'positive': post.get('votes', {}).get('positive', 0),
                        'important': post.get('votes', {}).get('important', 0)
                    }
                }
                
                news_items.append(news_item)
            
            print(f"✅ Retrieved {len(news_items)} news items from CryptoPanic")
            return news_items
            
        except Exception as e:
            print(f"❌ CryptoPanic news error: {e}")
            return self._get_fallback_news(limit)
    
    def _analyze_sentiment(self, post: Dict) -> str:
        """Analyze sentiment from CryptoPanic post data"""
        votes = post.get('votes', {})
        positive = votes.get('positive', 0)
        negative = votes.get('negative', 0)
        
        if positive > negative:
            return 'positive'
        elif negative > positive:
            return 'negative'
        else:
            return 'neutral'
    
    def _get_fallback_news(self, limit: int) -> List[Dict]:
        """Provide fallback news when API fails"""
        return [
            {
                'title': 'CryptoPanic - Cryptocurrency News Platform',
                'description': 'CryptoPanic aggregates cryptocurrency news from various sources with community sentiment analysis.',
                'url': 'https://cryptopanic.com',
                'published_at': datetime.now().isoformat(),
                'source': 'CryptoPanic',
                'category': 'crypto',
                'symbol': None,
                'currencies': [],
                'sentiment': 'neutral',
                'votes': {'negative': 0, 'positive': 0, 'important': 0}
            },
            {
                'title': 'Real-time Crypto Sentiment Analysis',
                'description': 'Track cryptocurrency market sentiment through community-driven news aggregation and voting.',
                'url': 'https://cryptopanic.com',
                'published_at': (datetime.now() - timedelta(hours=1)).isoformat(),
                'source': 'CryptoPanic',
                'category': 'crypto',
                'symbol': None,
                'currencies': [],
                'sentiment': 'neutral',
                'votes': {'negative': 0, 'positive': 0, 'important': 0}
            }
        ][:limit]
    
    def get_trending_currencies(self) -> List[Dict]:
        """Get trending cryptocurrencies"""
        try:
            data = self._make_request('/posts/', {'kind': 'news', 'limit': 50})
            
            if not data or 'results' not in data:
                return []
            
            # Count currency mentions
            currency_counts = {}
            for post in data['results']:
                if post.get('currencies'):
                    for currency in post['currencies']:
                        code = currency.get('code', '')
                        if code:
                            currency_counts[code] = currency_counts.get(code, 0) + 1
            
            # Sort by mentions and return top trending
            trending = sorted(currency_counts.items(), key=lambda x: x[1], reverse=True)
            
            return [{'currency': code, 'mentions': count} for code, count in trending[:10]]
            
        except Exception as e:
            print(f"❌ Error getting trending currencies: {e}")
            return []


# Global instance
crypto_panic_api = CryptoPanicAPI()