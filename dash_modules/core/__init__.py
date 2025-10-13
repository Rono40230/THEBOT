"""
Core Module - THEBOT Dash
Module central avec configuration et utilitaires de base - Données réelles uniquement
"""

from .calculators import calculator
from .config import dash_config

__all__ = ["dash_config", "calculator"]
