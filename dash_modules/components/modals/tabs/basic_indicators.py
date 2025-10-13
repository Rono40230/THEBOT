"""
📊 BASIC INDICATORS - Module Indicateurs de Base
===============================================

Module isolé pour les indicateurs de base : SMA, EMA, RSI, ATR, MACD.
Chaque indicateur a ses propres callbacks et gestion d'état.
"""

import json
from typing import Any, Dict, List, Tuple

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, ctx, html

from ..config.parameters_manager import parameters_manager
from ..controls.base_controls import ControlsFactory


class BasicIndicatorsTab:
    """Module pour les indicateurs techniques de base"""

    def __init__(self):
        self.parameters = parameters_manager
        self.controls_factory = ControlsFactory()

        # Registrer les callbacks spécifiques à ce module
        self._register_callbacks()

    def create_content(self) -> html.Div:
        """Créer le contenu complet des indicateurs de base"""
        config = self.parameters.get_all_basic_indicators()

        sections = []

        # === SECTION SMA ===
        sma_section = self._create_sma_section(config.get("sma", {}))
        sections.append(sma_section)

        # === SECTION EMA ===
        ema_section = self._create_ema_section(config.get("ema", {}))
        sections.append(ema_section)

        # === SECTION RSI ===
        rsi_section = self._create_rsi_section(config.get("rsi", {}))
        sections.append(rsi_section)

        # === SECTION ATR ===
        atr_section = self._create_atr_section(config.get("atr", {}))
        sections.append(atr_section)

        # === SECTION MACD ===
        macd_section = self._create_macd_section(config.get("macd", {}))
        sections.append(macd_section)

        return html.Div(
            [
                self.controls_factory.create_section_header(
                    "📊 Indicateurs Techniques de Base",
                    "Configuration des indicateurs techniques fondamentaux (SMA, EMA, RSI, ATR, MACD)",
                ),
                # Indicateur de statut global
                html.Div(id="basic-indicators-status", className="mb-3"),
                # Toutes les sections
                *sections,
                # Actions rapides
                self._create_quick_actions(),
            ]
        )

    def _create_sma_section(self, sma_config: Dict) -> html.Div:
        """Créer la section SMA avec tous ses contrôles"""
        enabled = sma_config.get("enabled", True)

        controls = [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            self.controls_factory.create_numeric_input(
                                "basic-sma-period",
                                "Période",
                                sma_config.get("period", 20),
                                sma_config.get("min_value", 5),
                                sma_config.get("max_value", 200),
                                1,
                                "barres",
                                "Nombre de périodes pour calculer la moyenne mobile simple",
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            self.controls_factory.create_color_picker(
                                "basic-sma-color",
                                "Couleur",
                                sma_config.get("color", "#2196F3"),
                                "Couleur d'affichage de la ligne SMA",
                            )
                        ],
                        width=6,
                    ),
                ]
            ),
            # Preview des valeurs actuelles
            html.Div(id="sma-preview", className="mt-2"),
        ]

        return self.controls_factory.create_collapsible_section(
            "basic-sma-collapse",
            "📈 Simple Moving Average (SMA)",
            controls,
            enabled,
            "basic-sma-enabled",
        )

    def _create_ema_section(self, ema_config: Dict) -> html.Div:
        """Créer la section EMA avec tous ses contrôles"""
        enabled = ema_config.get("enabled", True)

        controls = [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            self.controls_factory.create_numeric_input(
                                "basic-ema-period",
                                "Période",
                                ema_config.get("period", 12),
                                ema_config.get("min_value", 5),
                                ema_config.get("max_value", 200),
                                1,
                                "barres",
                                "Nombre de périodes pour calculer la moyenne mobile exponentielle",
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            self.controls_factory.create_color_picker(
                                "basic-ema-color",
                                "Couleur",
                                ema_config.get("color", "#FF9800"),
                                "Couleur d'affichage de la ligne EMA",
                            )
                        ],
                        width=6,
                    ),
                ]
            ),
            # Preview des valeurs actuelles
            html.Div(id="ema-preview", className="mt-2"),
        ]

        return self.controls_factory.create_collapsible_section(
            "basic-ema-collapse",
            "📊 Exponential Moving Average (EMA)",
            controls,
            enabled,
            "basic-ema-enabled",
        )

    def _create_rsi_section(self, rsi_config: Dict) -> html.Div:
        """Créer la section RSI avec tous ses contrôles"""
        enabled = rsi_config.get("enabled", True)

        controls = [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            self.controls_factory.create_numeric_input(
                                "basic-rsi-period",
                                "Période",
                                rsi_config.get("period", 14),
                                rsi_config.get("min_value", 2),
                                rsi_config.get("max_value", 50),
                                1,
                                "barres",
                                "Nombre de périodes pour calculer le RSI",
                            )
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        [
                            self.controls_factory.create_numeric_input(
                                "basic-rsi-overbought",
                                "Suracheté",
                                rsi_config.get("overbought", 70),
                                50,
                                95,
                                1,
                                "",
                                "Niveau RSI au-dessus duquel l'actif est suracheté",
                            )
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        [
                            self.controls_factory.create_numeric_input(
                                "basic-rsi-oversold",
                                "Survendu",
                                rsi_config.get("oversold", 30),
                                5,
                                50,
                                1,
                                "",
                                "Niveau RSI en-dessous duquel l'actif est survendu",
                            )
                        ],
                        width=4,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            self.controls_factory.create_color_picker(
                                "basic-rsi-color",
                                "Couleur RSI",
                                rsi_config.get("color", "#9C27B0"),
                                "Couleur de la ligne RSI",
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            # Zone RSI preview
                            html.Div(id="rsi-preview", className="mt-2")
                        ],
                        width=6,
                    ),
                ]
            ),
        ]

        return self.controls_factory.create_collapsible_section(
            "basic-rsi-collapse",
            "📉 Relative Strength Index (RSI)",
            controls,
            enabled,
            "basic-rsi-enabled",
        )

    def _create_atr_section(self, atr_config: Dict) -> html.Div:
        """Créer la section ATR avec tous ses contrôles"""
        enabled = atr_config.get("enabled", True)

        controls = [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            self.controls_factory.create_numeric_input(
                                "basic-atr-period",
                                "Période",
                                atr_config.get("period", 14),
                                atr_config.get("min_value", 5),
                                atr_config.get("max_value", 50),
                                1,
                                "barres",
                                "Nombre de périodes pour calculer l'ATR",
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            self.controls_factory.create_slider_control(
                                "basic-atr-multiplier",
                                "Multiplicateur",
                                atr_config.get("multiplier", 2.0),
                                0.5,
                                5.0,
                                0.1,
                                help_text="Multiplicateur ATR pour stop-loss et take-profit",
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
                            self.controls_factory.create_color_picker(
                                "basic-atr-color",
                                "Couleur",
                                atr_config.get("color", "#4CAF50"),
                                "Couleur d'affichage de l'ATR",
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col([html.Div(id="atr-preview", className="mt-2")], width=6),
                ]
            ),
        ]

        return self.controls_factory.create_collapsible_section(
            "basic-atr-collapse",
            "📊 Average True Range (ATR)",
            controls,
            enabled,
            "basic-atr-enabled",
        )

    def _create_macd_section(self, macd_config: Dict) -> html.Div:
        """Créer la section MACD avec tous ses contrôles"""
        enabled = macd_config.get("enabled", True)

        controls = [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            self.controls_factory.create_numeric_input(
                                "basic-macd-fast",
                                "EMA Rapide",
                                macd_config.get("fast_period", 12),
                                5,
                                50,
                                1,
                                "périodes",
                                "Période EMA rapide pour MACD",
                            )
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        [
                            self.controls_factory.create_numeric_input(
                                "basic-macd-slow",
                                "EMA Lente",
                                macd_config.get("slow_period", 26),
                                20,
                                100,
                                1,
                                "périodes",
                                "Période EMA lente pour MACD",
                            )
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        [
                            self.controls_factory.create_numeric_input(
                                "basic-macd-signal",
                                "Signal",
                                macd_config.get("signal_period", 9),
                                3,
                                20,
                                1,
                                "périodes",
                                "Période du signal MACD",
                            )
                        ],
                        width=4,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            self.controls_factory.create_color_picker(
                                "basic-macd-color-macd",
                                "Couleur MACD",
                                macd_config.get("color_macd", "#2196F3"),
                                "Couleur de la ligne MACD",
                            )
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        [
                            self.controls_factory.create_color_picker(
                                "basic-macd-color-signal",
                                "Couleur Signal",
                                macd_config.get("color_signal", "#FF5722"),
                                "Couleur de la ligne Signal",
                            )
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        [
                            self.controls_factory.create_color_picker(
                                "basic-macd-color-histogram",
                                "Couleur Histogramme",
                                macd_config.get("color_histogram", "#FFC107"),
                                "Couleur de l'histogramme MACD",
                            )
                        ],
                        width=4,
                    ),
                ]
            ),
            html.Div(id="macd-preview", className="mt-2"),
        ]

        return self.controls_factory.create_collapsible_section(
            "basic-macd-collapse",
            "📈 MACD (Moving Average Convergence Divergence)",
            controls,
            enabled,
            "basic-macd-enabled",
        )

    def _create_quick_actions(self) -> dbc.Card:
        """Créer les actions rapides"""
        return dbc.Card(
            [
                dbc.CardHeader(
                    [html.H6("⚡ Actions Rapides", className="mb-0 text-primary")]
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
                                                    className="fas fa-toggle-on me-2"
                                                ),
                                                "Tout Activer",
                                            ],
                                            id="basic-enable-all-btn",
                                            color="success",
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
                                            id="basic-disable-all-btn",
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
                                                html.I(className="fas fa-palette me-2"),
                                                "Couleurs Aléatoires",
                                            ],
                                            id="basic-random-colors-btn",
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
                                                html.I(className="fas fa-undo me-2"),
                                                "Valeurs Défaut",
                                            ],
                                            id="basic-reset-defaults-btn",
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
                Output("sma-preview", "children"),
                Output("ema-preview", "children"),
                Output("rsi-preview", "children"),
                Output("atr-preview", "children"),
                Output("macd-preview", "children"),
            ],
            [
                Input("basic-sma-period", "value"),
                Input("basic-ema-period", "value"),
                Input("basic-rsi-period", "value"),
                Input("basic-rsi-overbought", "value"),
                Input("basic-rsi-oversold", "value"),
                Input("basic-atr-period", "value"),
                Input("basic-atr-multiplier", "value"),
                Input("basic-macd-fast", "value"),
                Input("basic-macd-slow", "value"),
                Input("basic-macd-signal", "value"),
            ],
        )
        def update_previews(
            sma_period,
            ema_period,
            rsi_period,
            rsi_ob,
            rsi_os,
            atr_period,
            atr_mult,
            macd_fast,
            macd_slow,
            macd_signal,
        ):
            """Mettre à jour les previews en temps réel"""

            # SMA Preview
            sma_preview = dbc.Badge(
                f"SMA({sma_period or 20})", color="primary", className="me-2"
            )

            # EMA Preview
            ema_preview = dbc.Badge(
                f"EMA({ema_period or 12})", color="warning", className="me-2"
            )

            # RSI Preview
            rsi_preview = html.Div(
                [
                    dbc.Badge(
                        f"RSI({rsi_period or 14})", color="purple", className="me-2"
                    ),
                    dbc.Badge(f"OB: {rsi_ob or 70}", color="danger", className="me-1"),
                    dbc.Badge(f"OS: {rsi_os or 30}", color="success", className="me-1"),
                ]
            )

            # ATR Preview
            atr_preview = html.Div(
                [
                    dbc.Badge(
                        f"ATR({atr_period or 14})", color="success", className="me-2"
                    ),
                    dbc.Badge(f"x{atr_mult or 2.0}", color="info", className="me-1"),
                ]
            )

            # MACD Preview
            macd_preview = html.Div(
                [
                    dbc.Badge(
                        f"MACD({macd_fast or 12}, {macd_slow or 26})",
                        color="primary",
                        className="me-2",
                    ),
                    dbc.Badge(
                        f"Signal({macd_signal or 9})",
                        color="secondary",
                        className="me-1",
                    ),
                ]
            )

            return sma_preview, ema_preview, rsi_preview, atr_preview, macd_preview

        # Callback pour le statut global
        @callback(
            Output("basic-indicators-status", "children"),
            [
                Input("basic-sma-enabled", "value"),
                Input("basic-ema-enabled", "value"),
                Input("basic-rsi-enabled", "value"),
                Input("basic-atr-enabled", "value"),
                Input("basic-macd-enabled", "value"),
            ],
        )
        def update_status(
            sma_enabled, ema_enabled, rsi_enabled, atr_enabled, macd_enabled
        ):
            """Mettre à jour le statut global des indicateurs"""
            enabled_count = sum(
                [
                    sma_enabled or False,
                    ema_enabled or False,
                    rsi_enabled or False,
                    atr_enabled or False,
                    macd_enabled or False,
                ]
            )

            total_indicators = 5

            if enabled_count == 0:
                color = "danger"
                text = "Aucun indicateur activé"
                icon = "fas fa-exclamation-triangle"
            elif enabled_count == total_indicators:
                color = "success"
                text = (
                    f"Tous les indicateurs activés ({enabled_count}/{total_indicators})"
                )
                icon = "fas fa-check-circle"
            else:
                color = "warning"
                text = f"Indicateurs partiellement activés ({enabled_count}/{total_indicators})"
                icon = "fas fa-info-circle"

            return dbc.Alert(
                [html.I(className=f"{icon} me-2"), text], color=color, className="mb-0"
            )


# Instance du module
basic_indicators_tab = BasicIndicatorsTab()
