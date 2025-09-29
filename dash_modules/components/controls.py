"""
Controls Components Module - THEBOT Dash
Composants de contrôles d'interface réutilisables
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
from typing import List, Dict, Any
from ..core.config import dash_config, ui_config


class ControlsComponents:
    """Composants de contrôles d'interface"""
    
    def __init__(self):
        self.dash_config = dash_config
        self.ui_config = ui_config
        
    def create_header(self) -> dbc.Row:
        """Header compact avec indicateurs essentiels"""
        
        return dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4([
                        html.I(className="fas fa-robot me-2"),
                        "THEBOT",
                    ], className="mb-0 d-flex align-items-center text-light")
                ])
            ], width=4),
            
            dbc.Col([
                html.Div([
                    # Indicateurs de statut compacts
                    dbc.Badge([
                        html.I(className="fas fa-signal me-1"),
                        html.Span("LIVE", id="connection-status")
                    ], color="success", className="me-2 pulse"),
                    
                    dbc.Badge([
                        html.I(className="fas fa-chart-line me-1"),
                        html.Span("12", id="markets-count")
                    ], color="info", className="me-2"),
                    
                    dbc.Badge([
                        html.I(className="fas fa-brain me-1"),
                        html.Span("AI", id="ai-status")
                    ], color="warning", className="me-2"),
                    
                ], className="d-flex justify-content-end align-items-center")
            ], width=8)
            
        ], className="border-bottom border-secondary pb-2 mb-2")
    
    def create_control_bar(self) -> dbc.Row:
        """Barre de contrôle avec sélecteurs principaux"""
        
        # Options des marchés Binance (statiques)
        market_options = [
            {'label': 'Bitcoin/USDT', 'value': 'BTCUSDT'},
            {'label': 'Ethereum/USDT', 'value': 'ETHUSDT'},
            {'label': 'Binance Coin/USDT', 'value': 'BNBUSDT'},
            {'label': 'Cardano/USDT', 'value': 'ADAUSDT'},
            {'label': 'Solana/USDT', 'value': 'SOLUSDT'},
            {'label': 'Polkadot/USDT', 'value': 'DOTUSDT'},
            {'label': 'Chainlink/USDT', 'value': 'LINKUSDT'},
            {'label': 'Litecoin/USDT', 'value': 'LTCUSDT'},
        ]
        
        return dbc.Row([
            
            dbc.Col([
                dbc.Label("Market", className="fw-bold text-light small"),
                dcc.Dropdown(
                    id='symbol-selector',
                    options=market_options,
                    value='BTCUSDT',  # Valeur par défaut explicite
                    placeholder="Select a Market",
                    className="dash-bootstrap",
                    style={'backgroundColor': '#1f2937', 'color': 'white'}
                )
            ], width=3),
            
            dbc.Col([
                dbc.Label("Timeframe", className="fw-bold text-light small"),
                dcc.Dropdown(
                    id='timeframe-selector',
                    options=self.ui_config.timeframes,
                    value='1h',
                    className="dash-bootstrap"
                )
            ], width=2),
            
            dbc.Col([
                dbc.Label("Analysis Type", className="fw-bold text-light small"),
                dcc.Dropdown(
                    id='analysis-selector',
                    options=self.ui_config.analysis_types,
                    value='technical',
                    className="dash-bootstrap"
                )
            ], width=2),
            
            dbc.Col([
                dbc.Label("Action", className="fw-bold text-light small"),
                dbc.ButtonGroup([
                    dbc.Button("BUY", color="success", size="sm", outline=True),
                    dbc.Button("SELL", color="danger", size="sm", outline=True),
                    dbc.Button("HOLD", color="warning", size="sm", outline=True)
                ])
            ], width=2),
            
            dbc.Col([
                dbc.Label("Real-Time", className="fw-bold text-light small"),
                html.Div([
                    dbc.Button([
                        html.I(className="fas fa-play me-1"),
                        "Start"
                    ], id="start-btn", color="success", size="sm", className="me-1"),
                    
                    dbc.Button([
                        html.I(className="fas fa-stop me-1"),
                        "Stop"
                    ], id="stop-btn", color="secondary", size="sm", disabled=True)
                ])
            ], width=3)
            
        ], className="mb-3")
    
    def create_indicators_sidebar(self) -> html.Div:
        """Sidebar des indicateurs techniques"""
        
        return html.Div([
            
            # Titre de la section
            html.H5([
                html.I(className="fas fa-chart-bar me-2"),
                "Technical Indicators"
            ], className="text-primary mb-3"),
            
            # SMA Controls
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chart-line me-2"),
                        html.Label("SMA", className="fw-bold")
                    ], className="d-flex align-items-center mb-2"),
                    
                    dbc.Switch(
                        id="sma-switch",
                        label="Enable SMA",
                        value=False,
                        className="mb-2"
                    ),
                    
                    dbc.InputGroup([
                        dbc.InputGroupText("Period"),
                        dbc.Input(
                            id="sma-period",
                            type="number",
                            value=20,
                            min=5,
                            max=200,
                            step=1
                        )
                    ], size="sm")
                ])
            ], className="mb-3"),
            
            # EMA Controls  
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-trending-up me-2"),
                        html.Label("EMA", className="fw-bold")
                    ], className="d-flex align-items-center mb-2"),
                    
                    dbc.Switch(
                        id="ema-switch",
                        label="Enable EMA",
                        value=False,
                        className="mb-2"
                    ),
                    
                    dbc.InputGroup([
                        dbc.InputGroupText("Period"),
                        dbc.Input(
                            id="ema-period",
                            type="number",
                            value=12,
                            min=5,
                            max=200,
                            step=1
                        )
                    ], size="sm")
                ])
            ], className="mb-3"),
            
            # RSI Controls
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-wave-square me-2"),
                        html.Label("RSI", className="fw-bold")
                    ], className="d-flex align-items-center mb-2"),
                    
                    dbc.Switch(
                        id="rsi-switch",
                        label="Enable RSI",
                        value=True,
                        className="mb-2"
                    ),
                    
                    dbc.InputGroup([
                        dbc.InputGroupText("Period"),
                        dbc.Input(
                            id="rsi-period",
                            type="number",
                            value=14,
                            min=5,
                            max=50,
                            step=1
                        )
                    ], size="sm")
                ])
            ], className="mb-3"),
            
            # ATR Controls
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-arrows-alt-v me-2"),
                        html.Label("ATR", className="fw-bold")
                    ], className="d-flex align-items-center mb-2"),
                    
                    dbc.Switch(
                        id="atr-switch",
                        label="Enable ATR",
                        value=True,
                        className="mb-2"
                    ),
                    
                    dbc.InputGroup([
                        dbc.InputGroupText("Period"),
                        dbc.Input(
                            id="atr-period",
                            type="number",
                            value=14,
                            min=5,
                            max=50,
                            step=1
                        )
                    ], size="sm")
                ])
            ], className="mb-3"),
            
            # Trading Strategies
            html.Hr(),
            html.H6("⚡ Trading Strategies", className="text-warning mb-2"),
            
            dbc.Button("Scalping", color="danger", outline=True, size="sm", className="w-100 mb-2"),
            dbc.Button("Day Trading", color="warning", outline=True, size="sm", className="w-100 mb-2"),
            dbc.Button("Swing", color="success", outline=True, size="sm", className="w-100 mb-2"),
            
        ])
    
    def create_status_info(self) -> html.Div:
        """Informations de statut et performances"""
        
        return html.Div([
            
            # Market Status
            dbc.Card([
                dbc.CardHeader("📊 Market Status"),
                dbc.CardBody([
                    html.P(id="market-status", className="text-success mb-0")
                ])
            ], className="mb-3"),
            
            # Technical Summary
            dbc.Card([
                dbc.CardHeader("📈 Technical Summary"),
                dbc.CardBody([
                    html.Div(id="technical-summary")
                ])
            ], className="mb-3"),
            
            # Performance Metrics
            dbc.Card([
                dbc.CardHeader("⚡ Performance"),
                dbc.CardBody([
                    html.Div([
                        html.Small("Last Update: ", className="text-muted"),
                        html.Span(id="last-update", className="fw-bold")
                    ], className="mb-2"),
                    
                    html.Div([
                        html.Small("Data Points: ", className="text-muted"),
                        html.Span(id="data-points", className="fw-bold text-info")
                    ])
                ])
            ])
            
        ])


# Instance globale pour l'import direct
controls = ControlsComponents()