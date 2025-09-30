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
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import json

# Import pour la traduction
try:
    from googletrans import Translator
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False
    print("⚠️ Traduction non disponible: googletrans non installé")

# Import pour récupération de contenu web
try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False
    print("⚠️ Web scraping non disponible: requests ou beautifulsoup4 non installés")

class NewsModule(BaseMarketModule):
    """News module using Alpha Vantage API for economic news and events"""
    
    def __init__(self, calculators: Dict = None):
        # Get Alpha Vantage API key from config
        news_provider = api_config.get_provider('news', 'Alpha Vantage News')
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
        
    def fetch_full_article_content(self, url: str) -> str:
        """
        Récupère le contenu complet d'un article depuis son URL
        """
        if not WEB_SCRAPING_AVAILABLE:
            return "Contenu complet non disponible (web scraping non configuré)"
        
        # Vérifier si l'URL est valide
        if not url or url == '#' or url == '' or not url.startswith(('http://', 'https://')):
            return "URL de l'article non disponible. Seul le résumé peut être affiché."
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Supprimer les éléments indésirables
            for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
                element.decompose()
            
            # Chercher le contenu principal dans différentes balises communes
            content_selectors = [
                'article',
                '.article-body',
                '.content',
                '.post-content',
                '.entry-content',
                'main',
                '[role="main"]'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0].get_text(strip=True)
                    break
            
            # Si aucun sélecteur spécifique ne fonctionne, prendre tous les paragraphes
            if not content:
                paragraphs = soup.find_all('p')
                content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
            
            # Nettoyer et limiter le contenu
            if content:
                # Supprimer les espaces multiples et les sauts de ligne excessifs
                import re
                content = re.sub(r'\s+', ' ', content)
                content = re.sub(r'\n\s*\n', '\n\n', content)
                
                # Limiter à 3000 caractères pour éviter les modales trop longues
                if len(content) > 3000:
                    content = content[:3000] + "..."
                
                return content
            else:
                return "Impossible d'extraire le contenu de cet article."
                
        except requests.RequestException as e:
            return f"Erreur lors de la récupération de l'article: {str(e)}"
        except Exception as e:
            return f"Erreur lors du traitement de l'article: {str(e)}"
    
    def refresh_api_config(self):
        """Refresh API configuration - useful when API keys are updated"""
        news_provider = api_config.get_provider('news', 'Alpha Vantage News')
        api_key = news_provider['config'].get('api_key', '') if news_provider else ''
        self.data_provider.api_key = api_key
        print(f"🔄 News API config refreshed: {'✅ Key loaded' if api_key else '❌ No key'}")
    
    def translate_to_french(self, text: str) -> str:
        """Translate text to French using Google Translate"""
        if not TRANSLATION_AVAILABLE:
            return text
        
        try:
            translator = Translator()
            result = translator.translate(text, dest='fr')
            return result.text
        except Exception as e:
            print(f"⚠️ Erreur de traduction: {e}")
            return text
    
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
            # Refresh API configuration to get latest API key
            self.refresh_api_config()
            
            print(f"🔄 Loading news data for category: {category}...")
            news_list = self.data_provider.get_economic_news(limit=limit)
            
            if news_list and len(news_list) > 0:
                # Convert list of news items to DataFrame
                news_data = pd.DataFrame(news_list)
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
            ]),
            
            # Modal pour l'affichage détaillé des articles
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(id="news-modal-title"), close_button=True),
                dbc.ModalBody([
                    html.Div(id="news-modal-content", style={"min-height": "400px"})
                ]),
                dbc.ModalFooter([
                    dbc.Button("🔗 Lire la source originale", id="news-modal-source-btn", 
                               color="primary", size="sm", external_link=True, className="me-2"),
                    dbc.Button("Fermer", id="news-modal-close", color="secondary", size="sm")
                ])
            ], id="news-modal", size="lg", scrollable=True),
            
            # Store pour les données d'articles
            dcc.Store(id="news-articles-store", data=[])
        ])
    
    def create_news_feed(self, news_data: pd.DataFrame, sentiment_filter: str = 'all') -> tuple:
        """Create news feed component and return HTML + data"""
        if news_data.empty:
            return html.Div("No news data available", className="text-muted"), []
        
        # Filter by sentiment if needed
        if sentiment_filter != 'all':
            if sentiment_filter == 'positive':
                news_data = news_data[news_data['sentiment_score'] > 0.6]
            elif sentiment_filter == 'negative':
                news_data = news_data[news_data['sentiment_score'] < 0.4]
            else:  # neutral
                news_data = news_data[(news_data['sentiment_score'] >= 0.4) & 
                                     (news_data['sentiment_score'] <= 0.6)]
        
        # Store articles data for modal access
        articles_data = []
        
        # Create news items
        news_items = []
        for idx, (_, article) in enumerate(news_data.head(20).iterrows()):
            # Store article data
            articles_data.append({
                'title': article.get('title', ''),
                'summary': article.get('summary', ''),
                'url': article.get('url', ''),
                'source': article.get('source', 'Unknown'),
                'time_published': article.get('time_published', ''),
                'sentiment_score': article.get('sentiment_score', 0.5),
                'sentiment_label': article.get('sentiment_label', 'Neutral')
            })
            
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
                        html.Div([
                            dbc.Button("📖 Lire l'article", size="sm", color="outline-primary", 
                                     id={"type": "news-read-btn", "index": idx}, className="me-2"),
                            # Afficher le bouton Source seulement si l'URL est valide
                            *([dbc.Button("🔗 Source", size="sm", color="outline-secondary", 
                                        href=article.get('url', '#'), target="_blank")] 
                              if article.get('url') and article.get('url') != '#' and article.get('url').startswith(('http://', 'https://'))
                              else [])
                        ])
                    ])
                ])
            ], className="mb-3")
            
            news_items.append(news_item)
        
        return html.Div(news_items), articles_data
    
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
        """Create economic calendar widget with current dates"""
        from datetime import datetime, timedelta
        
        # Get current date and generate events for the coming weeks
        today = datetime.now()
        
        # Create realistic upcoming economic events with current dates
        events = [
            {
                'date': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
                'event': 'Unemployment Rate',
                'impact': 'High',
                'time': '08:30 EST'
            },
            {
                'date': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
                'event': 'Consumer Price Index (CPI)',
                'impact': 'High',
                'time': '08:30 EST'
            },
            {
                'date': (today + timedelta(days=5)).strftime('%Y-%m-%d'),
                'event': 'Federal Reserve Meeting',
                'impact': 'High',
                'time': '14:00 EST'
            },
            {
                'date': (today + timedelta(days=7)).strftime('%Y-%m-%d'),
                'event': 'GDP Growth Rate',
                'impact': 'High',
                'time': '08:30 EST'
            },
            {
                'date': (today + timedelta(days=10)).strftime('%Y-%m-%d'),
                'event': 'Producer Price Index (PPI)',
                'impact': 'Medium',
                'time': '08:30 EST'
            },
            {
                'date': (today + timedelta(days=12)).strftime('%Y-%m-%d'),
                'event': 'Retail Sales',
                'impact': 'Medium',
                'time': '08:30 EST'
            },
            {
                'date': (today + timedelta(days=14)).strftime('%Y-%m-%d'),
                'event': 'Industrial Production',
                'impact': 'Medium',
                'time': '09:15 EST'
            },
            {
                'date': (today + timedelta(days=17)).strftime('%Y-%m-%d'),
                'event': 'Consumer Confidence Index',
                'impact': 'Low',
                'time': '10:00 EST'
            }
        ]
        
        event_items = []
        for event in events:
            impact_color = {
                'High': 'danger',
                'Medium': 'warning',
                'Low': 'success'
            }.get(event['impact'], 'secondary')
            
            # Calculate days from today
            event_date = datetime.strptime(event['date'], '%Y-%m-%d')
            days_diff = (event_date - today).days
            
            if days_diff == 0:
                date_display = "Aujourd'hui"
            elif days_diff == 1:
                date_display = "Demain"
            else:
                date_display = f"Dans {days_diff} jours"
            
            event_item = html.Div([
                html.Div([
                    html.Div([
                        html.Strong(event['event']),
                        html.Br(),
                        html.Small(f"{event['time']}", className="text-muted")
                    ]),
                    html.Div([
                        dbc.Badge(event['impact'], color=impact_color, className="mb-1"),
                        html.Br(),
                        html.Small(date_display, className="text-info")
                    ], className="text-end")
                ], className="d-flex justify-content-between align-items-start"),
                html.Hr(className="my-2")
            ], className="mb-2")
            
            event_items.append(event_item)
        
        return html.Div([
            html.H6("📅 Événements à venir", className="mb-3"),
            html.Div(event_items, style={"max-height": "400px", "overflow-y": "auto"})
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
    
    def get_article_data(self, article_index: int, news_data: pd.DataFrame) -> Dict:
        """Get article data for modal display"""
        if article_index >= len(news_data):
            return {}
        
        article = news_data.iloc[article_index]
        return {
            'title': article.get('title', ''),
            'summary': article.get('summary', ''),
            'url': article.get('url', ''),
            'source': article.get('source', 'Unknown'),
            'time_published': article.get('time_published', ''),
            'sentiment_score': article.get('sentiment_score', 0),
            'sentiment_label': article.get('sentiment_label', 'Neutral')
        }
    
    def create_article_modal_content(self, article_data: Dict, translate: bool = True) -> html.Div:
        """Create content for article modal with optional translation and full content"""
        if not article_data:
            return html.Div("Article non trouvé", className="text-muted")
        
        # Récupération du contenu complet de l'article
        article_url = article_data.get('url', '')
        full_content = self.fetch_full_article_content(article_url) if article_url else "URL de l'article non disponible"
        
        # Vérifier si le contenu complet est disponible
        content_available = (full_content and 
                           "non disponible" not in full_content and 
                           "Erreur" not in full_content and
                           "URL invalide" not in full_content)
        
        # Traduction en français si demandée
        title = article_data['title']
        summary = article_data['summary']
        
        if translate and TRANSLATION_AVAILABLE:
            try:
                title_fr = self.translate_to_french(title)
                summary_fr = self.translate_to_french(summary)
                # Traduire aussi le contenu complet si disponible et pas trop long
                if content_available and len(full_content) < 2000:
                    full_content_fr = self.translate_to_french(full_content)
                else:
                    full_content_fr = full_content
            except:
                title_fr = title
                summary_fr = summary
                full_content_fr = full_content
        else:
            title_fr = title
            summary_fr = summary
            full_content_fr = full_content
        
        # Analyse du sentiment
        sentiment_score = article_data.get('sentiment_score', 0)
        if sentiment_score > 0.6:
            sentiment_color = "success"
            sentiment_text = "🟢 Positif"
        elif sentiment_score < 0.4:
            sentiment_color = "danger" 
            sentiment_text = "🔴 Négatif"
        else:
            sentiment_color = "secondary"
            sentiment_text = "🟡 Neutre"
        
        # Formatage de la date
        try:
            time_published = pd.to_datetime(article_data['time_published'], format='%Y%m%dT%H%M%S')
            date_formatted = time_published.strftime("%d/%m/%Y à %H:%M")
        except:
            date_formatted = "Date inconnue"
        
        return html.Div([
            # Header avec métadonnées
            dbc.Row([
                dbc.Col([
                    dbc.Badge(article_data.get('source', 'Source inconnue'), 
                              color="info", className="me-2"),
                    dbc.Badge(sentiment_text, color=sentiment_color, className="me-2"),
                    html.Small(f"Publié le {date_formatted}", className="text-muted")
                ], width=12)
            ], className="mb-3"),
            
            # Contenu principal
            html.Div([
                html.H5(title_fr, className="mb-3"),
                html.P(summary_fr, className="lead text-justify mb-4"),
                
                # Contenu complet de l'article
                html.Hr(),
                html.H6("📖 Article complet", className="mb-3"),
                html.Div([
                    html.P(full_content_fr, 
                          className="text-justify" if content_available else "text-muted fst-italic", 
                          style={"line-height": "1.6"})
                ], className="mb-4", 
                  style={
                      "max-height": "400px", 
                      "overflow-y": "auto", 
                      "border": "1px solid #dee2e6", 
                      "border-radius": "0.375rem", 
                      "padding": "15px", 
                      "background-color": "#f8f9fa" if content_available else "#fff3cd"
                  }),
                
                # Section traduction
                html.Hr(),
                dbc.Accordion([
                    dbc.AccordionItem([
                        html.Div([
                            html.H6("Titre original :", className="mb-2"),
                            html.P(title, className="text-muted mb-3"),
                            html.H6("Résumé original :", className="mb-2"), 
                            html.P(summary, className="text-muted"),
                            html.H6("Contenu original :", className="mb-2"),
                            html.P(full_content if content_available else "Contenu original non disponible", 
                                   className="text-muted", 
                                   style={"max-height": "300px", "overflow-y": "auto"})
                        ])
                    ], title="📄 Version originale (anglais)", item_id="original-text")
                ], start_collapsed=True, className="mb-3"),
                
                # Analyse de sentiment détaillée
                html.Hr(),
                dbc.Card([
                    dbc.CardHeader(html.H6("📊 Analyse de sentiment", className="mb-0")),
                    dbc.CardBody([
                        html.Div([
                            html.Span("Score: ", className="fw-bold"),
                            html.Span(f"{sentiment_score:.2f}/1.0", className="me-3"),
                            dbc.Progress(
                                value=abs(sentiment_score) * 100,
                                color=sentiment_color,
                                style={"height": "20px"},
                                className="mb-2"
                            ),
                            html.Small(
                                f"Impact potentiel sur les marchés : {'Élevé' if abs(sentiment_score) > 0.7 else 'Modéré' if abs(sentiment_score) > 0.4 else 'Faible'}",
                                className="text-muted"
                            )
                        ])
                    ])
                ], className="mb-3")
            ])
        ])