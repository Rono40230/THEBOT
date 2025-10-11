"""
THEBOT - Crypto Chart Components
Module dédié pour tous les composants graphiques crypto
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
from typing import Dict, Any, Optional
from dash_modules.core.price_formatter import format_crypto_price_adaptive, format_percentage_change, format_volume_adaptive


class CryptoChartComponents:
    """Classe pour créer tous les composants graphiques crypto"""
    
    def __init__(self):
        self.chart_config = {
            'displayModeBar': True,
            'displaylogo': False,
            'responsive': True,
            'modeBarButtonsToRemove': [
                'pan2d', 'lasso2d', 'select2d',
                'autoScale2d', 'hoverClosestCartesian'
            ]
        }
        
        self.secondary_chart_config = {
            'displayModeBar': False,
            'responsive': True
        }
    
    # === CRÉATION DES COMPOSANTS ===
    
    def create_main_chart(self) -> dcc.Graph:
        """Crée le graphique principal avec candlesticks"""
        return dcc.Graph(
            id='crypto-main-chart',
            style={'height': '600px', 'width': '100%'},
            config=self.chart_config
        )

    def create_secondary_charts(self) -> dbc.Row:
        """Crée les 3 graphiques secondaires (RSI, ATR, MACD)"""
        return dbc.Row([
            # RSI Chart
            dbc.Col([
                dcc.Graph(
                    id='crypto-rsi-chart',
                    style={'height': '400px', 'margin': '0px', 'margin-top': '30px', 'width': '100%'},
                    config=self.secondary_chart_config
                )
            ], width=4, style={'padding': '2px'}, xs=12, sm=12, md=6, lg=4),
            
            # ATR Chart
            dbc.Col([
                dcc.Graph(
                    id='crypto-atr-chart',
                    style={'height': '400px', 'margin': '0px', 'margin-top': '30px', 'width': '100%'},
                    config=self.secondary_chart_config
                )
            ], width=4, style={'padding': '2px'}, xs=12, sm=12, md=6, lg=4),
            
            # MACD Chart
            dbc.Col([
                dcc.Graph(
                    id='crypto-macd-chart',
                    style={'height': '400px', 'margin': '0px', 'margin-top': '30px', 'width': '100%'},
                    config=self.secondary_chart_config
                )
            ], width=4, style={'padding': '2px'}, xs=12, sm=12, md=12, lg=4)
        ], style={'margin': '0px'}, className="g-2")

    def create_ai_insights_cards(self) -> dbc.Row:
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
            
            # Trading Signals
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-robot me-2"),
                        "Trading Signals (AI)"
                    ], className="bg-success text-white"),
                    dbc.CardBody([
                        html.Div(
                            id="crypto-ai-signals-content",
                            children=[
                                dbc.Spinner([
                                    html.P("Analyzing...", className="text-center text-muted")
                                ], color="success")
                            ]
                        )
                    ])
                ], className="h-100")
            ], width=4)
        ], className="mb-4")

    # === MÉTHODES DE CRÉATION DES GRAPHIQUES ===
    
    def create_candlestick_chart(self, data: pd.DataFrame, symbol: str, timeframe: str) -> go.Figure:
        """Crée un graphique candlestick avec volume"""
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Aucune donnée disponible",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Créer subplots avec prix et volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.75, 0.25]
        )
        
        # Candlesticks
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name=symbol,
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4444',
            showlegend=True
        ), row=1, col=1)
        
        # Volume
        colors = ['#00ff88' if close >= open else '#ff4444' 
                 for close, open in zip(data['close'], data['open'])]
        
        fig.add_trace(go.Bar(
            x=data.index,
            y=data['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.6,
            showlegend=True
        ), row=2, col=1)
        
        # Style du graphique
        fig.update_layout(
            title=f"{symbol} - {timeframe}",
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            height=600,
            margin=dict(l=0, r=0, t=50, b=0),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig

    def create_rsi_chart(self, data: pd.DataFrame, rsi_data: pd.Series, symbol: str) -> go.Figure:
        """Crée un graphique RSI"""
        fig = go.Figure()
        
        if not rsi_data.empty:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=rsi_data,
                mode='lines',
                name='RSI',
                line=dict(color='#FFA500', width=2)
            ))
            
            # Lignes de surachat/survente
            fig.add_hline(y=70, line=dict(color='red', dash='dash'), annotation_text="Surachat")
            fig.add_hline(y=30, line=dict(color='green', dash='dash'), annotation_text="Survente")
            fig.add_hline(y=50, line=dict(color='gray', dash='dot'), annotation_text="Ligne médiane")
        
        fig.update_layout(
            title=f"RSI - {symbol}",
            yaxis=dict(range=[0, 100]),
            template='plotly_dark',
            height=400,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        
        return fig

    def create_atr_chart(self, data: pd.DataFrame, atr_data: Dict, symbol: str) -> go.Figure:
        """Crée un graphique ATR avec signaux"""
        fig = go.Figure()
        
        if atr_data and 'atr' in atr_data:
            # ATR principal
            fig.add_trace(go.Scatter(
                x=data.index,
                y=atr_data['atr'],
                mode='lines',
                name='ATR',
                line=dict(color='#00BFFF', width=2)
            ))
            
            # Moyenne mobile ATR
            if 'atr_ma' in atr_data:
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=atr_data['atr_ma'],
                    mode='lines',
                    name='ATR MA',
                    line=dict(color='#FFD700', width=1, dash='dash')
                ))
            
            # Seuils de volatilité
            if 'upper_threshold' in atr_data:
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=atr_data['upper_threshold'],
                    mode='lines',
                    name='Seuil Haut',
                    line=dict(color='red', width=1, dash='dot'),
                    opacity=0.7
                ))
            
            if 'lower_threshold' in atr_data:
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=atr_data['lower_threshold'],
                    mode='lines',
                    name='Seuil Bas',
                    line=dict(color='green', width=1, dash='dot'),
                    opacity=0.7
                ))
        
        fig.update_layout(
            title=f"ATR (Volatilité) - {symbol}",
            template='plotly_dark',
            height=400,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        
        return fig

    def create_macd_chart(self, data: pd.DataFrame, macd_data: Dict, symbol: str) -> go.Figure:
        """Crée un graphique MACD"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3]
        )
        
        if macd_data and 'macd' in macd_data:
            # Ligne MACD
            fig.add_trace(go.Scatter(
                x=data.index,
                y=macd_data['macd'],
                mode='lines',
                name='MACD',
                line=dict(color='#00BFFF', width=2)
            ), row=1, col=1)
            
            # Ligne de signal
            if 'signal' in macd_data:
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=macd_data['signal'],
                    mode='lines',
                    name='Signal',
                    line=dict(color='#FF6347', width=2)
                ), row=1, col=1)
            
            # Histogramme
            if 'histogram' in macd_data:
                colors = ['green' if h >= 0 else 'red' for h in macd_data['histogram']]
                fig.add_trace(go.Bar(
                    x=data.index,
                    y=macd_data['histogram'],
                    name='Histogramme',
                    marker_color=colors,
                    opacity=0.7
                ), row=2, col=1)
        
        fig.update_layout(
            title=f"MACD - {symbol}",
            template='plotly_dark',
            height=400,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        
        return fig

    def add_structural_levels_to_chart(self, fig: go.Figure, structural_data: Dict) -> go.Figure:
        """Ajoute les niveaux structurels au graphique principal"""
        if not structural_data:
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
                        annotation_position="right",
                        row=1, col=1
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
                        annotation_position="right",
                        row=1, col=1
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
                        row=1, col=1
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
                        row=1, col=1
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
                        row=1, col=1
                    )
                    
        except Exception as e:
            print(f"⚠️ Erreur ajout niveaux structurels: {e}")
        
        return fig

    def create_empty_chart(self, message: str = "Aucune donnée disponible") -> go.Figure:
        """Crée un graphique vide avec message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            template='plotly_dark',
            height=400
        )
        return fig

# Instance globale pour l'utilisation dans les modules
crypto_chart_components = CryptoChartComponents()