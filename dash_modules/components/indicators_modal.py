"""
🔄 MODAL INDICATORS - Point d'entrée Migration Progressive
=========================================================

Point d'entrée compatible pour migration progressive vers le nouveau système modulaire.
Remplace progressivement l'ancien monolithe par l'architecture modulaire v2.0.
"""

from typing import Any, Dict, Optional

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback_context, dcc, html

from dash_modules.core.style_trading import trading_style_manager

# Import du nouveau système modulaire
from .modal_adapter import MODAL_CSS, modal_adapter


class IndicatorsModal:
    """Modal pour configurer tous les indicateurs techniques - Version Modulaire v2.0"""

    def __init__(self):
        self.modal_id = "indicators-modal"
        # Utiliser le nouveau système modulaire via l'adaptateur
        self.adapter = modal_adapter
        self.indicators_config = self.adapter.get_current_config()

    def create_modal(self) -> html.Div:
        """Créer la modal avec le nouveau système modulaire"""
        return self.adapter.create_modal()

    def get_custom_css(self) -> str:
        """Retourner le CSS personnalisé pour la modal"""
        return MODAL_CSS


def register_indicators_modal_callbacks(app):
    """
    🔄 CALLBACKS MODAL INDICATEURS - Migration vers le Nouveau Système
    ================================================================

    Cette fonction utilise maintenant le nouveau système modulaire v2.0
    au lieu de l'ancien système monolithique.

    Les callbacks sont maintenant gérés par:
    - modal_manager.py (gestionnaire principal)
    - modal_adapter.py (interface d'adaptation)
    - basic_indicators.py et advanced_indicators.py (modules spécialisés)
    """
    print("✅ Callbacks Modal Indicateurs enregistrés (nouveau système)")

    # Import et activation du nouveau système modulaire
    try:
        from .modal_adapter import modal_adapter

        # Enregistrer les callbacks du nouveau système modulaire
        modal_adapter.register_callbacks(app)
        print("🔄 Nouveau système modulaire activé avec callbacks")

    except ImportError as e:
        print(f"⚠️ Erreur import nouveau système: {e}")


# Instance globale de la modal
indicators_modal = IndicatorsModal()

# Store pour sauvegarder la configuration des indicateurs
indicators_store = dcc.Store(
    id="indicators-config-store", data=indicators_modal.indicators_config
)
