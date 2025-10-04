#!/usr/bin/env python3
"""
Test du système d'alertes - Debug des erreurs JavaScript
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

# Test des imports
try:
    from dash_modules.components.price_alerts_modal import price_alerts_modal, register_alerts_modal_callbacks
    print("✅ Modal Alertes importé avec succès")
except Exception as e:
    print(f"❌ Erreur import modal alertes: {e}")
    exit(1)

try:
    from dash_modules.components.ai_trading_modal import ai_trading_modal, register_ai_modal_callbacks
    print("✅ Modal IA importé avec succès")
except Exception as e:
    print(f"❌ Erreur import modal IA: {e}")
    exit(1)

# Test de création de l'app de test
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout de test minimal
app.layout = html.Div([
    # Dropdowns nécessaires pour les callbacks
    dcc.Dropdown(
        id='crypto-symbol-dropdown',
        options=[{'label': 'BTCUSDT', 'value': 'BTCUSDT'}],
        value='BTCUSDT',
        style={'display': 'none'}  # Caché pour le test
    ),
    dcc.Dropdown(
        id='crypto-timeframe-dropdown',
        options=[{'label': '1h', 'value': '1h'}],
        value='1h',
        style={'display': 'none'}  # Caché pour le test
    ),
    
    # Zone de test avec boutons
    dbc.Card([
        dbc.CardBody([
            html.H4("Test Zone Prix"),
            dbc.ButtonGroup([
                dbc.Button(
                    [html.I(className="fas fa-brain me-2"), "AI Analysis"],
                    id="generate-ai-insights-btn",
                    color="primary",
                    size="sm"
                ),
                dbc.Button(
                    [html.I(className="fas fa-bell me-2"), "Price Alerts"],
                    id="manage-alerts-btn",
                    color="success",
                    size="sm"
                )
            ])
        ])
    ], className="mb-3"),
    
    # Status
    html.Div(id="test-status"),
    
    # Modals
    ai_trading_modal.create_modal(),
    price_alerts_modal.create_modal()
])

# Enregistrer les callbacks
try:
    register_ai_modal_callbacks(app)
    print("✅ Callbacks IA enregistrés")
except Exception as e:
    print(f"❌ Erreur callbacks IA: {e}")

try:
    register_alerts_modal_callbacks(app)
    print("✅ Callbacks Alertes enregistrés")
except Exception as e:
    print(f"❌ Erreur callbacks Alertes: {e}")

# Callback de test
@app.callback(
    Output("test-status", "children"),
    [Input("generate-ai-insights-btn", "n_clicks"),
     Input("manage-alerts-btn", "n_clicks")]
)
def test_buttons(ai_clicks, alerts_clicks):
    """Test des boutons"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return "En attente de test..."
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger == "generate-ai-insights-btn":
        return f"✅ Bouton IA cliqué {ai_clicks} fois"
    elif trigger == "manage-alerts-btn":
        return f"✅ Bouton Alertes cliqué {alerts_clicks} fois"
    
    return "Test en cours..."

if __name__ == "__main__":
    print("\n🧪 Lancement du test d'alertes...")
    print("🌐 Test disponible sur: http://localhost:8051")
    print("🔍 Vérifiez la console pour les erreurs JavaScript")
    app.run_server(debug=True, port=8051)