from src.thebot.core.logger import logger
"""
Phase 4 Extensions for Crypto News Module
Widgets compacts modulaires pour intégration dans crypto_news_module
Approche sûre et non-invasive
"""

from typing import Dict, List, Optional

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

# Imports conditionnels Phase 4 (modulaire)
try:
    from ..components.crypto_trends import crypto_trends
    from ..components.fear_greed_gauge import fear_greed_gauge
    from ..components.top_performers import top_performers

    PHASE4_AVAILABLE = True
    logger.info("✅ Phase 4 crypto widgets disponibles")
except ImportError:
    PHASE4_AVAILABLE = False
    logger.info("⚠️ Phase 4 crypto widgets non disponibles")


class CryptoNewsPhase4Extensions:
    """Extensions Phase 4 pour le module crypto news"""

    def __init__(self):
        self.widget_prefix = "crypto-news-p4"

    def get_compact_widgets_layout(self) -> html.Div:
        """Retourne le layout des widgets compacts Phase 4"""
        if not PHASE4_AVAILABLE:
            return html.Div(
                [
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H6("📊 Advanced Analysis", className="mb-2"),
                                    html.P(
                                        "Widgets Phase 4 non disponibles",
                                        className="text-muted small mb-0",
                                    ),
                                ]
                            )
                        ],
                        className="mb-3",
                    )
                ]
            )

        return html.Div(
            [
                # Fear & Greed Index Compact
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [html.H6("😨 Fear & Greed", className="mb-0 small")]
                        ),
                        dbc.CardBody(
                            [
                                html.Div(
                                    id=f"{self.widget_prefix}-fear-greed",
                                    className="text-center",
                                )
                            ],
                            className="py-2",
                        ),
                    ],
                    className="mb-2",
                ),
                # Top Performers Compact
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [html.H6("🏆 Top Gainers", className="mb-0 small")]
                        ),
                        dbc.CardBody(
                            [html.Div(id=f"{self.widget_prefix}-gainers")],
                            className="py-2",
                        ),
                    ],
                    className="mb-2",
                ),
                # Market Trends Compact
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [html.H6("📈 Market Pulse", className="mb-0 small")]
                        ),
                        dbc.CardBody(
                            [html.Div(id=f"{self.widget_prefix}-trends")],
                            className="py-2",
                        ),
                    ],
                    className="mb-2",
                ),
                # Auto-refresh interval
                dcc.Interval(
                    id=f"{self.widget_prefix}-interval",
                    interval=60 * 1000,  # 1 minute
                    n_intervals=0,
                ),
            ]
        )

    def register_callbacks(self):
        """CALLBACKS MIGRÉS vers NewsCallbacks manager"""
        # Les callbacks suivants ont été déplacés dans dash_modules/callbacks/managers/news_callbacks.py
        # - update_fear_greed_compact
        # - update_gainers_compact
        # - update_trends_compact
        pass


# Instance globale pour utilisation modulaire
crypto_news_phase4_extensions = CryptoNewsPhase4Extensions()


def get_phase4_sidebar_widgets() -> html.Div:
    """Fonction utilitaire pour obtenir les widgets Phase 4"""
    return crypto_news_phase4_extensions.get_compact_widgets_layout()


def register_phase4_callbacks():
    """CALLBACKS MIGRÉS vers NewsCallbacks manager"""
    # Les callbacks ont été déplacés dans dash_modules/callbacks/managers/news_callbacks.py
    pass


# Auto-registration des callbacks si importé
if PHASE4_AVAILABLE:
    register_phase4_callbacks()
