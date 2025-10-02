"""
Forex Market Module for THEBOT
Handles forex data using Alpha Vantage API
"""

from .base_market_module import BaseMarketModule
# AlphaVantage API supprimé - utilisation de Yahoo Finance et Binance
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

class ForexModule(BaseMarketModule):
    """Forex market module using Alpha Vantage API"""
    
    def __init__(self, calculators: Dict = None):
        # Get Alpha Vantage API key from config
        forex_provider = api_config.get_provider('forex', 'Alpha Vantage')
        api_key = forex_provider['config'].get('api_key', '') if forex_provider else ''
        
        super().__init__(
            market_type='forex',
            data_provider=None,  # Utiliser Twelve Data ou Yahoo Finance
            calculators=calculators
        )
        
        self.major_pairs = [
            'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
            'EURJPY', 'GBPJPY', 'EURGBP', 'EURAUD', 'EURCAD', 'EURCHF', 'GBPAUD',
            'GBPCAD', 'GBPCHF', 'AUDJPY', 'CADJPY', 'CHFJPY', 'AUDCAD', 'AUDCHF',
            'CADCHF', 'NZDJPY', 'AUDNZD'
        ]
    
    def get_symbols_list(self) -> List[str]:
        """Get list of available forex pairs"""
        return self.major_pairs
    
    def get_default_symbol(self) -> str:
        """Get default forex pair"""
        return 'EURUSD'
    
    def load_market_data(self, symbol: str, interval: str = '1h', limit: int = 200) -> pd.DataFrame:
        """Load forex market data from Alpha Vantage"""
        try:
            # Parse forex pair (e.g., EURUSD -> EUR, USD)
            if len(symbol) == 6:
                from_symbol = symbol[:3]
                to_symbol = symbol[3:]
            else:
                print(f"⚠️ Invalid forex pair format: {symbol}")
                return self._create_fallback_forex_data(symbol)
            
            print(f"🔄 Loading forex data for {from_symbol}/{to_symbol}...")
            data = self.data_provider.get_forex_data(from_symbol, to_symbol, interval)
            
            if not data.empty:
                print(f"✅ {symbol}: {len(data)} forex data points loaded")
                return data
            else:
                print(f"⚠️ No forex data for {symbol}, using fallback")
                return self._create_fallback_forex_data(symbol)
                
        except Exception as e:
            print(f"⚠️ Error loading forex data: {e}")
            return self._create_fallback_data(symbol)
    
    def get_layout(self):
        """Get complete forex layout reproduisant exactement l'interface crypto"""
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
    
    def _create_fallback_forex_data(self, symbol: str) -> pd.DataFrame:
        """Create fallback forex data when API unavailable"""
        print(f"📊 Creating fallback forex data for {symbol}")
        
        # Base rates for major forex pairs
        base_rates = {
            'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 149.50,
            'USDCHF': 0.8950, 'AUDUSD': 0.6450, 'USDCAD': 1.3750,
            'NZDUSD': 0.5950, 'EURJPY': 162.20, 'GBPJPY': 188.90,
            'EURGBP': 0.8580, 'EURAUD': 1.6840, 'EURCAD': 1.4920,
            'EURCHF': 0.9720, 'GBPAUD': 1.9650, 'GBPCAD': 1.7380,
            'GBPCHF': 1.1330, 'AUDJPY': 96.40, 'CADJPY': 108.80,
            'CHFJPY': 167.20, 'AUDCAD': 0.8860, 'AUDCHF': 0.5780,
            'CADCHF': 0.6520, 'NZDJPY': 89.10, 'AUDNZD': 1.0840
        }
        
        base_rate = base_rates.get(symbol, 1.0)
        
        # Generate realistic forex data
        dates = pd.date_range(end=datetime.now(), periods=200, freq='H')
        
        df_data = []
        current_rate = base_rate
        
        for i, date in enumerate(dates):
            # Forex volatility (lower than crypto, higher than bonds)
            change = (pd.np.random.randn() * 0.005) + (0.0002 * pd.np.sin(i/12))
            current_rate *= (1 + change)
            
            # Ensure reasonable forex range
            current_rate = max(min(current_rate, base_rate * 1.2), base_rate * 0.8)
            
            # Create OHLC data with forex-like precision
            high = current_rate * (1 + abs(pd.np.random.randn() * 0.002))
            low = current_rate * (1 - abs(pd.np.random.randn() * 0.002))
            open_rate = current_rate * (1 + pd.np.random.randn() * 0.0005)
            
            df_data.append({
                'timestamp': date,
                'open': round(open_rate, 5),
                'high': round(high, 5),
                'low': round(low, 5),
                'close': round(current_rate, 5)
            })
        
        df = pd.DataFrame(df_data)
        df.index = df['timestamp']
        return df
    
    def get_forex_specific_analysis(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Get forex-specific analysis and insights"""
        if data.empty:
            return {}
        
        analysis = {
            'pair_type': self._get_pair_type(symbol),
            'volatility': self._calculate_forex_volatility(data),
            'range_analysis': self._analyze_daily_range(data),
            'correlation': self._get_correlation_info(symbol),
            'economic_factors': self._get_economic_factors(symbol)
        }
        
        return analysis
    
    def _get_pair_type(self, symbol: str) -> str:
        """Categorize forex pair type"""
        majors = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']
        crosses = ['EURJPY', 'GBPJPY', 'EURGBP', 'EURAUD', 'EURCAD', 'EURCHF']
        
        if symbol in majors:
            return 'Major Pair'
        elif symbol in crosses:
            return 'Cross Pair'
        else:
            return 'Exotic Pair'
    
    def _calculate_forex_volatility(self, data: pd.DataFrame) -> Dict:
        """Calculate forex-specific volatility metrics"""
        if len(data) < 2:
            return {'daily_range': 0, 'atr': 0}
        
        # Daily range (high - low)
        daily_ranges = data['high'] - data['low']
        avg_daily_range = float(daily_ranges.mean())
        
        # Average True Range for last 14 periods
        atr_values = self.calculate_atr(data, 14)
        current_atr = atr_values[-1] if atr_values else 0
        
        return {
            'daily_range': round(avg_daily_range * 10000, 1),  # In pips
            'atr': round(current_atr * 10000, 1),  # In pips
            'volatility_category': self._categorize_volatility(avg_daily_range)
        }
    
    def _categorize_volatility(self, daily_range: float) -> str:
        """Categorize forex volatility level"""
        pips = daily_range * 10000
        
        if pips > 150:
            return 'High Volatility'
        elif pips > 80:
            return 'Medium Volatility'
        else:
            return 'Low Volatility'
    
    def _analyze_daily_range(self, data: pd.DataFrame) -> Dict:
        """Analyze daily trading range patterns"""
        if len(data) < 24:
            return {'status': 'Insufficient data'}
        
        # Calculate ranges for different time periods
        last_24h = data.tail(24)
        ranges_24h = last_24h['high'] - last_24h['low']
        
        current_range = float(ranges_24h.iloc[-1] * 10000)  # Current range in pips
        avg_range = float(ranges_24h.mean() * 10000)  # Average range in pips
        
        return {
            'current_range_pips': round(current_range, 1),
            'average_range_pips': round(avg_range, 1),
            'range_efficiency': round((current_range / avg_range * 100), 1) if avg_range > 0 else 0
        }
    
    def get_sidebar(self):
        """Get sidebar with forex-specific controls"""
        return dbc.Card([
            dbc.CardBody([
                
                # Section Timeframe
                html.Div([
                    html.H6([
                        html.I(className="fas fa-clock me-2"),
                        "Timeframe"
                    ], className="text-primary border-bottom border-secondary pb-2 mb-3"),
                    
                    dcc.Dropdown(
                        id='forex-timeframe-selector',
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
        """Dashboard IA avec insights dynamiques forex utilisant IA locale gratuite"""
        
        return html.Div([
            
            # Insights cards avec données IA locale pour forex
            dbc.Row([
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-globe me-2"),
                            "Economic Sentiment (AI)"
                        ]),
                        dbc.CardBody([
                            html.Div(id="ai-sentiment-display", children=[
                                html.H3("Analyzing...", className="text-info"),
                                html.P("Economic sentiment loading...", className="text-muted")
                            ])
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-area me-2"),
                            "Forex Technical (AI)"
                        ]),
                        dbc.CardBody([
                            html.Div(id="ai-technical-display", children=[
                                html.H3("Analyzing...", className="text-info"),
                                html.P("Forex patterns loading...", className="text-muted")
                            ])
                        ])
                    ])
                ], width=4),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-exchange-alt me-2"),
                            "Forex Strategy (AI)"
                        ]),
                        dbc.CardBody([
                            html.Div(id="ai-trading-display", children=[
                                html.H3("Analyzing...", className="text-info"),
                                html.P("Currency strategy loading...", className="text-muted")
                            ])
                        ])
                    ])
                ], width=4)
                
            ], className="mb-4"),
            
            # AI Analysis Text détaillé pour forex
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-robot me-2"),
                    "AI Forex Analysis (100% FREE)"
                ]),
                dbc.CardBody([
                    html.Div(id="ai-insights-text", children=[
                        html.P([
                            html.Strong("IA Forex: "),
                            "Analyse en cours... L'IA locale gratuite analyse les tendances forex, événements économiques et corrélations."
                        ]),
                        html.P([
                            html.Strong("Facteurs économiques: "), 
                            "Surveillance automatique des calendriers économiques et impacts sur paires de devises."
                        ]),
                        html.P([
                            html.Strong("Coût: "), 
                            html.Span("0€/mois - Analyses forex illimitées", className="text-success fw-bold")
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
        if price >= 1:
            return f"{price:.4f}"  # Forex needs more precision
        elif price >= 0.01:
            return f"{price:.6f}"
        else:
            return f"{price:.8f}"
    
    def _get_correlation_info(self, symbol: str) -> Dict:
        """Get correlation information for forex pair"""
        correlations = {
            'EURUSD': {'positive': ['GBPUSD', 'AUDUSD'], 'negative': ['USDCHF', 'USDJPY']},
            'GBPUSD': {'positive': ['EURUSD', 'AUDUSD'], 'negative': ['USDCHF', 'USDJPY']},
            'USDJPY': {'positive': ['USDCHF'], 'negative': ['EURUSD', 'GBPUSD', 'AUDUSD']},
            'USDCHF': {'positive': ['USDJPY'], 'negative': ['EURUSD', 'GBPUSD', 'AUDUSD']},
            'AUDUSD': {'positive': ['EURUSD', 'GBPUSD'], 'negative': ['USDCHF', 'USDJPY']},
            'USDCAD': {'positive': ['USDJPY'], 'negative': ['EURUSD', 'GBPUSD']}
        }
        
        return correlations.get(symbol, {'positive': [], 'negative': []})
    
    def _get_economic_factors(self, symbol: str) -> Dict:
        """Get key economic factors affecting the forex pair"""
        factors = {
            'EURUSD': {
                'base_currency': 'EUR',
                'quote_currency': 'USD',
                'key_factors': ['ECB Policy', 'Fed Policy', 'EU-US Interest Rate Differential'],
                'session_activity': ['London', 'New York']
            },
            'GBPUSD': {
                'base_currency': 'GBP', 
                'quote_currency': 'USD',
                'key_factors': ['BoE Policy', 'Fed Policy', 'Brexit Impact', 'UK Economic Data'],
                'session_activity': ['London', 'New York']
            },
            'USDJPY': {
                'base_currency': 'USD',
                'quote_currency': 'JPY', 
                'key_factors': ['Fed Policy', 'BoJ Policy', 'Risk Sentiment', 'US-Japan Yield Spread'],
                'session_activity': ['Tokyo', 'New York']
            }
        }
        
        return factors.get(symbol, {
            'base_currency': symbol[:3] if len(symbol) >= 3 else 'N/A',
            'quote_currency': symbol[3:] if len(symbol) >= 6 else 'N/A',
            'key_factors': ['Central Bank Policy', 'Economic Data', 'Market Sentiment'],
            'session_activity': ['Major Sessions']
        })
    
    def create_forex_ai_dashboard(self) -> dict:
        """Create forex-specific AI insights"""
        return {
            'sentiment_example': 'Neutral',
            'confidence': '65%',
            'prediction': '+0.8%',
            'analysis': 'Consolidation phase ahead of central bank meetings. Watch for ECB dovish signals and Fed hawkish stance.',
            'key_levels': {
                'support': '1.0820',
                'resistance': '1.0890'
            },
            'economic_calendar': [
                {'time': '14:30', 'event': 'US GDP', 'impact': 'High'},
                {'time': '16:00', 'event': 'ECB Minutes', 'impact': 'Medium'}
            ]
        }