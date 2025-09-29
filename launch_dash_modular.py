#!/usr/bin/from dash import Dash, html, dcc, Input, Output, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import webbrowser
import threading
import ti        def update_rsi_chart(symbol, rsi_enabled, rsi_period):
            """Mise à jour du graphique RSI"""
            
            try:
                if not symbol or symbol not in self.market_data or not rsi_enabled:
                    return self.charts.create_empty_chart("RSI Disabled")
                    
                df = self.market_data[symbol]
                print(f"📊 Génération RSI pour {symbol}")
                
                return self.charts.create_rsi_chart(
                    df=df,
                    rsi_period=rsi_period or dash_config.default_periods['rsi']
                )
            except Exception as e:
                print(f"❌ Erreur callback RSI: {e}")
                return self.charts.create_empty_chart(f"RSI Error: {str(e)}")s modu        def update_volume_chart(symbol):
            """Mise à jour du graphique de volume"""
            
            try:
                if not symbol or symbol not in self.market_data:
                    return self.charts.create_empty_chart("No Volume Data")
                    
                df = self.market_data[symbol]
                print(f"📊 Génération Volume pour {symbol}")
                
                return self.charts.create_volume_chart(df=df)
            except Exception as e:
                print(f"❌ Erreur callback Volume: {e}")
                return self.charts.create_empty_chart(f"Volume Error: {str(e)}")HEBOT
from dash_modules.core.config import dash_config, ui_config
from dash_modules.core.calculators import calculator
from dash_modules.components.charts import ChartComponents
from dash_modules.components.controls import ControlsComponents
from dash_modules.features.ai_dashboard_simple import ai_engine
from dash_modules.features.ai_layout import ai_components
from dash_modules.data_providers.real_data_manager import real_data_manager

"""
THEBOT - Interface Dash Modulaire v2.0
Architecture propre et maintenable - Données réelles uniquement
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import dash
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any

# Imports des modules THEBOT Dash
from dash_modules.core.config import dash_config, ui_config
from dash_modules.core.calculators import calculator
from dash_modules.components.charts import charts
from dash_modules.components.controls import controls
from dash_modules.features.ai_dashboard_simple import ai_engine
from dash_modules.features.ai_layout import ai_components


class THEBOTDashApp:
    """Application THEBOT Dash avec architecture modulaire"""
    
    def __init__(self):
        # Configuration Dash
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[
                dash_config.theme,
                dbc.icons.FONT_AWESOME,
                "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
            ],
            suppress_callback_exceptions=True,
            update_title=None
        )
        
        self.app.title = dash_config.title
        
        # Initialisation des composants
        self.controls = ControlsComponents()
        self.charts = ChartComponents()
        
        # Initialisation des données réelles Binance
        print("🚀 Initialisation des données réelles Binance...")
        real_data_manager.get_configuration_info()
        self.market_data = self._load_binance_data()
        self.economic_events = []  # Pas d'actualités pour l'instant
        
        # État de l'application
        self.is_streaming = False
        
        # Configuration de l'interface
        self.setup_layout()
        self.setup_callbacks()
        
        print("✅ THEBOT Dash App initialisé avec architecture modulaire")
    
    def _load_binance_data(self) -> Dict[str, pd.DataFrame]:
        """Charger données Binance GRATUITES"""
        print("📊 Chargement des données Binance...")
        
        market_data = {}
        # Prendre les 5 premiers marchés populaires
        symbols = list(real_data_manager.supported_markets.keys())[:5]
        
        for symbol in symbols:
            print(f"🔄 Chargement {symbol}...")
            try:
                df = real_data_manager.get_market_data(symbol, '1h', 100)
                if df is not None and not df.empty:
                    market_data[symbol] = df
                    print(f"✅ {symbol}: {len(df)} points chargés")
                else:
                    print(f"⚠️ {symbol}: Aucune donnée disponible")
            except Exception as e:
                print(f"❌ Erreur {symbol}: {e}")
        
        print(f"🎯 Chargement terminé: {len(market_data)} actifs Binance disponibles")
        return market_data
    
    def setup_layout(self):
        """Configuration du layout principal"""
        
        self.app.layout = dbc.Container([
            
            # Header
            self.controls.create_header(),
            
            # Barre de contrôle principale
            self.controls.create_control_bar(),
            
            # Layout principal avec sidebar + contenu
            dbc.Row([
                
                # Sidebar gauche - Contrôles d'indicateurs
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            self.controls.create_indicators_sidebar()
                        ])
                    ])
                ], width=3),
                
                # Zone principale - Graphiques
                dbc.Col([
                    self.create_main_content()
                ], width=6),
                
                # Sidebar droite - Status et infos
                dbc.Col([
                    self.controls.create_status_info()
                ], width=3)
                
            ]),
            
            # Interval pour mises à jour temps réel
            dcc.Interval(
                id='realtime-interval',
                interval=5000,  # 5 secondes
                n_intervals=0,
                disabled=True
            )
            
        ], fluid=True, className="dbc dbc-ag-grid", style={
            'fontFamily': 'Inter, sans-serif',
            'backgroundColor': '#0d1117',
            'minHeight': '100vh'
        })
    
    def create_main_content(self):
        """Créer le contenu principal avec onglets"""
        
        return dbc.Card([
            dbc.CardBody([
                
                # Onglets principaux
                dbc.Tabs([
                    
                    # Onglet Analysis
                    dbc.Tab(
                        label="📊 Technical Analysis",
                        tab_id="analysis-tab",
                        children=[
                            self.create_analysis_content()
                        ]
                    ),
                    
                    # Onglet AI Dashboard
                    dbc.Tab(
                        label="🧠 AI Dashboard",
                        tab_id="ai-tab", 
                        children=[
                            html.Div(id="ai-dashboard-content", className="p-3")
                        ]
                    ),
                    
                    # Onglet Economic Calendar (placeholder)
                    dbc.Tab(
                        label="📅 Economic Calendar",
                        tab_id="economic-tab",
                        children=[
                            html.Div([
                                html.H4("📅 Economic Calendar", className="text-primary"),
                                dbc.Alert("Module Economic Calendar à venir...", color="info")
                            ], className="p-3")
                        ]
                    )
                    
                ], id="main-tabs", active_tab="analysis-tab")
                
            ])
        ])
    
    def create_analysis_content(self):
        """Contenu de l'onglet analyse technique"""
        
        return html.Div([
            
            # Graphique principal
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='main-chart',
                        style={'height': f'{ui_config.main_chart_height}px'}
                    )
                ], width=12)
            ], className="mb-3"),
            
            # Indicateurs secondaires en 3 colonnes
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='rsi-chart', style={'height': f'{ui_config.indicator_chart_height}px'})
                ], width=4),
                dbc.Col([
                    dcc.Graph(id='volume-chart', style={'height': f'{ui_config.indicator_chart_height}px'})
                ], width=4),
                dbc.Col([
                    dcc.Graph(id='atr-chart', style={'height': f'{ui_config.indicator_chart_height}px'})
                ], width=4)
            ])
            
        ], className="p-3")
    
    def setup_callbacks(self):
        """Configuration des callbacks"""
        
        # Callback graphique principal
        @self.app.callback(
            Output('main-chart', 'figure'),
            [Input('symbol-selector', 'value'),
             Input('timeframe-selector', 'value'),
             Input('sma-switch', 'value'),
             Input('ema-switch', 'value'),
             Input('sma-period', 'value'),
             Input('ema-period', 'value')]
        )
        def update_main_chart(symbol, timeframe, sma_enabled, ema_enabled, sma_period, ema_period):
            """Mise à jour du graphique principal"""
            
            try:
                # Vérifier que nous avons un symbol valide
                if not symbol or symbol not in self.market_data:
                    print(f"⚠️ Symbol invalide: {symbol}, marchés disponibles: {list(self.market_data.keys())}")
                    return self.charts.create_empty_chart(f"No data for {symbol or 'None'}")
                    
                df = self.market_data[symbol]
                print(f"📊 Génération graphique pour {symbol}: {len(df)} points")
                
                return self.charts.create_candlestick_chart(
                    df=df,
                    symbol=symbol,
                    timeframe=timeframe or '1h',
                    sma_enabled=sma_enabled or False,
                    sma_period=sma_period or 20,
                    ema_enabled=ema_enabled or False,
                    ema_period=ema_period or 12
                )
            except Exception as e:
                print(f"❌ Erreur callback main_chart: {e}")
                return self.charts.create_empty_chart(f"Error: {str(e)}")
        
        # Callback graphique RSI
        @self.app.callback(
            Output('rsi-chart', 'figure'),
            [Input('symbol-selector', 'value'),
             Input('rsi-switch', 'value'),
             Input('rsi-period', 'value')]
        )
        def update_rsi_chart(symbol, rsi_enabled, rsi_period):
            """Mise à jour du graphique RSI"""
            
            if not symbol or symbol not in self.market_data or not rsi_enabled:
                return self.charts.create_empty_chart("RSI Disabled")
                
            df = self.market_data[symbol]
            
            return self.charts.create_rsi_chart(
                df=df,
                rsi_period=rsi_period or 14
            )
        
        # Callback graphique Volume
        @self.app.callback(
            Output('volume-chart', 'figure'),
            Input('symbol-selector', 'value')
        )
        def update_volume_chart(symbol):
            """Mise à jour du graphique de volume"""
            
            if not symbol or symbol not in self.market_data:
                return self.charts.create_empty_chart("No Volume Data")
                
            df = self.market_data[symbol]
            return self.charts.create_volume_chart(df)
        
        # Callback graphique ATR
        @self.app.callback(
            Output('atr-chart', 'figure'),
            [Input('symbol-selector', 'value'),
             Input('atr-switch', 'value'),
             Input('atr-period', 'value')]
        )
        def update_atr_chart(symbol, atr_enabled, atr_period):
            """Mise à jour du graphique ATR"""
            
            try:
                if not symbol or symbol not in self.market_data or not atr_enabled:
                    return self.charts.create_empty_chart("ATR Disabled")
                    
                df = self.market_data[symbol]
                print(f"📊 Génération ATR pour {symbol}")
                
                return self.charts.create_atr_chart(
                    df=df,
                    atr_period=atr_period or dash_config.default_periods['atr']
                )
            except Exception as e:
                print(f"❌ Erreur callback ATR: {e}")
                return self.charts.create_empty_chart(f"ATR Error: {str(e)}")
        
        # Callback streaming temps réel
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
        
        # Callback AI Dashboard
        @self.app.callback(
            Output('ai-dashboard-content', 'children'),
            [Input('symbol-selector', 'value'),
             Input('rsi-period', 'value'),
             Input('sma-period', 'value'),
             Input('ema-period', 'value'),
             Input('atr-period', 'value')]
        )
        def update_ai_dashboard(symbol, rsi_period, sma_period, ema_period, atr_period):
            """Mise à jour du dashboard IA"""
            
            if not symbol or symbol not in self.market_data:
                return dbc.Alert("Sélectionnez un marché valide", color="warning")
                
            df = self.market_data[symbol]
            
            # Calcul des indicateurs pour l'analyse IA
            indicators = {
                'sma': calculator.calculate_sma(df['close'].tolist(), 
                                              sma_period or dash_config.default_periods['sma']),
                'ema': calculator.calculate_ema(df['close'].tolist(),
                                              ema_period or dash_config.default_periods['ema']),
                'rsi': calculator.calculate_rsi(df['close'].tolist(),
                                              rsi_period or dash_config.default_periods['rsi']),
                'atr': calculator.calculate_atr(df['high'].tolist(), df['low'].tolist(),
                                              df['close'].tolist(),
                                              atr_period or dash_config.default_periods['atr'])
            }
            
            # Analyse IA complète
            ai_analysis = ai_engine.get_comprehensive_analysis(symbol, df, indicators)
            
            # Génération du layout IA
            return ai_components.create_ai_dashboard_layout(ai_analysis)
    
    def run(self, debug: bool = True, port: int = None):
        """Lancer l'application"""
        
        port = port or dash_config.port
        
        print(f"""
🚀 THEBOT Dashboard v2.0 Starting...
        
📊 Professional Trading Interface Ready!
        
🌐 Access URL: http://localhost:{port}
        
✨ Features Available:
   • Modular architecture  
   • Real-time market analysis
   • Technical indicators (SMA, EMA, RSI, ATR)
   • Professional charting
   • Clean and maintainable code
        
🎯 Ready for professional trading analysis!
        """)
        
        self.app.run(
            debug=debug, 
            port=port, 
            host=dash_config.host
        )


def main():
    """Point d'entrée principal"""
    app = THEBOTDashApp()
    app.run()


if __name__ == '__main__':
    main()