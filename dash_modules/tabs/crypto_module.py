"""
THEBOT Crypto Module - Interface Moderne Complète
Module crypto avec interface exacte selon spécifications + Indicateurs Structurels Phase 1
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
from dash_modules.core.price_formatter import format_crypto_price_adaptive, format_percentage_change, format_volume_adaptive, format_price_label_adaptive

# Import des providers de données
from ..data_providers.binance_api import binance_provider

# Indicateurs structurels Phase 1 - Import conditionnel
STRUCTURAL_INDICATORS_AVAILABLE = False
try:
    # Version simplifiée sans dépendances complexes
    print("📊 Chargement des indicateurs structurels Phase 1...")
    STRUCTURAL_INDICATORS_AVAILABLE = True
    print("✅ Mode indicateurs structurels activé")
except Exception as e:
    print(f"⚠️ Indicateurs structurels indisponibles: {e}")
    STRUCTURAL_INDICATORS_AVAILABLE = False

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
                options=[{'label': symbol, 'value': symbol} for symbol in self.get_symbols_list()],
                value=self.current_symbol,
                placeholder="Rechercher un actif crypto...",
                searchable=True,
                className="mb-3"
            )
        ], className="mb-4")
    
    def create_price_display(self):
        """Crée la fenêtre d'affichage du prix en temps réel"""
        return dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Span(
                            id='crypto-current-symbol',
                            children=self.current_symbol,
                            className="fw-bold me-3",
                            style={'color': '#212529', 'fontSize': '1.1rem'}
                        ),
                        html.Span(
                            id='crypto-current-price',
                            children="Loading...",
                            className="text-primary fw-bold me-2",
                            style={'fontSize': '1.2rem'}
                        ),
                        html.Span(
                            id='crypto-price-change',
                            children="",
                            className="me-3"
                        ),
                        html.Small([
                            html.Span("Vol: ", className="text-muted"),
                            html.Span(
                                id='crypto-volume-24h',
                                children="--",
                                className="fw-bold"
                            )
                        ])
                    ], width=12)
                ], align="center")
            ], className="py-1 px-3")
        ], className="mb-2 border-0 shadow-sm", style={'backgroundColor': '#f8f9fa'})
    
    def create_price_display(self):
        """Crée la fenêtre d'affichage du prix en temps réel"""
        return dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Span(
                            id='crypto-current-symbol',
                            children=self.current_symbol,
                            className="fw-bold me-3",
                            style={'color': '#212529', 'fontSize': '1.1rem'}
                        ),
                        html.Span(
                            id='crypto-current-price',
                            children="Loading...",
                            className="text-primary fw-bold me-2",
                            style={'fontSize': '1.2rem'}
                        ),
                        html.Span(
                            id='crypto-price-change',
                            children="",
                            className="me-3"
                        ),
                        html.Small([
                            html.Span("Vol: ", className="text-muted"),
                            html.Span(
                                id='crypto-volume-24h',
                                children="--",
                                className="fw-bold"
                            )
                        ])
                    ], width=12)
                ], align="center")
            ], className="py-1 px-3")
        ], className="mb-2 border-0 shadow-sm", style={'backgroundColor': '#f8f9fa'})

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
            
            # === INDICATEURS STRUCTURELS (PHASE 1) ===
            html.Hr(className="my-3"),
            html.H6("📊 Analyse Structurelle", className="text-primary mb-3"),
            
            # Support/Resistance
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Switch(
                            id="crypto-sr-switch",
                            label="Support/Resistance",
                            value=False
                        )
                    ], width=8),
                    dbc.Col([
                        dbc.Input(
                            id="crypto-sr-strength",
                            type="number",
                            value=2,
                            min=1, max=5, step=1,
                            size="sm"
                        )
                    ], width=4)
                ], className="mb-2")
            ]),
            
            # Fibonacci
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Switch(
                            id="crypto-fibonacci-switch",
                            label="Fibonacci",
                            value=False
                        )
                    ], width=8),
                    dbc.Col([
                        dbc.Input(
                            id="crypto-fibonacci-swing",
                            type="number",
                            value=2,
                            min=1, max=5, step=1,
                            size="sm"
                        )
                    ], width=4)
                ], className="mb-2")
            ]),
            
            # Pivot Points
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Switch(
                            id="crypto-pivot-switch",
                            label="Pivot Points",
                            value=False
                        )
                    ], width=8),
                    dbc.Col([
                        dcc.Dropdown(
                            id="crypto-pivot-method",
                            options=[
                                {'label': 'Standard', 'value': 'standard'},
                                {'label': 'Fibonacci', 'value': 'fibonacci'},
                                {'label': 'Camarilla', 'value': 'camarilla'}
                            ],
                            value='standard',
                            style={'fontSize': '12px'}
                        )
                    ], width=4)
                ], className="mb-2")
            ]),
            
            html.Div([
                html.Small("✨ Phase 1: Indicateurs Structurels Active", 
                          className="text-success fst-italic")
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
            
            # Affichage du prix en temps réel
            dbc.Row([
                dbc.Col([
                    self.create_price_display()
                ], width=12)
            ]),
            
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
        
        # Callback pour mettre à jour l'affichage du prix en temps réel
        @app.callback(
            [Output('crypto-current-symbol', 'children'),
             Output('crypto-current-price', 'children'),
             Output('crypto-price-change', 'children'),
             Output('crypto-volume-24h', 'children')],
            [Input('crypto-symbol-search', 'value'),
             Input('realtime-data-store', 'data')]
        )
        def update_price_display(selected_symbol, realtime_data):
            """Met à jour l'affichage du prix en temps réel"""
            try:
                # IMPORTANT: Synchroniser le symbole - TOUJOURS utiliser le dernier symbole sélectionné
                if selected_symbol:
                    if selected_symbol != self.current_symbol:
                        self.current_symbol = selected_symbol
                        print(f"🔄 Symbole prix mis à jour: {selected_symbol}")
                    active_symbol = selected_symbol
                else:
                    # Utiliser le symbole actuel seulement si aucun symbole sélectionné
                    active_symbol = self.current_symbol
                
                # Données en temps réel depuis WebSocket
                if realtime_data and realtime_data.get('symbol') == active_symbol:
                    price = realtime_data.get('price', 0)
                    price_change = realtime_data.get('price_change', 0)
                    volume = realtime_data.get('volume', 0)
                    
                    # Formatage du prix adaptatif
                    price_str = format_crypto_price_adaptive(price)
                    
                    # Formatage du changement de prix avec couleur
                    change_str = format_percentage_change(price_change)
                    if price_change > 0:
                        change_style = {'color': '#28a745'}
                    elif price_change < 0:
                        change_style = {'color': '#dc3545'}
                    else:
                        change_style = {'color': '#6c757d'}
                    
                    # Formatage du volume
                    if volume > 1000000:
                        volume_str = f"{volume/1000000:.1f}M"
                    elif volume > 1000:
                        volume_str = f"{volume/1000:.1f}K"
                    else:
                        volume_str = f"{volume:.0f}"
                    
                    return (
                        active_symbol,
                        price_str,
                        html.Span(change_str, style=change_style),
                        volume_str
                    )
                else:
                    # Données par défaut si pas de données WebSocket
                    data = self.load_market_data(active_symbol, '1h', 1)
                    if not data.empty:
                        current_price = data['close'].iloc[-1]
                        price_str = format_crypto_price_adaptive(current_price)
                        return active_symbol, price_str, "Loading...", "--"
                
                return active_symbol, "Loading...", "", "--"
                
            except Exception as e:
                print(f"❌ Erreur mise à jour prix: {e}")
                return (self.current_symbol, "Error", "", "--")
        
        # Callback pour le graphique principal avec indicateurs structurels
        @app.callback(
            Output('crypto-main-chart', 'figure'),
            [Input('crypto-symbol-search', 'value'),
             Input('crypto-timeframe-selector', 'value'),
             Input('crypto-sma-switch', 'value'),
             Input('crypto-sma-period', 'value'),
             Input('crypto-ema-switch', 'value'),
             Input('crypto-ema-period', 'value'),
             # Nouveaux inputs pour indicateurs structurels
             Input('crypto-sr-switch', 'value'),
             Input('crypto-sr-strength', 'value'),
             Input('crypto-fibonacci-switch', 'value'),
             Input('crypto-fibonacci-swing', 'value'),
             Input('crypto-pivot-switch', 'value'),
             Input('crypto-pivot-method', 'value')]
        )
        def update_main_chart(symbol, timeframe, sma_enabled, sma_period, ema_enabled, ema_period,
                             sr_enabled, sr_strength, fibonacci_enabled, fibonacci_swing,
                             pivot_enabled, pivot_method):
            """Met à jour le graphique principal avec indicateurs structurels"""
            try:
                # CORRECTION: Être strict sur le symbole, pas de fallback
                if not symbol:
                    return go.Figure().add_annotation(
                        text="Aucun symbole sélectionné",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False
                    )
                
                # IMPORTANT: Mettre à jour self.current_symbol UNIQUEMENT ici
                if symbol != self.current_symbol:
                    self.current_symbol = symbol
                    print(f"🔄 Graphique principal: symbole changé vers {symbol}")
                
                # Charger les données pour le nouveau symbole
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
                
                # === INDICATEURS STRUCTURELS (PHASE 1) ===
                # Calculer et ajouter les indicateurs structurels
                try:
                    structural_data = self.calculate_structural_indicators(
                        data,
                        sr_enabled=sr_enabled,
                        sr_strength=sr_strength or 2,
                        fibonacci_enabled=fibonacci_enabled,
                        fibonacci_swing=fibonacci_swing or 2,
                        pivot_enabled=pivot_enabled,
                        pivot_method=pivot_method or 'standard'
                    )
                    
                    # Ajouter les niveaux structurels au graphique
                    fig = self.add_structural_levels_to_chart(fig, structural_data)
                    
                    # Ajouter annotation pour indiquer les indicateurs actifs
                    active_indicators = []
                    if sr_enabled and structural_data.get('support_resistance'):
                        active_indicators.append("S/R")
                    if fibonacci_enabled and structural_data.get('fibonacci'):
                        active_indicators.append("Fibonacci")
                    if pivot_enabled and structural_data.get('pivot_points'):
                        active_indicators.append("Pivots")
                    
                    if active_indicators:
                        fig.add_annotation(
                            text=f"Phase 1: {', '.join(active_indicators)}",
                            xref="paper", yref="paper",
                            x=0.02, y=0.98,
                            showarrow=False,
                            font=dict(color='#00ff88', size=10),
                            bgcolor='rgba(0,0,0,0.5)',
                            bordercolor='#00ff88',
                            borderwidth=1
                        )
                        
                except Exception as e:
                    print(f"⚠️ Erreur indicateurs structurels: {e}")
                
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
             Input('crypto-rsi-switch', 'value'),
             Input('crypto-rsi-period', 'value'),
             Input('crypto-atr-switch', 'value'),
             Input('crypto-atr-period', 'value')]
        )
        def update_secondary_charts(symbol, timeframe, rsi_enabled, rsi_period, atr_enabled, atr_period):
            """Met à jour les graphiques secondaires"""
            try:
                # CORRECTION: Utiliser directement le symbole du callback, pas de fallback
                if not symbol:
                    return go.Figure(), go.Figure(), go.Figure()
                
                # Mettre à jour le symbole courant pour synchronisation
                if symbol != self.current_symbol:
                    self.current_symbol = symbol
                    print(f"🔄 Graphiques secondaires: symbole synchronisé vers {symbol}")
                    
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
                if rsi_enabled and rsi_period and rsi_period > 0:
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
                
                if not rsi_enabled:
                    rsi_fig.add_annotation(
                        text="RSI désactivé",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=14, color="#666666")
                    )
                
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
                if atr_enabled and atr_period and atr_period > 0:
                    atr = self.calculate_atr(data, atr_period)
                    atr_fig.add_trace(go.Scatter(
                        x=data.index,
                        y=atr,
                        mode='lines',
                        name='ATR',
                        line=dict(color='#95e1d3', width=2)
                    ))
                
                if not atr_enabled:
                    atr_fig.add_annotation(
                        text="ATR désactivé",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=14, color="#666666")
                    )
                
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

    # === NOUVEAUX INDICATEURS STRUCTURELS (PHASE 1) ===
    
    # === INDICATEURS STRUCTURELS SIMPLIFIÉS (PHASE 1) ===
    
    def calculate_support_resistance_simple(self, data, strength=2, lookback=50):
        """Version simplifiée du calcul Support/Resistance"""
        try:
            if len(data) < lookback:
                return {'support_levels': [], 'resistance_levels': []}
            
            # Utiliser les dernières données
            recent_data = data.tail(lookback)
            current_price = data['close'].iloc[-1]
            
            # Trouver les niveaux de support et résistance simples
            support_levels = []
            resistance_levels = []
            
            # Recherche de niveaux basée sur les minima/maxima locaux
            window = 10
            for i in range(window, len(recent_data) - window):
                price_window = recent_data['close'].iloc[i-window:i+window+1]
                current_val = recent_data['close'].iloc[i]
                
                # Support (minimum local)
                if current_val == price_window.min() and current_val < current_price:
                    support_levels.append({
                        'y': current_val,
                        'strength': strength,
                        'label': f"S: {format_price_label_adaptive(current_val)}",
                        'color': 'green',
                        'line_width': 2
                    })
                
                # Résistance (maximum local)
                if current_val == price_window.max() and current_val > current_price:
                    resistance_levels.append({
                        'y': current_val,
                        'strength': strength,
                        'label': f"R: {format_price_label_adaptive(current_val)}",
                        'color': 'red',
                        'line_width': 2
                    })
            
            # Limiter le nombre de niveaux et éliminer les doublons
            support_levels = sorted(support_levels, key=lambda x: abs(x['y'] - current_price))[:5]
            resistance_levels = sorted(resistance_levels, key=lambda x: abs(x['y'] - current_price))[:5]
            
            return {
                'support_levels': support_levels,
                'resistance_levels': resistance_levels
            }
            
        except Exception as e:
            print(f"⚠️ Erreur calcul S/R: {e}")
            return {'support_levels': [], 'resistance_levels': []}
    
    def calculate_fibonacci_simple(self, data, min_swing_pct=2):
        """Version simplifiée du calcul Fibonacci"""
        try:
            if len(data) < 50:
                return {'retracement_levels': [], 'extension_levels': []}
            
            # Trouver le swing high et low récents
            recent_data = data.tail(100)
            swing_high = recent_data['high'].max()
            swing_low = recent_data['low'].min()
            
            # Vérifier que le swing est assez grand
            swing_size = (swing_high - swing_low) / swing_low * 100
            if swing_size < min_swing_pct:
                return {'retracement_levels': [], 'extension_levels': []}
            
            # Ratios de Fibonacci
            fib_ratios = [0.236, 0.382, 0.5, 0.618, 0.786]
            extension_ratios = [1.272, 1.414, 1.618]
            
            fib_colors = {
                0.236: '#FFE4B5', 0.382: '#FFA500', 0.5: '#FF6347',
                0.618: '#DC143C', 0.786: '#8B0000', 1.272: '#9370DB',
                1.414: '#8A2BE2', 1.618: '#4B0082'
            }
            
            retracement_levels = []
            extension_levels = []
            
            # Calculer les retracements (du high vers le low)
            for ratio in fib_ratios:
                fib_price = swing_high - (swing_high - swing_low) * ratio
                retracement_levels.append({
                    'y': fib_price,
                    'ratio': ratio,
                    'label': f"Fib {ratio:.1%}: {format_price_label_adaptive(fib_price)}",
                    'color': fib_colors.get(ratio, '#888888'),
                    'line_width': 2 if ratio in [0.382, 0.5, 0.618] else 1,
                    'line_dash': 'solid' if ratio in [0.382, 0.5, 0.618] else 'dash'
                })
            
            # Calculer les extensions
            for ratio in extension_ratios:
                ext_price = swing_high + (swing_high - swing_low) * (ratio - 1.0)
                extension_levels.append({
                    'y': ext_price,
                    'ratio': ratio,
                    'label': f"Ext {ratio:.1%}: {format_price_label_adaptive(ext_price)}",
                    'color': fib_colors.get(ratio, '#888888'),
                    'line_width': 2,
                    'line_dash': 'dot'
                })
            
            return {
                'retracement_levels': retracement_levels,
                'extension_levels': extension_levels
            }
            
        except Exception as e:
            print(f"⚠️ Erreur calcul Fibonacci: {e}")
            return {'retracement_levels': [], 'extension_levels': []}
    
    def calculate_pivot_points_simple(self, data, method='standard'):
        """Version simplifiée du calcul Pivot Points"""
        try:
            if len(data) < 2:
                return {'pivot_levels': []}
            
            # Utiliser les données de la veille (ou dernière session complète)
            prev_data = data.iloc[-24:] if len(data) >= 24 else data
            
            high = prev_data['high'].max()
            low = prev_data['low'].min()
            close = prev_data['close'].iloc[-1]
            
            levels = []
            
            if method == 'standard':
                # Pivot Points standard
                pp = (high + low + close) / 3
                r1 = 2 * pp - low
                s1 = 2 * pp - high
                r2 = pp + (high - low)
                s2 = pp - (high - low)
                r3 = high + 2 * (pp - low)
                s3 = low - 2 * (high - pp)
                
                pivot_data = [
                    (pp, 'PP', '#FFFF00', 3),
                    (r1, 'R1', '#FF6B6B', 2), (s1, 'S1', '#4ECDC4', 2),
                    (r2, 'R2', '#FF8E8E', 1), (s2, 'S2', '#7EDDD8', 1),
                    (r3, 'R3', '#FFB3B3', 1), (s3, 'S3', '#AFEEED', 1)
                ]
                
            elif method == 'fibonacci':
                # Pivot Points Fibonacci
                pp = (high + low + close) / 3
                range_hl = high - low
                
                pivot_data = [
                    (pp, 'PP', '#FFFF00', 3),
                    (pp + 0.382 * range_hl, 'R1', '#FF6B6B', 2),
                    (pp - 0.382 * range_hl, 'S1', '#4ECDC4', 2),
                    (pp + 0.618 * range_hl, 'R2', '#FF8E8E', 1),
                    (pp - 0.618 * range_hl, 'S2', '#7EDDD8', 1),
                    (pp + 1.000 * range_hl, 'R3', '#FFB3B3', 1),
                    (pp - 1.000 * range_hl, 'S3', '#AFEEED', 1)
                ]
                
            else:  # camarilla
                # Pivot Points Camarilla
                pivot_data = [
                    (close, 'PP', '#FFFF00', 3),
                    (close + (high - low) * 1.1 / 12, 'R1', '#FF6B6B', 2),
                    (close - (high - low) * 1.1 / 12, 'S1', '#4ECDC4', 2),
                    (close + (high - low) * 1.1 / 6, 'R2', '#FF8E8E', 1),
                    (close - (high - low) * 1.1 / 6, 'S2', '#7EDDD8', 1),
                    (close + (high - low) * 1.1 / 4, 'R3', '#FFB3B3', 1),
                    (close - (high - low) * 1.1 / 4, 'S3', '#AFEEED', 1)
                ]
            
            for price, name, color, width in pivot_data:
                levels.append({
                    'y': price,
                    'label': f"{name}: {format_price_label_adaptive(price)}",
                    'color': color,
                    'line_width': width,
                    'line_dash': 'solid' if name == 'PP' else 'dash',
                    'level_type': 'pivot' if name == 'PP' else ('support' if name.startswith('S') else 'resistance'),
                    'touches': 0
                })
            
            return {'pivot_levels': levels}
            
        except Exception as e:
            print(f"⚠️ Erreur calcul Pivots: {e}")
            return {'pivot_levels': []}

    def calculate_structural_indicators(self, data, 
                                      sr_enabled=False, sr_strength=2,
                                      fibonacci_enabled=False, fibonacci_swing=2,
                                      pivot_enabled=False, pivot_method='standard'):
        """
        Version simplifiée des indicateurs structurels
        """
        results = {
            'support_resistance': None,
            'fibonacci': None,
            'pivot_points': None
        }
        
        if data.empty or len(data) < 10:
            return results
        
        try:
            # Support/Resistance
            if sr_enabled:
                results['support_resistance'] = self.calculate_support_resistance_simple(
                    data, strength=sr_strength or 2
                )
            
            # Fibonacci
            if fibonacci_enabled:
                results['fibonacci'] = self.calculate_fibonacci_simple(
                    data, min_swing_pct=fibonacci_swing or 2
                )
            
            # Pivot Points
            if pivot_enabled:
                results['pivot_points'] = self.calculate_pivot_points_simple(
                    data, method=pivot_method or 'standard'
                )
                
        except Exception as e:
            print(f"❌ Erreur calcul indicateurs structurels: {e}")
        
        return results

    def add_structural_levels_to_chart(self, fig, structural_data):
        """
        Ajoute les niveaux structurels au graphique principal
        
        Args:
            fig: Figure Plotly
            structural_data: Données des indicateurs structurels
        """
        if not structural_data or not any(structural_data.values()):
            return fig
        
        try:
            # Support/Resistance
            if structural_data.get('support_resistance'):
                sr_data = structural_data['support_resistance']
                
                # Supports
                for level in sr_data.get('support_levels', []):
                    fig.add_hline(
                        y=level['y'],
                        line=dict(
                            color=level['color'],
                            width=level['line_width'],
                            dash='solid'
                        ),
                        annotation_text=level['label'],
                        annotation_position="right"
                    )
                
                # Résistances
                for level in sr_data.get('resistance_levels', []):
                    fig.add_hline(
                        y=level['y'],
                        line=dict(
                            color=level['color'],
                            width=level['line_width'],
                            dash='solid'
                        ),
                        annotation_text=level['label'],
                        annotation_position="right"
                    )
            
            # Fibonacci
            if structural_data.get('fibonacci'):
                fib_data = structural_data['fibonacci']
                
                # Retracements
                for level in fib_data.get('retracement_levels', []):
                    fig.add_hline(
                        y=level['y'],
                        line=dict(
                            color=level['color'],
                            width=level['line_width'],
                            dash=level['line_dash']
                        ),
                        annotation_text=level['label'],
                        annotation_position="left"
                    )
                
                # Extensions
                for level in fib_data.get('extension_levels', []):
                    fig.add_hline(
                        y=level['y'],
                        line=dict(
                            color=level['color'],
                            width=level['line_width'],
                            dash=level['line_dash']
                        ),
                        annotation_text=level['label'],
                        annotation_position="left"
                    )
            
            # Pivot Points
            if structural_data.get('pivot_points'):
                pivot_data = structural_data['pivot_points']
                
                for level in pivot_data.get('pivot_levels', []):
                    fig.add_hline(
                        y=level['y'],
                        line=dict(
                            color=level['color'],
                            width=level['line_width'],
                            dash=level['line_dash']
                        ),
                        annotation_text=level['label'],
                        annotation_position="top right"
                    )
            
        except Exception as e:
            print(f"⚠️ Erreur ajout niveaux structurels: {e}")
        
        return fig