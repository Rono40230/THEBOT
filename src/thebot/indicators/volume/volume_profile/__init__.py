"""
Volume Profile + POC Module
Analyse de la distribution du volume par prix avec Point of Control
"""

from .config import VolumeProfileConfig, VolumeProfileType, ValueAreaMethod
from .calculator import (
    VolumeProfileCalculator, 
    VolumeNode, 
    ValueArea, 
    VolumeProfileResult
)

__all__ = [
    'VolumeProfileConfig',
    'VolumeProfileType', 
    'ValueAreaMethod',
    'VolumeProfileCalculator',
    'VolumeNode',
    'ValueArea', 
    'VolumeProfileResult',
    'create_volume_profile_analyzer',
    'get_volume_profile_signals',
    'get_poc_and_value_area'
]

def create_volume_profile_analyzer(trading_style: str = "day_trading", **kwargs) -> VolumeProfileCalculator:
    """
    Créer un analyseur Volume Profile optimisé pour un style de trading
    
    Args:
        trading_style: Style de trading ('scalping', 'day_trading', 'swing_trading', 'position_trading')
        **kwargs: Paramètres additionnels pour surcharger la configuration
        
    Returns:
        VolumeProfileCalculator configuré
    """
    # Configuration de base
    config = VolumeProfileConfig()
    
    # Optimisation selon le style
    style_params = config.get_trading_style_config(trading_style)
    
    # Application des paramètres du style
    for key, value in style_params.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    # Application des surcharges utilisateur
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return VolumeProfileCalculator(config)

def get_volume_profile_signals(data, trading_style: str = "day_trading") -> dict:
    """
    Analyse rapide Volume Profile pour signaux de trading
    
    Args:
        data: DataFrame avec colonnes OHLCV
        trading_style: Style de trading
        
    Returns:
        Dict avec signaux et niveaux clés
    """
    analyzer = create_volume_profile_analyzer(trading_style)
    return analyzer.get_trading_signals(data)

def get_poc_and_value_area(data, trading_style: str = "day_trading") -> dict:
    """
    Extraction POC et Value Area
    
    Args:
        data: DataFrame avec colonnes OHLCV
        trading_style: Style de trading
        
    Returns:
        Dict avec POC, Value Area High/Low, et forces
    """
    analyzer = create_volume_profile_analyzer(trading_style)
    result = analyzer.calculate(data)
    profile = result.get("volume_profile")
    
    if not profile:
        return {
            "poc": 0,
            "value_area_high": 0,
            "value_area_low": 0,
            "total_volume": 0,
            "high_volume_nodes": []
        }
    
    return {
        "poc": profile.poc.price_level,
        "poc_volume_percent": profile.poc.volume_percent,
        "value_area_high": profile.value_area.high,
        "value_area_low": profile.value_area.low,
        "value_area_percent": profile.value_area.volume_percent,
        "total_volume": profile.total_volume,
        "high_volume_nodes": [
            {
                "price": hvn.price_level,
                "volume_percent": hvn.volume_percent,
                "strength": hvn.support_strength
            }
            for hvn in profile.high_volume_nodes
        ]
    }