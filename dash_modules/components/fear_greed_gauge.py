"""
Component Fear & Greed Gauge - Phase 4 THEBOT
Intégration index Fear & Greed avec API gratuite
Alertes et analyse de sentiment crypto
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class FearGreedGaugeComponent:
    """Composant d'analyse Fear & Greed Index"""
    
    def __init__(self):
        self.api_url = "https://api.alternative.me/fng/"
        self.cache_duration = 300  # 5 minutes pour Fear & Greed
        self.last_update = {}
        self.cache = {}
        
        # Niveaux d'alerte
        self.alert_levels = {
            'extreme_fear': (0, 25),
            'fear': (25, 45),
            'neutral': (45, 55),
            'greed': (55, 75),
            'extreme_greed': (75, 100)
        }
        
    def get_fear_greed_index(self) -> Dict:
        """Récupère l'index Fear & Greed actuel"""
        try:
            cache_key = "current_fear_greed"
            now = datetime.now()
            
            if (cache_key in self.last_update and 
                (now - self.last_update[cache_key]).seconds < self.cache_duration):
                return self.cache.get(cache_key, {})
            
            # Requête API Fear & Greed
            response = requests.get(self.api_url, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"❌ Erreur API Fear & Greed: {response.status_code}")
                return {}
            
            data = response.json()
            
            if not data.get('data'):
                return {}
            
            current_data = data['data'][0]
            
            result = {
                'value': int(current_data.get('value', 0)),
                'value_classification': current_data.get('value_classification', 'Unknown'),
                'timestamp': current_data.get('timestamp', ''),
                'time_until_update': current_data.get('time_until_update', ''),
                'level': self._classify_level(int(current_data.get('value', 0))),
                'sentiment': self._analyze_sentiment(int(current_data.get('value', 0))),
                'recommendation': self._get_recommendation(int(current_data.get('value', 0)))
            }
            
            self.cache[cache_key] = result
            self.last_update[cache_key] = now
            
            logger.info(f"✅ Fear & Greed Index: {result['value']} ({result['value_classification']})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération Fear & Greed Index: {e}")
            return {}
    
    def get_historical_data(self, days: int = 30) -> List[Dict]:
        """Récupère l'historique Fear & Greed"""
        try:
            cache_key = f"historical_fear_greed_{days}"
            now = datetime.now()
            
            if (cache_key in self.last_update and 
                (now - self.last_update[cache_key]).seconds < self.cache_duration):
                return self.cache.get(cache_key, [])
            
            # Requête historique
            url = f"{self.api_url}?limit={days}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"❌ Erreur API Fear & Greed historique: {response.status_code}")
                return []
            
            data = response.json()
            
            if not data.get('data'):
                return []
            
            historical = []
            for entry in data['data']:
                processed_entry = {
                    'value': int(entry.get('value', 0)),
                    'value_classification': entry.get('value_classification', 'Unknown'),
                    'timestamp': entry.get('timestamp', ''),
                    'date': datetime.fromtimestamp(int(entry.get('timestamp', 0))).strftime('%Y-%m-%d'),
                    'level': self._classify_level(int(entry.get('value', 0)))
                }
                historical.append(processed_entry)
            
            # Trier par date (plus récent en premier)
            historical.sort(key=lambda x: int(x['timestamp']), reverse=True)
            
            self.cache[cache_key] = historical
            self.last_update[cache_key] = now
            
            logger.info(f"✅ Historique Fear & Greed: {len(historical)} entrées")
            return historical
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération historique Fear & Greed: {e}")
            return []
    
    def analyze_trends(self, historical_data: List[Dict] = None) -> Dict:
        """Analyse les tendances Fear & Greed"""
        try:
            if not historical_data:
                historical_data = self.get_historical_data(30)
            
            if len(historical_data) < 7:
                return {}
            
            # Prendre les derniers points pour l'analyse
            recent_values = [entry['value'] for entry in historical_data[:7]]  # 7 derniers jours
            older_values = [entry['value'] for entry in historical_data[7:14]] if len(historical_data) >= 14 else []
            
            current_avg = np.mean(recent_values)
            previous_avg = np.mean(older_values) if older_values else current_avg
            
            # Calculer la tendance
            trend_direction = "up" if current_avg > previous_avg else "down" if current_avg < previous_avg else "stable"
            trend_strength = abs(current_avg - previous_avg)
            
            # Volatilité
            volatility = np.std(recent_values)
            
            # Durée dans la zone actuelle
            current_level = self._classify_level(recent_values[0])
            zone_duration = 1
            for i in range(1, len(recent_values)):
                if self._classify_level(recent_values[i]) == current_level:
                    zone_duration += 1
                else:
                    break
            
            analysis = {
                'current_average': current_avg,
                'previous_average': previous_avg,
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'volatility': volatility,
                'zone_duration': zone_duration,
                'current_level': current_level,
                'extremes': {
                    'max_7d': max(recent_values),
                    'min_7d': min(recent_values),
                    'max_30d': max([entry['value'] for entry in historical_data]),
                    'min_30d': min([entry['value'] for entry in historical_data])
                },
                'signal': self._generate_trend_signal(trend_direction, trend_strength, current_avg, zone_duration)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse tendances: {e}")
            return {}
    
    def setup_alerts(self, current_value: int) -> List[Dict]:
        """Configure les alertes basées sur Fear & Greed"""
        alerts = []
        
        try:
            level = self._classify_level(current_value)
            
            # Alertes basées sur les niveaux
            if level == 'extreme_fear':
                alerts.append({
                    'type': 'opportunity',
                    'level': 'high',
                    'message': '🟢 OPPORTUNITÉ: Peur extrême détectée - Potentiel d\'achat',
                    'action': 'Consider buying opportunities',
                    'confidence': 85
                })
            
            elif level == 'extreme_greed':
                alerts.append({
                    'type': 'warning',
                    'level': 'high',
                    'message': '🔴 ATTENTION: Cupidité extrême - Risque de correction',
                    'action': 'Consider taking profits',
                    'confidence': 80
                })
            
            elif level == 'fear':
                alerts.append({
                    'type': 'opportunity',
                    'level': 'medium',
                    'message': '🟡 SURVEILLANCE: Zone de peur - Surveiller opportunités',
                    'action': 'Monitor for entry points',
                    'confidence': 65
                })
            
            elif level == 'greed':
                alerts.append({
                    'type': 'caution',
                    'level': 'medium',
                    'message': '🟡 PRUDENCE: Zone de cupidité - Attention aux risques',
                    'action': 'Be cautious with new positions',
                    'confidence': 60
                })
            
            # Alertes de transition
            historical = self.get_historical_data(7)
            if len(historical) >= 3:
                recent_levels = [self._classify_level(entry['value']) for entry in historical[:3]]
                
                if recent_levels[0] != recent_levels[1]:  # Changement de niveau
                    alerts.append({
                        'type': 'transition',
                        'level': 'medium',
                        'message': f'🔄 TRANSITION: Passage de {recent_levels[1]} à {recent_levels[0]}',
                        'action': 'Monitor trend continuation',
                        'confidence': 70
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration alertes: {e}")
            return []
    
    def create_gauge_widget(self, widget_id: str = "fear-greed-gauge") -> html.Div:
        """Crée le widget Fear & Greed Gauge"""
        return html.Div([
            html.H3("😨 Fear & Greed Index", className="widget-title"),
            
            # Contrôles
            html.Div([
                html.Label("Période historique:", className="control-label"),
                dcc.Dropdown(
                    id=f"{widget_id}-period",
                    options=[
                        {'label': '7 jours', 'value': 7},
                        {'label': '14 jours', 'value': 14},
                        {'label': '30 jours', 'value': 30},
                        {'label': '60 jours', 'value': 60}
                    ],
                    value=30,
                    className="control-dropdown"
                ),
                html.Label("Alertes actives:", className="control-label"),
                dcc.Checklist(
                    id=f"{widget_id}-alerts",
                    options=[
                        {'label': 'Extrêmes', 'value': 'extremes'},
                        {'label': 'Transitions', 'value': 'transitions'},
                        {'label': 'Opportunités', 'value': 'opportunities'}
                    ],
                    value=['extremes', 'opportunities'],
                    className="control-checklist"
                )
            ], className="widget-controls"),
            
            # Jauge principale
            html.Div([
                dcc.Graph(id=f"{widget_id}-gauge"),
                dcc.Graph(id=f"{widget_id}-historical-chart")
            ], className="widget-charts"),
            
            # Analyse et tendances
            html.Div(id=f"{widget_id}-analysis", className="widget-analysis"),
            
            # Alertes
            html.Div(id=f"{widget_id}-alerts-panel", className="widget-alerts"),
            
            # Auto-refresh
            dcc.Interval(
                id=f"{widget_id}-interval",
                interval=5*60*1000,  # 5 minutes
                n_intervals=0
            )
            
        ], className="fear-greed-gauge-widget dashboard-widget")
    
    def _classify_level(self, value: int) -> str:
        """Classifie le niveau basé sur la valeur"""
        for level, (min_val, max_val) in self.alert_levels.items():
            if min_val <= value < max_val:
                return level
        return 'extreme_greed' if value >= 75 else 'extreme_fear'
    
    def _analyze_sentiment(self, value: int) -> Dict:
        """Analyse le sentiment basé sur la valeur"""
        level = self._classify_level(value)
        
        sentiment_map = {
            'extreme_fear': {'emoji': '😱', 'description': 'Panique totale', 'market_state': 'Oversold'},
            'fear': {'emoji': '😰', 'description': 'Inquiétude', 'market_state': 'Bearish'},
            'neutral': {'emoji': '😐', 'description': 'Équilibre', 'market_state': 'Balanced'},
            'greed': {'emoji': '😊', 'description': 'Optimisme', 'market_state': 'Bullish'},
            'extreme_greed': {'emoji': '🤑', 'description': 'Euphorie', 'market_state': 'Overbought'}
        }
        
        return sentiment_map.get(level, {'emoji': '❓', 'description': 'Inconnu', 'market_state': 'Unknown'})
    
    def _get_recommendation(self, value: int) -> Dict:
        """Génère des recommandations basées sur l'index"""
        level = self._classify_level(value)
        
        recommendations = {
            'extreme_fear': {
                'action': 'BUY OPPORTUNITY',
                'description': 'Excellente opportunité d\'achat - Marché en panique',
                'risk': 'Medium',
                'timeframe': 'Medium-term'
            },
            'fear': {
                'action': 'ACCUMULATE',
                'description': 'Bon moment pour accumuler progressivement',
                'risk': 'Medium-Low',
                'timeframe': 'Short to Medium-term'
            },
            'neutral': {
                'action': 'HOLD',
                'description': 'Maintenir positions actuelles et surveiller',
                'risk': 'Balanced',
                'timeframe': 'Wait for signals'
            },
            'greed': {
                'action': 'CAUTION',
                'description': 'Prudence recommandée - Éviter FOMO',
                'risk': 'Medium-High',
                'timeframe': 'Short-term caution'
            },
            'extreme_greed': {
                'action': 'TAKE PROFITS',
                'description': 'Prendre des bénéfices - Marché surchauffé',
                'risk': 'High',
                'timeframe': 'Immediate'
            }
        }
        
        return recommendations.get(level, {})
    
    def _generate_trend_signal(self, direction: str, strength: float, current_avg: float, zone_duration: int) -> Dict:
        """Génère un signal basé sur l'analyse de tendance"""
        signal_strength = "weak"
        
        if strength > 10:
            signal_strength = "strong"
        elif strength > 5:
            signal_strength = "medium"
        
        # Signal composite
        if direction == "down" and current_avg < 30 and zone_duration >= 3:
            signal = "STRONG_BUY_SIGNAL"
        elif direction == "up" and current_avg > 70 and zone_duration >= 3:
            signal = "STRONG_SELL_SIGNAL"
        elif direction == "down" and current_avg < 45:
            signal = "BUY_SIGNAL"
        elif direction == "up" and current_avg > 55:
            signal = "SELL_SIGNAL"
        else:
            signal = "NEUTRAL"
        
        return {
            'signal': signal,
            'strength': signal_strength,
            'confidence': min(95, 50 + strength * 2 + zone_duration * 5)
        }


# Instance globale
fear_greed_gauge = FearGreedGaugeComponent()


# Callbacks pour le widget
@callback(
    [Output('fear-greed-gauge-gauge', 'figure'),
     Output('fear-greed-gauge-historical-chart', 'figure'),
     Output('fear-greed-gauge-analysis', 'children'),
     Output('fear-greed-gauge-alerts-panel', 'children')],
    [Input('fear-greed-gauge-period', 'value'),
     Input('fear-greed-gauge-alerts', 'value'),
     Input('fear-greed-gauge-interval', 'n_intervals')]
)
def update_fear_greed_gauge(period, alert_types, n_intervals):
    """Met à jour le widget Fear & Greed Gauge"""
    try:
        # Récupérer données actuelles et historiques
        current_data = fear_greed_gauge.get_fear_greed_index()
        historical_data = fear_greed_gauge.get_historical_data(period)
        
        # Jauge principale
        gauge_fig = go.Figure()
        
        if current_data:
            value = current_data['value']
            
            gauge_fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Fear & Greed Index<br>{current_data.get('value_classification', '')}"},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 25], 'color': "red"},
                        {'range': [25, 45], 'color': "orange"},
                        {'range': [45, 55], 'color': "yellow"},
                        {'range': [55, 75], 'color': "lightgreen"},
                        {'range': [75, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': value
                    }
                }
            ))
        
        gauge_fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
        
        # Graphique historique
        hist_fig = go.Figure()
        
        if historical_data:
            dates = [entry['date'] for entry in historical_data[::-1]]  # Inverser pour chronologique
            values = [entry['value'] for entry in historical_data[::-1]]
            
            hist_fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                name='Fear & Greed Index',
                line=dict(color='blue', width=2),
                marker=dict(size=6)
            ))
            
            # Ajouter zones colorées
            hist_fig.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="Extreme Fear")
            hist_fig.add_hline(y=75, line_dash="dash", line_color="green", annotation_text="Extreme Greed")
            hist_fig.add_hrect(y0=0, y1=25, fillcolor="red", opacity=0.1)
            hist_fig.add_hrect(y0=75, y1=100, fillcolor="green", opacity=0.1)
        
        hist_fig.update_layout(
            title=f"Fear & Greed Index - Last {period} Days",
            xaxis_title="Date",
            yaxis_title="Index Value",
            height=300,
            yaxis=dict(range=[0, 100])
        )
        
        # Analyse des tendances
        analysis_content = []
        if current_data and historical_data:
            trends = fear_greed_gauge.analyze_trends(historical_data)
            sentiment = current_data.get('sentiment', {})
            recommendation = current_data.get('recommendation', {})
            
            analysis_content = [
                html.Div([
                    html.H4("📊 Analyse Actuelle"),
                    html.P(f"Valeur: {current_data['value']}/100"),
                    html.P(f"Niveau: {current_data.get('level', 'Unknown').replace('_', ' ').title()}"),
                    html.P(f"Sentiment: {sentiment.get('emoji', '')} {sentiment.get('description', '')}"),
                    html.P(f"État marché: {sentiment.get('market_state', 'Unknown')}")
                ], className="analysis-current"),
                
                html.Div([
                    html.H4("📈 Tendances"),
                    html.P(f"Direction: {trends.get('trend_direction', 'Unknown').title()}"),
                    html.P(f"Force: {trends.get('trend_strength', 0):.1f}"),
                    html.P(f"Volatilité: {trends.get('volatility', 0):.1f}"),
                    html.P(f"Durée zone: {trends.get('zone_duration', 0)} jours")
                ], className="analysis-trends") if trends else html.Div(),
                
                html.Div([
                    html.H4("💡 Recommandation"),
                    html.P(f"Action: {recommendation.get('action', 'N/A')}"),
                    html.P(f"Description: {recommendation.get('description', 'N/A')}"),
                    html.P(f"Risque: {recommendation.get('risk', 'N/A')}"),
                    html.P(f"Horizon: {recommendation.get('timeframe', 'N/A')}")
                ], className="analysis-recommendation")
            ]
        
        # Alertes
        alerts_content = []
        if current_data and alert_types:
            alerts = fear_greed_gauge.setup_alerts(current_data['value'])
            
            for alert in alerts:
                if alert['type'] in ['opportunity'] and 'opportunities' in alert_types:
                    alert_class = f"alert-{alert['level']}"
                elif alert['type'] in ['warning', 'caution'] and 'extremes' in alert_types:
                    alert_class = f"alert-{alert['level']}"
                elif alert['type'] == 'transition' and 'transitions' in alert_types:
                    alert_class = "alert-info"
                else:
                    continue
                
                alert_div = html.Div([
                    html.P(alert['message'], className="alert-message"),
                    html.P(f"Action: {alert['action']}", className="alert-action"),
                    html.P(f"Confiance: {alert['confidence']}%", className="alert-confidence")
                ], className=f"alert-item {alert_class}")
                
                alerts_content.append(alert_div)
        
        if not alerts_content:
            alerts_content = [html.P("Aucune alerte active", className="no-alerts")]
        
        return gauge_fig, hist_fig, analysis_content, alerts_content
        
    except Exception as e:
        logger.error(f"❌ Erreur callback Fear & Greed Gauge: {e}")
        
        # Retourner vides en cas d'erreur
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Données non disponibles")
        
        error_content = [html.P(f"Erreur: {str(e)}", className="error-message")]
        
        return empty_fig, empty_fig, error_content, error_content