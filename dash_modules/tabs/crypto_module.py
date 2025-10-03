"""
THEBOT Crypto Module - Interface Moderne Complète
Module crypto avec interface exacte selon spécifications
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback
from typing import Dict, List, Optional, Any

# Import des providers de données
from ..data_providers.binance_api import binance_provider

class CryptoModule:
    """Module crypto moderne avec interface complète"""
    
    def __init__(self, calculators: Dict = None):
        """Initialisation du module crypto"""
        self.calculators = calculators or {}
        self.current_symbol = "BTCUSDT"
        self.current_timeframe = "1h"
        self.current_data = pd.DataFrame()
        
        # Symboles crypto populaires
        self.popular_symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'MATICUSDT', 'SHIBUSDT',
            'AVAXUSDT', 'LTCUSDT', 'UNIUSDT', 'LINKUSDT', 'ATOMUSDT',
            'ETCUSDT', 'XLMUSDT', 'BCHUSDT', 'FILUSDT', 'THETAUSDT',
            'VETUSDT', 'TRXUSDT', 'EOSUSDT', 'AAVEUSDT', 'MKRUSDT'
        ]
        
        # Configuration des indicateurs techniques
        self.default_indicators = {
            'sma': {'period': 20, 'enabled': True},
            'ema': {'period': 12, 'enabled': True},
            'rsi': {'period': 14, 'enabled': True},
            'atr': {'period': 14, 'enabled': True}
        }
        
        print("✅ CryptoModule nouveau initialisé")

    def get_symbols_list(self) -> List[str]:
        """Récupère la liste des symboles crypto disponibles"""
        try:
            symbols = binance_provider.get_all_symbols()
            return symbols if symbols else self.popular_symbols
        except Exception as e:
            print(f"⚠️ Erreur chargement symboles: {e}")
            return self.popular_symbols

    def get_default_symbol(self) -> str:
        """Retourne le symbole par défaut"""
        return self.current_symbol

    def load_market_data(self, symbol: str, interval: str = '1h', limit: int = 200) -> pd.DataFrame:
        """Charge les données de marché depuis Binance"""
        try:
            print(f"🔄 Chargement données crypto {symbol}...")
            data = binance_provider.get_klines(symbol, interval, limit)
            
            if data is not None and not data.empty:
                print(f"✅ {symbol}: {len(data)} points chargés")
                self.current_data = data
                self.current_symbol = symbol
                self.current_timeframe = interval
                return data
            else:
                print(f"⚠️ Aucune donnée pour {symbol}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Erreur chargement {symbol}: {e}")
            return pd.DataFrame()

    def create_search_component(self):
        """Crée le composant de recherche d'actifs"""
        return html.Div([
            dcc.Dropdown(
                id='crypto-symbol-search',
                options=[{'label': symbol, 'value': symbol} for symbol in self.get_symbols_list()[:50]],
                value=self.current_symbol,
                placeholder="Rechercher un actif crypto...",
                searchable=True,
                className="mb-3"
            )
        ], className="mb-4")

    def create_timeframe_component(self):
        """Crée le composant de sélection de timeframe"""
        return html.Div([
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
                value=self.current_timeframe,
                className="mb-3"
            )
        ], className="mb-4")

    def create_technical_indicators_component(self):
        """Crée le composant des indicateurs techniques (extensible)"""
        return html.Div([
            # SMA
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Switch(
                            id="crypto-sma-switch",
                            label="SMA",
                            value=self.default_indicators['sma']['enabled']
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Input(
                            id="crypto-sma-period",
                            type="number",
                            value=self.default_indicators['sma']['period'],
                            min=1, max=200, step=1,
                            size="sm"
                        )
                    ], width=6)
                ], className="mb-2")
            ]),
            
            # EMA
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Switch(
                            id="crypto-ema-switch",
                            label="EMA",
                            value=self.default_indicators['ema']['enabled']
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Input(
                            id="crypto-ema-period",
                            type="number",
                            value=self.default_indicators['ema']['period'],
                            min=1, max=200, step=1,
                            size="sm"
                        )
                    ], width=6)
                ], className="mb-2")
            ]),
            
            # RSI
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Switch(
                            id="crypto-rsi-switch",
                            label="RSI",
                            value=self.default_indicators['rsi']['enabled']
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Input(
                            id="crypto-rsi-period",
                            type="number",
                            value=self.default_indicators['rsi']['period'],
                            min=1, max=50, step=1,
                            size="sm"
                        )
                    ], width=6)
                ], className="mb-2")
            ]),
            
            # ATR
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Switch(
                            id="crypto-atr-switch",
                            label="ATR",
                            value=self.default_indicators['atr']['enabled']
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Input(
                            id="crypto-atr-period",
                            type="number",
                            value=self.default_indicators['atr']['period'],
                            min=1, max=50, step=1,
                            size="sm"
                        )
                    ], width=6)
                ], className="mb-2")
            ]),
            
            # Espace pour futurs indicateurs
            html.Div([
                html.Small("Plus d'indicateurs bientôt disponibles...", 
                          className="text-muted fst-italic")
            ], className="mt-3")
            
        ], className="mb-4")

    def create_ai_analysis_component(self):
        """Crée le composant d'analyse IA"""
        return html.Div([
            # Switch Enable AI Analysis
            dbc.Switch(
                id="crypto-ai-enabled-switch",
                label="Enable AI Analysis",
                value=True,
                className="mb-3"
            ),
            
            # Dropdown moteur IA
            html.Div([
                html.Label("Moteur IA:", className="form-label small"),
                dcc.Dropdown(
                    id='crypto-ai-engine-dropdown',
                    options=[
                        {'label': 'IA Locale Gratuite', 'value': 'local'},
                        {'label': 'IA Hybride Smart', 'value': 'smart'},
                        {'label': 'IA Premium', 'value': 'premium'}
                    ],
                    value='local',
                    className="mb-3"
                )
            ]),
            
            # Slider confidence threshold
            html.Div([
                html.Label("AI Confidence Threshold:", className="form-label small"),
                dcc.Slider(
                    id='crypto-ai-confidence-slider',
                    min=0, max=100, step=5, value=70,
                    marks={i: f'{i}%' for i in range(0, 101, 25)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], className="mb-3"),
            
            # Bouton Generate AI Insights
            dbc.Button(
                [html.I(className="fas fa-magic me-2"), "Generate AI Insights"],
                id="crypto-generate-ai-btn",
                color="success",
                className="w-100"
            )
            
        ], className="mb-4")

    def create_smart_alerts_component(self):
        """Crée le composant des alertes intelligentes"""
        return html.Div([
            # Switch Enable Alerts
            dbc.Switch(
                id="crypto-alerts-enabled-switch",
                label="Enable Alerts",
                value=False,
                className="mb-3"
            ),
            
            # Price Alerts
            html.Div([
                html.Label("Price Alerts:", className="form-label small"),
                
                # Above
                html.Div([
                    html.Label("Above:", className="form-label small text-success"),
                    dbc.Input(
                        id="crypto-alert-above",
                        type="number",
                        placeholder="Prix d'alerte (au-dessus)",
                        size="sm",
                        className="mb-2"
                    )
                ]),
                
                # Below
                html.Div([
                    html.Label("Below:", className="form-label small text-danger"),
                    dbc.Input(
                        id="crypto-alert-below",
                        type="number",
                        placeholder="Prix d'alerte (en-dessous)",
                        size="sm"
                    )
                ])
            ])
            
        ])

    def get_sidebar(self):
        """Retourne la sidebar complète"""
        return dbc.Card([
            dbc.CardBody([
                
                # Recherche d'actif
                self.create_search_component(),
                
                # Timeframe
                self.create_timeframe_component(),
                
                # Technical Indicators
                self.create_technical_indicators_component(),
                
                # AI Analysis
                self.create_ai_analysis_component(),
                
                # Smart Alerts
                self.create_smart_alerts_component()
                
            ])
        ], className="h-100", style={'backgroundColor': '#1f2937'})

    def create_main_chart(self):
        """Crée le graphique principal avec candlesticks et prix en direct"""
        return dcc.Graph(
            id='crypto-main-chart',
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

    def create_secondary_charts(self):
        """Crée les 3 graphiques secondaires (RSI, Volume, ATR)"""
        return dbc.Row([
            
            # RSI Chart
            dbc.Col([
                dcc.Graph(
                    id='crypto-rsi-chart',
                    style={'height': '200px'},
                    config={'displayModeBar': False}
                )
            ], width=4),
            
            # Volume Chart
            dbc.Col([
                dcc.Graph(
                    id='crypto-volume-chart',
                    style={'height': '200px'},
                    config={'displayModeBar': False}
                )
            ], width=4),
            
            # ATR Chart
            dbc.Col([
                dcc.Graph(
                    id='crypto-atr-chart',
                    style={'height': '200px'},
                    config={'displayModeBar': False}
                )
            ], width=4)
            
        ])

    def create_ai_insights_cards(self):
        """Crée les 3 cartes AI Insights"""
        return dbc.Row([
            
            # Market Sentiment
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-chart-pie me-2"),
                        "Market Sentiment (AI)"
                    ], className="bg-primary text-white"),
                    dbc.CardBody([
                        html.Div(
                            id="crypto-ai-sentiment-content",
                            children=[
                                dbc.Spinner([
                                    html.P("Analyzing...", className="text-center text-muted")
                                ], color="primary")
                            ]
                        )
                    ])
                ], className="h-100")
            ], width=4),
            
            # Technical Analysis
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-chart-line me-2"),
                        "Technical Analysis (AI)"
                    ], className="bg-info text-white"),
                    dbc.CardBody([
                        html.Div(
                            id="crypto-ai-technical-content",
                            children=[
                                dbc.Spinner([
                                    html.P("Analyzing...", className="text-center text-muted")
                                ], color="info")
                            ]
                        )
                    ])
                ], className="h-100")
            ], width=4),
            
            # Trading Insights
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-lightbulb me-2"),
                        "Trading Insights (AI)"
                    ], className="bg-warning text-white"),
                    dbc.CardBody([
                        html.Div(
                            id="crypto-ai-trading-content",
                            children=[
                                dbc.Spinner([
                                    html.P("Analyzing...", className="text-center text-muted")
                                ], color="warning")
                            ]
                        )
                    ])
                ], className="h-100")
            ], width=4)
            
        ], className="g-3")

    def get_layout(self):
        """Retourne le layout principal"""
        return html.Div([
            
            # Graphique principal
            dbc.Row([
                dbc.Col([
                    self.create_main_chart()
                ], width=12)
            ], className="mb-3"),
            
            # Graphiques secondaires
            self.create_secondary_charts(),
            
            # Onglet AI Insights
            dbc.Tabs([
                dbc.Tab(
                    label="🧠 AI Insights",
                    tab_id="ai-insights-tab",
                    children=[
                        html.Div([
                            self.create_ai_insights_cards()
                        ], className="p-3")
                    ]
                )
            ], id="crypto-secondary-tabs", active_tab="ai-insights-tab", className="custom-tabs mt-3")
            
        ], className="p-3")

    def setup_callbacks(self, app):
        """Configure les callbacks pour l'interactivité"""
        
        @app.callback(
            Output('crypto-main-chart', 'figure'),
            [Input('crypto-symbol-search', 'value'),
             Input('crypto-timeframe-selector', 'value'),
             Input('crypto-sma-switch', 'value'),
             Input('crypto-sma-period', 'value'),
             Input('crypto-ema-switch', 'value'),
             Input('crypto-ema-period', 'value')]
        )
        def update_main_chart(symbol, timeframe, sma_enabled, sma_period, ema_enabled, ema_period):
            """Met à jour le graphique principal"""
            try:
                if not symbol:
                    symbol = self.current_symbol
                    
                # Charger les données
                data = self.load_market_data(symbol, timeframe)
                
                if data.empty:
                    return go.Figure().add_annotation(
                        text="Aucune donnée disponible",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False
                    )
                
                # Créer le graphique candlestick
                fig = go.Figure()
                
                # Candlesticks
                fig.add_trace(go.Candlestick(
                    x=data.index,
                    open=data['open'],
                    high=data['high'],
                    low=data['low'],
                    close=data['close'],
                    name=symbol,
                    increasing_line_color='#00ff88',
                    decreasing_line_color='#ff4444'
                ))
                
                # Ajouter SMA si activé
                if sma_enabled and sma_period:
                    sma = data['close'].rolling(window=sma_period).mean()
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=sma,
                        mode='lines',
                        name=f'SMA {sma_period}',
                        line=dict(color='#ffa500', width=2)
                    ))
                
                # Ajouter EMA si activé
                if ema_enabled and ema_period:
                    ema = data['close'].ewm(span=ema_period).mean()
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=ema,
                        mode='lines',
                        name=f'EMA {ema_period}',
                        line=dict(color='#00bfff', width=2)
                    ))
                
                # Ligne de prix en direct (dernière valeur)
                if not data.empty:
                    current_price = data['close'].iloc[-1]
                    fig.add_hline(
                        y=current_price,
                        line=dict(color='yellow', width=2, dash='dash'),
                        annotation_text=f"Prix actuel: {current_price:.2f}",
                        annotation_position="top right"
                    )
                
                # Style du graphique
                fig.update_layout(
                    title=f"{symbol} - {timeframe}",
                    template='plotly_dark',
                    xaxis_title="Date",
                    yaxis_title="Prix (USDT)",
                    height=500,
                    showlegend=True,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                
                return fig
                
            except Exception as e:
                print(f"❌ Erreur graphique principal: {e}")
                return go.Figure().add_annotation(
                    text=f"Erreur: {str(e)}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
        
        @app.callback(
            [Output('crypto-rsi-chart', 'figure'),
             Output('crypto-volume-chart', 'figure'),
             Output('crypto-atr-chart', 'figure')],
            [Input('crypto-symbol-search', 'value'),
             Input('crypto-timeframe-selector', 'value'),
             Input('crypto-rsi-period', 'value'),
             Input('crypto-atr-period', 'value')]
        )
        def update_secondary_charts(symbol, timeframe, rsi_period, atr_period):
            """Met à jour les graphiques secondaires"""
            try:
                if not symbol:
                    symbol = self.current_symbol
                    
                data = self.current_data if not self.current_data.empty else self.load_market_data(symbol, timeframe)
                
                if data.empty:
                    empty_fig = go.Figure().add_annotation(
                        text="Pas de données",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False
                    )
                    return empty_fig, empty_fig, empty_fig
                
                # RSI Chart
                rsi_fig = go.Figure()
                if rsi_period and rsi_period > 0:
                    rsi = self.calculate_rsi(data['close'], rsi_period)
                    rsi_fig.add_trace(go.Scatter(
                        x=data.index,
                        y=rsi,
                        mode='lines',
                        name='RSI',
                        line=dict(color='#ff6b6b', width=2)
                    ))
                    rsi_fig.add_hline(y=70, line=dict(color='red', dash='dash'))
                    rsi_fig.add_hline(y=30, line=dict(color='green', dash='dash'))
                
                rsi_fig.update_layout(
                    title="RSI",
                    template='plotly_dark',
                    height=200,
                    margin=dict(l=0, r=0, t=30, b=0),
                    yaxis_range=[0, 100]
                )
                
                # Volume Chart
                volume_fig = go.Figure()
                volume_fig.add_trace(go.Bar(
                    x=data.index,
                    y=data['volume'],
                    name='Volume',
                    marker_color='#4ecdc4'
                ))
                volume_fig.update_layout(
                    title="Volume",
                    template='plotly_dark',
                    height=200,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                
                # ATR Chart
                atr_fig = go.Figure()
                if atr_period and atr_period > 0:
                    atr = self.calculate_atr(data, atr_period)
                    atr_fig.add_trace(go.Scatter(
                        x=data.index,
                        y=atr,
                        mode='lines',
                        name='ATR',
                        line=dict(color='#95e1d3', width=2)
                    ))
                
                atr_fig.update_layout(
                    title="ATR",
                    template='plotly_dark',
                    height=200,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                
                return rsi_fig, volume_fig, atr_fig
                
            except Exception as e:
                print(f"❌ Erreur graphiques secondaires: {e}")
                empty_fig = go.Figure().add_annotation(
                    text=f"Erreur: {str(e)}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                return empty_fig, empty_fig, empty_fig

    def calculate_rsi(self, prices, period=14):
        """Calcule le RSI"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except:
            return pd.Series([50] * len(prices), index=prices.index)

    def calculate_atr(self, data, period=14):
        """Calcule l'ATR"""
        try:
            high_low = data['high'] - data['low']
            high_close = np.abs(data['high'] - data['close'].shift())
            low_close = np.abs(data['low'] - data['close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            atr = true_range.rolling(period).mean()
            return atr
        except:
            return pd.Series([1] * len(data), index=data.index)