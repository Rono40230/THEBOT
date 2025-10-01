"""
News Module for THEBOT
Handles economic news and market events using multiple data providers
"""

from .base_market_module import BaseMarketModule
from ..data_providers.real_data_manager import real_data_manager
from ..core.api_config import api_config
import pandas as pd
from typing import List, Dict
from datetime import datetime, timedelta
import dash
from dash import dcc, html, callback, Input, Output, State, ALL
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
    """News module using multiple data providers for comprehensive news coverage"""
    
    def __init__(self, calculators: Dict = None):
        super().__init__(
            market_type='news',
            data_provider=real_data_manager,
            calculators=calculators
        )
        
        self.news_categories = [
            'All News', 'Market News', 'Economic Indicators', 'Central Banks',
            'Earnings', 'Commodities', 'Technology', 'Financial', 'Energy'
        ]
        
        # Ajout pour compatibilité avec la nouvelle architecture
        self.translator = None
        if TRANSLATION_AVAILABLE:
            try:
                self.translator = Translator()
            except Exception as e:
                print(f"⚠️ Erreur initialisation traducteur: {e}")
    
    def get_layout(self):
        """Layout complet pour le module News"""
        return html.Div([
            
            # Hidden inputs to keep callbacks working
            dcc.Store(id='news-category-dropdown', data='All News'),
            dcc.Store(id='news-time-range', data='24h'),
            dcc.Store(id='sentiment-filter', data='all'),
            
            # Layout principal avec 3 colonnes
            dbc.Row([
                
                # Colonne 1: Feed d'actualités
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-rss me-2"),
                            "Feed d'Actualités"
                        ]),
                        dbc.CardBody([
                            html.Div(id='news-feed-content', children=[
                                html.Div("Chargement des actualités...", className="text-center p-4")
                            ])
                        ])
                    ], className="h-100")
                ], width=5),
                
                # Colonne 2: Impact Marché
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-line me-2"),
                            "Impact Marché"
                        ]),
                        dbc.CardBody([
                            html.Div(id='market-impact-content', children=[
                                html.Div("Chargement de l'analyse d'impact...", className="text-center p-4")
                            ])
                        ])
                    ], className="h-100")
                ], width=3),
                
                # Colonne 3: Calendrier Économique
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-calendar-alt me-2"),
                            "Calendrier Économique"
                        ]),
                        dbc.CardBody([
                            html.Div(id='economic-calendar-content', children=[
                                html.Div("Chargement du calendrier...", className="text-center p-4")
                            ])
                        ])
                    ], className="h-100")
                ], width=4)
                
            ], style={'minHeight': '600px'}),
            
            # Modal pour affichage des articles complets
            dbc.Modal([
                dbc.ModalHeader([
                    dbc.ModalTitle(id="news-modal-title")
                ]),
                dbc.ModalBody([
                    html.Div(id="news-modal-content")
                ]),
                dbc.ModalFooter([
                    dbc.Button([
                        html.I(className="fas fa-external-link-alt me-2"),
                        "Lire l'article complet"
                    ], id="news-modal-source-btn", color="primary", target="_blank"),
                    dbc.Button("Fermer", id="news-modal-close", color="secondary")
                ])
            ], id="news-modal", size="lg", scrollable=True),
            
            # Store pour les données des articles
            dcc.Store(id='news-articles-store', data=[])
            
        ], className="p-4")
        
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
    
    def load_market_data(self, category: str = 'All News', time_range: str = '24h', limit: int = 50) -> pd.DataFrame:
        """Load economic news data from Alpha Vantage with time filtering"""
        # Load the news data
        news_data = self.load_news_data(category, limit)
        
        # Apply time filtering
        if not news_data.empty and 'time_published' in news_data.columns:
            news_data = self._filter_by_time_range(news_data, time_range)
        
        return news_data
    
    def load_news_data(self, category: str = 'All News', limit: int = 50) -> pd.DataFrame:
        """Load economic news data from multiple providers via real_data_manager"""
        try:
            print(f"🔄 Loading news data for category: {category}...")
            
            # Utiliser real_data_manager pour récupérer les news de tous les providers
            news_list = self.data_provider.get_news_data(limit=limit)
            
            if news_list and len(news_list) > 0:
                # Convert list of news items to DataFrame
                news_data = pd.DataFrame(news_list)
                
                # Apply category filtering only if not "All News"
                if category != 'All News':
                    original_count = len(news_data)
                    filtered_data = self._filter_by_category(news_data, category)
                    # If filtering found articles, use them; otherwise keep original
                    if len(filtered_data) > 0:
                        news_data = filtered_data
                        print(f"✅ Category filter applied: {original_count} → {len(news_data)} articles")
                    else:
                        print(f"⚠️ No articles found for category '{category}', showing all articles")
                
                print(f"✅ {category}: {len(news_data)} news articles loaded from multiple providers")
                return news_data
            else:
                print(f"❌ No news data available from providers for {category}")
                return pd.DataFrame()  # Return empty DataFrame instead of fallback
                
        except Exception as e:
            print(f"❌ Error loading news data for {category}: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()  # Return empty DataFrame instead of fallback
    
    def _filter_by_time_range(self, data: pd.DataFrame, time_range: str) -> pd.DataFrame:
        """Filter news data by time range"""
        if time_range == "all" or not time_range:
            return data
        
        try:
            # Check for time_published (Alpha Vantage) or published column
            time_col = None
            if 'time_published' in data.columns:
                time_col = 'time_published'
            elif 'published' in data.columns:
                time_col = 'published'
            else:
                print("⚠️ No time column found, returning unfiltered data")
                return data
            
            # Convert time column to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(data[time_col]):
                data[time_col] = pd.to_datetime(data[time_col], errors='coerce')
            
            # Get current time and calculate cutoff
            now = pd.Timestamp.now()
            
            if time_range == "6h":
                cutoff = now - pd.Timedelta(hours=6)
            elif time_range == "24h":
                cutoff = now - pd.Timedelta(hours=24)
            elif time_range == "3d":
                cutoff = now - pd.Timedelta(days=3)
            elif time_range == "7d":
                cutoff = now - pd.Timedelta(days=7)
            elif time_range == "30d":
                cutoff = now - pd.Timedelta(days=30)
            else:
                print(f"⚠️ Unknown time range: {time_range}, returning unfiltered data")
                return data
            
            # Filter data
            filtered_data = data[data[time_col] >= cutoff]
            print(f"🕒 Filtered {len(data)} articles to {len(filtered_data)} articles for time range: {time_range}")
            
            return filtered_data
            
        except Exception as e:
            print(f"❌ Error filtering by time range {time_range}: {e}")
            return data
    
    def _filter_by_category(self, data: pd.DataFrame, category: str) -> pd.DataFrame:
        """Filter news data by category based on keywords and topics"""
        try:
            # Category keyword mapping - more comprehensive and flexible
            category_keywords = {
                'Market News': ['market', 'stock', 'trading', 'index', 'equity', 'share', 'portfolio', 'investor', 'wall street', 'nasdaq', 'dow', 'sp500', 'bull', 'bear'],
                'Economic Indicators': ['gdp', 'inflation', 'unemployment', 'cpi', 'ppi', 'employment', 'economic', 'indicator', 'growth', 'recession', 'economy', 'fiscal'],
                'Central Banks': ['fed', 'federal reserve', 'ecb', 'central bank', 'interest rate', 'monetary policy', 'boe', 'boj', 'rate hike', 'rate cut', 'powell', 'fomc'],
                'Earnings': ['earnings', 'revenue', 'profit', 'quarterly', 'annual report', 'eps', 'guidance', 'results', 'beat', 'miss', 'outlook'],
                'Commodities': ['oil', 'gold', 'silver', 'commodity', 'crude', 'natural gas', 'copper', 'agricultural', 'wheat', 'corn', 'precious metals'],
                'Technology': ['tech', 'technology', 'ai', 'artificial intelligence', 'software', 'hardware', 'semiconductor', 'apple', 'microsoft', 'google', 'amazon'],
                'Financial': ['bank', 'financial', 'credit', 'lending', 'mortgage', 'insurance', 'fintech', 'jpmorgan', 'goldman', 'wells fargo'],
                'Energy': ['energy', 'oil', 'gas', 'renewable', 'solar', 'wind', 'electricity', 'power', 'exxon', 'chevron', 'bp']
            }
            
            if category not in category_keywords:
                print(f"⚠️ Unknown category: {category}, returning unfiltered data")
                return data
            
            # Get keywords for the category
            keywords = category_keywords[category]
            
            # Filter by checking title and summary for keywords (case insensitive)
            mask = pd.Series([False] * len(data), index=data.index)
            
            for idx, row in data.iterrows():
                text_to_search = ""
                
                # Combine title, summary and topics for keyword search
                for col in ['title', 'summary', 'topics', 'overall_sentiment_label']:
                    if col in row and pd.notna(row[col]):
                        text_to_search += str(row[col]).lower() + " "
                
                # Check if any keyword matches (more flexible matching)
                for keyword in keywords:
                    if keyword.lower() in text_to_search:
                        mask[idx] = True
                        break
            
            filtered_data = data[mask]
            print(f"📂 Filtered {len(data)} articles to {len(filtered_data)} articles for category: {category}")
            
            return filtered_data
            
        except Exception as e:
            print(f"❌ Error filtering by category {category}: {e}")
            return data
    

    
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
            return html.Div([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Aucune donnée d'actualités disponible"
                ], className="text-warning text-center p-4"),
                html.Small("Vérifiez votre configuration API ou vos limites de requêtes", 
                          className="text-muted d-block text-center")
            ]), []
        
        # Filter by sentiment if needed
        if sentiment_filter != 'all' and 'sentiment_score' in news_data.columns:
            print(f"🎯 Applying sentiment filter: {sentiment_filter}")
            original_count = len(news_data)
            
            if sentiment_filter == 'positive':
                news_data = news_data[news_data['sentiment_score'] > 0.6]
            elif sentiment_filter == 'negative':
                news_data = news_data[news_data['sentiment_score'] < 0.4]
            else:  # neutral
                news_data = news_data[(news_data['sentiment_score'] >= 0.4) & 
                                     (news_data['sentiment_score'] <= 0.6)]
            
            print(f"✅ Sentiment filter applied: {original_count} → {len(news_data)} articles")
        elif sentiment_filter != 'all':
            print("⚠️ No sentiment_score column found, skipping sentiment filter")
        
        # Store articles data for modal access
        articles_data = []
        
        # Create news items
        news_items = []
        for idx, (_, article) in enumerate(news_data.head(20).iterrows()):
            # Store article data
            articles_data.append({
                'title': article.get('title', ''),
                'summary': article.get('description', article.get('summary', '')),
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
                        html.P(article.get('description', article.get('summary', ''))[:200] + "...", className="card-text text-muted small"),
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
                                        href=article.get('url', '#'), target="_blank", className="me-2")] 
                              if article.get('url') and article.get('url') != '#' and article.get('url').startswith(('http://', 'https://'))
                              else []),
                            # Bouton avec source et date
                            dbc.Button(
                                f"{article.get('source', 'Unknown')} • {time_ago}",
                                size="sm", 
                                color="light", 
                                className="text-muted",
                                style={"cursor": "default", "pointer-events": "none"}
                            )
                        ])
                    ])
                ])
            ], className="mb-3")
            
            news_items.append(news_item)
        
        return html.Div(news_items), articles_data
    
    def create_market_impact_widget(self, news_data: pd.DataFrame) -> html.Div:
        """Create market impact analysis widget"""
        if news_data.empty:
            return html.Div([
                html.I(className="fas fa-chart-line-down me-2"),
                "Aucune donnée d'impact disponible"
            ], className="text-warning text-center p-4")
        
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
        """Create economic calendar widget using real API data only"""
        try:
            # Try to get real economic calendar data from API
            # For now, return a message indicating API-only mode
            return html.Div([
                html.Div([
                    html.I(className="fas fa-calendar-alt me-2"),
                    "Calendrier économique"
                ], className="text-info mb-3"),
                html.Div([
                    html.I(className="fas fa-info-circle me-2"),
                    "Mode API uniquement - Aucune donnée simulée"
                ], className="text-warning text-center p-4"),
                html.Small("Le calendrier économique nécessite une API dédiée", 
                          className="text-muted d-block text-center")
            ])
        except Exception as e:
            return html.Div([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "Erreur de chargement du calendrier"
            ], className="text-danger text-center p-4")
    
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
    
    def setup_callbacks(self, app):
        """Configurer les callbacks pour le module News"""
        
        @app.callback(
            [Output('news-feed-content', 'children'),
             Output('news-articles-store', 'data')],
            [Input('news-category-dropdown', 'data'),
             Input('news-time-range', 'data'),
             Input('sentiment-filter', 'data')]
        )
        def update_news_feed(category, time_range, sentiment):
            """Mettre à jour le feed d'actualités avec tous les filtres"""
            try:
                # Utiliser les valeurs par défaut si elles sont None
                category = category or 'All News'
                time_range = time_range or '24h'
                sentiment = sentiment or 'all'
                
                print(f"🔄 Updating news feed: category='{category}', time_range='{time_range}', sentiment='{sentiment}'")
                news_data = self.load_market_data(category, time_range)
                news_html, articles_data = self.create_news_feed(news_data, sentiment)
                print(f"✅ News feed updated: {len(articles_data)} articles")
                return news_html, articles_data
            except Exception as e:
                print(f"❌ Erreur callback news: {e}")
                import traceback
                traceback.print_exc()
                return html.Div(f"Erreur de chargement des actualités: {str(e)}", className="text-muted"), []
        
        @app.callback(
            Output('market-impact-content', 'children'),
            [Input('news-category-dropdown', 'data'),
             Input('news-time-range', 'data')]
        )
        def update_market_impact(category, time_range):
            """Mettre à jour l'analyse d'impact marché"""
            try:
                # Utiliser les valeurs par défaut si elles sont None
                category = category or 'All News'
                time_range = time_range or '24h'
                
                news_data = self.load_market_data(category, time_range)
                return self.create_market_impact_widget(news_data)
            except:
                return html.Div("Pas de données d'impact", className="text-muted")
        
        @app.callback(
            Output('economic-calendar-content', 'children'),
            [Input('main-tabs', 'active_tab')]
        )
        def update_economic_calendar(active_tab):
            """Mettre à jour le calendrier économique"""
            if active_tab == 'news':
                try:
                    return self.create_economic_calendar_widget()
                except:
                    return html.Div("Calendrier non disponible", className="text-muted")
            return html.Div()
        
        # Callbacks pour la modal d'article
        @app.callback(
            [Output("news-modal", "is_open"),
             Output("news-modal-title", "children"),
             Output("news-modal-content", "children"),
             Output("news-modal-source-btn", "href"),
             Output("news-modal-source-btn", "style")],
            [Input({"type": "news-read-btn", "index": ALL}, "n_clicks"),
             Input("news-modal-close", "n_clicks")],
            [State("news-modal", "is_open"),
             State("news-articles-store", "data")],
            prevent_initial_call=True
        )
        def handle_news_modal(read_clicks, close_clicks, is_open, articles_data):
            """Gérer l'ouverture/fermeture de la modal d'article"""
            ctx = dash.callback_context
            if not ctx.triggered:
                return False, "", "", "", {"display": "none"}
            
            trigger_id = ctx.triggered[0]["prop_id"]
            
            # Fermer la modal
            if "news-modal-close" in trigger_id:
                return False, "", "", "", {"display": "none"}
            
            # Ouvrir la modal avec un article
            if "news-read-btn" in trigger_id and any(read_clicks):
                try:
                    # Trouver quel bouton a été cliqué
                    clicked_index = None
                    for i, clicks in enumerate(read_clicks):
                        if clicks:
                            clicked_index = i
                            break
                    
                    if clicked_index is not None and articles_data and clicked_index < len(articles_data):
                        article = articles_data[clicked_index]
                        modal_content = self.create_article_modal_content(article, translate=True)
                        
                        # Vérifier si l'URL est valide
                        article_url = article.get('url', '#')
                        button_style = {"display": "none"} if (not article_url or article_url == '#' or not article_url.startswith(('http://', 'https://'))) else {}
                        
                        return (
                            True,
                            f"📰 {article.get('title', 'Article')[:60]}{'...' if len(article.get('title', '')) > 60 else ''}",
                            modal_content,
                            article_url,
                            button_style
                        )
                except Exception as e:
                    print(f"❌ Erreur modal: {e}")
                    return True, "Erreur", html.Div("Impossible de charger l'article"), "", {"display": "none"}
            
            return is_open, "", "", "", {"display": "none"}