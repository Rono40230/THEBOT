#!/usr/bin/env python3
"""
Script de test pour la modal API Configuration simplifiée
"""

from dash_modules.core.api_config import APIConfig
from dash import Dash, html, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc

# Initialiser l'app de test
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Créer l'instance de configuration
config = APIConfig()

# Layout de test
app.layout = html.Div([
    html.H1("🧪 Test de la Modal API Configuration", className="text-center mb-4"),
    
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [html.I(className="fas fa-key me-1"), "🔑 API Keys"],
                    id="open-api-config-btn",
                    color="primary",
                    size="lg",
                    className="mb-3"
                ),
                html.Div(id="test-output")
            ])
        ]),
        
        # Modal de configuration
        config.get_api_config_modal()
    ])
])

# Callback pour ouvrir/fermer la modal
@app.callback(
    Output("api-config-modal", "is_open"),
    [Input("open-api-config-btn", "n_clicks"), 
     Input("close-config-btn", "n_clicks")],
    [State("api-config-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_api_config_modal(open_clicks, close_clicks, is_open):
    """Toggle API configuration modal"""
    if not ctx.triggered:
        return False
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "open-api-config-btn":
        print("📱 Ouverture de la modal API")
        return True
    elif button_id == "close-config-btn":
        print("❌ Fermeture de la modal API")
        return False
    
    return is_open

# Callback pour le test
@app.callback(
    Output("test-output", "children"),
    Input("test-all-btn", "n_clicks"),
    prevent_initial_call=True
)
def test_config(n_clicks):
    if n_clicks:
        return dbc.Alert(
            "✅ Test de configuration lancé",
            color="success"
        )
    return ""

if __name__ == "__main__":
    print("🚀 Lancement du test de la modal API Configuration...")
    print("📱 Interface disponible sur: http://0.0.0.0:8051/")
    print("🔍 Cliquez sur le bouton '🔑 API Keys' pour tester l'ouverture de la modal")
    app.run(debug=True, host="0.0.0.0", port=8051)