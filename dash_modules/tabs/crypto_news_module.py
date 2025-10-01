"""
Crypto News Module for THEBOT
Handles cryptocurrency and blockchain news
"""

from .base_news_module import BaseNewsModule
import dash
from dash import dcc, html, callback, Input, Output, State, ALL
import dash_bootstrap_components as dbc
from typing import List, Dict
import pandas as pd

class CryptoNewsModule(BaseNewsModule):
    """Crypto News Module handling cryptocurrency and blockchain news"""
    
    def __init__(self, calculators: Dict = None):
        super().__init__(
            news_type='crypto',
            calculators=calculators
        )

    def _get_news_sources(self) -> List[str]:
        """Get news sources for crypto news"""
        # Sources pour les news crypto
        return ['binance', 'crypto_panic', 'coin_gecko']

    def _filter_news_by_type(self, news_list: List[Dict]) -> List[Dict]:
        """Filter news to include only crypto/blockchain news"""
        if not news_list:
            return []
        
        # Keywords for crypto news (in multiple languages)
        crypto_keywords = [
            # French terms
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptomonnaie', 
            'blockchain', 'altcoin', 'defi', 'nft', 'dogecoin', 'litecoin',
            'ripple', 'xrp', 'ada', 'cardano', 'binance coin', 'bnb',
            'solana', 'sol', 'avalanche', 'avax', 'polygon', 'matic',
            'chainlink', 'link', 'polkadot', 'dot', 'uniswap', 'uni',
            'web3', 'métaverse', 'stablecoin', 'mining', 'minage',
            
            # English terms
            'cryptocurrency', 'digital currency', 'virtual currency',
            'decentralized', 'smart contract', 'dapp', 'dao',
            'yield farming', 'liquidity mining', 'staking', 'hodl',
            'metaverse', 'gamefi', 'play-to-earn', 'p2e'
        ]
        
        # Economic keywords to exclude if no crypto context
        exclude_if_no_crypto = [
            'traditional banking', 'conventional finance', 'fiat currency',
            'stock market only', 'forex only', 'commodities only'
        ]
        
        filtered_news = []
        for news_item in news_list:
            # Get title and description for analysis
            title = (news_item.get('title', '') or '').lower()
            description = (news_item.get('description', '') or news_item.get('summary', '') or '').lower()
            source = (news_item.get('source', '') or '').lower()
            
            # Check if source is crypto-focused
            crypto_sources = ['binance', 'crypto_panic', 'coin_gecko', 'coindesk', 'cointelegraph']
            is_crypto_source = any(src in source for src in crypto_sources)
            
            # Check for crypto keywords
            has_crypto_keywords = any(keyword in title or keyword in description for keyword in crypto_keywords)
            
            # Include if it's from crypto source OR has crypto keywords
            if is_crypto_source or has_crypto_keywords:
                filtered_news.append(news_item)
        
        print(f"🪙 Crypto news filter: {len(news_list)} → {len(filtered_news)} articles")
        return filtered_news

    def get_layout(self):
        """Get the complete layout for crypto news module"""
        return html.Div([
            # Hidden stores for data and callbacks
            dcc.Store(id='crypto-news-data-store', data=[]),
            dcc.Store(id='crypto-news-articles-store', data=[]),
            
            # Loading indicator
            dcc.Loading([
                html.Div(id='crypto-news-loading-target')
            ], id='crypto-news-loading', type='circle'),
            
            # Main content container
            html.Div([
                # Quick Stats Row
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("🪙", className="text-primary mb-0"),
                                html.Small("News Crypto", className="text-muted")
                            ])
                        ], className="h-100 text-center")
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(id='crypto-total-articles', children="0", className="text-info mb-0"),
                                html.Small("Articles Totaux", className="text-muted")
                            ])
                        ], className="h-100 text-center")
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(id='crypto-sentiment-score', children="Neutre", className="text-success mb-0"),
                                html.Small("Sentiment Global", className="text-muted")
                            ])
                        ], className="h-100 text-center")
                    ], width=3),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(id='crypto-last-update', children="--:--", className="text-warning mb-0"),
                                html.Small("Dernière MAJ", className="text-muted")
                            ])
                        ], className="h-100 text-center")
                    ], width=3)
                ], className="mb-4"),
                
                # News Feed
                dbc.Row([
                    dbc.Col([
                        # News Feed
                        html.Div(id='crypto-news-feed', children=[
                            html.P("Chargement des actualités crypto...", className="text-center text-muted p-4")
                        ])
                    ], width=8),
                    dbc.Col([
                        # Side widgets
                        html.Div([
                            # Market Impact Widget
                            dbc.Card([
                                dbc.CardBody(id='crypto-market-impact')
                            ], className="mb-3"),
                            
                            # Trending Cryptos Widget
                            dbc.Card([
                                dbc.CardBody(id='crypto-trending')
                            ])
                        ])
                    ], width=4)
                ])
            ], id='crypto-news-content')
        ])

    def create_trending_cryptos_widget(self) -> html.Div:
        """Create trending cryptocurrencies widget"""
        try:
            # Try to get trending data from CoinGecko
            from ..data_providers.coin_gecko_api import coin_gecko_api
            
            trending_data = coin_gecko_api.get_trending_coins()
            
            if trending_data and len(trending_data) > 0:
                trending_items = []
                for crypto in trending_data[:5]:  # Top 5
                    trending_items.append(
                        html.Div([
                            html.Span(f"🔥 {crypto.get('name', 'Unknown')}", className="fw-bold"),
                            html.Br(),
                            html.Small(f"#{crypto.get('market_cap_rank', 'N/A')}", className="text-muted")
                        ], className="mb-2")
                    )
                
                return html.Div([
                    html.H6("🔥 Trending Cryptos", className="mb-3"),
                    html.Div(trending_items)
                ])
            else:
                return html.Div([
                    html.H6("🔥 Trending Cryptos", className="mb-3"),
                    html.P("Données de tendance non disponibles", className="text-muted small")
                ])
                
        except Exception as e:
            print(f"⚠️ Error creating trending cryptos widget: {e}")
            return html.Div([
                html.H6("🔥 Trending Cryptos", className="mb-3"),
                html.P("Fonctionnalité en développement...", className="text-muted small")
            ])

    def setup_callbacks(self, app):
        """Setup callbacks for crypto news module"""
        
        @app.callback(
            [Output('crypto-news-data-store', 'data'),
             Output('crypto-news-articles-store', 'data'),
             Output('crypto-news-feed', 'children'),
             Output('crypto-total-articles', 'children'),
             Output('crypto-sentiment-score', 'children'),
             Output('crypto-last-update', 'children'),
             Output('crypto-market-impact', 'children'),
             Output('crypto-trending', 'children'),
             Output('crypto-news-loading-target', 'children')],
            [Input('crypto-news-data-store', 'id')],  # Trigger on component mount
            prevent_initial_call=False
        )
        def load_crypto_news_data(_):
            """Load and display crypto news data"""
            try:
                # Load crypto news data
                news_data = self.load_news_data(category='All News', limit=100)
                
                if news_data.empty:
                    return (
                        [], [], 
                        html.P("Aucune actualité crypto disponible.", className="text-center text-muted p-4"),
                        "0", "Neutre", "--:--",
                        html.P("Pas de données d'impact", className="text-muted"),
                        self.create_trending_cryptos_widget(),
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
                        sentiment_score = "Bullish 🚀"
                    elif sentiment_counts.get('negative', 0) > sentiment_counts.get('positive', 0):
                        sentiment_score = "Bearish 📉"
                    else:
                        sentiment_score = "Neutre ⚖️"
                else:
                    sentiment_score = "Neutre ⚖️"
                
                # Last update time
                from datetime import datetime
                last_update = datetime.now().strftime("%H:%M")
                
                # Market impact widget
                market_impact = self.create_market_impact_widget(news_data)
                
                # Trending cryptos widget
                trending_cryptos = self.create_trending_cryptos_widget()
                
                return (
                    news_data.to_dict('records'),
                    articles_data,
                    news_feed,
                    str(total_articles),
                    sentiment_score,
                    last_update,
                    market_impact,
                    trending_cryptos,
                    ""
                )
                
            except Exception as e:
                print(f"❌ Error in crypto news callback: {e}")
                import traceback
                traceback.print_exc()
                
                return (
                    [], [],
                    html.P("Erreur lors du chargement des actualités crypto.", className="text-center text-danger p-4"),
                    "0", "Erreur", "--:--",
                    html.P("Erreur de chargement", className="text-muted"),
                    self.create_trending_cryptos_widget(),
                    ""
                )