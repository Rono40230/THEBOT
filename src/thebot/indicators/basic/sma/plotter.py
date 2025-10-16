"""
SMA Plotter Module
Single responsibility: SMA visualization with Plotly
"""

import plotly.graph_objects as go
from typing import List, Dict, Any, Optional

from ....core.types import IndicatorResult


class SMAPlotter:
    """SMA visualization using Plotly charts"""

    @staticmethod
    def plot(sma_results: List[IndicatorResult]) -> go.Figure:
        """
        Plot SMA indicator

        Args:
            sma_results: List of SMA calculation results

        Returns:
            Plotly figure with SMA line
        """
        if not sma_results:
            # Return empty figure if no data
            fig = go.Figure()
            fig.update_layout(
                title="SMA Indicator",
                xaxis_title="Time",
                yaxis_title="SMA Value",
                height=400
            )
            return fig

        # Extract data
        timestamps = [result.timestamp for result in sma_results]
        sma_values = [float(result.value) for result in sma_results]

        # Create figure
        fig = go.Figure()

        # Add SMA line
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=sma_values,
            mode='lines',
            name='SMA',
            line=dict(color='blue', width=2)
        ))

        # Update layout
        fig.update_layout(
            title="Simple Moving Average (SMA)",
            xaxis_title="Time",
            yaxis_title="SMA Value",
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
    def plot_with_price(sma_results: List[IndicatorResult], price_data: Optional[List[float]] = None) -> go.Figure:
        """
        Plot SMA with price data for crossover analysis

        Args:
            sma_results: List of SMA calculation results
            price_data: Optional price data for comparison

        Returns:
            Plotly figure with SMA and price lines
        """
        fig = SMAPlotter.plot(sma_results)

        if not sma_results or not price_data:
            return fig

        # Add price line if provided
        timestamps = [result.timestamp for result in sma_results]
        if len(price_data) == len(timestamps):
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=price_data,
                mode='lines',
                name='Price',
                line=dict(color='gray', width=1, dash='dot')
            ))

        return fig