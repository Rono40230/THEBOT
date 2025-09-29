"""
Core Module - THEBOT Dash
Module central avec configuration et utilitaires de base - Données réelles uniquement
"""

from .config import dash_config
from .calculators import calculator

__all__ = ['dash_config', 'calculator']