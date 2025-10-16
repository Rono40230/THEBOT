from src.thebot.core.logger import logger
"""
Base Market Module for THEBOT
Provides common interface for Crypto, Forex, and Stocks markets
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from plotly.subplots import make_subplots


class BaseMarketModule(ABC):
    """
    Abstract base class for market modules (Crypto, Forex, Stocks)
    Provides common interface and functionality
    """

    def __init__(self, market_type: str, data_provider: Any, calculators: Dict = None):
        self.market_type = market_type  # 'crypto', 'forex', 'stocks'
        self.data_provider = data_provider
        self.calculators = calculators or {}
        self.current_symbol = None
        self.current_data = pd.DataFrame()

    @abstractmethod
    def get_symbols_list(self) -> List[str]:
        """Get available symbols for this market"""
        pass

    @abstractmethod
    def load_market_data(
        self, symbol: str, interval: str = "1h", limit: int = 200
    ) -> pd.DataFrame:
        """Load market data for given symbol"""
        pass

    @abstractmethod
    def get_default_symbol(self) -> str:
        """Get default symbol for this market"""
        pass

    def format_price_adaptive(self, price: float) -> str:
        """Format price according to market type and value"""
        if self.market_type == "crypto":
            # Utiliser le formatage adaptatif centralisé pour crypto
            from dash_modules.core.price_formatter import format_crypto_price_adaptive

            formatted = format_crypto_price_adaptive(price)
            # Enlever le symbole $ car cette fonction ne doit retourner que le nombre
            return formatted[1:] if formatted.startswith("$") else formatted
        elif self.market_type == "forex":
            # Forex typically 4-5 decimal places
            return f"{price:.5f}"
        else:  # stocks
            # Stocks typically 2 decimal places
            return f"{price:.2f}"

    def calculate_technical_indicators(
        self,
        data: pd.DataFrame,
        sma_enabled: bool = False,
        sma_period: int = 20,
        ema_enabled: bool = False,
        ema_period: int = 12,
        rsi_enabled: bool = False,
        rsi_period: int = 14,
        atr_enabled: bool = False,
        atr_period: int = 14,
    ) -> Dict:
        """Calculate technical indicators for the data"""
        indicators = {}

        if data.empty:
            return indicators

        prices = data["close"].tolist()

        if sma_enabled and sma_period and len(prices) >= sma_period:
            indicators["sma"] = self.calculate_sma(prices, sma_period)

        if ema_enabled and ema_period and len(prices) >= ema_period:
            indicators["ema"] = self.calculate_ema(prices, ema_period)

        if rsi_enabled and rsi_period and len(prices) >= rsi_period:
            indicators["rsi"] = self.calculate_rsi(prices, rsi_period)

        if atr_enabled and atr_period and len(data) >= atr_period:
            indicators["atr"] = self.calculate_atr(data, atr_period)

        return indicators

    def calculate_sma(self, prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return [0] * len(prices)

        sma_values = []
        for i in range(len(prices)):
            if i < period - 1:
                sma_values.append(0)
            else:
                avg = sum(prices[i - period + 1 : i + 1]) / period
                sma_values.append(avg)

        return sma_values

    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return [0] * len(prices)

        multiplier = 2 / (period + 1)
        ema_values = [0] * (period - 1)

        # First EMA value is SMA
        ema_values.append(sum(prices[:period]) / period)

        # Calculate subsequent EMA values
        for i in range(period, len(prices)):
            ema = (prices[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)

        return ema_values

    def calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return [50] * len(prices)

        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        gains = [max(0, delta) for delta in deltas]
        losses = [max(0, -delta) for delta in deltas]

        rsi_values = [50]  # First value

        # Calculate initial averages
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period

            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            rsi_values.append(rsi)

        # Pad beginning with 50s
        return [50] * (len(prices) - len(rsi_values)) + rsi_values

    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> List[float]:
        """Calculate Average True Range"""
        if len(data) < period:
            return [0] * len(data)

        high = data["high"]
        low = data["low"]
        close = data["close"]
        prev_close = close.shift(1)

        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)

        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr.fillna(0).tolist()

    def create_price_chart(
        self, data: pd.DataFrame, symbol: str, indicators: Dict = None
    ) -> go.Figure:
        """Create price chart with indicators"""
        if data.empty:
            return go.Figure()

        fig = go.Figure()

        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data["open"],
                high=data["high"],
                low=data["low"],
                close=data["close"],
                name=symbol,
                increasing_line_color="#00ff88",
                decreasing_line_color="#ff4444",
            )
        )

        # Add current price line
        if not data.empty:
            current_price = data["close"].iloc[-1]
            formatted_price = self.format_price_adaptive(current_price)
            fig.add_hline(
                y=current_price,
                line_dash="dot",
                line_color="#FFD700",
                line_width=2,
                opacity=0.8,
                annotation_text=f"Prix actuel: ${formatted_price}",
                annotation_position="bottom right",
                annotation=dict(
                    font=dict(color="#FFD700", size=12),
                    bgcolor="rgba(0,0,0,0.7)",
                    bordercolor="#FFD700",
                    borderwidth=1,
                ),
            )

        # Add technical indicators
        if indicators:
            if "sma" in indicators and any(indicators["sma"]):
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=indicators["sma"],
                        mode="lines",
                        name="SMA",
                        line=dict(color="orange", width=2),
                    )
                )

            if "ema" in indicators and any(indicators["ema"]):
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=indicators["ema"],
                        mode="lines",
                        name="EMA",
                        line=dict(color="cyan", width=2),
                    )
                )

        # Update layout
        fig.update_layout(
            title=f"{symbol} | 📊 {self.market_type.title()} Analysis",
            xaxis_title="Time",
            yaxis_title="Price",
            template="plotly_dark",
            height=500,
            showlegend=True,
            legend=dict(x=0, y=1),
            margin=dict(l=0, r=0, t=40, b=0),
        )

        fig.update_xaxes(rangeslider_visible=False)

        return fig

    def create_rsi_chart(
        self, data: pd.DataFrame, symbol: str, rsi_values: List[float] = None
    ) -> go.Figure:
        """Create RSI indicator chart"""
        if data.empty:
            return go.Figure()

        fig = go.Figure()

        if rsi_values and any(rsi_values):
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=rsi_values,
                    mode="lines",
                    name="RSI",
                    line=dict(color="purple", width=2),
                )
            )

            # Add RSI levels
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.7)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.7)
            fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1)
            fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1)

        fig.update_layout(
            title=f"RSI - {symbol}",
            xaxis_title="Time",
            yaxis_title="RSI",
            template="plotly_dark",
            height=200,
            showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0),
            yaxis=dict(range=[0, 100]),
        )

        return fig

    def create_volume_chart(self, data: pd.DataFrame, symbol: str) -> go.Figure:
        """Create volume chart"""
        if data.empty or "volume" not in data.columns:
            return go.Figure()

        fig = go.Figure()

        colors = [
            "green" if data["close"].iloc[i] >= data["open"].iloc[i] else "red"
            for i in range(len(data))
        ]

        fig.add_trace(
            go.Bar(x=data.index, y=data["volume"], name="Volume", marker_color=colors)
        )

        fig.update_layout(
            title=f"Volume - {symbol}",
            xaxis_title="Time",
            yaxis_title="Volume",
            template="plotly_dark",
            height=200,
            showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0),
        )

        return fig

    def create_atr_chart(
        self, data: pd.DataFrame, symbol: str, atr_values: List[float] = None
    ) -> go.Figure:
        """Create ATR indicator chart"""
        if data.empty:
            return go.Figure()

        fig = go.Figure()

        if atr_values and any(atr_values):
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=atr_values,
                    mode="lines",
                    name="ATR",
                    line=dict(color="orange", width=2),
                )
            )

            # Add trend lines if enabled
            if len(atr_values) > 20:
                # Simple trend line
                x_numeric = list(range(len(atr_values)))
                z = np.polyfit(x_numeric, atr_values, 1)
                p = np.poly1d(z)
                trend_line = p(x_numeric)

                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=trend_line,
                        mode="lines",
                        name="ATR Trend",
                        line=dict(color="yellow", width=1, dash="dash"),
                        opacity=0.7,
                    )
                )

        fig.update_layout(
            title=f"ATR - {symbol}",
            xaxis_title="Time",
            yaxis_title="ATR",
            template="plotly_dark",
            height=200,
            showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0),
        )

        return fig

    def get_market_layout(self) -> html.Div:
        """Get the complete market layout (charts + controls)"""
        return html.Div(
            [
                # Charts section
                dbc.Row(
                    [
                        dbc.Col(
                            [dcc.Graph(id=f"{self.market_type}-price-chart")], width=12
                        )
                    ],
                    className="mb-3",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [dcc.Graph(id=f"{self.market_type}-rsi-chart")], width=4
                        ),
                        dbc.Col(
                            [dcc.Graph(id=f"{self.market_type}-volume-chart")], width=4
                        ),
                        dbc.Col(
                            [dcc.Graph(id=f"{self.market_type}-atr-chart")], width=4
                        ),
                    ],
                    className="mb-3",
                ),
                # AI Insights section
                html.Div(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    label="🧠 AI Insights",
                                    tab_id=f"{self.market_type}-ai-tab",
                                    children=[
                                        html.Div(
                                            [self.create_ai_dashboard()],
                                            className="p-3",
                                        )
                                    ],
                                )
                            ],
                            id=f"{self.market_type}-secondary-tabs",
                            active_tab=f"{self.market_type}-ai-tab",
                            className="custom-tabs mt-3",
                        )
                    ],
                    className="p-3",
                ),
            ]
        )

    def create_ai_dashboard(self) -> html.Div:
        """Create AI insights dashboard for this market"""
        market_context = {
            "crypto": {
                "sentiment_example": "Bullish",
                "confidence": "78%",
                "prediction": "+12.5%",
                "analysis": "Strong momentum with high volume confirmation",
            },
            "forex": {
                "sentiment_example": "Neutral",
                "confidence": "65%",
                "prediction": "+2.1%",
                "analysis": "Consolidation phase with economic data pending",
            },
            "stocks": {
                "sentiment_example": "Bullish",
                "confidence": "72%",
                "prediction": "+8.3%",
                "analysis": "Positive earnings outlook with sector rotation",
            },
        }

        context = market_context.get(self.market_type, market_context["crypto"])

        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.I(
                                                    className="fas fa-trend-up me-2"
                                                ),
                                                "Market Sentiment",
                                            ]
                                        ),
                                        dbc.CardBody(
                                            [
                                                html.H3(
                                                    context["sentiment_example"],
                                                    className="text-success",
                                                ),
                                                html.P(
                                                    f"Confidence: {context['confidence']}",
                                                    className="text-muted",
                                                ),
                                                dcc.Graph(
                                                    figure=px.pie(
                                                        values=[78, 22],
                                                        names=["Bullish", "Bearish"],
                                                        color_discrete_map={
                                                            "Bullish": "#28a745",
                                                            "Bearish": "#dc3545",
                                                        },
                                                        title=f"{self.market_type.title()} Sentiment",
                                                    ).update_layout(
                                                        template="plotly_dark",
                                                        height=200,
                                                        showlegend=False,
                                                    )
                                                ),
                                            ]
                                        ),
                                    ]
                                )
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.I(
                                                    className="fas fa-chart-line me-2"
                                                ),
                                                "Price Prediction",
                                            ]
                                        ),
                                        dbc.CardBody(
                                            [
                                                html.H3(
                                                    context["prediction"],
                                                    className="text-info",
                                                ),
                                                html.P(
                                                    "Next 24h forecast",
                                                    className="text-muted",
                                                ),
                                                dcc.Graph(
                                                    figure=go.Figure(
                                                        go.Indicator(
                                                            mode="gauge+number",
                                                            value=float(
                                                                context["prediction"]
                                                                .replace("%", "")
                                                                .replace("+", "")
                                                            ),
                                                            domain={
                                                                "x": [0, 1],
                                                                "y": [0, 1],
                                                            },
                                                            title={"text": "Forecast"},
                                                            gauge={
                                                                "axis": {
                                                                    "range": [-20, 20]
                                                                },
                                                                "bar": {
                                                                    "color": "darkblue"
                                                                },
                                                                "steps": [
                                                                    {
                                                                        "range": [
                                                                            -20,
                                                                            0,
                                                                        ],
                                                                        "color": "lightgray",
                                                                    },
                                                                    {
                                                                        "range": [
                                                                            0,
                                                                            20,
                                                                        ],
                                                                        "color": "gray",
                                                                    },
                                                                ],
                                                                "threshold": {
                                                                    "line": {
                                                                        "color": "red",
                                                                        "width": 4,
                                                                    },
                                                                    "thickness": 0.75,
                                                                    "value": 15,
                                                                },
                                                            },
                                                        )
                                                    ).update_layout(
                                                        template="plotly_dark",
                                                        height=200,
                                                    )
                                                ),
                                            ]
                                        ),
                                    ]
                                )
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            [
                                                html.I(className="fas fa-brain me-2"),
                                                "Technical Analysis",
                                            ]
                                        ),
                                        dbc.CardBody(
                                            [
                                                html.H6(
                                                    "AI Analysis",
                                                    className="text-warning",
                                                ),
                                                html.P(
                                                    context["analysis"],
                                                    className="small",
                                                ),
                                                html.Hr(),
                                                html.H6(
                                                    "Key Levels", className="text-info"
                                                ),
                                                html.P(
                                                    "Support: $0.00875",
                                                    className="small text-success",
                                                ),
                                                html.P(
                                                    "Resistance: $0.00920",
                                                    className="small text-danger",
                                                ),
                                                html.Hr(),
                                                html.H6(
                                                    "Recommendation",
                                                    className="text-primary",
                                                ),
                                                html.P(
                                                    "Hold position with tight stop-loss",
                                                    className="small",
                                                ),
                                            ]
                                        ),
                                    ]
                                )
                            ],
                            width=4,
                        ),
                    ]
                )
            ]
        )

    def update_market_data(self, symbol: str, interval: str = "1h") -> Dict[str, Any]:
        """Update market data and return processed information"""
        try:
            # Load new data
            data = self.load_market_data(symbol, interval)

            if data.empty:
                return {"error": f"No data available for {symbol}"}

            self.current_symbol = symbol
            self.current_data = data

            return {
                "symbol": symbol,
                "data": data.to_json(),
                "last_update": datetime.now().isoformat(),
                "points_count": len(data),
            }

        except Exception as e:
            logger.info(f"❌ Error updating {self.market_type} data for {symbol}: {e}")
            return {"error": str(e)}
