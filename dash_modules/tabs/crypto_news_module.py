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

# Import Phase 4 Components
try:
    from ..components.crypto_trends import crypto_trends
    from ..components.top_performers import top_performers  
    from ..components.fear_greed_gauge import fear_greed_gauge
    PHASE4_COMPONENTS_AVAILABLE = True
except ImportError:
    print("⚠️ Phase 4 Components non disponibles")
    PHASE4_COMPONENTS_AVAILABLE = False

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
    
    def _format_date(self, date_value):
        """Formater une date pour l'affichage"""
        if not date_value or date_value in ['N/A', 'Unknown Date', '']:
            return "Date inconnue"
        
        try:
            # Si c'est déjà une string formatée, la retourner
            if isinstance(date_value, str):
                # Essayer de parser différents formats
                from datetime import datetime
                try:
                    # Format ISO avec timezone
                    if 'T' in date_value and ('+' in date_value or 'Z' in date_value):
                        dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                        return dt.strftime("%d/%m/%Y %H:%M")
                    # Format ISO simple
                    elif 'T' in date_value:
                        dt = datetime.fromisoformat(date_value)
                        return dt.strftime("%d/%m/%Y %H:%M")
                    # Déjà formaté
                    else:
                        return date_value
                except:
                    return date_value
            # Si c'est un objet datetime
            elif hasattr(date_value, 'strftime'):
                return date_value.strftime("%d/%m/%Y %H:%M")
            else:
                return str(date_value)
        except Exception as e:
            return "Date invalide"

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
                    
                    # Créer article enrichi avec traduction et mapping des champs
                    enriched_article = {
                        **article,
                        'title': translated_title,
                        'original_title': original_title,
                        'summary': translated_summary,
                        'original_summary': original_summary,
                        # Mapper les champs de date pour uniformité
                        'published_time': article.get('published_time') or article.get('published_date') or article.get('pubDate') or 'Unknown Date',
                        # Mapper les champs de source
                        'source': article.get('source') or article.get('source_name') or 'Unknown Source'
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
        """Layout principal avec widgets AI crypto optimisés"""
        return html.Div([
            # AI Widgets Row Optimisée - Seulement les widgets fonctionnels
            dbc.Row([
                # Fear & Greed Index Crypto - Gauge comme les news éco
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-thermometer-half me-2"),
                            "😨 Fear & Greed Index"
                        ]),
                        dbc.CardBody([
                            dcc.Graph(id="crypto-fear-greed-gauge", style={'height': '200px'})
                        ])
                    ])
                ], width=4),
                
                # Top Performers Crypto - Widget personnalisé
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-trophy me-2"),
                            "🏆 Top Performers"
                        ]),
                        dbc.CardBody([
                            html.Div(id="crypto-trending-coins", children=[
                                dbc.Row([
                                    dbc.Col("BTC", width=4),
                                    dbc.Col("$65,432", width=4, className="text-end"),
                                    dbc.Col([html.I(className="fas fa-arrow-up text-success")], width=4, className="text-end")
                                ], className="mb-2"),
                                dbc.Row([
                                    dbc.Col("ETH", width=4),
                                    dbc.Col("$3,124", width=4, className="text-end"),
                                    dbc.Col([html.I(className="fas fa-arrow-up text-success")], width=4, className="text-end")
                                ], className="mb-2"),
                                dbc.Row([
                                    dbc.Col("SOL", width=4),
                                    dbc.Col("$145", width=4, className="text-end"),
                                    dbc.Col([html.I(className="fas fa-arrow-down text-danger")], width=4, className="text-end")
                                ])
                            ])
                        ])
                    ])
                ], width=4),
                
                # Crypto Trends Analysis - Widget personnalisé
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-line me-2"),
                            "📊 Crypto Trends"
                        ]),
                        dbc.CardBody([
                            html.Div(id="crypto-price-impact-widget", children=[
                                html.Div([
                                    html.H6("📈 DeFi en hausse", className="mb-1"),
                                    html.P("Les protocoles décentralisés attirent plus d'attention", className="small text-muted")
                                ], className="mb-3"),
                                html.Div([
                                    html.H6("📈 Adoption institutionnelle", className="mb-1"),
                                    html.P("Les grandes entreprises s'intéressent aux cryptos", className="small text-muted")
                                ], className="mb-3"),
                                html.Div([
                                    html.H6("⚡ Layer 2 Solutions", className="mb-1"),
                                    html.P("Les solutions de mise à l'échelle gagnent du terrain", className="small text-muted")
                                ])
                            ])
                        ])
                    ])
                ], width=4)
            ], className="mb-4"),
            
            # News Feed Principal avec bouton refresh intégré
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-rss me-2"),
                            "Live RSS Crypto News Feed",
                            dbc.Button([
                                html.I(className="fas fa-sync-alt")
                            ], id="refresh-crypto-news-btn", color="warning", size="sm", 
                               className="float-end ms-2", style={'padding': '0.25rem 0.5rem'})
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
            
            # Format cohérent pour tous les widgets
            news_data = {
                'news': articles,  # Liste d'articles pour les widgets
                'trending': trending,
                'fear_greed': fear_greed,
                'price_impact': price_impact,
                'total': len(articles),
                'timestamp': datetime.now().isoformat()
            }
            
            return news_data, sentiment
        
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
                                        dbc.Badge(article.get('source', 'Unknown Source'), color="info", className="me-2"),
                                        html.Small([
                                            html.I(className="fas fa-clock me-1"),
                                            self._format_date(article.get('published_time', article.get('published_date', 'Unknown Date')))
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
            Output('crypto-fear-greed-gauge', 'figure'),
            [Input('crypto-news-store', 'data')]
        )
        def update_crypto_fear_greed_gauge(news_data):
            """Gauge Fear & Greed crypto basé sur l'analyse des vraies news"""
            try:
                # Calcul du score basé sur les vraies données RSS
                if not news_data or not news_data.get('news'):
                    # Valeurs par défaut
                    fear_greed_score = 55
                else:
                    # Calculer le score basé sur les news réelles
                    articles = news_data.get('news', [])
                    
                    # Analyser le sentiment des titres et résumés
                    positive_words = [
                        'pump', 'bull', 'bullish', 'rise', 'gain', 'up', 'rally', 'surge', 'profit',
                        'moon', 'lambo', 'hodl', 'buy', 'long', 'green', 'breakout', 'ath'
                    ]
                    negative_words = [
                        'dump', 'bear', 'bearish', 'fall', 'crash', 'down', 'drop', 'dip', 'loss',
                        'rekt', 'sell', 'short', 'red', 'correction', 'fud', 'liquidation'
                    ]
                    
                    positive_score = 0
                    negative_score = 0
                    total_articles = len(articles)
                    
                    for article in articles:
                        title_lower = article.get('title', '').lower()
                        summary_lower = article.get('summary', '').lower()
                        text = f"{title_lower} {summary_lower}"
                        
                        # Compter les mots positifs et négatifs
                        pos_count = sum(1 for word in positive_words if word in text)
                        neg_count = sum(1 for word in negative_words if word in text)
                        
                        positive_score += pos_count
                        negative_score += neg_count
                    
                    # Calculer le score Fear & Greed (0-100)
                    if positive_score == 0 and negative_score == 0:
                        fear_greed_score = 50  # Neutre si pas de sentiment détecté
                    else:
                        # Score basé sur le ratio positif/négatif
                        total_sentiment = positive_score + negative_score
                        positivity_ratio = positive_score / total_sentiment if total_sentiment > 0 else 0.5
                        
                        # Convertir en score 0-100 avec ajustement
                        fear_greed_score = 30 + (positivity_ratio * 40)  # Entre 30 et 70 base
                        
                        # Bonus/malus selon l'intensité
                        intensity = total_sentiment / total_articles if total_articles > 0 else 0
                        if intensity > 2:  # Beaucoup de sentiment
                            if positivity_ratio > 0.6:
                                fear_greed_score += 20  # Très bullish
                            elif positivity_ratio < 0.4:
                                fear_greed_score -= 20  # Très bearish
                    
                    # Limiter entre 5 et 95
                    fear_greed_score = max(5, min(95, fear_greed_score))
                
                # Déterminer la couleur et le texte
                if fear_greed_score >= 75:
                    bar_color = "#16a34a"  # Vert foncé
                    classification = "Extreme Greed"
                elif fear_greed_score >= 60:
                    bar_color = "#22c55e"  # Vert
                    classification = "Greed"
                elif fear_greed_score >= 45:
                    bar_color = "#eab308"  # Jaune
                    classification = "Neutral"
                elif fear_greed_score >= 25:
                    bar_color = "#f97316"  # Orange
                    classification = "Fear"
                else:
                    bar_color = "#dc2626"  # Rouge
                    classification = "Extreme Fear"
                
                # Création du gauge Plotly
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = fear_greed_score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': f"Crypto {classification}", 'font': {'color': 'white'}},
                    number = {'font': {'color': 'white', 'size': 40}},
                    gauge = {
                        'axis': {
                            'range': [None, 100],
                            'tickcolor': 'white',
                            'tickfont': {'color': 'white'}
                        },
                        'bar': {'color': bar_color, 'thickness': 0.8},
                        'steps': [
                            {'range': [0, 25], 'color': "#dc2626", 'name': 'Extreme Fear'},
                            {'range': [25, 45], 'color': "#f97316", 'name': 'Fear'},
                            {'range': [45, 60], 'color': "#eab308", 'name': 'Neutral'},
                            {'range': [60, 75], 'color': "#22c55e", 'name': 'Greed'},
                            {'range': [75, 100], 'color': "#16a34a", 'name': 'Extreme Greed'}
                        ],
                        'threshold': {
                            'line': {'color': "white", 'width': 3},
                            'thickness': 0.75,
                            'value': 50
                        }
                    }
                ))
                
                fig.update_layout(
                    height=200,
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                
                return fig
                
            except Exception as e:
                print(f"❌ Erreur Fear & Greed Gauge: {e}")
                # Gauge par défaut en cas d'erreur
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = 50,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Crypto Neutral", 'font': {'color': 'white'}},
                    number = {'font': {'color': 'white', 'size': 40}},
                    gauge = {
                        'axis': {'range': [None, 100], 'tickcolor': 'white'},
                        'bar': {'color': "#eab308"},
                        'steps': [
                            {'range': [0, 25], 'color': "#dc2626"},
                            {'range': [25, 45], 'color': "#f97316"},
                            {'range': [45, 60], 'color': "#eab308"},
                            {'range': [60, 75], 'color': "#22c55e"},
                            {'range': [75, 100], 'color': "#16a34a"}
                        ]
                    }
                ))
                fig.update_layout(
                    height=200,
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                return fig
        
        @app.callback(
            Output('crypto-trending-coins', 'children'),
            [Input('crypto-news-store', 'data')]
        )
        def update_crypto_trending_coins(news_data):
            """Widget coins tendance basé sur les mentions dans les news"""
            try:
                if not news_data or not news_data.get('news'):
                    # Données de démonstration
                    return html.Div([
                        dbc.Row([
                            dbc.Col("BTC", width=4),
                            dbc.Col("$65,432", width=4, className="text-end"),
                            dbc.Col([html.I(className="fas fa-arrow-up text-success")], width=4, className="text-end")
                        ], className="mb-2"),
                        dbc.Row([
                            dbc.Col("ETH", width=4),  
                            dbc.Col("$3,124", width=4, className="text-end"),
                            dbc.Col([html.I(className="fas fa-arrow-up text-success")], width=4, className="text-end")
                        ], className="mb-2"),
                        dbc.Row([
                            dbc.Col("SOL", width=4),
                            dbc.Col("$145", width=4, className="text-end"),
                            dbc.Col([html.I(className="fas fa-arrow-down text-danger")], width=4, className="text-end")
                        ])
                    ])
                
                # Analyser les articles pour extraire les mentions de cryptos
                articles = news_data.get('news', [])
                crypto_mentions = Counter()
                crypto_sentiment = {}
                
                # Liste des cryptos principales à chercher
                major_cryptos = {
                    'bitcoin': 'BTC', 'btc': 'BTC',
                    'ethereum': 'ETH', 'eth': 'ETH', 
                    'solana': 'SOL', 'sol': 'SOL',
                    'cardano': 'ADA', 'ada': 'ADA',
                    'ripple': 'XRP', 'xrp': 'XRP',
                    'binance': 'BNB', 'bnb': 'BNB'
                }
                
                positive_words = ['pump', 'bull', 'rise', 'gain', 'up', 'rally', 'surge', 'profit']
                negative_words = ['dump', 'bear', 'fall', 'crash', 'down', 'drop', 'dip', 'loss']
                
                for article in articles:
                    title_lower = article.get('title', '').lower()
                    summary_lower = article.get('summary', '').lower()
                    text = f"{title_lower} {summary_lower}"
                    
                    for word, symbol in major_cryptos.items():
                        if word in text:
                            crypto_mentions[symbol] += 1
                            
                            # Analyser le sentiment pour cette crypto
                            positive_score = sum(1 for pw in positive_words if pw in text)
                            negative_score = sum(1 for nw in negative_words if nw in text)
                            
                            if symbol not in crypto_sentiment:
                                crypto_sentiment[symbol] = {'positive': 0, 'negative': 0}
                            
                            crypto_sentiment[symbol]['positive'] += positive_score
                            crypto_sentiment[symbol]['negative'] += negative_score
                
                # Créer les éléments d'affichage
                trending_items = []
                for symbol, mentions in crypto_mentions.most_common(6):
                    sentiment = crypto_sentiment.get(symbol, {'positive': 0, 'negative': 0})
                    
                    if sentiment['positive'] > sentiment['negative']:
                        icon = "fas fa-arrow-up text-success"
                        text_color = "text-success"
                    elif sentiment['negative'] > sentiment['positive']:
                        icon = "fas fa-arrow-down text-danger"
                        text_color = "text-danger"
                    else:
                        icon = "fas fa-minus text-warning"
                        text_color = "text-warning"
                    
                    trending_items.append(
                        dbc.Row([
                            dbc.Col(html.Span(symbol, className=f"fw-bold {text_color}"), width=4),
                            dbc.Col(html.Span(f"{mentions} mentions", className="small"), width=5, className="text-end"),
                            dbc.Col([html.I(className=icon)], width=3, className="text-end")
                        ], className="mb-2")
                    )
                
                return html.Div(trending_items[:6] if trending_items else [
                    html.P("Pas assez de données crypto", className="text-muted text-center")
                ])
                
            except Exception as e:
                print(f"❌ Erreur Top Performers: {e}")
                # Fallback en cas d'erreur
                return html.Div([
                    dbc.Row([
                        dbc.Col("BTC", width=4),
                        dbc.Col("Analyse...", width=5, className="text-end"),
                        dbc.Col([html.I(className="fas fa-sync-alt fa-spin text-info")], width=3, className="text-end")
                    ])
                ])
        
        @app.callback(
            Output('crypto-price-impact-widget', 'children'),
            [Input('crypto-news-store', 'data')]
        )
        def update_crypto_trends_widget(news_data):
            """Widget tendances crypto basé sur l'analyse des news"""
            try:
                if not news_data or not news_data.get('news'):
                    # Tendances génériques de démonstration
                    return html.Div([
                        html.Div([
                            html.H6("🚀 DeFi en hausse", className="mb-1"),
                            html.P("Les protocoles décentralisés attirent plus d'attention", className="small text-muted")
                        ], className="mb-3"),
                        html.Div([
                            html.H6("📈 Adoption institutionnelle", className="mb-1"),
                            html.P("Les grandes entreprises s'intéressent aux cryptos", className="small text-muted")
                        ], className="mb-3"),
                        html.Div([
                            html.H6("⚡ Layer 2 Solutions", className="mb-1"),
                            html.P("Les solutions de mise à l'échelle gagnent du terrain", className="small text-muted")
                        ])
                    ])
                
                # Analyser les articles pour détecter les tendances
                articles = news_data.get('news', [])
                trend_keywords = {
                    '🚀 DeFi': ['defi', 'decentralized', 'uniswap', 'pancakeswap', 'yield', 'farming'],
                    '📈 Adoption': ['institutional', 'adoption', 'enterprise', 'corporate', 'mainstream'],
                    '⚡ Layer 2': ['layer 2', 'l2', 'scaling', 'polygon', 'arbitrum', 'optimism'],
                    '🎮 Gaming': ['gaming', 'metaverse', 'nft', 'play-to-earn', 'virtual'],
                    '🔒 Security': ['security', 'hack', 'vulnerability', 'audit', 'safe'],
                    '🏛️ Regulation': ['regulation', 'regulatory', 'compliance', 'legal', 'government'],
                    '💰 Staking': ['staking', 'validator', 'consensus', 'proof-of-stake', 'rewards'],
                    '🌐 Web3': ['web3', 'dapp', 'blockchain', 'smart contract', 'ecosystem']
                }
                
                trend_scores = {trend: 0 for trend in trend_keywords.keys()}
                trend_details = {trend: [] for trend in trend_keywords.keys()}
                
                for article in articles:
                    title_lower = article.get('title', '').lower()
                    summary_lower = article.get('summary', '').lower()
                    text = f"{title_lower} {summary_lower}"
                    
                    for trend, keywords in trend_keywords.items():
                        matches = sum(1 for keyword in keywords if keyword in text)
                        if matches > 0:
                            trend_scores[trend] += matches
                            if len(trend_details[trend]) < 2:
                                trend_details[trend].append(article.get('title', '')[:50] + '...')
                
                # Créer l'affichage des tendances
                sorted_trends = sorted(trend_scores.items(), key=lambda x: x[1], reverse=True)
                trend_items = []
                
                for trend, score in sorted_trends[:4]:
                    if score > 0:
                        intensity = "forte" if score >= 3 else "modérée" if score >= 2 else "faible"
                        color_class = "text-success" if score >= 3 else "text-warning" if score >= 2 else "text-info"
                        
                        examples = trend_details[trend]
                        detail_text = f"Activité {intensity} ({score} mentions)"
                        if examples:
                            detail_text = f"{examples[0][:40]}..."
                        
                        trend_items.append(
                            html.Div([
                                html.H6(trend, className=f"mb-1 {color_class}"),
                                html.P(detail_text, className="small text-muted")
                            ], className="mb-3")
                        )
                
                if not trend_items:
                    trend_items = [
                        html.Div([
                            html.H6("📊 Analyse en cours", className="mb-1"),
                            html.P("Collecte des données de tendances...", className="small text-muted")
                        ])
                    ]
                
                return html.Div(trend_items)
                
            except Exception as e:
                print(f"❌ Erreur Crypto Trends: {e}")
                return html.Div([
                    html.H6("⚠️ Erreur d'analyse", className="mb-1 text-warning"),
                    html.P("Impossible d'analyser les tendances actuellement", className="small text-muted")
                ])