"""
Volume Profile Plotter Module
Single responsibility: Volume Profile visualization with Plotly
"""

import plotly.graph_objects as go
from typing import List, Dict, Any, Optional

from ....core.types import IndicatorResult


class VolumeProfilePlotter:
    """Volume Profile visualization using Plotly charts"""

    @staticmethod
    def plot(volume_profile_results: List[IndicatorResult]) -> go.Figure:
        """
        Plot volume profile with POC and Value Area

        Args:
            volume_profile_results: List of volume profile calculation results

        Returns:
            Plotly figure with volume profile analysis
        """
        if not volume_profile_results:
            fig = go.Figure()
            fig.update_layout(
                title="Volume Profile",
                xaxis_title="Volume",
                yaxis_title="Price",
                height=600
            )
            return fig

        # Extract the most recent result for visualization
        latest_result = volume_profile_results[-1]

        if not hasattr(latest_result, 'metadata') or not latest_result.metadata:
            fig = go.Figure()
            fig.update_layout(title="Volume Profile - No Data")
            return fig

        metadata = latest_result.metadata

        # Extract volume nodes
        nodes = metadata.get('nodes', [])
        if not nodes:
            fig = go.Figure()
            fig.update_layout(title="Volume Profile - No Volume Nodes")
            return fig

        # Extract POC and Value Area
        poc_price = metadata.get('poc', {}).get('price_level', 0)
        value_area = metadata.get('value_area', {})
        va_high = value_area.get('high', 0)
        va_low = value_area.get('low', 0)

        # Prepare data for horizontal bar chart
        prices = [node.get('price_level', 0) for node in nodes]
        volumes = [node.get('volume', 0) for node in nodes]
        volume_percents = [node.get('volume_percent', 0) for node in nodes]

        # Sort by price for better visualization
        sorted_data = sorted(zip(prices, volumes, volume_percents))
        prices, volumes, volume_percents = [list(t) for t in zip(*sorted_data)]

        # Create subplot figure (volume bars + price line)
        fig = go.Figure()

        # Add volume bars (horizontal)
        fig.add_trace(go.Bar(
            x=volumes,
            y=prices,
            orientation='h',
            name='Volume',
            marker=dict(
                color='lightblue',
                opacity=0.7
            ),
            width=0.01  # Thin bars
        ))

        # Update layout for horizontal bars
        fig.update_layout(
            title="Volume Profile Analysis",
            xaxis_title="Volume",
            yaxis_title="Price Level",
            height=600,
            showlegend=True,
            bargap=0.1
        )

        # Add POC line
        if poc_price > 0:
            fig.add_trace(go.Scatter(
                x=[0, max(volumes) * 0.1],  # Short horizontal line at POC level
                y=[poc_price, poc_price],
                mode='lines',
                name='POC (Point of Control)',
                line=dict(color='red', width=3, dash='solid')
            ))

        # Add Value Area rectangle
        if va_high > 0 and va_low > 0:
            fig.add_shape(
                type="rect",
                x0=0,
                y0=va_low,
                x1=max(volumes) * 0.05,
                y1=va_high,
                fillcolor="rgba(0, 255, 0, 0.2)",
                line=dict(color="green", width=2),
                name="Value Area (70%)"
            )

            # Add Value Area label
            fig.add_annotation(
                x=max(volumes) * 0.025,
                y=(va_high + va_low) / 2,
                text="Value Area",
                showarrow=False,
                font=dict(color="green", size=12)
            )

        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

        return fig

    @staticmethod
    def plot_with_price(volume_profile_results: List[IndicatorResult],
                       price_data: Optional[List[float]] = None) -> go.Figure:
        """
        Plot volume profile alongside price chart

        Args:
            volume_profile_results: List of volume profile results
            price_data: Recent price data for context

        Returns:
            Subplot figure with volume profile and price
        """
        from plotly.subplots import make_subplots

        if not volume_profile_results:
            fig = go.Figure()
            fig.update_layout(title="Volume Profile + Price")
            return fig

        # Create subplot
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Volume Profile', 'Price Context'),
            column_widths=[0.4, 0.6]
        )

        # Add volume profile to first subplot
        vp_fig = VolumeProfilePlotter.plot(volume_profile_results)

        # Copy traces to subplot
        for trace in vp_fig.data:
            fig.add_trace(trace, row=1, col=1)

        # Add price data to second subplot
        if price_data:
            timestamps = list(range(len(price_data)))
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=price_data,
                    mode='lines',
                    name='Price',
                    line=dict(color='blue', width=2)
                ),
                row=1, col=2
            )

        # Update layout
        fig.update_layout(
            title="Volume Profile & Price Analysis",
            height=500,
            showlegend=True
        )

        # Update subplot axes
        fig.update_xaxes(title_text="Volume", row=1, col=1)
        fig.update_yaxes(title_text="Price Level", row=1, col=1)
        fig.update_xaxes(title_text="Time", row=1, col=2)
        fig.update_yaxes(title_text="Price", row=1, col=2)

        return fig