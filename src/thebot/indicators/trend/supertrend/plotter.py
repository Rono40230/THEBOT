"""
SuperTrend Plotter Module
Single responsibility: SuperTrend visualization with Plotly
"""

import plotly.graph_objects as go
from typing import List

from ....core.types import IndicatorResult


class SuperTrendPlotter:
    """SuperTrend visualization using Plotly charts"""

    @staticmethod
    def plot(supertrend_results: List[IndicatorResult]) -> go.Figure:
        """
        Plot SuperTrend indicator

        Args:
            supertrend_results: List of SuperTrend calculation results

        Returns:
            Plotly figure with SuperTrend bands
        """
        if not supertrend_results:
            # Return empty figure if no data
            fig = go.Figure()
            fig.update_layout(
                title="SuperTrend Indicator",
                xaxis_title="Time",
                yaxis_title="Price",
                height=400
            )
            return fig

        # Extract data
        timestamps = [result.timestamp for result in supertrend_results]

        # SuperTrend typically returns upper and lower bands
        # We'll need to parse the result values accordingly
        upper_bands = []
        lower_bands = []

        for result in supertrend_results:
            # Assuming result.value contains band information
            # This may need adjustment based on actual SuperTrend implementation
            if hasattr(result, 'metadata') and result.metadata:
                upper_bands.append(float(result.metadata.get('upper_band', result.value)))
                lower_bands.append(float(result.metadata.get('lower_band', result.value)))
            else:
                # Fallback if no metadata
                upper_bands.append(float(result.value))
                lower_bands.append(float(result.value))

        # Create figure
        fig = go.Figure()

        # Add upper band
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=upper_bands,
            mode='lines',
            name='Upper Band',
            line=dict(color='red', width=2)
        ))

        # Add lower band
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=lower_bands,
            mode='lines',
            name='Lower Band',
            line=dict(color='green', width=2)
        ))

        # Update layout
        fig.update_layout(
            title="SuperTrend",
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
    def plot_with_signals(supertrend_results: List[IndicatorResult]) -> go.Figure:
        """
        Plot SuperTrend with trend signals

        Args:
            supertrend_results: List of SuperTrend calculation results with signals

        Returns:
            Plotly figure with SuperTrend and signals
        """
        fig = SuperTrendPlotter.plot(supertrend_results)

        if not supertrend_results:
            return fig

        # Extract signal data
        timestamps = [result.timestamp for result in supertrend_results]

        # Extract bands for signal plotting
        upper_bands = []
        lower_bands = []

        for result in supertrend_results:
            if hasattr(result, 'metadata') and result.metadata:
                upper_bands.append(float(result.metadata.get('upper_band', result.value)))
                lower_bands.append(float(result.metadata.get('lower_band', result.value)))
            else:
                upper_bands.append(float(result.value))
                lower_bands.append(float(result.value))

        buy_signals = []
        sell_signals = []
        trend_changes = []

        for i, result in enumerate(supertrend_results):
            if result.signals:
                for signal in result.signals:
                    if signal.direction.name == 'BUY':
                        buy_signals.append((timestamps[i], lower_bands[i]))
                    elif signal.direction.name == 'SELL':
                        sell_signals.append((timestamps[i], upper_bands[i]))
                    elif 'trend' in signal.direction.name.lower():
                        trend_changes.append((timestamps[i], (upper_bands[i] + lower_bands[i]) / 2))

        # Add buy signals (trend up)
        if buy_signals:
            buy_x, buy_y = zip(*buy_signals)
            fig.add_trace(go.Scatter(
                x=buy_x,
                y=buy_y,
                mode='markers',
                name='Bullish Trend',
                marker=dict(
                    symbol='triangle-up',
                    size=10,
                    color='green'
                )
            ))

        # Add sell signals (trend down)
        if sell_signals:
            sell_x, sell_y = zip(*sell_signals)
            fig.add_trace(go.Scatter(
                x=sell_x,
                y=sell_y,
                mode='markers',
                name='Bearish Trend',
                marker=dict(
                    symbol='triangle-down',
                    size=10,
                    color='red'
                )
            ))

        # Add trend change signals
        if trend_changes:
            change_x, change_y = zip(*trend_changes)
            fig.add_trace(go.Scatter(
                x=change_x,
                y=change_y,
                mode='markers',
                name='Trend Change',
                marker=dict(
                    symbol='diamond',
                    size=12,
                    color='blue'
                )
            ))

        return fig