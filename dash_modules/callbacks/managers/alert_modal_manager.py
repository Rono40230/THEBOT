"""
Alert Modal Manager - Contrôleur MVC pour le modal d'alertes
Gère les callbacks en utilisant AlertService pour la logique métier
"""

import json
import logging
from typing import Any, Dict, List, Optional

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, callback_context, dcc, html
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate

from ..base.callback_manager import CallbackManager
from ...services import alert_service
from ...core.price_formatter import format_crypto_price_adaptive

logger = logging.getLogger(__name__)


class AlertModalManager(CallbackManager):
    """
    Contrôleur pour le modal d'alertes de prix.
    Gère tous les callbacks liés aux alertes en utilisant AlertService.
    """

    def __init__(self, app):
        super().__init__(app, "AlertModalManager")

    def register_all_callbacks(self) -> None:
        """Enregistre tous les callbacks du modal d'alertes"""
        logger.info("🔄 Enregistrement des callbacks modal alertes...")

        self._register_alerts_modal_callbacks()

        self.log_callback_registration()
        logger.info("✅ Callbacks modal alertes enregistrés")

    def _register_alerts_modal_callbacks(self) -> None:
        """Enregistre les callbacks du modal d'alertes"""

        @self.app.callback(
            [Output("alerts-store", "data"), Output("alerts-count-badge", "children")],
            [Input("price-alerts-modal", "is_open")],
            prevent_initial_call=False,
        )
        def initialize_alerts_on_modal_open(is_open):
            """Charge les alertes depuis AlertService quand le modal s'ouvre"""
            try:
                all_alerts = alert_service.get_all_alerts()
                alert_dicts = [alert.to_dict() for alert in all_alerts]
                return alert_dicts, len(all_alerts)
            except Exception as e:
                logger.error(f"Erreur chargement alertes: {e}")
                return [], 0

        @self.app.callback(
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
            """Crée une nouvelle alerte via AlertService"""
            if not n_clicks or not alert_type or not price:
                raise PreventUpdate

            try:
                # Extraire le symbole du texte affiché
                symbol = symbol_text.split()[0] if symbol_text else "UNKNOWN"

                # Créer l'alerte via le service
                from ..models import AlertType
                alert_type_enum = AlertType(alert_type)
                alert_service.create_alert(
                    symbol=symbol,
                    alert_type=alert_type_enum,
                    price=float(price),
                    message=message or ""
                )

                # Récupérer toutes les alertes mises à jour
                all_alerts = alert_service.get_all_alerts()
                alert_dicts = [alert.to_dict() for alert in all_alerts]

                # Réinitialiser le formulaire et retourner les alertes mises à jour
                return alert_dicts, len(all_alerts), None, None, ""

            except Exception as e:
                logger.error(f"Erreur création alerte: {e}")
                raise PreventUpdate

#         # @self.app.callback(
#             Output("alerts-table-container", "children"),
#             [Input("alerts-store", "data")],
#             prevent_initial_call=False,
#         )
#         def update_alerts_table(alerts_data):
#             """Met à jour l'affichage des alertes"""
#             try:
#                 all_alerts = alert_service.get_all_alerts()
# 
#                 if not all_alerts:
#                     return html.Div(
#                         [
#                             html.P(
#                                 "Aucune alerte configurée", className="text-muted text-center mt-3"
#                             )
#                         ]
#                     )
# 
#                 alert_cards = []
#                 for alert in all_alerts:
#                     # Icône et couleur selon le type
#                     if alert.alert_type.value == "Prix Supérieur à (Above)":
#                         icon = "fas fa-arrow-up text-success"
#                         type_text = "Au-dessus:"
#                     else:
#                         icon = "fas fa-arrow-down text-danger"
#                         type_text = "En-dessous:"
# 
#                     card = html.Div(
#                         [
#                             html.Div(
#                                 [
#                                     html.Strong(f"{alert.symbol} ", className="text-primary"),
#                                     html.Span(
#                                         f"{type_text} ${format_crypto_price_adaptive(alert.price)}"
#                                     ),
#                                     html.Br(),
#                                     (
#                                         html.Small(alert.message, className="text-muted")
#                                         if alert.message
#                                         else ""
#                                     ),
#                                 ],
#                                 className="d-flex justify-content-between align-items-center",
#                             ),
#                             dbc.Button(
#                                 [
#                                     html.I(className="fas fa-trash me-1"),
#                                     "Supprimer",
#                                 ],
#                                 id={"type": "delete-alert-btn", "index": alert.id},
#                                 color="danger",
#                                 size="sm",
#                                 className="mt-2",
#                             ),
#                         ],
#                         className="border rounded p-3 mb-2 bg-white",
#                     )
#                     alert_cards.append(card)
# 
#                 return alert_cards
# 
#             except Exception as e:
#                 logger.error(f"Erreur mise à jour table alertes: {e}")
#                 return html.Div("Erreur chargement alertes")
# 
#         @self.app.callback(
#             [
#                 Output("alerts-store", "data", allow_duplicate=True),
#                 Output("alerts-count-badge", "children", allow_duplicate=True),
#             ],
#             [Input({"type": "delete-alert-btn", "index": ALL}, "n_clicks")],
#             prevent_initial_call=True,
#         )
#         def delete_alert(n_clicks_list):
            """Supprime une alerte via AlertService"""
            if not n_clicks_list or not any(n_clicks_list):
                raise PreventUpdate

            try:
                # Trouver quel bouton a été cliqué
                ctx = callback_context
                if not ctx.triggered:
                    raise PreventUpdate

                # Extraire l'ID de l'alerte depuis l'ID du bouton
                button_id = ctx.triggered[0]["prop_id"].split(".")[0]
                alert_id = json.loads(button_id)["index"]

                # Supprimer via le service
                success = alert_service.delete_alert(alert_id)

                if success:
                    # Récupérer toutes les alertes mises à jour
                    all_alerts = alert_service.get_all_alerts()
                    alert_dicts = [alert.to_dict() for alert in all_alerts]
                    return alert_dicts, len(all_alerts)
                else:
                    logger.warning(f"Échec suppression alerte {alert_id}")
                    raise PreventUpdate

            except Exception as e:
                logger.error(f"Erreur suppression alerte: {e}")
                raise PreventUpdate

        @self.app.callback(
            Output("price-alerts-modal", "is_open"),
            [
                Input("manage-alerts-btn", "n_clicks"),
                Input("alerts-modal-close-btn", "n_clicks"),
            ],
            [State("price-alerts-modal", "is_open")],
        )
        def toggle_alerts_modal(open_clicks, close_clicks, is_open):
            """Ouvre/ferme le modal d'alertes"""
            if open_clicks or close_clicks:
                return not is_open
            return is_open