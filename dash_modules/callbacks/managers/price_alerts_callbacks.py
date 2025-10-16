from src.thebot.core.logger import logger
"""
Price Alerts Callbacks Manager - Gestionnaire centralisé des callbacks alertes prix
Regroupe tous les callbacks liés aux alertes de prix et notifications
"""

import json
import logging
from typing import Any, Dict, List, Optional

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, callback_context, dcc, html
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate

from ..base.callback_manager import CallbackManager
from ..base.callback_registry import get_callback_registry
from ...core.alerts_manager import alerts_manager
from ...core.price_formatter import format_crypto_price_adaptive

logger = logging.getLogger(__name__)


class PriceAlertsCallbacks(CallbackManager):
    """
    Gestionnaire centralisé des callbacks pour les alertes de prix.
    Regroupe les callbacks de :
    - price_alerts_modal.py (6 callbacks)
    """

    def __init__(self, app, alerts_manager=None):
        """
        Initialise le gestionnaire de callbacks alertes prix.

        Args:
            app: Instance de l'application Dash
            alerts_manager: Gestionnaire d'alertes
        """
        super().__init__(app, "PriceAlertsCallbacks")
        self.alerts_manager = alerts_manager or alerts_manager
        self.registry = get_callback_registry()

    def register_all_callbacks(self) -> None:
        """Enregistre tous les callbacks alertes prix."""
        logger.info("🔄 Enregistrement des callbacks alertes prix...")

        # Callbacks du modal alertes prix
        self._register_price_alerts_modal_callbacks()

        self.log_callback_registration()
        logger.info("✅ Callbacks alertes prix enregistrés")

    def _register_price_alerts_modal_callbacks(self) -> None:
        """Enregistre les callbacks du modal alertes prix"""
        app = self.app

        # Note: Le callback initialize_alerts_on_modal_open est maintenant géré par AlertModalManager (MVC)
        # pour éviter les conflits de callbacks dupliqués

        # Note: Le callback create_alert est maintenant géré par AlertModalManager (MVC)
        # pour éviter les conflits de callbacks dupliqués
        """
        @callback(
            [
                Output("alerts-store", "data", allow_duplicate=True),
                Output("alerts-count-badge", "children", allow_duplicate=True),
                Output("alert-type-dropdown", "value"),
                Output("alert-price-input", "value"),
                Output("alert-message-input", "value"),
            ],
            [Input("create-alert-btn", "n_clicks")],
            [
                State("crypto-current-symbol", "children"),
                State("alert-type-dropdown", "value"),
                State("alert-price-input", "value"),
                State("alert-message-input", "value"),
            ],
            prevent_initial_call=True,
        )
        def create_alert(n_clicks, symbol_text, alert_type, price, message):
            Créer une nouvelle alerte de prix
            try:
                if not n_clicks or not alert_type or not price:
                    raise PreventUpdate

                # Extraire le symbole du texte affiché
                symbol = symbol_text.split()[0] if symbol_text else "UNKNOWN"

                # Créer la nouvelle alerte via le gestionnaire
                alerts_manager.add_alert(
                    symbol=symbol, alert_type=alert_type, price=float(price), message=message or ""
                )

                # Récupérer toutes les alertes mises à jour
                all_alerts = alerts_manager.get_all_alerts()

                # Réinitialiser le formulaire et retourner les alertes mises à jour
                return all_alerts, len(all_alerts), None, None, ""
            except Exception as e:
                logger.error(f"Erreur création alerte: {e}")
                raise PreventUpdate
        """

        @callback(
            Output("alerts-table-container", "children"),
            [Input("alerts-store", "data")],
            prevent_initial_call=False,
        )
        def update_alerts_table(alerts_data):
            """Mettre à jour l'affichage du tableau d'alertes"""
            try:
                # Charger les alertes depuis le gestionnaire (toujours à jour)
                all_alerts = alerts_manager.get_all_alerts()

                if not all_alerts:
                    return html.Div(
                        [
                            html.P(
                                "Aucune alerte configurée", className="text-muted text-center mt-3"
                            )
                        ]
                    )

                alert_cards = []
                for alert in all_alerts:
                    # Icône et couleur selon le type
                    if alert["type"] == "Prix Supérieur à (Above)":
                        icon = "fas fa-arrow-up text-success"
                        type_text = "Au-dessus:"
                    else:
                        icon = "fas fa-arrow-down text-danger"
                        type_text = "En-dessous:"

                    card = dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Strong(f"{alert['symbol']} - {alert['type']} {alert['price']}"),
                                    html.Br(),
                                    (
                                        html.Small(alert.get("message", ""), className="text-muted")
                                        if alert.get("message")
                                        else None
                                    ),
                                    html.Br(),
                                    html.Small(f"Créé: {alert['created']}", className="text-muted"),
                                ],
                                width=8,  # 8/12 colonnes sur desktop
                                md=8,     # 8/12 sur tablette
                                sm=12,    # pleine largeur sur mobile
                            ),
                            dbc.Col(
                                [
                                    html.Button(
                                        html.I(className="fas fa-trash"),
                                        id={"type": "delete-alert-btn", "index": alert["id"]},
                                        className="btn btn-outline-danger btn-sm ms-1",
                                        title="Supprimer l'alerte",
                                    )
                                ],
                                width=4,  # 4/12 colonnes sur desktop
                                md=4,     # 4/12 sur tablette
                                sm=12,    # pleine largeur sur mobile
                                className="text-end",
                            ),
                        ],
                        className="align-items-center p-3 mb-2 bg-dark text-light rounded",
                    )

                    alert_cards.append(card)

                return html.Div(alert_cards)
            except Exception as e:
                logger.error(f"Erreur mise à jour tableau alertes: {e}")
                return html.Div("Erreur chargement alertes")

        # Note: Le callback delete_alert est maintenant géré par AlertModalManager (MVC)
        # pour éviter les conflits de callbacks dupliqués
        """
        @callback(
            [
                Output("alerts-store", "data", allow_duplicate=True),
                Output("alerts-count-badge", "children", allow_duplicate=True),
            ],
            [Input({"type": "delete-alert-btn", "index": ALL}, "n_clicks")],
            prevent_initial_call=True,
        )
        def delete_alert(n_clicks_list):
            Supprimer une alerte de prix
            try:
                if not any(n_clicks_list or []):
                    raise PreventUpdate

                # Trouver quel bouton a été cliqué
                ctx = callback_context
                if not ctx.triggered:
                    raise PreventUpdate

                button_id = ctx.triggered[0]["prop_id"].split(".")[0]
                alert_id = json.loads(button_id)["index"]

                # Supprimer l'alerte via le gestionnaire
                success = alerts_manager.delete_alert(alert_id)

                if success:
                    # Récupérer toutes les alertes mises à jour
                    all_alerts = alerts_manager.get_all_alerts()
                    return all_alerts, len(all_alerts)
                else:
                    raise PreventUpdate
            except Exception as e:
                logger.error(f"Erreur suppression alerte: {e}")
                raise PreventUpdate
#         """
# 
#         @callback(
#             Output("price-alerts-modal", "is_open"),
#             [
#                 Input("manage-alerts-btn", "n_clicks"),
#                 Input("alerts-modal-close-btn", "n_clicks"),
#             ],
#             [State("price-alerts-modal", "is_open")],
#         )
#         def toggle_alerts_modal(open_clicks, close_clicks, is_open):
#             """Ouvrir/fermer le modal d'alertes"""
#             try:
#                 if open_clicks or close_clicks:
#                     return not is_open
#                 return is_open
#             except Exception as e:
#                 logger.error(f"Erreur toggle modal alertes: {e}")
#                 return False