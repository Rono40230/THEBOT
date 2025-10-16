"""
OBV Plotter Module
Single responsibility: OBV visualization with Plotly
"""

import plotly.graph_objects as go
from typing import List

from ....core.types import IndicatorResult


class OBVPlotter:
    """OBV visualization using Plotly charts"""

    @staticmethod
    def plot(obv_results: List[IndicatorResult]) -> go.Figure:
        """
        Plot OBV indicator

        Args:
            obv_results: List of OBV calculation results

        Returns:
            Plotly figure with OBV line
        """
        if not obv_results:
            # Return empty figure if no data
            fig = go.Figure()
            fig.update_layout(
                title="OBV Indicator",
                xaxis_title="Time",
                yaxis_title="OBV Value",
                height=400
            )
            return fig

        # Extract data
        timestamps = [result.timestamp for result in obv_results]
        obv_values = [float(result.value) for result in obv_results]

        # Create figure
        fig = go.Figure()

        # Add OBV line
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=obv_values,
            mode='lines',
            name='OBV',
            line=dict(color='purple', width=2)
        ))

        # Update layout
        fig.update_layout(
            title="On-Balance Volume (OBV)",
            xaxis_title="Time",
            yaxis_title="OBV Value",
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
    def plot_with_signals(obv_results: List[IndicatorResult]) -> go.Figure:
        """
        Plot OBV with volume-based signals

        Args:
            obv_results: List of OBV calculation results with signals

        Returns:
            Plotly figure with OBV and signals
        """
        fig = OBVPlotter.plot(obv_results)

        if not obv_results:
            return fig

        # Extract signal data
        timestamps = [result.timestamp for result in obv_results]
        obv_values = [float(result.value) for result in obv_results]

        buy_signals = []
        sell_signals = []
        divergence_signals = []

        for i, result in enumerate(obv_results):
            if result.signals:
                for signal in result.signals:
                    signal_name = signal.direction.name.lower()
                    if signal.direction.name == 'BUY':
                        buy_signals.append((timestamps[i], obv_values[i]))
                    elif signal.direction.name == 'SELL':
                        sell_signals.append((timestamps[i], obv_values[i]))
                    elif 'divergence' in signal_name:
                        divergence_signals.append((timestamps[i], obv_values[i]))

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

        # Add divergence signals
        if divergence_signals:
            div_x, div_y = zip(*divergence_signals)
            fig.add_trace(go.Scatter(
                x=div_x,
                y=div_y,
                mode='markers',
                name='Divergence',
                marker=dict(
                    symbol='x',
                    size=12,
                    color='orange'
                )
            ))

        return fig