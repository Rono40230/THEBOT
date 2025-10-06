"""
Module de visualisation pour les Order Blocks (Blocs d'Ordres)
Affichage professionnel des zones institutionnelles Smart Money
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from .config import OrderBlockConfig, OrderBlockType, OrderBlockStatus, OrderBlockStrength
from .calculator import OrderBlock, OrderBlockCalculator


class OrderBlockPlotter:
    """Gestionnaire de visualisation des Order Blocks"""
    
    def __init__(self, config: OrderBlockConfig):
        self.config = config
        
    def add_blocks_to_chart(self, fig: go.Figure, blocks: List[OrderBlock], 
                           data: pd.DataFrame) -> go.Figure:
        """
        Ajoute les Order Blocks au graphique principal
        
        Args:
            fig: Figure Plotly existante
            blocks: Liste des Order Blocks à afficher
            data: DataFrame des données OHLC
        
        Returns:
            Figure mise à jour avec les Order Blocks
        """
        
        if not blocks:
            return fig
        
        # Filtrer les blocs à afficher
        visible_blocks = self._filter_blocks_for_display(blocks)
        
        # Ajouter chaque bloc
        for block in visible_blocks:
            fig = self._add_single_block(fig, block, data)
        
        # Ajouter la légende des Order Blocks
        fig = self._add_legend_info(fig, visible_blocks)
        
        return fig
    
    def _filter_blocks_for_display(self, blocks: List[OrderBlock]) -> List[OrderBlock]:
        """Filtre les blocs à afficher selon la configuration"""
        
        # Filtrer par statut
        visible_blocks = [
            b for b in blocks 
            if b.status in [OrderBlockStatus.ACTIVE, OrderBlockStatus.TESTED]
        ]
        
        # Limiter le nombre
        if len(visible_blocks) > self.config.max_blocks_display:
            # Prioriser par force et récence
            visible_blocks.sort(
                key=lambda x: (x.strength_score, -x.formation_bar), 
                reverse=True
            )
            visible_blocks = visible_blocks[:self.config.max_blocks_display]
        
        return visible_blocks
    
    def _add_single_block(self, fig: go.Figure, block: OrderBlock, 
                         data: pd.DataFrame) -> go.Figure:
        """Ajoute un Order Block individuel au graphique"""
        
        # Couleurs selon le type et le statut
        if block.type == OrderBlockType.BULLISH:
            base_color = self.config.bullish_color
        else:
            base_color = self.config.bearish_color
        
        # Opacité selon le statut
        if block.status == OrderBlockStatus.ACTIVE:
            opacity = self.config.opacity_active
        elif block.status == OrderBlockStatus.TESTED:
            opacity = self.config.opacity_tested
        else:
            opacity = self.config.opacity_broken
        
        # Calculer les coordonnées temporelles
        start_time = block.left_time
        
        # Estimer la fin (jusqu'à maintenant ou cassure)
        if block.break_time:
            end_time = block.break_time
        elif block.status == OrderBlockStatus.EXPIRED:
            end_time = start_time + timedelta(hours=self.config.max_age_bars)
        else:
            end_time = data.index[-1]
        
        # Ajouter le rectangle du bloc
        fig.add_shape(
            type="rect",
            x0=start_time,
            y0=block.bottom,
            x1=end_time,
            y1=block.top,
            fillcolor=base_color,
            opacity=opacity,
            line=dict(
                color=base_color,
                width=2 if block.status == OrderBlockStatus.ACTIVE else 1
            ),
            layer="below"
        )
        
        # Ajouter les labels si activés
        if self.config.show_labels:
            fig = self._add_block_label(fig, block, start_time)
        
        # Ajouter les marqueurs de retest
        if block.retest_count > 0:
            fig = self._add_retest_markers(fig, block, data)
        
        # Ajouter ligne de milieu pour les blocs forts
        if block.strength_level in [OrderBlockStrength.STRONG, OrderBlockStrength.VERY_STRONG]:
            fig = self._add_midline(fig, block, start_time, end_time, base_color)
        
        return fig
    
    def _add_block_label(self, fig: go.Figure, block: OrderBlock, 
                        start_time: datetime) -> go.Figure:
        """Ajoute un label informatif au bloc"""
        
        # Position du label
        label_y = block.top if block.type == OrderBlockType.BULLISH else block.bottom
        
        # Contenu du label
        label_parts = []
        
        # Type de bloc
        if block.type == OrderBlockType.BULLISH:
            label_parts.append("📈 OB Bull")
        else:
            label_parts.append("📉 OB Bear")
        
        # Force si activée
        if self.config.show_strength:
            strength_emoji = {
                OrderBlockStrength.WEAK: "⭐",
                OrderBlockStrength.MEDIUM: "⭐⭐",
                OrderBlockStrength.STRONG: "⭐⭐⭐",
                OrderBlockStrength.VERY_STRONG: "⭐⭐⭐⭐"
            }
            label_parts.append(strength_emoji[block.strength_level])
        
        # Nombre de retests si activé
        if self.config.show_retest_count and block.retest_count > 0:
            label_parts.append(f"RT:{block.retest_count}")
        
        label_text = " ".join(label_parts)
        
        # Ajouter l'annotation
        fig.add_annotation(
            x=start_time,
            y=label_y,
            text=label_text,
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=self.config.bullish_color if block.type == OrderBlockType.BULLISH else self.config.bearish_color,
            font=dict(
                size=10,
                color="white"
            ),
            bgcolor=self.config.bullish_color if block.type == OrderBlockType.BULLISH else self.config.bearish_color,
            bordercolor="white",
            borderwidth=1,
            opacity=0.8,
            xanchor="left" if block.type == OrderBlockType.BULLISH else "right",
            yanchor="bottom" if block.type == OrderBlockType.BULLISH else "top"
        )
        
        return fig
    
    def _add_retest_markers(self, fig: go.Figure, block: OrderBlock, 
                           data: pd.DataFrame) -> go.Figure:
        """Ajoute des marqueurs pour les retests"""
        
        # Pour simplifier, on ajoute juste un indicateur de retest
        # Dans une implémentation complète, on pourrait traquer chaque retest
        
        if block.last_retest_time:
            # Marqueur de dernier retest
            fig.add_trace(go.Scatter(
                x=[block.last_retest_time],
                y=[block.mid_price],
                mode='markers',
                marker=dict(
                    symbol='circle',
                    size=8,
                    color='yellow',
                    line=dict(color='orange', width=2)
                ),
                name=f'Retest OB',
                showlegend=False,
                hovertemplate=f'<b>Retest Order Block</b><br>' +
                             f'Type: {block.type.value}<br>' +
                             f'Retests: {block.retest_count}<br>' +
                             f'Force: {block.strength_level.value}<br>' +
                             '<extra></extra>'
            ))
        
        return fig
    
    def _add_midline(self, fig: go.Figure, block: OrderBlock, 
                    start_time: datetime, end_time: datetime, 
                    color: str) -> go.Figure:
        """Ajoute une ligne de milieu pour les blocs importants"""
        
        fig.add_shape(
            type="line",
            x0=start_time,
            y0=block.mid_price,
            x1=end_time,
            y1=block.mid_price,
            line=dict(
                color=color,
                width=2,
                dash="dot"
            ),
            opacity=0.7
        )
        
        return fig
    
    def _add_legend_info(self, fig: go.Figure, blocks: List[OrderBlock]) -> go.Figure:
        """Ajoute des informations de légende"""
        
        if not blocks:
            return fig
        
        # Statistiques des blocs
        active_count = len([b for b in blocks if b.status == OrderBlockStatus.ACTIVE])
        tested_count = len([b for b in blocks if b.status == OrderBlockStatus.TESTED])
        strong_count = len([b for b in blocks if b.strength_level in [OrderBlockStrength.STRONG, OrderBlockStrength.VERY_STRONG]])
        
        # Ajouter trace invisible pour la légende
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=0.1, color='rgba(0,0,0,0)'),
            name=f'📊 Order Blocks: {len(blocks)} total',
            showlegend=True,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=0.1, color='rgba(0,0,0,0)'),
            name=f'✅ Actifs: {active_count} | Testés: {tested_count}',
            showlegend=True,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=0.1, color='rgba(0,0,0,0)'),
            name=f'💪 Forts: {strong_count}',
            showlegend=True,
            hoverinfo='skip'
        ))
        
        return fig
    
    def create_analysis_chart(self, blocks: List[OrderBlock]) -> go.Figure:
        """Crée un graphique d'analyse des Order Blocks"""
        
        if not blocks:
            return go.Figure()
        
        # Préparer les données pour l'analyse
        block_data = []
        for block in blocks:
            block_data.append({
                'id': block.id,
                'type': block.type.value,
                'status': block.status.value,
                'strength': block.strength_score,
                'strength_level': block.strength_level.value,
                'size_pct': block.size_percentage,
                'retest_count': block.retest_count,
                'impulse_strength': block.impulse_strength,
                'age_bars': block.age_bars
            })
        
        df = pd.DataFrame(block_data)
        
        # Créer un graphique en barres de la distribution des forces
        fig = go.Figure()
        
        # Histogramme des forces
        fig.add_trace(go.Histogram(
            x=df['strength'],
            nbinsx=20,
            name='Distribution Force',
            marker_color='lightblue',
            opacity=0.7
        ))
        
        fig.update_layout(
            title='📊 Analyse des Order Blocks - Distribution des Forces',
            xaxis_title='Score de Force',
            yaxis_title='Nombre de Blocs',
            template='plotly_dark',
            height=400
        )
        
        return fig
    
    def create_statistics_summary(self, blocks: List[OrderBlock]) -> Dict[str, Any]:
        """Crée un résumé statistique des Order Blocks"""
        
        if not blocks:
            return {
                'total_blocks': 0,
                'active_blocks': 0,
                'average_strength': 0,
                'strongest_block': None,
                'most_retested': None
            }
        
        # Calculs statistiques
        active_blocks = [b for b in blocks if b.status == OrderBlockStatus.ACTIVE]
        
        strengths = [b.strength_score for b in blocks]
        average_strength = np.mean(strengths) if strengths else 0
        
        # Bloc le plus fort
        strongest_block = max(blocks, key=lambda x: x.strength_score) if blocks else None
        
        # Bloc le plus retesté
        most_retested = max(blocks, key=lambda x: x.retest_count) if blocks else None
        
        # Distribution par type
        bullish_count = len([b for b in blocks if b.type == OrderBlockType.BULLISH])
        bearish_count = len([b for b in blocks if b.type == OrderBlockType.BEARISH])
        
        return {
            'total_blocks': len(blocks),
            'active_blocks': len(active_blocks),
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'average_strength': round(average_strength, 3),
            'strongest_block': {
                'id': strongest_block.id,
                'type': strongest_block.type.value,
                'strength': round(strongest_block.strength_score, 3),
                'level': strongest_block.strength_level.value
            } if strongest_block else None,
            'most_retested': {
                'id': most_retested.id,
                'type': most_retested.type.value,
                'retest_count': most_retested.retest_count,
                'strength': round(most_retested.strength_score, 3)
            } if most_retested else None
        }


def create_order_blocks_overlay(data: pd.DataFrame, config: OrderBlockConfig) -> Dict[str, Any]:
    """
    Fonction utilitaire pour créer une overlay Order Blocks complète
    
    Args:
        data: DataFrame OHLCV
        config: Configuration Order Blocks
    
    Returns:
        Dictionnaire avec les traces et informations pour l'overlay
    """
    
    # Créer le calculateur
    calculator = OrderBlockCalculator(config)
    
    # Analyser les blocs
    blocks = calculator.analyze_blocks(data)
    
    # Créer le plotter
    plotter = OrderBlockPlotter(config)
    
    # Créer une figure temporaire pour extraire les traces
    temp_fig = go.Figure()
    temp_fig = plotter.add_blocks_to_chart(temp_fig, blocks, data)
    
    # Extraire les informations
    overlay_data = {
        'blocks': blocks,
        'total_blocks': len(blocks),
        'active_blocks': len([b for b in blocks if b.status == OrderBlockStatus.ACTIVE]),
        'strong_blocks': len([b for b in blocks if b.strength_level in [OrderBlockStrength.STRONG, OrderBlockStrength.VERY_STRONG]]),
        'shapes': temp_fig.layout.shapes,
        'annotations': temp_fig.layout.annotations,
        'traces': temp_fig.data,
        'statistics': plotter.create_statistics_summary(blocks),
        'trading_signals': calculator.get_trading_signals(data['close'].iloc[-1]) if len(data) > 0 else {}
    }
    
    return overlay_data