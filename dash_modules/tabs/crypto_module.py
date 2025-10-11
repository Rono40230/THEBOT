"""
THEBOT Crypto Module - Interface Moderne Complète PROPRE
Module crypto avec architecture modulaire - Version nettoyée sans code mort
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

# Import des nouveaux modules modulaires
try:
    from ..components.crypto_search_bar import crypto_search_bar, CryptoSearchBar
    from ..components.technical_indicators import technical_indicators, TechnicalIndicators
    from ..components.crypto_chart_components import crypto_chart_components, CryptoChartComponents
    print("🔄 Initialisation des modules modulaires...")
    MODULAR_COMPONENTS_AVAILABLE = True
    print("✅ Modules modulaires disponibles")
except ImportError as e:
    print(f"⚠️ Modules modulaires non disponibles: {e}")
    MODULAR_COMPONENTS_AVAILABLE = False

# Indicateurs structurels Phase 1 - Import conditionnel
try:
    from dash_modules.core.calculators import StructuralIndicatorsCalculator
    STRUCTURAL_INDICATORS_AVAILABLE = True
    print("📊 Chargement des indicateurs structurels Phase 1...")
    print("✅ Mode indicateurs structurels activé")
except ImportError:
    STRUCTURAL_INDICATORS_AVAILABLE = False

# Smart Money Indicators - Import conditionnel
try:
    from dash_modules.core.calculators import FairValueGapCalculator, OrderBlockCalculator
    
    class SmartMoneyIndicators:
        def __init__(self):
            self.fvg_calculator = FairValueGapCalculator()
            self.ob_calculator = OrderBlockCalculator()
    
    SMART_MONEY_AVAILABLE = True
    smart_money_indicators = SmartMoneyIndicators()
    print("🧠 Fair Value Gaps Smart Money disponibles")
    print("📦 Order Blocks Smart Money disponibles")
except ImportError:
    SMART_MONEY_AVAILABLE = False
    smart_money_indicators = None

# Variable globale pour l'instance crypto
global_crypto_module_instance = None

# Variable globale pour l'app Dash (sera définie par le launcher)
dash_app_instance = None

class CryptoModule:
    """Module crypto avec architecture modulaire propre"""
    
    def __init__(self):
        global global_crypto_module_instance
        
        # Symboles crypto populaires
        self.crypto_symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LTCUSDT',
            'LINKUSDT', 'UNIUSDT', 'BCHUSDT', 'XLMUSDT', 'ATOMUSDT'
        ]
        
        # Configuration des indicateurs techniques
        self.indicators_config = {
            'rsi_period': 14,
            'atr_period': 14,
            'macd_params': (12, 26, 9)
        }
        
        # Enregistrer l'instance globalement
        global_crypto_module_instance = self
        
        # Initialiser le symbole par défaut
        self.initialize_default_symbol()
        
        print("✅ CryptoModule nouveau initialisé et enregistré globalement")

    def get_supported_timeframes(self):
        """Retourne les timeframes supportés"""
        return [
            {'label': '1mn', 'value': '1m'},
            {'label': '15mn', 'value': '15m'},
            {'label': '30mn', 'value': '30m'},
            {'label': '1h', 'value': '1h'},
            {'label': '4h', 'value': '4h'},
            {'label': '1d', 'value': '1d'},
            {'label': '1m', 'value': '1M'}
        ]

    def initialize_default_symbol(self):
        """Initialise le symbole par défaut (BTCUSDT)"""
        self.current_symbol = 'BTCUSDT'
        self.current_timeframe = '1h'
        print(f"🪙 Symbole par défaut initialisé: {self.current_symbol}")
        print(f"⏰ Timeframe par défaut initialisé: {self.current_timeframe}")

    # =====================================================
    # 📊 MÉTHODES DE CRÉATION DE GRAPHIQUES
    # =====================================================
    
    def create_candlestick_chart(self, df, symbol, timeframe):
        """Crée le graphique candlestick principal"""
        try:
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name=symbol,
                increasing_line_color='#00d4aa',
                decreasing_line_color='#ff6b6b'
            )])
            
            # Configuration du layout
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                xaxis_title="",  # Suppression du titre "Temps"
                yaxis_title="",  # Suppression du titre "Prix"
                font=dict(color='white'),
                xaxis_rangeslider_visible=False,
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            print(f"❌ Erreur création candlestick: {e}")
            return go.Figure()
    
    def create_volume_chart(self, df):
        """Crée le graphique de volume"""
        try:
            # Couleurs basées sur le mouvement des prix
            colors = ['#00d4aa' if df['close'].iloc[i] >= df['open'].iloc[i] 
                     else '#ff6b6b' for i in range(len(df))]
            
            fig = go.Figure(data=[go.Bar(
                x=df.index,
                y=df['volume'],
                marker_color=colors,
                name='Volume'
            )])
            
            fig.update_layout(
                title="Volume",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=200,
                xaxis_title="",  # Suppression du titre "Temps"
                yaxis_title="Volume",
                font=dict(color='white'),
                showlegend=False,
                xaxis=dict(
                    showticklabels=False,  # Cache les labels des dates
                    tickformat=""
                )
            )
            
            return fig
            
        except Exception as e:
            print(f"❌ Erreur création volume: {e}")
            return go.Figure()
    
    def create_technical_indicators_chart(self, df):
        """Crée le graphique des indicateurs techniques"""
        try:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                subplot_titles=('RSI', 'MACD'),
                vertical_spacing=0.1
            )
            
            # Calcul RSI
            if len(df) >= 14:
                rsi = self.calculate_rsi(df['close'])
                fig.add_trace(
                    go.Scatter(x=df.index, y=rsi, name='RSI', line=dict(color='#ffd93d')),
                    row=1, col=1
                )
                
                # Lignes de surachat/survente
                fig.add_hline(y=70, row=1, col=1, line_dash="dash", line_color="red", opacity=0.5)
                fig.add_hline(y=30, row=1, col=1, line_dash="dash", line_color="green", opacity=0.5)
            
            # Calcul MACD
            if len(df) >= 26:
                macd_line, macd_signal, macd_histogram = self.calculate_macd(df['close'])
                fig.add_trace(
                    go.Scatter(x=df.index, y=macd_line, name='MACD', line=dict(color='#00d4aa')),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df.index, y=macd_signal, name='Signal', line=dict(color='#ff6b6b')),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Bar(x=df.index, y=macd_histogram, name='Histogram', marker_color='gray', opacity=0.6),
                    row=2, col=1
                )
            
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=300,
                font=dict(color='white'),
                showlegend=False,
                xaxis=dict(
                    showticklabels=False,  # Cache les labels des dates pour éviter l'affichage 2025
                    tickformat=""
                ),
                xaxis2=dict(
                    showticklabels=False,  # Cache les labels des dates pour éviter l'affichage 2025
                    tickformat=""
                )
            )
            
            return fig
            
        except Exception as e:
            print(f"❌ Erreur création indicateurs: {e}")
            return go.Figure()
    
    def calculate_rsi(self, prices, period=14):
        """Calcule l'indicateur RSI"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except:
            return pd.Series([50] * len(prices), index=prices.index)
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calcule l'indicateur MACD"""
        try:
            exp1 = prices.ewm(span=fast).mean()
            exp2 = prices.ewm(span=slow).mean()
            macd_line = exp1 - exp2
            macd_signal = macd_line.ewm(span=signal).mean()
            macd_histogram = macd_line - macd_signal
            return macd_line, macd_signal, macd_histogram
        except:
            zeros = pd.Series([0] * len(prices), index=prices.index)
            return zeros, zeros, zeros

    def create_rsi_chart(self, df):
        """Crée le graphique RSI séparé"""
        try:
            rsi = self.calculate_rsi(df['close'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index, 
                y=rsi, 
                name='RSI',
                line=dict(color='#ffd93d', width=2)
            ))
            
            # Lignes de surachat/survente
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.7)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.7)
            
            fig.update_layout(
                title="RSI (14)",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                yaxis=dict(range=[0, 100]),
                font=dict(color='white'),
                showlegend=False,
                xaxis=dict(
                    showticklabels=False,  # Cache les labels des dates
                    tickformat=""
                )
            )
            
            return fig
        except Exception as e:
            print(f"❌ Erreur création RSI: {e}")
            return go.Figure()

    def create_atr_chart(self, df):
        """Crée le graphique ATR séparé"""
        try:
            # Calcul ATR
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = tr.rolling(window=14).mean()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index, 
                y=atr, 
                name='ATR',
                line=dict(color='#ff9500', width=2),
                fill='tozeroy',
                fillcolor='rgba(255, 149, 0, 0.1)'
            ))
            
            fig.update_layout(
                title="ATR (14)",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                font=dict(color='white'),
                showlegend=False,
                xaxis=dict(
                    showticklabels=False,  # Cache les labels des dates
                    tickformat=""
                )
            )
            
            return fig
        except Exception as e:
            print(f"❌ Erreur création ATR: {e}")
            return go.Figure()

    def create_macd_chart(self, df):
        """Crée le graphique MACD séparé"""
        try:
            macd_line, macd_signal, macd_histogram = self.calculate_macd(df['close'])
            
            fig = go.Figure()
            
            # MACD Line
            fig.add_trace(go.Scatter(
                x=df.index, 
                y=macd_line, 
                name='MACD',
                line=dict(color='#00d4aa', width=2)
            ))
            
            # Signal Line
            fig.add_trace(go.Scatter(
                x=df.index, 
                y=macd_signal, 
                name='Signal',
                line=dict(color='#ff6b6b', width=2)
            ))
            
            # Histogram
            colors = ['green' if val >= 0 else 'red' for val in macd_histogram]
            fig.add_trace(go.Bar(
                x=df.index, 
                y=macd_histogram, 
                name='Histogram',
                marker_color=colors,
                opacity=0.6
            ))
            
            fig.update_layout(
                title="MACD (12,26,9)",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                font=dict(color='white'),
                showlegend=False,
                xaxis=dict(
                    showticklabels=False,  # Cache les labels des dates
                    tickformat=""
                )
            )
            
            return fig
        except Exception as e:
            print(f"❌ Erreur création MACD: {e}")
            return go.Figure()

    def get_crypto_symbols(self):
        """Retourne la liste des symboles avec formatage pour dropdown"""
        return [{'label': symbol, 'value': symbol} for symbol in self.crypto_symbols]

    def create_search_component(self):
        """Crée le composant de recherche - VERSION SIMPLIFIÉE QUI FONCTIONNE"""
        
        # Symboles populaires
        popular_symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LINKUSDT',
            'LTCUSDT', 'BCHUSDT', 'XLMUSDT', 'ATOMUSDT', 'UNIUSDT'
        ]
        
        timeframes = [
            {'label': '1mn', 'value': '1m'},
            {'label': '15mn', 'value': '15m'},
            {'label': '30mn', 'value': '30m'},
            {'label': '1h', 'value': '1h'},
            {'label': '4h', 'value': '4h'},
            {'label': '1d', 'value': '1d'},
            {'label': '1M', 'value': '1M'}
        ]
        
        return dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dcc.Dropdown(
                            id='crypto-symbol-search',
                            options=[{'label': s, 'value': s} for s in popular_symbols],
                            value='BTCUSDT',
                            placeholder="Rechercher une crypto...",
                            searchable=True,
                            clearable=False,
                            style={
                                'backgroundColor': '#2c2c2e',
                                'color': '#ffffff'
                            }
                        ),
                        # Informations prix/progression/volume
                        html.Div([
                            html.Span("", id="crypto-price-display", className="fw-bold text-primary me-3"),
                            html.Span("", id="crypto-price-change", className="me-3"),
                            html.Span("Vol: ", className="text-muted"),
                            html.Span("", id="crypto-volume-display", className="fw-bold")
                        ], className="mt-2 small")
                    ], width=4),
                    
                    dbc.Col([
                        dcc.Dropdown(
                            id='crypto-timeframe-selector',
                            options=timeframes,
                            value='1h',
                            clearable=False,
                            style={
                                'backgroundColor': '#2c2c2e',
                                'color': '#ffffff'
                            }
                        )
                    ], width=3),
                    
                    dbc.Col([
                        html.Div([
                            dbc.Button("📊 Analyse", color="success", size="sm", className="me-2"),
                            dbc.Button("🔔 Alertes", color="warning", size="sm")
                        ])
                    ], width=5)
                ])
            ])
        ], style={
            'backgroundColor': '#495057',
            'border': '1px solid #6c757d'
        }, className="mb-3")

    def create_timeframe_component(self):
        """Crée le sélecteur de timeframe"""
        return dbc.Card([
            dbc.CardHeader(html.H5("Timeframe", className="mb-0")),
            dbc.CardBody([
                dcc.Dropdown(
                    id='crypto-timeframe-selector-main',
                    options=self.get_supported_timeframes(),
                    value='1h',
                    placeholder="Sélectionner un timeframe"
                )
            ])
        ], className="mb-3")

    def create_technical_indicators_component(self):
        """Crée le composant des indicateurs techniques"""
        return html.Div()

    def create_ai_analysis_component(self):
        """Crée le composant d'analyse IA"""
        return html.Div()

    def create_smart_alerts_component(self):
        """Crée le composant des alertes intelligentes"""
        return html.Div()

    def add_hidden_dropdowns_for_modal(self):
        """IMPORTANT: Garde les dropdowns cachés pour les callbacks du modal IA"""
        return html.Div([
            dcc.Dropdown(id='crypto-symbol-modal-sync', style={'display': 'none'}),
            dcc.Dropdown(id='crypto-timeframe-modal-sync', style={'display': 'none'})
        ])

    def create_main_chart(self):
        """Crée le graphique principal"""
        if MODULAR_COMPONENTS_AVAILABLE:
            return crypto_chart_components.create_main_chart()
        else:
            # Version de secours
            return dcc.Graph(
                id='crypto-main-chart',
                style={'height': '600px', 'width': '100%'},
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'responsive': True
                }
            )

    def create_secondary_charts(self):
        """Crée les graphiques secondaires"""
        if MODULAR_COMPONENTS_AVAILABLE:
            return crypto_chart_components.create_secondary_charts()
        else:
            # Version de secours
            return dbc.Row([
                # RSI Chart
                dbc.Col([
                    dcc.Graph(
                        id='crypto-rsi-chart',
                        style={'height': '400px', 'margin': '0px', 'margin-top': '30px', 'width': '100%'}
                    )
                ], width=4, style={'padding': '2px'}, xs=12, sm=12, md=6, lg=4),
                
                # ATR Chart
                dbc.Col([
                    dcc.Graph(
                        id='crypto-atr-chart',
                        style={'height': '400px', 'margin': '0px', 'margin-top': '30px', 'width': '100%'}
                    )
                ], width=4, style={'padding': '2px'}, xs=12, sm=12, md=6, lg=4),
                
                # MACD Chart
                dbc.Col([
                    dcc.Graph(
                        id='crypto-macd-chart',
                        style={'height': '400px', 'margin': '0px', 'margin-top': '30px', 'width': '100%'}
                    )
                ], width=4, style={'padding': '2px'}, xs=12, sm=12, md=12, lg=4)
            ], style={'margin': '0px'}, className="g-2")

    def create_ai_insights_cards(self):
        """Crée les cartes AI Insights"""
        if MODULAR_COMPONENTS_AVAILABLE:
            return crypto_chart_components.create_ai_insights_cards()
        else:
            # Version de secours simplifiée
            return dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Market Sentiment (AI)"),
                        dbc.CardBody([html.P("Analyzing...", className="text-center text-muted")])
                    ], className="h-100")
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Technical Analysis (AI)"),
                        dbc.CardBody([html.P("Analyzing...", className="text-center text-muted")])
                    ], className="h-100")
                ], width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Trading Signals (AI)"),
                        dbc.CardBody([html.P("Analyzing...", className="text-center text-muted")])
                    ], className="h-100")
                ], width=4)
            ], className="mb-4")

    def get_layout(self):
        """Retourne le layout complet du module crypto"""
        layout_components = [
            # Barre de contrôle complète (prix + recherche + timeframe + boutons)
            dbc.Container([
                self.create_search_component()
            ], fluid=True, className="mb-3"),
            
            # Graphique principal en pleine largeur
            dbc.Container([
                dbc.Row([
                    dbc.Col([self.create_main_chart()], width=12)
                ])
            ], fluid=True, className="mb-3"),
            
            # Graphiques secondaires
            dbc.Container([
                self.create_secondary_charts()
            ], fluid=True, className="mb-3"),
        ]
        
        # Ajouter les modals IA et Alertes si disponibles
        if AI_MODAL_AVAILABLE and ai_trading_modal:
            # Utiliser la méthode create_modal() pour obtenir le layout
            layout_components.append(ai_trading_modal.create_modal())
            
        if ALERTS_MODAL_AVAILABLE and alerts_store:
            # Ajouter le Store pour les alertes
            layout_components.append(alerts_store)
        
        # Ajouter la modal des indicateurs
        try:
            from ..components.indicators_modal import indicators_modal
            if hasattr(indicators_modal, 'create_modal'):
                layout_components.append(indicators_modal.create_modal())
            elif hasattr(indicators_modal, 'layout'):
                layout_components.append(indicators_modal.layout)
            else:
                layout_components.append(indicators_modal)
        except ImportError:
            pass
        
        # Ajouter les dropdowns cachés
        layout_components.append(self.add_hidden_dropdowns_for_modal())
        
        return html.Div(layout_components)

    def setup_callbacks(self, app):
        """Méthode appelée par le launcher pour enregistrer les callbacks"""
        self.register_callbacks(app)
        print("✅ Callbacks crypto configurés via setup_callbacks")

    def register_callbacks(self, app):
        """Enregistre tous les callbacks du module"""
        global dash_app_instance
        dash_app_instance = app
        
        # Enregistrer les callbacks du modal IA si disponible
        # DÉSACTIVÉ - Cause "Duplicate callback outputs" 
        # if AI_MODAL_AVAILABLE and register_ai_modal_callbacks:
        #     register_ai_modal_callbacks(app)
        
        # Enregistrer les callbacks du modal Alertes si disponible
        # DÉSACTIVÉ - Cause "Duplicate callback outputs"
        # if ALERTS_MODAL_AVAILABLE and register_alerts_modal_callbacks:
        #     register_alerts_modal_callbacks(app)
        
        # Enregistrer les callbacks de la modal des indicateurs
        # DÉSACTIVÉ - Cause "Duplicate callback outputs"
        # try:
        #     from ..components.indicators_modal import register_indicators_modal_callbacks
        #     register_indicators_modal_callbacks(app)
        # except ImportError:
        #     pass

        # Ajouter les dropdowns nécessaires pour le modal
        # if AI_MODAL_AVAILABLE:
        #     # Callback pour synchroniser les dropdowns avec le modal
        #     @app.callback(
        #         [Output('crypto-symbol-modal-sync', 'value'),
        #          Output('crypto-timeframe-modal-sync', 'value')],
        #         [Input('crypto-symbol-search', 'value'),
        #          Input('crypto-timeframe-selector', 'value')]
        #     )
        #     def sync_modal_dropdowns(symbol, timeframe):
        #         return symbol, timeframe

        # =====================================================
        # 🔍 CALLBACK DE RECHERCHE DYNAMIQUE SIMPLIFIÉE
        # =====================================================
        @app.callback(
            Output('crypto-symbol-search', 'options'),
            Input('crypto-symbol-search', 'search_value'),
            prevent_initial_call=True
        )
        def update_search_options_simple(search_value):
            """Met à jour dynamiquement les options de recherche - VERSION SIMPLIFIÉE"""
            try:
                # Symboles populaires par défaut
                popular_symbols = [
                    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
                    'SOLUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LINKUSDT',
                    'LTCUSDT', 'BCHUSDT', 'XLMUSDT', 'ATOMUSDT', 'UNIUSDT'
                ]
                
                if not search_value or len(search_value) < 2:
                    return [{'label': s, 'value': s} for s in popular_symbols]
                
                # Recherche simple avec l'API Binance
                try:
                    all_symbols = binance_provider.get_all_symbols()
                    search_upper = search_value.upper()
                    filtered = [s for s in all_symbols if search_upper in s][:20]
                    if filtered:
                        return [{'label': s, 'value': s} for s in filtered]
                except:
                    pass
                
                # Fallback
                filtered = [s for s in popular_symbols if search_value.upper() in s]
                return [{'label': s, 'value': s} for s in filtered] or [{'label': 'BTCUSDT', 'value': 'BTCUSDT'}]
                
            except Exception as e:
                print(f"⚠️ Erreur recherche: {e}")
                return [{'label': 'BTCUSDT', 'value': 'BTCUSDT'}]

        # =====================================================
        # 💰 CALLBACK DE MISE À JOUR DU PRIX ET VOLUME
        # =====================================================
        @app.callback(
            [Output('crypto-price-display', 'children'),
             Output('crypto-price-change', 'children'),
             Output('crypto-volume-display', 'children')],
            [Input('crypto-symbol-search', 'value')],
            prevent_initial_call=False
        )
        def update_price_display(selected_symbol):
            """Met à jour l'affichage du prix en temps réel"""
            try:
                if not selected_symbol:
                    selected_symbol = 'BTCUSDT'
                
                print(f"🔄 Callback prix déclenché pour: {selected_symbol}")
                
                # Récupérer les données depuis Binance
                ticker_data = binance_provider.get_ticker_24hr(selected_symbol)
                print(f"🔍 DEBUG ticker_data: {ticker_data}")
                
                if ticker_data and 'lastPrice' in ticker_data:
                    # Formatage du prix adaptatif
                    price = float(ticker_data['lastPrice'])
                    formatted_price = format_crypto_price_adaptive(price)
                    
                    # Formatage du changement de prix avec couleur
                    price_change_percent = float(ticker_data.get('priceChangePercent', 0))
                    formatted_change = format_percentage_change(price_change_percent)
                    
                    # Classe CSS pour la couleur
                    change_class = "text-success" if price_change_percent >= 0 else "text-danger"
                    change_html = html.Span(formatted_change, className=change_class)
                    
                    # Formatage du volume
                    volume = float(ticker_data.get('volume', 0))
                    formatted_volume = format_volume_adaptive(volume)
                    
                    print(f"✅ Prix mis à jour: {formatted_price} ({formatted_change})")
                    return (formatted_price, change_html, formatted_volume)
                else:
                    print(f"⚠️ Pas de données pour {selected_symbol}, ticker_data: {ticker_data}")
                    return ("--", html.Span("--", className="text-muted"), "--")
                    
            except Exception as e:
                print(f"❌ Erreur update_price_display: {e}")
                import traceback
                traceback.print_exc()
                return ("Error", html.Span("--", className="text-muted"), "--")

        # =====================================================
        # 📊 CALLBACK DE MISE À JOUR DES GRAPHIQUES
        # =====================================================
        @app.callback(
            [Output('crypto-main-chart', 'figure'),
             Output('crypto-rsi-chart', 'figure'),
             Output('crypto-atr-chart', 'figure'),
             Output('crypto-macd-chart', 'figure')],
            [Input('crypto-symbol-search', 'value'),
             Input('crypto-timeframe-selector', 'value')],
            prevent_initial_call=False
        )
        def update_charts(selected_symbol, selected_timeframe):
            """Met à jour tous les graphiques quand symbole ou timeframe change"""
            try:
                if not selected_symbol:
                    selected_symbol = 'BTCUSDT'
                if not selected_timeframe:
                    selected_timeframe = '1h'
                
                print(f"🔄 Mise à jour graphiques: {selected_symbol} - {selected_timeframe}")
                
                # Récupérer les données OHLCV depuis Binance
                df = binance_provider.get_klines(
                    symbol=selected_symbol,
                    interval=selected_timeframe,
                    limit=200
                )
                
                if df is None or df.empty:
                    # Retourner des graphiques vides en cas d'erreur
                    empty_fig = go.Figure()
                    empty_fig.add_annotation(
                        text=f"Données non disponibles pour {selected_symbol}",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, xanchor='center', yanchor='middle',
                        showarrow=False, font=dict(size=16, color="gray")
                    )
                    empty_fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        height=300
                    )
                    return empty_fig, empty_fig, empty_fig, empty_fig
                
                # 1. Graphique principal (Candlestick)
                main_fig = self.create_candlestick_chart(df, selected_symbol, selected_timeframe)
                
                # 2. Graphique RSI
                rsi_fig = self.create_rsi_chart(df)
                
                # 3. Graphique ATR
                atr_fig = self.create_atr_chart(df)
                
                # 4. Graphique MACD
                macd_fig = self.create_macd_chart(df)
                
                return main_fig, rsi_fig, atr_fig, macd_fig
                
            except Exception as e:
                print(f"❌ Erreur mise à jour graphiques: {e}")
                # Retourner des graphiques d'erreur
                error_fig = go.Figure()
                error_fig.add_annotation(
                    text=f"Erreur: {str(e)}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=14, color="red")
                )
                error_fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=300
                )
                return error_fig, error_fig, error_fig, error_fig

    # =====================================================
    # 🔧 MÉTHODES DE COMPATIBILITÉ LAUNCHER
    # =====================================================
    
    def get_sidebar(self):
        """Retourne la sidebar pour compatibilité avec le launcher"""
        # Retourner un div vide pour éviter les doublons
        # Le contenu est intégré dans le layout principal
        return html.Div()
    
    def get_content(self):
        """Retourne le contenu principal pour compatibilité avec le launcher"""
        return self.get_layout()

# =====================================================
# 🔧 FONCTION PRINCIPALE DE CRÉATION DU LAYOUT
# =====================================================

def create_crypto_layout():
    """
    Fonction principale pour créer le layout crypto complet
    Utilise l'architecture modulaire ou les composants intégrés
    """
    try:
        # Créer l'instance du module crypto
        crypto_module = CryptoModule()
        
        # Générer le layout complet
        layout = crypto_module.get_layout()
        
        print("✅ Layout crypto créé avec succès")
        return layout
        
    except Exception as e:
        print(f"❌ Erreur création layout crypto: {e}")
        import traceback
        traceback.print_exc()
        
        # Layout d'erreur de secours
        return dbc.Container([
            dbc.Alert([
                html.H4("❌ Erreur de chargement", className="alert-heading"),
                html.P(f"Impossible de charger le module crypto: {str(e)}"),
                html.Hr(),
                html.P("Veuillez vérifier la configuration et réessayer.", className="mb-0")
            ], color="danger")
        ])

# =====================================================
# 🚀 PHASE 5 : SYSTÈME DE CALLBACKS MODULAIRES
# =====================================================

def setup_callbacks(app):
    """Fonction setup_callbacks pour le launcher"""
    try:
        crypto_module = CryptoModule()
        crypto_module.setup_callbacks(app)
        return True
    except Exception as e:
        print(f"❌ Erreur setup callbacks crypto: {e}")
        return False

def register_new_crypto_callbacks(dash_app):
    """Enregistre les callbacks Phase 6 - Version directe sans conflits"""
    try:
        # Utiliser directement nos callbacks intégrés
        crypto_module = CryptoModule()
        crypto_module.register_callbacks(dash_app)
        print("🚀 Phase 6: Callbacks directs activés (sans conflits)")
        return True
    except Exception as e:
        print(f"❌ Erreur enregistrement callbacks: {e}")
        return False

def register_essential_callbacks(dash_app):
    """Callbacks essentiels de secours"""
    # Créer une instance pour accéder aux méthodes
    crypto_module = CryptoModule()
    crypto_module.register_callbacks(dash_app)
    print("✅ Callbacks essentiels de secours enregistrés")

# Export de la fonction pour l'utilisation externe
__all__ = ['create_crypto_layout', 'CryptoModule', 'register_new_crypto_callbacks']