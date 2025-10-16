"""
Breakout Plotter Module
Single responsibility: Breakout visualization with Plotly
"""

import plotly.graph_objects as go
from typing import List, Dict, Any, Optional

from ....core.types import IndicatorResult


class BreakoutPlotter:
    """Breakout visualization using Plotly charts"""

    @staticmethod
    def plot(breakout_results: List[IndicatorResult]) -> go.Figure:
        """
        Plot breakout analysis with support/resistance levels

        Args:
            breakout_results: List of breakout calculation results

        Returns:
            Plotly figure with support/resistance levels and breakout signals
        """
        if not breakout_results:
            fig = go.Figure()
            fig.update_layout(
                title="Breakout Indicator",
                xaxis_title="Time",
                yaxis_title="Price",
                height=400
            )
            return fig

        # Extract data
        timestamps = []
        support_levels = []
        resistance_levels = []
        breakout_signals = []

        for result in breakout_results:
            timestamps.append(result.timestamp)

            # Extract levels from metadata or result value
            if hasattr(result, 'metadata') and result.metadata:
                support_levels.append(float(result.metadata.get('support_level', 0)))
                resistance_levels.append(float(result.metadata.get('resistance_level', 0)))

                # Check for breakout signals
                if result.metadata.get('breakout_detected', False):
                    breakout_signals.append({
                        'timestamp': result.timestamp,
                        'price': float(result.metadata.get('current_price', result.value)),
                        'type': result.metadata.get('breakout_type', 'unknown'),
                        'strength': float(result.metadata.get('breakout_strength', 0))
                    })
            else:
                # Fallback if no metadata
                support_levels.append(0)
                resistance_levels.append(0)

        # Create figure
        fig = go.Figure()

        # Add support level
        if any(s > 0 for s in support_levels):
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=support_levels,
                mode='lines',
                name='Support',
                line=dict(color='green', width=2, dash='dash')
            ))

        # Add resistance level
        if any(r > 0 for r in resistance_levels):
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=resistance_levels,
                mode='lines',
                name='Resistance',
                line=dict(color='red', width=2, dash='dash')
            ))

        # Add breakout signals
        for signal in breakout_signals:
            color = 'red' if signal['type'] == 'resistance' else 'green'
            symbol = 'triangle-up' if signal['type'] == 'resistance' else 'triangle-down'

            fig.add_trace(go.Scatter(
                x=[signal['timestamp']],
                y=[signal['price']],
                mode='markers',
                name=f"{signal['type'].title()} Breakout",
                marker=dict(
                    symbol=symbol,
                    size=max(8, min(15, signal['strength'] * 10)),  # Size based on strength
                    color=color
                ),
                showlegend=False  # Avoid duplicate legends
            ))

        # Update layout
        fig.update_layout(
            title="Breakout Analysis",
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
    def plot_with_price(breakout_results: List[IndicatorResult], price_data: Optional[List[float]] = None) -> go.Figure:
        """
        Plot breakout analysis with price data

        Args:
            breakout_results: List of breakout calculation results
            price_data: Price data for context

        Returns:
            Plotly figure with breakout analysis and price
        """
        fig = BreakoutPlotter.plot(breakout_results)

        if price_data and len(price_data) == len(breakout_results):
            timestamps = [result.timestamp for result in breakout_results]
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=price_data,
                mode='lines',
                name='Price',
                line=dict(color='blue', width=1),
                opacity=0.7
            ))

        return fig