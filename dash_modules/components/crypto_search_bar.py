"""
THEBOT - Crypto Search Bar Component
Composant modulaire pour la barre de recherche crypto avec sélecteur de timeframe
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from typing import List, Dict, Any

# Import de l'API Binance pour la recherche dynamique
try:
    from ..data_providers.binance_api import BinanceProvider
    binance_provider = BinanceProvider()
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False
    binance_provider = None

class CryptoSearchBar:
    """Composant modulaire pour la barre de recherche crypto"""
    
    def __init__(self):
        # Symboles par défaut pour fallback
        self.default_symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LINKUSDT'
        ]
        
        # Récupérer les symboles depuis Binance si disponible
        if BINANCE_AVAILABLE and binance_provider:
            try:
                self.all_symbols = binance_provider.get_all_symbols()
                self.initial_symbols = binance_provider.get_popular_symbols()
                print(f"✅ {len(self.all_symbols)} symboles Binance chargés")
            except Exception as e:
                print(f"⚠️ Erreur chargement symboles Binance: {e}")
                self.all_symbols = self.default_symbols
                self.initial_symbols = self.default_symbols
        else:
            self.all_symbols = self.default_symbols
            self.initial_symbols = self.default_symbols
        
        self.timeframes = [
            {'label': '1mn', 'value': '1m'},
            {'label': '15mn', 'value': '15m'},
            {'label': '30mn', 'value': '30m'},
            {'label': '1h', 'value': '1h'},
            {'label': '4h', 'value': '4h'},
            {'label': '1d', 'value': '1d'},
            {'label': '1m', 'value': '1M'}
        ]
    
    def create_search_dropdown(self) -> dcc.Dropdown:
        """Crée le dropdown de recherche de symboles crypto avec recherche dynamique"""
        return dcc.Dropdown(
            id='crypto-symbol-search',
            options=[
                {'label': symbol, 'value': symbol} 
                for symbol in self.initial_symbols
            ],
            value='BTCUSDT',
            placeholder="Rechercher un symbole crypto...",
            searchable=True,
            clearable=False,
            optionHeight=35,
            maxHeight=300,
            style={
                'color': '#ffffff',
                'backgroundColor': '#2c2c2e',
                'border': '1px solid #3a3a3c'
            },
            className='crypto-dropdown-white'
        )
    
    def create_timeframe_selector(self) -> dcc.Dropdown:
        """Crée le sélecteur de timeframe"""
        return dcc.Dropdown(
            id='crypto-timeframe-selector',
            options=self.timeframes,
            value='1h',
            clearable=False,
            style={
                'color': '#ffffff',
                'backgroundColor': '#2c2c2e',
                'border': '1px solid #3a3a3c'
            },
            className='crypto-dropdown-white'
        )
    
    def create_action_buttons(self) -> html.Div:
        """Crée les boutons d'action"""
        return html.Div([
            dbc.Button(
                "🤖 IA Trading",
                id="open-ai-modal-btn",
                color="primary",
                size="sm",
                className="me-2",
                style={'fontSize': '12px'}
            ),
            dbc.Button(
                "🔔 Alertes",
                id="open-alerts-modal-btn",
                color="warning",
                size="sm",
                className="me-2",
                style={'fontSize': '12px'}
            ),
            dbc.Button(
                "📊 Analyse",
                id="crypto-analyze-btn",
                color="success",
                size="sm",
                style={'fontSize': '12px'}
            )
        ], className="d-flex")
    
    def create_complete_search_bar(self) -> dbc.Card:
        """Crée la barre de recherche complète avec fond sombre"""
        return dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        self.create_search_dropdown(),
                        # Ajout des informations prix/progression/volume sur la même ligne
                        html.Div([
                            html.Span("", id="crypto-price-display", className="fw-bold text-primary me-3"),
                            html.Span("", id="crypto-price-change", className="me-3"),
                            html.Span("Vol: ", className="text-muted"),
                            html.Span("", id="crypto-volume-display", className="fw-bold")
                        ], className="mt-1 small")
                    ], width=4),
                    dbc.Col([
                        self.create_timeframe_selector()
                    ], width=3),
                    dbc.Col([
                        self.create_action_buttons()
                    ], width=5)
                ], align="start")  # Changé de "end" à "start" pour l'alignement
            ])
        ], className="mb-3", style={
            'backgroundColor': '#6c757d',
            'border': '1px solid #adb5bd',
            'borderRadius': '8px',
            'padding': '10px'
        })
    
    def get_symbol_options(self, search_value: str = None) -> List[Dict[str, str]]:
        """Retourne les options de symboles filtrées selon la recherche avec API Binance"""
        if not search_value or len(search_value) < 2:
            return [{'label': symbol, 'value': symbol} for symbol in self.initial_symbols]
        
        # Utiliser l'API Binance pour la recherche intelligente si disponible
        if BINANCE_AVAILABLE and binance_provider:
            try:
                filtered_symbols = binance_provider.search_symbols(search_value, limit=20)
                return [{'label': symbol, 'value': symbol} for symbol in filtered_symbols]
            except Exception as e:
                print(f"⚠️ Erreur recherche Binance: {e}")
                # Fallback sur recherche locale
                pass
        
        # Fallback : filtrage local simple
        search_upper = search_value.upper()
        filtered = [s for s in self.all_symbols if search_upper in s][:20]
        return [{'label': symbol, 'value': symbol} for symbol in filtered]

# Instance globale pour l'utilisation dans les modules
crypto_search_bar = CryptoSearchBar()