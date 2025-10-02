"""
Economic News Module for THEBOT
News économiques exclusivement alimentées par RSS avec widgets AI
"""

import dash
from dash import dcc, html, callback, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime, timedelta
import json
import re
from collections import Counter
import numpy as np

# Import RSS News Manager
try:
    from ..data_providers.rss_news_manager import rss_news_manager
    RSS_AVAILABLE = True
except ImportError:
    print("⚠️ RSS News Manager non disponible")
    RSS_AVAILABLE = False

# Import AI Engine
try:
    from ..ai_engine.smart_ai_manager import smart_ai_manager
    AI_AVAILABLE = True
except ImportError:
    print("⚠️ Smart AI Manager non disponible")
    AI_AVAILABLE = False

class EconomicNewsModule:
    """Module News Économiques alimenté exclusivement par RSS avec widgets AI complets"""
    
    def __init__(self, calculators: Dict = None):
        self.calculators = calculators or {}
        self.news_cache = []
        self.sentiment_cache = {}
        self.trending_cache = []
        self.last_update = None
        
        # Configuration économique
        self.economic_keywords = [
            'économie', 'économique', 'finance', 'financier', 'banque', 'bourse',
            'marché', 'action', 'obligation', 'taux', 'inflation', 'croissance',
            'pib', 'fed', 'bce', 'banque centrale', 'politique monétaire',
            'commerce', 'industrie', 'emploi', 'chômage', 'consommation',
            'economy', 'economic', 'finance', 'financial', 'banking', 'stock market',
            'market', 'stock', 'bond', 'rate', 'inflation', 'growth',
            'gdp', 'federal reserve', 'central bank', 'monetary policy',
            'trade', 'industry', 'employment', 'unemployment', 'consumption',
            'earnings', 'revenue', 'profit', 'dividend', 'treasury'
        ]
        
        self.exclude_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency',
            'altcoin', 'defi', 'nft', 'blockchain', 'mining'
        ]
        
        print("✅ Economic News Module initialisé (RSS exclusif)")
    
    def translate_article_title(self, title: str) -> str:
        """Traduire titre d'article en français"""
        try:
            if AI_AVAILABLE:
                translated = smart_ai_manager.translate_to_french(title)
                return translated if translated and len(translated) > 3 else title
            return title
        except Exception as e:
            print(f"⚠️ Erreur traduction titre: {e}")
            return title
    
    def translate_article_summary(self, summary: str) -> str:
        """Traduire résumé d'article en français"""
        try:
            if AI_AVAILABLE and len(summary) > 10:
                translated = smart_ai_manager.translate_to_french(summary)
                return translated if translated and len(translated) > 5 else summary
            return summary
        except Exception as e:
            print(f"⚠️ Erreur traduction résumé: {e}")
            return summary

    def get_rss_news(self, limit: int = 20) -> Dict:
        """Récupérer les news RSS économiques avec traduction"""
        try:
            if not RSS_AVAILABLE:
                return {'news': [], 'total': 0, 'source': 'RSS indisponible'}
            
            # Récupérer news RSS (utiliser toutes les catégories disponibles)
            rss_news = rss_news_manager.get_news(
                categories=None,  # Toutes les catégories
                limit=limit
            )
            
            if not rss_news:
                return {'news': [], 'total': 0, 'source': 'RSS'}
            
            # Normaliser le résultat RSS (peut être une liste ou un dict)
            if isinstance(rss_news, list):
                all_news = rss_news
            else:
                all_news = rss_news.get('articles', [])
            
            # Filtrer et enrichir pour économie
            economic_news = []
            
            for article in all_news:
                # Vérifier si pertinent pour économie
                title = (article.get('title', '') or '').lower()
                description = (article.get('description', '') or '').lower()
                content = f"{title} {description}"
                
                # Score de pertinence économique
                relevance_score = sum(1 for keyword in self.economic_keywords 
                                   if keyword in content)
                
                if relevance_score >= 1:  # Au moins 1 keyword économique
                    # Traduire titre et résumé
                    original_title = article.get('title', 'No Title')
                    original_summary = article.get('description', 'No summary')[:300]
                    
                    translated_title = self.translate_article_title(original_title)
                    translated_summary = self.translate_article_summary(original_summary)
                    
                    # Enrichir article
                    enriched_article = {
                        'title': translated_title,
                        'original_title': original_title,
                        'summary': translated_summary,
                        'original_summary': original_summary,
                        'source': article.get('source', 'RSS'),
                        'published_time': article.get('published_time', 'N/A'),
                        'url': article.get('url', '#'),
                        'relevance_score': relevance_score,
                        'category': 'economy'
                    }
                    
                    # Analyser sentiment avec IA si disponible
                    if AI_AVAILABLE:
                        sentiment_result = smart_ai_manager.analyze_with_best_ai({
                            'news_articles': [original_title + ' ' + original_summary]
                        }, task_type="sentiment")
                        
                        sentiment = sentiment_result.get('sentiment', 'neutral')
                        if sentiment == 'bullish':
                            enriched_article['sentiment'] = 'positive'
                        elif sentiment == 'bearish':
                            enriched_article['sentiment'] = 'negative'
                        else:
                            enriched_article['sentiment'] = 'neutral'
                        
                        enriched_article['sentiment_confidence'] = sentiment_result.get('confidence', 50)
                    else:
                        enriched_article['sentiment'] = 'neutral'
                        enriched_article['sentiment_confidence'] = 50
                    
                    economic_news.append(enriched_article)
            
            # Trier par pertinence puis par temps
            economic_news.sort(key=lambda x: (x['relevance_score'], x['published_time']), reverse=True)
            
            print(f"✅ {len(economic_news)} news économiques RSS récupérées (traduites)")
            
            return {
                'news': economic_news[:limit],
                'total': len(economic_news),
                'source': 'RSS',
                'categories': ['economy', 'business', 'finance']
            }
            
        except Exception as e:
            print(f"❌ Erreur récupération RSS économique: {e}")
            return {'news': [], 'total': 0, 'source': 'RSS Error'}
    
    def _is_economic_news(self, article: Dict) -> bool:
        """Déterminer si un article est économique"""
        text_to_check = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        # Vérifier présence de mots-clés économiques
        has_economic = any(keyword in text_to_check for keyword in self.economic_keywords)
        
        # Exclure crypto explicitement
        has_crypto = any(keyword in text_to_check for keyword in self.exclude_keywords)
        
        return has_economic and not has_crypto
    
    def _get_fallback_news(self) -> List[Dict]:
        """News simulées en cas d'échec RSS"""
        return [
            {
                'title': 'Fed Maintains Interest Rates at 5.25%',
                'summary': 'Federal Reserve keeps rates steady amid inflation concerns...',
                'published_time': datetime.now() - timedelta(hours=1),
                'source': 'RSS Economic Feed',
                'url': '#',
                'sentiment': 'neutral'
            },
            {
                'title': 'EU Economic Growth Slows to 0.1% in Q3',
                'summary': 'European economy shows signs of slowdown with GDP growth...',
                'published_time': datetime.now() - timedelta(hours=2),
                'source': 'RSS Economic Feed',
                'url': '#',
                'sentiment': 'negative'
            },
            {
                'title': 'Tech Stocks Rally on AI Innovation',
                'summary': 'Technology sector leads market gains as AI developments...',
                'published_time': datetime.now() - timedelta(hours=3),
                'source': 'RSS Economic Feed',
                'url': '#',
                'sentiment': 'positive'
            }
        ]
    
    def analyze_sentiment(self, articles: List[Dict]) -> Dict:
        """Analyser le sentiment des articles avec IA"""
        if not AI_AVAILABLE or not articles:
            return {'positive': 30, 'neutral': 50, 'negative': 20, 'confidence': 0.6}
        
        try:
            # Analyser avec Smart AI Manager
            sentiments = []
            for article in articles[:20]:  # Limiter pour performance
                text = f"{article.get('title', '')} {article.get('summary', '')}"
                if len(text.strip()) > 10:
                    result = smart_ai_manager.analyze_with_best_ai({'text': text}, 'sentiment')
                    sentiment = result.get('sentiment', 'neutral')
                    sentiments.append(sentiment)
            
            if not sentiments:
                return {'positive': 30, 'neutral': 50, 'negative': 20, 'confidence': 0.6}
            
            # Calculer distribution
            sentiment_counts = Counter(sentiments)
            total = len(sentiments)
            
            result = {
                'positive': round((sentiment_counts.get('positive', 0) / total) * 100, 1),
                'neutral': round((sentiment_counts.get('neutral', 0) / total) * 100, 1),
                'negative': round((sentiment_counts.get('negative', 0) / total) * 100, 1),
                'confidence': 0.85
            }
            
            self.sentiment_cache = result
            return result
            
        except Exception as e:
            print(f"❌ Erreur analyse sentiment: {e}")
            return {'positive': 30, 'neutral': 50, 'negative': 20, 'confidence': 0.6}
    
    def extract_trending_topics(self, articles: List[Dict]) -> List[Dict]:
        """Extraire les sujets tendance avec IA"""
        if not articles:
            return []
        
        try:
            # Extraire mots-clés de tous les titres
            all_text = ' '.join([article.get('title', '') for article in articles])
            
            # Compter les mots importants
            words = re.findall(r'\b[A-Za-zÀ-ÿ]{4,}\b', all_text.lower())
            word_counts = Counter(words)
            
            # Filtrer et créer sujets tendance
            trending = []
            for word, count in word_counts.most_common(10):
                if word in self.economic_keywords and count > 1:
                    trending.append({
                        'topic': word.title(),
                        'count': count,
                        'trend': 'up' if count > 2 else 'stable'
                    })
            
            self.trending_cache = trending[:8]  # Top 8
            return self.trending_cache
            
        except Exception as e:
            print(f"❌ Erreur trending topics: {e}")
            return []
    
    def calculate_fear_greed_index(self, articles: List[Dict], sentiment: Dict) -> Dict:
        """Calculer l'indice Fear & Greed pour l'économie"""
        try:
            # Facteurs économiques
            positive_pct = sentiment.get('positive', 30)
            negative_pct = sentiment.get('negative', 20)
            
            # Calcul basé sur sentiment et volume de news
            news_volume_factor = min(len(articles) / 20, 1.0)  # Normaliser
            sentiment_factor = (positive_pct - negative_pct) / 100
            
            # Score final (0-100)
            fear_greed_score = 50 + (sentiment_factor * 40) + (news_volume_factor * 10)
            fear_greed_score = max(0, min(100, fear_greed_score))
            
            # Classification
            if fear_greed_score >= 75:
                classification = "Extreme Greed"
                color = "#16a34a"
            elif fear_greed_score >= 55:
                classification = "Greed"
                color = "#22c55e"
            elif fear_greed_score >= 45:
                classification = "Neutral"
                color = "#eab308"
            elif fear_greed_score >= 25:
                classification = "Fear"
                color = "#f97316"
            else:
                classification = "Extreme Fear"
                color = "#dc2626"
            
            return {
                'score': round(fear_greed_score, 1),
                'classification': classification,
                'color': color,
                'confidence': sentiment.get('confidence', 0.7)
            }
            
        except Exception as e:
            print(f"❌ Erreur Fear & Greed: {e}")
            return {
                'score': 50.0,
                'classification': 'Neutral',
                'color': '#eab308',
                'confidence': 0.5
            }
    
    def get_layout(self) -> html.Div:
        """Layout principal avec widgets AI complets"""
        return html.Div([
            # AI Widgets Row
            dbc.Row([
                # Sentiment Analysis
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-brain me-2"),
                            "AI Sentiment Analysis",
                            dbc.Button([
                                html.I(className="fas fa-sync-alt")
                            ], id="refresh-economic-news-btn", color="info", size="sm", 
                               className="float-end ms-2", style={'padding': '0.25rem 0.5rem'})
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="economic-sentiment-chart", style={'height': '300px'})
                        ])
                    ])
                ], width=4),
                
                # Fear & Greed Index
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-thermometer-half me-2"),
                            "Economic Fear & Greed"
                        ]),
                        dbc.CardBody([
                            html.Div(id="economic-fear-greed-widget")
                        ])
                    ])
                ], width=4),
                
                # Trending Topics
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-fire me-2"),
                            "Trending Topics"
                        ]),
                        dbc.CardBody([
                            html.Div(id="economic-trending-topics")
                        ])
                    ])
                ], width=4)
            ], className="mb-4"),
            
            # News Feed Principal
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-rss me-2"),
                            "Live RSS Economic News Feed"
                        ]),
                        dbc.CardBody([
                            html.Div(id="economic-news-feed", style={'maxHeight': '600px', 'overflowY': 'auto'})
                        ])
                    ])
                ], width=12)
            ]),
            
            # Store pour données
            dcc.Store(id='economic-news-store'),
            dcc.Store(id='economic-sentiment-store'),
            
            # Interval pour auto-refresh
            dcc.Interval(
                id='economic-news-interval',
                interval=60000,  # 1 minute
                n_intervals=0
            )
        ], className="p-3")
    
    def setup_callbacks(self, app):
        """Configurer les callbacks pour Economic News"""
        
        @app.callback(
            [Output('economic-news-store', 'data'),
             Output('economic-sentiment-store', 'data')],
            [Input('refresh-economic-news-btn', 'n_clicks'),
             Input('economic-news-interval', 'n_intervals')]
        )
        def update_economic_news_data(refresh_clicks, interval_clicks):
            """Mettre à jour les données RSS économiques"""
            # Récupérer news RSS
            news_result = self.get_rss_news()
            articles = news_result.get('news', []) if isinstance(news_result, dict) else []
            
            # Analyser sentiment avec la liste d'articles
            sentiment = self.analyze_sentiment(articles)
            
            # Extraire trending topics avec la liste d'articles
            trending = self.extract_trending_topics(articles)
            
            # Calculer Fear & Greed avec la liste d'articles
            fear_greed = self.calculate_fear_greed_index(articles, sentiment)
            
            return {
                'news': articles,
                'trending': trending,
                'fear_greed': fear_greed,
                'timestamp': datetime.now().isoformat()
            }, sentiment
        
        @app.callback(
            Output('economic-news-feed', 'children'),
            [Input('economic-news-store', 'data')]
        )
        def update_news_feed(news_data):
            """Mettre à jour le feed de news"""
            if not news_data or not news_data.get('news'):
                return dbc.Alert("Aucune news RSS disponible", color="warning")
            
            news_items = []
            for article in news_data['news'][:20]:
                # Déterminer couleur sentiment
                sentiment = article.get('sentiment', 'neutral')
                if sentiment == 'positive':
                    border_color = "border-success"
                    icon_color = "text-success"
                    icon = "fas fa-arrow-up"
                elif sentiment == 'negative':
                    border_color = "border-danger"
                    icon_color = "text-danger"
                    icon = "fas fa-arrow-down"
                else:
                    border_color = "border-warning"
                    icon_color = "text-warning"
                    icon = "fas fa-minus"
                
                news_items.append(
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H6(article.get('title', 'No Title'), className="mb-2"),
                                    html.P(article.get('summary', 'No summary available')[:200] + '...', 
                                          className="text-muted small mb-2"),
                                    html.Div([
                                        dbc.Badge(article.get('source', 'RSS'), color="info", className="me-2"),
                                        html.Small([
                                            html.I(className="fas fa-clock me-1"),
                                            str(article.get('published_time', 'N/A'))
                                        ], className="text-muted me-3"),
                                        dbc.Button([
                                            html.I(className="fas fa-external-link-alt me-1"),
                                            "Lire l'article"
                                        ], 
                                        href=article.get('url', '#'),
                                        target="_blank",
                                        color="primary",
                                        size="sm",
                                        outline=True,
                                        className="ms-2"
                                        )
                                    ], className="d-flex align-items-center")
                                ], width=10),
                                dbc.Col([
                                    html.I(className=f"{icon} {icon_color}", style={'fontSize': '1.5rem'})
                                ], width=2, className="text-center")
                            ])
                        ])
                    ], className=f"mb-3 {border_color}")
                )
            
            return news_items
        
        @app.callback(
            Output('economic-sentiment-chart', 'figure'),
            [Input('economic-sentiment-store', 'data')]
        )
        def update_sentiment_chart(sentiment_data):
            """Mettre à jour le graphique de sentiment"""
            if not sentiment_data:
                sentiment_data = {'positive': 30, 'neutral': 50, 'negative': 20}
            
            # Graphique en donut
            fig = go.Figure(data=[
                go.Pie(
                    labels=['Positive', 'Neutral', 'Negative'],
                    values=[sentiment_data.get('positive', 0), 
                           sentiment_data.get('neutral', 0), 
                           sentiment_data.get('negative', 0)],
                    hole=0.5,
                    marker_colors=['#22c55e', '#eab308', '#ef4444']
                )
            ])
            
            fig.update_layout(
                title="Market Sentiment",
                showlegend=True,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=300
            )
            
            return fig
        
        @app.callback(
            Output('economic-fear-greed-widget', 'children'),
            [Input('economic-news-store', 'data')]
        )
        def update_fear_greed_widget(news_data):
            """Widget Fear & Greed"""
            if not news_data or not news_data.get('fear_greed'):
                fear_greed = {'score': 50, 'classification': 'Neutral', 'color': '#eab308'}
            else:
                fear_greed = news_data['fear_greed']
            
            return html.Div([
                html.H1(str(fear_greed['score']), 
                       className="text-center mb-2", 
                       style={'color': fear_greed['color'], 'fontSize': '4rem'}),
                html.H5(fear_greed['classification'], 
                       className="text-center mb-3", 
                       style={'color': fear_greed['color']}),
                dbc.Progress(
                    value=fear_greed['score'],
                    color="success" if fear_greed['score'] > 60 else "warning" if fear_greed['score'] > 40 else "danger",
                    style={'height': '10px'}
                )
            ])
        
        @app.callback(
            Output('economic-trending-topics', 'children'),
            [Input('economic-news-store', 'data')]
        )
        def update_trending_topics(news_data):
            """Widget sujets tendance"""
            if not news_data or not news_data.get('trending'):
                return html.P("Aucun sujet tendance", className="text-muted text-center")
            
            trending_items = []
            for topic in news_data['trending'][:6]:
                trending_items.append(
                    dbc.Row([
                        dbc.Col([
                            html.Span(topic['topic'], className="fw-bold")
                        ], width=8),
                        dbc.Col([
                            dbc.Badge(topic['count'], color="info", className="me-1"),
                            html.I(className=f"fas fa-arrow-up text-success" if topic['trend'] == 'up' else "fas fa-minus text-warning")
                        ], width=4, className="text-end")
                    ], className="mb-2")
                )
            
            return trending_items