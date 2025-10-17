"""
Launcher Callbacks - Gestion Centralisée des Callbacks du Launcher
Architecture MVC - Couche CONTROLLER conforme .clinerules
"""

import logging
from typing import Any, Dict, List, Optional

from dash import Input, Output, html
from src.thebot.core.logger import logger

# Stub temporaire pour la migration - sera complété dans Phase 2
class LauncherCallbacks:
    """
    Gestionnaire centralisé des callbacks du launcher
    Version temporaire pour migration Phase 2
    """

    def __init__(self, app=None, modules=None):
        self.app = app
        self.modules = modules or {}
        logger.info("🔧 LauncherCallbacks initialisé (stub Phase 2)")

    def register_callbacks(self):
        """Enregistrer tous les callbacks - stub temporaire"""
        if self.app and self.modules:
            self._register_tab_callbacks()
        logger.info("📝 Callbacks enregistrés (stub Phase 2)")

    def _register_tab_callbacks(self):
        """Callback pour gérer l'affichage des onglets"""
        @self.app.callback(
            Output("tab-content", "children"),
            Input("main-tabs", "value")
        )
        def update_tab_content(selected_tab):
            """Met à jour le contenu de l'onglet sélectionné"""
            try:
                if selected_tab in self.modules:
                    module = self.modules[selected_tab]
                    if hasattr(module, 'get_layout'):
                        return module.get_layout()

                # Contenu par défaut si onglet non trouvé
                return html.Div([
                    html.H3("❌ Onglet non trouvé", style={"color": "#ff6b35"}),
                    html.P(f"Onglet sélectionné: {selected_tab}", style={"color": "#cccccc"})
                ], style={"padding": "20px", "backgroundColor": "#1a1a1a"})

            except Exception as e:
                logger.error(f"Erreur callback onglet {selected_tab}: {e}")
                return html.Div([
                    html.H3("❌ Erreur", style={"color": "#ff0000"}),
                    html.P(f"Erreur: {str(e)}", style={"color": "#cccccc"})
                ], style={"padding": "20px", "backgroundColor": "#1a1a1a"})

    def get_status(self) -> Dict[str, Any]:
        """Statut du launcher"""
        return {
            "status": "initializing",
            "callbacks_registered": bool(self.app),
            "modules_count": len(self.modules),
            "phase": "2_migration"
        }


# Instance globale temporaire
launcher_callbacks = LauncherCallbacks()