"""
Announcements Calendar Module - Migration Phase 2
Stub temporaire pour compatibilité
"""

import logging
from typing import Any, Dict, Optional

from dash import html
from src.thebot.core.base_module import BaseModule
from src.thebot.core.logger import logger


class AnnouncementsCalendarModule(BaseModule):
    """Module calendrier des annonces économiques - Stub Phase 2"""

    def __init__(self):
        super().__init__("announcements_calendar")
        logger.info("📅 AnnouncementsCalendarModule initialisé (stub Phase 2)")

    def get_layout(self) -> html.Div:
        """Layout temporaire en cours de migration"""
        return html.Div([
            html.H3("📅 Calendrier des Annonces Économiques", style={"color": "white"}),
            html.P("Module en cours de migration vers architecture unifiée...",
                  style={"color": "gray"}),
            html.P("🔄 Phase 2 - Migration UI", style={"color": "orange"})
        ], style={"padding": "20px"})

    def setup_callbacks(self, app) -> None:
        """Configuration des callbacks - stub temporaire"""
        logger.info("🔧 Callbacks AnnouncementsCalendar configurés (stub Phase 2)")
        pass


# Instance globale temporaire
announcements_calendar_module = AnnouncementsCalendarModule()