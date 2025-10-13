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
        
        # Charger VRAIES données Binance via API
        try:
            print("🔄 Chargement symboles Binance...")
            self.crypto_symbols = binance_provider.get_all_symbols()
            print(f"✅ {len(self.crypto_symbols)} symboles Binance chargés")
        except Exception as e:
            print(f"⚠️ Erreur API Binance, utilisation liste de fallback: {e}")
            # Fallback en cas d'erreur API
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
    
    def refresh_crypto_symbols(self):
        """Rafraîchit la liste des symboles depuis Binance API"""
        try:
            print("🔄 Rafraîchissement symboles Binance...")
            self.crypto_symbols = binance_provider.get_all_symbols()
            print(f"✅ {len(self.crypto_symbols)} symboles mis à jour")
            return True
        except Exception as e:
            print(f"❌ Erreur rafraîchissement symboles: {e}")
            return False

    def create_search_component(self):
        """Crée le composant de recherche avec VRAIES données Binance"""
        
        # Utiliser TOUS les symboles pour que PEPE et autres fonctionnent
        try:
            # Charger TOUS les 429 symboles (pas seulement 50)
            top_symbols = self.crypto_symbols
            # S'assurer que BTCUSDT est en premier (pour l'affichage)
            if 'BTCUSDT' in top_symbols:
                top_symbols.remove('BTCUSDT')
            top_symbols.insert(0, 'BTCUSDT')
            print(f"🔄 Dropdown populé avec {len(top_symbols)} symboles")
        except:
            # Fallback symboles populaires si erreur
            top_symbols = [
                'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
                'SOLUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LINKUSDT'
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
                            options=[{'label': s, 'value': s} for s in top_symbols],
                            value='BTCUSDT',
                            placeholder="Rechercher une crypto...",
                            searchable=True,
                            clearable=False,
                            className='custom-dropdown',
                            optionHeight=35
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
                            className='custom-dropdown',
                            optionHeight=35
                        )
                    ], width=3),
                    
                    dbc.Col([
                        html.Div([
                            dbc.Button("📊 Analyse", color="success", size="sm", className="me-2"),
                            dbc.Button("📈 Indicateurs", color="info", size="sm", className="me-2", id="crypto-indicators-btn"),
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
        # Utiliser le nouveau système centralisé
        from .crypto_callbacks import register_all_crypto_callbacks
        register_all_crypto_callbacks(app)
        print("✅ Callbacks crypto configurés via système centralisé")

    def register_callbacks(self, app):
        """ANCIEN SYSTÈME - SUPPRIMÉ
        
        Tous les callbacks sont maintenant dans crypto_callbacks.py
        Cette méthode est conservée pour compatibilité mais ne fait rien.
        """
        # Tous les callbacks ont été migrés vers crypto_callbacks.py
        # Cette méthode ne fait plus rien pour éviter les duplications
        print("⚠️ register_callbacks() obsolète - utilise crypto_callbacks.py")
        pass

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

# Export de la fonction pour l'utilisation externe
__all__ = ['CryptoModule']
