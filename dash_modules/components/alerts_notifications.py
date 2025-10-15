"""
Composant de Notifications d'Alertes pour Dash
Affichage des notifications d'alertes en temps réel
"""

import time

import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, clientside_callback, dcc, html

from dash_modules.core.alerts_monitor import alerts_monitor, notification_manager


class AlertsNotificationComponent:
    """Composant de notifications d'alertes pour Dash"""

    def __init__(self):
        self.component_id = "alerts-notifications"

    def create_notification_container(self):
        """Créer le conteneur de notifications"""
        return html.Div(
            [
                # Store pour les notifications
                dcc.Store(id="notifications-store", data=[]),
                # Conteneur des notifications (position fixe)
                html.Div(
                    id="notifications-container",
                    className="alerts-notifications-container",
                    children=[],
                    style={
                        "position": "fixed",
                        "top": "20px",
                        "right": "20px",
                        "zIndex": "9999",
                        "maxWidth": "400px",
                    },
                ),
                # Intervalle pour vérifier les nouvelles notifications
                dcc.Interval(
                    id="notifications-interval",
                    interval=2000,  # Vérifier toutes les 2 secondes
                    n_intervals=0,
                ),
            ]
        )

    def get_custom_css(self):
        """CSS pour les notifications"""
        return """
        /* Notifications d'alertes */
        .alerts-notifications-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            pointer-events: none;
        }
        
        .alert-notification {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 10px;
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
            border-left: 5px solid #fff;
            animation: slideInRight 0.5s ease-out;
            pointer-events: auto;
            position: relative;
            overflow: hidden;
        }
        
        .alert-notification::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #fff, rgba(255,255,255,0.5));
            animation: progressBar 10s linear;
        }
        
        .alert-notification-header {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            font-weight: bold;
            font-size: 16px;
        }
        
        .alert-notification-body {
            font-size: 14px;
            line-height: 1.4;
            margin-bottom: 8px;
        }
        
        .alert-notification-time {
            font-size: 12px;
            opacity: 0.8;
            text-align: right;
        }
        
        .alert-notification-close {
            position: absolute;
            top: 8px;
            right: 12px;
            background: none;
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            opacity: 0.7;
            transition: opacity 0.2s;
        }
        
        .alert-notification-close:hover {
            opacity: 1;
        }
        
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        @keyframes progressBar {
            from {
                width: 100%;
            }
            to {
                width: 0%;
            }
        }
        
        .alert-notification.closing {
            animation: slideOutRight 0.3s ease-in forwards;
        }
        
        /* Statut de surveillance */
        .monitoring-status {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(40, 167, 69, 0.9);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            z-index: 1000;
            backdrop-filter: blur(10px);
        }
        
        .monitoring-status.inactive {
            background: rgba(220, 53, 69, 0.9);
        }
        """


# Instance globale
alerts_notification_component = AlertsNotificationComponent()

# Callbacks pour les notifications - MIGRÉS vers AlertsCallbacks manager
# Les callbacks suivants ont été déplacés dans dash_modules/callbacks/managers/alerts_callbacks.py

# Callback update_notifications_store MIGRÉ vers AlertsCallbacks


# Callback update_notifications_display MIGRÉ vers AlertsCallbacks


# Callback côté client pour auto-fermer les notifications
clientside_callback(
    """
    function(n_intervals) {
        // Auto-fermer les notifications après 10 secondes
        const notifications = document.querySelectorAll('.alert-notification');
        notifications.forEach(function(notif, index) {
            if (!notif.dataset.timer) {
                notif.dataset.timer = Date.now();
            }
            
            const elapsed = Date.now() - parseInt(notif.dataset.timer);
            if (elapsed > 10000) { // 10 secondes
                notif.classList.add('closing');
                setTimeout(function() {
                    if (notif.parentNode) {
                        notif.parentNode.removeChild(notif);
                    }
                }, 300);
            }
        });
        
        return window.dash_clientside.no_update;
    }
    """,
    Output("notifications-container", "id"),
    Input("notifications-interval", "n_intervals"),
    prevent_initial_call=True,
)


# Composant de statut de surveillance
def create_monitoring_status_component():
    """Créer le composant de statut de surveillance"""
    return html.Div(
        [
            html.Div(
                id="monitoring-status-display",
                className="monitoring-status",
                children="🔔 Surveillance inactive",
            ),
            dcc.Interval(
                id="monitoring-status-interval",
                interval=5000,  # Vérifier toutes les 5 secondes
                n_intervals=0,
            ),
        ]
    )


# Callback update_monitoring_status MIGRÉ vers AlertsCallbacks
