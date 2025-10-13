"""
Advanced Charts - Phase 3 THEBOT
Composants de graphiques avancés avec indicateurs techniques
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html
from plotly.subplots import make_subplots


class AdvancedCharts:
    """
    Générateur de graphiques avancés avec indicateurs techniques
    """

    def __init__(self):
        self.chart_types = {
            "candlestick": {
                "label": "🕯️ Chandelier",
                "description": "Graphique en chandeliers",
            },
            "line": {"label": "📈 Ligne", "description": "Graphique en ligne simple"},
            "area": {"label": "📊 Zone", "description": "Graphique en zone"},
            "ohlc": {"label": "📏 OHLC", "description": "Open-High-Low-Close"},
            "volume": {"label": "📦 Volume", "description": "Graphique de volume"},
        }

        self.timeframes = {
            "1m": {"label": "1 Min", "interval": 1, "unit": "minute"},
            "5m": {"label": "5 Min", "interval": 5, "unit": "minute"},
            "15m": {"label": "15 Min", "interval": 15, "unit": "minute"},
            "30m": {"label": "30 Min", "interval": 30, "unit": "minute"},
            "1h": {"label": "1 Heure", "interval": 1, "unit": "hour"},
            "4h": {"label": "4 Heures", "interval": 4, "unit": "hour"},
            "1d": {"label": "1 Jour", "interval": 1, "unit": "day"},
            "1w": {"label": "1 Semaine", "interval": 1, "unit": "week"},
        }

        self.indicators = {
            "sma": {
                "label": "SMA",
                "description": "Moyenne Mobile Simple",
                "params": ["period"],
            },
            "ema": {
                "label": "EMA",
                "description": "Moyenne Mobile Exponentielle",
                "params": ["period"],
            },
            "bollinger": {
                "label": "Bollinger",
                "description": "Bandes de Bollinger",
                "params": ["period", "std"],
            },
            "rsi": {
                "label": "RSI",
                "description": "Relative Strength Index",
                "params": ["period"],
            },
            "macd": {
                "label": "MACD",
                "description": "MACD Convergence Divergence",
                "params": ["fast", "slow", "signal"],
            },
            "volume_sma": {
                "label": "Volume SMA",
                "description": "Moyenne Mobile du Volume",
                "params": ["period"],
            },
            "support_resistance": {
                "label": "S/R",
                "description": "Support et Résistance",
                "params": ["lookback"],
            },
        }

        self.color_schemes = {
            "default": {
                "up": "#26a69a",
                "down": "#ef5350",
                "volume_up": "#26a69a",
                "volume_down": "#ef5350",
                "bg": "#ffffff",
                "grid": "#f0f0f0",
            },
            "dark": {
                "up": "#4caf50",
                "down": "#f44336",
                "volume_up": "#4caf50",
                "volume_down": "#f44336",
                "bg": "#2e2e2e",
                "grid": "#404040",
            },
            "crypto": {
                "up": "#f7931a",
                "down": "#8b5cf6",
                "volume_up": "#f7931a",
                "volume_down": "#8b5cf6",
                "bg": "#ffffff",
                "grid": "#f8f9fa",
            },
        }

    def create_advanced_chart_interface(self) -> html.Div:
        """Crée l'interface complète des graphiques avancés"""
        return html.Div(
            [
                # Contrôles du graphique
                self.create_chart_controls(),
                # Zone graphique principale
                html.Div(
                    [
                        dcc.Graph(
                            id="advanced-price-chart",
                            config={
                                "displayModeBar": True,
                                "displaylogo": False,
                                "modeBarButtonsToAdd": [
                                    "drawline",
                                    "drawopenpath",
                                    "drawclosedpath",
                                    "drawrect",
                                    "eraseshape",
                                ],
                            },
                            style={"height": "500px"},
                        )
                    ]
                ),
                # Panneaux d'indicateurs
                html.Div(id="indicators-panels"),
                # Panneau de configuration
                self.create_chart_settings_panel(),
                # Stores
                dcc.Store(id="chart-data-store"),
                dcc.Store(
                    id="chart-config-store",
                    data={
                        "symbol": "BTCUSDT",
                        "timeframe": "1h",
                        "chart_type": "candlestick",
                        "indicators": [],
                        "theme": "default",
                    },
                ),
            ]
        )

    def create_chart_controls(self) -> dbc.Card:
        """Crée les contrôles du graphique"""
        return dbc.Card(
            [
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                # Sélection symbole
                                dbc.Col(
                                    [
                                        dbc.Label("Symbole"),
                                        dbc.Select(
                                            id="chart-symbol-select",
                                            options=[
                                                {
                                                    "label": "BTC/USDT",
                                                    "value": "BTCUSDT",
                                                },
                                                {
                                                    "label": "ETH/USDT",
                                                    "value": "ETHUSDT",
                                                },
                                                {"label": "EUR/USD", "value": "EURUSD"},
                                                {"label": "GBP/USD", "value": "GBPUSD"},
                                            ],
                                            value="BTCUSDT",
                                        ),
                                    ],
                                    width=2,
                                ),
                                # Timeframe
                                dbc.Col(
                                    [
                                        dbc.Label("Période"),
                                        dbc.Select(
                                            id="chart-timeframe-select",
                                            options=[
                                                {"label": info["label"], "value": tf}
                                                for tf, info in self.timeframes.items()
                                            ],
                                            value="1h",
                                        ),
                                    ],
                                    width=2,
                                ),
                                # Type de graphique
                                dbc.Col(
                                    [
                                        dbc.Label("Type"),
                                        dbc.Select(
                                            id="chart-type-select",
                                            options=[
                                                {
                                                    "label": info["label"],
                                                    "value": chart_type,
                                                }
                                                for chart_type, info in self.chart_types.items()
                                            ],
                                            value="candlestick",
                                        ),
                                    ],
                                    width=2,
                                ),
                                # Indicateurs
                                dbc.Col(
                                    [
                                        dbc.Label("Indicateurs"),
                                        dbc.Checklist(
                                            id="chart-indicators-checklist",
                                            options=[
                                                {
                                                    "label": info["label"],
                                                    "value": indicator,
                                                }
                                                for indicator, info in self.indicators.items()
                                            ],
                                            value=[],
                                            inline=True,
                                        ),
                                    ],
                                    width=4,
                                ),
                                # Actions
                                dbc.Col(
                                    [
                                        dbc.Label("Actions"),
                                        dbc.ButtonGroup(
                                            [
                                                dbc.Button(
                                                    html.I(className="fas fa-sync"),
                                                    id="chart-refresh-btn",
                                                    color="primary",
                                                    size="sm",
                                                ),
                                                dbc.Button(
                                                    html.I(className="fas fa-cog"),
                                                    id="chart-settings-btn",
                                                    color="secondary",
                                                    size="sm",
                                                ),
                                                dbc.Button(
                                                    html.I(className="fas fa-download"),
                                                    id="chart-export-btn",
                                                    color="success",
                                                    size="sm",
                                                ),
                                            ]
                                        ),
                                    ],
                                    width=2,
                                ),
                            ]
                        )
                    ]
                )
            ],
            className="chart-controls mb-3",
        )

    def create_chart_settings_panel(self) -> dbc.Offcanvas:
        """Crée le panneau de paramètres"""
        return dbc.Offcanvas(
            [
                html.H4("Paramètres du Graphique"),
                html.Hr(),
                # Thème
                dbc.Label("Thème"),
                dbc.RadioItems(
                    id="chart-theme-radio",
                    options=[
                        {"label": "Défaut", "value": "default"},
                        {"label": "Sombre", "value": "dark"},
                        {"label": "Crypto", "value": "crypto"},
                    ],
                    value="default",
                ),
                html.Hr(),
                # Paramètres des indicateurs
                html.H5("Paramètres des Indicateurs"),
                html.Div(id="indicator-settings-container"),
                html.Hr(),
                # Options d'affichage
                html.H5("Options d'Affichage"),
                dbc.Checklist(
                    id="chart-display-options",
                    options=[
                        {"label": "Afficher le volume", "value": "show_volume"},
                        {"label": "Grille", "value": "show_grid"},
                        {"label": "Crosshair", "value": "show_crosshair"},
                        {"label": "Légende", "value": "show_legend"},
                    ],
                    value=["show_volume", "show_grid", "show_legend"],
                ),
            ],
            id="chart-settings-offcanvas",
            title="Paramètres",
            is_open=False,
        )

    def create_candlestick_chart(self, data: pd.DataFrame, config: Dict) -> go.Figure:
        """Crée un graphique en chandeliers"""
        if data.empty:
            return self.create_empty_chart("Aucune donnée disponible")

        theme = self.color_schemes.get(config.get("theme", "default"))

        # Créer subplots si des indicateurs nécessitent des panneaux séparés
        subplot_titles = ["Prix"]
        subplot_rows = 1

        indicators = config.get("indicators", [])
        if "rsi" in indicators:
            subplot_titles.append("RSI")
            subplot_rows += 1
        if "macd" in indicators:
            subplot_titles.append("MACD")
            subplot_rows += 1
        if "volume" in config.get("display_options", []) or "volume_sma" in indicators:
            subplot_titles.append("Volume")
            subplot_rows += 1

        # Créer la figure avec subplots
        fig = make_subplots(
            rows=subplot_rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=subplot_titles,
            row_heights=(
                [0.6] + [0.2] * (subplot_rows - 1) if subplot_rows > 1 else [1.0]
            ),
        )

        # Graphique principal - Chandeliers
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data["open"],
                high=data["high"],
                low=data["low"],
                close=data["close"],
                name="Prix",
                increasing_line_color=theme["up"],
                decreasing_line_color=theme["down"],
            ),
            row=1,
            col=1,
        )

        # Ajouter indicateurs sur le graphique principal
        current_row = 1
        if "sma" in indicators:
            sma_data = self.calculate_sma(data["close"], 20)
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=sma_data,
                    name="SMA(20)",
                    line=dict(color="blue", width=1),
                ),
                row=1,
                col=1,
            )

        if "ema" in indicators:
            ema_data = self.calculate_ema(data["close"], 20)
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=ema_data,
                    name="EMA(20)",
                    line=dict(color="orange", width=1),
                ),
                row=1,
                col=1,
            )

        if "bollinger" in indicators:
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(
                data["close"]
            )
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=bb_upper,
                    name="BB Upper",
                    line=dict(color="gray", width=1),
                    showlegend=False,
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=bb_lower,
                    name="BB Lower",
                    line=dict(color="gray", width=1),
                    fill="tonexty",
                    fillcolor="rgba(128,128,128,0.1)",
                    showlegend=False,
                ),
                row=1,
                col=1,
            )

        # Indicateurs dans des panneaux séparés
        current_row += 1

        if "rsi" in indicators and current_row <= subplot_rows:
            rsi_data = self.calculate_rsi(data["close"])
            fig.add_trace(
                go.Scatter(
                    x=data.index, y=rsi_data, name="RSI", line=dict(color="purple")
                ),
                row=current_row,
                col=1,
            )
            # Lignes de niveaux RSI
            fig.add_hline(
                y=70, line_dash="dash", line_color="red", row=current_row, col=1
            )
            fig.add_hline(
                y=30, line_dash="dash", line_color="green", row=current_row, col=1
            )
            current_row += 1

        if "macd" in indicators and current_row <= subplot_rows:
            macd_line, macd_signal, macd_histogram = self.calculate_macd(data["close"])
            fig.add_trace(
                go.Scatter(
                    x=data.index, y=macd_line, name="MACD", line=dict(color="blue")
                ),
                row=current_row,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=data.index, y=macd_signal, name="Signal", line=dict(color="red")
                ),
                row=current_row,
                col=1,
            )
            current_row += 1

        # Volume
        if (
            "show_volume" in config.get("display_options", [])
            and current_row <= subplot_rows
        ):
            colors = [
                theme["volume_up"] if close >= open_price else theme["volume_down"]
                for close, open_price in zip(data["close"], data["open"])
            ]

            fig.add_trace(
                go.Bar(
                    x=data.index, y=data["volume"], name="Volume", marker_color=colors
                ),
                row=current_row,
                col=1,
            )

        # Configuration du layout
        fig.update_layout(
            title=f"{config.get('symbol', 'Unknown')} - {config.get('timeframe', '1h')}",
            xaxis_rangeslider_visible=False,
            plot_bgcolor=theme["bg"],
            paper_bgcolor=theme["bg"],
            font=dict(color="black" if theme["bg"] == "#ffffff" else "white"),
            showlegend=config.get("show_legend", True),
            height=600,
        )

        # Configuration des axes
        fig.update_xaxes(
            showgrid=config.get("show_grid", True), gridcolor=theme["grid"]
        )
        fig.update_yaxes(
            showgrid=config.get("show_grid", True), gridcolor=theme["grid"]
        )

        return fig

    def create_empty_chart(self, message: str = "Aucune donnée") -> go.Figure:
        """Crée un graphique vide avec message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            plot_bgcolor="white",
            height=400,
        )
        return fig

    # Indicateurs techniques
    def calculate_sma(self, prices: pd.Series, period: int = 20) -> pd.Series:
        """Calcule la moyenne mobile simple"""
        return prices.rolling(window=period).mean()

    def calculate_ema(self, prices: pd.Series, period: int = 20) -> pd.Series:
        """Calcule la moyenne mobile exponentielle"""
        return prices.ewm(span=period).mean()

    def calculate_bollinger_bands(
        self, prices: pd.Series, period: int = 20, std: float = 2
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calcule les bandes de Bollinger"""
        sma = prices.rolling(window=period).mean()
        rolling_std = prices.rolling(window=period).std()

        upper_band = sma + (rolling_std * std)
        lower_band = sma - (rolling_std * std)

        return upper_band, sma, lower_band

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcule le RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def calculate_macd(
        self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calcule le MACD en utilisant le module dédié"""
        try:
            from src.thebot.indicators.momentum.macd import MACD, MACDConfig

            config = MACDConfig(
                fast_period=fast, slow_period=slow, signal_period=signal, source="close"
            )

            macd_calculator = MACD(config)

            # Préparer DataFrame au format attendu
            data = pd.DataFrame(
                {
                    "open": prices,
                    "high": prices * 1.01,
                    "low": prices * 0.99,
                    "close": prices,
                    "volume": [1000] * len(prices),
                }
            )

            result = macd_calculator.calculate(data, include_signals=False)

            # Extraire les données et convertir en Series
            result_data = result["data"]
            macd_line = pd.Series(result_data["macd"], index=prices.index)
            signal_line = pd.Series(result_data["signal"], index=prices.index)
            histogram = pd.Series(result_data["histogram"], index=prices.index)

            return macd_line, signal_line, histogram

        except Exception as e:
            print(f"Erreur MACD module: {e}")
            # Fallback vers ancienne méthode
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()

            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line

            return macd_line, signal_line, histogram

    def detect_support_resistance(self, data: pd.DataFrame, lookback: int = 20) -> Dict:
        """Détecte les niveaux de support et résistance"""
        highs = data["high"].rolling(window=lookback).max()
        lows = data["low"].rolling(window=lookback).min()

        # Simplification: prendre les niveaux les plus récents
        resistance_levels = highs.dropna().tail(5).unique()
        support_levels = lows.dropna().tail(5).unique()

        return {"resistance": resistance_levels, "support": support_levels}


# Instance globale
advanced_charts = AdvancedCharts()
