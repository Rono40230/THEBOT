"""
Stocks Market Module for THEBOT
Handles stock data using Alpha Vantage API
"""

from .base_market_module import BaseMarketModule
# AlphaVantage API supprimé - utilisation de Yahoo Finance
from ..core.api_config import api_config
from ..components.symbol_search import default_symbol_search
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State, ALL
from typing import List, Dict
from datetime import datetime, timedelta
import requests
from decimal import Decimal

class StocksModule(BaseMarketModule):
    """Stocks market module using Alpha Vantage API"""
    
    def __init__(self, calculators: Dict = None):
        # Get Alpha Vantage API key from config
        stocks_provider = api_config.get_provider('stocks', 'Alpha Vantage')
        api_key = stocks_provider['config'].get('api_key', '') if stocks_provider else ''
        
        super().__init__(
            market_type='stocks',
            data_provider=None,  # Utiliser Yahoo Finance ou Twelve Data
            calculators=calculators
        )
        
        self.popular_stocks = [
            # Tech Giants
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX',
            # Traditional Blue Chips
            'JPM', 'JNJ', 'PG', 'UNH', 'HD', 'MA', 'V', 'WMT', 'DIS', 'KO',
            # Financial
            'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP',
            # Industrial
            'BA', 'CAT', 'GE', 'MMM', 'HON',
            # Healthcare
            'PFE', 'ABBV', 'TMO', 'ABT', 'MRK', 'LLY',
            # Energy
            'XOM', 'CVX', 'COP', 'SLB',
            # ETFs
            'SPY', 'QQQ', 'IWM', 'VTI', 'VEA', 'VWO'
        ]
    
    def get_symbols_list(self) -> List[str]:
        """Get list of available stock symbols"""
        return self.popular_stocks
    
    def get_default_symbol(self) -> str:
        """Get default stock symbol"""
        return 'AAPL'
    
    def load_market_data(self, symbol: str, interval: str = '1h', limit: int = 200) -> pd.DataFrame:
        """Load stock market data from Alpha Vantage"""
        try:
            print(f"🔄 Loading stock data for {symbol}...")
            data = self.data_provider.get_stock_data(symbol, interval)
            
            if not data.empty:
                print(f"✅ {symbol}: {len(data)} stock data points loaded")
                return data
            else:
                print(f"⚠️ No stock data for {symbol}, using fallback")
                return self._create_fallback_stock_data(symbol)
                
        except Exception as e:
            print(f"❌ Error loading stock data for {symbol}: {e}")
            return self._create_fallback_stock_data(symbol)
    
    def get_layout(self):
        """Get complete stocks layout reproduisant exactement l'interface crypto"""
        return html.Div([
            
            # Graphique principal
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='main-chart',
                        style={'height': '500px'},
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToRemove': [
                                'pan2d', 'lasso2d', 'select2d',
                                'autoScale2d', 'hoverClosestCartesian'
                            ]
                        }
                    )
                ], width=12)
            ], className="mb-3"),
            
            # Indicateurs secondaires
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='rsi-chart', style={'height': '200px'})
                ], width=4),
                dbc.Col([
                    dcc.Graph(id='volume-chart', style={'height': '200px'})
                ], width=4),
                dbc.Col([
                    dcc.Graph(id='atr-chart', style={'height': '200px'})
                ], width=4)
            ]),
            
            # Tab AI Insights
            dbc.Tabs([
                dbc.Tab(
                    label="🧠 AI Insights",
                    tab_id="ai-tab",
                    children=[
                        html.Div([
                            self.create_ai_dashboard()
                        ], className="p-3")
                    ]
                )
                
            ], id="secondary-tabs", active_tab="ai-tab", className="custom-tabs mt-3")
            
        ], className="p-3")
    
    def get_sidebar(self):
        """Get sidebar with stocks-specific controls"""
        return dbc.Card([
            dbc.CardBody([
                
                # Section Timeframe
                html.Div([
                    html.H6([
                        html.I(className="fas fa-clock me-2"),
                        "Timeframe"
                    ], className="text-primary border-bottom border-secondary pb-2 mb-3"),
                    
                    dcc.Dropdown(
                        id='stocks-timeframe-selector',
                        options=[
                            {'label': '🔥 1m - Scalping', 'value': '1m'},
                            {'label': '⚡ 5m - Quick Trades', 'value': '5m'},
                            {'label': '📊 15m - Short Term', 'value': '15m'},
                            {'label': '📈 1h - Day Trading', 'value': '1h'},
                            {'label': '📅 4h - Swing', 'value': '4h'},
                            {'label': '🏛️ 1D - Position', 'value': '1d'}
                        ],
                        value='1h',
                        className="mb-3"
                    )
                    
                ], className="mb-4"),
                
                # Section Indicateurs Techniques
                html.Div([
                    html.H6([
                        html.I(className="fas fa-chart-line me-2"),
                        "Technical Indicators"
                    ], className="text-info border-bottom border-secondary pb-2 mb-3"),
                    
                    self.create_indicator_controls(),
                    
                ], className="mb-4"),
                
                # Section IA
                html.Div([
                    html.H6([
                        html.I(className="fas fa-brain me-2"),
                        "AI Analysis"
                    ], className="text-warning border-bottom border-secondary pb-2 mb-3"),
                    
                    self.create_ai_controls(),
                    
                ], className="mb-4"),
                
                # Section Alertes
                html.Div([
                    html.H6([
                        html.I(className="fas fa-bell me-2"),
                        "Smart Alerts"
                    ], className="text-danger border-bottom border-secondary pb-2 mb-3"),
                    
                    self.create_alerts_controls(),
                    
                ])
                
            ])
        ], className="h-100", style={'backgroundColor': '#1f2937'})
    
    def _create_fallback_stock_data(self, symbol: str) -> pd.DataFrame:
        """Create fallback stock data when API unavailable"""
        print(f"📊 Creating fallback stock data for {symbol}")
        
        # Base prices for popular stocks
        base_prices = {
            # Tech Giants
            'AAPL': 175.50, 'MSFT': 415.20, 'GOOGL': 140.30, 'AMZN': 145.80,
            'META': 325.40, 'TSLA': 245.60, 'NVDA': 875.30, 'NFLX': 385.90,
            # Blue Chips
            'JPM': 155.20, 'JNJ': 168.30, 'PG': 152.40, 'UNH': 485.70,
            'HD': 325.80, 'MA': 425.90, 'V': 245.60, 'WMT': 165.20,
            'DIS': 95.40, 'KO': 58.70,
            # Financial
            'BAC': 32.45, 'WFC': 45.30, 'GS': 385.20, 'MS': 88.50,
            'C': 52.80, 'AXP': 185.40,
            # ETFs
            'SPY': 485.20, 'QQQ': 385.60, 'IWM': 195.30, 'VTI': 245.80
        }
        
        base_price = base_prices.get(symbol, 100.0)
        
        # Generate realistic stock data
        dates = pd.date_range(end=datetime.now(), periods=200, freq='H')
        
        df_data = []
        current_price = base_price
        
        for i, date in enumerate(dates):
            # Stock market volatility (moderate, less than crypto)
            change = (pd.np.random.randn() * 0.015) + (0.001 * pd.np.sin(i/6))
            current_price *= (1 + change)
            
            # Ensure reasonable stock price range
            current_price = max(current_price, base_price * 0.5)
            
            # Create OHLCV data with stock-like characteristics
            high = current_price * (1 + abs(pd.np.random.randn() * 0.008))
            low = current_price * (1 - abs(pd.np.random.randn() * 0.008))
            open_price = current_price * (1 + pd.np.random.randn() * 0.003)
            
            # Stock volume patterns (higher during market hours)
            hour = date.hour
            if 9 <= hour <= 16:  # Market hours
                volume = int(pd.np.random.randint(500000, 5000000))
            else:
                volume = int(pd.np.random.randint(50000, 500000))
            
            df_data.append({
                'timestamp': date,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(current_price, 2),
                'volume': volume
            })
        
        df = pd.DataFrame(df_data)
        df.index = df['timestamp']
        return df
    
    def get_stocks_specific_analysis(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Get stocks-specific analysis and insights"""
        if data.empty:
            return {}
        
        analysis = {
            'sector': self._get_sector(symbol),
            'market_cap': self._get_market_cap_category(symbol),
            'volatility': self._calculate_stock_volatility(data),
            'volume_analysis': self._analyze_stock_volume(data),
            'valuation_metrics': self._get_valuation_metrics(symbol),
            'earnings_info': self._get_earnings_info(symbol)
        }
        
        return analysis
    
    def _get_sector(self, symbol: str) -> str:
        """Get sector classification for stock"""
        sectors = {
            # Technology
            'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology',
            'AMZN': 'Technology', 'META': 'Technology', 'NVDA': 'Technology',
            'NFLX': 'Technology', 'TSLA': 'Technology',
            
            # Healthcare
            'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'ABBV': 'Healthcare',
            'UNH': 'Healthcare', 'TMO': 'Healthcare', 'ABT': 'Healthcare',
            'MRK': 'Healthcare', 'LLY': 'Healthcare',
            
            # Financial
            'JPM': 'Financial', 'BAC': 'Financial', 'WFC': 'Financial',
            'GS': 'Financial', 'MS': 'Financial', 'C': 'Financial',
            'AXP': 'Financial', 'MA': 'Financial', 'V': 'Financial',
            
            # Consumer Goods
            'PG': 'Consumer Goods', 'KO': 'Consumer Goods', 'WMT': 'Consumer Goods',
            'HD': 'Consumer Goods', 'DIS': 'Consumer Goods',
            
            # Industrial
            'BA': 'Industrial', 'CAT': 'Industrial', 'GE': 'Industrial',
            'MMM': 'Industrial', 'HON': 'Industrial',
            
            # Energy
            'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy', 'SLB': 'Energy'
        }
        
        return sectors.get(symbol, 'Diversified')
    
    def _get_market_cap_category(self, symbol: str) -> str:
        """Categorize stock by market cap"""
        large_cap = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 
                    'JPM', 'JNJ', 'PG', 'UNH', 'HD', 'MA', 'V', 'WMT']
        mid_cap = ['DIS', 'KO', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP']
        
        if symbol in large_cap:
            return 'Large Cap (>$10B)'
        elif symbol in mid_cap:
            return 'Mid Cap ($2B-$10B)'
        else:
            return 'Small Cap (<$2B)'
    
    def _calculate_stock_volatility(self, data: pd.DataFrame) -> Dict:
        """Calculate stock-specific volatility metrics"""
        if len(data) < 20:
            return {'daily_volatility': 0, 'beta_estimate': 1.0}
        
        # Daily returns
        returns = data['close'].pct_change().dropna()
        daily_volatility = float(returns.std() * 100)
        
        # Annualized volatility (assuming 252 trading days)
        annualized_volatility = daily_volatility * (252 ** 0.5)
        
        return {
            'daily_volatility': round(daily_volatility, 2),
            'annualized_volatility': round(annualized_volatility, 2),
            'volatility_category': self._categorize_stock_volatility(daily_volatility)
        }
    
    def _categorize_stock_volatility(self, daily_vol: float) -> str:
        """Categorize stock volatility level"""
        if daily_vol > 3.0:
            return 'High Volatility'
        elif daily_vol > 1.5:
            return 'Medium Volatility'
        else:
            return 'Low Volatility'
    
    def _analyze_stock_volume(self, data: pd.DataFrame) -> Dict:
        """Analyze stock trading volume patterns"""
        if 'volume' not in data.columns or data['volume'].sum() == 0:
            return {'status': 'No volume data', 'trend': 'Unknown'}
        
        # Volume analysis
        recent_volume = data['volume'].tail(10).mean()
        historical_volume = data['volume'].mean()
        
        volume_ratio = recent_volume / historical_volume if historical_volume > 0 else 1
        
        # Volume trend analysis
        if volume_ratio > 2.0:
            trend = 'Exceptional Activity'
        elif volume_ratio > 1.5:
            trend = 'High Activity'
        elif volume_ratio > 1.2:
            trend = 'Above Average'
        elif volume_ratio < 0.7:
            trend = 'Below Average'
        else:
            trend = 'Normal Activity'
        
        return {
            'volume_ratio': round(volume_ratio, 2),
            'trend': trend,
            'recent_avg': f'{recent_volume:,.0f}',
            'historical_avg': f'{historical_volume:,.0f}'
        }
    
    def _get_valuation_metrics(self, symbol: str) -> Dict:
        """Get estimated valuation metrics (simplified)"""
        # Simplified P/E estimates based on sector
        pe_estimates = {
            'Technology': 25.0, 'Healthcare': 18.0, 'Financial': 12.0,
            'Consumer Goods': 22.0, 'Industrial': 16.0, 'Energy': 14.0
        }
        
        sector = self._get_sector(symbol)
        estimated_pe = pe_estimates.get(sector, 20.0)
        
        return {
            'estimated_pe': estimated_pe,
            'sector_avg_pe': estimated_pe,
            'valuation': 'Fair' if 15 <= estimated_pe <= 25 else ('Expensive' if estimated_pe > 25 else 'Cheap')
        }
    
    def _get_earnings_info(self, symbol: str) -> Dict:
        """Get earnings-related information"""
        # Simplified earnings calendar (mock data)
        import random
        
        days_to_earnings = random.randint(5, 90)
        
        return {
            'next_earnings': f'In {days_to_earnings} days',
            'last_earnings': 'Beat estimates',
            'consensus': 'Hold',
            'analysts_target': 'Price target range varies by analyst'
        }
    
    def create_stocks_ai_dashboard(self) -> dict:
        """Create stocks-specific AI insights"""
        return {
            'sentiment_example': 'Bullish',
            'confidence': '72%',
            'prediction': '+8.3%',
            'analysis': 'Strong fundamentals with positive earnings outlook. Sector rotation favoring growth stocks.',
            'key_levels': {
                'support': '$165.20',
                'resistance': '$182.50'
            },
            'earnings_calendar': [
                {'date': '2024-01-15', 'company': 'Major Bank Earnings', 'impact': 'High'},
                {'date': '2024-01-18', 'company': 'Tech Earnings Season', 'impact': 'High'}
            ],
            'analyst_ratings': {
                'buy': 8,
                'hold': 5,
                'sell': 1,
                'average_target': '$185.00'
            }
        }
    
    def create_indicator_controls(self):
        """Contrôles des indicateurs techniques"""
        
        return html.Div([
            
            # SMA
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Switch(
                            id="sma-switch",
                            label="SMA",
                            value=True,
                            className="mb-2"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Input(
                            id="sma-period",
                            type="number",
                            value=20,
                            min=5,
                            max=100,
                            size="sm"
                        )
                    ], width=6)
                ], align="center")
            ], className="mb-3"),
            
            # EMA
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Switch(
                            id="ema-switch",
                            label="EMA",
                            value=True,
                            className="mb-2"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Input(
                            id="ema-period",
                            type="number",
                            value=12,
                            min=5,
                            max=100,
                            size="sm"
                        )
                    ], width=6)
                ], align="center")
            ], className="mb-3"),
            
            # RSI
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Switch(
                            id="rsi-switch",
                            label="RSI",
                            value=True,
                            className="mb-2"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Input(
                            id="rsi-period",
                            type="number",
                            value=14,
                            min=5,
                            max=30,
                            size="sm"
                        )
                    ], width=6)
                ], align="center")
            ], className="mb-3"),
            
            # ATR
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Switch(
                            id="atr-switch",
                            label="ATR",
                            value=True,
                            className="mb-2"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Input(
                            id="atr-period",
                            type="number",
                            value=14,
                            min=5,
                            max=30,
                            size="sm"
                        )
                    ], width=6)
                ], align="center")
            ], className="mb-3")
            
        ])
    
    def create_ai_controls(self):
        """Contrôles IA avec options gratuites identiques aux modules crypto/forex"""
        
        return html.Div([
            
            dbc.Switch(
                id="ai-enabled",
                label="Enable AI Analysis (FREE)",
                value=True,
                className="mb-3"
            ),
            
            dbc.Select(
                id="ai-model",
                options=[
                    {"label": "🆓 IA Locale (Gratuite)", "value": "local"},
                    {"label": "🌐 IA Publique (100/jour)", "value": "free_public"},
                    {"label": "🧠 IA Hybride (10€/mois)", "value": "smart"}
                ],
                value="local",
                size="sm",
                className="mb-3"
            ),
            
            html.Div([
                dbc.Label("AI Confidence Threshold", size="sm"),
                dcc.Slider(
                    id="ai-confidence",
                    min=0,
                    max=100,
                    step=5,
                    value=75,
                    marks={0: '0%', 50: '50%', 100: '100%'},
                    className="mb-3"
                )
            ]),
            
            dbc.Button([
                html.I(className="fas fa-brain me-2"),
                "Generate AI Insights (FREE)"
            ], id="ai-insights-btn", color="success", size="sm", className="w-100")
            
        ])
    
    def create_alerts_controls(self):
        """Contrôles des alertes"""
        
        return html.Div([
            
            dbc.Switch(
                id="alerts-enabled",
                label="Enable Alerts",
                value=True,
                className="mb-3"
            ),
            
            html.Div([
                dbc.Label("Price Alerts", size="sm", className="mb-2"),
                
                dbc.InputGroup([
                    dbc.InputGroupText("Above"),
                    dbc.Input(id="alert-price-high", type="number", placeholder="Price"),
                    dbc.InputGroupText("$")
                ], size="sm", className="mb-2"),
                
                dbc.InputGroup([
                    dbc.InputGroupText("Below"),
                    dbc.Input(id="alert-price-low", type="number", placeholder="Price"),
                    dbc.InputGroupText("$")
                ], size="sm", className="mb-3")
            ]),
            
            html.Div([
                dbc.Label("Technical Alerts", size="sm", className="mb-2"),
                
                dbc.Checklist(
                    id="technical-alerts",
                    options=[
                        {"label": "RSI Overbought/Oversold", "value": "rsi"},
                        {"label": "Moving Average Cross", "value": "ma_cross"},
                        {"label": "Breakout Detection", "value": "breakout"},
                        {"label": "Volume Spike", "value": "volume"}
                    ],
                    value=["rsi", "ma_cross"],
                    className="small"
                )
            ]),
            
        ])
    
    def create_ai_dashboard(self):
        """Dashboard IA avec insights dynamiques utilisant IA locale gratuite pour stocks"""
        
        return html.Div([
            
            # Insights cards avec données IA locale pour stocks
            dbc.Row([
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-bar me-2"),
                            "Earnings Sentiment (AI)"
                        ]),
                        dbc.CardBody([
                            html.Div(id="ai-sentiment-display", children=[
                                html.H3("Analyzing...", className="text-info"),
                                html.P("Earnings sentiment loading...", className="text-muted")
                            ])
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-line me-2"),
                            "Technical Analysis (AI)"
                        ]),
                        dbc.CardBody([
                            html.Div(id="ai-technical-display", children=[
                                html.H3("Analyzing...", className="text-info"),
                                html.P("Technical patterns loading...", className="text-muted")
                            ])
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-brain me-2"),
                            "Trading Insight (AI)"
                        ]),
                        dbc.CardBody([
                            html.Div(id="ai-trading-display", children=[
                                html.H3("Analyzing...", className="text-info"),
                                html.P("Investment recommendations loading...", className="text-muted")
                            ])
                        ])
                    ])
                ], width=4)
                
            ], className="mb-4"),
            
            # AI Analysis Text détaillé
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-robot me-2"),
                    "AI Stock Analysis (100% FREE)"
                ]),
                dbc.CardBody([
                    html.Div(id="ai-insights-text", children=[
                        html.P("🔮 L'IA locale analyse le marché des actions...", className="text-info"),
                        html.P("📊 Analyse des tendances en cours...", className="text-muted"),
                        html.P("💡 Recommandations de trading en génération...", className="text-warning")
                    ])
                ])
            ])
            
        ])
    
    def calculate_real_sma(self, prices, period=20):
        """Calculer SMA réel"""
        return pd.Series(prices).rolling(window=period).mean().tolist()
    
    def calculate_real_ema(self, prices, period=12):
        """Calculer EMA réel"""
        return pd.Series(prices).ewm(span=period).mean().tolist()
    
    def calculate_real_rsi(self, prices, period=14):
        """Calculer RSI réel"""
        series = pd.Series(prices)
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50).tolist()
    
    def calculate_real_atr(self, highs, lows, closes, period=14):
        """Calculer ATR réel"""
        high_series = pd.Series(highs)
        low_series = pd.Series(lows) 
        close_series = pd.Series(closes)
        
        prev_close = close_series.shift(1)
        tr1 = high_series - low_series
        tr2 = abs(high_series - prev_close)
        tr3 = abs(low_series - prev_close)
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        return atr.fillna(0).tolist()
    
    def format_price_adaptive(self, price):
        """Formatage adaptatif du prix selon sa valeur"""
        return f"${price:.2f}"  # Stocks typically use 2 decimal places

    def setup_callbacks(self, app):
        """Setup callbacks pour les interactions IA stocks"""
        from dash.dependencies import Input, Output, State
        import time
        from ..ai_engine.local_ai_engine import LocalAIEngine
        
        local_ai_engine = LocalAIEngine()
        
        @app.callback(
            [Output('ai-sentiment-display', 'children'),
             Output('ai-technical-display', 'children'),
             Output('ai-trading-display', 'children'),
             Output('ai-insights-text', 'children')],
            [Input('ai-insights-btn', 'n_clicks'),
             Input('symbol-dropdown', 'value')],
            [State('ai-model', 'value'),
             State('ai-enabled', 'value')]
        )
        def update_stocks_ai_analysis(n_clicks, symbol, ai_model, ai_enabled):
            """Callback pour l'analyse IA en temps réel des stocks"""
            
            if not ai_enabled or not symbol:
                return (
                    html.P("IA désactivée", className="text-muted"),
                    html.P("IA désactivée", className="text-muted"),
                    html.P("IA désactivée", className="text-muted"),
                    html.P("💤 IA locale en veille. Activez l'analyse IA pour obtenir des insights.", className="text-info")
                )
            
            try:
                # Données de test adaptées aux stocks
                price_data = [175.20, 174.85, 176.30, 177.15, 175.90, 178.25, 179.40, 177.80, 180.15, 181.25]
                indicators = {
                    'rsi': 68.5,
                    'sma_20': 176.85,
                    'ema_12': 177.90,
                    'volume_ratio': 1.35,
                    'atr': 2.45
                }
                
                # Articles de test pour sentiment stocks
                news_articles = [
                    "Strong Q4 earnings beat expectations for tech sector",
                    "Federal Reserve maintains dovish stance on interest rates",
                    "Growth stocks showing renewed momentum after consolidation",
                    "Institutional buying increases in large-cap equities",
                    "Market volatility decreases as investor confidence returns"
                ]
                
                start_time = time.time()
                
                # Analyse IA locale spécialisée stocks
                sentiment_result = local_ai_engine.analyze_sentiment(news_articles, market_type="stocks")
                technical_result = local_ai_engine.analyze_technical_pattern_simple(price_data, indicators)
                trading_insight = local_ai_engine.generate_trading_insight_enhanced(
                    symbol, 
                    {'technical_analysis': technical_result},
                    sentiment_result,
                    market_type="stocks"
                )
                
                # Formatage résultats spécifiques stocks
                sentiment_display = html.Div([
                    html.H3(sentiment_result['sentiment'].title(), 
                           className=f"text-{'success' if sentiment_result['sentiment'] == 'bullish' else 'danger' if sentiment_result['sentiment'] == 'bearish' else 'warning'}"),
                    html.P(f"Confiance: {sentiment_result['confidence']:.1f}%", className="text-muted"),
                    html.Small(f"Earnings focus: {sentiment_result['analysis']['bullish_articles']} positifs")
                ])
                
                technical_display = html.Div([
                    html.H4(technical_result['pattern'], className="text-info"),
                    html.P(f"RSI: {indicators['rsi']:.1f}", className="small"),
                    html.P(f"Support: ${price_data[-1]:.2f}", className="small text-success"),
                    html.Small(" | ".join(technical_result.get('signals', ['Analyse en cours'])))
                ])
                
                trading_display = html.Div([
                    html.H4(trading_insight['action'], className=f"text-{'success' if trading_insight['action'] == 'BUY' else 'danger' if trading_insight['action'] == 'SELL' else 'warning'}"),
                    html.P(trading_insight['explanation'][:50] + "...", className="small"),
                    html.Small(trading_insight['strength'] + " Signal")
                ])
                
                execution_time = (time.time() - start_time) * 1000
                
                insights_text = html.Div([
                    html.P([
                        html.Strong("Earnings Sentiment: "),
                        f"{sentiment_result['analysis']['bullish_articles']} rapports positifs, "
                        f"{sentiment_result['analysis']['bearish_articles']} négatifs sur {sentiment_result['analysis']['total_articles']} analysés."
                    ]),
                    html.P([
                        html.Strong("Technical Analysis: "),
                        f"Pattern {technical_result['pattern']} détecté. " + 
                        (" | ".join(technical_result.get('signals', [])))
                    ]),
                    html.P([
                        html.Strong("Investment Recommendation: "),
                        trading_insight['explanation']
                    ]),
                    html.P([
                        html.Strong("IA Engine: "), 
                        f"🆓 Local AI (FREE) | ⚡ {execution_time:.0f}ms | Model: Stocks-optimized"
                    ], className="text-success small")
                ])
                
                return sentiment_display, technical_display, trading_display, insights_text
                
            except Exception as e:
                error_msg = html.P(f"❌ Erreur IA: {str(e)}", className="text-danger")
                return error_msg, error_msg, error_msg, error_msg

        def _calculate_simple_rsi(self, prices, period=14):
            """Helper pour RSI simplifié"""
            if len(prices) < period + 1:
                return 50.0
            
            gains = []
            losses = []
            
            for i in range(1, len(prices)):
                change = prices[i] - prices[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(-change)
            
            if len(gains) < period:
                return 50.0
                
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            if avg_loss == 0:
                return 100.0
                
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi