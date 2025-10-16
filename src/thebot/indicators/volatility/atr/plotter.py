"""
ATR Plotter Module
Single responsibility: ATR visualization with Plotly
"""

import plotly.graph_objects as go
from typing import List

from ....core.types import IndicatorResult


class ATRPlotter:
    """ATR visualization using Plotly charts"""

    @staticmethod
    def plot(atr_results: List[IndicatorResult]) -> go.Figure:
        """
        Plot ATR indicator

        Args:
            atr_results: List of ATR calculation results

        Returns:
            Plotly figure with ATR line
        """
        if not atr_results:
            # Return empty figure if no data
            fig = go.Figure()
            fig.update_layout(
                title="ATR Indicator",
                xaxis_title="Time",
                yaxis_title="ATR Value",
                height=400
            )
            return fig

        # Extract data
        timestamps = [result.timestamp for result in atr_results]
        atr_values = [float(result.value) for result in atr_results]

        # Create figure
        fig = go.Figure()

        # Add ATR line
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=atr_values,
            mode='lines',
            name='ATR',
            line=dict(color='orange', width=2)
        ))

        # Update layout
        fig.update_layout(
            title="Average True Range (ATR)",
            xaxis_title="Time",
            yaxis_title="ATR Value",
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
    def plot_with_signals(atr_results: List[IndicatorResult],
                         low_threshold: float = None,
                         high_threshold: float = None) -> go.Figure:
        """
        Plot ATR with volatility signals

        Args:
            atr_results: List of ATR calculation results with signals
            low_threshold: Low volatility threshold
            high_threshold: High volatility threshold

        Returns:
            Plotly figure with ATR and signals
        """
        fig = ATRPlotter.plot(atr_results)

        if not atr_results:
            return fig

        # Extract signal data
        timestamps = [result.timestamp for result in atr_results]
        atr_values = [float(result.value) for result in atr_results]

        low_vol_signals = []
        high_vol_signals = []

        for i, result in enumerate(atr_results):
            if result.signals:
                for signal in result.signals:
                    signal_name = signal.direction.name.lower()
                    if 'low' in signal_name or 'calm' in signal_name:
                        low_vol_signals.append((timestamps[i], atr_values[i]))
                    elif 'high' in signal_name or 'volatile' in signal_name:
                        high_vol_signals.append((timestamps[i], atr_values[i]))

        # Add threshold lines if provided
        if low_threshold is not None:
            fig.add_trace(go.Scatter(
                x=[timestamps[0], timestamps[-1]],
                y=[low_threshold, low_threshold],
                mode='lines',
                name='Low Volatility Threshold',
                line=dict(color='green', width=1, dash='dot')
            ))

        if high_threshold is not None:
            fig.add_trace(go.Scatter(
                x=[timestamps[0], timestamps[-1]],
                y=[high_threshold, high_threshold],
                mode='lines',
                name='High Volatility Threshold',
                line=dict(color='red', width=1, dash='dot')
            ))

        # Add low volatility signals
        if low_vol_signals:
            low_x, low_y = zip(*low_vol_signals)
            fig.add_trace(go.Scatter(
                x=low_x,
                y=low_y,
                mode='markers',
                name='Low Volatility',
                marker=dict(
                    symbol='circle',
                    size=8,
                    color='green'
                )
            ))

        # Add high volatility signals
        if high_vol_signals:
            high_x, high_y = zip(*high_vol_signals)
            fig.add_trace(go.Scatter(
                x=high_x,
                y=high_y,
                mode='markers',
                name='High Volatility',
                marker=dict(
                    symbol='diamond',
                    size=8,
                    color='red'
                )
            ))

        return fig