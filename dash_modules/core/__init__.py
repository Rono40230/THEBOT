"""
Core Module - THEBOT Dash
Module central avec configuration et utilitaires de base - Données réelles uniquement
Fichiers restants : uniquement UI (config, callbacks, layout)
"""

# Imports des modules UI restants
from .layout_manager import LayoutManager
from .launcher_callbacks import LauncherCallbacks

__all__ = ["LayoutManager", "LauncherCallbacks"]
