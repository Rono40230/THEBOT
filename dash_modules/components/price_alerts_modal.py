"""
Modal Alertes de Prix - THEBOT - Vue Pure (MVC)
Interface utilisateur uniquement, logique métier dans AlertService
"""

import json
from datetime import datetime

import dash
import dash_bootstrap_components as dbc
from dash import (
    Input,
    Output,
    State,
    callback,
    callback_context,
    clientside_callback,
    dash_table,
    dcc,
    html,
)
from dash.exceptions import PreventUpdate

from ..services import alert_service
from ..core.price_formatter import format_crypto_price_adaptive


class PriceAlertsModal:
    """Modal professionnel pour la gestion des alertes de prix"""

    def __init__(self):
        self.modal_id = "price-alerts-modal"

    def create_modal(self):
        """Créer le modal d'alertes de prix"""
        return dbc.Modal(
            [
                # Header personnalisé avec style vert
                html.Div(
                    [
                        html.Div(
                            [
                                html.I(className="fas fa-bell me-2"),
                                html.Span(
                                    "Gestionnaire d'Alertes de Prix",
                                    className="fw-bold",
                                ),
                            ],
                            className="d-flex align-items-center",
                        ),
                    ],
                    className="modal-header-draggable",
                ),
                # Corps du modal
                dbc.ModalBody(
                    [
                        # Section création d'alerte
                        html.Div(
                            [
                                html.H5(
                                    [
                                        html.I(className="fas fa-plus-circle me-2"),
                                        "Créer une Nouvelle Alerte",
                                    ],
                                    className="mb-3",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    "Type d'Alerte:",
                                                    className="form-label",
                                                ),
                                                dcc.Dropdown(
                                                    id="alert-type-dropdown",
                                                    options=[
                                                        {
                                                            "label": "📈 Prix Supérieur à (Above)",
                                                            "value": "Prix Supérieur à (Above)",
                                                        },
                                                        {
                                                            "label": "📉 Prix Inférieur à (Below)",
                                                            "value": "Prix Inférieur à (Below)",
                                                        },
                                                    ],
                                                    placeholder="Sélectionner le type d'alerte",
                                                    className="mb-3",
                                                ),
                                            ],
                                            width=6,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    "Prix d'Alerte:",
                                                    className="form-label",
                                                ),
                                                dbc.Input(
                                                    id="alert-price-input",
                                                    type="number",
                                                    step="any",
                                                    placeholder="Ex: 0.000001400",
                                                    className="mb-3",
                                                ),
                                            ],
                                            width=6,
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    "Message personnalisé (optionnel):",
                                                    className="form-label",
                                                ),
                                                dbc.Textarea(
                                                    id="alert-message-input",
                                                    placeholder="Ex: Bitcoin atteint mon objectif !",
                                                    rows=2,
                                                    className="mb-3",
                                                ),
                                            ],
                                            width=8,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    "Actions:", className="form-label"
                                                ),
                                                dbc.Button(
                                                    [
                                                        html.I(
                                                            className="fas fa-bell me-2"
                                                        ),
                                                        "Créer Alerte",
                                                    ],
                                                    id="create-alert-btn",
                                                    color="primary",
                                                    className="w-100",
                                                ),
                                            ],
                                            width=4,
                                        ),
                                    ]
                                ),
                            ],
                            className="p-3 mb-4 bg-light rounded",
                        ),
                        # Section alertes actives
                        html.Div(
                            [
                                html.H5(
                                    [
                                        html.I(className="fas fa-list me-2"),
                                        "Alertes Actives",
                                        dbc.Badge(
                                            "0",
                                            id="alerts-count-badge",
                                            color="primary",
                                            className="ms-2",
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                html.Div(
                                    id="alerts-table-container",
                                    children=[
                                        html.P(
                                            "Aucune alerte configurée",
                                            className="text-muted text-center mt-3",
                                        )
                                    ],
                                ),
                            ]
                        ),
                    ],
                    className="modal-body-custom",
                ),
                # Footer
                dbc.ModalFooter(
                    [
                        html.Div(
                            "Alertes temps réel - Notifications instantanées",
                            className="text-success small me-auto",
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-times me-2"), "Fermer"],
                            id="alerts-modal-close-btn",
                            color="secondary",
                            outline=True,
                        ),
                    ]
                ),
            ],
            id=self.modal_id,
            size="xl",
            is_open=False,
            backdrop=False,
            className="alerts-modal-custom",
            style={"position": "absolute", "top": "50px", "left": "50px"},
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
alerts_store = dcc.Store(id="alerts-store", data=[])

# Callbacks migrés vers PriceAlertsCallbacks manager - Phase 2.5 terminée ✅
