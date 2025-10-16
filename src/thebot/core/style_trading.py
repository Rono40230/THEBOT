"""
Module de gestion des styles de trading avec paramètres pré-configurés.
Fournit des configurations optimales pour différents styles de trading.
Version temporaire pour migration Phase 2
"""

from dataclasses import dataclass
from typing import Any, Dict

from src.thebot.core.logger import logger


@dataclass
class IndicatorConfig:
    """Configuration d'un indicateur spécifique"""
    enabled: bool
    parameters: Dict[str, Any]
    visual: Dict[str, Any]


class TradingStyleManager:
    """Gestionnaire des styles de trading avec paramètres optimisés"""

    TRADING_STYLES = {
        "scalping": {
            "name": "⚡ Scalping (1-5min)",
            "description": "Trading ultra-rapide avec nombreux signaux",
            "timeframes": ["1m", "5m"],
            "characteristics": "Signaux fréquents, faible risque par trade",
        },
        "day_trading": {
            "name": "🌅 Day Trading (15min-4h)",
            "description": "Trading journalier avec analyse technique",
            "timeframes": ["15m", "1h", "4h"],
            "characteristics": "Analyse complète, risque modéré",
        },
        "swing": {
            "name": "🎯 Swing Trading (4h-1D)",
            "description": "Trading positionnel sur plusieurs jours",
            "timeframes": ["4h", "1D"],
            "characteristics": "Patience requise, fort potentiel",
        },
    }

    def __init__(self):
        self.current_style = "day_trading"
        logger.info("🎨 TradingStyleManager initialisé (Phase 2)")

    def get_style_config(self, style_name: str) -> Dict[str, Any]:
        """Récupérer la configuration d'un style de trading"""
        return self.TRADING_STYLES.get(style_name, self.TRADING_STYLES["day_trading"])

    def set_current_style(self, style_name: str):
        """Définir le style de trading actuel"""
        if style_name in self.TRADING_STYLES:
            self.current_style = style_name
            logger.info(f"🎯 Style de trading changé: {style_name}")
        else:
            logger.warning(f"Style inconnu: {style_name}")

    def get_current_style(self) -> Dict[str, Any]:
        """Récupérer le style actuel"""
        return self.get_style_config(self.current_style)


# Instance globale
trading_style_manager = TradingStyleManager()