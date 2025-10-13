#!/usr/bin/env python3
"""
Configuration HuggingFace pour THEBOT (Version Corrigée)
Interface de configuration de l'IA publique gratuite
"""

import json
import os
from datetime import datetime

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, dcc, html


def create_huggingface_config_interface() -> html.Div:
    """Créer interface de configuration HuggingFace"""

    return html.Div(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2(
                                [
                                    html.I(className="fab fa-hive me-3"),
                                    "Configuration HuggingFace",
                                ],
                                className="text-success mb-4",
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-info-circle me-2"),
                                    "HuggingFace offre 100 analyses gratuites par jour avec des modèles IA avancés.",
                                ],
                                color="info",
                                className="mb-4",
                            ),
                        ]
                    )
                ]
            ),
            # Configuration principale
            dbc.Row(
                [
                    # Colonne gauche : Configuration
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(className="fas fa-cog me-2"),
                                            "Configuration IA",
                                        ]
                                    ),
                                    dbc.CardBody(
                                        [
                                            # Mode IA
                                            html.Div(
                                                [
                                                    dbc.Label(
                                                        "Mode de fonctionnement IA",
                                                        className="fw-bold mb-2",
                                                    ),
                                                    dbc.Select(
                                                        id="ai-mode-select",
                                                        options=[
                                                            {
                                                                "label": "🧠 Automatique Intelligent",
                                                                "value": "auto",
                                                            },
                                                            {
                                                                "label": "👤 Manuel (Utilisateur choisit)",
                                                                "value": "manual",
                                                            },
                                                            {
                                                                "label": "🔄 Hybride Optimisé",
                                                                "value": "hybrid",
                                                            },
                                                        ],
                                                        value="auto",
                                                        className="mb-3",
                                                    ),
                                                    html.Small(
                                                        "Mode automatique recommandé pour les meilleures performances",
                                                        className="text-muted",
                                                    ),
                                                ],
                                                className="mb-4",
                                            ),
                                            # Test HuggingFace
                                            html.Div(
                                                [
                                                    dbc.Button(
                                                        [
                                                            html.I(
                                                                className="fas fa-test-tube me-2"
                                                            ),
                                                            "Tester HuggingFace",
                                                        ],
                                                        id="test-huggingface-btn",
                                                        color="info",
                                                        className="w-100",
                                                    )
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ],
                        width=6,
                    ),
                    # Colonne droite : Status
                    dbc.Col(
                        [
                            # Status IA
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.I(className="fas fa-chart-bar me-2"),
                                            "Status IA en Temps Réel",
                                        ]
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.Div(
                                                id="ai-status-display",
                                                children=[
                                                    html.P(
                                                        "Chargement du status...",
                                                        className="text-muted",
                                                    )
                                                ],
                                            )
                                        ]
                                    ),
                                ]
                            )
                        ],
                        width=6,
                    ),
                ]
            ),
            # Test Results
            dbc.Row([dbc.Col([html.Div(id="test-results", className="mt-4")])]),
            # Hidden stores pour données
            dcc.Store(id="ai-config-store"),
            dcc.Interval(id="status-update-interval", interval=5000, n_intervals=0),
        ],
        className="p-4",
    )


def register_huggingface_callbacks(app):
    """Enregistrer callbacks pour interface HuggingFace"""

    @app.callback(
        Output("ai-status-display", "children"),
        [Input("status-update-interval", "n_intervals")],
    )
    def update_ai_status(n_intervals):
        """Mettre à jour status IA en temps réel"""
        try:
            from dash_modules.ai_engine.smart_ai_manager import smart_ai_manager

            # Initialiser si nécessaire
            if not smart_ai_manager.local_ai:
                smart_ai_manager.initialize_engines()

            status = smart_ai_manager.get_ai_status()

            return html.Div(
                [
                    # IA Locale
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H6("🆓 IA Locale", className="text-success"),
                                    html.P(
                                        f"⚡ {status['local']['performance']['speed']:,} analyses/sec",
                                        className="mb-1 small",
                                    ),
                                    html.P(
                                        f"💰 {status['local']['quota']}",
                                        className="mb-2 small text-muted",
                                    ),
                                ],
                                width=8,
                            ),
                            dbc.Col(
                                [
                                    dbc.Badge(
                                        (
                                            "ACTIF"
                                            if status["local"]["available"]
                                            else "INACTIF"
                                        ),
                                        color=(
                                            "success"
                                            if status["local"]["available"]
                                            else "danger"
                                        ),
                                    )
                                ],
                                width=4,
                            ),
                        ],
                        className="mb-3",
                    ),
                    # HuggingFace
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H6("🤗 HuggingFace", className="text-info"),
                                    html.P(
                                        f"📊 {status['huggingface']['quota']}",
                                        className="mb-1 small",
                                    ),
                                    html.P(
                                        f"🎯 Précision: {status['huggingface']['performance']['accuracy']}%",
                                        className="mb-2 small text-muted",
                                    ),
                                ],
                                width=8,
                            ),
                            dbc.Col(
                                [
                                    dbc.Badge(
                                        (
                                            "DISPONIBLE"
                                            if status["huggingface"]["available"]
                                            else "QUOTA ÉPUISÉ"
                                        ),
                                        color=(
                                            "success"
                                            if status["huggingface"]["available"]
                                            else "warning"
                                        ),
                                    )
                                ],
                                width=4,
                            ),
                        ],
                        className="mb-3",
                    ),
                    # Premium
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H6("🧠 IA Premium", className="text-warning"),
                                    html.P(
                                        f"💎 {status['premium']['quota']}",
                                        className="mb-1 small",
                                    ),
                                    html.P(
                                        f"🚀 Précision: {status['premium']['performance']['accuracy']}%",
                                        className="mb-2 small text-muted",
                                    ),
                                ],
                                width=8,
                            ),
                            dbc.Col(
                                [
                                    dbc.Badge(
                                        (
                                            "CONFIGURÉ"
                                            if status["premium"]["available"]
                                            else "NON CONFIGURÉ"
                                        ),
                                        color=(
                                            "success"
                                            if status["premium"]["available"]
                                            else "secondary"
                                        ),
                                    )
                                ],
                                width=4,
                            ),
                        ]
                    ),
                ]
            )

        except Exception as e:
            return dbc.Alert(f"Erreur status IA: {e}", color="danger")

    @app.callback(
        Output("test-results", "children"),
        [Input("test-huggingface-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def test_huggingface_connection(n_clicks):
        """Tester connexion HuggingFace"""
        if not n_clicks:
            return ""

        try:
            from dash_modules.ai_engine.free_ai_engine import FreeAIEngine

            free_ai = FreeAIEngine()

            # Test avec phrase simple
            test_text = "Tesla stock rises on strong quarterly earnings"
            start_time = datetime.now()

            result = free_ai.analyze_with_huggingface(test_text)

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            if result and "sentiment" in result:
                return dbc.Alert(
                    [
                        html.H5(
                            "✅ Test HuggingFace Réussi!", className="alert-heading"
                        ),
                        html.P(f"📝 Texte testé: '{test_text}'"),
                        html.P(f"🎯 Sentiment détecté: {result['sentiment'].title()}"),
                        html.P(f"📊 Confiance: {result.get('confidence', 0):.1f}%"),
                        html.P(f"⚡ Temps d'exécution: {execution_time:.0f}ms"),
                        html.P(f"🔧 Source: {result.get('source', 'HuggingFace')}"),
                    ],
                    color="success",
                )
            else:
                return dbc.Alert("❌ Test échoué - Résultat invalide", color="danger")

        except Exception as e:
            return dbc.Alert(f"❌ Erreur test HuggingFace: {e}", color="danger")


if __name__ == "__main__":
    # Test interface
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = create_huggingface_config_interface()
    register_huggingface_callbacks(app)
    app.run_server(debug=True, port=8051)
