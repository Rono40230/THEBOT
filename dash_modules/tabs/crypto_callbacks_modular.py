"""
THEBOT Crypto Callbacks Modulaires - Phase 5
Système de callbacks utilisant l'architecture modulaire complète
"""

import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, Input, Output, State, callback, no_update
from typing import Dict, List, Optional, Any

# Import des providers de données
from ..data_providers.binance_api import binance_provider
from ..data_providers.real_data_manager import real_data_manager

# Import des modules modulaires
try:
    from ..components.crypto_search_bar import crypto_search_bar
    from ..components.technical_indicators import technical_indicators
    from ..components.crypto_chart_components import crypto_chart_components
    MODULAR_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Callbacks modulaires non disponibles: {e}")
    MODULAR_COMPONENTS_AVAILABLE = False

# Import formatters
from ..core.price_formatter import format_crypto_price_adaptive, format_percentage_change, format_volume_adaptive

class CryptoCallbacksModular:
    """Gestionnaire de callbacks utilisant l'architecture modulaire"""
    
    def __init__(self):
        self.current_symbol = 'BTCUSDT'
        self.current_timeframe = '1h'
        self.indicators_config = {
            'rsi_period': 14,
            'atr_period': 14,
            'macd_params': (12, 26, 9),
            'structural_indicators': {
                'support_resistance_enabled': True,
                'fibonacci_enabled': True,
                'pivot_points_enabled': True
            }
        }
        print("🔧 Callbacks modulaires Phase 5 initialisés")

    def register_all_callbacks(self, app):
        """Enregistre tous les callbacks modulaires"""
        if not MODULAR_COMPONENTS_AVAILABLE:
            print("⚠️ Modules modulaires non disponibles - callbacks désactivés")
            return
        
        print("🚀 Enregistrement des callbacks modulaires Phase 5...")
        
        # Callback principal pour le graphique avec architecture modulaire
        self.register_main_chart_callback(app)
        
        # Callbacks pour les graphiques secondaires
        self.register_secondary_charts_callbacks(app)
        
        # Callback pour l'affichage du prix en temps réel
        self.register_price_display_callback(app)
        
        # Callbacks pour les AI insights
        self.register_ai_insights_callbacks(app)
        
        print("✅ Tous les callbacks modulaires enregistrés")

    def register_main_chart_callback(self, app):
        """Callback principal utilisant les composants modulaires"""
        
        @app.callback(
            Output('crypto-main-chart', 'figure'),
            [Input('crypto-symbol-search', 'value'),
             Input('crypto-timeframe-selector', 'value')],
            prevent_initial_call=False
        )
        def update_main_chart_modular(symbol, timeframe):
            """Met à jour le graphique principal avec architecture modulaire"""
            try:
                # Utiliser les valeurs par défaut si nécessaire
                symbol = symbol or self.current_symbol
                timeframe = timeframe or self.current_timeframe
                
                # Mettre à jour les variables d'état
                self.current_symbol = symbol
                self.current_timeframe = timeframe
                
                print(f"📊 Mise à jour graphique modulaire: {symbol} / {timeframe}")
                
                # Récupération des données via le data manager
                data = real_data_manager.get_crypto_data(symbol, timeframe, limit=200)
                
                if data is None or data.empty:
                    return crypto_chart_components.create_empty_chart(
                        f"Aucune donnée disponible pour {symbol}"
                    )
                
                # Calculs des indicateurs techniques via le module modulaire
                all_indicators = technical_indicators.calculate_all_indicators(
                    data, self.indicators_config
                )
                
                # Création du graphique principal via le composant modulaire
                fig = crypto_chart_components.create_candlestick_chart(
                    data, symbol, timeframe
                )
                
                # Ajout des niveaux structurels via le composant modulaire
                if all_indicators.get('structural'):
                    fig = crypto_chart_components.add_structural_levels_to_chart(
                        fig, all_indicators['structural']
                    )
                
                return fig
                
            except Exception as e:
                print(f"❌ Erreur callback graphique principal: {e}")
                return crypto_chart_components.create_empty_chart(
                    f"Erreur: {str(e)}"
                )

    def register_secondary_charts_callbacks(self, app):
        """Callbacks pour les graphiques secondaires RSI, ATR, MACD"""
        
        # Callback RSI
        @app.callback(
            Output('crypto-rsi-chart', 'figure'),
            [Input('crypto-symbol-search', 'value'),
             Input('crypto-timeframe-selector', 'value')],
            prevent_initial_call=False
        )
        def update_rsi_chart_modular(symbol, timeframe):
            """Met à jour le graphique RSI avec composants modulaires"""
            try:
                symbol = symbol or self.current_symbol
                timeframe = timeframe or self.current_timeframe
                
                # Récupération des données
                data = real_data_manager.get_crypto_data(symbol, timeframe, limit=100)
                
                if data is None or data.empty:
                    return crypto_chart_components.create_empty_chart("Pas de données RSI")
                
                # Calcul RSI via le module modulaire
                rsi_series = technical_indicators.calculate_rsi(
                    data['close'], period=self.indicators_config['rsi_period']
                )
                
                # Création du graphique RSI via le composant modulaire
                return crypto_chart_components.create_rsi_chart(data, rsi_series, symbol)
                
            except Exception as e:
                print(f"❌ Erreur RSI modulaire: {e}")
                return crypto_chart_components.create_empty_chart("Erreur RSI")

        # Callback ATR
        @app.callback(
            Output('crypto-atr-chart', 'figure'),
            [Input('crypto-symbol-search', 'value'),
             Input('crypto-timeframe-selector', 'value')],
            prevent_initial_call=False
        )
        def update_atr_chart_modular(symbol, timeframe):
            """Met à jour le graphique ATR avec composants modulaires"""
            try:
                symbol = symbol or self.current_symbol
                timeframe = timeframe or self.current_timeframe
                
                # Récupération des données
                data = real_data_manager.get_crypto_data(symbol, timeframe, limit=100)
                
                if data is None or data.empty:
                    return crypto_chart_components.create_empty_chart("Pas de données ATR")
                
                # Calcul ATR via le module modulaire
                atr_data = technical_indicators.calculate_atr(
                    data, period=self.indicators_config['atr_period']
                )
                
                # Création du graphique ATR via le composant modulaire
                return crypto_chart_components.create_atr_chart(data, atr_data, symbol)
                
            except Exception as e:
                print(f"❌ Erreur ATR modulaire: {e}")
                return crypto_chart_components.create_empty_chart("Erreur ATR")

        # Callback MACD
        @app.callback(
            Output('crypto-macd-chart', 'figure'),
            [Input('crypto-symbol-search', 'value'),
             Input('crypto-timeframe-selector', 'value')],
            prevent_initial_call=False
        )
        def update_macd_chart_modular(symbol, timeframe):
            """Met à jour le graphique MACD avec composants modulaires"""
            try:
                symbol = symbol or self.current_symbol
                timeframe = timeframe or self.current_timeframe
                
                # Récupération des données
                data = real_data_manager.get_crypto_data(symbol, timeframe, limit=100)
                
                if data is None or data.empty:
                    return crypto_chart_components.create_empty_chart("Pas de données MACD")
                
                # Calcul MACD via le module modulaire
                macd_data = technical_indicators.calculate_macd(
                    data['close'], *self.indicators_config['macd_params']
                )
                
                # Création du graphique MACD via le composant modulaire
                return crypto_chart_components.create_macd_chart(data, macd_data, symbol)
                
            except Exception as e:
                print(f"❌ Erreur MACD modulaire: {e}")
                return crypto_chart_components.create_empty_chart("Erreur MACD")

    def register_price_display_callback(self, app):
        """Callback pour l'affichage du prix en temps réel"""
        
        @app.callback(
            [Output('crypto-price-display', 'children'),
             Output('crypto-price-change', 'children'),
             Output('crypto-volume-display', 'children')],
            [Input('crypto-symbol-search', 'value')],
            prevent_initial_call=False
        )
        def update_price_display_modular(selected_symbol):
            """Met à jour l'affichage du prix avec formatage modulaire"""
            try:
                symbol = selected_symbol or self.current_symbol
                
                # Données en temps réel depuis Binance
                ticker_data = binance_provider.get_ticker_24hr(symbol)
                
                if ticker_data and 'lastPrice' in ticker_data:
                    # Formatage adaptatif du prix
                    price = float(ticker_data['lastPrice'])
                    formatted_price = format_crypto_price_adaptive(price)
                    
                    # Formatage du changement avec couleur
                    price_change_percent = float(ticker_data.get('priceChangePercent', 0))
                    formatted_change = format_percentage_change(price_change_percent)
                    change_class = "text-success" if price_change_percent >= 0 else "text-danger"
                    
                    # Formatage du volume
                    volume = float(ticker_data.get('volume', 0))
                    formatted_volume = format_volume_adaptive(volume)
                    
                    # Retourner des éléments sérialisables
                    price_display = formatted_price
                    change_display = html.Span(formatted_change, className=change_class)
                    volume_display = formatted_volume
                    
                    return [price_display, change_display, volume_display]
                else:
                    return ["--", html.Span("--", className="text-muted"), "--"]
                    
            except Exception as e:
                print(f"⚠️ Erreur price display modulaire: {e}")
                return ["Error", html.Span("--", className="text-muted"), "--"]

    def register_ai_insights_callbacks(self, app):
        """Callbacks pour les cartes AI Insights"""
        
        @app.callback(
            [Output('crypto-ai-sentiment-content', 'children'),
             Output('crypto-ai-technical-content', 'children'),
             Output('crypto-ai-signals-content', 'children')],
            [Input('crypto-symbol-search', 'value'),
             Input('crypto-timeframe-selector', 'value')],
            prevent_initial_call=True
        )
        def update_ai_insights_modular(symbol, timeframe):
            """Met à jour les insights IA avec analyse modulaire"""
            try:
                symbol = symbol or self.current_symbol
                timeframe = timeframe or self.current_timeframe
                
                # Récupération des données pour l'analyse IA
                data = real_data_manager.get_crypto_data(symbol, timeframe, limit=50)
                
                if data is None or data.empty:
                    empty_content = html.P("Pas de données", className="text-center text-muted")
                    return [empty_content, empty_content, empty_content]
                
                # Calculs techniques pour l'IA
                indicators = technical_indicators.calculate_all_indicators(
                    data, self.indicators_config
                )
                
                # Analyse de sentiment basique
                sentiment_content = self.create_sentiment_analysis(data, indicators)
                
                # Analyse technique basique
                technical_content = self.create_technical_analysis(data, indicators)
                
                # Signaux de trading basiques
                signals_content = self.create_trading_signals(data, indicators)
                
                return [sentiment_content, technical_content, signals_content]
                
            except Exception as e:
                print(f"⚠️ Erreur AI insights modulaire: {e}")
                error_content = html.P("Erreur analyse", className="text-center text-danger")
                return [error_content, error_content, error_content]

    def create_sentiment_analysis(self, data, indicators):
        """Crée l'analyse de sentiment basique"""
        try:
            # Calculs de base pour le sentiment
            price_change = ((data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0]) * 100
            volume_trend = data['volume'].tail(5).mean() / data['volume'].head(5).mean()
            
            # Détermination du sentiment
            if price_change > 2 and volume_trend > 1.2:
                sentiment = "🟢 Bullish"
                color = "success"
            elif price_change < -2 and volume_trend > 1.2:
                sentiment = "🔴 Bearish"
                color = "danger"
            else:
                sentiment = "🟡 Neutre"
                color = "warning"
            
            return html.Div([
                html.H6(sentiment, className=f"text-{color}"),
                html.P(f"Prix: {price_change:+.2f}%", className="small mb-1"),
                html.P(f"Volume: {(volume_trend-1)*100:+.1f}%", className="small mb-0")
            ])
            
        except Exception as e:
            return html.P("Erreur sentiment", className="text-danger small")

    def create_technical_analysis(self, data, indicators):
        """Crée l'analyse technique basique"""
        try:
            analysis_points = []
            
            # RSI Analysis
            if 'rsi' in indicators:
                rsi_current = indicators['rsi'].iloc[-1] if not indicators['rsi'].empty else 50
                if rsi_current > 70:
                    analysis_points.append("RSI: Surachat")
                elif rsi_current < 30:
                    analysis_points.append("RSI: Survente")
                else:
                    analysis_points.append(f"RSI: {rsi_current:.1f}")
            
            # Price vs MA
            if len(data) > 20:
                ma20 = data['close'].rolling(20).mean().iloc[-1]
                current_price = data['close'].iloc[-1]
                if current_price > ma20:
                    analysis_points.append("Prix > MA20")
                else:
                    analysis_points.append("Prix < MA20")
            
            return html.Div([
                html.P(point, className="small mb-1") for point in analysis_points[:3]
            ])
            
        except Exception as e:
            return html.P("Erreur technique", className="text-danger small")

    def create_trading_signals(self, data, indicators):
        """Crée les signaux de trading basiques"""
        try:
            signals = []
            
            # Signal basé sur la tendance
            if len(data) > 10:
                recent_trend = (data['close'].iloc[-1] - data['close'].iloc[-10]) / data['close'].iloc[-10] * 100
                if recent_trend > 3:
                    signals.append("🟢 Tendance haussière")
                elif recent_trend < -3:
                    signals.append("🔴 Tendance baissière")
                else:
                    signals.append("🟡 Consolidation")
            
            # Signal de volume
            if len(data) > 5:
                volume_increase = data['volume'].tail(3).mean() > data['volume'].head(-3).mean()
                if volume_increase:
                    signals.append("📈 Volume croissant")
                else:
                    signals.append("📉 Volume décroissant")
            
            return html.Div([
                html.P(signal, className="small mb-1") for signal in signals[:2]
            ])
            
        except Exception as e:
            return html.P("Erreur signaux", className="text-danger small")

# Instance globale des callbacks modulaires
crypto_callbacks_modular = CryptoCallbacksModular()

def register_crypto_callbacks_modular(app):
    """Fonction principale pour enregistrer tous les callbacks modulaires"""
    try:
        crypto_callbacks_modular.register_all_callbacks(app)
        print("✅ Callbacks modulaires Phase 5 enregistrés avec succès")
    except Exception as e:
        print(f"❌ Erreur enregistrement callbacks modulaires: {e}")
        import traceback
        traceback.print_exc()

# Export des fonctions principales
__all__ = ['register_crypto_callbacks_modular', 'crypto_callbacks_modular', 'CryptoCallbacksModular']