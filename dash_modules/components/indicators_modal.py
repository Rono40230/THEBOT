"""
Modal pour la configuration des indicateurs techniques
Architecture basée sur price_alerts_modal.py pour assurer la cohérence
"""

import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from typing import Dict, Any, Optional


class IndicatorsModal:
    """Modal pour configurer tous les indicateurs techniques"""
    
    def __init__(self):
        self.modal_id = "indicators-modal"
        self.indicators_config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut des indicateurs"""
        return {
            # Moyennes mobiles
            'sma': {
                'enabled': False,
                'period': 20,
                'color': '#2E86C1'
            },
            'ema': {
                'enabled': False, 
                'period': 20,
                'color': '#E74C3C'
            },
            
            # Niveaux structurels
            'support_resistance': {
                'enabled': False,
                'strength': 3,
                'lookback': 50
            },
            'fibonacci': {
                'enabled': False,
                'swing_points': 20,
                'levels': [0.236, 0.382, 0.5, 0.618, 0.786]
            },
            'pivot_points': {
                'enabled': False,
                'method': 'standard',
                'period': 'daily'
            },
            
            # Oscillateurs (pour futures extensions)
            'rsi': {
                'enabled': False,
                'period': 14,
                'overbought': 70,
                'oversold': 30
            },
            'macd': {
                'enabled': False,
                'fast': 12,
                'slow': 26,
                'signal': 9
            }
        }
    
    def create_modal(self) -> dbc.Modal:
        """Créer la modal des indicateurs"""
        return dbc.Modal([
            dbc.ModalHeader([
                html.H4([
                    html.I(className="fas fa-chart-line me-2"),
                    "Configuration des Indicateurs Techniques"
                ], className="mb-0")
            ]),
            
            dbc.ModalBody([
                # Onglets pour organiser les indicateurs
                dbc.Tabs([
                    
                    # Onglet Moyennes Mobiles
                    dbc.Tab(label="📈 Moyennes Mobiles", tab_id="moving-averages", children=[
                        html.Div([
                            self._create_sma_section(),
                            html.Hr(),
                            self._create_ema_section()
                        ], className="p-3")
                    ]),
                    
                    # Onglet Niveaux Structurels
                    dbc.Tab(label="📊 Niveaux", tab_id="levels", children=[
                        html.Div([
                            self._create_sr_section(),
                            html.Hr(),
                            self._create_fibonacci_section(),
                            html.Hr(),
                            self._create_pivot_section()
                        ], className="p-3")
                    ]),
                    
                    # Onglet Oscillateurs (préparé pour le futur)
                    dbc.Tab(label="📉 Oscillateurs", tab_id="oscillators", children=[
                        html.Div([
                            self._create_rsi_section(),
                            html.Hr(),
                            self._create_macd_section()
                        ], className="p-3")
                    ])
                    
                ], id="indicators-tabs", active_tab="moving-averages")
            ]),
            
            dbc.ModalFooter([
                dbc.Button(
                    "Réinitialiser",
                    id="indicators-reset-btn",
                    color="secondary",
                    outline=True,
                    className="me-2"
                ),
                dbc.Button(
                    "Appliquer",
                    id="indicators-apply-btn", 
                    color="primary"
                ),
                dbc.Button(
                    "Fermer",
                    id="indicators-close-btn",
                    color="dark",
                    outline=True,
                    className="ms-2"
                )
            ])
            
        ], id=self.modal_id, size="lg", is_open=False, backdrop=True, scrollable=True)
    
    def _create_sma_section(self) -> html.Div:
        """Section SMA (Simple Moving Average)"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6("Simple Moving Average (SMA)", className="fw-bold"),
                    html.P("Moyenne mobile simple pour identifier les tendances", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-sma-switch",
                        value=False,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Période", className="fw-bold"),
                        dbc.Input(
                            id="indicators-sma-period",
                            type="number",
                            value=20,
                            min=1,
                            max=200,
                            step=1,
                            size="sm"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Couleur", className="fw-bold"),
                        dbc.Input(
                            id="indicators-sma-color",
                            type="color",
                            value="#2E86C1",
                            size="sm"
                        )
                    ], width=6)
                ], className="mt-2")
            ], id="indicators-sma-collapse", is_open=False)
        ])
    
    def _create_ema_section(self) -> html.Div:
        """Section EMA (Exponential Moving Average)"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6("Exponential Moving Average (EMA)", className="fw-bold"),
                    html.P("Moyenne mobile exponentielle, plus réactive aux changements récents", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-ema-switch",
                        value=False,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Période", className="fw-bold"),
                        dbc.Input(
                            id="indicators-ema-period",
                            type="number",
                            value=20,
                            min=1,
                            max=200,
                            step=1,
                            size="sm"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Couleur", className="fw-bold"),
                        dbc.Input(
                            id="indicators-ema-color",
                            type="color",
                            value="#E74C3C",
                            size="sm"
                        )
                    ], width=6)
                ], className="mt-2")
            ], id="indicators-ema-collapse", is_open=False)
        ])
    
    def _create_sr_section(self) -> html.Div:
        """Section Support/Résistance"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6("Support et Résistance", className="fw-bold"),
                    html.P("Niveaux de prix clés basés sur l'historique", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-sr-switch",
                        value=False,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Force minimale", className="fw-bold"),
                        dbc.Input(
                            id="indicators-sr-strength",
                            type="number",
                            value=3,
                            min=1,
                            max=10,
                            step=1,
                            size="sm"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Période d'analyse", className="fw-bold"),
                        dbc.Input(
                            id="indicators-sr-lookback",
                            type="number",
                            value=50,
                            min=10,
                            max=200,
                            step=10,
                            size="sm"
                        )
                    ], width=6)
                ], className="mt-2")
            ], id="indicators-sr-collapse", is_open=False)
        ])
    
    def _create_fibonacci_section(self) -> html.Div:
        """Section Fibonacci"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6("Retracements de Fibonacci", className="fw-bold"),
                    html.P("Niveaux de retracement basés sur la séquence de Fibonacci", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-fibonacci-switch",
                        value=False,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Points de swing", className="fw-bold"),
                        dbc.Input(
                            id="indicators-fibonacci-swing",
                            type="number",
                            value=20,
                            min=5,
                            max=100,
                            step=5,
                            size="sm"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Niveaux", className="fw-bold"),
                        html.Small("23.6%, 38.2%, 50%, 61.8%, 78.6%", className="text-muted d-block")
                    ], width=6)
                ], className="mt-2")
            ], id="indicators-fibonacci-collapse", is_open=False)
        ])
    
    def _create_pivot_section(self) -> html.Div:
        """Section Points Pivots"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6("Points Pivots", className="fw-bold"),
                    html.P("Niveaux calculés à partir des prix de la session précédente", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-pivot-switch",
                        value=False,
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            
            dbc.Collapse([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Méthode", className="fw-bold"),
                        dbc.Select(
                            id="indicators-pivot-method",
                            options=[
                                {"label": "Standard", "value": "standard"},
                                {"label": "Fibonacci", "value": "fibonacci"},
                                {"label": "Camarilla", "value": "camarilla"}
                            ],
                            value="standard",
                            size="sm"
                        )
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Période", className="fw-bold"),
                        dbc.Select(
                            id="indicators-pivot-period",
                            options=[
                                {"label": "Journalier", "value": "daily"},
                                {"label": "Hebdomadaire", "value": "weekly"},
                                {"label": "Mensuel", "value": "monthly"}
                            ],
                            value="daily",
                            size="sm"
                        )
                    ], width=6)
                ], className="mt-2")
            ], id="indicators-pivot-collapse", is_open=False)
        ])
    
    def _create_rsi_section(self) -> html.Div:
        """Section RSI (pour futures extensions)"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6("RSI (Relative Strength Index)", className="fw-bold"),
                    html.P("Oscillateur de momentum (14 périodes par défaut)", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-rsi-switch",
                        value=False,
                        disabled=True,  # Désactivé pour l'instant
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            html.Small("🚧 Fonctionnalité en développement", className="text-warning")
        ])
    
    def _create_macd_section(self) -> html.Div:
        """Section MACD (pour futures extensions)"""
        return html.Div([
            dbc.Row([
                dbc.Col([
                    html.H6("MACD", className="fw-bold"),
                    html.P("Moving Average Convergence Divergence", className="text-muted small")
                ], width=8),
                dbc.Col([
                    dbc.Switch(
                        id="indicators-macd-switch",
                        value=False,
                        disabled=True,  # Désactivé pour l'instant
                        className="ms-auto"
                    )
                ], width=4, className="d-flex align-items-center justify-content-end")
            ]),
            html.Small("🚧 Fonctionnalité en développement", className="text-warning")
        ])
    
    def get_custom_css(self) -> str:
        """CSS personnalisé pour la modal des indicateurs"""
        return """
        /* Modal Indicateurs */
        #indicators-modal .modal-dialog {
            max-width: 800px;
        }
        
        #indicators-modal .modal-body {
            max-height: 70vh;
            overflow-y: auto;
        }
        
        /* Onglets */
        #indicators-tabs .nav-link {
            border: none;
            border-bottom: 2px solid transparent;
            background: none !important;
            color: #6c757d !important;
            font-weight: 500;
        }
        
        #indicators-tabs .nav-link.active {
            border-bottom-color: #007bff !important;
            color: #007bff !important;
            background: none !important;
        }
        
        /* Sections d'indicateurs */
        .indicators-section {
            border: 1px solid #e9ecef;
            border-radius: 0.375rem;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: #f8f9fa;
        }
        
        /* Switches */
        .form-switch .form-check-input {
            width: 3rem;
            height: 1.5rem;
        }
        
        /* Collapse animations */
        .collapse {
            transition: height 0.3s ease;
        }
        
        /* Inputs couleur */
        input[type="color"] {
            border: 1px solid #ced4da;
            border-radius: 0.375rem;
            width: 100%;
            height: 38px;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            #indicators-modal .modal-dialog {
                max-width: 95%;
                margin: 1rem auto;
            }
        }
        """


# Instance globale
indicators_modal = IndicatorsModal()


def register_indicators_modal_callbacks(app):
    """Enregistrer les callbacks pour la modal des indicateurs"""
    
    # Callback pour ouvrir/fermer la modal
    @app.callback(
        Output("indicators-modal", "is_open"),
        [Input("manage-indicators-btn", "n_clicks"),
         Input("indicators-close-btn", "n_clicks"),
         Input("indicators-apply-btn", "n_clicks")],
        [State("indicators-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_indicators_modal(open_clicks, close_clicks, apply_clicks, is_open):
        """Gérer l'ouverture/fermeture de la modal"""
        ctx = callback_context
        if not ctx.triggered:
            return False
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == "manage-indicators-btn":
            return True
        elif button_id in ["indicators-close-btn", "indicators-apply-btn"]:
            return False
        
        return is_open
    
    # Callbacks pour les collapses des sections
    collapse_callbacks = [
        ("indicators-sma-switch", "indicators-sma-collapse"),
        ("indicators-ema-switch", "indicators-ema-collapse"),
        ("indicators-sr-switch", "indicators-sr-collapse"),
        ("indicators-fibonacci-switch", "indicators-fibonacci-collapse"),
        ("indicators-pivot-switch", "indicators-pivot-collapse")
    ]
    
    for switch_id, collapse_id in collapse_callbacks:
        @app.callback(
            Output(collapse_id, "is_open"),
            [Input(switch_id, "value")],
            prevent_initial_call=True
        )
        def toggle_collapse(enabled):
            """Ouvrir/fermer la section quand l'indicateur est activé/désactivé"""
            return enabled
    
    # Callback principal pour synchroniser avec le graphique
    @app.callback(
        [Output('crypto-sma-switch', 'value'),
         Output('crypto-sma-period', 'value'),
         Output('crypto-ema-switch', 'value'),
         Output('crypto-ema-period', 'value'),
         Output('crypto-sr-switch', 'value'),
         Output('crypto-sr-strength', 'value'),
         Output('crypto-fibonacci-switch', 'value'),
         Output('crypto-fibonacci-swing', 'value'),
         Output('crypto-pivot-switch', 'value'),
         Output('crypto-pivot-method', 'value')],
        [Input("indicators-apply-btn", "n_clicks")],
        [State("indicators-sma-switch", "value"),
         State("indicators-sma-period", "value"),
         State("indicators-ema-switch", "value"),
         State("indicators-ema-period", "value"),
         State("indicators-sr-switch", "value"),
         State("indicators-sr-strength", "value"),
         State("indicators-fibonacci-switch", "value"),
         State("indicators-fibonacci-swing", "value"),
         State("indicators-pivot-switch", "value"),
         State("indicators-pivot-method", "value")],
        prevent_initial_call=True
    )
    def apply_indicators_config(apply_clicks, sma_enabled, sma_period, ema_enabled, ema_period,
                               sr_enabled, sr_strength, fib_enabled, fib_swing, 
                               pivot_enabled, pivot_method):
        """Appliquer la configuration des indicateurs au graphique"""
        if apply_clicks:
            return (sma_enabled, sma_period, ema_enabled, ema_period,
                   sr_enabled, sr_strength, fib_enabled, fib_swing,
                   pivot_enabled, pivot_method)
        
        # Retourner les valeurs actuelles sans changement
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


# Store pour sauvegarder la configuration des indicateurs
indicators_store = dcc.Store(id='indicators-config-store', data=indicators_modal.indicators_config)