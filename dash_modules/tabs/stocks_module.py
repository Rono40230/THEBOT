"""
Stocks Market Module for THEBOT
Handles stock data using Alpha Vantage API
"""

from .base_market_module import BaseMarketModule
from ..data_providers.alpha_vantage_api import AlphaVantageAPI
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
            data_provider=AlphaVantageAPI(api_key),
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
        """Contrôles IA"""
        
        return html.Div([
            
            dbc.Switch(
                id="ai-enabled",
                label="Enable AI Analysis",
                value=False,
                className="mb-3"
            ),
            
            dbc.Select(
                id="ai-model",
                options=[
                    {"label": "🤖 GPT-4 Turbo", "value": "gpt4"},
                    {"label": "🧠 Claude-3.5 Sonnet", "value": "claude"},
                    {"label": "⚡ Custom LSTM", "value": "lstm"}
                ],
                value="gpt4",
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
                html.I(className="fas fa-magic me-2"),
                "Generate Insights"
            ], id="ai-insights-btn", color="warning", size="sm", className="w-100", disabled=True)
            
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
        """Dashboard IA avec insights reproduisant exactement l'interface de l'image"""
        
        return html.Div([
            
            # Insights cards directement
            dbc.Row([
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-trend-up me-2"),
                            "Market Sentiment"
                        ]),
                        dbc.CardBody([
                            html.H3("Bullish", className="text-success"),
                            html.P("Confidence: 78%", className="text-muted"),
                            dcc.Graph(
                                figure=px.pie(
                                    values=[78, 22], 
                                    names=['Bullish', 'Bearish'],
                                    color_discrete_map={'Bullish': '#10b981', 'Bearish': '#ef4444'}
                                ).update_layout(
                                    showlegend=False,
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    height=200
                                ),
                                style={'height': '200px'}
                            )
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-line me-2"),
                            "Price Prediction"
                        ]),
                        dbc.CardBody([
                            html.H3("+2.3%", className="text-info"),
                            html.P("Next 24h target", className="text-muted"),
                            # Mini chart de prédiction
                            html.Div("Prediction chart placeholder", className="text-center p-4 bg-secondary rounded")
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-exclamation-triangle me-2"),
                            "Risk Assessment"
                        ]),
                        dbc.CardBody([
                            html.H3("Medium", className="text-warning"),
                            html.P("Volatility expected", className="text-muted"),
                            dbc.Progress(value=60, color="warning", className="mb-2"),
                            html.Small("Risk Score: 60/100")
                        ])
                    ])
                ], width=4)
                
            ], className="mb-4"),
            
            # AI Insights Text
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-brain me-2"),
                    "AI Market Analysis"
                ]),
                dbc.CardBody([
                    html.Div(id="ai-insights-text", children=[
                        html.P([
                            html.Strong("Technical Analysis: "),
                            "The market is showing strong bullish momentum with RSI at 67, indicating room for further upside. "
                            "The 20-period SMA is acting as dynamic support."
                        ]),
                        html.P([
                            html.Strong("Volume Analysis: "), 
                            "Above-average volume confirms the current price action. "
                            "Smart money appears to be accumulating."
                        ]),
                        html.P([
                            html.Strong("Economic Context: "),
                            "Upcoming Fed decision could introduce volatility. "
                            "Market positioning suggests preparation for dovish outcome."
                        ])
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