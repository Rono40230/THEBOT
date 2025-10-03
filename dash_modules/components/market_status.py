"""
Module de gestion du statut des marchés globaux
Affiche les heures d'ouverture/fermeture des principales places boursières
"""

import dash_bootstrap_components as dbc
from dash import html
from datetime import datetime
import pytz
from typing import List, Dict, Tuple


class MarketStatusManager:
    """Gestionnaire du statut des marchés globaux"""
    
    def __init__(self):
        """Initialise le gestionnaire avec les fuseaux horaires des marchés"""
        self.markets = {
            'NY': {
                'name': 'New York',
                'timezone': 'America/New_York',
                'open_time': (9, 30),  # 9h30 EST
                'close_time': (16, 0),  # 16h00 EST
                'days': [0, 1, 2, 3, 4]  # Lundi à Vendredi
            },
            'London': {
                'name': 'London',
                'timezone': 'Europe/London',
                'open_time': (8, 0),   # 8h00 GMT
                'close_time': (16, 30), # 16h30 GMT
                'days': [0, 1, 2, 3, 4]
            },
            'Paris': {
                'name': 'Paris',
                'timezone': 'Europe/Paris',
                'open_time': (9, 0),   # 9h00 CET
                'close_time': (17, 30), # 17h30 CET
                'days': [0, 1, 2, 3, 4]
            },
            'Tokyo': {
                'name': 'Tokyo',
                'timezone': 'Asia/Tokyo',
                'open_time': (9, 0),   # 9h00 JST
                'close_time': (15, 0), # 15h00 JST
                'days': [0, 1, 2, 3, 4]
            },
            'HK': {
                'name': 'Hong Kong',
                'timezone': 'Asia/Hong_Kong',
                'open_time': (9, 30),  # 9h30 HKT
                'close_time': (16, 0), # 16h00 HKT
                'days': [0, 1, 2, 3, 4]
            },
            'Sydney': {
                'name': 'Sydney',
                'timezone': 'Australia/Sydney',
                'open_time': (10, 0),  # 10h00 AEST
                'close_time': (16, 0), # 16h00 AEST
                'days': [0, 1, 2, 3, 4]
            }
        }
    
    def is_market_open(self, market_code: str) -> bool:
        """Vérifie si un marché est actuellement ouvert"""
        if market_code not in self.markets:
            return False
        
        market = self.markets[market_code]
        
        try:
            # Obtenir l'heure actuelle dans le fuseau du marché
            tz = pytz.timezone(market['timezone'])
            now = datetime.now(tz)
            
            # Vérifier si c'est un jour ouvrable
            if now.weekday() not in market['days']:
                return False
            
            # Vérifier si c'est dans les heures d'ouverture
            open_hour, open_minute = market['open_time']
            close_hour, close_minute = market['close_time']
            
            current_time = now.time()
            open_time = now.replace(hour=open_hour, minute=open_minute, second=0, microsecond=0).time()
            close_time = now.replace(hour=close_hour, minute=close_minute, second=0, microsecond=0).time()
            
            return open_time <= current_time <= close_time
            
        except Exception:
            # En cas d'erreur, retourner False
            return False
    
    def get_market_status_badge(self, market_code: str) -> dbc.Badge:
        """Crée un badge de statut pour un marché donné"""
        is_open = self.is_market_open(market_code)
        
        status_text = "Open" if is_open else "Closed"
        color = "success" if is_open else "secondary"
        
        return dbc.Badge(
            f"{market_code}: {status_text}",
            color=color,
            className="me-2"
        )
    
    def get_all_market_badges(self) -> List[dbc.Badge]:
        """Retourne la liste de tous les badges de statut des marchés"""
        badges = []
        for market_code in self.markets.keys():
            badges.append(self.get_market_status_badge(market_code))
        return badges
    
    def get_market_status_component(self) -> html.Div:
        """Composant complet avec tous les indicateurs de marchés"""
        return html.Div([
            html.Div(
                self.get_all_market_badges(),
                id="market-status-badges",
                className="d-inline-flex"
            )
        ])
    
    def get_market_status_with_refresh(self, component_id: str = "market-status-container") -> html.Div:
        """Composant avec mise à jour automatique (nécessite un callback)"""
        return html.Div([
            self.get_market_status_component()
        ], id=component_id)


# Instance globale pour l'application
market_status_manager = MarketStatusManager()


def get_market_status_badges() -> List[dbc.Badge]:
    """Fonction helper pour obtenir rapidement les badges"""
    return market_status_manager.get_all_market_badges()


def get_market_status_component() -> html.Div:
    """Fonction helper pour obtenir le composant complet"""
    return market_status_manager.get_market_status_component()