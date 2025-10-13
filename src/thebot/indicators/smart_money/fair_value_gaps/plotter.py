# src/thebot/indicators/smart_money/fair_value_gaps/plotter.py

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .calculator import FairValueGap, FVGStatus, FVGType
from .config import FVGConfig


class FVGPlotterError(Exception):
    """Erreur lors de la visualisation des Fair Value Gaps."""

    pass


class FVGPlotter:
    """
    Visualiseur pour les Fair Value Gaps sur graphiques Plotly.

    Génère les éléments visuels pour afficher les zones FVG directement
    sur le graphique principal des prix.
    """

    def __init__(self, config: FVGConfig):
        """
        Initialise le visualiseur FVG.

        Args:
            config: Configuration FVG pour les couleurs et styles
        """
        self.config = config

    def add_gaps_to_figure(
        self,
        fig: go.Figure,
        gaps: List[FairValueGap],
        x_data: List[datetime],
        row: int = 1,
        col: int = 1,
    ) -> go.Figure:
        """
        Ajoute les Fair Value Gaps à un graphique Plotly.

        Args:
            fig: Figure Plotly existante
            gaps: Liste des gaps à afficher
            x_data: Données temporelles pour l'axe X
            row: Ligne du subplot (défaut: 1)
            col: Colonne du subplot (défaut: 1)

        Returns:
            Figure Plotly modifiée avec les gaps
        """
        if not gaps:
            return fig

        try:
            # Trier les gaps par âge (plus anciens en premier pour layering)
            sorted_gaps = sorted(gaps, key=lambda g: g.creation_time)

            for gap in sorted_gaps:
                fig = self._add_single_gap(fig, gap, x_data, row, col)

            return fig

        except Exception as e:
            raise FVGPlotterError(f"Erreur lors de l'ajout des gaps: {str(e)}")

    def _add_single_gap(
        self,
        fig: go.Figure,
        gap: FairValueGap,
        x_data: List[datetime],
        row: int,
        col: int,
    ) -> go.Figure:
        """Ajoute un seul gap au graphique."""

        # Déterminer les couleurs selon le type et statut
        fill_color, line_color = self._get_gap_colors(gap)

        # Calculer les coordonnées temporelles
        start_index = max(0, gap.creation_index)
        end_index = min(len(x_data) - 1, start_index + gap.age_in_candles)

        if start_index >= len(x_data) or end_index >= len(x_data):
            return fig

        x_start = x_data[start_index]
        x_end = x_data[end_index]

        # Ajouter la zone rectangulaire du gap
        fig.add_shape(
            type="rect",
            x0=x_start,
            x1=x_end,
            y0=gap.bottom,
            y1=gap.top,
            fillcolor=fill_color,
            line=dict(color=line_color, width=1),
            opacity=self.config.gap_opacity,
            row=row,
            col=col,
        )

        # Ajouter les lignes de délimitation
        self._add_gap_lines(fig, gap, x_start, x_end, line_color, row, col)

        # Ajouter les labels si activés
        if self.config.show_gap_labels:
            self._add_gap_label(fig, gap, x_start, x_end, row, col)

        return fig

    def _get_gap_colors(self, gap: FairValueGap) -> Tuple[str, str]:
        """Détermine les couleurs du gap selon son type et statut."""

        if gap.status == FVGStatus.FILLED:
            return self.config.filled_gap_color, self.config.filled_gap_color

        if gap.type == FVGType.BULLISH:
            base_color = self.config.bullish_gap_color
        else:
            base_color = self.config.bearish_gap_color

        # Ajuster la couleur selon le statut
        if gap.status == FVGStatus.PARTIALLY_FILLED:
            # Couleur légèrement atténuée pour gaps partiellement comblés
            fill_color = self._adjust_color_opacity(base_color, 0.6)
        else:
            fill_color = base_color

        return fill_color, base_color

    def _adjust_color_opacity(self, color: str, opacity: float) -> str:
        """Ajuste l'opacité d'une couleur hexadécimale."""
        if color.startswith("#") and len(color) == 7:
            # Convertir hex en rgba pour ajuster l'opacité
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return f"rgba({r}, {g}, {b}, {opacity})"
        return color

    def _add_gap_lines(
        self,
        fig: go.Figure,
        gap: FairValueGap,
        x_start: datetime,
        x_end: datetime,
        line_color: str,
        row: int,
        col: int,
    ):
        """Ajoute les lignes de délimitation du gap."""

        # Ligne du haut
        fig.add_shape(
            type="line",
            x0=x_start,
            x1=x_end,
            y0=gap.top,
            y1=gap.top,
            line=dict(color=line_color, width=2, dash="solid"),
            row=row,
            col=col,
        )

        # Ligne du bas
        fig.add_shape(
            type="line",
            x0=x_start,
            x1=x_end,
            y0=gap.bottom,
            y1=gap.bottom,
            line=dict(color=line_color, width=2, dash="solid"),
            row=row,
            col=col,
        )

        # Ligne médiane (optionnelle)
        if gap.is_active():
            fig.add_shape(
                type="line",
                x0=x_start,
                x1=x_end,
                y0=gap.mid_point,
                y1=gap.mid_point,
                line=dict(color=line_color, width=1, dash="dot"),
                opacity=0.7,
                row=row,
                col=col,
            )

    def _add_gap_label(
        self,
        fig: go.Figure,
        gap: FairValueGap,
        x_start: datetime,
        x_end: datetime,
        row: int,
        col: int,
    ):
        """Ajoute un label informatif au gap."""

        # Position du label (côté gauche du gap)
        label_x = x_start
        label_y = gap.mid_point

        # Contenu du label
        gap_type_symbol = "🔼" if gap.type == FVGType.BULLISH else "🔽"
        status_symbol = self._get_status_symbol(gap.status)

        label_text = f"{gap_type_symbol} FVG {status_symbol}"

        if self.config.show_fill_percentage and gap.fill_percentage > 0:
            label_text += f"<br>{gap.fill_percentage:.1f}% filled"

        # Ajouter informations supplémentaires
        if gap.volume_confirmation:
            label_text += "<br>📊 Vol✓"

        label_text += f"<br>💪 {gap.strength:.2f}"

        # Couleur du texte selon le type
        text_color = (
            self.config.bullish_gap_color
            if gap.type == FVGType.BULLISH
            else self.config.bearish_gap_color
        )

        fig.add_annotation(
            x=label_x,
            y=label_y,
            text=label_text,
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=text_color,
            font=dict(size=10, color=text_color),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor=text_color,
            borderwidth=1,
            row=row,
            col=col,
        )

    def _get_status_symbol(self, status: FVGStatus) -> str:
        """Retourne le symbole correspondant au statut."""
        symbols = {
            FVGStatus.ACTIVE: "🟢",
            FVGStatus.PARTIALLY_FILLED: "🟡",
            FVGStatus.FILLED: "🔴",
            FVGStatus.EXPIRED: "⚫",
        }
        return symbols.get(status, "❓")

    def create_gaps_summary_table(self, gaps: List[FairValueGap]) -> go.Figure:
        """
        Crée un tableau récapitulatif des gaps.

        Args:
            gaps: Liste des gaps à inclure dans le tableau

        Returns:
            Figure Plotly avec tableau
        """
        if not gaps:
            return go.Figure()

        # Préparer les données du tableau
        headers = [
            "ID",
            "Type",
            "Status",
            "Size (%)",
            "Fill (%)",
            "Strength",
            "Age",
            "Touches",
            "Volume Conf.",
        ]

        rows = []
        for gap in gaps:
            row = [
                gap.id,
                "🔼 Bull" if gap.type == FVGType.BULLISH else "🔽 Bear",
                self._get_status_symbol(gap.status) + " " + gap.status.value.title(),
                f"{gap.size:.2f}%",
                f"{gap.fill_percentage:.1f}%" if gap.fill_percentage > 0 else "-",
                f"{gap.strength:.2f}",
                f"{gap.age_in_candles}",
                f"{gap.touches}",
                "✅" if gap.volume_confirmation else "❌",
            ]
            rows.append(row)

        # Transposer pour Plotly table
        cell_values = [list(row) for row in zip(*rows)]

        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=headers,
                        fill_color="paleturquoise",
                        align="left",
                        font=dict(size=12, color="black"),
                    ),
                    cells=dict(
                        values=cell_values,
                        fill_color="lavender",
                        align="left",
                        font=dict(size=11, color="black"),
                    ),
                )
            ]
        )

        fig.update_layout(
            title="📊 Fair Value Gaps Summary",
            height=300,
            margin=dict(l=0, r=0, t=40, b=0),
        )

        return fig

    def create_gaps_statistics_chart(self, statistics: Dict[str, Any]) -> go.Figure:
        """
        Crée un graphique de statistiques des gaps.

        Args:
            statistics: Dictionnaire avec statistiques calculées

        Returns:
            Figure Plotly avec graphiques de stats
        """
        # Créer sous-graphiques
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=[
                "Gap Distribution",
                "Gap Status",
                "Gap Sizes",
                "Fill Rate Trend",
            ],
            specs=[
                [{"type": "pie"}, {"type": "bar"}],
                [{"type": "histogram"}, {"type": "scatter"}],
            ],
        )

        # 1. Distribution des types de gaps
        gap_types = {"Bullish": 0, "Bearish": 0}
        gap_statuses = {"Active": 0, "Filled": 0, "Partially Filled": 0, "Expired": 0}
        gap_sizes = []

        # TODO: Extraire ces données depuis statistics
        # Pour l'instant, utiliser des données d'exemple

        # Graphique en secteurs pour les types
        fig.add_trace(
            go.Pie(
                labels=list(gap_types.keys()),
                values=list(gap_types.values()),
                name="Gap Types",
            ),
            row=1,
            col=1,
        )

        # Graphique en barres pour les statuts
        fig.add_trace(
            go.Bar(
                x=list(gap_statuses.keys()),
                y=list(gap_statuses.values()),
                name="Gap Status",
            ),
            row=1,
            col=2,
        )

        fig.update_layout(
            title="📈 Fair Value Gaps Analytics", height=600, showlegend=True
        )

        return fig

    def get_gaps_for_alerts(
        self,
        gaps: List[FairValueGap],
        current_price: float,
        proximity_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Identifie les gaps proches du prix actuel pour les alertes.

        Args:
            gaps: Liste des gaps actifs
            current_price: Prix actuel
            proximity_threshold: Seuil de proximité en %

        Returns:
            Liste des alertes FVG
        """
        alerts = []

        for gap in gaps:
            if not gap.is_active():
                continue

            # Calculer la distance au gap
            distances = [
                abs(current_price - gap.top) / current_price * 100,
                abs(current_price - gap.bottom) / current_price * 100,
            ]
            min_distance = min(distances)

            if min_distance <= proximity_threshold:
                alert = {
                    "gap_id": gap.id,
                    "gap_type": gap.type.value,
                    "distance": min_distance,
                    "strength": gap.strength,
                    "message": self._generate_alert_message(gap, current_price),
                    "priority": self._calculate_alert_priority(gap, min_distance),
                }
                alerts.append(alert)

        # Trier par priorité
        alerts.sort(key=lambda a: a["priority"], reverse=True)
        return alerts

    def _generate_alert_message(self, gap: FairValueGap, current_price: float) -> str:
        """Génère un message d'alerte pour un gap."""
        gap_type = "Bullish" if gap.type == FVGType.BULLISH else "Bearish"
        direction = "approaching" if gap.status == FVGStatus.ACTIVE else "testing"

        return (
            f"Price {direction} {gap_type} FVG at {gap.mid_point:.4f} "
            f"(Current: {current_price:.4f}, Strength: {gap.strength:.2f})"
        )

    def _calculate_alert_priority(self, gap: FairValueGap, distance: float) -> float:
        """Calcule la priorité d'une alerte (0-1)."""
        # Plus proche = plus prioritaire
        distance_score = max(0, (2.0 - distance) / 2.0)

        # Plus fort = plus prioritaire
        strength_score = gap.strength

        # Moins de touches = plus prioritaire
        touch_score = max(0, (5 - gap.touches) / 5)

        return distance_score * 0.4 + strength_score * 0.4 + touch_score * 0.2
