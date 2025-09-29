#!/usr/bin/env python3
"""
THEBOT - Interface Dash Simple et Fonctionnelle
VERSION CORRIGÉE - Données Binance réelles uniquement
"""

import dash
from dash import dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Imports modulaires THEBOT
from dash_modules.core.config import dash_config, ui_config
from dash_modules.core.calculators import calculator
from dash_modules.components.charts import ChartComponents
from dash_modules.components.controls import ControlsComponents
from dash_modules.data_providers.real_data_manager import real_data_manager


class TheBotDashApp:
    """Application Dash THEBOT simplifiée et fonctionnelle"""
    
    def __init__(self):
        """Initialisation de l'application"""
        
        # Configuration Dash
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dash_config.theme],
            suppress_callback_exceptions=True,
            title=dash_config.title
        )
        
        # Initialisation des composants
        self.controls = ControlsComponents()
        self.charts = ChartComponents()
        
        # Chargement des données Binance réelles
        print("🚀 Chargement des données Binance réelles...")
        real_data_manager.get_configuration_info()
        self.market_data = self._load_binance_data()
        
        # Configuration de l'interface
        self.setup_layout()
        self.setup_callbacks()
        
        print("✅ THEBOT Dash App Simple initialisé avec succès")
    
    def _load_binance_data(self):
        """Charger données Binance réelles"""
        print("📊 Chargement des données Binance...")
        
        market_data = {}
        symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
        
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
                print(f"❌ Erreur chargement {symbol}: {e}")
        
        print(f"🎯 Chargement terminé: {len(market_data)} actifs Binance disponibles")
        return market_data
    
    def setup_layout(self):
        """Configuration du layout"""
        
        self.app.layout = dbc.Container([
            
            # Header
            self.controls.create_header(),
            
            # Barre de contrôle principale  
            self.controls.create_control_bar(),
            
            # Layout principal
            dbc.Row([
                
                # Sidebar gauche - Indicateurs
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
                
                # Sidebar droite - Status
                dbc.Col([
                    self.controls.create_status_info()
                ], width=3)
                
            ])
            
        ], fluid=True, className="dbc", style={
            'fontFamily': 'Inter, sans-serif',
            'backgroundColor': '#0e1117',
            'color': 'white',
            'minHeight': '100vh'
        })
    
    def create_main_content(self):
        """Contenu principal avec graphiques"""
        
        return dbc.Card([
            dbc.CardBody([
                
                # Graphique principal
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(
                            id='main-chart',
                            style={'height': f'{ui_config.main_chart_height}px'}
                        )
                    ], width=12)
                ], className="mb-3"),
                
                # Indicateurs secondaires
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
                
            ])
        ])
    
    def setup_callbacks(self):
        """Configuration des callbacks avec gestion d'erreur"""
        
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
            """Mise à jour du graphique principal avec gestion d'erreur"""
            
            try:
                print(f"🔄 Callback main_chart: symbol={symbol}, timeframe={timeframe}")
                
                # Vérifications
                if not symbol:
                    print("⚠️ Aucun symbol sélectionné")
                    return self.charts.create_empty_chart("Sélectionnez un marché")
                
                if symbol not in self.market_data:
                    print(f"⚠️ Symbol {symbol} non trouvé dans {list(self.market_data.keys())}")
                    return self.charts.create_empty_chart(f"Données non disponibles pour {symbol}")
                
                # Génération du graphique
                df = self.market_data[symbol]
                print(f"✅ Génération graphique {symbol}: {len(df)} points")
                
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
                import traceback
                traceback.print_exc()
                return self.charts.create_empty_chart(f"Erreur: {str(e)}")
        
        # Callback RSI
        @self.app.callback(
            Output('rsi-chart', 'figure'),
            [Input('symbol-selector', 'value'),
             Input('rsi-switch', 'value'),
             Input('rsi-period', 'value')]
        )
        def update_rsi_chart(symbol, rsi_enabled, rsi_period):
            """Mise à jour RSI avec gestion d'erreur"""
            
            try:
                if not rsi_enabled or not symbol or symbol not in self.market_data:
                    return self.charts.create_empty_chart("RSI Désactivé")
                
                df = self.market_data[symbol]
                print(f"📊 Génération RSI pour {symbol}")
                
                return self.charts.create_rsi_chart(
                    df=df,
                    rsi_period=rsi_period or 14
                )
                
            except Exception as e:
                print(f"❌ Erreur RSI: {e}")
                return self.charts.create_empty_chart(f"Erreur RSI: {str(e)}")
        
        # Callback Volume
        @self.app.callback(
            Output('volume-chart', 'figure'),
            Input('symbol-selector', 'value')
        )
        def update_volume_chart(symbol):
            """Mise à jour Volume avec gestion d'erreur"""
            
            try:
                if not symbol or symbol not in self.market_data:
                    return self.charts.create_empty_chart("Pas de données Volume")
                
                df = self.market_data[symbol]
                print(f"📊 Génération Volume pour {symbol}")
                
                return self.charts.create_volume_chart(df=df)
                
            except Exception as e:
                print(f"❌ Erreur Volume: {e}")
                return self.charts.create_empty_chart(f"Erreur Volume: {str(e)}")
        
        # Callback ATR
        @self.app.callback(
            Output('atr-chart', 'figure'),
            [Input('symbol-selector', 'value'),
             Input('atr-switch', 'value'),
             Input('atr-period', 'value')]
        )
        def update_atr_chart(symbol, atr_enabled, atr_period):
            """Mise à jour ATR avec gestion d'erreur"""
            
            try:
                if not atr_enabled or not symbol or symbol not in self.market_data:
                    return self.charts.create_empty_chart("ATR Désactivé")
                
                df = self.market_data[symbol]
                print(f"📊 Génération ATR pour {symbol}")
                
                return self.charts.create_atr_chart(
                    df=df,
                    atr_period=atr_period or 14
                )
                
            except Exception as e:
                print(f"❌ Erreur ATR: {e}")
                return self.charts.create_empty_chart(f"Erreur ATR: {str(e)}")
    
    def run(self):
        """Démarrer l'application"""
        
        print(f"""
🚀 THEBOT Dashboard Simple Starting...
        
📊 Professional Trading Interface Ready!
        
🌐 Access URL: http://localhost:{dash_config.port}
        
✨ Features Available:
   • Real Binance data only ({len(self.market_data)} markets)
   • Technical indicators (SMA, EMA, RSI, ATR)
   • Professional charting
   • Error-free callbacks
        
🎯 Ready for professional trading analysis!
        """)
        
        self.app.run(
            host=dash_config.host,
            port=dash_config.port,
            debug=dash_config.debug
        )


if __name__ == '__main__':
    app = TheBotDashApp()
    app.run()