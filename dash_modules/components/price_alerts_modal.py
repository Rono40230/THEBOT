"""
Modal Alertes de Prix - THEBOT
Gestion complète des alertes de prix avec interface moderne et persistance
"""

import dash
from dash import html, dcc, Input, Output, State, callback, clientside_callback, dash_table, callback_context
import dash_bootstrap_components as dbc
from datetime import datetime
import json
from dash.exceptions import PreventUpdate
from dash_modules.core.alerts_manager import alerts_manager

def format_crypto_price(price):
    """Formatter pour les prix de crypto avec 10 décimales"""
    return f"{price:.10f}"

class PriceAlertsModal:
    """Modal professionnel pour la gestion des alertes de prix"""
    
    def __init__(self):
        self.modal_id = "price-alerts-modal"
    
    def create_modal(self):
        """Créer le modal d'alertes de prix"""
        return dbc.Modal([
            # Header personnalisé avec style vert
            html.Div([
                html.Div([
                    html.I(className="fas fa-bell me-2"),
                    html.Span("Gestionnaire d'Alertes de Prix", className="fw-bold")
                ], className="d-flex align-items-center"),
            ], className="modal-header-draggable"),
            
            # Corps du modal
            dbc.ModalBody([
                # Section création d'alerte
                html.Div([
                    html.H5([
                        html.I(className="fas fa-plus-circle me-2"),
                        "Créer une Nouvelle Alerte"
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Type d'Alerte:", className="form-label"),
                            dcc.Dropdown(
                                id="alert-type-dropdown",
                                options=[
                                    {"label": "📈 Prix Supérieur à (Above)", "value": "Prix Supérieur à (Above)"},
                                    {"label": "📉 Prix Inférieur à (Below)", "value": "Prix Inférieur à (Below)"}
                                ],
                                placeholder="Sélectionner le type d'alerte",
                                className="mb-3"
                            )
                        ], width=6),
                        
                        dbc.Col([
                            dbc.Label("Prix d'Alerte:", className="form-label"),
                            dbc.Input(
                                id="alert-price-input",
                                type="number",
                                step="any",
                                placeholder="Ex: 0.000001400",
                                className="mb-3"
                            )
                        ], width=6)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Message personnalisé (optionnel):", className="form-label"),
                            dbc.Textarea(
                                id="alert-message-input",
                                placeholder="Ex: Bitcoin atteint mon objectif !",
                                rows=2,
                                className="mb-3"
                            )
                        ], width=8),
                        
                        dbc.Col([
                            dbc.Label("Actions:", className="form-label"),
                            dbc.Button(
                                [html.I(className="fas fa-bell me-2"), "Créer Alerte"],
                                id="create-alert-btn",
                                color="primary",
                                className="w-100"
                            )
                        ], width=4)
                    ])
                ], className="p-3 mb-4 bg-light rounded"),
                
                # Section alertes actives
                html.Div([
                    html.H5([
                        html.I(className="fas fa-list me-2"),
                        "Alertes Actives",
                        dbc.Badge(
                            "0",
                            id="alerts-count-badge",
                            color="primary",
                            className="ms-2"
                        )
                    ], className="mb-3"),
                    
                    html.Div(
                        id="alerts-table-container",
                        children=[
                            html.P("Aucune alerte configurée", className="text-muted text-center mt-3")
                        ]
                    )
                ])
            ], className="modal-body-custom"),
            
            # Footer
            dbc.ModalFooter([
                html.Div("Alertes temps réel - Notifications instantanées", 
                        className="text-success small me-auto"),
                dbc.Button(
                    [html.I(className="fas fa-times me-2"), "Fermer"],
                    id="alerts-modal-close-btn",
                    color="secondary",
                    outline=True
                )
            ])
        ], 
        id=self.modal_id,
        size="xl",
        is_open=False,
        backdrop=False,
        className="alerts-modal-custom",
        style={"position": "absolute", "top": "50px", "left": "50px"}
        )
    
    def get_custom_css(self) -> str:
        """CSS personnalisé pour le modal alertes"""
        return """
        /* Modal alertes - Styles cohérents avec modal IA */
        .alerts-modal-custom .modal-dialog {
            max-width: 90vw;
            margin: 0;
            transition: transform 0.1s ease-out;
        }
        
        .alerts-modal-custom .modal-content {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 2px solid #28a745;
        }
        
        /* Header déplaçable - Vert pour les alertes */
        .alerts-modal-custom .modal-header-draggable {
            background: linear-gradient(90deg, #28a745, #20c997);
            color: white;
            border-radius: 13px 13px 0 0;
            border-bottom: 2px solid #20c997;
            padding: 1rem 1.5rem;
            position: relative;
        }
        
        .alerts-modal-custom .modal-header-draggable::before {
            content: '';
            position: absolute;
            top: 8px;
            left: 50%;
            transform: translateX(-50%);
            width: 40px;
            height: 4px;
            background: rgba(255,255,255,0.5);
            border-radius: 2px;
        }
        
        /* Corriger les couleurs des titres pour qu'ils soient visibles */
        .alerts-modal-custom .modal-body h5 {
            color: #212529 !important;
            font-weight: 600;
        }
        
        .alerts-modal-custom .form-label {
            color: #495057 !important;
            font-weight: 500;
        }
        
        .alerts-modal-custom .text-muted {
            color: #6c757d !important;
        }
        
        .alerts-modal-custom .modal-body-custom {
            max-height: 70vh;
            overflow-y: auto;
            padding: 1.5rem;
        }
        
        .alerts-modal-custom .modal-footer {
            border-top: 1px solid #dee2e6;
            background: rgba(255,255,255,0.9);
            border-radius: 0 0 13px 13px;
        }
        
        /* Animation de dragging */
        .alerts-modal-dragging {
            transition: none !important;
            z-index: 1060 !important;
        }
        
        /* Badges */
        .alerts-modal-custom .badge {
            font-size: 0.8em;
        }
        
        /* Boutons d'action */
        .alerts-modal-custom .btn {
            border-radius: 8px;
            font-weight: 500;
        }
        
        /* Formulaire */
        .alerts-modal-custom .form-control, .alerts-modal-custom .form-select {
            border-radius: 8px;
            border: 1px solid #ced4da;
        }
        
        .alerts-modal-custom .form-control:focus, .alerts-modal-custom .form-select:focus {
            border-color: #28a745;
            box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
        }
        """

# Instance globale
price_alerts_modal = PriceAlertsModal()

# Store pour les alertes (utilisé pour les callbacks uniquement)
alerts_store = dcc.Store(id='alerts-store', data=[])

# Callbacks pour le modal d'alertes

@callback(
    [Output('alerts-store', 'data'),
     Output('alerts-count-badge', 'children')],
    [Input('price-alerts-modal', 'is_open')],
    prevent_initial_call=False
)
def initialize_alerts_on_modal_open(is_open):
    """Charger les alertes depuis la persistance quand le modal s'ouvre ou au démarrage"""
    all_alerts = alerts_manager.get_all_alerts()
    return all_alerts, len(all_alerts)

@callback(
    [
        Output('alerts-store', 'data', allow_duplicate=True),
        Output('alerts-count-badge', 'children', allow_duplicate=True),
        Output('alert-type-dropdown', 'value'),
        Output('alert-price-input', 'value'),
        Output('alert-message-input', 'value')
    ],
    [
        Input('create-alert-btn', 'n_clicks')
    ],
    [
        State('crypto-current-symbol', 'children'),
        State('alert-type-dropdown', 'value'),
        State('alert-price-input', 'value'),
        State('alert-message-input', 'value')
    ],
    prevent_initial_call=True
)
def create_alert(n_clicks, symbol_text, alert_type, price, message):
    if not n_clicks or not alert_type or not price:
        raise PreventUpdate
    
    # Extraire le symbole du texte affiché
    symbol = symbol_text.split()[0] if symbol_text else "UNKNOWN"
    
    # Créer la nouvelle alerte via le gestionnaire
    alerts_manager.add_alert(
        symbol=symbol,
        alert_type=alert_type,
        price=float(price),
        message=message or ""
    )
    
    # Récupérer toutes les alertes mises à jour
    all_alerts = alerts_manager.get_all_alerts()
    
    # Réinitialiser le formulaire et retourner les alertes mises à jour
    return all_alerts, len(all_alerts), None, None, ""

@callback(
    Output('alerts-table-container', 'children'),
    [Input('alerts-store', 'data')],
    prevent_initial_call=False
)
def update_alerts_table(alerts_data):
    # Charger les alertes depuis le gestionnaire (toujours à jour)
    all_alerts = alerts_manager.get_all_alerts()
    
    if not all_alerts:
        return html.Div([
            html.P("Aucune alerte configurée", className="text-muted text-center mt-3")
        ])
    
    alert_cards = []
    for alert in all_alerts:
        # Icône et couleur selon le type
        if alert['type'] == 'Prix Supérieur à (Above)':
            icon = "fas fa-arrow-up text-success"
            type_text = "Au-dessus:"
        else:
            icon = "fas fa-arrow-down text-danger"
            type_text = "En-dessous:"
        
        card = html.Div([
            html.Div([
                html.Strong(f"{alert['symbol']} ", className="text-primary"),
                html.Span(f"{type_text} ${format_crypto_price(alert['price'])}"),
                html.Br(),
                html.Small(alert.get('message', ''), className="text-muted") if alert.get('message') else None,
                html.Br(),
                html.Small(f"Créé: {alert['created']}", className="text-muted")
            ], className="col-8"),
            html.Div([
                html.Button(
                    html.I(className="fas fa-trash"),
                    id={'type': 'delete-alert-btn', 'index': alert['id']},
                    className="btn btn-outline-danger btn-sm ms-1",
                    title="Supprimer l'alerte"
                )
            ], className="col-4 text-end")
        ], className="row align-items-center p-3 mb-2 bg-dark text-light rounded")
        
        alert_cards.append(card)
    
    return html.Div(alert_cards)

@callback(
    [Output('alerts-store', 'data', allow_duplicate=True),
     Output('alerts-count-badge', 'children', allow_duplicate=True)],
    [Input({'type': 'delete-alert-btn', 'index': dash.dependencies.ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def delete_alert(n_clicks_list):
    if not any(n_clicks_list or []):
        raise PreventUpdate
    
    # Trouver quel bouton a été cliqué
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    alert_id = json.loads(button_id)['index']
    
    # Supprimer l'alerte via le gestionnaire
    success = alerts_manager.delete_alert(alert_id)
    
    if success:
        # Récupérer toutes les alertes mises à jour
        all_alerts = alerts_manager.get_all_alerts()
        return all_alerts, len(all_alerts)
    else:
        raise PreventUpdate

@callback(
    Output('price-alerts-modal', 'is_open'),
    [Input('manage-alerts-btn', 'n_clicks'),
     Input('alerts-modal-close-btn', 'n_clicks')],
    [State('price-alerts-modal', 'is_open')]
)
def toggle_alerts_modal(open_clicks, close_clicks, is_open):
    """Ouvrir/fermer le modal d'alertes"""
    if open_clicks or close_clicks:
        return not is_open
    return is_open

def register_alerts_modal_callbacks(app=None):
    """Enregistrer tous les callbacks du modal d'alertes"""
    # Les callbacks sont définis avec le décorateur @callback ci-dessus
    pass