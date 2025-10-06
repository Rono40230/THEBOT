"""
Visualiseur pour l'indicateur MACD
Module ultra-modulaire - Responsabilité unique : Visualisation MACD
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Optional, List, Tuple
import logging

from .config import MACDConfig

logger = logging.getLogger(__name__)


class VisualizationError(Exception):
    """Erreur de visualisation"""
    pass


class MACDPlotter:
    """Visualiseur professionnel pour MACD"""
    
    def __init__(self, config: MACDConfig):
        """
        Initialise le visualiseur.
        
        Args:
            config: Configuration MACD validée
        """
        self.config = config
    
    def create_subplot_figure(self, macd_data: Dict[str, pd.Series], 
                             signals: Optional[pd.DataFrame] = None,
                             title: str = "MACD") -> go.Figure:
        """
        Crée un graphique MACD complet dans un subplot.
        
        Args:
            macd_data: Données MACD (macd, signal, histogram)
            signals: Signaux optionnels
            title: Titre du graphique
            
        Returns:
            Figure Plotly complète
            
        Raises:
            VisualizationError: Si création échoue
        """
        try:
            fig = go.Figure()
            
            # Histogramme (en arrière-plan)
            if self.config.histogram_enabled and 'histogram' in macd_data:
                self._add_histogram(fig, macd_data['histogram'])
            
            # Ligne zéro
            if getattr(self.config, 'zero_line_enabled', True):
                self._add_zero_line(fig)
            
            # Lignes MACD et Signal
            self._add_macd_lines(fig, macd_data)
            
            # Signaux de crossover
            if signals is not None and getattr(self.config, 'crossover_signals', True):
                self._add_crossover_signals(fig, macd_data, signals)
            
            # Configuration layout
            self._configure_layout(fig, title)
            
            logger.debug(f"Graphique MACD créé: {title}")
            return fig
            
        except Exception as e:
            raise VisualizationError(f"Erreur création graphique MACD: {str(e)}") from e
    
    def _add_histogram(self, fig: go.Figure, histogram: pd.Series):
        """Ajoute l'histogramme MACD"""
        # Couleurs selon signe
        colors = [
            self.config.histogram_positive_color if x >= 0 
            else self.config.histogram_negative_color 
            for x in histogram
        ]
        
        fig.add_trace(go.Bar(
            x=histogram.index,
            y=histogram,
            name='Histogramme',
            marker_color=colors,
            opacity=0.6,
            showlegend=False,
            hovertemplate='<b>Histogramme</b>: %{y:.4f}<br>' +
                         '<b>Date</b>: %{x}<br>' +
                         '<b>Force</b>: %{customdata}<br>' +
                         '<extra></extra>',
            customdata=[
                'Momentum haussier' if x > 0 else 'Momentum baissier' 
                for x in histogram
            ]
        ))
    
    def _add_zero_line(self, fig: go.Figure):
        """Ajoute la ligne zéro de référence"""
        fig.add_hline(
            y=0,
            line=dict(color='white', dash='dot', width=1),
            annotation_text="Ligne zéro",
            annotation_position="top right"
        )
    
    def _add_macd_lines(self, fig: go.Figure, macd_data: Dict[str, pd.Series]):
        """Ajoute les lignes MACD et Signal"""
        # Ligne MACD principale
        fig.add_trace(go.Scatter(
            x=macd_data['macd'].index,
            y=macd_data['macd'],
            mode='lines',
            name='MACD',
            line=dict(
                color=self.config.macd_color,
                width=self.config.line_width
            ),
            showlegend=True,
            hovertemplate='<b>MACD</b>: %{y:.4f}<br>' +
                         '<b>Date</b>: %{x}<br>' +
                         f'<b>Config</b>: EMA({self.config.fast_period}) - EMA({self.config.slow_period})<br>' +
                         '<extra></extra>'
        ))
        
        # Ligne Signal
        fig.add_trace(go.Scatter(
            x=macd_data['signal'].index,
            y=macd_data['signal'],
            mode='lines',
            name='Signal',
            line=dict(
                color=self.config.signal_color,
                width=self.config.line_width
            ),
            showlegend=True,
            hovertemplate='<b>Signal</b>: %{y:.4f}<br>' +
                         '<b>Date</b>: %{x}<br>' +
                         f'<b>Config</b>: EMA({self.config.signal_period}) du MACD<br>' +
                         '<extra></extra>'
        ))
    
    def _add_crossover_signals(self, fig: go.Figure, macd_data: Dict[str, pd.Series], 
                              signals: pd.DataFrame):
        """Ajoute les marqueurs de signaux de crossover"""
        buy_signals = signals[signals['signal_type'] == 'buy']
        sell_signals = signals[signals['signal_type'] == 'sell']
        
        # Signaux d'achat
        if not buy_signals.empty:
            fig.add_trace(go.Scatter(
                x=buy_signals.index,
                y=[macd_data['macd'].loc[idx] for idx in buy_signals.index],
                mode='markers',
                name='Signal Achat',
                marker=dict(
                    size=10,
                    color='lime',
                    symbol='triangle-up',
                    line=dict(width=2, color='darkgreen')
                ),
                showlegend=True,
                hovertemplate='<b>Signal ACHAT</b><br>' +
                             'Date: %{x}<br>' +
                             'MACD: %{y:.4f}<br>' +
                             '📈 MACD croise au-dessus Signal<br>' +
                             '<extra></extra>'
            ))
        
        # Signaux de vente
        if not sell_signals.empty:
            fig.add_trace(go.Scatter(
                x=sell_signals.index,
                y=[macd_data['macd'].loc[idx] for idx in sell_signals.index],
                mode='markers',
                name='Signal Vente',
                marker=dict(
                    size=10,
                    color='red',
                    symbol='triangle-down',
                    line=dict(width=2, color='darkred')
                ),
                showlegend=True,
                hovertemplate='<b>Signal VENTE</b><br>' +
                             'Date: %{x}<br>' +
                             'MACD: %{y:.4f}<br>' +
                             '📉 MACD croise en-dessous Signal<br>' +
                             '<extra></extra>'
            ))
    
    def _configure_layout(self, fig: go.Figure, title: str):
        """Configure le layout du graphique"""
        fig.update_layout(
            title=title,
            template='plotly_dark',
            height=250,
            margin=dict(l=40, r=40, t=40, b=40),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                title="",
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            yaxis=dict(
                title="MACD",
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)',
                zeroline=True,
                zerolinecolor='white',
                zerolinewidth=1
            )
        )
    
    def get_visual_config(self) -> Dict[str, any]:
        """Retourne la configuration visuelle actuelle"""
        return {
            "macd_color": self.config.macd_color,
            "signal_color": self.config.signal_color,
            "histogram_enabled": self.config.histogram_enabled,
            "histogram_positive_color": getattr(self.config, 'histogram_positive_color', '#4CAF50'),
            "histogram_negative_color": getattr(self.config, 'histogram_negative_color', '#F44336'),
            "line_width": self.config.line_width,
            "zero_line_enabled": getattr(self.config, 'zero_line_enabled', True),
            "crossover_signals": getattr(self.config, 'crossover_signals', True)
        }