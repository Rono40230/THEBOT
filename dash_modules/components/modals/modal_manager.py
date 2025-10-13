"""
🎯 MODAL MANAGER - Gestionnaire Principal Architecture Modulaire
===============================================================

Gestionnaire principal qui orchestre tous les modules de la modal.
Remplace l'ancien monolithe 4000+ lignes par une architecture modulaire.
"""

import json
from typing import Any, Dict, List, Optional, Tuple

import dash_bootstrap_components as dbc
from dash import ALL, Input, Output, State, callback, ctx, dcc, html

from .config.parameters_manager import parameters_manager
from .controls.base_controls import CUSTOM_CONTROLS_CSS, ControlsFactory
from .tabs.advanced_indicators import advanced_indicators_tab
from .tabs.basic_indicators import basic_indicators_tab


class ModalIndicatorsManager:
    """Gestionnaire principal de la modal des indicateurs modulaire"""

    def __init__(self):
        self.parameters = parameters_manager
        self.controls_factory = ControlsFactory()
        self.active_tabs = {}  # Cache des modules chargés

        # Registrer les callbacks
        self._register_callbacks()

    def create_modal(self) -> dbc.Modal:
        """Créer la modal principale avec architecture modulaire"""
        modal_content = dbc.Modal(
            [
                # Header
                dbc.ModalHeader(
                    [
                        html.Div(
                            [
                                html.I(className="fas fa-chart-line me-2"),
                                html.Span(
                                    "Gestion des Indicateurs", className="fw-bold"
                                ),
                                dbc.Badge(
                                    "v2.0 Modulaire", color="primary", className="ms-2"
                                ),
                            ]
                        )
                    ],
                    close_button=True,
                ),
                # Body avec tabs
                dbc.ModalBody(
                    [
                        self._create_navigation_tabs(),
                        html.Div(id="indicators-modal-content", className="mt-3"),
                        html.Div(id="debug-info-container"),  # Debug info
                    ],
                    style={"maxHeight": "70vh", "overflowY": "auto"},
                ),
                # Footer
                dbc.ModalFooter(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            [
                                                html.I(className="fas fa-undo me-2"),
                                                "Reset",
                                            ],
                                            id="indicators-reset-btn",
                                            color="warning",
                                            outline=True,
                                            size="sm",
                                        )
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            [
                                                html.I(
                                                    className="fas fa-download me-2"
                                                ),
                                                "Export",
                                            ],
                                            id="indicators-export-btn",
                                            color="info",
                                            outline=True,
                                            size="sm",
                                        )
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            [
                                                html.I(className="fas fa-upload me-2"),
                                                "Import",
                                            ],
                                            id="indicators-import-btn",
                                            color="secondary",
                                            outline=True,
                                            size="sm",
                                        )
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            [
                                                html.I(className="fas fa-check me-2"),
                                                "Appliquer",
                                            ],
                                            id="indicators-apply-btn",
                                            color="success",
                                            size="sm",
                                        )
                                    ],
                                    width="auto",
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            [
                                                html.I(className="fas fa-times me-2"),
                                                "Fermer",
                                            ],
                                            id="indicators-close-btn",
                                            color="light",
                                            outline=True,
                                            size="sm",
                                        )
                                    ],
                                    width="auto",
                                ),
                            ],
                            justify="between",
                            className="w-100",
                        )
                    ]
                ),
            ],
            id="indicators-modal",
            size="xl",
            backdrop="static",
            keyboard=False,
            style={"--bs-modal-width": "90%"},
        )

        return modal_content

    def _create_navigation_tabs(self) -> dbc.Tabs:
        """Créer les onglets de navigation"""
        tabs = dbc.Tabs(
            [
                dbc.Tab(
                    label="📊 Indicateurs de Base",
                    tab_id="basic_indicators",
                    active_label_style={"color": "#4299e1", "fontWeight": "bold"},
                ),
                dbc.Tab(
                    label="🎯 Indicateurs Avancés",
                    tab_id="advanced_indicators",
                    active_label_style={"color": "#4299e1", "fontWeight": "bold"},
                ),
                dbc.Tab(
                    label="🎨 Styles de Trading",
                    tab_id="trading_styles",
                    active_label_style={"color": "#4299e1", "fontWeight": "bold"},
                ),
                dbc.Tab(
                    label="⚙️ Configuration",
                    tab_id="configuration",
                    active_label_style={"color": "#4299e1", "fontWeight": "bold"},
                ),
            ],
            id="indicators-tabs",
            active_tab="basic_indicators",
            className="mb-3",
        )

        return tabs

    def _register_callbacks(self):
        """Enregistrer tous les callbacks de la modal"""

        @callback(
            Output("indicators-modal-content", "children"),
            Input("indicators-tabs", "active_tab"),
        )
        def update_tab_content(active_tab):
            """Mettre à jour le contenu selon l'onglet actif"""
            try:
                if active_tab == "basic_indicators":
                    return self._create_basic_indicators_content()
                elif active_tab == "advanced_indicators":
                    return self._create_advanced_indicators_content()
                elif active_tab == "trading_styles":
                    return self._create_trading_styles_content()
                elif active_tab == "configuration":
                    return self._create_configuration_content()
                else:
                    return html.Div("Onglet non trouvé", className="text-warning")

            except Exception as e:
                return html.Div(
                    [
                        dbc.Alert(
                            [
                                html.H6("❌ Erreur de chargement", className="mb-2"),
                                html.P(f"Erreur: {str(e)}", className="mb-0"),
                            ],
                            color="danger",
                        )
                    ]
                )

        # Callback pour debug info
        @callback(
            Output("debug-info-container", "children"),
            [Input({"type": "indicator-control", "id": ALL}, "value")],
        )
        def update_debug_info(values):
            """Afficher les informations de debug"""
            if not values:
                return []

            current_config = self.parameters.get_all_basic_indicators()

            debug_info = dbc.Alert(
                [
                    html.H6("🔍 Debug Info", className="mb-2"),
                    html.Pre(
                        json.dumps(current_config, indent=2),
                        className="mb-0",
                        style={
                            "fontSize": "0.75rem",
                            "maxHeight": "150px",
                            "overflowY": "auto",
                        },
                    ),
                ],
                color="info",
                className="mt-3",
            )

            return debug_info

    def _create_basic_indicators_content(self) -> html.Div:
        """Créer le contenu des indicateurs de base"""
        return basic_indicators_tab.create_content()

    def _create_advanced_indicators_content(self) -> html.Div:
        """Créer le contenu des indicateurs avancés"""
        return advanced_indicators_tab.create_content()

    def _create_trading_styles_content(self) -> html.Div:
        """Créer le contenu des styles de trading"""
        return html.Div(
            [
                self.controls_factory.create_section_header(
                    "🎨 Styles de Trading",
                    "Presets prédéfinis pour différents styles de trading",
                ),
                dbc.Alert(
                    [
                        html.H6("🚧 En cours de développement", className="mb-2"),
                        html.P(
                            "Les styles de trading seront disponibles dans la prochaine version.",
                            className="mb-0",
                        ),
                    ],
                    color="info",
                ),
            ]
        )

    def _create_configuration_content(self) -> html.Div:
        """Créer le contenu de configuration"""
        return html.Div(
            [
                self.controls_factory.create_section_header(
                    "⚙️ Configuration", "Import/Export et paramètres globaux"
                ),
                dbc.Alert(
                    [
                        html.H6("🚧 En cours de développement", className="mb-2"),
                        html.P(
                            "Les options de configuration seront disponibles dans la prochaine version.",
                            className="mb-0",
                        ),
                    ],
                    color="info",
                ),
            ]
        )


# CSS styles
MODAL_CSS = f"""
{CUSTOM_CONTROLS_CSS}

.modal-xl {{
    max-width: 90% !important;
}}

.modal-body {{
    background-color: #1a202c;
    color: #e2e8f0;
}}

.modal-header {{
    background-color: #2d3748;
    color: #e2e8f0;
    border-bottom: 1px solid #4a5568;
}}

.modal-footer {{
    background-color: #2d3748;
    border-top: 1px solid #4a5568;
}}

.nav-tabs .nav-link {{
    background-color: #2d3748;
    border-color: #4a5568;
    color: #a0aec0;
}}

.nav-tabs .nav-link.active {{
    background-color: #4a5568;
    border-color: #4a5568;
    color: #e2e8f0;
}}

.border-secondary {{
    border-color: #4a5568 !important;
}}

.text-primary {{
    color: #4299e1 !important;
}}
"""


# Instance globale
modal_manager = ModalIndicatorsManager()
