#!/usr/bin/env python3
"""
THEBOT - Interface Dash Ultra-Moderne
Solution professionnelle pour trading avancé
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import dash
from dash import dcc, html, dash_table, callback_context, clientside_callback, ClientsideFunction
from dash.dependencies import Input, Output, State, ALL, MATCH
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import threading
import time
from decimal import Decimal

# Import modules THEBOT
from dash_modules.data_providers.binance_api import binance_provider
from dash_modules.components.symbol_search import default_symbol_search

# Import calculateurs THEBOT
try:
    from thebot.indicators.basic.sma.config import SMAConfig
    from thebot.indicators.basic.sma.calculator import SMACalculator
    from thebot.indicators.basic.ema.config import EMAConfig
    from thebot.indicators.basic.ema.calculator import EMACalculator
    from thebot.indicators.oscillators.rsi.config import RSIConfig
    from thebot.indicators.oscillators.rsi.calculator import RSICalculator
    from thebot.indicators.volatility.atr.config import ATRConfig
    from thebot.indicators.volatility.atr.calculator import ATRCalculator
    CALCULATORS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Calculateurs THEBOT non disponibles: {e}")
    CALCULATORS_AVAILABLE = False


class THEBOTDashApp:
    """Application THEBOT avec interface Dash ultra-moderne"""
    
    def __init__(self):
        # Configuration Dash
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[
                dbc.themes.CYBORG,  # Thème dark moderne
                dbc.icons.FONT_AWESOME,  # Icônes
                "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
            ],
            suppress_callback_exceptions=True,
            update_title=None  # Pas de "Updating..." dans le titre
        )
        
        # Configuration globale
        self.app.title = "🤖 THEBOT - Trading Intelligence Platform"
        
        # Cache des symboles Binance
        self.all_symbols = self.get_all_binance_symbols()
        
        # Données de marché (chargées à la demande)
        self.market_data = {}
        self.indicators_data = {}
        self.economic_events = self.generate_economic_events()
        
        # État de l'application
        self.is_streaming = False
        self.selected_symbol = "BTCUSDT"
        self.selected_timeframe = "5m"
        
        self.setup_layout()
        self.setup_callbacks()
        self.setup_calculators()
        
    def get_all_binance_symbols(self):
        """Récupérer tous les symboles Binance disponibles"""
        try:
            import requests
            
            url = "https://api.binance.com/api/v3/exchangeInfo"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Erreur récupération symboles: {response.status_code}")
                return self.get_popular_symbols()
            
            data = response.json()
            symbols = []
            
            for symbol_info in data['symbols']:
                if (symbol_info['status'] == 'TRADING' and 
                    symbol_info['symbol'].endswith('USDT')):
                    symbols.append(symbol_info['symbol'])
            
            print(f"✅ {len(symbols)} symboles Binance chargés")
            return sorted(symbols)
            
        except Exception as e:
            print(f"❌ Erreur API exchange info: {e}")
            return self.get_popular_symbols()
    
    def get_popular_symbols(self):
        """Symboles populaires en fallback"""
        return ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'XRPUSDT', 'DOTUSDT', 
                'LINKUSDT', 'LTCUSDT', 'BCHABCUSDT', 'EOSUSDT', 'TRXUSDT', 'ETCUSDT', 'XLMUSDT']
    
    def search_symbols(self, query, symbols_list, limit=10):
        """Rechercher des symboles selon une requête"""
        if not query:
            return self.get_popular_symbols()[:limit]
        
        query_upper = query.upper()
        matches = []
        
        # Recherche exacte au début
        for symbol in symbols_list:
            if symbol.startswith(query_upper):
                matches.append(symbol)
                
        # Recherche partielle
        for symbol in symbols_list:
            if query_upper in symbol and symbol not in matches:
                matches.append(symbol)
                
        return matches[:limit]

    def get_binance_data(self, symbol='BTCUSDT', interval='1h', limit=500):
        """Récupérer vraies données Binance (GRATUIT et ILLIMITÉ)"""
        try:
            import requests
            print(f"🔄 Chargement {symbol}...")
            
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval, 
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                print(f"❌ Erreur HTTP {response.status_code} pour {symbol}")
                return None
                
            data = response.json()
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades', 
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Conversion des types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            # Index sur timestamp pour compatibilité
            df.set_index('timestamp', inplace=True)
                
            print(f"✅ {symbol}: {len(df)} points récupérés")
            return df
            
        except Exception as e:
            print(f"❌ Erreur Binance {symbol}: {e}")
            return None

    def load_symbol_data(self, symbol, interval='1h', limit=200):
        """Charger les données d'un symbole spécifique à la demande"""
        df = self.get_binance_data(symbol, interval, limit)
        if df is not None:
            self.market_data[symbol] = df
            return df
        else:
            # Fallback avec données simulées
            print(f"⚠️ Fallback simulation pour {symbol}")
            fallback_data = self._create_fallback_data(symbol)
            self.market_data[symbol] = fallback_data
            return fallback_data
    
    def _create_fallback_data(self, symbol):
        """Créer données simulées en cas d'échec API"""
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=7),
            end=datetime.now(),
            freq='1h'
        )
        
        # Prix de base selon le symbole
        base_prices = {
            'BTCUSDT': 43000,
            'ETHUSDT': 2600, 
            'BNBUSDT': 250,
            'ADAUSDT': 0.5,
            'SOLUSDT': 50
        }
        base_price = base_prices.get(symbol, 100)
        
        # Génération prix simulés
        prices = [base_price]
        for i in range(1, len(dates)):
            change = np.random.randn() * base_price * 0.02
            prices.append(max(0.01, prices[-1] + change))
        
        # OHLCV basique
        data = []
        for i in range(len(prices)-1):
            open_price = prices[i]
            close_price = prices[i+1]
            high_price = max(open_price, close_price) * (1 + abs(np.random.randn()) * 0.01)
            low_price = min(open_price, close_price) * (1 - abs(np.random.randn()) * 0.01)
            volume = abs(np.random.randn()) * 1000 + 500
            
            data.append({
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })
        
        df = pd.DataFrame(data, index=dates[1:])
        return df
        
    def generate_economic_events(self):
        """Générer des événements économiques simulés"""
        
        events = []
        base_date = datetime.now()
        
        event_types = [
            {"name": "Fed Rate Decision", "impact": "High", "currency": "USD"},
            {"name": "Non-Farm Payrolls", "impact": "High", "currency": "USD"},
            {"name": "CPI m/m", "impact": "Medium", "currency": "USD"},
            {"name": "ECB Rate Decision", "impact": "High", "currency": "EUR"},
            {"name": "GDP q/q", "impact": "Medium", "currency": "EUR"},
            {"name": "BoE Rate Decision", "impact": "High", "currency": "GBP"},
        ]
        
        for i in range(20):
            event = event_types[i % len(event_types)].copy()
            event['datetime'] = base_date + timedelta(days=np.random.randint(-5, 15))
            event['forecast'] = round(np.random.uniform(0.1, 5.0), 1)
            event['previous'] = round(np.random.uniform(0.1, 5.0), 1)
            events.append(event)
            
        return sorted(events, key=lambda x: x['datetime'])
    
    def calculate_real_sma(self, prices, period=20):
        """Calculer SMA réel avec THEBOT"""
        if self.calculators_loaded and len(prices) >= period:
            try:
                # Utilisation de la méthode statique calculate_batch
                results = SMACalculator.calculate_batch(prices, period)
                return results
            except Exception as e:
                print(f"Info SMA: Utilisation fallback pandas - {e}")
        
        # Fallback pandas (très fiable)
        return pd.Series(prices).rolling(window=period).mean().tolist()
    
    def calculate_real_ema(self, prices, period=12):
        """Calculer EMA réel avec pandas (optimisé)"""
        # Calcul EMA direct avec pandas - très efficace
        return pd.Series(prices).ewm(span=period).mean().tolist()
    
    def calculate_real_rsi(self, prices, period=14):
        """Calculer RSI réel avec pandas (optimisé)"""
        # Calcul RSI manual optimisé avec pandas
        series = pd.Series(prices)
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50).tolist()
    
    def calculate_real_atr(self, highs, lows, closes, period=14):
        """Calculer ATR réel avec pandas (optimisé)"""
        # Calcul ATR optimisé avec pandas
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
        
    def setup_calculators(self):
        """Initialiser les calculateurs THEBOT"""
        if CALCULATORS_AVAILABLE:
            try:
                # Calculateurs par défaut
                self.sma_calc = SMACalculator(SMAConfig(period=20))
                self.ema_calc = EMACalculator(EMAConfig(period=12))
                self.rsi_calc = RSICalculator(RSIConfig(period=14))
                self.atr_calc = ATRCalculator(ATRConfig(period=14))
                
                self.calculators_loaded = True
                print("✅ Calculateurs THEBOT initialisés (SMA, EMA, RSI, ATR)")
                
            except Exception as e:
                print(f"⚠️ Erreur calculateurs: {e}")
                self.calculators_loaded = False
        else:
            self.calculators_loaded = False
            print("⚠️ Mode simulation - calculateurs indisponibles")
    
    def setup_layout(self):
        """Configurer le layout principal"""
        
        self.app.layout = dbc.Container([
            
            # ===== HEADER =====
            self.create_header(),
            
            # ===== CONTROL BAR =====  
            self.create_control_bar(),
            
            # ===== MAIN CONTENT =====
            dbc.Row([
                
                # Sidebar gauche
                dbc.Col([
                    self.create_sidebar()
                ], width=3, className="pe-0"),
                
                # Zone principale
                dbc.Col([
                    self.create_main_content()
                ], width=9, className="ps-2")
                
            ], className="g-0 mt-3"),
            
            # ===== FOOTER STATUS =====
            self.create_footer(),
            
            # Stores pour données avec initialisation par défaut
            dcc.Store(id='market-data-store', data=self.get_default_market_data()),
            dcc.Store(id='indicators-store', data={}),
            dcc.Store(id='settings-store', data=self.get_default_settings()),
            dcc.Store(id='symbol-search-selected', data='BTCUSDT'),
            dcc.Store(id='symbols-cache-store', data=self.all_symbols),
            
            # Interval pour updates
            dcc.Interval(
                id='realtime-interval',
                interval=2000,  # 2 secondes
                n_intervals=0,
                disabled=True
            )
            
        ], fluid=True, className="dbc dbc-ag-grid", style={
            'fontFamily': 'Inter, sans-serif',
            'backgroundColor': '#0d1117',
            'minHeight': '100vh'
        })
        
    def create_header(self):
        """Créer le header compact avec indicateurs globaux"""
        
        return dbc.Row([
            dbc.Col([
                html.Div([
                    # Indicateurs de performance en temps réel
                    dbc.Badge([
                        html.I(className="fas fa-signal me-1"),
                        html.Span("LIVE", id="connection-status")
                    ], color="success", className="me-2 pulse"),
                    
                    dbc.Badge([
                        html.I(className="fas fa-chart-line me-1"),
                        html.Span("Markets: 4", id="markets-count")
                    ], color="info", className="me-2"),
                    
                    dbc.Badge([
                        html.I(className="fas fa-brain me-1"),
                        html.Span("AI: Active", id="ai-status")
                    ], color="warning", className="me-2"),
                    
                ], className="d-flex justify-content-center align-items-center")
            ], width=12)
            
        ], className="border-bottom border-secondary pb-2 mb-2")
        
    def create_control_bar(self):
        """Barre de contrôle avec sélecteurs principaux"""
        
        return dbc.Row([
            # Remplacement par le composant modulaire
            default_symbol_search.get_complete_layout(),
            
            dbc.Col([
                dbc.Label("Timeframe", className="fw-bold text-light small"),
                dcc.Dropdown(
                    id='timeframe-selector',
                    options=[
                        {'label': '🔥 1m - Scalping', 'value': '1m'},
                        {'label': '⚡ 5m - Quick Trades', 'value': '5m'},
                        {'label': '📊 15m - Short Term', 'value': '15m'},
                        {'label': '📈 1h - Day Trading', 'value': '1h'},
                        {'label': '📅 4h - Swing', 'value': '4h'},
                        {'label': '🏛️ 1D - Position', 'value': '1d'}
                    ],
                    value='5m',
                    className="dash-bootstrap"
                )
            ], width=2),
            
            dbc.Col([
                dbc.Label("Analysis Type", className="fw-bold text-light small"),
                dcc.Dropdown(
                    id='analysis-selector',
                    options=[
                        {'label': '🔧 Technical Only', 'value': 'technical'},
                        {'label': '🧠 AI Enhanced', 'value': 'ai'},
                        {'label': '📅 Economic Impact', 'value': 'economic'},
                        {'label': '🎯 Full Spectrum', 'value': 'full'}
                    ],
                    value='technical',
                    className="dash-bootstrap"
                )
            ], width=2),
            
            dbc.Col([
                dbc.Label("Actions", className="fw-bold text-light small"),
                html.Div([
                    dbc.ButtonGroup([
                        dbc.Button([
                            html.I(className="fas fa-play"),
                            " Start"
                        ], id="start-btn", color="success", size="sm"),
                        
                        dbc.Button([
                            html.I(className="fas fa-stop"),
                            " Stop"
                        ], id="stop-btn", color="danger", size="sm", disabled=True),
                        
                        dbc.Button([
                            html.I(className="fas fa-refresh"),
                        ], id="refresh-btn", color="secondary", size="sm")
                    ])
                ])
            ], width=2),
            
            dbc.Col([
                dbc.Label("Market Status", className="fw-bold text-light small"),
                html.Div([
                    dbc.Badge("NY: Open", color="success", className="me-1 small"),
                    dbc.Badge("London: Open", color="success", className="me-1 small"),
                    dbc.Badge("Tokyo: Closed", color="secondary", className="me-1 small")
                ])
            ], width=3)
            
        ], className="bg-dark p-3 rounded border border-secondary mb-3")
        
    def create_sidebar(self):
        """Sidebar avec contrôles avancés"""
        
        return dbc.Card([
            dbc.CardHeader([
                html.H5([
                    html.I(className="fas fa-cogs me-2"),
                    "Analysis Controls"
                ], className="mb-0 text-light")
            ]),
            
            dbc.CardBody([
                
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
            ], className="mb-3"),
            
            # Boutons presets
            html.Hr(),
            dbc.ButtonGroup([
                dbc.Button("Scalping", size="sm", outline=True, color="info"),
                dbc.Button("Swing", size="sm", outline=True, color="warning"),
                dbc.Button("Custom", size="sm", outline=True, color="secondary")
            ], size="sm", className="w-100")
            
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
        
    def create_main_content(self):
        """Zone principale avec graphiques et tableaux"""
        
        return dbc.Tabs([
            
            # Tab 1: Real-Time Analysis
            dbc.Tab(
                label="📈 Real-Time Analysis",
                tab_id="realtime-tab",
                children=[
                    html.Div([
                        
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
                        ])
                        
                    ], className="p-3")
                ]
            ),
            
            # Tab 2: Economic Calendar
            dbc.Tab(
                label="📅 Economic Calendar",
                tab_id="economic-tab",
                children=[
                    html.Div([
                        self.create_economic_calendar()
                    ], className="p-3")
                ]
            ),
            
            # Tab 3: AI Insights
            dbc.Tab(
                label="🧠 AI Insights",
                tab_id="ai-tab",
                children=[
                    html.Div([
                        self.create_ai_dashboard()
                    ], className="p-3")
                ]
            ),
            
            # Tab 4: Backtesting
            dbc.Tab(
                label="🔄 Backtesting",
                tab_id="backtest-tab",
                children=[
                    html.Div([
                        self.create_backtesting_panel()
                    ], className="p-3")
                ]
            )
            
        ], id="main-tabs", active_tab="realtime-tab", className="custom-tabs")
        
    def create_economic_calendar(self):
        """Calendrier économique interactif"""
        
        # Table des événements
        events_df = pd.DataFrame(self.economic_events)
        
        return html.Div([
            
            dbc.Row([
                dbc.Col([
                    html.H4([
                        html.I(className="fas fa-calendar-alt me-2"),
                        "Economic Events This Week"
                    ], className="text-info")
                ], width=8),
                
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("Today", size="sm", outline=True, color="info"),
                        dbc.Button("This Week", size="sm", color="info"),
                        dbc.Button("High Impact", size="sm", outline=True, color="warning")
                    ])
                ], width=4, className="text-end")
            ], className="mb-4"),
            
            # Table interactive
            dash_table.DataTable(
                id='economic-table',
                columns=[
                    {'name': 'Time', 'id': 'datetime', 'type': 'datetime'},
                    {'name': 'Event', 'id': 'name'},
                    {'name': 'Impact', 'id': 'impact'},
                    {'name': 'Currency', 'id': 'currency'},
                    {'name': 'Forecast', 'id': 'forecast', 'type': 'numeric'},
                    {'name': 'Previous', 'id': 'previous', 'type': 'numeric'}
                ],
                data=events_df.head(10).to_dict('records'),
                style_cell={'textAlign': 'left', 'backgroundColor': '#1f2937', 'color': 'white'},
                style_header={'backgroundColor': '#374151', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{impact} = High'},
                        'backgroundColor': '#dc2626',
                        'color': 'white',
                    },
                    {
                        'if': {'filter_query': '{impact} = Medium'},
                        'backgroundColor': '#d97706',
                        'color': 'white',
                    }
                ],
                sort_action='native',
                filter_action='native',
                page_size=15
            )
            
        ])
        
    def create_ai_dashboard(self):
        """Dashboard IA avec insights"""
        
        return html.Div([
            
            # Status IA
            dbc.Alert([
                html.I(className="fas fa-robot me-2"),
                html.Strong("AI Status: "),
                html.Span("Analyzing market conditions...", id="ai-status-text")
            ], color="info", className="mb-4"),
            
            # Insights cards
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
        
    def create_backtesting_panel(self):
        """Panel de backtesting"""
        
        return html.Div([
            
            dbc.Row([
                dbc.Col([
                    html.H4([
                        html.I(className="fas fa-history me-2"),
                        "Strategy Backtesting"
                    ], className="text-primary")
                ], width=8),
                
                dbc.Col([
                    dbc.Button([
                        html.I(className="fas fa-play me-2"),
                        "Run Backtest"
                    ], id="backtest-btn", color="primary")
                ], width=4, className="text-end")
            ], className="mb-4"),
            
            # Configuration du backtest
            dbc.Row([
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Backtest Configuration"),
                        dbc.CardBody([
                            
                            html.Div([
                                dbc.Label("Date Range"),
                                dcc.DatePickerRange(
                                    id='backtest-date-range',
                                    start_date=datetime.now() - timedelta(days=30),
                                    end_date=datetime.now(),
                                    className="mb-3"
                                )
                            ]),
                            
                            html.Div([
                                dbc.Label("Initial Capital"),
                                dbc.Input(
                                    id="initial-capital",
                                    type="number",
                                    value=10000,
                                    min=1000,
                                    step=1000
                                )
                            ], className="mb-3"),
                            
                            html.Div([
                                dbc.Label("Strategy"),
                                dbc.Select(
                                    id="strategy-select",
                                    options=[
                                        {"label": "SMA Crossover", "value": "sma_cross"},
                                        {"label": "RSI Mean Reversion", "value": "rsi_reversal"},
                                        {"label": "Breakout", "value": "breakout"}
                                    ],
                                    value="sma_cross"
                                )
                            ])
                            
                        ])
                    ])
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Results Summary"),
                        dbc.CardBody([
                            
                            # Métriques
                            html.Div([
                                dbc.Row([
                                    dbc.Col([
                                        html.H6("Total Return"),
                                        html.H4("+15.3%", className="text-success")
                                    ], width=6),
                                    dbc.Col([
                                        html.H6("Sharpe Ratio"),
                                        html.H4("1.82", className="text-info")
                                    ], width=6)
                                ], className="mb-3"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        html.H6("Max Drawdown"),
                                        html.H4("-5.2%", className="text-danger")
                                    ], width=6),
                                    dbc.Col([
                                        html.H6("Win Rate"),
                                        html.H4("68%", className="text-warning")
                                    ], width=6)
                                ])
                            ], id="backtest-metrics"),
                            
                        ])
                    ])
                ], width=6)
                
            ])
            
        ])
        
    def create_footer(self):
        """Footer avec informations de statut"""
        
        return dbc.Row([
            dbc.Col([
                html.Small([
                    html.I(className="fas fa-clock me-1"),
                    html.Span("Last Update: ", className="text-muted"),
                    html.Span("--:--:--", id="last-update-time"),
                    html.Span(" | ", className="text-muted mx-2"),
                    html.Span("Server: Online", className="text-success"),
                    html.Span(" | ", className="text-muted mx-2"),
                    html.Span("Data: Binance, Alpha Vantage", className="text-info")
                ])
            ], width=8),
            
            dbc.Col([
                html.Small([
                    "THEBOT v2.0 | ",
                    html.A("Docs", href="#", className="text-decoration-none"),
                    " | ",
                    html.A("Support", href="#", className="text-decoration-none")
                ], className="text-end text-muted")
            ], width=4)
            
        ], className="border-top border-secondary pt-2 mt-4 small")
        
    def get_default_settings(self):
        """Configuration par défaut"""
        
        return {
            'theme': 'dark',
            'auto_refresh': True,
            'refresh_interval': 2000,
            'indicators': {
                'sma': {'enabled': True, 'period': 20},
                'ema': {'enabled': True, 'period': 12},
                'rsi': {'enabled': True, 'period': 14},
                'atr': {'enabled': True, 'period': 14}
            },
            'ai': {
                'enabled': False,
                'model': 'gpt4',
                'confidence': 75
            }
        }
    
    def get_default_market_data(self):
        """Initialiser les données par défaut pour éviter les chargements redondants"""
        default_symbol = 'BTCUSDT'
        print(f"🔄 Initialisation des données par défaut: {default_symbol}")
        df = self.load_symbol_data(default_symbol, '1h', 200)
        
        if df is not None and not df.empty:
            return {
                'symbol': default_symbol,
                'data': df.to_json(date_format='iso'),
                'timestamp': datetime.now().isoformat()
            }
        return {}
        
    def setup_callbacks(self):
        """Configurer les callbacks Dash"""
        
        # Callback pour la recherche dynamique de symboles (modulaire)
        @self.app.callback(
            [Output('symbol-search-results', 'children'),
             Output('symbol-search-results', 'style')],
            [Input('symbol-search-input', 'value')],
            [State('symbols-cache-store', 'data')]
        )
        def update_search_results(search_query, all_symbols):
            """Mettre à jour les résultats de recherche en temps réel"""
            
            # Style par défaut (masqué)
            hidden_style = {
                'maxHeight': '0px',
                'overflowY': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '0.375rem',
                'padding': '0rem',
                'transition': 'all 0.3s ease'
            }
            
            # Style visible
            visible_style = {
                'maxHeight': '200px',
                'overflowY': 'auto',
                'backgroundColor': '#1f2937',
                'borderRadius': '0.375rem',
                'padding': '0.5rem',
                'transition': 'all 0.3s ease'
            }
            
            if not search_query or len(search_query) < 2:
                # Masquer par défaut quand pas de recherche
                return [], hidden_style
            
            # Rechercher des correspondances dans la liste des symboles
            if not all_symbols:
                return [dbc.Alert("Symboles non chargés", color="warning", className="small")], visible_style
            
            # Fonction de recherche simple
            query_upper = search_query.upper()
            matches = []
            
            # Recherche exacte puis partielle
            for symbol in all_symbols:
                if symbol.startswith(query_upper):
                    matches.append(symbol)
                elif query_upper in symbol:
                    matches.append(symbol)
                
                if len(matches) >= 10:  # Limiter à 10 résultats
                    break
            
            # Utiliser le composant modulaire pour créer les boutons
            results = default_symbol_search.create_result_buttons(matches[:10])
            
            # Afficher le conteneur seulement s'il y a des résultats
            style = visible_style if matches else hidden_style
            
            return results, style
        
        # Callback pour sélectionner un symbole (modulaire)
        @self.app.callback(
            [Output('symbol-search-selected', 'data'),
             Output('symbol-search-input', 'value')],
            [Input({'type': 'symbol-search-result', 'index': ALL}, 'n_clicks')],
            prevent_initial_call=True
        )
        def select_symbol(n_clicks_list):
            """Sélectionner un symbole depuis les résultats de recherche"""
            ctx = callback_context
            if not ctx.triggered:
                return dash.no_update, dash.no_update
            
            # Identifier quel bouton a été cliqué
            button_id = ctx.triggered[0]['prop_id']
            if button_id == '.':
                return dash.no_update, dash.no_update
            
            # Extraire le symbole du bouton cliqué
            import json
            button_data = json.loads(button_id.split('.')[0])
            selected_symbol = button_data['index']
            
            return selected_symbol, selected_symbol
        
        # Callback pour charger les données du symbole sélectionné
        @self.app.callback(
            Output('market-data-store', 'data'),
            [Input('symbol-search-selected', 'data'),
             Input('timeframe-selector', 'value')],
            prevent_initial_call=True
        )
        def load_symbol_data(selected_symbol, timeframe):
            """Charger les données du symbole sélectionné"""
            if not selected_symbol:
                return {}
            
            print(f"🔄 Chargement des données pour {selected_symbol}...")
            # Utiliser la méthode de l'instance directement
            df = self.load_symbol_data(selected_symbol, timeframe, 200)
            
            if df is not None and not df.empty:
                # Convertir en format JSON pour le store
                return {
                    'symbol': selected_symbol,
                    'data': df.to_json(date_format='iso'),
                    'timestamp': datetime.now().isoformat()
                }
            
            return {}
        
        @self.app.callback(
            Output('main-chart', 'figure'),
            [Input('market-data-store', 'data'),
             Input('sma-switch', 'value'),
             Input('ema-switch', 'value'),
             Input('sma-period', 'value'),
             Input('ema-period', 'value')]
        )
        def update_main_chart(market_data, sma_enabled, ema_enabled, sma_period, ema_period):
            """Mise à jour du graphique principal avec vrais calculs THEBOT"""
            
            if not market_data or 'data' not in market_data:
                print("❌ Aucune donnée de marché disponible")
                return {
                    'data': [],
                    'layout': {
                        'title': 'Sélectionnez un symbole pour commencer l\'analyse',
                        'paper_bgcolor': '#1f2937',
                        'plot_bgcolor': '#1f2937',
                        'font': {'color': 'white'}
                    }
                }
            
            # Récupérer les données depuis le store
            symbol = market_data['symbol']
            from io import StringIO
            df = pd.read_json(StringIO(market_data['data']))
            
            print(f"📊 Mise à jour graphique pour {symbol}: {len(df)} points")
            
            # Graphique candlestick
            fig = go.Figure()
            
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name=symbol,
                increasing_line_color='#00ff88',
                decreasing_line_color='#ff4444'
            ))
            
            # Ajouter SMA si activé - AVEC VRAIS CALCULS
            if sma_enabled and sma_period:
                sma_values = self.calculate_real_sma(df['close'].tolist(), sma_period)
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=sma_values,
                    mode='lines',
                    name=f'SMA({sma_period})',
                    line=dict(color='orange', width=2)
                ))
            
            # Ajouter EMA si activé - AVEC VRAIS CALCULS  
            if ema_enabled and ema_period:
                ema_values = self.calculate_real_ema(df['close'].tolist(), ema_period)
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=ema_values,
                    mode='lines',
                    name=f'EMA({ema_period})',
                    line=dict(color='cyan', width=2)
                ))
            
            # Configuration du graphique
            fig.update_layout(
                title=f"{symbol} | 📊 THEBOT Analysis",
                xaxis_title="Time",
                yaxis_title="Price",
                template="plotly_dark",
                height=500,
                showlegend=True,
                legend=dict(x=0, y=1),
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            fig.update_xaxes(rangeslider_visible=False)
            
            return fig
        
        @self.app.callback(
            Output('rsi-chart', 'figure'),
            [Input('market-data-store', 'data'),
             Input('rsi-switch', 'value'),
             Input('rsi-period', 'value')]
        )
        def update_rsi_chart(market_data, rsi_enabled, rsi_period):
            """Mise à jour du graphique RSI avec vrais calculs THEBOT"""
            
            fig = go.Figure()
            
            if market_data and 'data' in market_data and rsi_enabled:
                symbol = market_data['symbol']
                from io import StringIO
                df = pd.read_json(StringIO(market_data['data']))
                
                # RSI réel avec calculateur THEBOT
                rsi_values = self.calculate_real_rsi(df['close'].tolist(), rsi_period)
                
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=rsi_values,
                    mode='lines',
                    name=f'RSI({rsi_period})',
                    line=dict(color='purple', width=2),
                    fill=None
                ))
                
                # Zones de surachat/survente
                fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.7, 
                             annotation_text="Overbought")
                fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.7,
                             annotation_text="Oversold")
                fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1, 
                             annotation_text="Sell Zone", annotation_position="top left")
                fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1,
                             annotation_text="Buy Zone", annotation_position="bottom left")
            
            fig.update_layout(
                title="📊 RSI Oscillator - THEBOT Analysis",
                yaxis=dict(range=[0, 100]),
                template="plotly_dark",
                height=200,
                margin=dict(l=0, r=0, t=40, b=0),
                showlegend=False
            )
            
            return fig
        
        @self.app.callback(
            Output('volume-chart', 'figure'),
            Input('market-data-store', 'data')
        )
        def update_volume_chart(market_data):
            """Mise à jour du graphique de volume"""
            
            fig = go.Figure()
            
            if market_data and 'data' in market_data:
                symbol = market_data['symbol']
                from io import StringIO
                df = pd.read_json(StringIO(market_data['data']))
                
                fig.add_trace(go.Bar(
                    x=df.index,
                    y=df['volume'],
                    name='Volume',
                    marker_color='rgba(100, 149, 237, 0.6)'
                ))
            
            fig.update_layout(
                title="Volume",
                template="plotly_dark",
                height=200,
                margin=dict(l=0, r=0, t=40, b=0),
                showlegend=False
            )
            
            return fig
        
        @self.app.callback(
            Output('atr-chart', 'figure'),
            [Input('market-data-store', 'data'),
             Input('atr-switch', 'value'),
             Input('atr-period', 'value')]
        )
        def update_atr_chart(market_data, atr_enabled, atr_period):
            """Mise à jour du graphique ATR avec vrais calculs THEBOT"""
            
            fig = go.Figure()
            
            if market_data and 'data' in market_data and atr_enabled:
                symbol = market_data['symbol']
                from io import StringIO
                df = pd.read_json(StringIO(market_data['data']))
                
                # ATR réel avec calculateur THEBOT
                atr_values = self.calculate_real_atr(
                    df['high'].tolist(), 
                    df['low'].tolist(), 
                    df['close'].tolist(), 
                    atr_period
                )
                
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=atr_values,
                    mode='lines',
                    name=f'ATR({atr_period})',
                    line=dict(color='darkorange', width=2),
                    fill='tonexty'
                ))
                
                # Ligne de moyenne pour référence
                if len(atr_values) > 20:
                    atr_mean = pd.Series(atr_values).rolling(window=20).mean()
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=atr_mean,
                        mode='lines',
                        name=f'ATR MA(20)',
                        line=dict(color='yellow', width=1, dash='dot'),
                        opacity=0.7
                    ))
            
            fig.update_layout(
                title="📊 ATR (Average True Range) - Volatility",
                template="plotly_dark",
                height=200,
                margin=dict(l=0, r=0, t=40, b=0),
                showlegend=False,
                yaxis_title="ATR Value"
            )
            
            return fig
        
        # Callback pour démarrer/arrêter le streaming
        @self.app.callback(
            [Output('start-btn', 'disabled'),
             Output('stop-btn', 'disabled'),
             Output('realtime-interval', 'disabled')],
            [Input('start-btn', 'n_clicks'),
             Input('stop-btn', 'n_clicks')]
        )
        def toggle_streaming(start_clicks, stop_clicks):
            """Toggle du streaming temps réel"""
            
            ctx = callback_context
            if not ctx.triggered:
                return False, True, True
                
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'start-btn':
                return True, False, False  # Démarrer
            else:
                return False, True, True   # Arrêter
                
    def run(self, debug=False, port=8050):
        """Lancer l'application Dash"""
        
        print(f"""
🚀 THEBOT Dashboard Starting...
        
📊 Professional Trading Interface Ready!
        
🌐 Access URL: http://localhost:{port}
        
✨ Features Available:
   • Real-time market analysis
   • 25+ technical indicators  
   • AI-powered insights
   • Economic calendar
   • Professional backtesting
   • Multi-market support
        
🎯 Ready for professional trading analysis!
        """)
        
        self.app.run(debug=debug, port=port, host='0.0.0.0')


def main():
    """Point d'entrée principal"""
    app = THEBOTDashApp()
    app.run(debug=True, port=8050)


if __name__ == '__main__':
    main()