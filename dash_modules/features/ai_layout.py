"""
AI Dashboard Layout Components - THEBOT Dash
Composants d'interface pour le dashboard IA
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any
from datetime import datetime


class AIDashboardComponents:
    """Composants d'interface pour le dashboard IA"""
    
    def __init__(self):
        self.colors = {
            'bullish': '#10b981',
            'bearish': '#ef4444', 
            'neutral': '#6b7280',
            'ai_primary': '#3b82f6',
            'ai_secondary': '#8b5cf6'
        }
    
    def create_ai_status_card(self, ai_status: str = "simulation_mode") -> dbc.Card:
        """Carte de statut IA"""
        
        if ai_status == "simulation_mode":
            color = "info"
            icon = "fas fa-cog"
            title = "AI Mode: Simulation"
            description = "Analyses intelligentes basées sur logique technique avancée"
        else:
            color = "success"
            icon = "fas fa-brain"
            title = "AI Mode: Active"
            description = "Analyses IA en temps réel via OpenAI/Claude"
            
        return dbc.Card([
            dbc.CardHeader([
                html.I(className=f"{icon} me-2"),
                html.Strong(title)
            ]),
            dbc.CardBody([
                html.P(description, className="mb-0 text-muted")
            ])
        ], color=color, outline=True, className="mb-3")
    
    def create_sentiment_card(self, sentiment_data: Dict[str, Any]) -> dbc.Card:
        """Carte d'analyse de sentiment"""
        
        sentiment = sentiment_data.get('sentiment', 'Neutral')
        confidence = sentiment_data.get('confidence', 0)
        reasoning = sentiment_data.get('reasoning', 'Analyse en cours...')
        
        # Couleur basée sur sentiment
        if sentiment == 'Bullish':
            color = 'success'
            icon = 'fas fa-arrow-up'
        elif sentiment == 'Bearish':
            color = 'danger' 
            icon = 'fas fa-arrow-down'
        else:
            color = 'warning'
            icon = 'fas fa-minus'
        
        return dbc.Card([
            dbc.CardHeader([
                html.I(className=f"{icon} me-2"),
                html.Strong("Market Sentiment"),
                dbc.Badge(f"{confidence}%", color="light", className="ms-2")
            ]),
            dbc.CardBody([
                html.H4(sentiment, className=f"text-{color} mb-2"),
                html.P(reasoning, className="mb-0")
            ])
        ], className="mb-3")
    
    def create_prediction_card(self, prediction_data: Dict[str, Any]) -> dbc.Card:
        """Carte de prédiction de prix"""
        
        direction = prediction_data.get('direction', 'Sideways')
        target_price = prediction_data.get('target_price', 0)
        change_percent = prediction_data.get('change_percent', 0)
        confidence = prediction_data.get('confidence', 0)
        timeframe = prediction_data.get('timeframe', '24h')
        
        # Couleur basée sur direction
        if direction == 'Bullish':
            color = 'success'
            icon = 'fas fa-chart-line'
        elif direction == 'Bearish':
            color = 'danger'
            icon = 'fas fa-chart-line-down' 
        else:
            color = 'info'
            icon = 'fas fa-exchange-alt'
            
        return dbc.Card([
            dbc.CardHeader([
                html.I(className=f"{icon} me-2"),
                html.Strong(f"Price Prediction ({timeframe})"),
                dbc.Badge(f"{confidence}%", color="light", className="ms-2")
            ]),
            dbc.CardBody([
                html.H4([
                    f"${target_price:,.4f}",
                    html.Small(f" ({change_percent:+.1f}%)", 
                             className=f"text-{color} ms-2")
                ], className="mb-2"),
                html.P(f"Direction: {direction}", className="mb-0")
            ])
        ], className="mb-3")
    
    def create_risk_assessment_card(self, risk_data: Dict[str, Any]) -> dbc.Card:
        """Carte d'évaluation des risques"""
        
        risk_level = risk_data.get('risk_level', 'Medium')
        risk_score = risk_data.get('risk_score', 50)
        description = risk_data.get('description', 'Analyse en cours...')
        recommendation = risk_data.get('recommendation', 'Surveiller le marché')
        
        # Couleur basée sur niveau de risque
        if risk_level == 'Low':
            color = 'success'
            icon = 'fas fa-shield-alt'
        elif risk_level == 'High':
            color = 'danger'
            icon = 'fas fa-exclamation-triangle'
        else:
            color = 'warning' 
            icon = 'fas fa-exclamation-circle'
            
        return dbc.Card([
            dbc.CardHeader([
                html.I(className=f"{icon} me-2"),
                html.Strong("Risk Assessment"),
                dbc.Badge(f"{risk_score}/100", color="light", className="ms-2")
            ]),
            dbc.CardBody([
                html.H4(f"{risk_level} Risk", className=f"text-{color} mb-2"),
                html.P(description, className="mb-2"),
                html.Small(recommendation, className="text-muted")
            ])
        ], className="mb-3")
    
    def create_insights_card(self, insights: List[str]) -> dbc.Card:
        """Carte d'insights de trading"""
        
        return dbc.Card([
            dbc.CardHeader([
                html.I(className="fas fa-lightbulb me-2"),
                html.Strong("AI Trading Insights")
            ]),
            dbc.CardBody([
                html.Div([
                    dbc.Alert(
                        insight,
                        color="info",
                        className="mb-2 p-2"
                    ) for insight in insights
                ]) if insights else html.P("Analyse des insights en cours...", 
                                         className="text-muted mb-0")
            ])
        ], className="mb-3")
    
    def create_confidence_gauge(self, sentiment_confidence: float, 
                              prediction_confidence: float) -> go.Figure:
        """Graphique en gauge pour les niveaux de confiance"""
        
        # Moyenne des confidences
        avg_confidence = (sentiment_confidence + prediction_confidence) / 2
        
        fig = go.Figure()
        
        fig.add_trace(go.Indicator(
            mode = "gauge+number+delta",
            value = avg_confidence,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "AI Confidence Level"},
            delta = {'reference': 75},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': self.colors['ai_primary']},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            template="plotly_dark",
            height=250,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        return fig
    
    def create_sentiment_pie_chart(self, sentiment_data: Dict[str, Any]) -> go.Figure:
        """Graphique en secteurs pour sentiment"""
        
        sentiment = sentiment_data.get('sentiment', 'Neutral')
        confidence = sentiment_data.get('confidence', 50)
        
        # Répartition basée sur sentiment et confiance
        if sentiment == 'Bullish':
            values = [confidence, 100-confidence]
            labels = ['Bullish', 'Uncertainty']
            colors = [self.colors['bullish'], '#374151']
        elif sentiment == 'Bearish':
            values = [confidence, 100-confidence]
            labels = ['Bearish', 'Uncertainty'] 
            colors = [self.colors['bearish'], '#374151']
        else:
            values = [confidence, 100-confidence]
            labels = ['Neutral', 'Uncertainty']
            colors = [self.colors['neutral'], '#374151']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.3,
            marker_colors=colors
        )])
        
        fig.update_layout(
            title="Market Sentiment Distribution",
            template="plotly_dark",
            height=300,
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False
        )
        
        return fig
    
    def create_ai_dashboard_layout(self, analysis_data: Dict[str, Any]) -> html.Div:
        """Layout complet du dashboard IA"""
        
        sentiment = analysis_data.get('sentiment', {})
        prediction = analysis_data.get('prediction', {})
        risk = analysis_data.get('risk_assessment', {})
        insights = analysis_data.get('insights', [])
        ai_status = analysis_data.get('ai_status', 'simulation_mode')
        
        return html.Div([
            
            # Header avec statut IA
            dbc.Row([
                dbc.Col([
                    self.create_ai_status_card(ai_status)
                ], width=12)
            ]),
            
            # Cartes principales d'analyse
            dbc.Row([
                dbc.Col([
                    self.create_sentiment_card(sentiment)
                ], width=4),
                dbc.Col([
                    self.create_prediction_card(prediction)
                ], width=4),
                dbc.Col([
                    self.create_risk_assessment_card(risk)
                ], width=4)
            ]),
            
            # Insights et graphiques
            dbc.Row([
                dbc.Col([
                    self.create_insights_card(insights)
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-pie me-2"),
                            html.Strong("Sentiment Analysis")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=self.create_sentiment_pie_chart(sentiment),
                                style={'height': '300px'}
                            )
                        ])
                    ])
                ], width=6)
            ], className="mt-3"),
            
            # Gauge de confiance
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-tachometer-alt me-2"),
                            html.Strong("AI Analysis Confidence")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=self.create_confidence_gauge(
                                    sentiment.get('confidence', 50),
                                    prediction.get('confidence', 50)
                                ),
                                style={'height': '250px'}
                            )
                        ])
                    ])
                ], width=12)
            ], className="mt-3")
            
        ])


# Instance globale
ai_components = AIDashboardComponents()