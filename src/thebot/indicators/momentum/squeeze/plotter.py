"""
Squeeze Plotter Module
Single responsibility: Squeeze visualization with Plotly
"""

import plotly.graph_objects as go
from typing import List, Dict, Any

from ....core.types import IndicatorResult


class SqueezePlotter:
    """Squeeze visualization using Plotly charts"""

    @staticmethod
    def plot(squeeze_results: List[IndicatorResult]) -> go.Figure:
        """
        Plot squeeze analysis with Bollinger Bands and Keltner Channels

        Args:
            squeeze_results: List of squeeze calculation results

        Returns:
            Plotly figure with squeeze analysis
        """
        if not squeeze_results:
            fig = go.Figure()
            fig.update_layout(
                title="Squeeze Indicator",
                xaxis_title="Time",
                yaxis_title="Value",
                height=400
            )
            return fig

        # Extract data
        timestamps = []
        bb_upper = []
        bb_lower = []
        kc_upper = []
        kc_lower = []
        momentum_values = []
        squeeze_active = []

        for result in squeeze_results:
            timestamps.append(result.timestamp)

            if hasattr(result, 'metadata') and result.metadata:
                bb_data = result.metadata.get('bollinger_bands', {})
                kc_data = result.metadata.get('keltner_channels', {})

                bb_upper.append(float(bb_data.get('upper', 0)))
                bb_lower.append(float(bb_data.get('lower', 0)))
                kc_upper.append(float(kc_data.get('upper', 0)))
                kc_lower.append(float(kc_data.get('lower', 0)))
                momentum_values.append(float(result.metadata.get('momentum', 0)))
                squeeze_active.append(result.metadata.get('squeeze_active', False))
            else:
                # Fallback values
                bb_upper.append(0)
                bb_lower.append(0)
                kc_upper.append(0)
                kc_lower.append(0)
                momentum_values.append(0)
                squeeze_active.append(False)

        # Create subplot figure
        fig = go.Figure()

        # Add Bollinger Bands
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=bb_upper,
            mode='lines',
            name='BB Upper',
            line=dict(color='blue', width=1, dash='dot')
        ))

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=bb_lower,
            mode='lines',
            name='BB Lower',
            line=dict(color='blue', width=1, dash='dot'),
            fill='tonexty',
            fillcolor='rgba(0, 0, 255, 0.1)'
        ))

        # Add Keltner Channels
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=kc_upper,
            mode='lines',
            name='KC Upper',
            line=dict(color='red', width=1, dash='dash')
        ))

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=kc_lower,
            mode='lines',
            name='KC Lower',
            line=dict(color='red', width=1, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(255, 0, 0, 0.1)'
        ))

        # Add squeeze background
        squeeze_periods = []
        for i, is_squeeze in enumerate(squeeze_active):
            if is_squeeze:
                squeeze_periods.append((timestamps[i], bb_lower[i], kc_upper[i]))

        if squeeze_periods:
            squeeze_x, squeeze_y1, squeeze_y2 = zip(*squeeze_periods)
            fig.add_trace(go.Scatter(
                x=squeeze_x,
                y=squeeze_y1,
                mode='lines',
                name='Squeeze Active',
                line=dict(width=0),
                showlegend=False
            ))
            fig.add_trace(go.Scatter(
                x=squeeze_x,
                y=squeeze_y2,
                mode='lines',
                name='Squeeze Period',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(255, 255, 0, 0.2)',
                showlegend=True
            ))

        # Update layout
        fig.update_layout(
            title="Squeeze Momentum Analysis",
            xaxis_title="Time",
            yaxis_title="Price",
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
    def plot_momentum(squeeze_results: List[IndicatorResult]) -> go.Figure:
        """
        Plot squeeze momentum oscillator

        Args:
            squeeze_results: List of squeeze calculation results

        Returns:
            Plotly figure with momentum oscillator
        """
        if not squeeze_results:
            fig = go.Figure()
            fig.update_layout(
                title="Squeeze Momentum",
                xaxis_title="Time",
                yaxis_title="Momentum",
                height=300
            )
            return fig

        # Extract momentum data
        timestamps = []
        momentum_values = []

        for result in squeeze_results:
            timestamps.append(result.timestamp)
            if hasattr(result, 'metadata') and result.metadata:
                momentum_values.append(float(result.metadata.get('momentum', 0)))
            else:
                momentum_values.append(0)

        # Create figure
        fig = go.Figure()

        # Add momentum line
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=momentum_values,
            mode='lines',
            name='Momentum',
            line=dict(color='purple', width=2)
        ))

        # Add zero line
        fig.add_trace(go.Scatter(
            x=[timestamps[0], timestamps[-1]],
            y=[0, 0],
            mode='lines',
            name='Zero Line',
            line=dict(color='black', width=1, dash='dot')
        ))

        # Update layout
        fig.update_layout(
            title="Squeeze Momentum Oscillator",
            xaxis_title="Time",
            yaxis_title="Momentum",
            height=300,
            showlegend=True
        )

        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

        return fig