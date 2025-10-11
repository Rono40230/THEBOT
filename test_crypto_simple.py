#!/usr/bin/env python3
"""
APPLICATION DE TEST SIMPLIFIÉE POUR RÉSOUDRE LES PROBLÈMES
Version ultra simple pour corriger le dropdown et la recherche
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import sys
import os

# Ajout du chemin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import module simplifié
from dash_modules.tabs.crypto_module_simple import crypto_module_simple

# Création de l'app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "THEBOT - Test Crypto"

# Layout ultra simple
app.layout = html.Div([
    html.H1("THEBOT - Test Crypto Simplifié", className="text-center text-white mb-4"),
    
    # Module crypto
    crypto_module_simple.create_layout()
    
], style={
    'backgroundColor': '#2c2c2e',
    'minHeight': '100vh',
    'padding': '20px'
})

# Enregistrement des callbacks
crypto_module_simple.register_callbacks(app)

if __name__ == '__main__':
    print("🚀 Lancement de l'application test simplifiée...")
    print("📊 URL: http://127.0.0.1:8052")
    app.run_server(debug=True, host='0.0.0.0', port=8052)