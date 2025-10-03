"""
Classes de base pour les indicateurs techniques
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from .types import MarketData, IndicatorResult, Signal


class BaseIndicator(ABC):
    """
    Classe de base abstraite pour tous les indicateurs techniques
    """
    
    def __init__(self):
        self._data_points = 0
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nom de l'indicateur"""
        pass
    
    @abstractmethod
    def get_required_periods(self) -> int:
        """Nombre minimum de périodes nécessaires"""
        pass
    
    @property
    @abstractmethod
    def is_ready(self) -> bool:
        """Vérifie si l'indicateur a assez de données"""
        pass
    
    @property
    @abstractmethod
    def current_value(self) -> Any:
        """Valeur actuelle de l'indicateur"""
        pass
    
    @property
    @abstractmethod
    def data_count(self) -> int:
        """Nombre de points de données traités"""
        pass
    
    @abstractmethod
    def add_data(self, market_data: MarketData) -> Optional[IndicatorResult]:
        """
        Ajoute des données et calcule l'indicateur
        
        Args:
            market_data: Nouvelles données de marché
            
        Returns:
            IndicatorResult si l'indicateur peut être calculé, None sinon
        """
        pass
    
    @abstractmethod
    def generate_signal(self, current_result: IndicatorResult) -> Optional[Signal]:
        """
        Génère un signal de trading basé sur le résultat actuel
        
        Args:
            current_result: Résultat actuel de l'indicateur
            
        Returns:
            Signal si générable, None sinon
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Remet à zéro l'état de l'indicateur"""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Métadonnées de l'indicateur (optionnel)"""
        return {
            'name': self.name,
            'data_points': self.data_count,
            'is_ready': self.is_ready,
            'required_periods': self.get_required_periods()
        }