"""
Base Module Abstrait - Architecture MVC THEBOT
Classe abstraite pour standardiser tous les modules selon .clinerules
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
import logging
from dash import html, dcc

# Configuration du logging conforme .clinerules
logger = logging.getLogger(__name__)

class BaseModule(ABC):
    """
    Classe abstraite pour tous les modules THEBOT
    
    Responsabilités selon .clinerules :
    - Single Responsibility : Un module = une fonctionnalité
    - Type hints obligatoires
    - Logging structuré
    - Interface standardisée
    """
    
    def __init__(self, module_name: str) -> None:
        """
        Initialise le module de base
        
        Args:
            module_name: Nom du module (crypto, forex, stocks, etc.)
        
        Raises:
            ValueError: Si module_name est vide
        """
        if not module_name:
            raise ValueError("module_name ne peut pas être vide")
            
        self.module_name: str = module_name
        self.is_initialized: bool = False
        self.logger: logging.Logger = logging.getLogger(f"thebot.modules.{module_name}")
        
        self.logger.info(f"🏗️ Initialisation du module {module_name}")
    
    @abstractmethod
    def get_layout(self) -> html.Div:
        """
        Retourne le layout principal du module
        
        Returns:
            html.Div: Layout Dash complet du module
            
        Note:
            Méthode abstraite - DOIT être implémentée par chaque module
        """
        pass
    
    @abstractmethod
    def setup_callbacks(self, app) -> None:
        """
        Configure les callbacks Dash du module
        
        Args:
            app: Instance de l'application Dash
            
        Note:
            Méthode abstraite - DOIT être implémentée par chaque module
        """
        pass
    
    def get_sidebar(self) -> html.Div:
        """
        Retourne la sidebar du module (optionnelle)
        
        Returns:
            html.Div: Sidebar ou div vide si pas de sidebar
            
        Note:
            Méthode par défaut - peut être surchargée
        """
        return html.Div()  # Pas de sidebar par défaut
    
    def get_content(self) -> html.Div:
        """
        Retourne le contenu principal (alias de get_layout)
        
        Returns:
            html.Div: Contenu principal du module
        """
        return self.get_layout()
    
    def get_supported_timeframes(self) -> List[Dict[str, str]]:
        """
        Retourne les timeframes supportés par le module
        
        Returns:
            List[Dict]: Liste des timeframes au format [{'label': '1h', 'value': '1h'}]
            
        Note:
            Méthode par défaut - peut être surchargée
        """
        return [
            {'label': '1mn', 'value': '1m'},
            {'label': '15mn', 'value': '15m'},
            {'label': '30mn', 'value': '30m'},
            {'label': '1h', 'value': '1h'},
            {'label': '4h', 'value': '4h'},
            {'label': '1d', 'value': '1d'},
            {'label': '1M', 'value': '1M'}
        ]
    
    def get_module_info(self) -> Dict[str, Any]:
        """
        Retourne les informations du module
        
        Returns:
            Dict: Informations détaillées du module
        """
        return {
            'name': self.module_name,
            'initialized': self.is_initialized,
            'has_sidebar': bool(self.get_sidebar().children),
            'supported_timeframes': len(self.get_supported_timeframes()),
            'class_name': self.__class__.__name__
        }
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Valide un symbole financier
        
        Args:
            symbol: Symbole à valider (ex: 'BTCUSDT')
            
        Returns:
            bool: True si valide, False sinon
        """
        if not symbol or not isinstance(symbol, str):
            return False
        
        # Validation basique : au moins 3 caractères, alphanumériques
        return len(symbol) >= 3 and symbol.isalnum()
    
    def validate_timeframe(self, timeframe: str) -> bool:
        """
        Valide un timeframe
        
        Args:
            timeframe: Timeframe à valider (ex: '1h')
            
        Returns:
            bool: True si supporté, False sinon
        """
        supported = [tf['value'] for tf in self.get_supported_timeframes()]
        return timeframe in supported
    
    def log_info(self, message: str) -> None:
        """
        Log une information du module
        
        Args:
            message: Message à logger
        """
        self.logger.info(f"[{self.module_name}] {message}")
    
    def log_error(self, message: str, exception: Optional[Exception] = None) -> None:
        """
        Log une erreur du module
        
        Args:
            message: Message d'erreur
            exception: Exception optionnelle
        """
        if exception:
            self.logger.error(f"[{self.module_name}] {message}: {exception}")
        else:
            self.logger.error(f"[{self.module_name}] {message}")
    
    def log_warning(self, message: str) -> None:
        """
        Log un avertissement du module
        
        Args:
            message: Message d'avertissement
        """
        self.logger.warning(f"[{self.module_name}] {message}")
    
    def __str__(self) -> str:
        """Représentation string du module"""
        return f"BaseModule({self.module_name})"
    
    def __repr__(self) -> str:
        """Représentation détaillée du module"""
        return f"BaseModule(name='{self.module_name}', initialized={self.is_initialized})"

# Export conforme .clinerules
__all__ = ['BaseModule']