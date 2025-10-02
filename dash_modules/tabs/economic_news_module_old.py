"""
Economic News Module for THEBOT
Handles general economic and financial news
"""

from .base_news_module import BaseNewsModule
import dash
from dash import dcc, html, callback, Input, Output, State, ALL
import dash_bootstrap_components as dbc
from typing import List, Dict
import pandas as pd

class EconomicNewsModule(BaseNewsModule):
    """Economic News Module handling general financial and economic news"""
    
    def __init__(self, calculators: Dict = None):
        super().__init__(
            news_type='economic',
            calculators=calculators
        )

    def _get_news_sources(self) -> List[str]:
        """Get news sources for economic news"""
        # Sources pour les news économiques générales (alpha_vantage deprecated)
        return ['yahoo', 'fmp', 'reuters']

    def _filter_news_by_type(self, news_list: List[Dict]) -> List[Dict]:
        """Filter news to include only economic/financial news"""
        if not news_list:
            return []
        
        # Keywords for economic news (in multiple languages)
        economic_keywords = [
            # French terms
            'économie', 'économique', 'finance', 'financier', 'banque', 'bourse', 
            'marché', 'action', 'obligation', 'taux', 'inflation', 'croissance',
            'pib', 'fed', 'bce', 'banque centrale', 'politique monétaire',
            'commerce', 'industrie', 'emploi', 'chômage', 'consommation',
            
            # English terms
            'economy', 'economic', 'finance', 'financial', 'banking', 'stock market',
            'market', 'stock', 'bond', 'rate', 'inflation', 'growth',
            'gdp', 'federal reserve', 'central bank', 'monetary policy',
            'trade', 'industry', 'employment', 'unemployment', 'consumption',
            'earnings', 'revenue', 'profit', 'dividend', 'treasury'
        ]
        
        # Keywords to exclude (crypto-related)
        crypto_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency',
            'blockchain', 'altcoin', 'defi', 'nft', 'dogecoin', 'litecoin',
            'ripple', 'xrp', 'ada', 'cardano', 'binance coin', 'bnb'
        ]
        
        filtered_news = []
        for news_item in news_list:
            # Get title and description for analysis
            title = (news_item.get('title', '') or '').lower()
            description = (news_item.get('description', '') or news_item.get('summary', '') or '').lower()
            source = (news_item.get('source', '') or '').lower()
            
            # Check if source is economic-focused (alpha_vantage deprecated)
            economic_sources = ['yahoo', 'fmp', 'marketwatch', 'bloomberg', 'reuters']
            is_economic_source = any(src in source for src in economic_sources)
            
            # Check for crypto keywords (exclude if found)
            has_crypto_keywords = any(keyword in title or keyword in description for keyword in crypto_keywords)
            
            # Check for economic keywords (include if found)
            has_economic_keywords = any(keyword in title or keyword in description for keyword in economic_keywords)
            
            # Include if it's from economic source and doesn't have crypto keywords
            # OR if it has economic keywords and doesn't have crypto keywords
            if (is_economic_source and not has_crypto_keywords) or (has_economic_keywords and not has_crypto_keywords):
                filtered_news.append(news_item)
        
        print(f"📊 Economic news filter: {len(news_list)} → {len(filtered_news)} articles")
        return filtered_news

    def get_layout(self):
        """Get the complete layout for economic news module"""
        return html.Div([
            # Hidden stores for data and callbacks
            dcc.Store(id='economic-news-data-store', data=[]),
            dcc.Store(id='economic-news-articles-store', data=[]),
            
            # Loading indicator
            dcc.Loading([
                html.Div(id='economic-news-loading-target')
            ], id='economic-news-loading', type='circle'),
            
            # Main content container
            html.Div([
                # Quick Stats Row
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("📊", className="text-primary mb-0"),
                                html.Small("News Économiques", className="text-muted")
                            ])
                        ], className="h-100 text-center")
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(id='economic-total-articles', children="0", className="text-info mb-0"),
                                html.Small("Articles Totaux", className="text-muted")
                            ])
                        ], className="h-100 text-center")
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(id='economic-sentiment-score', children="Neutre", className="text-success mb-0"),
                                html.Small("Sentiment Global", className="text-muted")
                            ])
                        ], className="h-100 text-center")
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(id='economic-last-update', children="--:--", className="text-warning mb-0"),
                                html.Small("Dernière MAJ", className="text-muted")
                            ])
                        ], className="h-100 text-center")
                    ], width=3)
                ], className="mb-4"),
                
                # News Feed
                dbc.Row([
                    dbc.Col([
                        # News Feed
                        html.Div(id='economic-news-feed', children=[
                            html.P("Chargement des actualités économiques...", className="text-center text-muted p-4")
                        ])
                    ], width=8),
                    dbc.Col([
                        # Side widgets
                        html.Div([
                            # Market Impact Widget
                            dbc.Card([
                                dbc.CardBody(id='economic-market-impact')
                            ], className="mb-3"),
                            
                            # Economic Calendar Widget
                            dbc.Card([
                                dbc.CardBody(id='economic-calendar')
                            ])
                        ])
                    ], width=4)
                ])
            ], id='economic-news-content')
        ])

    def setup_callbacks(self, app):
        """Setup callbacks for economic news module"""
        
        @app.callback(
            [Output('economic-news-data-store', 'data'),
             Output('economic-news-articles-store', 'data'),
             Output('economic-news-feed', 'children'),
             Output('economic-total-articles', 'children'),
             Output('economic-sentiment-score', 'children'),
             Output('economic-last-update', 'children'),
             Output('economic-market-impact', 'children'),
             Output('economic-calendar', 'children'),
             Output('economic-news-loading-target', 'children')],
            [Input('economic-news-data-store', 'id')],  # Trigger on component mount
            prevent_initial_call=False
        )
        def load_economic_news_data(_):
            """Load and display economic news data"""
            try:
                # Load economic news data
                news_data = self.load_news_data(category='All News', limit=100)
                
                if news_data.empty:
                    return (
                        [], [], 
                        html.P("Aucune actualité économique disponible.", className="text-center text-muted p-4"),
                        "0", "Neutre", "--:--",
                        html.P("Pas de données d'impact", className="text-muted"),
                        self.create_economic_calendar_widget(),
                        ""
                    )
                
                # Create news feed
                news_feed, articles_data = self.create_news_feed(news_data)
                
                # Calculate statistics
                total_articles = len(news_data)
                
                # Calculate sentiment
                if 'sentiment' in news_data.columns:
                    sentiment_counts = news_data['sentiment'].value_counts()
                    if sentiment_counts.get('positive', 0) > sentiment_counts.get('negative', 0):
                        sentiment_score = "Positif"
                    elif sentiment_counts.get('negative', 0) > sentiment_counts.get('positive', 0):
                        sentiment_score = "Négatif"
                    else:
                        sentiment_score = "Neutre"
                else:
                    sentiment_score = "Neutre"
                
                # Last update time
                from datetime import datetime
                last_update = datetime.now().strftime("%H:%M")
                
                # Market impact widget
                market_impact = self.create_market_impact_widget(news_data)
                
                # Economic calendar widget
                economic_calendar = self.create_economic_calendar_widget()
                
                return (
                    news_data.to_dict('records'),
                    articles_data,
                    news_feed,
                    str(total_articles),
                    sentiment_score,
                    last_update,
                    market_impact,
                    economic_calendar,
                    ""
                )
                
            except Exception as e:
                print(f"❌ Error in economic news callback: {e}")
                import traceback
                traceback.print_exc()
                
                return (
                    [], [],
                    html.P("Erreur lors du chargement des actualités économiques.", className="text-center text-danger p-4"),
                    "0", "Erreur", "--:--",
                    html.P("Erreur de chargement", className="text-muted"),
                    self.create_economic_calendar_widget(),
                    ""
                )