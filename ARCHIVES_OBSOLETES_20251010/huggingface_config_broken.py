#!/usr/bin/env python3
"""
Configuration HuggingFace pour THEBOT
Interface de configuration de l'IA publique gratuite
"""

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import json
import os
from datetime import datetime

def create_huggingface_config_interface():
    """Créer interface de configuration HuggingFace"""
    
    return html.Div([
        
        # Header
        dbc.Row([
            dbc.Col([
                html.H2([
                    html.I(className="fab fa-hive me-3"),
                    "Configuration HuggingFace"
                ], className="text-success mb-4"),
                
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    "HuggingFace offre 100 analyses gratuites par jour avec des modèles IA avancés."
                ], color="info", className="mb-4")
            ])
        ]),
        
        # Configuration principale
        dbc.Row([
            
            # Colonne gauche : Configuration
            dbc.Col([
                
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-cog me-2"),
                        "Configuration IA"
                    ]),
                    dbc.CardBody([
                        
                        # Mode IA
                        html.Div([
                            dbc.Label("Mode de fonctionnement IA", className="fw-bold mb-2"),
                            dbc.Select(
                                id="ai-mode-select",
                                options=[
                                    {"label": "🧠 Automatique Intelligent", "value": "auto"},
                                    {"label": "👤 Manuel (Utilisateur choisit)", "value": "manual"},
                                    {"label": "🔄 Hybride Optimisé", "value": "hybrid"}
                                ],
                                value="auto",
                                className="mb-3"
                            ),
                            html.Small("Mode automatique recommandé pour les meilleures performances", 
                                     className="text-muted")
                        ], className="mb-4"),
                        
                        # Boutons actions
                        html.Div([
                            dbc.Button([
                                html.I(className="fas fa-test-tube me-2"),
                                "Tester HuggingFace"
                            ], id="test-huggingface-btn", color="info", className="me-2")
                        ])
                        
                    ])
                ])
                
            ], width=6),
            
            # Colonne droite : Status
            dbc.Col([
                
                # Status IA
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-chart-bar me-2"),
                        "Status IA en Temps Réel"
                    ]),
                    dbc.CardBody([
                        html.Div(id="ai-status-display", children=[
                            html.P("Chargement du status...", className="text-muted")
                        ])
                    ])
                ])
                
            ], width=6)
            
        ]),
        
        # Test Results
        dbc.Row([
            dbc.Col([
                html.Div(id="test-results", className="mt-4")
            ])
        ]),
        
        # Hidden stores pour données
        dcc.Store(id="ai-config-store"),
        dcc.Interval(id="status-update-interval", interval=5000, n_intervals=0)
        
    ], className="p-4")\n\ndef register_huggingface_callbacks(app):\n    \"\"\"Enregistrer callbacks pour interface HuggingFace\"\"\"\n    \n    @app.callback(\n        Output('ai-status-display', 'children'),\n        [Input('status-update-interval', 'n_intervals')]\n    )\n    def update_ai_status(n_intervals):\n        \"\"\"Mettre à jour status IA en temps réel\"\"\"\n        try:\n            from dash_modules.ai_engine.smart_ai_manager import smart_ai_manager\n            \n            # Initialiser si nécessaire\n            if not smart_ai_manager.local_ai:\n                smart_ai_manager.initialize_engines()\n            \n            status = smart_ai_manager.get_ai_status()\n            usage = smart_ai_manager.get_usage_stats()\n            \n            return html.Div([\n                \n                # IA Locale\n                dbc.Row([\n                    dbc.Col([\n                        html.H6(\"🆓 IA Locale\", className=\"text-success\"),\n                        html.P(f\"⚡ {status['local']['performance']['speed']:,} analyses/sec\", className=\"mb-1 small\"),\n                        html.P(f\"💰 {status['local']['quota']}\", className=\"mb-2 small text-muted\")\n                    ], width=4),\n                    dbc.Col([\n                        dbc.Badge(\"ACTIF\" if status['local']['available'] else \"INACTIF\", \n                                color=\"success\" if status['local']['available'] else \"danger\")\n                    ], width=\"auto\")\n                ], className=\"mb-3\"),\n                \n                # HuggingFace\n                dbc.Row([\n                    dbc.Col([\n                        html.H6(\"🤗 HuggingFace\", className=\"text-info\"),\n                        html.P(f\"📊 {status['huggingface']['quota']}\", className=\"mb-1 small\"),\n                        html.P(f\"🎯 Précision: {status['huggingface']['performance']['accuracy']}%\", className=\"mb-2 small text-muted\")\n                    ], width=4),\n                    dbc.Col([\n                        dbc.Badge(\"DISPONIBLE\" if status['huggingface']['available'] else \"QUOTA ÉPUISÉ\", \n                                color=\"success\" if status['huggingface']['available'] else \"warning\")\n                    ], width=\"auto\")\n                ], className=\"mb-3\"),\n                \n                # Premium\n                dbc.Row([\n                    dbc.Col([\n                        html.H6(\"🧠 IA Premium\", className=\"text-warning\"),\n                        html.P(f\"💎 {status['premium']['quota']}\", className=\"mb-1 small\"),\n                        html.P(f\"🚀 Précision: {status['premium']['performance']['accuracy']}%\", className=\"mb-2 small text-muted\")\n                    ], width=4),\n                    dbc.Col([\n                        dbc.Badge(\"CONFIGURÉ\" if status['premium']['available'] else \"NON CONFIGURÉ\", \n                                color=\"success\" if status['premium']['available'] else \"secondary\")\n                    ], width=\"auto\")\n                ])\n                \n            ])\n            \n        except Exception as e:\n            return dbc.Alert(f\"Erreur status IA: {e}\", color=\"danger\")\n    \n    @app.callback(\n        Output('test-results', 'children'),\n        [Input('test-huggingface-btn', 'n_clicks')],\n        prevent_initial_call=True\n    )\n    def test_huggingface_connection(n_clicks):\n        \"\"\"Tester connexion HuggingFace\"\"\"\n        if not n_clicks:\n            return \"\"\n        \n        try:\n            from dash_modules.ai_engine.free_ai_engine import FreeAIEngine\n            \n            free_ai = FreeAIEngine()\n            \n            # Test avec phrase simple\n            test_text = \"Tesla stock rises on strong quarterly earnings\"\n            start_time = datetime.now()\n            \n            result = free_ai.analyze_with_huggingface(test_text)\n            \n            execution_time = (datetime.now() - start_time).total_seconds() * 1000\n            \n            if result and 'sentiment' in result:\n                return dbc.Alert([\n                    html.H5(\"✅ Test HuggingFace Réussi!\", className=\"alert-heading\"),\n                    html.P(f\"📝 Texte testé: '{test_text}'\"),\n                    html.P(f\"🎯 Sentiment détecté: {result['sentiment'].title()}\"),\n                    html.P(f\"📊 Confiance: {result.get('confidence', 0):.1f}%\"),\n                    html.P(f\"⚡ Temps d'exécution: {execution_time:.0f}ms\"),\n                    html.P(f\"🔧 Source: {result.get('source', 'HuggingFace')}\"),\n                ], color=\"success\")\n            else:\n                return dbc.Alert(\"❌ Test échoué - Résultat invalide\", color=\"danger\")\n                \n        except Exception as e:\n            return dbc.Alert(f\"❌ Erreur test HuggingFace: {e}\", color=\"danger\")\n    \n    @app.callback(\n        Output('ai-recommendations', 'children'),\n        [Input('status-update-interval', 'n_intervals')]\n    )\n    def update_recommendations(n_intervals):\n        \"\"\"Mettre à jour recommandations IA\"\"\"\n        try:\n            from dash_modules.ai_engine.smart_ai_manager import smart_ai_manager\n            \n            if not smart_ai_manager.local_ai:\n                smart_ai_manager.initialize_engines()\n            \n            recommendations = smart_ai_manager._get_recommendations()\n            \n            if not recommendations:\n                return dbc.Alert(\"🎉 Configuration IA optimale!\", color=\"success\")\n            \n            return html.Div([\n                html.Div([\n                    html.I(className=\"fas fa-arrow-right me-2\"),\n                    rec\n                ], className=\"mb-2\") for rec in recommendations\n            ])\n            \n        except Exception as e:\n            return html.P(f\"Erreur recommendations: {e}\", className=\"text-danger\")\n\nif __name__ == \"__main__\":\n    # Test interface\n    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])\n    app.layout = create_huggingface_config_interface()\n    register_huggingface_callbacks(app)\n    app.run_server(debug=True, port=8051)