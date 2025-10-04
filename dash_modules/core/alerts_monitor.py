"""
Module de Surveillance des Alertes - THEBOT
Surveillance en temps réel des prix et déclenchement des alertes
"""

import asyncio
import threading
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json
from dash_modules.core.alerts_manager import alerts_manager
from dash_modules.data_providers.binance_api import BinanceProvider

logger = logging.getLogger(__name__)

class AlertsMonitor:
    """Surveillant des alertes en temps réel"""
    
    def __init__(self, check_interval: int = 10):
        """
        Initialiser le surveillant d'alertes
        
        Args:
            check_interval: Intervalle de vérification en secondes (par défaut 10s)
        """
        self.check_interval = check_interval
        self.binance_api = BinanceProvider()
        self.is_running = False
        self.monitor_thread = None
        self.current_prices = {}
        self.triggered_alerts = set()  # Pour éviter les notifications multiples
        
        # Callbacks pour les notifications
        self.notification_callbacks = []
        
        logger.info("🔔 AlertsMonitor initialisé")
    
    def add_notification_callback(self, callback):
        """Ajouter un callback pour les notifications d'alertes"""
        self.notification_callbacks.append(callback)
    
    def start_monitoring(self):
        """Démarrer la surveillance des alertes"""
        if self.is_running:
            logger.warning("⚠️ La surveillance est déjà en cours")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("🚀 Surveillance des alertes démarrée")
    
    def stop_monitoring(self):
        """Arrêter la surveillance des alertes"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("🛑 Surveillance des alertes arrêtée")
    
    def _monitor_loop(self):
        """Boucle principale de surveillance"""
        logger.info(f"🔄 Boucle de surveillance démarrée (intervalle: {self.check_interval}s)")
        
        while self.is_running:
            try:
                # Récupérer les alertes actives
                active_alerts = alerts_manager.get_active_alerts()
                
                if not active_alerts:
                    time.sleep(self.check_interval)
                    continue
                
                # Extraire les symboles uniques à surveiller
                symbols_to_monitor = list(set(alert['symbol'] for alert in active_alerts))
                
                # Récupérer les prix actuels
                self._fetch_current_prices(symbols_to_monitor)
                
                # Vérifier chaque alerte
                for alert in active_alerts:
                    self._check_alert(alert)
                
                # Nettoyer les alertes déclenchées anciennes
                self._cleanup_triggered_alerts()
                
            except Exception as e:
                logger.error(f"❌ Erreur dans la boucle de surveillance: {e}")
            
            time.sleep(self.check_interval)
    
    def _fetch_current_prices(self, symbols: List[str]):
        """Récupérer les prix actuels pour une liste de symboles"""
        try:
            for symbol in symbols:
                try:
                    # Utiliser l'API Binance pour récupérer le prix
                    price_data = self.binance_api.get_ticker_price(symbol)
                    if price_data and 'price' in price_data:
                        self.current_prices[symbol] = price_data['price']  # Déjà un float
                        logger.debug(f"📊 Prix {symbol}: {self.current_prices[symbol]}")
                except Exception as e:
                    logger.warning(f"⚠️ Impossible de récupérer le prix pour {symbol}: {e}")
        
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des prix: {e}")
    
    def _check_alert(self, alert: Dict):
        """Vérifier si une alerte doit être déclenchée"""
        symbol = alert['symbol']
        alert_id = alert['id']
        
        # Éviter de déclencher la même alerte plusieurs fois
        alert_key = f"{alert_id}_{symbol}"
        if alert_key in self.triggered_alerts:
            return
        
        # Vérifier si nous avons le prix actuel
        if symbol not in self.current_prices:
            return
        
        current_price = self.current_prices[symbol]
        target_price = alert['price']
        alert_type = alert['type']
        
        should_trigger = False
        
        # Vérifier les conditions de déclenchement
        if alert_type == 'Prix Supérieur à (Above)' and current_price >= target_price:
            should_trigger = True
        elif alert_type == 'Prix Inférieur à (Below)' and current_price <= target_price:
            should_trigger = True
        
        if should_trigger:
            self._trigger_alert(alert, current_price)
            self.triggered_alerts.add(alert_key)
    
    def _trigger_alert(self, alert: Dict, current_price: float):
        """Déclencher une alerte"""
        alert_data = {
            'alert': alert,
            'current_price': current_price,
            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'type': 'price_alert'
        }
        
        # Log de l'alerte
        symbol = alert['symbol']
        condition = "au-dessus" if alert['type'] == 'Prix Supérieur à (Above)' else "en-dessous"
        logger.info(f"🚨 ALERTE DÉCLENCHÉE: {symbol} est {condition} de {alert['price']:.10f} "
                   f"(Prix actuel: {current_price:.10f})")
        
        # Appeler tous les callbacks de notification
        for callback in self.notification_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                logger.error(f"❌ Erreur dans le callback de notification: {e}")
        
        # Désactiver l'alerte pour éviter les déclenchements multiples
        alerts_manager.update_alert(alert['id'], active=False)
    
    def _cleanup_triggered_alerts(self):
        """Nettoyer les alertes déclenchées (garder seulement les 100 dernières)"""
        if len(self.triggered_alerts) > 100:
            # Garder seulement les 50 plus récentes
            self.triggered_alerts = set(list(self.triggered_alerts)[-50:])
    
    def get_status(self) -> Dict:
        """Récupérer le statut du surveillant"""
        active_alerts = alerts_manager.get_active_alerts()
        monitored_symbols = list(set(alert['symbol'] for alert in active_alerts))
        
        return {
            'is_running': self.is_running,
            'check_interval': self.check_interval,
            'active_alerts_count': len(active_alerts),
            'monitored_symbols': monitored_symbols,
            'current_prices_count': len(self.current_prices),
            'triggered_alerts_count': len(self.triggered_alerts)
        }
    
    def force_check(self):
        """Forcer une vérification immédiate (pour debug)"""
        if not self.is_running:
            logger.warning("⚠️ Surveillant non démarré")
            return
        
        active_alerts = alerts_manager.get_active_alerts()
        symbols_to_monitor = list(set(alert['symbol'] for alert in active_alerts))
        
        self._fetch_current_prices(symbols_to_monitor)
        
        for alert in active_alerts:
            self._check_alert(alert)
        
        logger.info(f"🔍 Vérification forcée terminée - {len(active_alerts)} alertes vérifiées")

class AlertsNotificationManager:
    """Gestionnaire des notifications d'alertes"""
    
    def __init__(self):
        self.notification_history = []
        self.max_history = 50
    
    def browser_notification(self, alert_data: Dict):
        """Notification dans le navigateur (pour Dash)"""
        notification = {
            'id': f"alert_{int(time.time())}",
            'title': f"🚨 Alerte {alert_data['alert']['symbol']}",
            'message': self._format_alert_message(alert_data),
            'type': 'warning',
            'timestamp': alert_data['timestamp'],
            'duration': 10000  # 10 secondes
        }
        
        # Ajouter à l'historique
        self.notification_history.append(notification)
        
        # Limiter l'historique
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[-self.max_history:]
        
        logger.info(f"🔔 Notification créée: {notification['title']}")
        return notification
    
    def console_notification(self, alert_data: Dict):
        """Notification dans la console"""
        message = self._format_alert_message(alert_data)
        print(f"\n{'='*60}")
        print(f"🚨 ALERTE PRIX - {alert_data['timestamp']}")
        print(f"{'='*60}")
        print(message)
        print(f"{'='*60}\n")
    
    def _format_alert_message(self, alert_data: Dict) -> str:
        """Formater le message d'alerte"""
        alert = alert_data['alert']
        current_price = alert_data['current_price']
        
        condition = "au-dessus" if alert['type'] == 'Prix Supérieur à (Above)' else "en-dessous"
        
        message = f"{alert['symbol']} est passé {condition} de {alert['price']:.10f}\n"
        message += f"Prix actuel: {current_price:.10f}\n"
        
        if alert.get('message'):
            message += f"Message: {alert['message']}\n"
        
        return message
    
    def get_recent_notifications(self, limit: int = 10) -> List[Dict]:
        """Récupérer les notifications récentes"""
        return self.notification_history[-limit:]

# Instances globales
alerts_monitor = AlertsMonitor(check_interval=15)  # Vérification toutes les 15 secondes
notification_manager = AlertsNotificationManager()

# Enregistrer les callbacks de notification
alerts_monitor.add_notification_callback(notification_manager.browser_notification)
alerts_monitor.add_notification_callback(notification_manager.console_notification)

def start_alerts_monitoring():
    """Fonction helper pour démarrer la surveillance"""
    alerts_monitor.start_monitoring()

def stop_alerts_monitoring():
    """Fonction helper pour arrêter la surveillance"""
    alerts_monitor.stop_monitoring()

def get_monitoring_status():
    """Fonction helper pour récupérer le statut"""
    return alerts_monitor.get_status()