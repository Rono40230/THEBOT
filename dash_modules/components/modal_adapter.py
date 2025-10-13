"""
🔄 MODAL ADAPTER - Intégration Progressive Nouveau/Ancien
========================================================

Adaptateur pour migration progressive de l'ancienne modal vers la nouvelle
architecture modulaire. Permet de tester le nouveau système sans casser l'ancien.
"""

from typing import Any, Dict, Optional

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, ctx, html

# Import du nouveau système modulaire
from .modals.modal_manager import MODAL_CSS, modal_manager

# Ancien système désactivé - on utilise seulement le nouveau
# from .indicators_modal_BACKUP import IndicatorsModal as OldIndicatorsModal


class ModalAdapter:
    """Adaptateur pour migration progressive entre ancien et nouveau système"""

    def __init__(self):
        # Nouveau système modulaire
        self.new_modal = modal_manager

        # Ancien système désactivé
        # self.old_modal = OldIndicatorsModal()
        self.old_modal = None

        # Flag de mode (True = nouveau, False = ancien)
        self.use_new_system = True  # Par défaut utiliser le nouveau

    def create_modal(self) -> html.Div:
        """Créer la modal avec sélecteur de système"""

        # Modal principale (nouveau système)
        new_modal_content = self.new_modal.create_modal()

        # Wrapper simplifié
        return html.Div(
            [
                # Modal principale uniquement
                new_modal_content,
            ]
        )

    def get_current_config(self) -> Dict[str, Any]:
        """Récupérer la configuration actuelle du nouveau système"""
        # Nouveau système uniquement : utiliser parameters_manager
        basic_config = self.new_modal.parameters.get_all_basic_indicators()
        advanced_config = self.new_modal.parameters.get_all_advanced_indicators()

        # Convertir au format attendu
        return self._convert_new_to_old_format(basic_config, advanced_config)

    def _convert_new_to_old_format(
        self, basic_config: Dict, advanced_config: Dict
    ) -> Dict[str, Any]:
        """Convertir le format nouveau vers ancien pour compatibilité"""
        converted = {}

        # Indicateurs de base
        for indicator, config in basic_config.items():
            converted[indicator] = {
                "enabled": config.get("enabled", True),
                "period": config.get("period", 14),
                "color": config.get("color", "#2196F3"),
            }

            # Paramètres spéciaux selon l'indicateur
            if indicator == "rsi":
                converted[indicator].update(
                    {
                        "overbought": config.get("overbought", 70),
                        "oversold": config.get("oversold", 30),
                    }
                )
            elif indicator == "atr":
                converted[indicator].update(
                    {"multiplier": config.get("multiplier", 2.0)}
                )
            elif indicator == "macd":
                converted[indicator].update(
                    {
                        "fast_period": config.get("fast_period", 12),
                        "slow_period": config.get("slow_period", 26),
                        "signal_period": config.get("signal_period", 9),
                    }
                )

        # Indicateurs avancés
        for indicator, config in advanced_config.items():
            converted[indicator] = config.copy()

        return converted

    def update_config(self, config: Dict[str, Any]):
        """Mettre à jour la configuration (compatible ancien/nouveau)"""
        if self.use_new_system:
            # Nouveau système : distribuer dans parameters_manager
            self._update_new_system_config(config)
        else:
            # Ancien système
            self.old_modal.indicators_config.update(config)

    def _update_new_system_config(self, config: Dict[str, Any]):
        """Mettre à jour la configuration du nouveau système"""
        basic_indicators = ["sma", "ema", "rsi", "atr", "macd"]
        advanced_indicators = ["support_resistance", "fibonacci", "pivot_points"]

        for indicator, values in config.items():
            if indicator in basic_indicators:
                for key, value in values.items():
                    self.new_modal.parameters.update_indicator_config(
                        "basic_indicators", indicator, key, value
                    )
            elif indicator in advanced_indicators:
                for key, value in values.items():
                    self.new_modal.parameters.update_indicator_config(
                        "advanced_indicators", indicator, key, value
                    )

    def export_debug_info(self) -> Dict[str, Any]:
        """Exporter les informations de debug"""
        return {
            "system_mode": "new_modular" if self.use_new_system else "old_legacy",
            "new_system_config": (
                self.new_modal.parameters.config if self.use_new_system else None
            ),
            "old_system_config": (
                self.old_modal.indicators_config if not self.use_new_system else None
            ),
            "adapter_version": "1.0.0",
            "migration_status": "progressive_testing",
        }


# Instance globale de l'adaptateur
modal_adapter = ModalAdapter()


def create_indicators_modal() -> html.Div:
    """
    Fonction principale pour créer la modal des indicateurs
    Point d'entrée unique pour le système
    """
    return modal_adapter.create_modal()


def get_indicators_config() -> Dict[str, Any]:
    """Récupérer la configuration actuelle des indicateurs"""
    return modal_adapter.get_current_config()


def update_indicators_config(config: Dict[str, Any]):
    """Mettre à jour la configuration des indicateurs"""
    modal_adapter.update_config(config)
