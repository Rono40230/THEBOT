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

# Import du modal IA
try:
    from ..components.ai_trading_modal import ai_trading_modal, register_ai_modal_callbacks
    AI_MODAL_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Modal IA non disponible: {e}")
    ai_trading_modal = None
    register_ai_modal_callbacks = None
    AI_MODAL_AVAILABLE = False

# Import du modal alertes
try:
    from ..components.price_alerts_modal import price_alerts_modal, register_alerts_modal_callbacks, alerts_store
    ALERTS_MODAL_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Modal Alertes non disponible: {e}")
    price_alerts_modal = None
    register_alerts_modal_callbacks = None
    alerts_store = None
    ALERTS_MODAL_AVAILABLE = False

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
    
    def create_enhanced_price_display(self):
        """Crée la barre de contrôle complète avec prix, recherche, timeframe et boutons"""
        return dbc.Card([
            dbc.CardBody([
                # Première ligne : Recherche d'actif et Timeframe
                dbc.Row([
                    dbc.Col([
                        dcc.Dropdown(
                            id='crypto-symbol-search',
                            options=[{'label': symbol, 'value': symbol} for symbol in self.get_symbols_list()],
                            value=self.current_symbol,
                            placeholder="🔍 Rechercher un actif crypto...",
                            searchable=True,
                            className="mb-2"
                        )
                    ], width=8),
                    dbc.Col([
                        dcc.Dropdown(
                            id='crypto-timeframe-selector',
                            options=[
                                {'label': '🔥 1m', 'value': '1m'},
                                {'label': '⚡ 5m', 'value': '5m'},
                                {'label': '📊 15m', 'value': '15m'},
                                {'label': '📈 1h', 'value': '1h'},
                                {'label': '📅 4h', 'value': '4h'},
                                {'label': '🏛️ 1D', 'value': '1d'},
                                {'label': '📆 1W', 'value': '1w'},
                                {'label': '🗓️ 1M', 'value': '1M'}
                            ],
                            value=self.current_timeframe,
                            className="mb-2"
                        )
                    ], width=4)
                ]),
                
                # Deuxième ligne : Prix et informations
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
                    ], width=7),
                    dbc.Col([
                        # Trio de boutons : IA, Alertes, Indicateurs
                        dbc.ButtonGroup([
                            dbc.Button(
                                [html.I(className="fas fa-brain me-2"), "AI Analysis"],
                                id="generate-ai-insights-btn",
                                color="primary",
                                size="sm"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-bell me-2"), "Price Alerts"],
                                id="manage-alerts-btn",
                                color="success",
                                size="sm"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-chart-line me-2"), "Indicators"],
                                id="manage-indicators-btn",
                                color="info",
                                size="sm"
                            )
                        ], className="float-end")
                    ], width=5, className="text-end")
                ], align="center")
            ], className="py-2 px-3")
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
                    {'label': '🏛️ 1D - Position', 'value': '1d'},
                    {'label': '📆 1W - Weekly', 'value': '1w'},
                    {'label': '🗓️ 1M - Monthly', 'value': '1M'}
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
        """Composant IA simplifié - Retourné vide car contrôles déplacés"""
        return html.Div([
            # Composant vide - Tous les contrôles IA sont maintenant dans le modal et la zone prix
        ])

    def create_smart_alerts_component(self):
        """Composant alertes simplifié - Retouré vide car contrôles déplacés"""
        return html.Div([
            # Composant vide - Tous les contrôles alertes sont maintenant dans le modal et la zone prix
        ])

    def get_sidebar(self):
        """Retourne None car nous utilisons maintenant le layout pleine largeur"""
        # IMPORTANT: Garde les dropdowns cachés pour les callbacks du modal IA
        return html.Div([
            dcc.Dropdown(
                id='crypto-symbol-dropdown', 
                options=[{'label': symbol, 'value': symbol} for symbol in self.popular_symbols],
                value=self.current_symbol,
                style={'display': 'none'}
            ),
            dcc.Dropdown(
                id='crypto-timeframe-dropdown',
                options=[
                    {'label': '1m', 'value': '1m'},
                    {'label': '5m', 'value': '5m'},
                    {'label': '15m', 'value': '15m'},
                    {'label': '1h', 'value': '1h'},
                    {'label': '4h', 'value': '4h'},
                    {'label': '1d', 'value': '1d'},
                    {'label': '1w', 'value': '1w'},
                    {'label': '1M', 'value': '1M'}
                ],
                value=self.current_timeframe,
                style={'display': 'none'}
            )
        ], style={'display': 'none'})

    def create_main_chart(self):
        """Crée le graphique principal avec candlesticks et prix en direct"""
        return dcc.Graph(
            id='crypto-main-chart',
            style={'height': '600px'},  # Augmenté pour accommoder le volume
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
        """Crée les 2 graphiques secondaires (RSI, ATR) - Volume intégré au graphique principal"""
        return dbc.Row([
            
            # RSI Chart
            dbc.Col([
                dcc.Graph(
                    id='crypto-rsi-chart',
                    style={'height': '200px'},
                    config={'displayModeBar': False}
                )
            ], width=6),  # Élargi à 6 colonnes au lieu de 4
            
            # ATR Chart
            dbc.Col([
                dcc.Graph(
                    id='crypto-atr-chart',
                    style={'height': '200px'},
                    config={'displayModeBar': False}
                )
            ], width=6)  # Élargi à 6 colonnes au lieu de 4
            
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
        """Retourne le layout principal en pleine largeur avec modal IA, Alertes et Indicateurs"""
        layout_components = [
            
            # Barre de contrôle complète (prix + recherche + timeframe + boutons)
            dbc.Row([
                dbc.Col([
                    self.create_enhanced_price_display()
                ], width=12)
            ]),
            
            # Graphique principal en pleine largeur
            dbc.Row([
                dbc.Col([
                    self.create_main_chart()
                ], width=12)
            ], className="mb-3"),
            
            # Graphiques secondaires
            self.create_secondary_charts()
            
        ]
        
        # Ajouter les modals IA et Alertes si disponibles
        if AI_MODAL_AVAILABLE and ai_trading_modal:
            layout_components.append(ai_trading_modal.create_modal())
        
        if ALERTS_MODAL_AVAILABLE and price_alerts_modal:
            layout_components.append(price_alerts_modal.create_modal())
            # Ajouter le Store pour les alertes
            layout_components.append(alerts_store)
        
        # Ajouter la modal des indicateurs
        try:
            from ..components.indicators_modal import indicators_modal, indicators_store
            layout_components.append(indicators_modal.create_modal())
            layout_components.append(indicators_store)
        except ImportError:
            print("⚠️ Modal des indicateurs non disponible")
        
        return html.Div(layout_components, className="p-3")
    
    def setup_callbacks(self, app):
        """Configure les callbacks pour l'interactivité avec modals IA et Alertes"""
        
        # Enregistrer les callbacks du modal IA si disponible
        if AI_MODAL_AVAILABLE and register_ai_modal_callbacks:
            register_ai_modal_callbacks(app)
            print("✅ Callbacks Modal IA enregistrés")
        
        # Enregistrer les callbacks du modal Alertes si disponible
        if ALERTS_MODAL_AVAILABLE and register_alerts_modal_callbacks:
            register_alerts_modal_callbacks(app)
            print("✅ Callbacks Modal Alertes enregistrés")
            
        # Enregistrer les callbacks de la modal des indicateurs
        try:
            from ..components.indicators_modal import register_indicators_modal_callbacks
            register_indicators_modal_callbacks(app)
            print("✅ Callbacks Modal Indicateurs enregistrés")
        except ImportError:
            print("⚠️ Callbacks modal indicateurs non disponibles")
            
        # Ajouter les dropdowns nécessaires pour le modal
        if AI_MODAL_AVAILABLE:
            # Callback pour synchroniser les dropdowns avec le modal
            @app.callback(
                [Output('crypto-symbol-dropdown', 'value'),
                 Output('crypto-timeframe-dropdown', 'value')],
                [Input('crypto-symbol-search', 'value'),
                 Input('crypto-timeframe-selector', 'value')]
            )
            def sync_modal_dropdowns(symbol, timeframe):
                """Synchroniser les valeurs pour le modal IA"""
                return symbol or self.current_symbol, timeframe or self.current_timeframe
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
             Input('indicators-sma-switch', 'value'),
             Input('indicators-sma-period', 'value'),
             Input('indicators-ema-switch', 'value'),
             Input('indicators-ema-period', 'value'),
             Input('indicators-sr-switch', 'value'),
             Input('indicators-sr-strength', 'value'),
             Input('indicators-sr-lookback', 'value'),
             Input('indicators-sr-support-color', 'value'),
             Input('indicators-sr-resistance-color', 'value'),
             Input('indicators-sr-line-style', 'value'),
             Input('indicators-sr-line-width', 'value'),
             Input('indicators-fibonacci-switch', 'value'),
             Input('indicators-fibonacci-swing', 'value'),
             Input('indicators-fibonacci-line-style', 'value'),
             Input('indicators-fibonacci-line-width', 'value'),
             Input('indicators-fibonacci-transparency', 'value'),
             Input('indicators-pivot-switch', 'value'),
             Input('indicators-pivot-method', 'value'),
             Input('indicators-pivot-line-style', 'value'),
             Input('indicators-pivot-line-width', 'value')]
        )
        def update_main_chart(symbol, timeframe, sma_enabled, sma_period, ema_enabled, ema_period, 
                             sr_enabled, sr_strength, sr_lookback, sr_support_color, sr_resistance_color, sr_line_style, sr_line_width,
                             fibonacci_enabled, fibonacci_swing, fibonacci_line_style, fibonacci_line_width, fibonacci_transparency,
                             pivot_enabled, pivot_method, pivot_line_style, pivot_line_width):
            """Met à jour le graphique principal"""
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
                
                # Créer des subplots : graphique principal + volume
                fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.03,
                    subplot_titles=('Prix', 'Volume'),
                    row_heights=[0.75, 0.25]  # 75% pour prix, 25% pour volume
                )
                
                # Candlesticks avec tooltip enrichi
                fig.add_trace(go.Candlestick(
                    x=data.index,
                    open=data['open'],
                    high=data['high'],
                    low=data['low'],
                    close=data['close'],
                    name=symbol,
                    increasing_line_color='#00ff88',
                    decreasing_line_color='#ff4444',
                    hoverinfo='all',
                    showlegend=True
                ), row=1, col=1)
                
                # Volume bipolaire amélioré : une seule série avec couleurs conditionnelles
                volume_values = []
                volume_colors = []
                volume_signals = []
                
                for i, (close, open_price, vol) in enumerate(zip(data['close'], data['open'], data['volume'])):
                    if close >= open_price:  # Chandelier haussier
                        volume_values.append(vol)
                        volume_colors.append('#00ff88')
                        volume_signals.append('Pression acheteuse')
                    else:  # Chandelier baissier
                        volume_values.append(-vol)  # Volume négatif pour visualisation
                        volume_colors.append('#ff4444')
                        volume_signals.append('Pression vendeuse')
                
                # Volume unique avec tooltip enrichi
                fig.add_trace(go.Bar(
                    x=data.index,
                    y=volume_values,
                    name='Volume',
                    marker_color=volume_colors,
                    opacity=0.7,
                    showlegend=False,
                    hovertemplate='<b>Volume</b><br>' +
                                 '<b>Date</b>: %{x}<br>' +
                                 '<b>Volume</b>: %{text:,.0f}<br>' +
                                 '<b>Signal</b>: %{customdata}<br>' +
                                 '<extra></extra>',
                    text=[abs(vol) for vol in volume_values],  # Valeurs absolues pour affichage
                    customdata=volume_signals
                ), row=2, col=1)
                
                # Utiliser les valeurs des indicateurs reçues en paramètres
                # Tous les paramètres sont maintenant connectés aux switchs de la modal
                # sr_enabled, sr_strength, fibonacci_enabled, fibonacci_swing, pivot_enabled, pivot_method
                # sont déjà disponibles via les inputs du callback
                
                # Ajouter SMA si activé (sur le graphique principal) avec tooltip
                if sma_enabled and sma_period:
                    sma = data['close'].rolling(window=sma_period).mean()
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=sma,
                        mode='lines',
                        name=f'SMA {sma_period}',
                        line=dict(color='#ffa500', width=2),
                        hovertemplate='<b>SMA %{fullData.name}</b><br>' +
                                     '<b>Date</b>: %{x}<br>' +
                                     '<b>Valeur</b>: %{y:.2f}<br>' +
                                     '<b>Type</b>: Moyenne mobile simple<br>' +
                                     '<b>Période</b>: ' + str(sma_period) + ' périodes<br>' +
                                     '<extra></extra>'
                    ), row=1, col=1)
                
                # Ajouter EMA si activé (sur le graphique principal) avec tooltip
                if ema_enabled and ema_period:
                    ema = data['close'].ewm(span=ema_period).mean()
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=ema,
                        mode='lines',
                        name=f'EMA {ema_period}',
                        line=dict(color='#00bfff', width=2),
                        hovertemplate='<b>EMA %{fullData.name}</b><br>' +
                                     '<b>Date</b>: %{x}<br>' +
                                     '<b>Valeur</b>: %{y:.2f}<br>' +
                                     '<b>Type</b>: Moyenne mobile exponentielle<br>' +
                                     '<b>Période</b>: ' + str(ema_period) + ' périodes<br>' +
                                     '<b>Réactivité</b>: Plus sensible que SMA<br>' +
                                     '<extra></extra>'
                    ), row=1, col=1)
                
                # === INDICATEURS STRUCTURELS (PHASE 1) ===
                # Calculer et ajouter les indicateurs structurels
                try:
                    # Paramètres visuels pour les indicateurs
                    visual_params = {
                        'support_resistance': {
                            'lookback': sr_lookback or 50,
                            'support_color': sr_support_color or '#27AE60',
                            'resistance_color': sr_resistance_color or '#E74C3C',
                            'line_style': sr_line_style or 'solid',
                            'line_width': sr_line_width or 2
                        },
                        'fibonacci': {
                            'line_style': fibonacci_line_style or 'dashed',
                            'line_width': fibonacci_line_width or 1,
                            'transparency': fibonacci_transparency or 0.8
                        },
                        'pivot': {
                            'line_style': pivot_line_style or 'dotted',
                            'line_width': pivot_line_width or 2
                        }
                    }
                    
                    structural_data = self.calculate_structural_indicators(
                        data,
                        sr_enabled=sr_enabled,
                        sr_strength=sr_strength or 2,
                        fibonacci_enabled=fibonacci_enabled,
                        fibonacci_swing=fibonacci_swing or 20,
                        pivot_enabled=pivot_enabled,
                        pivot_method=pivot_method or 'standard',
                        visual_params=visual_params
                    )
                    
                    # Ajouter les niveaux structurels au graphique
                    fig = self.add_structural_levels_to_chart(fig, structural_data, visual_params)
                    
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
                    height=600,  # Augmenté pour 2 subplots
                    showlegend=True,
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                
                # Configurer les axes sans labels encombrants
                fig.update_yaxes(title_text="", row=1, col=1)  # Supprimer "Prix (USDT)"
                fig.update_yaxes(title_text="", row=2, col=1)  # Supprimer "Volume"
                fig.update_xaxes(title_text="Date", row=2, col=1)
                
                # Supprimer le mini-graphique de zoom
                fig.update_xaxes(rangeslider_visible=False)
                
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
             Output('crypto-atr-chart', 'figure')],
            [Input('crypto-symbol-search', 'value'),
             Input('crypto-timeframe-selector', 'value'),
             Input('indicators-rsi-switch', 'value'),
             Input('indicators-rsi-period', 'value'),
             Input('indicators-atr-switch', 'value'),
             Input('indicators-atr-period', 'value')]
        )
        def update_secondary_charts(symbol, timeframe, rsi_enabled, rsi_period, atr_enabled, atr_period):
            """Met à jour les graphiques secondaires (RSI, ATR) - Volume intégré au principal"""
            try:
                # CORRECTION: Utiliser directement le symbole du callback, pas de fallback
                if not symbol:
                    return go.Figure(), go.Figure()
                
                # Mettre à jour le symbole courant pour synchronisation
                if symbol != self.current_symbol:
                    self.current_symbol = symbol
                
                # Utiliser les valeurs des indicateurs reçues en paramètres
                # rsi_enabled, rsi_period, atr_enabled, atr_period sont déjà disponibles
                
                print(f"🔄 Graphiques secondaires: symbole synchronisé vers {symbol}")
                    
                data = self.current_data if not self.current_data.empty else self.load_market_data(symbol, timeframe)
                
                if data.empty:
                    empty_fig = go.Figure().add_annotation(
                        text="Pas de données",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False
                    )
                    return empty_fig, empty_fig  # Retourner seulement 2 figures
                
                # RSI Chart Professionnel
                rsi_fig = go.Figure()
                if rsi_enabled and rsi_period and rsi_period > 0:
                    rsi = self.calculate_rsi(data['close'], rsi_period)
                    
                    # Zones d'arrière-plan colorées avec tooltips explicatifs
                    # Zone surachat (70-100) - Rouge
                    rsi_fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255, 0, 0, 0.1)", 
                                      line_width=0)
                    # Zone survente (0-30) - Vert
                    rsi_fig.add_hrect(y0=0, y1=30, fillcolor="rgba(0, 255, 0, 0.1)", 
                                      line_width=0)
                    # Zone neutre (30-70) - Gris léger
                    rsi_fig.add_hrect(y0=30, y1=70, fillcolor="rgba(128, 128, 128, 0.05)", 
                                      line_width=0)
                    
                    # Ligne RSI principale avec tooltip enrichi
                    rsi_fig.add_trace(go.Scatter(
                        x=data.index,
                        y=rsi,
                        mode='lines',
                        name='RSI',
                        line=dict(color='#00bfff', width=2),
                        showlegend=False,  # Masquer de la légende
                        hovertemplate='<b>RSI</b>: %{y:.1f}<br>' +
                                     '<b>Date</b>: %{x}<br>' +
                                     '<b>Signal</b>: %{customdata}<br>' +
                                     '<extra></extra>',
                        customdata=[
                            'Surachat - Possible baisse' if val >= 70 
                            else 'Survente - Possible hausse' if val <= 30 
                            else 'Zone neutre' 
                            for val in rsi
                        ]
                    ))
                    
                    # Lignes de niveaux critiques sans annotations
                    rsi_fig.add_hline(y=70, line=dict(color='#ff4444', dash='dash', width=1))
                    rsi_fig.add_hline(y=30, line=dict(color='#00ff88', dash='dash', width=1))
                    rsi_fig.add_hline(y=50, line=dict(color='#888888', dash='dot', width=1))
                    
                    # Tooltips invisibles pour expliquer chaque niveau RSI
                    # Tooltip niveau 70 (surachat)
                    rsi_fig.add_trace(go.Scatter(
                        x=[data.index[0]], y=[70],
                        mode='markers',
                        marker=dict(size=0.1, color='rgba(0,0,0,0)'),
                        hovertemplate='<b>Niveau 70 - Seuil Surachat</b><br>' +
                                     'Signal: Prix potentiellement trop élevé<br>' +
                                     'Action: Zone de prudence pour les achats<br>' +
                                     'Risque: Possible correction baissière<br>' +
                                     '<extra></extra>',
                        showlegend=False,
                        name='Seuil 70'
                    ))
                    
                    # Tooltip niveau 30 (survente)
                    rsi_fig.add_trace(go.Scatter(
                        x=[data.index[0]], y=[30],
                        mode='markers',
                        marker=dict(size=0.1, color='rgba(0,0,0,0)'),
                        hovertemplate='<b>Niveau 30 - Seuil Survente</b><br>' +
                                     'Signal: Prix potentiellement sous-évalué<br>' +
                                     'Action: Zone d\'opportunité d\'achat<br>' +
                                     'Potentiel: Possible rebond haussier<br>' +
                                     '<extra></extra>',
                        showlegend=False,
                        name='Seuil 30'
                    ))
                    
                    # Tooltip niveau 50 (neutre)
                    rsi_fig.add_trace(go.Scatter(
                        x=[data.index[0]], y=[50],
                        mode='markers',
                        marker=dict(size=0.1, color='rgba(0,0,0,0)'),
                        hovertemplate='<b>Niveau 50 - Ligne Neutre</b><br>' +
                                     'Signal: Équilibre acheteurs/vendeurs<br>' +
                                     'Tendance: Ni haussière ni baissière<br>' +
                                     'Interprétation: Zone d\'indécision<br>' +
                                     '<extra></extra>',
                        showlegend=False,
                        name='Ligne neutre'
                    ))
                
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
                    yaxis_range=[0, 100],
                    showlegend=False
                )
                
                # ATR Chart Professionnel avec zones de volatilité
                atr_fig = go.Figure()
                if atr_enabled and atr_period and atr_period > 0:
                    atr = self.calculate_atr(data, atr_period)
                    
                    # Calculer percentiles pour zones de volatilité
                    atr_p25 = atr.quantile(0.25)
                    atr_p75 = atr.quantile(0.75)
                    atr_max = atr.max()
                    
                    # Zones de volatilité avec tooltips explicatifs
                    # Volatilité faible (0 - P25) - Vert
                    atr_fig.add_hrect(y0=0, y1=atr_p25, fillcolor="rgba(0, 255, 0, 0.1)", 
                                      line_width=0)
                    # Volatilité normale (P25 - P75) - Jaune
                    atr_fig.add_hrect(y0=atr_p25, y1=atr_p75, fillcolor="rgba(255, 255, 0, 0.1)", 
                                      line_width=0)
                    # Volatilité élevée (P75 - Max) - Rouge
                    atr_fig.add_hrect(y0=atr_p75, y1=atr_max, fillcolor="rgba(255, 0, 0, 0.1)", 
                                      line_width=0)
                    
                    # Ligne ATR avec gradient de couleur selon intensité
                    colors = ['#00ff88' if val <= atr_p25 else '#ffaa00' if val <= atr_p75 else '#ff4444' 
                             for val in atr]
                    
                    # ATR principal avec tooltip enrichi
                    atr_fig.add_trace(go.Scatter(
                        x=data.index,
                        y=atr,
                        mode='lines',
                        name='ATR',
                        line=dict(color='#00bfff', width=2),
                        showlegend=False,  # Masquer de la légende
                        hovertemplate='<b>ATR</b>: %{y:.4f}<br>' +
                                     '<b>Date</b>: %{x}<br>' +
                                     '<b>Volatilité</b>: %{customdata}<br>' +
                                     '<b>Stop suggéré</b>: ±%{text:.4f}<br>' +
                                     '<extra></extra>',
                        customdata=[
                            'Faible - Marché calme' if val <= atr_p25 
                            else 'Normale - Conditions habituelles' if val <= atr_p75 
                            else 'Élevée - Marché agité' 
                            for val in atr
                        ],
                        text=atr * 2  # Stop loss suggéré à 2x ATR
                    ))
                    
                    # ATR lissé avec tooltip explicatif
                    atr_smooth = atr.rolling(window=5).mean()
                    atr_fig.add_trace(go.Scatter(
                        x=data.index,
                        y=atr_smooth,
                        mode='lines',
                        name='ATR Lissé',
                        line=dict(color='#ffa500', width=1, dash='dot'),
                        opacity=0.7,
                        showlegend=False,  # Masquer de la légende
                        hovertemplate='<b>ATR Lissé</b>: %{y:.4f}<br>' +
                                     '<b>Date</b>: %{x}<br>' +
                                     '<b>Tendance</b>: Volatilité moyenne sur 5 périodes<br>' +
                                     '<extra></extra>'
                    ))
                    
                    # Lignes de niveaux sans annotations
                    atr_fig.add_hline(y=atr_p25, line=dict(color='#00ff88', dash='dash', width=1))
                    atr_fig.add_hline(y=atr_p75, line=dict(color='#ff4444', dash='dash', width=1))
                    
                    # Tooltips invisibles pour expliquer chaque niveau ATR
                    # Tooltip seuil faible (P25)
                    atr_fig.add_trace(go.Scatter(
                        x=[data.index[0]], y=[atr_p25],
                        mode='markers',
                        marker=dict(size=0.1, color='rgba(0,0,0,0)'),
                        hovertemplate=f'<b>Seuil Volatilité Faible: {atr_p25:.3f} USDT</b><br>' +
                                     'Signification: Marché calme et stable<br>' +
                                     'Mouvement: Prix varie peu (±' + f'{atr_p25:.0f}' + ' USDT)<br>' +
                                     'Stratégie: Idéal pour positions long terme<br>' +
                                     'Stop-loss: ±' + f'{atr_p25*2:.0f}' + ' USDT suggéré<br>' +
                                     '<extra></extra>',
                        showlegend=False,
                        name='Seuil faible'
                    ))
                    
                    # Tooltip seuil élevé (P75)
                    atr_fig.add_trace(go.Scatter(
                        x=[data.index[0]], y=[atr_p75],
                        mode='markers',
                        marker=dict(size=0.1, color='rgba(0,0,0,0)'),
                        hovertemplate=f'<b>Seuil Volatilité Élevée: {atr_p75:.3f} USDT</b><br>' +
                                     'Signification: Marché agité et imprévisible<br>' +
                                     'Mouvement: Prix varie beaucoup (±' + f'{atr_p75:.0f}' + ' USDT)<br>' +
                                     'Stratégie: Attention aux positions importantes<br>' +
                                     'Stop-loss: ±' + f'{atr_p75*2:.0f}' + ' USDT suggéré<br>' +
                                     '<extra></extra>',
                        showlegend=False,
                        name='Seuil élevé'
                    ))
                
                if not atr_enabled:
                    atr_fig.add_annotation(
                        text="ATR désactivé",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=14, color="#666666")
                    )
                
                atr_fig.update_layout(
                    title="ATR - Volatilité",
                    template='plotly_dark',
                    height=200,
                    margin=dict(l=0, r=0, t=30, b=0),
                    showlegend=False
                )
                
                return rsi_fig, atr_fig  # Retourner seulement RSI et ATR
                
            except Exception as e:
                print(f"❌ Erreur graphiques secondaires: {e}")
                empty_fig = go.Figure().add_annotation(
                    text=f"Erreur: {str(e)}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                return empty_fig, empty_fig  # Retourner seulement 2 figures

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
    
    def calculate_support_resistance_simple(self, data, strength=2, lookback=50, 
                                           support_color='#27AE60', resistance_color='#E74C3C', 
                                           line_style='solid', line_width=2):
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
                        'color': support_color,
                        'line_width': line_width,
                        'line_dash': line_style
                    })
                
                # Résistance (maximum local)
                if current_val == price_window.max() and current_val > current_price:
                    resistance_levels.append({
                        'y': current_val,
                        'strength': strength,
                        'label': f"R: {format_price_label_adaptive(current_val)}",
                        'color': resistance_color,
                        'line_width': line_width,
                        'line_dash': line_style
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
    
    def calculate_fibonacci_simple(self, data, min_swing_pct=2, line_style='dashed', line_width=1, transparency=0.8):
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
                    'line_width': line_width + (1 if ratio in [0.382, 0.5, 0.618] else 0),  # Niveaux importants légèrement plus épais
                    'line_dash': line_style
                })
            
            # Calculer les extensions
            for ratio in extension_ratios:
                ext_price = swing_high + (swing_high - swing_low) * (ratio - 1.0)
                extension_levels.append({
                    'y': ext_price,
                    'ratio': ratio,
                    'label': f"Ext {ratio:.1%}: {format_price_label_adaptive(ext_price)}",
                    'color': fib_colors.get(ratio, '#888888'),
                    'line_width': line_width,
                    'line_dash': line_style
                })
            
            return {
                'retracement_levels': retracement_levels,
                'extension_levels': extension_levels
            }
            
        except Exception as e:
            print(f"⚠️ Erreur calcul Fibonacci: {e}")
            return {'retracement_levels': [], 'extension_levels': []}
    
    def calculate_pivot_points_simple(self, data, method='standard', line_style='dotted', line_width=2):
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
                    (pp, 'PP', '#FFFF00', line_width + 1),
                    (r1, 'R1', '#FF6B6B', line_width), (s1, 'S1', '#4ECDC4', line_width),
                    (r2, 'R2', '#FF8E8E', max(1, line_width - 1)), (s2, 'S2', '#7EDDD8', max(1, line_width - 1)),
                    (r3, 'R3', '#FFB3B3', max(1, line_width - 1)), (s3, 'S3', '#AFEEED', max(1, line_width - 1))
                ]
                
            elif method == 'fibonacci':
                # Pivot Points Fibonacci
                pp = (high + low + close) / 3
                range_hl = high - low
                
                pivot_data = [
                    (pp, 'PP', '#FFFF00', line_width + 1),
                    (pp + 0.382 * range_hl, 'R1', '#FF6B6B', line_width),
                    (pp - 0.382 * range_hl, 'S1', '#4ECDC4', line_width),
                    (pp + 0.618 * range_hl, 'R2', '#FF8E8E', max(1, line_width - 1)),
                    (pp - 0.618 * range_hl, 'S2', '#7EDDD8', max(1, line_width - 1)),
                    (pp + 1.000 * range_hl, 'R3', '#FFB3B3', max(1, line_width - 1)),
                    (pp - 1.000 * range_hl, 'S3', '#AFEEED', max(1, line_width - 1))
                ]
                
            else:  # camarilla
                # Pivot Points Camarilla
                pivot_data = [
                    (close, 'PP', '#FFFF00', line_width + 1),
                    (close + (high - low) * 1.1 / 12, 'R1', '#FF6B6B', line_width),
                    (close - (high - low) * 1.1 / 12, 'S1', '#4ECDC4', line_width),
                    (close + (high - low) * 1.1 / 6, 'R2', '#FF8E8E', max(1, line_width - 1)),
                    (close - (high - low) * 1.1 / 6, 'S2', '#7EDDD8', max(1, line_width - 1)),
                    (close + (high - low) * 1.1 / 4, 'R3', '#FFB3B3', max(1, line_width - 1)),
                    (close - (high - low) * 1.1 / 4, 'S3', '#AFEEED', max(1, line_width - 1))
                ]
            
            for price, name, color, width in pivot_data:
                levels.append({
                    'y': price,
                    'label': f"{name}: {format_price_label_adaptive(price)}",
                    'color': color,
                    'line_width': width,
                    'line_dash': line_style,
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
                                      pivot_enabled=False, pivot_method='standard',
                                      visual_params=None):
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
        
        # Paramètres visuels par défaut
        if visual_params is None:
            visual_params = {}
        
        try:
            # Support/Resistance avec paramètres visuels
            if sr_enabled:
                sr_visual = visual_params.get('support_resistance', {})
                results['support_resistance'] = self.calculate_support_resistance_simple(
                    data, 
                    strength=sr_strength or 2,
                    lookback=sr_visual.get('lookback', 50),
                    support_color=sr_visual.get('support_color', '#27AE60'),
                    resistance_color=sr_visual.get('resistance_color', '#E74C3C'),
                    line_style=sr_visual.get('line_style', 'solid'),
                    line_width=sr_visual.get('line_width', 2)
                )
            
            # Fibonacci avec paramètres visuels
            if fibonacci_enabled:
                fib_visual = visual_params.get('fibonacci', {})
                results['fibonacci'] = self.calculate_fibonacci_simple(
                    data, 
                    min_swing_pct=fibonacci_swing or 2,
                    line_style=fib_visual.get('line_style', 'dashed'),
                    line_width=fib_visual.get('line_width', 1),
                    transparency=fib_visual.get('transparency', 0.8)
                )
            
            # Pivot Points avec paramètres visuels
            if pivot_enabled:
                pivot_visual = visual_params.get('pivot', {})
                results['pivot_points'] = self.calculate_pivot_points_simple(
                    data, 
                    method=pivot_method or 'standard',
                    line_style=pivot_visual.get('line_style', 'dotted'),
                    line_width=pivot_visual.get('line_width', 2)
                )
                
        except Exception as e:
            print(f"❌ Erreur calcul indicateurs structurels: {e}")
        
        return results

    def add_structural_levels_to_chart(self, fig, structural_data, visual_params=None):
        """
        Ajoute les niveaux structurels au graphique principal
        
        Args:
            fig: Figure Plotly (avec subplots)
            structural_data: Données des indicateurs structurels
            visual_params: Paramètres visuels pour chaque indicateur
        """
        if not structural_data or not any(structural_data.values()):
            return fig
        
        try:
            # Support/Resistance
            if structural_data.get('support_resistance'):
                sr_data = structural_data['support_resistance']
                
                # Supports (ajoutés au subplot prix - row=1)
                for level in sr_data.get('support_levels', []):
                    fig.add_hline(
                        y=level['y'],
                        line=dict(
                            color=level['color'],
                            width=level['line_width'],
                            dash='solid'
                        ),
                        annotation_text=level['label'],
                        annotation_position="right",
                        row=1, col=1  # Spécifier le subplot prix
                    )
                
                # Résistances (ajoutées au subplot prix - row=1)
                for level in sr_data.get('resistance_levels', []):
                    fig.add_hline(
                        y=level['y'],
                        line=dict(
                            color=level['color'],
                            width=level['line_width'],
                            dash='solid'
                        ),
                        annotation_text=level['label'],
                        annotation_position="right",
                        row=1, col=1  # Spécifier le subplot prix
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
                        annotation_position="left",
                        row=1, col=1  # Spécifier le subplot prix
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
                        annotation_position="left",
                        row=1, col=1  # Spécifier le subplot prix
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
                        annotation_position="top right",
                        row=1, col=1  # Spécifier le subplot prix
                    )
            
        except Exception as e:
            print(f"⚠️ Erreur ajout niveaux structurels: {e}")
        
        return fig