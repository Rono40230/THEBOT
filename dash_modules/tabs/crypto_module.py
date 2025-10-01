"""
Crypto Market Module for THEBOT
Handles cryptocurrency data using Binance API
"""

from .base_market_module import BaseMarketModule
from ..data_providers.binance_api import binance_provider
from ..components.symbol_search import default_symbol_search
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import datetime
from dash.dependencies import Input, Output, State, ALL
from typing import List, Dict
from datetime import datetime, timedelta
import requests
from decimal import Decimal

class CryptoModule(BaseMarketModule):
    """Crypto market module using Binance API"""
    
    def __init__(self, calculators: Dict = None):
        super().__init__(
            market_type='crypto',
            data_provider=binance_provider,
            calculators=calculators
        )
        self.popular_symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'MATICUSDT', 'SHIBUSDT',
            'AVAXUSDT', 'LTCUSDT', 'UNIUSDT', 'LINKUSDT', 'ATOMUSDT',
            'ETCUSDT', 'XLMUSDT', 'BCHUSDT', 'FILUSDT', 'THETAUSDT',
            'VETUSDT', 'TRXUSDT', 'EOSUSDT', 'AAVEUSDT', 'MKRUSDT',
            'COMPUSDT', 'YFIUSDT', 'SUSHIUSDT', 'SNXUSDT', 'CRVUSDT',
            'PEPEUSDT', 'FLOKIUSDT', 'BONKUSDT', '1000SATSUSDT'
        ]
    
    def get_symbols_list(self) -> List[str]:
        """Get list of available crypto symbols"""
        try:
            symbols = self.data_provider.get_all_symbols()
            return symbols if symbols else self.popular_symbols
        except Exception as e:
            print(f"⚠️ Error loading crypto data: {e}")
            return self._create_fallback_data(symbol)
    
    def get_layout(self):
        """Get complete crypto layout reproducing the exact interface from the image"""
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
        """Get sidebar with crypto-specific controls"""
        return dbc.Card([
            dbc.CardBody([
                
                # Section Timeframe
                html.Div([
                    html.H6([
                        html.I(className="fas fa-clock me-2"),
                        "Timeframe"
                    ], className="text-primary border-bottom border-secondary pb-2 mb-3"),
                    
                    dcc.Dropdown(
                        id='crypto-timeframe-selector',
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
    
    def get_default_symbol(self) -> str:
        """Get default crypto symbol"""
        return 'BTCUSDT'
    
    def load_market_data(self, symbol: str, interval: str = '1h', limit: int = 200) -> pd.DataFrame:
        """Load crypto market data from Binance"""
        try:
            print(f"🔄 Loading crypto data for {symbol}...")
            data = self.data_provider.get_binance_data(symbol, interval, limit)
            
            if not data.empty:
                print(f"✅ {symbol}: {len(data)} crypto data points loaded")
                return data
            else:
                print(f"⚠️ No crypto data for {symbol}, using fallback")
                return self._create_fallback_crypto_data(symbol)
                
        except Exception as e:
            print(f"❌ Error loading crypto data for {symbol}: {e}")
            return self._create_fallback_crypto_data(symbol)
    
    def _create_fallback_crypto_data(self, symbol: str) -> pd.DataFrame:
        """Create fallback crypto data when API unavailable"""
        print(f"📊 Creating fallback crypto data for {symbol}")
        
        # Base prices for popular cryptos
        base_prices = {
            'BTCUSDT': 65000.0, 'ETHUSDT': 2500.0, 'BNBUSDT': 315.0,
            'ADAUSDT': 0.45, 'XRPUSDT': 0.62, 'SOLUSDT': 145.0,
            'DOGEUSDT': 0.085, 'DOTUSDT': 6.50, 'MATICUSDT': 0.75,
            'SHIBUSDT': 0.000018, 'AVAXUSDT': 28.5, 'LTCUSDT': 75.0,
            'PEPEUSDT': 0.000007869, 'FLOKIUSDT': 0.000145
        }
        
        base_price = base_prices.get(symbol, 100.0)
        
        # Generate realistic crypto data
        dates = pd.date_range(end=datetime.now(), periods=200, freq='H')
        
        df_data = []
        current_price = base_price
        
        for i, date in enumerate(dates):
            # Crypto volatility (higher than traditional markets)
            change = (pd.np.random.randn() * 0.025) + (0.002 * pd.np.sin(i/8))
            current_price *= (1 + change)
            
            # Ensure positive price
            current_price = max(current_price, base_price * 0.01)
            
            # Create OHLCV data with crypto-like volatility
            high = current_price * (1 + abs(pd.np.random.randn() * 0.015))
            low = current_price * (1 - abs(pd.np.random.randn() * 0.015))
            open_price = current_price * (1 + pd.np.random.randn() * 0.005)
            
            # Crypto volume patterns
            volume = int(pd.np.random.randint(100000, 5000000))
            
            # Format according to symbol type
            if 'USDT' in symbol and base_price < 1:
                # Small cap cryptos
                decimals = 8 if base_price < 0.001 else 6
            else:
                # Major cryptos
                decimals = 2
            
            df_data.append({
                'timestamp': date,
                'open': round(open_price, decimals),
                'high': round(high, decimals),
                'low': round(low, decimals), 
                'close': round(current_price, decimals),
                'volume': volume
            })
        
        df = pd.DataFrame(df_data)
        df.index = df['timestamp']
        return df
    
    def get_crypto_specific_analysis(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Get crypto-specific analysis and insights"""
        if data.empty:
            return {}
        
        analysis = {
            'market_cap_category': self._get_market_cap_category(symbol),
            'volatility': self._calculate_volatility(data),
            'volume_analysis': self._analyze_volume(data),
            'support_resistance': self._find_support_resistance(data),
            'trend_strength': self._calculate_trend_strength(data)
        }
        
        return analysis
    
    def _get_market_cap_category(self, symbol: str) -> str:
        """Categorize crypto by market cap"""
        large_cap = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'SOLUSDT']
        mid_cap = ['DOGEUSDT', 'DOTUSDT', 'MATICUSDT', 'AVAXUSDT', 'LTCUSDT', 'LINKUSDT']
        
        if symbol in large_cap:
            return 'Large Cap'
        elif symbol in mid_cap:
            return 'Mid Cap'
        else:
            return 'Small Cap'
    
    def _calculate_volatility(self, data: pd.DataFrame) -> float:
        """Calculate crypto volatility (24h price change %)"""
        if len(data) < 2:
            return 0.0
        
        price_changes = data['close'].pct_change().dropna()
        return float(price_changes.std() * 100)
    
    def _analyze_volume(self, data: pd.DataFrame) -> Dict:
        """Analyze trading volume patterns"""
        if 'volume' not in data.columns or data['volume'].sum() == 0:
            return {'status': 'No volume data', 'trend': 'Unknown'}
        
        recent_volume = data['volume'].tail(24).mean()
        historical_volume = data['volume'].mean()
        
        volume_ratio = recent_volume / historical_volume if historical_volume > 0 else 1
        
        if volume_ratio > 1.5:
            trend = 'High Activity'
        elif volume_ratio > 1.2:
            trend = 'Increased Activity' 
        elif volume_ratio < 0.8:
            trend = 'Low Activity'
        else:
            trend = 'Normal Activity'
        
        return {
            'status': f'Volume Ratio: {volume_ratio:.2f}x',
            'trend': trend,
            'recent_avg': f'{recent_volume:,.0f}',
            'historical_avg': f'{historical_volume:,.0f}'
        }
    
    def _find_support_resistance(self, data: pd.DataFrame) -> Dict:
        """Find key support and resistance levels"""
        if len(data) < 50:
            return {'support': 0, 'resistance': 0}
        
        highs = data['high'].tail(100)
        lows = data['low'].tail(100)
        
        # Simple support/resistance based on recent price action
        resistance = float(highs.quantile(0.9))
        support = float(lows.quantile(0.1))
        
        return {
            'support': support,
            'resistance': resistance,
            'current_position': self._get_price_position(data['close'].iloc[-1], support, resistance)
        }
    
    def _get_price_position(self, current_price: float, support: float, resistance: float) -> str:
        """Determine current price position relative to support/resistance"""
        range_size = resistance - support
        if range_size == 0:
            return 'Neutral'
        
        position = (current_price - support) / range_size
        
        if position > 0.8:
            return 'Near Resistance'
        elif position < 0.2:
            return 'Near Support'
        elif position > 0.6:
            return 'Upper Range'
        elif position < 0.4:
            return 'Lower Range'
        else:
            return 'Mid Range'
    
    def _calculate_trend_strength(self, data: pd.DataFrame) -> Dict:
        """Calculate trend strength and direction"""
        if len(data) < 20:
            return {'direction': 'Unknown', 'strength': 0}
        
        # Simple trend calculation using price changes
        short_ma = data['close'].tail(10).mean()
        long_ma = data['close'].tail(20).mean()
        
        if short_ma > long_ma * 1.02:
            direction = 'Strong Uptrend'
            strength = min(100, abs((short_ma / long_ma - 1) * 100))
        elif short_ma > long_ma * 1.005:
            direction = 'Weak Uptrend'
            strength = abs((short_ma / long_ma - 1) * 100)
        elif short_ma < long_ma * 0.98:
            direction = 'Strong Downtrend'
            strength = min(100, abs((short_ma / long_ma - 1) * 100))
        elif short_ma < long_ma * 0.995:
            direction = 'Weak Downtrend'
            strength = abs((short_ma / long_ma - 1) * 100)
        else:
            direction = 'Sideways'
            strength = 0
        
        return {
            'direction': direction,
            'strength': round(strength, 1)
        }
    
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
            return f"{price:.2f}"
        elif price >= 0.01:
            return f"{price:.4f}"
        elif price >= 0.0001:
            return f"{price:.6f}"
        else:
            return f"{price:.8f}"
    
    def setup_callbacks(self, app):
        """Configuration des callbacks spécifiques au module crypto"""
        from dash import Input, Output, State
        
        @app.callback(
            Output('market-data-store', 'data', allow_duplicate=True),
            [Input('crypto-timeframe-selector', 'value')],
            [State('main-symbol-selected', 'data')],
            prevent_initial_call=True
        )
        def on_crypto_timeframe_change(new_timeframe, current_symbol):
            """Déclencher un rechargement quand le timeframe crypto change"""
            if current_symbol and new_timeframe:
                try:
                    data = self.load_market_data(current_symbol, new_timeframe)
                    if not data.empty:
                        return {
                            'symbol': current_symbol,
                            'data': data.to_json(date_format='iso'),
                            'timestamp': datetime.now().isoformat(),
                            'timeframe': new_timeframe
                        }
                except Exception as e:
                    print(f"❌ Erreur changement timeframe crypto: {e}")
            return {}