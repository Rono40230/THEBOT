"""
Advanced Dashboard - Phase 3 THEBOT
Dashboard unifié responsive avec widgets redimensionnables
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, callback, clientside_callback, dcc, html


class AdvancedDashboard:
    """
    Dashboard avancé avec widgets personnalisables et layout responsive
    """

    def __init__(self):
        self.default_layout = {
            "market_overview": {"x": 0, "y": 0, "w": 12, "h": 6},
            "news_feed": {"x": 0, "y": 6, "w": 6, "h": 8},
            "price_charts": {"x": 6, "y": 6, "w": 6, "h": 8},
            "alerts": {"x": 0, "y": 14, "w": 12, "h": 4},
        }

        self.widget_catalog = {
            "market_overview": {
                "title": "📊 Vue d'ensemble Marchés",
                "description": "Performance temps réel multi-marchés",
                "min_size": {"w": 6, "h": 4},
            },
            "news_feed": {
                "title": "📰 Actualités RSS",
                "description": "Feed RSS en temps réel",
                "min_size": {"w": 4, "h": 6},
            },
            "price_charts": {
                "title": "📈 Graphiques Prix",
                "description": "Charts interactifs avancés",
                "min_size": {"w": 6, "h": 6},
            },
            "alerts": {
                "title": "🔔 Alertes",
                "description": "Système d'alertes configurables",
                "min_size": {"w": 6, "h": 3},
            },
            "portfolio": {
                "title": "💼 Portfolio",
                "description": "Suivi portefeuille",
                "min_size": {"w": 4, "h": 4},
            },
            "technical_analysis": {
                "title": "🔍 Analyse Technique",
                "description": "Indicateurs techniques",
                "min_size": {"w": 6, "h": 5},
            },
        }

    def create_layout(self, user_layout: Dict = None) -> html.Div:
        """Crée le layout principal du dashboard"""
        layout = user_layout or self.default_layout

        return html.Div(
            [
                # Header du dashboard
                self.create_header(),
                # Toolbar de configuration
                self.create_toolbar(),
                # Zone de widgets
                html.Div(
                    id="dashboard-container",
                    children=self.create_widgets(layout),
                    className="dashboard-grid",
                ),
                # CSS et JavaScript pour le drag & drop
                self.create_dashboard_styles(),
                # Store pour sauvegarder le layout
                dcc.Store(id="dashboard-layout-store", data=layout),
                dcc.Store(id="dashboard-config-store", data={"theme": "light"}),
                # Interval pour auto-refresh
                dcc.Interval(
                    id="dashboard-refresh-interval",
                    interval=30 * 1000,  # 30 secondes
                    n_intervals=0,
                ),
            ]
        )

    def create_header(self) -> dbc.Container:
        """Crée l'en-tête du dashboard"""
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H1(
                                    [
                                        html.I(className="fas fa-chart-line me-2"),
                                        "THEBOT Dashboard Pro",
                                    ],
                                    className="dashboard-title",
                                ),
                                html.P(
                                    f"Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}",
                                    id="last-update-time",
                                    className="text-muted small",
                                ),
                            ],
                            width=8,
                        ),
                        dbc.Col(
                            [
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button(
                                            [
                                                html.I(className="fas fa-plus"),
                                                " Widget",
                                            ],
                                            id="add-widget-btn",
                                            color="primary",
                                            size="sm",
                                        ),
                                        dbc.Button(
                                            [html.I(className="fas fa-cog"), " Config"],
                                            id="config-btn",
                                            color="secondary",
                                            size="sm",
                                        ),
                                        dbc.Button(
                                            [
                                                html.I(className="fas fa-save"),
                                                " Sauver",
                                            ],
                                            id="save-layout-btn",
                                            color="success",
                                            size="sm",
                                        ),
                                    ]
                                )
                            ],
                            width=4,
                            className="text-end",
                        ),
                    ]
                )
            ],
            fluid=True,
            className="dashboard-header",
        )

    def create_toolbar(self) -> dbc.Container:
        """Crée la barre d'outils"""
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button(
                                            "🌙",
                                            id="theme-toggle",
                                            color="outline-secondary",
                                            size="sm",
                                        ),
                                        dbc.Button(
                                            "📱",
                                            id="mobile-view",
                                            color="outline-info",
                                            size="sm",
                                        ),
                                        dbc.Button(
                                            "🖥️",
                                            id="desktop-view",
                                            color="outline-info",
                                            size="sm",
                                        ),
                                        dbc.Button(
                                            "🔄",
                                            id="refresh-all",
                                            color="outline-warning",
                                            size="sm",
                                        ),
                                    ]
                                )
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Select(
                                    id="quick-layout-select",
                                    options=[
                                        {
                                            "label": "Layout par défaut",
                                            "value": "default",
                                        },
                                        {"label": "Focus Trading", "value": "trading"},
                                        {"label": "Focus News", "value": "news"},
                                        {"label": "Vue Mobile", "value": "mobile"},
                                    ],
                                    value="default",
                                    size="sm",
                                )
                            ],
                            width=6,
                        ),
                    ]
                )
            ],
            fluid=True,
            className="dashboard-toolbar",
        )

    def create_widgets(self, layout: Dict) -> List:
        """Crée les widgets selon le layout"""
        widgets = []

        for widget_id, config in layout.items():
            if widget_id in self.widget_catalog:
                widget = self.create_widget(widget_id, config)
                widgets.append(widget)

        return widgets

    def create_widget(self, widget_id: str, config: Dict) -> dbc.Card:
        """Crée un widget individual"""
        widget_info = self.widget_catalog[widget_id]

        return dbc.Card(
            [
                dbc.CardHeader(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H5(
                                            widget_info["title"],
                                            className="card-title mb-0",
                                        )
                                    ],
                                    width=8,
                                ),
                                dbc.Col(
                                    [
                                        dbc.ButtonGroup(
                                            [
                                                dbc.Button(
                                                    html.I(
                                                        className="fas fa-expand-arrows-alt"
                                                    ),
                                                    id=f"resize-{widget_id}",
                                                    color="link",
                                                    size="sm",
                                                ),
                                                dbc.Button(
                                                    html.I(className="fas fa-times"),
                                                    id=f"close-{widget_id}",
                                                    color="link",
                                                    size="sm",
                                                    className="text-danger",
                                                ),
                                            ]
                                        )
                                    ],
                                    width=4,
                                    className="text-end",
                                ),
                            ]
                        )
                    ]
                ),
                dbc.CardBody(
                    [
                        html.Div(
                            id=f"widget-content-{widget_id}",
                            children=self.get_widget_content(widget_id),
                            className="widget-content",
                        )
                    ]
                ),
            ],
            id=f"widget-{widget_id}",
            className=f"dashboard-widget widget-{widget_id}",
            style={
                "gridColumnStart": config.get("x", 0) + 1,
                "gridColumnEnd": config.get("x", 0) + config.get("w", 6) + 1,
                "gridRowStart": config.get("y", 0) + 1,
                "gridRowEnd": config.get("y", 0) + config.get("h", 4) + 1,
            },
        )

    def get_widget_content(self, widget_id: str) -> html.Div:
        """Retourne le contenu d'un widget spécifique"""
        if widget_id == "market_overview":
            return self.create_market_overview_widget()
        elif widget_id == "news_feed":
            return self.create_news_feed_widget()
        elif widget_id == "price_charts":
            return self.create_price_charts_widget()
        elif widget_id == "alerts":
            return self.create_alerts_widget()
        elif widget_id == "portfolio":
            return self.create_portfolio_widget()
        elif widget_id == "technical_analysis":
            return self.create_technical_analysis_widget()
        else:
            return html.Div("Widget non implémenté", className="text-muted")

    def create_market_overview_widget(self) -> html.Div:
        """Widget vue d'ensemble des marchés"""
        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "📈 Crypto",
                                                    className="text-success",
                                                ),
                                                html.H2(
                                                    id="crypto-index",
                                                    children="Loading...",
                                                    className="text-success",
                                                ),
                                                html.Small(
                                                    id="crypto-change",
                                                    className="text-muted",
                                                ),
                                            ]
                                        )
                                    ],
                                    color="light",
                                )
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "💱 Forex", className="text-info"
                                                ),
                                                html.H2(
                                                    id="forex-index",
                                                    children="Loading...",
                                                    className="text-info",
                                                ),
                                                html.Small(
                                                    id="forex-change",
                                                    className="text-muted",
                                                ),
                                            ]
                                        )
                                    ],
                                    color="light",
                                )
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "📊 Stocks",
                                                    className="text-primary",
                                                ),
                                                html.H2(
                                                    id="stocks-index",
                                                    children="Loading...",
                                                    className="text-primary",
                                                ),
                                                html.Small(
                                                    id="stocks-change",
                                                    className="text-muted",
                                                ),
                                            ]
                                        )
                                    ],
                                    color="light",
                                )
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "📰 News", className="text-warning"
                                                ),
                                                html.H2(
                                                    id="news-count",
                                                    children="Loading...",
                                                    className="text-warning",
                                                ),
                                                html.Small(
                                                    "Articles récents",
                                                    className="text-muted",
                                                ),
                                            ]
                                        )
                                    ],
                                    color="light",
                                )
                            ],
                            width=3,
                        ),
                    ]
                ),
                html.Hr(),
                # Graphique de performance comparative
                dcc.Graph(id="market-overview-chart", config={"displayModeBar": False}),
            ]
        )

    def create_news_feed_widget(self) -> html.Div:
        """Widget feed d'actualités"""
        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.InputGroup(
                                    [
                                        dbc.Input(
                                            placeholder="Rechercher news...",
                                            id="news-search-input",
                                        ),
                                        dbc.Button(
                                            html.I(className="fas fa-search"),
                                            id="news-search-btn",
                                            color="primary",
                                        ),
                                    ]
                                )
                            ],
                            width=8,
                        ),
                        dbc.Col(
                            [
                                dbc.Select(
                                    id="news-category-filter",
                                    options=[
                                        {"label": "Toutes", "value": "all"},
                                        {"label": "Crypto", "value": "crypto"},
                                        {"label": "Économie", "value": "economic"},
                                        {"label": "Marchés", "value": "market"},
                                    ],
                                    value="all",
                                    size="sm",
                                )
                            ],
                            width=4,
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(
                    id="news-feed-content",
                    children=[
                        dbc.Spinner(
                            html.Div("Chargement des actualités..."), color="primary"
                        )
                    ],
                    className="news-feed-container",
                ),
            ]
        )

    def create_price_charts_widget(self) -> html.Div:
        """Widget graphiques de prix"""
        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Select(
                                    id="chart-symbol-select",
                                    options=[
                                        {"label": "BTC/USDT", "value": "BTCUSDT"},
                                        {"label": "ETH/USDT", "value": "ETHUSDT"},
                                        {"label": "EUR/USD", "value": "EURUSD"},
                                    ],
                                    value="BTCUSDT",
                                )
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Select(
                                    id="chart-timeframe-select",
                                    options=[
                                        {"label": "1H", "value": "1h"},
                                        {"label": "4H", "value": "4h"},
                                        {"label": "1D", "value": "1d"},
                                    ],
                                    value="1h",
                                )
                            ],
                            width=6,
                        ),
                    ],
                    className="mb-3",
                ),
                dcc.Graph(id="price-chart", config={"displayModeBar": True}),
            ]
        )

    def create_alerts_widget(self) -> html.Div:
        """Widget système d'alertes"""
        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-plus"),
                                        " Nouvelle Alerte",
                                    ],
                                    id="new-alert-btn",
                                    color="primary",
                                    size="sm",
                                )
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Badge(
                                    id="active-alerts-count",
                                    children="0 alertes actives",
                                    color="info",
                                )
                            ],
                            width=6,
                            className="text-end",
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(
                    id="alerts-list",
                    children=[
                        html.P(
                            "Aucune alerte configurée",
                            className="text-muted text-center",
                        )
                    ],
                ),
            ]
        )

    def create_portfolio_widget(self) -> html.Div:
        """Widget portfolio (placeholder)"""
        return html.Div(
            [
                html.H5("💼 Portfolio", className="text-center"),
                html.P("Fonctionnalité à venir", className="text-muted text-center"),
                dbc.Button(
                    "Configurer",
                    color="outline-primary",
                    size="sm",
                    className="d-block mx-auto",
                ),
            ]
        )

    def create_technical_analysis_widget(self) -> html.Div:
        """Widget analyse technique (placeholder)"""
        return html.Div(
            [
                html.H5("🔍 Analyse Technique", className="text-center"),
                html.P(
                    "Indicateurs techniques à venir", className="text-muted text-center"
                ),
                dbc.Button(
                    "Voir Plus",
                    color="outline-primary",
                    size="sm",
                    className="d-block mx-auto",
                ),
            ]
        )

    def create_dashboard_styles(self) -> html.Div:
        """Styles CSS pour le dashboard"""
        return html.Div(
            [html.Link(rel="stylesheet", href="/assets/dashboard.css")],
            style={"display": "none"},
        )

    def get_dashboard_css(self) -> str:
        """Retourne le CSS du dashboard"""
        return """
            .dashboard-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1rem 0;
                margin-bottom: 1rem;
                border-radius: 0.5rem;
            }
            
            .dashboard-title {
                margin: 0;
                font-weight: 600;
            }
            
            .dashboard-toolbar {
                background: #f8f9fa;
                padding: 0.5rem 0;
                margin-bottom: 1rem;
                border-radius: 0.3rem;
                border: 1px solid #e9ecef;
            }
            
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(12, 1fr);
                grid-auto-rows: 100px;
                gap: 1rem;
                padding: 1rem;
            }
            
            .dashboard-widget {
                transition: all 0.3s ease;
                border: 2px solid transparent;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .dashboard-widget:hover {
                border-color: #007bff;
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                transform: translateY(-2px);
            }
            
            .widget-content {
                height: 100%;
                overflow: auto;
            }
            
            .news-feed-container {
                max-height: 400px;
                overflow-y: auto;
                border: 1px solid #e9ecef;
                border-radius: 0.3rem;
                padding: 1rem;
            }
            
            @media (max-width: 768px) {
                .dashboard-grid {
                    grid-template-columns: 1fr;
                    grid-auto-rows: auto;
                }
                
                .dashboard-widget {
                    grid-column: 1 !important;
                    grid-row: auto !important;
                }
            }
        """


# Instance globale
advanced_dashboard = AdvancedDashboard()
