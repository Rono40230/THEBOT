"""
🎯 MODAL INDICATORS - ARCHITECTURE MODULAIRE v2.0
=================================================

Architecture séparée pour éviter le monolithe 4000+ lignes :
- modal_manager.py   : Gestionnaire principal
- config/           : Gestion paramètres JSON
- controls/         : Factory de contrôles (Input/Slider)
- tabs/            : Modules par indicateur (isolation)
- styles/          : Gestion styles trading
"""

from .modal_manager import ModalIndicatorsManager

__all__ = ['ModalIndicatorsManager']