"""
Component Top Performers - Phase 4 THEBOT
Tracking des meilleures et pires performances crypto
Analyse multi-timeframes et corrélations
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Import des providers THEBOT
from ..data_providers.binance_api import binance_provider
from ..data_providers.coin_gecko_api import coin_gecko_api

logger = logging.getLogger(__name__)


class TopPerformersComponent:
    """Composant de tracking des top performers crypto"""
    
    def __init__(self):
        self.cache_duration = 60  # 1 minute
        self.last_update = {}
        self.cache = {}
        
    def get_top_gainers(self, limit: int = 10) -> List[Dict]:
        """Récupère les meilleures performances 24h"""
        try:
            cache_key = f"top_gainers_{limit}"
            now = datetime.now()
            
            if (cache_key in self.last_update and 
                (now - self.last_update[cache_key]).seconds < self.cache_duration):
                return self.cache.get(cache_key, [])
            
            # Utiliser la méthode Binance
            gainers_losers = binance_provider.get_gainers_losers(limit)
            gainers = gainers_losers.get('gainers', [])
            
            # Enrichir les données
            enriched_gainers = []
            for gainer in gainers:
                enriched = {
                    'symbol': gainer['symbol'],
                    'price': gainer['price'],
                    'change_percent': gainer['change_percent'],
                    'volume': gainer['volume'],
                    'performance_score': self._calculate_performance_score(gainer),
                    'risk_level': self._assess_risk_level(gainer),
                    'momentum_strength': self._analyze_momentum(gainer)
                }
                enriched_gainers.append(enriched)
            
            self.cache[cache_key] = enriched_gainers
            self.last_update[cache_key] = now
            
            logger.info(f"✅ {len(enriched_gainers)} top gainers récupérés")
            return enriched_gainers
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération top gainers: {e}")
            return []
    
    def get_top_losers(self, limit: int = 10) -> List[Dict]:
        """Récupère les pires performances 24h"""
        try:
            cache_key = f"top_losers_{limit}"
            now = datetime.now()
            
            if (cache_key in self.last_update and 
                (now - self.last_update[cache_key]).seconds < self.cache_duration):
                return self.cache.get(cache_key, [])
            
            # Utiliser la méthode Binance
            gainers_losers = binance_provider.get_gainers_losers(limit)
            losers = gainers_losers.get('losers', [])
            
            # Enrichir les données
            enriched_losers = []
            for loser in losers:
                enriched = {
                    'symbol': loser['symbol'],
                    'price': loser['price'],
                    'change_percent': loser['change_percent'],
                    'volume': loser['volume'],
                    'support_level': self._find_support_level(loser),
                    'recovery_potential': self._assess_recovery_potential(loser),
                    'risk_level': self._assess_risk_level(loser)
                }
                enriched_losers.append(enriched)
            
            self.cache[cache_key] = enriched_losers
            self.last_update[cache_key] = now
            
            logger.info(f"✅ {len(enriched_losers)} top losers récupérés")
            return enriched_losers
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération top losers: {e}")
            return []
    
    def calculate_correlations(self, symbols: List[str] = None) -> Dict:
        """Calcule les corrélations entre cryptos populaires"""
        try:
            cache_key = f"correlations_{'_'.join(symbols) if symbols else 'default'}"
            now = datetime.now()
            
            if (cache_key in self.last_update and 
                (now - self.last_update[cache_key]).seconds < self.cache_duration):
                return self.cache.get(cache_key, {})
            
            # Symboles par défaut si non spécifiés
            if not symbols:
                symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT']
            
            # Récupérer données 24h pour chaque symbole
            correlations_data = {}
            price_changes = {}
            
            for symbol in symbols:
                ticker = binance_provider.get_24hr_ticker(symbol)
                if ticker and ticker.get('symbol'):
                    price_changes[symbol] = ticker['priceChangePercent']
                    
                    correlations_data[symbol] = {
                        'price': ticker['price'],
                        'change_24h': ticker['priceChangePercent'],
                        'volume': ticker['quoteVolume'],
                        'volatility': self._calculate_volatility(ticker)
                    }
            
            # Matrice de corrélation simple (pour demo, basée sur les changements 24h)
            correlation_matrix = {}
            for symbol1 in price_changes:
                correlation_matrix[symbol1] = {}
                for symbol2 in price_changes:
                    if symbol1 == symbol2:
                        correlation_matrix[symbol1][symbol2] = 1.0
                    else:
                        # Corrélation approximative basée sur la direction du changement
                        change1 = price_changes[symbol1]
                        change2 = price_changes[symbol2]
                        
                        # Corrélation directionnelle simple
                        if (change1 > 0 and change2 > 0) or (change1 < 0 and change2 < 0):
                            correlation = min(0.9, abs(change1 * change2) / 100)
                        else:
                            correlation = -min(0.9, abs(change1 * change2) / 100)
                        
                        correlation_matrix[symbol1][symbol2] = correlation
            
            result = {
                'correlation_matrix': correlation_matrix,
                'symbols_data': correlations_data,
                'market_leaders': self._identify_market_leaders(correlations_data),
                'diversification_score': self._calculate_diversification_score(correlation_matrix)
            }
            
            self.cache[cache_key] = result
            self.last_update[cache_key] = now
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul corrélations: {e}")
            return {}
    
    def get_performance_ratios(self) -> Dict:
        """Calcule les ratios de performance du marché"""
        try:
            cache_key = "performance_ratios"
            now = datetime.now()
            
            if (cache_key in self.last_update and 
                (now - self.last_update[cache_key]).seconds < self.cache_duration):
                return self.cache.get(cache_key, {})
            
            # Récupérer résumé marché
            market_summary = binance_provider.get_market_summary()
            if not market_summary:
                return {}
            
            gainers = market_summary.get('gainers_count', 0)
            losers = market_summary.get('losers_count', 0)
            total = gainers + losers
            
            ratios = {
                'bull_bear_ratio': gainers / losers if losers > 0 else float('inf'),
                'market_participation': total / market_summary.get('total_pairs', 1),
                'gainer_percentage': (gainers / total * 100) if total > 0 else 0,
                'loser_percentage': (losers / total * 100) if total > 0 else 0,
                'market_momentum': self._calculate_market_momentum(market_summary),
                'volume_concentration': self._calculate_volume_concentration(market_summary),
                'strength_index': self._calculate_strength_index(gainers, losers, total)
            }
            
            # Classification du marché
            ratios['market_condition'] = self._classify_market_condition(ratios)
            
            self.cache[cache_key] = ratios
            self.last_update[cache_key] = now
            
            return ratios
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul ratios performance: {e}")
            return {}
    
    def create_performance_widget(self, widget_id: str = "top-performers") -> html.Div:
        """Crée le widget des top performers"""
        return html.Div([
            html.H3("🏆 Top Performers", className="widget-title"),
            
            # Contrôles
            html.Div([
                html.Label("Mode d'affichage:", className="control-label"),
                dcc.RadioItems(
                    id=f"{widget_id}-mode",
                    options=[
                        {'label': 'Gainers', 'value': 'gainers'},
                        {'label': 'Losers', 'value': 'losers'},
                        {'label': 'Both', 'value': 'both'}
                    ],
                    value='both',
                    className="control-radio"
                ),
                html.Label("Nombre:", className="control-label"),
                dcc.Slider(
                    id=f"{widget_id}-limit",
                    min=5,
                    max=20,
                    step=5,
                    value=10,
                    marks={i: str(i) for i in range(5, 25, 5)},
                    className="control-slider"
                )
            ], className="widget-controls"),
            
            # Graphiques principaux
            html.Div([
                dcc.Graph(id=f"{widget_id}-chart"),
                dcc.Graph(id=f"{widget_id}-correlation-chart")
            ], className="widget-charts"),
            
            # Ratios et métriques
            html.Div(id=f"{widget_id}-ratios", className="widget-ratios"),
            
            # Tableaux
            html.Div(id=f"{widget_id}-tables", className="widget-tables"),
            
            # Auto-refresh
            dcc.Interval(
                id=f"{widget_id}-interval",
                interval=60*1000,  # 1 minute
                n_intervals=0
            )
            
        ], className="top-performers-widget dashboard-widget")
    
    def _calculate_performance_score(self, coin_data: Dict) -> float:
        """Calcule un score de performance global"""
        change = coin_data.get('change_percent', 0)
        volume = coin_data.get('volume', 0)
        
        # Score basé sur changement et volume
        volume_score = min(10, np.log10(volume / 1000000)) if volume > 0 else 0
        change_score = min(10, abs(change) / 2)
        
        return (volume_score + change_score) / 2
    
    def _assess_risk_level(self, coin_data: Dict) -> str:
        """Évalue le niveau de risque"""
        change = abs(coin_data.get('change_percent', 0))
        volume = coin_data.get('volume', 0)
        
        if change > 15 and volume < 5000000:
            return "🔴 High Risk"
        elif change > 10:
            return "🟡 Medium Risk"
        elif change > 5:
            return "🟢 Low Risk"
        else:
            return "⚪ Very Low Risk"
    
    def _analyze_momentum(self, coin_data: Dict) -> str:
        """Analyse la force du momentum"""
        change = coin_data.get('change_percent', 0)
        volume = coin_data.get('volume', 0)
        
        if change > 15 and volume > 10000000:
            return "🚀 Explosive"
        elif change > 10 and volume > 5000000:
            return "💪 Strong"
        elif change > 5:
            return "📈 Moderate"
        else:
            return "➡️ Weak"
    
    def _find_support_level(self, coin_data: Dict) -> str:
        """Identifie des niveaux de support approximatifs"""
        change = coin_data.get('change_percent', 0)
        
        if change < -20:
            return "🔻 Critical Support Needed"
        elif change < -15:
            return "⚠️ Approaching Support"
        elif change < -10:
            return "📉 Support Test"
        else:
            return "✅ Above Support"
    
    def _assess_recovery_potential(self, coin_data: Dict) -> str:
        """Évalue le potentiel de récupération"""
        change = coin_data.get('change_percent', 0)
        volume = coin_data.get('volume', 0)
        
        if change < -15 and volume > 5000000:
            return "🔄 High Recovery Potential"
        elif change < -10 and volume > 2000000:
            return "📈 Medium Recovery Potential"
        elif change < -5:
            return "➡️ Low Recovery Potential"
        else:
            return "❓ Unclear"
    
    def _calculate_volatility(self, ticker: Dict) -> float:
        """Calcule la volatilité approximative"""
        high = ticker.get('high', 0)
        low = ticker.get('low', 0)
        price = ticker.get('price', 0)
        
        if price > 0:
            return ((high - low) / price) * 100
        return 0
    
    def _identify_market_leaders(self, symbols_data: Dict) -> List[str]:
        """Identifie les leaders du marché"""
        leaders = []
        for symbol, data in symbols_data.items():
            if (data['volume'] > 20000000 and 
                abs(data['change_24h']) < 5):  # Stabilité avec volume
                leaders.append(symbol)
        
        return leaders[:3]
    
    def _calculate_diversification_score(self, correlation_matrix: Dict) -> float:
        """Calcule un score de diversification"""
        if not correlation_matrix:
            return 0
        
        correlations = []
        symbols = list(correlation_matrix.keys())
        
        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols):
                if i < j:  # Éviter les doublons
                    corr = correlation_matrix[symbol1].get(symbol2, 0)
                    correlations.append(abs(corr))
        
        if correlations:
            avg_correlation = np.mean(correlations)
            # Score inversé : moins de corrélation = meilleure diversification
            return max(0, 100 - (avg_correlation * 100))
        
        return 0
    
    def _calculate_market_momentum(self, market_summary: Dict) -> float:
        """Calcule le momentum global du marché"""
        gainers = market_summary.get('gainers_count', 0)
        losers = market_summary.get('losers_count', 0)
        total = gainers + losers
        
        if total > 0:
            return (gainers - losers) / total * 100
        return 0
    
    def _calculate_volume_concentration(self, market_summary: Dict) -> float:
        """Calcule la concentration du volume"""
        top_volume = market_summary.get('top_volume_pairs', [])
        if len(top_volume) >= 5:
            total_top5 = sum(pair.get('volume', 0) for pair in top_volume[:5])
            total_market = market_summary.get('total_volume_usdt', 0)
            
            if total_market > 0:
                return (total_top5 / total_market) * 100
        
        return 0
    
    def _calculate_strength_index(self, gainers: int, losers: int, total: int) -> float:
        """Calcule un index de force du marché"""
        if total == 0:
            return 50
        
        # Index de 0 à 100
        ratio = gainers / total
        return ratio * 100
    
    def _classify_market_condition(self, ratios: Dict) -> str:
        """Classifie les conditions du marché"""
        strength = ratios.get('strength_index', 50)
        momentum = ratios.get('market_momentum', 0)
        
        if strength > 70 and momentum > 20:
            return "🚀 Strong Bull Market"
        elif strength > 60 and momentum > 10:
            return "📈 Bull Market"
        elif strength < 30 and momentum < -20:
            return "📉 Strong Bear Market"
        elif strength < 40 and momentum < -10:
            return "🔻 Bear Market"
        else:
            return "😐 Sideways Market"


# Instance globale
top_performers = TopPerformersComponent()


# Callbacks pour le widget
@callback(
    [Output('top-performers-chart', 'figure'),
     Output('top-performers-correlation-chart', 'figure'),
     Output('top-performers-ratios', 'children'),
     Output('top-performers-tables', 'children')],
    [Input('top-performers-mode', 'value'),
     Input('top-performers-limit', 'value'),
     Input('top-performers-interval', 'n_intervals')]
)
def update_top_performers(mode, limit, n_intervals):
    """Met à jour le widget top performers"""
    try:
        # Récupérer données selon le mode
        gainers = []
        losers = []
        
        if mode in ['gainers', 'both']:
            gainers = top_performers.get_top_gainers(limit)
        
        if mode in ['losers', 'both']:
            losers = top_performers.get_top_losers(limit)
        
        # Récupérer corrélations et ratios
        correlations = top_performers.calculate_correlations()
        ratios = top_performers.get_performance_ratios()
        
        # Graphique principal
        main_fig = go.Figure()
        
        if gainers and mode in ['gainers', 'both']:
            symbols = [g['symbol'].replace('USDT', '') for g in gainers]
            changes = [g['change_percent'] for g in gainers]
            
            main_fig.add_trace(go.Bar(
                x=symbols,
                y=changes,
                name="Top Gainers",
                marker_color='green',
                text=[f"+{change:.1f}%" for change in changes],
                textposition='outside'
            ))
        
        if losers and mode in ['losers', 'both']:
            symbols = [l['symbol'].replace('USDT', '') for l in losers]
            changes = [l['change_percent'] for l in losers]
            
            main_fig.add_trace(go.Bar(
                x=symbols,
                y=changes,
                name="Top Losers",
                marker_color='red',
                text=[f"{change:.1f}%" for change in changes],
                textposition='outside'
            ))
        
        main_fig.update_layout(
            title=f"Top Performers - {mode.title()}",
            xaxis_title="Crypto",
            yaxis_title="Change 24h (%)",
            height=400
        )
        
        # Graphique de corrélation
        corr_fig = go.Figure()
        
        if correlations and correlations.get('correlation_matrix'):
            matrix = correlations['correlation_matrix']
            symbols = list(matrix.keys())
            
            # Créer la matrice pour le heatmap
            z_matrix = []
            for symbol1 in symbols:
                row = []
                for symbol2 in symbols:
                    row.append(matrix[symbol1].get(symbol2, 0))
                z_matrix.append(row)
            
            corr_fig.add_trace(go.Heatmap(
                z=z_matrix,
                x=[s.replace('USDT', '') for s in symbols],
                y=[s.replace('USDT', '') for s in symbols],
                colorscale='RdBu',
                zmid=0
            ))
        
        corr_fig.update_layout(
            title="Correlation Matrix",
            height=400
        )
        
        # Ratios et métriques
        ratios_content = []
        if ratios:
            ratios_content = [
                html.Div([
                    html.H4("📊 Market Ratios"),
                    html.P(f"Market Condition: {ratios.get('market_condition', 'Unknown')}"),
                    html.P(f"Bull/Bear Ratio: {ratios.get('bull_bear_ratio', 0):.2f}"),
                    html.P(f"Strength Index: {ratios.get('strength_index', 0):.1f}%"),
                    html.P(f"Market Momentum: {ratios.get('market_momentum', 0):.1f}%"),
                    html.P(f"Gainer %: {ratios.get('gainer_percentage', 0):.1f}%"),
                    html.P(f"Loser %: {ratios.get('loser_percentage', 0):.1f}%")
                ], className="ratios-panel")
            ]
        
        # Tableaux
        tables_content = []
        
        if gainers and mode in ['gainers', 'both']:
            gainer_table = [
                html.H4("🏆 Top Gainers"),
                html.Table([
                    html.Tr([
                        html.Th("Symbol"),
                        html.Th("Price"),
                        html.Th("Change %"),
                        html.Th("Volume"),
                        html.Th("Risk")
                    ])
                ] + [
                    html.Tr([
                        html.Td(g['symbol'].replace('USDT', '')),
                        html.Td(f"${g['price']:.4f}"),
                        html.Td(f"+{g['change_percent']:.2f}%", style={'color': 'green'}),
                        html.Td(f"${g['volume']:,.0f}"),
                        html.Td(g['risk_level'])
                    ]) for g in gainers[:5]
                ], className="performance-table")
            ]
            tables_content.extend(gainer_table)
        
        if losers and mode in ['losers', 'both']:
            loser_table = [
                html.H4("📉 Top Losers"),
                html.Table([
                    html.Tr([
                        html.Th("Symbol"),
                        html.Th("Price"),
                        html.Th("Change %"),
                        html.Th("Volume"),
                        html.Th("Recovery")
                    ])
                ] + [
                    html.Tr([
                        html.Td(l['symbol'].replace('USDT', '')),
                        html.Td(f"${l['price']:.4f}"),
                        html.Td(f"{l['change_percent']:.2f}%", style={'color': 'red'}),
                        html.Td(f"${l['volume']:,.0f}"),
                        html.Td(l['recovery_potential'])
                    ]) for l in losers[:5]
                ], className="performance-table")
            ]
            tables_content.extend(loser_table)
        
        return main_fig, corr_fig, ratios_content, tables_content
        
    except Exception as e:
        logger.error(f"❌ Erreur callback top performers: {e}")
        
        # Retourner vides en cas d'erreur
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Données non disponibles")
        
        return empty_fig, empty_fig, html.Div("Erreur"), html.Div()