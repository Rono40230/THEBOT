"""
RSI Plotter Module
Single responsibility: RSI visualization with Plotly
"""

import plotly.graph_objects as go
from typing import List

from ....core.types import IndicatorResult


class RSIPlotter:
    """RSI visualization using Plotly charts"""

    @staticmethod
    def plot(rsi_results: List[IndicatorResult], overbought_level: float = 70,
             oversold_level: float = 30) -> go.Figure:
        """
        Plot RSI indicator with overbought/oversold levels

        Args:
            rsi_results: List of RSI calculation results
            overbought_level: Overbought threshold (default 70)
            oversold_level: Oversold threshold (default 30)

        Returns:
            Plotly figure with RSI line and levels
        """
        if not rsi_results:
            # Return empty figure if no data
            fig = go.Figure()
            fig.update_layout(
                title="RSI Indicator",
                xaxis_title="Time",
                yaxis_title="RSI Value",
                height=400
            )
            return fig

        # Extract data
        timestamps = [result.timestamp for result in rsi_results]
        rsi_values = [float(result.value) for result in rsi_results]

        # Create figure
        fig = go.Figure()

        # Add RSI line
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=rsi_values,
            mode='lines',
            name='RSI',
            line=dict(color='blue', width=2)
        ))

        # Add overbought level
        fig.add_trace(go.Scatter(
            x=[timestamps[0], timestamps[-1]],
            y=[overbought_level, overbought_level],
            mode='lines',
            name='Overbought',
            line=dict(color='red', width=1, dash='dash')
        ))

        # Add oversold level
        fig.add_trace(go.Scatter(
            x=[timestamps[0], timestamps[-1]],
            y=[oversold_level, oversold_level],
            mode='lines',
            name='Oversold',
            line=dict(color='green', width=1, dash='dash')
        ))

        # Update layout
        fig.update_layout(
            title="Relative Strength Index (RSI)",
            xaxis_title="Time",
            yaxis_title="RSI Value",
            yaxis=dict(range=[0, 100]),  # RSI range is 0-100
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
    def plot_with_signals(rsi_results: List[IndicatorResult],
                         overbought_level: float = 70,
                         oversold_level: float = 30) -> go.Figure:
        """
        Plot RSI with buy/sell signals

        Args:
            rsi_results: List of RSI calculation results with signals
            overbought_level: Overbought threshold
            oversold_level: Oversold threshold

        Returns:
            Plotly figure with RSI, levels, and signals
        """
        fig = RSIPlotter.plot(rsi_results, overbought_level, oversold_level)

        if not rsi_results:
            return fig

        # Extract signal data
        timestamps = [result.timestamp for result in rsi_results]
        rsi_values = [float(result.value) for result in rsi_results]

        buy_signals = []
        sell_signals = []

        for i, result in enumerate(rsi_results):
            if result.signals:
                for signal in result.signals:
                    if signal.direction.name == 'BUY':
                        buy_signals.append((timestamps[i], rsi_values[i]))
                    elif signal.direction.name == 'SELL':
                        sell_signals.append((timestamps[i], rsi_values[i]))

        # Add buy signals
        if buy_signals:
            buy_x, buy_y = zip(*buy_signals)
            fig.add_trace(go.Scatter(
                x=buy_x,
                y=buy_y,
                mode='markers',
                name='Buy Signal',
                marker=dict(
                    symbol='triangle-up',
                    size=10,
                    color='green'
                )
            ))

        # Add sell signals
        if sell_signals:
            sell_x, sell_y = zip(*sell_signals)
            fig.add_trace(go.Scatter(
                x=sell_x,
                y=sell_y,
                mode='markers',
                name='Sell Signal',
                marker=dict(
                    symbol='triangle-down',
                    size=10,
                    color='red'
                )
            ))

        return fig