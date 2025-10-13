"""
Charts Components Module - THEBOT Dash
Composants de graphiques réutilisables avec Plotly
"""

from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go

from ..core.calculators import calculator
from ..core.config import ui_config


class ChartComponents:
    """Composants de graphiques réutilisables"""

    def __init__(self):
        self.config = ui_config
        self.calculator = calculator

    def create_candlestick_chart(
        self,
        df: pd.DataFrame,
        symbol: str,
        timeframe: str,
        sma_enabled: bool = False,
        sma_period: int = 20,
        ema_enabled: bool = False,
        ema_period: int = 12,
    ) -> go.Figure:
        """Créer graphique candlestick avec indicateurs"""

        fig = go.Figure()

        # Graphique candlestick principal
        fig.add_trace(
            go.Candlestick(
                x=df.index,  # timestamp est l'index, pas une colonne
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name=symbol,
                increasing_line_color=self.config.colors["bullish"],
                decreasing_line_color=self.config.colors["bearish"],
            )
        )

        # Ajouter SMA si activé
        if sma_enabled and sma_period > 0:
            sma_values = self.calculator.calculate_sma(df["close"].tolist(), sma_period)
            fig.add_trace(
                go.Scatter(
                    x=df.index,  # timestamp est l'index
                    y=sma_values,
                    mode="lines",
                    name=f"SMA({sma_period})",
                    line=dict(color=self.config.colors["sma"], width=2),
                    opacity=0.8,
                )
            )

        # Ajouter EMA si activé
        if ema_enabled and ema_period > 0:
            ema_values = self.calculator.calculate_ema(df["close"].tolist(), ema_period)
            fig.add_trace(
                go.Scatter(
                    x=df.index,  # timestamp est l'index
                    y=ema_values,
                    mode="lines",
                    name=f"EMA({ema_period})",
                    line=dict(color=self.config.colors["ema"], width=2),
                    opacity=0.8,
                )
            )

        # Configuration du graphique
        fig.update_layout(
            title=f"📊 {symbol} - {timeframe} | THEBOT Analysis",
            xaxis_title="Time",
            yaxis_title="Price",
            template="plotly_dark",
            height=self.config.main_chart_height,
            showlegend=True,
            legend=dict(x=0, y=1, orientation="h"),
            margin=dict(l=0, r=0, t=40, b=0),
            hovermode="x unified",
        )

        fig.update_xaxes(rangeslider_visible=False)

        return fig

    def create_rsi_chart(self, df: pd.DataFrame, rsi_period: int = 14) -> go.Figure:
        """Créer graphique RSI"""

        fig = go.Figure()

        # Calcul RSI
        rsi_values = self.calculator.calculate_rsi(df["close"].tolist(), rsi_period)

        # Graphique RSI principal
        fig.add_trace(
            go.Scatter(
                x=df.index,  # timestamp est l'index
                y=rsi_values,
                mode="lines",
                name=f"RSI({rsi_period})",
                line=dict(color=self.config.colors["rsi"], width=2),
                fill=None,
            )
        )

        # Zones de surachat/survente
        fig.add_hline(
            y=70,
            line_dash="dash",
            line_color="red",
            opacity=0.7,
            annotation_text="Overbought",
            annotation_position="top right",
        )
        fig.add_hline(
            y=30,
            line_dash="dash",
            line_color="green",
            opacity=0.7,
            annotation_text="Oversold",
            annotation_position="bottom right",
        )

        # Zones colorées
        fig.add_hrect(
            y0=70,
            y1=100,
            fillcolor="red",
            opacity=0.1,
            annotation_text="SELL ZONE",
            annotation_position="top left",
        )
        fig.add_hrect(
            y0=0,
            y1=30,
            fillcolor="green",
            opacity=0.1,
            annotation_text="BUY ZONE",
            annotation_position="bottom left",
        )

        # Configuration
        fig.update_layout(
            title="📈 RSI Oscillator - THEBOT Analysis",
            yaxis=dict(range=[0, 100]),
            template="plotly_dark",
            height=self.config.indicator_chart_height,
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False,
            hovermode="x unified",
        )

        return fig

    def create_volume_chart(self, df: pd.DataFrame) -> go.Figure:
        """Créer graphique de volume"""

        fig = go.Figure()

        # Graphique en barres pour le volume
        fig.add_trace(
            go.Bar(
                x=df.index,  # timestamp est l'index
                y=df["volume"],
                name="Volume",
                marker_color=self.config.colors["volume"],
                opacity=0.7,
            )
        )

        # Ligne de moyenne pour contexte
        volume_ma = pd.Series(df["volume"]).rolling(window=20).mean()
        fig.add_trace(
            go.Scatter(
                x=df.index,  # timestamp est l'index
                y=volume_ma,
                mode="lines",
                name="Volume MA(20)",
                line=dict(color="yellow", width=1, dash="dot"),
                opacity=0.8,
            )
        )

        # Configuration
        fig.update_layout(
            title="📊 Volume Analysis",
            yaxis_title="Volume",
            template="plotly_dark",
            height=self.config.indicator_chart_height,
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False,
            hovermode="x unified",
        )

        return fig

    def create_atr_chart(self, df: pd.DataFrame, atr_period: int = 14) -> go.Figure:
        """Créer graphique ATR"""

        fig = go.Figure()

        # Calcul ATR
        atr_values = self.calculator.calculate_atr(
            df["high"].tolist(), df["low"].tolist(), df["close"].tolist(), atr_period
        )

        # Graphique ATR principal avec remplissage
        fig.add_trace(
            go.Scatter(
                x=df.index,  # timestamp est l'index
                y=atr_values,
                mode="lines",
                name=f"ATR({atr_period})",
                line=dict(color=self.config.colors["atr"], width=2),
                fill="tozeroy",
                fillcolor="rgba(255, 140, 0, 0.2)",
            )
        )

        # Moyenne mobile ATR pour référence
        atr_ma = pd.Series(atr_values).rolling(window=20).mean()
        fig.add_trace(
            go.Scatter(
                x=df.index,  # timestamp est l'index
                y=atr_ma,
                mode="lines",
                name="ATR MA(20)",
                line=dict(color="yellow", width=1, dash="dot"),
                opacity=0.7,
            )
        )

        # Configuration
        fig.update_layout(
            title="📊 ATR (Average True Range) - Volatility",
            yaxis_title="ATR Value",
            template="plotly_dark",
            height=self.config.indicator_chart_height,
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False,
            hovermode="x unified",
        )

        return fig

    def create_empty_chart(self, title: str = "No Data") -> go.Figure:
        """Créer un graphique vide pour les cas d'erreur"""

        fig = go.Figure()

        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )

        fig.update_layout(
            title=title,
            template="plotly_dark",
            height=200,
            margin=dict(l=0, r=0, t=40, b=0),
        )

        return fig


# Instance globale
charts = ChartComponents()
