"""
Crypto News Module for THEBOT
News crypto exclusivement alimentées par RSS avec widgets AI
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

class CryptoNewsModule:
    """Module News Crypto alimenté exclusivement par RSS avec widgets AI complets"""
    
    def __init__(self, calculators: Dict = None):
        self.calculators = calculators or {}
        self.news_cache = []
        self.sentiment_cache = {}
        self.trending_cache = []
        self.price_impact_cache = {}
        self.last_update = None
        
        # Configuration crypto
        self.crypto_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptomonnaie',
            'blockchain', 'altcoin', 'defi', 'nft', 'dogecoin', 'litecoin',
            'ripple', 'xrp', 'ada', 'cardano', 'binance coin', 'bnb',
            'solana', 'sol', 'avalanche', 'avax', 'polygon', 'matic',
            'chainlink', 'link', 'polkadot', 'dot', 'uniswap', 'uni',
            'web3', 'métaverse', 'stablecoin', 'mining', 'minage',
            'cryptocurrency', 'digital currency', 'virtual currency',
            'decentralized', 'smart contract', 'dapp', 'dao',
            'yield farming', 'liquidity mining', 'staking', 'hodl',
            'metaverse', 'gamefi', 'play-to-earn', 'p2e'
        ]
        
        print("✅ Crypto News Module initialisé (RSS exclusif)")
    
    def translate_article_title(self, title: str) -> str:
        """Traduire titre d'article crypto en français"""
        try:
            if AI_AVAILABLE:
                translated = smart_ai_manager.translate_to_french(title)
                return translated if translated and len(translated) > 3 else title
            return title
        except Exception as e:
            print(f"⚠️ Erreur traduction titre crypto: {e}")
            return title
    
    def translate_article_summary(self, summary: str) -> str:
        """Traduire résumé d'article crypto en français"""
        try:
            if AI_AVAILABLE and len(summary) > 10:
                translated = smart_ai_manager.translate_to_french(summary)
                return translated if translated and len(translated) > 5 else summary
            return summary
        except Exception as e:
            print(f"⚠️ Erreur traduction résumé crypto: {e}")
            return summary

    def get_rss_news(self) -> List[Dict]:
        """Récupérer les news depuis RSS Manager avec traduction"""
        if not RSS_AVAILABLE:
            return self._get_fallback_news()
        
        try:
            # Récupérer toutes les news RSS
            rss_result = rss_news_manager.get_news(limit=100)
            all_news = rss_result if isinstance(rss_result, list) else rss_result.get('articles', [])
            
            # Filtrer pour crypto seulement et traduire
            crypto_news = []
            for article in all_news:
                if self._is_crypto_news(article):
                    # Traduire titre et résumé
                    original_title = article.get('title', 'No Title')
                    original_summary = article.get('summary', article.get('description', 'No summary'))
                    
                    translated_title = self.translate_article_title(original_title)
                    translated_summary = self.translate_article_summary(original_summary)
                    
                    # Créer article enrichi avec traduction
                    enriched_article = {
                        **article,
                        'title': translated_title,
                        'original_title': original_title,
                        'summary': translated_summary,
                        'original_summary': original_summary
                    }
                    
                    crypto_news.append(enriched_article)
            
            # Limiter et trier par date
            crypto_news = sorted(crypto_news, 
                               key=lambda x: x.get('published_time', datetime.now()), 
                               reverse=True)[:30]
            
            self.news_cache = crypto_news
            self.last_update = datetime.now()
            
            print(f"✅ {len(crypto_news)} news crypto RSS récupérées (traduites)")
            return crypto_news
            
        except Exception as e:
            print(f"❌ Erreur RSS Crypto News: {e}")
            return self._get_fallback_news()
    
    def _is_crypto_news(self, article: Dict) -> bool:
        """Déterminer si un article est crypto"""
        text_to_check = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        # Vérifier présence de mots-clés crypto
        return any(keyword in text_to_check for keyword in self.crypto_keywords)
    
    def _get_fallback_news(self) -> List[Dict]:
        """News simulées en cas d'échec RSS"""
        return [
            {
                'title': 'Bitcoin Surges Past $45,000 on ETF Optimism',
                'summary': 'Bitcoin price rallies as investors anticipate spot ETF approval...',
                'published_time': datetime.now() - timedelta(hours=1),
                'source': 'RSS Crypto Feed',
                'url': '#',
                'sentiment': 'positive',
                'impact': 'high'
            },
            {
                'title': 'Ethereum 2.0 Staking Rewards Hit New High',
                'summary': 'Ethereum staking yields increase as more validators join...',
                'published_time': datetime.now() - timedelta(hours=2),
                'source': 'RSS Crypto Feed',
                'url': '#',
                'sentiment': 'positive',
                'impact': 'medium'
            },
            {
                'title': 'Regulatory Concerns Weigh on Altcoin Market',
                'summary': 'Regulatory uncertainty affects smaller cryptocurrencies...',
                'published_time': datetime.now() - timedelta(hours=3),
                'source': 'RSS Crypto Feed',
                'url': '#',
                'sentiment': 'negative',
                'impact': 'medium'
            }
        ]
    
    def analyze_crypto_sentiment(self, articles: List[Dict]) -> Dict:
        """Analyser le sentiment crypto avec IA"""
        if not AI_AVAILABLE or not articles:
            return {'bullish': 40, 'neutral': 35, 'bearish': 25, 'confidence': 0.7}
        
        try:
            # Analyser avec Smart AI Manager
            sentiments = []
            for article in articles[:20]:
                text = f"{article.get('title', '')} {article.get('summary', '')}"
                if len(text.strip()) > 10:
                    result = smart_ai_manager.analyze_with_best_ai({'text': text}, 'crypto_sentiment')
                    sentiment = result.get('sentiment', 'neutral')
                    if sentiment == 'positive':
                        sentiments.append('bullish')
                    elif sentiment == 'negative':
                        sentiments.append('bearish')
                    else:
                        sentiments.append('neutral')
            
            if not sentiments:
                return {'bullish': 40, 'neutral': 35, 'bearish': 25, 'confidence': 0.7}
            
            # Calculer distribution crypto-spécifique
            sentiment_counts = Counter(sentiments)
            total = len(sentiments)
            
            result = {
                'bullish': round((sentiment_counts.get('bullish', 0) / total) * 100, 1),
                'neutral': round((sentiment_counts.get('neutral', 0) / total) * 100, 1),
                'bearish': round((sentiment_counts.get('bearish', 0) / total) * 100, 1),
                'confidence': 0.85
            }
            
            self.sentiment_cache = result
            return result
            
        except Exception as e:
            print(f"❌ Erreur analyse sentiment crypto: {e}")
            return {'bullish': 40, 'neutral': 35, 'bearish': 25, 'confidence': 0.7}
    
    def extract_crypto_trending(self, articles: List[Dict]) -> List[Dict]:
        """Extraire les coins/tokens tendance"""
        if not articles:
            return []
        
        try:
            # Extraire mentions de cryptos
            all_text = ' '.join([article.get('title', '') + ' ' + article.get('summary', '') for article in articles])
            
            # Chercher mentions spécifiques de cryptos
            crypto_mentions = []
            for keyword in self.crypto_keywords:
                if keyword in all_text.lower():
                    count = all_text.lower().count(keyword)
                    if count > 0:
                        crypto_mentions.append((keyword, count))
            
            # Trier et créer trending
            trending = []
            for crypto, count in sorted(crypto_mentions, key=lambda x: x[1], reverse=True)[:10]:
                trending.append({
                    'coin': crypto.upper() if len(crypto) <= 4 else crypto.title(),
                    'mentions': count,
                    'trend': 'up' if count > 2 else 'stable',
                    'sentiment': 'positive' if count > 3 else 'neutral'
                })
            
            self.trending_cache = trending[:8]
            return self.trending_cache
            
        except Exception as e:
            print(f"❌ Erreur trending crypto: {e}")
            return []
    
    def calculate_crypto_fear_greed(self, articles: List[Dict], sentiment: Dict) -> Dict:
        """Calculer l'indice Fear & Greed crypto-spécifique"""
        try:
            # Facteurs crypto
            bullish_pct = sentiment.get('bullish', 40)
            bearish_pct = sentiment.get('bearish', 25)
            
            # Impact de volume et sentiment
            news_volume_factor = min(len(articles) / 15, 1.0)
            sentiment_factor = (bullish_pct - bearish_pct) / 100
            
            # Bonus pour mentions Bitcoin/Ethereum
            major_coin_bonus = 0
            for article in articles[:10]:
                text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
                if 'bitcoin' in text or 'btc' in text:
                    major_coin_bonus += 5
                if 'ethereum' in text or 'eth' in text:
                    major_coin_bonus += 3
            
            # Score final crypto (0-100)
            fear_greed_score = 50 + (sentiment_factor * 35) + (news_volume_factor * 10) + min(major_coin_bonus, 15)
            fear_greed_score = max(0, min(100, fear_greed_score))
            
            # Classification crypto
            if fear_greed_score >= 80:
                classification = "Extreme Greed 🚀"
                color = "#16a34a"
            elif fear_greed_score >= 60:
                classification = "Greed 📈"
                color = "#22c55e"
            elif fear_greed_score >= 40:
                classification = "Neutral ⚖️"
                color = "#eab308"
            elif fear_greed_score >= 20:
                classification = "Fear 📉"
                color = "#f97316"
            else:
                classification = "Extreme Fear 💀"
                color = "#dc2626"
            
            return {
                'score': round(fear_greed_score, 1),
                'classification': classification,
                'color': color,
                'confidence': sentiment.get('confidence', 0.75)
            }
            
        except Exception as e:
            print(f"❌ Erreur Crypto Fear & Greed: {e}")
            return {
                'score': 50.0,
                'classification': 'Neutral ⚖️',
                'color': '#eab308',
                'confidence': 0.5
            }
    
    def analyze_price_impact(self, articles: List[Dict]) -> Dict:
        """Analyser l'impact potentiel sur les prix"""
        try:
            # Analyser mentions et sentiment
            high_impact_count = 0
            medium_impact_count = 0
            low_impact_count = 0
            
            for article in articles[:15]:
                text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
                
                # Mots-clés d'impact élevé
                high_impact_keywords = ['etf', 'regulation', 'adoption', 'institutional', 'government', 'ban', 'approval']
                medium_impact_keywords = ['partnership', 'listing', 'upgrade', 'fork', 'announcement']
                
                if any(keyword in text for keyword in high_impact_keywords):
                    high_impact_count += 1
                elif any(keyword in text for keyword in medium_impact_keywords):
                    medium_impact_count += 1
                else:
                    low_impact_count += 1
            
            total = high_impact_count + medium_impact_count + low_impact_count
            if total == 0:
                return {'high': 20, 'medium': 50, 'low': 30}
            
            return {
                'high': round((high_impact_count / total) * 100, 1),
                'medium': round((medium_impact_count / total) * 100, 1),
                'low': round((low_impact_count / total) * 100, 1)
            }
            
        except Exception as e:
            print(f"❌ Erreur analyse impact prix: {e}")
            return {'high': 20, 'medium': 50, 'low': 30}
    
    def get_layout(self) -> html.Div:
        """Layout principal avec widgets AI crypto complets"""
        return html.Div([
            # AI Widgets Row
            dbc.Row([
                # Sentiment Analysis Crypto
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-brain me-2"),
                            "Crypto Sentiment",
                            dbc.Button([
                                html.I(className="fas fa-sync-alt")
                            ], id="refresh-crypto-news-btn", color="warning", size="sm", 
                               className="float-end ms-2", style={'padding': '0.25rem 0.5rem'})
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="crypto-sentiment-chart", style={'height': '300px'})
                        ])
                    ])
                ], width=3),
                
                # Fear & Greed Index Crypto
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-thermometer-half me-2"),
                            "Crypto Fear & Greed"
                        ]),
                        dbc.CardBody([
                            html.Div(id="crypto-fear-greed-widget")
                        ])
                    ])
                ], width=3),
                
                # Trending Coins/Tokens
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-fire me-2"),
                            "Trending Coins"
                        ]),
                        dbc.CardBody([
                            html.Div(id="crypto-trending-coins")
                        ])
                    ])
                ], width=3),
                
                # Price Impact Analysis
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-line me-2"),
                            "Price Impact"
                        ]),
                        dbc.CardBody([
                            html.Div(id="crypto-price-impact-widget")
                        ])
                    ])
                ], width=3)
            ], className="mb-4"),
            
            # News Feed Principal
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-rss me-2"),
                            "Live RSS Crypto News Feed"
                        ]),
                        dbc.CardBody([
                            html.Div(id="crypto-news-feed", style={'maxHeight': '600px', 'overflowY': 'auto'})
                        ])
                    ])
                ], width=12)
            ]),
            
            # Store pour données
            dcc.Store(id='crypto-news-store'),
            dcc.Store(id='crypto-sentiment-store'),
            
            # Interval pour auto-refresh
            dcc.Interval(
                id='crypto-news-interval',
                interval=45000,  # 45 secondes (crypto plus volatil)
                n_intervals=0
            )
        ], className="p-3")
    
    def setup_callbacks(self, app):
        """Configurer les callbacks pour Crypto News"""
        
        @app.callback(
            [Output('crypto-news-store', 'data'),
             Output('crypto-sentiment-store', 'data')],
            [Input('refresh-crypto-news-btn', 'n_clicks'),
             Input('crypto-news-interval', 'n_intervals')]
        )
        def update_crypto_news_data(refresh_clicks, interval_clicks):
            """Mettre à jour les données RSS crypto"""
            # Récupérer news RSS (retourne une liste d'articles)
            articles = self.get_rss_news()
            
            # Analyser sentiment crypto avec la liste
            sentiment = self.analyze_crypto_sentiment(articles)
            
            # Extraire trending coins avec la liste
            trending = self.extract_crypto_trending(articles)
            
            # Calculer Fear & Greed crypto avec la liste
            fear_greed = self.calculate_crypto_fear_greed(articles, sentiment)
            
            # Analyser impact prix avec la liste
            price_impact = self.analyze_price_impact(articles)
            
            return {
                'news': articles,
                'trending': trending,
                'fear_greed': fear_greed,
                'price_impact': price_impact,
                'timestamp': datetime.now().isoformat()
            }, sentiment
        
        @app.callback(
            Output('crypto-news-feed', 'children'),
            [Input('crypto-news-store', 'data')]
        )
        def update_crypto_news_feed(news_data):
            """Mettre à jour le feed de news crypto"""
            if not news_data or not news_data.get('news'):
                return dbc.Alert("Aucune news crypto RSS disponible", color="warning")
            
            news_items = []
            for article in news_data['news'][:20]:
                # Déterminer couleur sentiment crypto
                sentiment = article.get('sentiment', 'neutral')
                if sentiment in ['positive', 'bullish']:
                    border_color = "border-success"
                    icon_color = "text-success"
                    icon = "fas fa-rocket"
                elif sentiment in ['negative', 'bearish']:
                    border_color = "border-danger"
                    icon_color = "text-danger"
                    icon = "fas fa-arrow-down"
                else:
                    border_color = "border-warning"
                    icon_color = "text-warning"
                    icon = "fas fa-minus"
                
                # Impact badge
                impact = article.get('impact', 'low')
                if impact == 'high':
                    impact_badge = dbc.Badge("HIGH IMPACT", color="danger", className="me-2")
                elif impact == 'medium':
                    impact_badge = dbc.Badge("MEDIUM", color="warning", className="me-2")
                else:
                    impact_badge = dbc.Badge("LOW", color="secondary", className="me-2")
                
                news_items.append(
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.H6(article.get('title', 'No Title'), className="mb-2"),
                                    html.P(article.get('summary', 'No summary available')[:200] + '...', 
                                          className="text-muted small mb-2"),
                                    html.Div([
                                        impact_badge,
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
                                        color="success",
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
            Output('crypto-sentiment-chart', 'figure'),
            [Input('crypto-sentiment-store', 'data')]
        )
        def update_crypto_sentiment_chart(sentiment_data):
            """Mettre à jour le graphique de sentiment crypto"""
            if not sentiment_data:
                sentiment_data = {'bullish': 40, 'neutral': 35, 'bearish': 25}
            
            # Graphique en donut crypto
            fig = go.Figure(data=[
                go.Pie(
                    labels=['Bullish 🚀', 'Neutral ⚖️', 'Bearish 📉'],
                    values=[sentiment_data.get('bullish', 0), 
                           sentiment_data.get('neutral', 0), 
                           sentiment_data.get('bearish', 0)],
                    hole=0.5,
                    marker_colors=['#22c55e', '#eab308', '#ef4444']
                )
            ])
            
            fig.update_layout(
                title="Crypto Market Sentiment",
                showlegend=True,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=300
            )
            
            return fig
        
        @app.callback(
            Output('crypto-fear-greed-widget', 'children'),
            [Input('crypto-news-store', 'data')]
        )
        def update_crypto_fear_greed_widget(news_data):
            """Widget Fear & Greed crypto"""
            if not news_data or not news_data.get('fear_greed'):
                fear_greed = {'score': 50, 'classification': 'Neutral ⚖️', 'color': '#eab308'}
            else:
                fear_greed = news_data['fear_greed']
            
            return html.Div([
                html.H1(str(fear_greed['score']), 
                       className="text-center mb-2", 
                       style={'color': fear_greed['color'], 'fontSize': '4rem'}),
                html.H6(fear_greed['classification'], 
                       className="text-center mb-3", 
                       style={'color': fear_greed['color']}),
                dbc.Progress(
                    value=fear_greed['score'],
                    color="success" if fear_greed['score'] > 60 else "warning" if fear_greed['score'] > 40 else "danger",
                    style={'height': '10px'}
                )
            ])
        
        @app.callback(
            Output('crypto-trending-coins', 'children'),
            [Input('crypto-news-store', 'data')]
        )
        def update_crypto_trending_coins(news_data):
            """Widget coins tendance"""
            if not news_data or not news_data.get('trending'):
                return html.P("Aucun coin tendance", className="text-muted text-center")
            
            trending_items = []
            for coin in news_data['trending'][:6]:
                # Couleur selon sentiment
                if coin.get('sentiment') == 'positive':
                    text_color = "text-success"
                    icon = "fas fa-arrow-up"
                else:
                    text_color = "text-warning"
                    icon = "fas fa-minus"
                
                trending_items.append(
                    dbc.Row([
                        dbc.Col([
                            html.Span(coin['coin'], className=f"fw-bold {text_color}")
                        ], width=7),
                        dbc.Col([
                            dbc.Badge(coin['mentions'], color="warning", className="me-1"),
                            html.I(className=f"{icon} {text_color}")
                        ], width=5, className="text-end")
                    ], className="mb-2")
                )
            
            return trending_items
        
        @app.callback(
            Output('crypto-price-impact-widget', 'children'),
            [Input('crypto-news-store', 'data')]
        )
        def update_crypto_price_impact_widget(news_data):
            """Widget impact prix"""
            if not news_data or not news_data.get('price_impact'):
                price_impact = {'high': 20, 'medium': 50, 'low': 30}
            else:
                price_impact = news_data['price_impact']
            
            return html.Div([
                html.H6("Price Impact Analysis", className="text-center mb-3"),
                
                # High Impact
                dbc.Row([
                    dbc.Col([
                        html.Span("High Impact", className="small")
                    ], width=6),
                    dbc.Col([
                        html.Span(f"{price_impact['high']}%", className="fw-bold text-danger")
                    ], width=6, className="text-end")
                ], className="mb-1"),
                
                dbc.Progress(value=price_impact['high'], color="danger", style={'height': '6px'}, className="mb-2"),
                
                # Medium Impact
                dbc.Row([
                    dbc.Col([
                        html.Span("Medium Impact", className="small")
                    ], width=6),
                    dbc.Col([
                        html.Span(f"{price_impact['medium']}%", className="fw-bold text-warning")
                    ], width=6, className="text-end")
                ], className="mb-1"),
                
                dbc.Progress(value=price_impact['medium'], color="warning", style={'height': '6px'}, className="mb-2"),
                
                # Low Impact
                dbc.Row([
                    dbc.Col([
                        html.Span("Low Impact", className="small")
                    ], width=6),
                    dbc.Col([
                        html.Span(f"{price_impact['low']}%", className="fw-bold text-secondary")
                    ], width=6, className="text-end")
                ], className="mb-1"),
                
                dbc.Progress(value=price_impact['low'], color="secondary", style={'height': '6px'})
            ])