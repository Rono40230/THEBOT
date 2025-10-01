#!/usr/bin/env python3
"""
Test simple de la modal API avec sauvegarde
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
    html.H1("🧪 Test Sauvegarde Clés API", className="text-center mb-4"),
    
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [html.I(className="fas fa-key me-1"), "🔑 Ouvrir API Config"],
                    id="open-api-config-btn",
                    color="primary",
                    size="lg",
                    className="mb-3"
                ),
                html.Div(id="test-status")
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

# Callback de sauvegarde des clés
@app.callback(
    [Output("test-status", "children"),
     Output("api-config-modal", "is_open", allow_duplicate=True)],
    [Input("save-config-btn", "n_clicks")],
    [State("api-key-alpha-vantage", "value"),
     State("api-key-cryptopanic", "value"), 
     State("api-key-coingecko", "value"),
     State("api-key-fmp", "value")],
    prevent_initial_call=True
)
def save_api_config_test(save_clicks, alpha_key, crypto_key, coin_key, fmp_key):
    """Test save API configuration"""
    if save_clicks:
        try:
            # Afficher les valeurs reçues
            print(f"🔑 Alpha Vantage: {'✅' if alpha_key else '❌'} - {alpha_key[:10] if alpha_key else 'Vide'}...")
            print(f"🔑 CryptoPanic: {'✅' if crypto_key else '❌'} - {crypto_key[:10] if crypto_key else 'Vide'}...")
            print(f"🔑 CoinGecko: {'✅' if coin_key else '❌'} - {coin_key[:10] if coin_key else 'Vide'}...")
            print(f"🔑 FMP: {'✅' if fmp_key else '❌'} - {fmp_key[:10] if fmp_key else 'Vide'}...")
            
            # Sauvegarder les clés API
            saved_count = 0
            
            # Alpha Vantage
            if alpha_key and alpha_key.strip():
                for section in config.config["providers"]["data_sources"].values():
                    for provider in section:
                        if provider["name"] == "Alpha Vantage":
                            provider["config"]["api_key"] = alpha_key.strip()
                            provider["status"] = "active"
                            saved_count += 1
                            break
            
            # CryptoPanic
            if crypto_key and crypto_key.strip():
                for section in config.config["providers"]["data_sources"].values():
                    for provider in section:
                        if provider["name"] == "CryptoPanic":
                            provider["config"]["api_key"] = crypto_key.strip()
                            provider["status"] = "active"
                            saved_count += 1
                            break
            
            # CoinGecko 
            if coin_key and coin_key.strip():
                for section in config.config["providers"]["data_sources"].values():
                    for provider in section:
                        if provider["name"] == "CoinGecko":
                            provider["config"]["api_key"] = coin_key.strip()
                            provider["status"] = "active"
                            saved_count += 1
                            break
            
            # FMP
            if fmp_key and fmp_key.strip():
                for section in config.config["providers"]["data_sources"].values():
                    for provider in section:
                        if provider["name"] == "FMP":
                            provider["config"]["api_key"] = fmp_key.strip()
                            provider["status"] = "active"
                            saved_count += 1
                            break
            
            # Sauvegarder la configuration
            config.save_config()
            print(f"✅ Configuration sauvegardée - {saved_count} clés mises à jour")
            
            status_message = dbc.Alert(
                f"✅ Configuration sauvegardée avec succès! {saved_count} clés mises à jour",
                color="success",
                duration=4000
            )
            
            return status_message, False
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            error_message = dbc.Alert(
                f"❌ Erreur lors de la sauvegarde: {e}",
                color="danger",
                duration=4000
            )
            return error_message, True
    
    return "", True

if __name__ == "__main__":
    print("🚀 Lancement du test de sauvegarde des clés API...")
    print("📱 Interface disponible sur: http://0.0.0.0:8052/")
    print("🔍 Instructions:")
    print("  1. Cliquez sur 'Ouvrir API Config'")
    print("  2. Saisissez des clés API de test")
    print("  3. Cliquez sur 'Enregistrer'")
    print("  4. Vérifiez la console pour les logs")
    app.run(debug=True, host="0.0.0.0", port=8052)