"""
Phase 5.2 - Modern Indicator UI Components
Composants Dash pour intégration des indicateurs modernes au dashboard
"""

from typing import Dict, List, Optional, Any
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go

from src.thebot.core.logger import logger
from src.thebot.core.types import TimeFrame


class IndicatorSelector:
    """
    Composant pour sélectionner les indicateurs à afficher
    Dropdown avec tous les indicateurs disponibles
    """

    AVAILABLE_INDICATORS = {
        "basic": ["SMA", "EMA"],
        "oscillators": ["RSI"],
        "volatility": ["ATR"],
        "momentum": ["MACD", "SuperTrend", "Squeeze", "Breakout"],
        "volume": ["Volume Profile", "OBV"],
        "structural": ["FairValueGaps"],
    }

    TIMEFRAMES = [
        ("1m", TimeFrame.M1),
        ("5m", TimeFrame.M5),
        ("15m", TimeFrame.M15),
        ("1h", TimeFrame.H1),
        ("4h", TimeFrame.H4),
        ("1d", TimeFrame.D1),
    ]

    @staticmethod
    def create() -> dbc.Card:
        """
        Créer le composant de sélection d'indicateurs
        
        Returns:
            dbc.Card avec dropdown et paramètres
        """
        # Créer liste des indicateurs
        indicator_options = []
        for category, indicators in IndicatorSelector.AVAILABLE_INDICATORS.items():
            for indicator in indicators:
                indicator_options.append({
                    "label": f"{indicator} ({category})",
                    "value": f"{indicator}_{category}"
                })

        # Créer liste des timeframes
        timeframe_options = [
            {"label": label, "value": label}
            for label, _ in IndicatorSelector.TIMEFRAMES
        ]

        return dbc.Card(
            [
                dbc.CardHeader(
                    html.H5("📊 Indicateurs", className="mb-0"),
                    className="bg-primary text-white"
                ),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Sélectionner un indicateur:", 
                                     className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="indicator-selector",
                                options=indicator_options,
                                value="SMA_basic",
                                clearable=False,
                                className="w-100"
                            ),
                        ], lg=6),
                        dbc.Col([
                            html.Label("Timeframe:", 
                                     className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="timeframe-selector",
                                options=timeframe_options,
                                value="1h",
                                clearable=False,
                                className="w-100"
                            ),
                        ], lg=6),
                    ], className="mb-3"),
                    
                    # Paramètres de l'indicateur
                    dbc.Row([
                        dbc.Col([
                            html.Label("Paramètres:", 
                                     className="fw-bold mb-2"),
                            html.Div(
                                id="indicator-params",
                                children=[]
                            ),
                        ], lg=12),
                    ]),
                ]),
            ],
            className="mb-4"
        )


class IndicatorComparison:
    """
    Composant pour comparer plusieurs indicateurs côte à côte
    """

    @staticmethod
    def create() -> dbc.Card:
        """
        Créer le composant de comparaison
        
        Returns:
            dbc.Card avec multi-select et comparaison
        """
        indicator_options = []
        for category, indicators in IndicatorSelector.AVAILABLE_INDICATORS.items():
            for indicator in indicators:
                indicator_options.append({
                    "label": f"{indicator}",
                    "value": f"{indicator}_{category}"
                })

        return dbc.Card(
            [
                dbc.CardHeader(
                    html.H5("🔄 Comparaison d'Indicateurs", className="mb-0"),
                    className="bg-info text-white"
                ),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Sélectionner plusieurs indicateurs:", 
                                     className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="comparison-indicators",
                                options=indicator_options,
                                value=["SMA_basic", "EMA_basic"],
                                multi=True,
                                className="w-100"
                            ),
                        ], lg=12),
                    ], className="mb-3"),
                    
                    # Tableau de comparaison
                    html.Div(
                        id="comparison-table",
                        children=[]
                    ),
                ]),
            ],
            className="mb-4"
        )


class SignalAlertModal:
    """
    Modal pour afficher les signaux et alertes
    """

    @staticmethod
    def create() -> dbc.Modal:
        """
        Créer le modal d'alerte de signaux
        
        Returns:
            dbc.Modal avec signaux et alertes
        """
        return dbc.Modal(
            [
                dbc.ModalHeader(
                    html.H4("🚨 Signaux & Alertes", className="text-warning"),
                    close_button=True
                ),
                dbc.ModalBody([
                    html.Div(id="signals-content", children=[
                        html.P("Aucun signal pour le moment...", 
                               className="text-muted")
                    ]),
                ]),
                dbc.ModalFooter([
                    dbc.Button(
                        "Exporter Signaux",
                        id="export-signals-btn",
                        color="primary",
                        className="me-2"
                    ),
                    dbc.Button(
                        "Fermer",
                        id="close-signals-modal",
                        color="secondary",
                        className="ms-auto"
                    ),
                ]),
            ],
            id="signals-modal",
            size="lg",
            scrollable=True,
        )


class IndicatorMetrics:
    """
    Widget pour afficher les métriques d'un indicateur
    """

    @staticmethod
    def create(title: str = "📈 Métriques") -> dbc.Card:
        """
        Créer le widget de métriques
        
        Args:
            title: Titre du widget
            
        Returns:
            dbc.Card avec métriques
        """
        return dbc.Card(
            [
                dbc.CardHeader(
                    html.H5(title, className="mb-0"),
                    className="bg-success text-white"
                ),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.Span("Valeur Actuelle:", className="fw-bold"),
                                html.Br(),
                                html.Span(id="metric-current-value", 
                                        children="N/A",
                                        className="badge bg-info")
                            ])
                        ], lg=3),
                        dbc.Col([
                            html.Div([
                                html.Span("Variation (24h):", className="fw-bold"),
                                html.Br(),
                                html.Span(id="metric-change", 
                                        children="N/A",
                                        className="badge bg-success")
                            ])
                        ], lg=3),
                        dbc.Col([
                            html.Div([
                                html.Span("Signaux Today:", className="fw-bold"),
                                html.Br(),
                                html.Span(id="metric-signals-today", 
                                        children="0",
                                        className="badge bg-warning")
                            ])
                        ], lg=3),
                        dbc.Col([
                            html.Div([
                                html.Span("Dernière mise à jour:", className="fw-bold"),
                                html.Br(),
                                html.Span(id="metric-last-update", 
                                        children="N/A",
                                        className="badge bg-secondary")
                            ])
                        ], lg=3),
                    ]),
                ]),
            ],
            className="mb-4"
        )


class IndicatorChart:
    """
    Composant pour afficher les charts des indicateurs
    """

    @staticmethod
    def create(indicator_name: str = "SMA") -> dbc.Card:
        """
        Créer le composant de chart
        
        Args:
            indicator_name: Nom de l'indicateur
            
        Returns:
            dbc.Card avec chart
        """
        return dbc.Card(
            [
                dbc.CardHeader(
                    html.H5(f"📊 {indicator_name} Chart", className="mb-0"),
                    className="bg-dark text-white"
                ),
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-chart",
                        type="default",
                        children=[
                            dcc.Graph(
                                id="indicator-chart",
                                config={"responsive": True},
                                style={"height": "500px"}
                            )
                        ]
                    ),
                ]),
            ],
            className="mb-4"
        )


class SignalHistoryTable:
    """
    Tableau pour afficher l'historique des signaux
    """

    @staticmethod
    def create() -> dbc.Card:
        """
        Créer le tableau d'historique des signaux
        
        Returns:
            dbc.Card avec tableau
        """
        return dbc.Card(
            [
                dbc.CardHeader(
                    html.H5("📋 Historique des Signaux", className="mb-0"),
                    className="bg-warning text-dark"
                ),
                dbc.CardBody([
                    html.Div(
                        id="signals-history-table",
                        children=html.P("Chargement...", className="text-muted")
                    ),
                ]),
            ],
            className="mb-4"
        )


class IndicatorStatistics:
    """
    Widget pour afficher les statistiques des signaux
    """

    @staticmethod
    def create() -> dbc.Card:
        """
        Créer le widget de statistiques
        
        Returns:
            dbc.Card avec statistiques
        """
        return dbc.Card(
            [
                dbc.CardHeader(
                    html.H5("📊 Statistiques des Signaux", className="mb-0"),
                    className="bg-secondary text-white"
                ),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H6("Signaux UP ⬆️", className="text-success"),
                                html.H3(id="stat-signals-up", children="0")
                            ], className="text-center")
                        ], lg=3),
                        dbc.Col([
                            html.Div([
                                html.H6("Signaux DOWN ⬇️", className="text-danger"),
                                html.H3(id="stat-signals-down", children="0")
                            ], className="text-center")
                        ], lg=3),
                        dbc.Col([
                            html.Div([
                                html.H6("Ratio UP/DOWN", className="text-info"),
                                html.H3(id="stat-ratio", children="0%")
                            ], className="text-center")
                        ], lg=3),
                        dbc.Col([
                            html.Div([
                                html.H6("Puissance moyenne", className="text-primary"),
                                html.H3(id="stat-strength", children="0.0")
                            ], className="text-center")
                        ], lg=3),
                    ]),
                ]),
            ],
            className="mb-4"
        )


def create_full_indicator_dashboard() -> dbc.Container:
    """
    Créer le dashboard complet des indicateurs
    
    Returns:
        dbc.Container avec tous les composants
    """
    return dbc.Container(
        [
            dbc.Row([
                dbc.Col([
                    html.H1("🚀 Tableau de Bord des Indicateurs", 
                           className="mb-4 text-center text-primary")
                ], lg=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    IndicatorSelector.create()
                ], lg=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    IndicatorMetrics.create()
                ], lg=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    IndicatorChart.create()
                ], lg=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    IndicatorComparison.create()
                ], lg=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    IndicatorStatistics.create()
                ], lg=6),
                dbc.Col([
                    SignalHistoryTable.create()
                ], lg=6)
            ]),
            
            SignalAlertModal.create(),
        ],
        fluid=True,
        className="mt-5"
    )


logger.info("✅ Modern Indicator UI Components loaded")
