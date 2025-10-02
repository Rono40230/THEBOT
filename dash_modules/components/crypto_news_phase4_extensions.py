"""
Phase 4 Extensions for Crypto News Module
Widgets compacts modulaires pour intégration dans crypto_news_module
Approche sûre et non-invasive
"""

import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from typing import Dict, List, Optional

# Imports conditionnels Phase 4 (modulaire)
try:
    from ..components.crypto_trends import crypto_trends
    from ..components.top_performers import top_performers
    from ..components.fear_greed_gauge import fear_greed_gauge
    PHASE4_AVAILABLE = True
    print("✅ Phase 4 crypto widgets disponibles")
except ImportError:
    PHASE4_AVAILABLE = False
    print("⚠️ Phase 4 crypto widgets non disponibles")


class CryptoNewsPhase4Extensions:
    """Extensions Phase 4 pour le module crypto news"""
    
    def __init__(self):
        self.widget_prefix = "crypto-news-p4"
        
    def get_compact_widgets_layout(self) -> html.Div:
        """Retourne le layout des widgets compacts Phase 4"""
        if not PHASE4_AVAILABLE:
            return html.Div([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("📊 Advanced Analysis", className="mb-2"),
                        html.P("Widgets Phase 4 non disponibles", className="text-muted small mb-0")
                    ])
                ], className="mb-3")
            ])
        
        return html.Div([
            # Fear & Greed Index Compact
            dbc.Card([
                dbc.CardHeader([
                    html.H6("😨 Fear & Greed", className="mb-0 small")
                ]),
                dbc.CardBody([
                    html.Div(id=f"{self.widget_prefix}-fear-greed", className="text-center")
                ], className="py-2")
            ], className="mb-2"),
            
            # Top Performers Compact  
            dbc.Card([
                dbc.CardHeader([
                    html.H6("🏆 Top Gainers", className="mb-0 small")
                ]),
                dbc.CardBody([
                    html.Div(id=f"{self.widget_prefix}-gainers")
                ], className="py-2")
            ], className="mb-2"),
            
            # Market Trends Compact
            dbc.Card([
                dbc.CardHeader([
                    html.H6("📈 Market Pulse", className="mb-0 small")
                ]),
                dbc.CardBody([
                    html.Div(id=f"{self.widget_prefix}-trends")
                ], className="py-2")
            ], className="mb-2"),
            
            # Auto-refresh interval
            dcc.Interval(
                id=f"{self.widget_prefix}-interval",
                interval=60*1000,  # 1 minute
                n_intervals=0
            )
        ])
    
    def register_callbacks(self):
        """Enregistre les callbacks pour les widgets compacts"""
        if not PHASE4_AVAILABLE:
            return
            
        # Callback Fear & Greed
        @callback(
            Output(f"{self.widget_prefix}-fear-greed", 'children'),
            [Input(f"{self.widget_prefix}-interval", 'n_intervals')],
            prevent_initial_call=False
        )
        def update_fear_greed_compact(n_intervals):
            try:
                data = fear_greed_gauge.get_fear_greed_index()
                if not data:
                    return html.P("N/A", className="text-muted mb-0")
                
                value = data['value']
                classification = data['value_classification']
                
                # Couleur selon valeur
                if value <= 25:
                    color_class = "text-danger"
                    emoji = "😱"
                elif value <= 45:
                    color_class = "text-warning"
                    emoji = "😰"
                elif value <= 55:
                    color_class = "text-secondary"
                    emoji = "😐"
                elif value <= 75:
                    color_class = "text-info"
                    emoji = "😊"
                else:
                    color_class = "text-success"
                    emoji = "🤑"
                
                return html.Div([
                    html.H5(f"{emoji} {value}", className=f"{color_class} mb-1"),
                    html.P(classification, className="small text-muted mb-0")
                ])
                
            except Exception as e:
                return html.P("Erreur", className="text-muted small mb-0")
        
        # Callback Top Gainers
        @callback(
            Output(f"{self.widget_prefix}-gainers", 'children'),
            [Input(f"{self.widget_prefix}-interval", 'n_intervals')],
            prevent_initial_call=False
        )
        def update_gainers_compact(n_intervals):
            try:
                gainers = top_performers.get_top_gainers(3)
                if not gainers:
                    return html.P("N/A", className="text-muted small mb-0")
                
                items = []
                for gainer in gainers:
                    symbol = gainer['symbol'].replace('USDT', '')
                    change = gainer['change_percent']
                    
                    items.append(
                        html.Div([
                            html.Span(f"{symbol}: ", className="fw-bold small"),
                            html.Span(f"+{change:.1f}%", className="text-success small")
                        ], className="d-flex justify-content-between")
                    )
                
                return html.Div(items)
                
            except Exception as e:
                return html.P("Erreur", className="text-muted small mb-0")
        
        # Callback Market Trends
        @callback(
            Output(f"{self.widget_prefix}-trends", 'children'),
            [Input(f"{self.widget_prefix}-interval", 'n_intervals')],
            prevent_initial_call=False
        )
        def update_trends_compact(n_intervals):
            try:
                # Volume analysis
                volume_analysis = crypto_trends.get_volume_analysis()
                if not volume_analysis:
                    return html.P("N/A", className="text-muted small mb-0")
                
                sentiment = volume_analysis.get('market_sentiment', 'Unknown')
                gainers_count = volume_analysis.get('gainers_count', 0)
                losers_count = volume_analysis.get('losers_count', 0)
                
                # Tendance générale
                if gainers_count > losers_count:
                    trend_emoji = "📈"
                    trend_color = "text-success"
                elif losers_count > gainers_count:
                    trend_emoji = "📉"
                    trend_color = "text-danger"
                else:
                    trend_emoji = "➡️"
                    trend_color = "text-secondary"
                
                return html.Div([
                    html.P([
                        html.Span(f"{trend_emoji} ", className=trend_color),
                        html.Span(f"{gainers_count}↗️ {losers_count}↘️", className="small")
                    ], className="mb-1"),
                    html.P(sentiment.split()[1] if len(sentiment.split()) > 1 else sentiment, 
                           className="small text-muted mb-0")
                ])
                
            except Exception as e:
                return html.P("Erreur", className="text-muted small mb-0")


# Instance globale pour utilisation modulaire
crypto_news_phase4_extensions = CryptoNewsPhase4Extensions()


def get_phase4_sidebar_widgets() -> html.Div:
    """Fonction utilitaire pour obtenir les widgets Phase 4"""
    return crypto_news_phase4_extensions.get_compact_widgets_layout()


def register_phase4_callbacks():
    """Fonction utilitaire pour enregistrer les callbacks Phase 4"""
    crypto_news_phase4_extensions.register_callbacks()


# Auto-registration des callbacks si importé
if PHASE4_AVAILABLE:
    register_phase4_callbacks()