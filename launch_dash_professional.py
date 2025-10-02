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
from dash.dependencies import Input, Output, State, ALL
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
from dash_modules.core.api_config import api_config

# Import modules modulaires
from dash_modules.tabs.crypto_module import CryptoModule
from dash_modules.tabs.forex_module import ForexModule
from dash_modules.tabs.stocks_module import StocksModule
from dash_modules.tabs.economic_news_module import EconomicNewsModule
from dash_modules.tabs.crypto_news_module import CryptoNewsModule
from dash_modules.tabs.strategies_module import StrategiesModule

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
        self.current_tab = "crypto"  # Onglet actuel
        
        # Initialisation des modules modulaires
        self._init_modular_modules()
        
        # Initialisation de l'interface
        self.setup_calculators()
        self.setup_layout()
        self.setup_callbacks()
    
    def _init_modular_modules(self):
        """Initialise les modules modulaires"""
        print("🔄 Initialisation des modules modulaires...")
        
        try:
            # Initialisation des modules avec calculateurs partagés
            shared_calculators = {
                'sma': None,
                'ema': None, 
                'rsi': None,
                'atr': None
            }
            
            self.modules = {
                'crypto': CryptoModule(calculators=shared_calculators),
                'forex': ForexModule(calculators=shared_calculators),
                'stocks': StocksModule(calculators=shared_calculators),
                'economic_news': EconomicNewsModule(calculators=shared_calculators),
                'crypto_news': CryptoNewsModule(calculators=shared_calculators),
                'strategies': StrategiesModule(calculators=shared_calculators)
            }
            
            print("✅ Modules modulaires initialisés avec succès")
            
            # Configuration unique des callbacks pour les modules qui en ont
            if 'crypto' in self.modules and hasattr(self.modules['crypto'], 'setup_callbacks'):
                self.modules['crypto'].setup_callbacks(self.app)
                print("✅ Callbacks Crypto configurés")
            
            if 'economic_news' in self.modules and hasattr(self.modules['economic_news'], 'setup_callbacks'):
                self.modules['economic_news'].setup_callbacks(self.app)
                print("✅ Callbacks Economic News configurés")
            
            if 'crypto_news' in self.modules and hasattr(self.modules['crypto_news'], 'setup_callbacks'):
                self.modules['crypto_news'].setup_callbacks(self.app)
                print("✅ Callbacks Crypto News configurés")
            
            if 'strategies' in self.modules and hasattr(self.modules['strategies'], 'setup_callbacks'):
                self.modules['strategies'].setup_callbacks(self.app)
                print("✅ Callbacks Strategies configurés")
            
            # Setup API configuration callbacks
            if hasattr(api_config, 'setup_callbacks'):
                api_config.setup_callbacks(self.app)
                print("✅ Callbacks API Config configurés")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation des modules: {e}")
            # Fallback - continuer sans modules modulaires
            self.modules = {}

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
            
            # ===== CONTROL BAR (conditionnelle) =====  
            html.Div(id="control-bar-content"),
            
            # ===== MAIN CONTENT =====
            dbc.Row([
                
                # Sidebar gauche (conditionnel selon l'onglet)
                dbc.Col([
                    html.Div(id="sidebar-content", children=self.create_sidebar())
                ], width=3, className="pe-0", id="sidebar-col"),
                
                # Zone principale modulaire
                dbc.Col([
                    self.create_modular_content()
                ], width=9, className="ps-2", id="main-content-col")
                
            ], className="g-0 mt-3"),
            
            # ===== FOOTER STATUS =====
            self.create_footer(),
            
            # ===== API CONFIGURATION MODAL =====
            api_config.get_api_config_modal(),
            
            # Stores pour données avec initialisation par défaut
            dcc.Store(id='market-data-store', data=self.get_default_market_data()),
            dcc.Store(id='indicators-store', data={}),
            dcc.Store(id='settings-store', data=self.get_default_settings()),
            dcc.Store(id='main-symbol-selected', data='BTCUSDT'),
            dcc.Store(id='symbols-cache-store', data=self.all_symbols),
            
            # Interval pour updates automatiques
            dcc.Interval(
                id='realtime-interval',
                interval=5000,  # 5 secondes
                n_intervals=0,
                disabled=False  # Toujours actif
            )
            
        ], fluid=True, className="dbc dbc-ag-grid", style={
            'fontFamily': 'Inter, sans-serif',
            'backgroundColor': '#0d1117',
            'minHeight': '100vh'
        })
        
    def create_header(self):
        """Créer le header avec navigation modulaire"""
        
        return dbc.Row([
            # Navigation principale - Onglets modulaires
            dbc.Col([
                dbc.Tabs([
                    dbc.Tab(label="� News Éco", tab_id="economic_news"),
                    dbc.Tab(label="🪙 News Crypto", tab_id="crypto_news"),
                    dbc.Tab(label="₿ Crypto", tab_id="crypto"),
                    dbc.Tab(label="💱 Forex", tab_id="forex"),
                    dbc.Tab(label="📈 Stocks", tab_id="stocks"),
                    dbc.Tab(label="🎯 Strategies", tab_id="strategies")
                ], id="main-tabs", active_tab="economic_news", className="mb-0")
            ], width=7),
            
            # Indicateurs de marchés globaux et API Keys
            dbc.Col([
                html.Div([
                    dbc.Badge("NY: Open", color="success", className="me-2"),
                    dbc.Badge("London: Open", color="success", className="me-2"),
                    dbc.Badge("Tokyo: Closed", color="secondary", className="me-2"),
                    dbc.Button(
                        [html.I(className="fas fa-key me-1"), "🔑 API Keys"],
                        color="dark",
                        size="sm",
                        outline=True,
                        className="ms-3",
                        id="open-api-config-btn"
                    )
                ], className="d-flex justify-content-end align-items-center")
            ], width=5)
            
        ], className="border-bottom border-secondary pb-2 mb-2")
        
    def create_control_bar(self):
        """Barre de contrôle avec sélecteurs principaux"""
        
        return dbc.Row([
            # Remplacement par le composant modulaire
            default_symbol_search.get_complete_layout(),
            
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
            

            
        ], className="bg-dark p-3 rounded border border-secondary mb-3")
        
    def create_sidebar(self):
        """Sidebar avec contrôles avancés"""
        
        return dbc.Card([
            # Suppression du header "Analysis Controls" pour gagner de l'espace
            dbc.CardBody([
                
                # Section Indicateurs Techniques
                html.Div([
                    html.H6([
                        html.I(className="fas fa-chart-line me-2"),
                        "Technical Indicators"
                    ], className="text-info border-bottom border-secondary pb-2 mb-3"),
                    
                    # Technical indicators moved to individual modules
                    html.P("Technical indicators available in each market module", 
                           className="text-muted small"),
                    
                ], className="mb-4"),
                
                
                # AI controls moved to individual modules
                html.Div([
                    html.H6([
                        html.I(className="fas fa-brain me-2"),
                        "AI Analysis"
                    ], className="text-warning border-bottom border-secondary pb-2 mb-3"),
                    
                    html.P("AI analysis available in each market module", 
                           className="text-muted small"),
                    
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
    
    def create_modular_content(self):
        """Créer le contenu modulaire basé sur l'onglet actif"""
        return html.Div(id="modular-content", children=[
            # Le contenu sera mis à jour par les callbacks selon l'onglet actif
            self.create_default_crypto_content()  # Contenu par défaut
        ])
    
    def create_default_crypto_content(self):
        """Contenu par défaut pour l'onglet crypto"""
        if 'crypto' in self.modules:
            # Utiliser le layout du module crypto mais garder compatibilité
            return self.create_main_content()
        else:
            return self.create_main_content()
        
    def create_main_content(self):
        """Zone principale avec graphiques et tableaux"""
        
        return html.Div([
            
            # Charts are now handled by individual modules
            html.Div([
                html.P("Charts and technical indicators are available in each market module (Crypto, Forex, Stocks)", 
                       className="text-muted text-center p-4")
            ], className="mb-3"),
            
            # Tab AI Insights uniquement - Backtesting déplacé vers l'onglet Stratégies
            dbc.Tabs([
                dbc.Tab(
                    label="🧠 AI Insights",
                    tab_id="ai-tab",
                    children=[
                        html.Div([
                            html.P("AI Dashboard moved to individual market modules", 
                                   className="text-muted text-center p-4")
                        ], className="p-3")
                    ]
                )
                
            ], id="secondary-tabs", active_tab="ai-tab", className="custom-tabs mt-3")
            
        ], className="p-3")
        
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
            
            # Insights cards directement - suppression du status AI inutile
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
        
        # Callback pour la barre de contrôle conditionnelle
        @self.app.callback(
            Output('control-bar-content', 'children'),
            [Input('main-tabs', 'active_tab')]
        )
        def update_control_bar(active_tab):
            """Afficher la barre de contrôle seulement pour les onglets de marché"""
            # Onglets qui ont besoin de la barre de contrôle
            market_tabs = ['crypto', 'forex', 'stocks']
            
            if active_tab in market_tabs:
                return self.create_control_bar()
            else:
                # Pas de barre de contrôle pour news et strategies
                return html.Div()
        
        # Callback principal pour la navigation entre onglets modulaires
        @self.app.callback(
            [Output('modular-content', 'children'),
             Output('sidebar-content', 'children'),
             Output('sidebar-col', 'width'),
             Output('main-content-col', 'width')],
            [Input('main-tabs', 'active_tab')]
        )
        def update_tab_content(active_tab):
            """Mettre à jour le contenu selon l'onglet actif - délégation aux modules"""
            
            self.current_tab = active_tab
            
            try:
                if active_tab == 'economic_news':
                    # Economic News module : layout spécialisé
                    if 'economic_news' in self.modules:
                        return (
                            self.modules['economic_news'].get_layout() if hasattr(self.modules['economic_news'], 'get_layout') else html.Div("Economic News en cours de développement"),
                            html.Div(),  # Pas de sidebar pour news
                            0,  # Pas de sidebar
                            12  # Pleine largeur
                        )
                
                elif active_tab == 'crypto_news':
                    # Crypto News module : layout spécialisé
                    if 'crypto_news' in self.modules:
                        return (
                            self.modules['crypto_news'].get_layout() if hasattr(self.modules['crypto_news'], 'get_layout') else html.Div("Crypto News en cours de développement"),
                            html.Div(),  # Pas de sidebar pour news
                            0,  # Pas de sidebar
                            12  # Pleine largeur
                        )
                
                elif active_tab == 'strategies':
                    # Strategies module : layout spécialisé
                    if 'strategies' in self.modules:
                        return (
                            self.modules['strategies'].get_layout() if hasattr(self.modules['strategies'], 'get_layout') else html.Div("Strategies en cours de développement"),
                            html.Div(),  # Pas de sidebar pour strategies
                            0,  # Pas de sidebar
                            12  # Pleine largeur
                        )
                
                elif active_tab in ['crypto', 'forex', 'stocks']:
                    # Modules de marché : utiliser leur layout complet
                    if active_tab in self.modules:
                        return (
                            self.modules[active_tab].get_layout(),
                            self.modules[active_tab].get_sidebar(),
                            3,  # Sidebar
                            9   # Contenu principal
                        )
                    else:
                        # Fallback si module non disponible
                        return (
                            html.Div([
                                dbc.Alert(f"Module {active_tab} non disponible", color="warning")
                            ]),
                            self.create_sidebar(),
                            3,
                            9
                        )
                
                else:
                    # Onglet inconnu - fallback crypto
                    if 'crypto' in self.modules:
                        return (
                            self.modules['crypto'].get_layout(),
                            self.modules['crypto'].get_sidebar(),
                            3,
                            9
                        )
                    else:
                        return (
                            html.Div([
                                dbc.Alert("Aucun module disponible", color="danger")
                            ]),
                            html.Div(),
                            0,
                            12
                        )
                    
            except Exception as e:
                print(f"❌ Erreur dans update_tab_content: {e}")
                # Fallback vers le contenu crypto par défaut
                return (
                    self.create_main_content(),
                    self.create_sidebar(),
                    3,
                    9
                )
        
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
            [Output('main-symbol-selected', 'data'),
             Output('symbol-search-input', 'value')],
            [Input({'type': 'symbol-search-result', 'index': ALL}, 'n_clicks')],
            prevent_initial_call=True
        )
        def select_symbol(n_clicks_list):
            """Sélectionner un symbole depuis les résultats de recherche"""
            ctx = dash.callback_context
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
        
        # Callback pour charger les données du symbole sélectionné (sans timeframe)
        @self.app.callback(
            Output('market-data-store', 'data'),
            [Input('main-symbol-selected', 'data'),
             Input('realtime-interval', 'n_intervals'),
             Input('main-tabs', 'active_tab')],
            prevent_initial_call=True
        )
        def load_symbol_data(selected_symbol, n_intervals, active_tab):
            """Charger les données du symbole sélectionné"""
            # Ne traiter que si on est sur un onglet de marché
            if active_tab not in ['crypto', 'forex', 'stocks'] or not selected_symbol:
                return {}
            
            # Utiliser un timeframe par défaut
            timeframe = '1h'
            if not timeframe:
                timeframe = '1h'
            
            print(f"🔄 Chargement des données pour {selected_symbol}...")
            df = self.load_symbol_data(selected_symbol, timeframe, 200)
            
            if df is not None and not df.empty:
                # Convertir en format JSON pour le store
                return {
                    'symbol': selected_symbol,
                    'data': df.to_json(date_format='iso'),
                    'timestamp': datetime.now().isoformat()
                }
            
            return {}
        
        # ===== API CONFIGURATION CALLBACKS =====
        # Note: API Config modal callbacks are handled in api_config.py module
        
        @self.app.callback(
            Output("api-config-modal", "is_open"),
            [Input("open-api-config-btn", "n_clicks"), 
             Input("close-config-btn", "n_clicks")],
            [State("api-config-modal", "is_open")],
            prevent_initial_call=True
        )
        def toggle_api_config_modal(open_clicks, close_clicks, is_open):
            """Toggle API configuration modal"""
            ctx = dash.callback_context
            if not ctx.triggered:
                return False
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == "open-api-config-btn":
                return True
            elif button_id == "close-config-btn":
                return False
            
            return is_open
        
        @self.app.callback(
            [Output("api-config-modal", "children", allow_duplicate=True),
             Output("api-config-modal", "is_open", allow_duplicate=True)],
            [Input("save-config-btn", "n_clicks")],
            [State("api-key-alpha-vantage", "value"),
             State("api-key-cryptopanic", "value"), 
             State("api-key-coingecko", "value"),
             State("api-key-fmp", "value"),
             State("api-key-twelve-data", "value"),
             State("api-key-huggingface", "value"),
             State("api-config-modal", "is_open")],
            prevent_initial_call=True
        )
        def save_api_config(save_clicks, alpha_key, crypto_key, coin_key, fmp_key, twelve_key, hf_key, is_open):
            """Save API configuration"""
            if save_clicks and is_open:
                try:
                    # Sauvegarder les clés API
                    saved_count = 0
                    
                    # Alpha Vantage
                    if alpha_key and alpha_key.strip():
                        for section in api_config.config["providers"]["data_sources"].values():
                            for provider in section:
                                if provider["name"] == "Alpha Vantage":
                                    provider["config"]["api_key"] = alpha_key.strip()
                                    provider["status"] = "active"
                                    saved_count += 1
                                    break
                    
                    # CryptoPanic
                    if crypto_key and crypto_key.strip():
                        for section in api_config.config["providers"]["data_sources"].values():
                            for provider in section:
                                if provider["name"] == "CryptoPanic":
                                    provider["config"]["api_key"] = crypto_key.strip()
                                    provider["status"] = "active"
                                    saved_count += 1
                                    break
                    
                    # CoinGecko 
                    if coin_key and coin_key.strip():
                        for section in api_config.config["providers"]["data_sources"].values():
                            for provider in section:
                                if provider["name"] == "CoinGecko":
                                    provider["config"]["api_key"] = coin_key.strip()
                                    provider["status"] = "active"
                                    saved_count += 1
                                    break
                    
                    # FMP
                    if fmp_key and fmp_key.strip():
                        for section in api_config.config["providers"]["data_sources"].values():
                            for provider in section:
                                if provider["name"] == "FMP":
                                    provider["config"]["api_key"] = fmp_key.strip()
                                    provider["status"] = "active"
                                    saved_count += 1
                                    break
                    
                    # Twelve Data
                    if twelve_key and twelve_key.strip():
                        for section in api_config.config["providers"]["data_sources"].values():
                            for provider in section:
                                if provider["name"] == "Twelve Data":
                                    provider["config"]["api_key"] = twelve_key.strip()
                                    provider["status"] = "active"
                                    saved_count += 1
                                    break
                    
                    # HuggingFace (AI Provider)
                    if hf_key and hf_key.strip():
                        if api_config.save_huggingface_key(hf_key.strip()):
                            saved_count += 1
                    
                    # Sauvegarder la configuration
                    api_config.save_config()
                    print(f"✅ API Configuration saved - {saved_count} clés mises à jour")
                    
                    # Fermer la modal et rafraîchir
                    return api_config.get_api_config_modal().children, False
                    
                except Exception as e:
                    print(f"❌ Error saving API config: {e}")
                    return api_config.get_api_config_modal().children, is_open
            
            return dash.no_update, dash.no_update

        # API configuration module should handle its own callbacks
        # All technical indicator callbacks moved to respective modules
        # Note: News modal callbacks are handled in their respective modules
        
    def run(self, debug=False, port=8050):
        """Lancer l'application Dash"""
        print("🚀 THEBOT Dashboard Starting - Pure Orchestrator Mode!")
        self.app.run(debug=debug, port=port, host='0.0.0.0')


def main():
    """Point d'entrée principal"""
    app = THEBOTDashApp()
    app.run(debug=True, port=8050)


def create_dash_app(debug=False, port=8050):
    """Factory function for creating THEBOT Dash app (for testing)"""
    return THEBOTDashApp()


if __name__ == '__main__':
    main()