"""
Module de composant de recherche de symboles
Interface utilisateur pour la recherche dynamique d'actifs Binance
Architecture modulaire THEBOT
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc
from typing import List, Optional


class SymbolSearchComponent:
    """Composant de recherche dynamique de symboles"""
    
    def __init__(self, component_id: str = "symbol-search"):
        self.component_id = component_id
        self.search_input_id = f"{component_id}-input"
        self.results_id = f"{component_id}-results"
        self.selected_store_id = f"{component_id}-selected"
    
    def render_search_input(self, placeholder: str = "Tapez BTC, ETH, ADA...") -> dbc.InputGroup:
        """Rendu de l'input de recherche"""
        return dbc.InputGroup([
            dbc.Input(
                id=self.search_input_id,
                placeholder=placeholder,
                type='text',
                className="bg-dark text-light border-secondary",
                style={
                    'fontSize': '14px',
                    'border': '2px solid #6c757d',
                    'borderRadius': '0.375rem 0 0 0.375rem',
                    'boxShadow': '0 0 0 0.2rem rgba(108, 117, 125, 0.25)'
                },
                debounce=True,
                value=""
            ),
            dbc.Button([
                html.I(className="fas fa-search")
            ], 
            id=f"{self.component_id}-search-btn", 
            color="primary", 
            size="sm",
            style={
                'border': '2px solid #0d6efd',
                'borderLeft': 'none'
            })
        ], style={'border': 'none'})
    
    def render_results_container(self) -> html.Div:
        """Conteneur pour les résultats de recherche - masqué par défaut"""
        return html.Div(
            id=self.results_id,
            className="mt-1",
            style={
                'maxHeight': '0px',  # Masqué par défaut
                'overflowY': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '0.375rem',
                'padding': '0rem',
                'transition': 'all 0.3s ease'
            }
        )
    
    def create_result_buttons(self, symbols: List[str], max_display: int = 12) -> List[dbc.Button]:
        """Créer les boutons de résultats"""
        if not symbols:
            return [
                dbc.Alert(
                    "Aucun symbole trouvé", 
                    color="warning", 
                    className="small text-center"
                )
            ]
        
        buttons = []
        for symbol in symbols[:max_display]:
            icon = self._get_crypto_icon(symbol)
            
            buttons.append(
                dbc.Button([
                    html.I(className=f"me-1 {icon}"),
                    symbol
                ],
                id={'type': f'{self.component_id}-result', 'index': symbol},
                size='sm',
                outline=True,
                color='info',
                className='me-1 mb-1',
                style={'fontSize': '12px', 'minWidth': '90px'}
                )
            )
        
        if len(symbols) > max_display:
            buttons.append(
                html.Small(
                    f"+ {len(symbols) - max_display} autres...",
                    className="text-muted d-block mt-1"
                )
            )
        
        return buttons
    
    def render_popular_symbols(self, popular_symbols: List[str]) -> List[dbc.Button]:
        """Afficher les symboles populaires par défaut"""
        return self.create_result_buttons(popular_symbols[:8])
    
    def get_complete_layout(self, 
                           label: str = "Rechercher un Actif",
                           placeholder: str = "Tapez BTC, ETH, ADA...") -> dbc.Col:
        """Layout complet du composant"""
        return dbc.Col([
            dbc.Label(label, className="fw-bold text-light small"),
            self.render_search_input(placeholder),
            self.render_results_container(),
            dcc.Store(id=self.selected_store_id, data=None)
        ], width=4)
    
    def _get_crypto_icon(self, symbol: str) -> str:
        """Retourner icône appropriée selon le symbole"""
        crypto_icons = {
            'BTC': 'fab fa-bitcoin',
            'ETH': 'fab fa-ethereum', 
            'BNB': 'fas fa-coins',
            'ADA': 'fas fa-heart',
            'SOL': 'fas fa-sun',
            'DOT': 'fas fa-circle',
            'LINK': 'fas fa-link',
            'AVAX': 'fas fa-mountain'
        }
        
        base_symbol = symbol.replace('USDT', '').replace('BUSD', '')
        return crypto_icons.get(base_symbol, 'fas fa-coins')


# Instance globale réutilisable
default_symbol_search = SymbolSearchComponent()