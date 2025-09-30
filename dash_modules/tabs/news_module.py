"""
News Module for THEBOT
Handles economic news and market events using Alpha Vantage API
"""

from .base_market_module import BaseMarketModule
from ..data_providers.alpha_vantage_api import AlphaVantageAPI
from ..core.api_config import api_config
import pandas as pd
from typing import List, Dict
from datetime import datetime, timedelta
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

class NewsModule(BaseMarketModule):
    """News module using Alpha Vantage API for economic news and events"""
    
    def __init__(self, calculators: Dict = None):
        # Get Alpha Vantage API key from config
        news_provider = api_config.get_provider('news', 'Alpha Vantage')
        api_key = news_provider['config'].get('api_key', '') if news_provider else ''
        
        super().__init__(
            market_type='news',
            data_provider=AlphaVantageAPI(api_key),
            calculators=calculators
        )
        
        self.news_categories = [
            'All News', 'Market News', 'Economic Indicators', 'Central Banks',
            'Earnings', 'Commodities', 'Technology', 'Financial', 'Energy'
        ]
    
    def get_symbols_list(self) -> List[str]:
        """Get list of news categories"""
        return self.news_categories
    
    def get_default_symbol(self) -> str:
        """Get default news category"""
        return 'All News'
    
    def load_market_data(self, category: str = 'All News', interval: str = '1h', limit: int = 50) -> pd.DataFrame:
        """Load economic news data from Alpha Vantage"""
        # Alias pour la compatibilité avec BaseMarketModule
        return self.load_news_data(category, limit)
    
    def load_news_data(self, category: str = 'All News', limit: int = 50) -> pd.DataFrame:
        """Load economic news data from Alpha Vantage"""
        try:
            print(f"🔄 Loading news data for category: {category}...")
            news_data = self.data_provider.get_economic_news(topics=category.lower(), limit=limit)
            
            if not news_data.empty:
                print(f"✅ {category}: {len(news_data)} news articles loaded")
                return news_data
            else:
                print(f"⚠️ No news data for {category}, using fallback")
                return self._create_fallback_news_data(category)
                
        except Exception as e:
            print(f"❌ Error loading news data for {category}: {e}")
            return self._create_fallback_news_data(category)
    
    def _create_fallback_news_data(self, category: str) -> pd.DataFrame:
        """Create fallback news data when API unavailable"""
        print(f"📰 Creating fallback news data for {category}")
        
        # Generate realistic news headlines and content
        news_templates = {
            'Market News': [
                "Market rallies on positive economic data",
                "Stocks close mixed amid volatility concerns",
                "Tech sector leads market gains",
                "Energy stocks surge on oil price increase"
            ],
            'Economic Indicators': [
                "GDP growth exceeds expectations in Q4",
                "Inflation data shows cooling trend",
                "Employment numbers beat forecasts",
                "Consumer confidence index rises"
            ],
            'Central Banks': [
                "Federal Reserve signals rate pause",
                "ECB maintains monetary policy stance",
                "Bank of Japan considers policy adjustment",
                "Central bank coordination on global stability"
            ],
            'Earnings': [
                "Major tech companies report strong earnings",
                "Banking sector shows resilient profits",
                "Retail earnings reflect consumer strength",
                "Energy companies post record revenues"
            ],
            'Technology': [
                "AI breakthrough drives tech innovation",
                "Semiconductor demand remains strong",
                "Cloud computing growth accelerates",
                "Cybersecurity spending increases"
            ]
        }
        
        # Select templates based on category
        if category in news_templates:
            headlines = news_templates[category]
        else:
            # Mix all categories for 'All News'
            headlines = []
            for cat_headlines in news_templates.values():
                headlines.extend(cat_headlines[:2])
        
        # Generate news data
        news_data = []
        for i, headline in enumerate(headlines[:20]):  # Limit to 20 items
            news_time = datetime.now() - timedelta(hours=i*2)
            
            # Generate realistic news data
            news_item = {
                'time_published': news_time.strftime('%Y%m%dT%H%M%S'),
                'title': headline,
                'url': f'https://example-news.com/article-{i+1}',
                'summary': f'Detailed analysis of {headline.lower()}. Market impact and expert opinions...',
                'source': self._get_random_source(),
                'category_within_source': category,
                'sentiment_score': round(0.5 + (i % 3 - 1) * 0.3, 2),  # Vary between 0.2 and 0.8
                'relevance_score': round(0.8 - (i * 0.02), 2)  # Decrease relevance with time
            }
            news_data.append(news_item)
        
        df = pd.DataFrame(news_data)
        df['timestamp'] = pd.to_datetime(df['time_published'], format='%Y%m%dT%H%M%S')
        df.index = df['timestamp']
        
        return df
    
    def _get_random_source(self) -> str:
        """Get random news source"""
        sources = [
            'Reuters', 'Bloomberg', 'Financial Times', 'Wall Street Journal',
            'MarketWatch', 'CNBC', 'Yahoo Finance', 'Barrons'
        ]
        import random
        return random.choice(sources)
    
    def create_news_layout(self) -> html.Div:
        """Create news-specific layout"""
        return html.Div([
            # News controls
            dbc.Row([
                dbc.Col([
                    dbc.Label("News Category:", className="form-label"),
                    dcc.Dropdown(
                        id='news-category-dropdown',
                        options=[{'label': cat, 'value': cat} for cat in self.news_categories],
                        value='All News',
                        className="mb-3"
                    )
                ], width=4),
                dbc.Col([
                    dbc.Label("Time Range:", className="form-label"),
                    dcc.Dropdown(
                        id='news-time-range',
                        options=[
                            {'label': 'Last Hour', 'value': '1h'},
                            {'label': 'Last 4 Hours', 'value': '4h'},
                            {'label': 'Last 24 Hours', 'value': '24h'},
                            {'label': 'Last 3 Days', 'value': '3d'},
                            {'label': 'Last Week', 'value': '7d'}
                        ],
                        value='24h',
                        className="mb-3"
                    )
                ], width=4),
                dbc.Col([
                    dbc.Label("Sentiment Filter:", className="form-label"),
                    dcc.Dropdown(
                        id='sentiment-filter',
                        options=[
                            {'label': 'All Sentiment', 'value': 'all'},
                            {'label': 'Positive Only', 'value': 'positive'},
                            {'label': 'Negative Only', 'value': 'negative'},
                            {'label': 'Neutral Only', 'value': 'neutral'}
                        ],
                        value='all',
                        className="mb-3"
                    )
                ], width=4)
            ], className="mb-4"),
            
            # News feed
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("📰 Economic News Feed", className="mb-0")
                        ]),
                        dbc.CardBody([
                            html.Div(id='news-feed-content')
                        ])
                    ])
                ], width=8),
                
                # Market impact sidebar
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H6("📊 Market Impact", className="mb-0")
                        ]),
                        dbc.CardBody([
                            html.Div(id='market-impact-content')
                        ])
                    ], className="mb-3"),
                    
                    dbc.Card([
                        dbc.CardHeader([
                            html.H6("📅 Economic Calendar", className="mb-0")
                        ]),
                        dbc.CardBody([
                            html.Div(id='economic-calendar-content')
                        ])
                    ])
                ], width=4)
            ])
        ])
    
    def create_news_feed(self, news_data: pd.DataFrame, sentiment_filter: str = 'all') -> html.Div:
        """Create news feed component"""
        if news_data.empty:
            return html.Div("No news data available", className="text-muted")
        
        # Filter by sentiment if needed
        if sentiment_filter != 'all':
            if sentiment_filter == 'positive':
                news_data = news_data[news_data['sentiment_score'] > 0.6]
            elif sentiment_filter == 'negative':
                news_data = news_data[news_data['sentiment_score'] < 0.4]
            else:  # neutral
                news_data = news_data[(news_data['sentiment_score'] >= 0.4) & 
                                     (news_data['sentiment_score'] <= 0.6)]
        
        # Create news items
        news_items = []
        for _, article in news_data.head(20).iterrows():
            # Sentiment badge
            sentiment_score = article.get('sentiment_score', 0.5)
            if sentiment_score > 0.6:
                sentiment_badge = dbc.Badge("Positive", color="success", className="me-2")
            elif sentiment_score < 0.4:
                sentiment_badge = dbc.Badge("Negative", color="danger", className="me-2")
            else:
                sentiment_badge = dbc.Badge("Neutral", color="secondary", className="me-2")
            
            # Time ago calculation
            try:
                time_published = pd.to_datetime(article['time_published'], format='%Y%m%dT%H%M%S')
                time_ago = self._calculate_time_ago(time_published)
            except:
                time_ago = "Recently"
            
            news_item = dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H6(article['title'], className="card-title mb-2"),
                        html.P(article['summary'][:200] + "...", className="card-text text-muted small"),
                        html.Div([
                            sentiment_badge,
                            dbc.Badge(article.get('source', 'Unknown'), color="light", text_color="dark", className="me-2"),
                            html.Small(time_ago, className="text-muted")
                        ], className="d-flex align-items-center"),
                        html.Hr(className="my-2"),
                        dbc.Button("Read More", size="sm", color="outline-primary", 
                                 href=article.get('url', '#'), target="_blank")
                    ])
                ])
            ], className="mb-3")
            
            news_items.append(news_item)
        
        return html.Div(news_items)
    
    def create_market_impact_widget(self, news_data: pd.DataFrame) -> html.Div:
        """Create market impact analysis widget"""
        if news_data.empty:
            return html.Div("No impact data", className="text-muted")
        
        # Calculate sentiment distribution
        positive_count = len(news_data[news_data['sentiment_score'] > 0.6])
        negative_count = len(news_data[news_data['sentiment_score'] < 0.4])
        neutral_count = len(news_data) - positive_count - negative_count
        
        # Overall market sentiment
        avg_sentiment = news_data['sentiment_score'].mean()
        if avg_sentiment > 0.6:
            market_mood = ("Bullish", "success")
        elif avg_sentiment < 0.4:
            market_mood = ("Bearish", "danger")
        else:
            market_mood = ("Neutral", "warning")
        
        return html.Div([
            html.H6("Market Sentiment", className="mb-3"),
            dbc.Alert([
                html.Strong(f"Overall: {market_mood[0]}"),
                html.Br(),
                html.Small(f"Score: {avg_sentiment:.2f}/1.0")
            ], color=market_mood[1], className="mb-3"),
            
            html.H6("News Distribution", className="mb-2"),
            html.Div([
                dbc.Badge(f"Positive: {positive_count}", color="success", className="me-2 mb-2"),
                dbc.Badge(f"Neutral: {neutral_count}", color="secondary", className="me-2 mb-2"),
                dbc.Badge(f"Negative: {negative_count}", color="danger", className="mb-2")
            ]),
            
            html.Hr(),
            html.H6("Top Sources", className="mb-2"),
            html.Div([
                html.Small(source, className="d-block text-muted")
                for source in news_data['source'].value_counts().head(5).index
            ])
        ])
    
    def create_economic_calendar_widget(self) -> html.Div:
        """Create economic calendar widget"""
        # Mock economic events
        events = [
            {'date': '2024-01-15', 'event': 'Federal Reserve Meeting', 'impact': 'High'},
            {'date': '2024-01-18', 'event': 'GDP Release', 'impact': 'High'},
            {'date': '2024-01-22', 'event': 'Employment Data', 'impact': 'Medium'},
            {'date': '2024-01-25', 'event': 'Corporate Earnings', 'impact': 'Medium'},
            {'date': '2024-01-29', 'event': 'Consumer Confidence', 'impact': 'Low'}
        ]
        
        event_items = []
        for event in events:
            impact_color = {
                'High': 'danger',
                'Medium': 'warning',
                'Low': 'success'
            }.get(event['impact'], 'secondary')
            
            event_item = html.Div([
                html.Div([
                    html.Strong(event['event']),
                    dbc.Badge(event['impact'], color=impact_color, className="float-end")
                ], className="d-flex justify-content-between align-items-center"),
                html.Small(event['date'], className="text-muted")
            ], className="border-bottom pb-2 mb-2")
            
            event_items.append(event_item)
        
        return html.Div([
            html.H6("Upcoming Events", className="mb-3"),
            html.Div(event_items)
        ])
    
    def _calculate_time_ago(self, timestamp: datetime) -> str:
        """Calculate human-readable time ago"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    
    def get_news_analysis(self, news_data: pd.DataFrame) -> Dict:
        """Get news-specific analysis"""
        if news_data.empty:
            return {}
        
        return {
            'total_articles': len(news_data),
            'sentiment_breakdown': {
                'positive': len(news_data[news_data['sentiment_score'] > 0.6]),
                'neutral': len(news_data[(news_data['sentiment_score'] >= 0.4) & 
                                       (news_data['sentiment_score'] <= 0.6)]),
                'negative': len(news_data[news_data['sentiment_score'] < 0.4])
            },
            'top_sources': news_data['source'].value_counts().head(5).to_dict(),
            'average_sentiment': news_data['sentiment_score'].mean(),
            'recent_trend': self._analyze_sentiment_trend(news_data)
        }
    
    def _analyze_sentiment_trend(self, news_data: pd.DataFrame) -> str:
        """Analyze sentiment trend over time"""
        if len(news_data) < 10:
            return "Insufficient data"
        
        # Split into recent and older news
        mid_point = len(news_data) // 2
        recent_sentiment = news_data.head(mid_point)['sentiment_score'].mean()
        older_sentiment = news_data.tail(mid_point)['sentiment_score'].mean()
        
        diff = recent_sentiment - older_sentiment
        
        if diff > 0.1:
            return "Improving sentiment"
        elif diff < -0.1:
            return "Declining sentiment"
        else:
            return "Stable sentiment"