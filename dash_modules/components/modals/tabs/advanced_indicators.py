"""
🎯 ADVANCED INDICATORS - Module Indicateurs Avancés
===================================================

Module isolé pour les indicateurs avancés : Support/Resistance, Fibonacci, Pivots.
Chaque indicateur a ses propres callbacks et gestion d'état.
"""

import json
from typing import Any, Dict, List, Tuple

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, ctx, html

from ..config.parameters_manager import parameters_manager
from ..controls.base_controls import ControlsFactory


class AdvancedIndicatorsTab:
    """Module pour les indicateurs techniques avancés"""

    def __init__(self):
        self.parameters = parameters_manager
        self.controls_factory = ControlsFactory()

        # Registrer les callbacks spécifiques à ce module
        self._register_callbacks()

    def create_content(self) -> html.Div:
        """Créer le contenu complet des indicateurs avancés"""
        config = self.parameters.get_all_advanced_indicators()

        sections = []

        # === SECTION SUPPORT/RESISTANCE ===
        sr_section = self._create_support_resistance_section(
            config.get("support_resistance", {})
        )
        sections.append(sr_section)

        # === SECTION FIBONACCI ===
        fib_section = self._create_fibonacci_section(config.get("fibonacci", {}))
        sections.append(fib_section)

        # === SECTION PIVOT POINTS ===
        pivot_section = self._create_pivot_points_section(
            config.get("pivot_points", {})
        )
        sections.append(pivot_section)

        return html.Div(
            [
                self.controls_factory.create_section_header(
                    "🎯 Indicateurs Techniques Avancés",
                    "Configuration des indicateurs avancés (Support/Resistance, Fibonacci, Pivots)",
                ),
                # Indicateur de statut global
                html.Div(id="advanced-indicators-status", className="mb-3"),
                # Toutes les sections
                *sections,
                # Actions rapides
                self._create_quick_actions(),
            ]
        )

    def _create_support_resistance_section(self, sr_config: Dict) -> html.Div:
        """Créer la section Support/Resistance"""
        enabled = sr_config.get("enabled", False)

        controls = [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            self.controls_factory.create_numeric_input(
                                "advanced-sr-strength",
                                "Force",
                                sr_config.get("strength", 2),
                                sr_config.get("min_strength", 1),
                                sr_config.get("max_strength", 5),
                                1,
                                "niveau",
                                "Force minimum pour valider un niveau S/R",
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            self.controls_factory.create_numeric_input(
                                "advanced-sr-lookback",
                                "Lookback",
                                sr_config.get("lookback", 50),
                                sr_config.get("min_lookback", 10),
                                sr_config.get("max_lookback", 200),
                                1,
                                "barres",
                                "Nombre de barres à analyser pour les niveaux S/R",
                            )
                        ],
                        width=6,
                    ),
                ]
            ),
            # Preview des valeurs actuelles
            html.Div(id="sr-preview", className="mt-2"),
        ]

        return self.controls_factory.create_collapsible_section(
            "advanced-sr-collapse",
            "📊 Support & Resistance",
            controls,
            enabled,
            "advanced-sr-enabled",
        )

    def _create_fibonacci_section(self, fib_config: Dict) -> html.Div:
        """Créer la section Fibonacci"""
        enabled = fib_config.get("enabled", False)

        controls = [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            self.controls_factory.create_numeric_input(
                                "advanced-fibonacci-swing",
                                "Swing Period",
                                fib_config.get("swing_period", 20),
                                fib_config.get("min_swing", 5),
                                fib_config.get("max_swing", 100),
                                1,
                                "barres",
                                "Période pour détecter les swings Fibonacci",
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            self.controls_factory.create_numeric_input(
                                "advanced-fibonacci-line-width",
                                "Épaisseur lignes",
                                fib_config.get("line_width", 1),
                                1,
                                5,
                                1,
                                "px",
                                "Épaisseur des lignes Fibonacci",
                            )
                        ],
                        width=6,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H6(
                                "Niveaux Fibonacci", className="text-light mt-3 mb-2"
                            ),
                            html.Div(
                                [
                                    dbc.Badge(
                                        "0.0%", color="secondary", className="me-1"
                                    ),
                                    dbc.Badge("23.6%", color="info", className="me-1"),
                                    dbc.Badge(
                                        "38.2%", color="primary", className="me-1"
                                    ),
                                    dbc.Badge(
                                        "50.0%", color="warning", className="me-1"
                                    ),
                                    dbc.Badge(
                                        "61.8%", color="success", className="me-1"
                                    ),
                                    dbc.Badge(
                                        "78.6%", color="danger", className="me-1"
                                    ),
                                    dbc.Badge("100.0%", color="dark", className="me-1"),
                                ]
                            ),
                        ],
                        width=12,
                    )
                ]
            ),
            # Preview des valeurs actuelles
            html.Div(id="fibonacci-preview", className="mt-2"),
        ]

        return self.controls_factory.create_collapsible_section(
            "advanced-fibonacci-collapse",
            "🌀 Fibonacci Retracements",
            controls,
            enabled,
            "advanced-fibonacci-enabled",
        )

    def _create_pivot_points_section(self, pivot_config: Dict) -> html.Div:
        """Créer la section Pivot Points"""
        enabled = pivot_config.get("enabled", False)

        controls = [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            self.controls_factory.create_dropdown_control(
                                "advanced-pivot-method",
                                "Méthode de calcul",
                                [
                                    {
                                        "label": "Standard (Classic)",
                                        "value": "traditional",
                                    },
                                    {"label": "Fibonacci", "value": "fibonacci"},
                                    {"label": "Camarilla", "value": "camarilla"},
                                    {"label": "Woodie", "value": "woodie"},
                                    {"label": "DeMark", "value": "demark"},
                                ],
                                pivot_config.get("method", "traditional"),
                                "Méthode de calcul des points pivots",
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            html.H6("Niveaux affichés", className="text-light mb-2"),
                            dbc.Checklist(
                                id="advanced-pivot-levels",
                                options=[
                                    {"label": "R3", "value": "show_r3"},
                                    {"label": "R2", "value": "show_r2"},
                                    {"label": "R1", "value": "show_r1"},
                                    {"label": "PP", "value": "show_pp"},
                                    {"label": "S1", "value": "show_s1"},
                                    {"label": "S2", "value": "show_s2"},
                                    {"label": "S3", "value": "show_s3"},
                                ],
                                value=[
                                    level
                                    for level, show in pivot_config.items()
                                    if level.startswith("show_") and show
                                ],
                                inline=True,
                                className="text-light",
                            ),
                        ],
                        width=6,
                    ),
                ]
            ),
            # Preview des valeurs actuelles
            html.Div(id="pivot-preview", className="mt-2"),
        ]

        return self.controls_factory.create_collapsible_section(
            "advanced-pivot-collapse",
            "🎯 Pivot Points",
            controls,
            enabled,
            "advanced-pivot-enabled",
        )

    def _create_quick_actions(self) -> dbc.Card:
        """Créer les actions rapides pour indicateurs avancés"""
        return dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.H6(
                            "⚡ Actions Rapides Avancées", className="mb-0 text-primary"
                        )
                    ]
                ),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            [
                                                html.I(
                                                    className="fas fa-chart-line me-2"
                                                ),
                                                "S/R + Fibonacci",
                                            ],
                                            id="advanced-sr-fib-combo-btn",
                                            color="primary",
                                            outline=True,
                                            size="sm",
                                            className="w-100",
                                        )
                                    ],
                                    width=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            [
                                                html.I(
                                                    className="fas fa-crosshairs me-2"
                                                ),
                                                "Pivots + S/R",
                                            ],
                                            id="advanced-pivot-sr-combo-btn",
                                            color="info",
                                            outline=True,
                                            size="sm",
                                            className="w-100",
                                        )
                                    ],
                                    width=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            [
                                                html.I(
                                                    className="fas fa-toggle-off me-2"
                                                ),
                                                "Tout Désactiver",
                                            ],
                                            id="advanced-disable-all-btn",
                                            color="danger",
                                            outline=True,
                                            size="sm",
                                            className="w-100",
                                        )
                                    ],
                                    width=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Button(
                                            [
                                                html.I(className="fas fa-undo me-2"),
                                                "Valeurs Défaut",
                                            ],
                                            id="advanced-reset-defaults-btn",
                                            color="warning",
                                            outline=True,
                                            size="sm",
                                            className="w-100",
                                        )
                                    ],
                                    width=3,
                                ),
                            ]
                        )
                    ]
                ),
            ],
            className="mt-4",
        )

    def _register_callbacks(self):
        """Enregistrer tous les callbacks du module"""

        # Callback pour les previews en temps réel
        @callback(
            [
                Output("sr-preview", "children"),
                Output("fibonacci-preview", "children"),
                Output("pivot-preview", "children"),
            ],
            [
                Input("advanced-sr-strength", "value"),
                Input("advanced-sr-lookback", "value"),
                Input("advanced-fibonacci-swing", "value"),
                Input("advanced-fibonacci-line-width", "value"),
                Input("advanced-pivot-method", "value"),
                Input("advanced-pivot-levels", "value"),
            ],
        )
        def update_advanced_previews(
            sr_strength, sr_lookback, fib_swing, fib_width, pivot_method, pivot_levels
        ):
            """Mettre à jour les previews des indicateurs avancés"""

            # S/R Preview
            sr_preview = html.Div(
                [
                    dbc.Badge(
                        f"Force: {sr_strength or 2}", color="info", className="me-2"
                    ),
                    dbc.Badge(
                        f"Lookback: {sr_lookback or 50}",
                        color="secondary",
                        className="me-1",
                    ),
                ]
            )

            # Fibonacci Preview
            fib_preview = html.Div(
                [
                    dbc.Badge(
                        f"Swing: {fib_swing or 20}", color="primary", className="me-2"
                    ),
                    dbc.Badge(
                        f"Ligne: {fib_width or 1}px", color="success", className="me-1"
                    ),
                    dbc.Badge("7 niveaux", color="warning", className="me-1"),
                ]
            )

            # Pivot Preview
            method_labels = {
                "traditional": "Standard",
                "fibonacci": "Fibonacci",
                "camarilla": "Camarilla",
                "woodie": "Woodie",
                "demark": "DeMark",
            }
            pivot_preview = html.Div(
                [
                    dbc.Badge(
                        f"Méthode: {method_labels.get(pivot_method or 'traditional', 'Standard')}",
                        color="primary",
                        className="me-2",
                    ),
                    dbc.Badge(
                        f"{len(pivot_levels or [])} niveaux",
                        color="info",
                        className="me-1",
                    ),
                ]
            )

            return sr_preview, fib_preview, pivot_preview

        # Callback pour le statut global
        @callback(
            Output("advanced-indicators-status", "children"),
            [
                Input("advanced-sr-enabled", "value"),
                Input("advanced-fibonacci-enabled", "value"),
                Input("advanced-pivot-enabled", "value"),
            ],
        )
        def update_advanced_status(sr_enabled, fib_enabled, pivot_enabled):
            """Mettre à jour le statut global des indicateurs avancés"""
            enabled_count = sum(
                [sr_enabled or False, fib_enabled or False, pivot_enabled or False]
            )

            total_indicators = 3

            if enabled_count == 0:
                color = "secondary"
                text = "Indicateurs avancés désactivés"
                icon = "fas fa-pause-circle"
            elif enabled_count == total_indicators:
                color = "success"
                text = f"Tous les indicateurs avancés activés ({enabled_count}/{total_indicators})"
                icon = "fas fa-check-circle"
            else:
                color = "warning"
                text = (
                    f"Indicateurs avancés partiels ({enabled_count}/{total_indicators})"
                )
                icon = "fas fa-exclamation-circle"

            return dbc.Alert(
                [html.I(className=f"{icon} me-2"), text], color=color, className="mb-0"
            )


# Instance du module
advanced_indicators_tab = AdvancedIndicatorsTab()
