#!/usr/bin/env python3
"""
THEBOT - VERSION ULTRA SIMPLE QUI MARCHE
Fini les complications, on fait du basique qui fonctionne !
"""

import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

# Simple récupération Binance directe
def get_binance_data(symbol='BTCUSDT', limit=100):
    """Récupérer données Binance directement"""
    try:
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': '1h', 
            'limit': limit
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        # Conversion des types
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
            
        print(f"✅ {symbol}: {len(df)} points récupérés")
        return df
        
    except Exception as e:
        print(f"❌ Erreur {symbol}: {e}")
        return None

# Application Dash ultra simple
app = dash.Dash(__name__)

app.layout = html.Div([
    
    html.H1("🤖 THEBOT - SIMPLE ET EFFICACE", style={'textAlign': 'center', 'color': 'white'}),
    
    html.Div([
        html.Label("Market:", style={'color': 'white', 'marginRight': '10px'}),
        dcc.Dropdown(
            id='symbol-dropdown',
            options=[
                {'label': 'Bitcoin/USDT', 'value': 'BTCUSDT'},
                {'label': 'Ethereum/USDT', 'value': 'ETHUSDT'},
                {'label': 'Binance Coin/USDT', 'value': 'BNBUSDT'}
            ],
            value='BTCUSDT',
            style={'width': '200px', 'display': 'inline-block'}
        )
    ], style={'margin': '20px'}),
    
    # Graphique principal
    dcc.Graph(id='main-chart'),
    
    # Message de statut
    html.Div(id='status-message', style={'textAlign': 'center', 'color': 'lime', 'fontSize': '18px'})
    
], style={'backgroundColor': '#1e1e1e', 'padding': '20px', 'minHeight': '100vh'})

@app.callback(
    [Output('main-chart', 'figure'),
     Output('status-message', 'children')],
    Input('symbol-dropdown', 'value')
)
def update_chart(symbol):
    """Mise à jour du graphique principal"""
    
    try:
        print(f"🔄 Chargement {symbol}...")
        
        # Récupération des données
        df = get_binance_data(symbol)
        
        if df is None or df.empty:
            return {}, f"❌ Impossible de charger {symbol}"
        
        # Création du graphique candlestick
        fig = go.Figure(data=[go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol
        )])
        
        fig.update_layout(
            title=f"📊 {symbol} - Prix en temps réel Binance",
            template="plotly_dark",
            height=600,
            xaxis_title="Date/Heure",
            yaxis_title="Prix (USDT)"
        )
        
        current_price = float(df['close'].iloc[-1])
        message = f"✅ {symbol}: ${current_price:,.2f} | {len(df)} points chargés | Données Binance réelles"
        
        return fig, message
        
    except Exception as e:
        print(f"❌ Erreur callback: {e}")
        return {}, f"❌ Erreur: {str(e)}"

if __name__ == '__main__':
    print("""
🚀 THEBOT - VERSION SIMPLE
    
✅ Pas de modules complexes
✅ API Binance directe  
✅ Interface basique mais fonctionnelle
✅ Données réelles garanties

🌐 Démarrage sur http://localhost:8050
    """)
    
    app.run(host='0.0.0.0', port=8050, debug=True)