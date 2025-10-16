"""
EMA Plotter Module
Single responsibility: EMA visualization with Plotly
"""

import plotly.graph_objects as go
from typing import List, Dict, Any, Optional

from ....core.types import IndicatorResult


class EMAPlotter:
    """EMA visualization using Plotly charts"""

    @staticmethod
    def plot(ema_results: List[IndicatorResult]) -> go.Figure:
        """
        Plot EMA indicator

        Args:
            ema_results: List of EMA calculation results

        Returns:
            Plotly figure with EMA line
        """
        if not ema_results:
            # Return empty figure if no data
            fig = go.Figure()
            fig.update_layout(
                title="EMA Indicator",
                xaxis_title="Time",
                yaxis_title="EMA Value",
                height=400
            )
            return fig

        # Extract data
        timestamps = [result.timestamp for result in ema_results]
        ema_values = [float(result.value) for result in ema_results]

        # Create figure
        fig = go.Figure()

        # Add EMA line
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=ema_values,
            mode='lines',
            name='EMA',
            line=dict(color='red', width=2)
        ))

        # Update layout
        fig.update_layout(
            title="Exponential Moving Average (EMA)",
            xaxis_title="Time",
            yaxis_title="EMA Value",
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

        return fig

    @staticmethod
    def plot_with_price(ema_results: List[IndicatorResult], price_data: Optional[List[float]] = None) -> go.Figure:
        """
        Plot EMA with price data for crossover analysis

        Args:
            ema_results: List of EMA calculation results
            price_data: Optional price data for comparison

        Returns:
            Plotly figure with EMA and price lines
        """
        fig = EMAPlotter.plot(ema_results)

        if not ema_results or not price_data:
            return fig

        # Add price line if provided
        timestamps = [result.timestamp for result in ema_results]
        if len(price_data) == len(timestamps):
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=price_data,
                mode='lines',
                name='Price',
                line=dict(color='gray', width=1, dash='dot')
            ))

        return fig

    @staticmethod
    def plot_dual_ema(short_ema_results: List[IndicatorResult],
                      long_ema_results: List[IndicatorResult]) -> go.Figure:
        """
        Plot dual EMA (fast and slow) for crossover signals

        Args:
            short_ema_results: Fast EMA results
            long_ema_results: Slow EMA results

        Returns:
            Plotly figure with dual EMA lines
        """
        if not short_ema_results or not long_ema_results:
            fig = go.Figure()
            fig.update_layout(title="Dual EMA")
            return fig

        # Extract data
        timestamps = [result.timestamp for result in short_ema_results]
        short_values = [float(result.value) for result in short_ema_results]
        long_values = [float(result.value) for result in long_ema_results]

        # Create figure
        fig = go.Figure()

        # Add fast EMA
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=short_values,
            mode='lines',
            name='Fast EMA',
            line=dict(color='blue', width=2)
        ))

        # Add slow EMA
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=long_values,
            mode='lines',
            name='Slow EMA',
            line=dict(color='red', width=2)
        ))

        # Update layout
        fig.update_layout(
            title="Dual EMA Crossover",
            xaxis_title="Time",
            yaxis_title="EMA Value",
            height=400,
            showlegend=True
        )

        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

        return fig