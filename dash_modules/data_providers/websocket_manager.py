"""
WebSocket Manager pour données crypto en temps réel
Gestion des connexions WebSocket Binance avec reconnexion automatique
"""

import json
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional

import websocket

logger = logging.getLogger(__name__)


class BinanceWebSocketManager:
    """Gestionnaire WebSocket pour les données Binance en temps réel"""

    def __init__(self):
        """Initialise le gestionnaire WebSocket"""
        self.base_url = "wss://stream.binance.com:9443/ws/"
        self.connections: Dict[str, websocket.WebSocketApp] = {}
        self.callbacks: Dict[str, Callable] = {}
        self.latest_data: Dict[str, Dict[str, Any]] = {}
        self.running: Dict[str, bool] = {}

        logger.info("🚀 WebSocket Manager initialisé")

    def _create_url(self, symbol: str) -> str:
        """Crée l'URL WebSocket pour un symbole"""
        return f"{self.base_url}{symbol.lower()}@ticker"

    def _on_open(self, ws, symbol: str):
        """Callback d'ouverture de connexion"""
        logger.info(f"✅ WebSocket connecté: {symbol}")

    def _on_message(self, ws, message: str, symbol: str):
        """Callback de réception de message"""
        try:
            data = json.loads(message)

            # Extraire les données importantes
            parsed_data = {
                "symbol": data["s"],
                "price": float(data["c"]),
                "price_change": float(data["P"]),
                "volume": float(data["v"]),
                "high_24h": float(data["h"]),
                "low_24h": float(data["l"]),
                "timestamp": int(data["E"]),
            }

            # Stocker les dernières données
            self.latest_data[symbol] = parsed_data

            # Exécuter callback si défini
            if symbol in self.callbacks and self.callbacks[symbol]:
                self.callbacks[symbol](parsed_data)

        except Exception as e:
            logger.error(f"❌ Erreur parsing message {symbol}: {e}")

    def _on_error(self, ws, error, symbol: str):
        """Callback d'erreur"""
        logger.error(f"❌ Erreur WebSocket {symbol}: {error}")

    def _on_close(self, ws, close_status_code, close_msg, symbol: str):
        """Callback de fermeture"""
        logger.info(f"🔌 WebSocket fermé: {symbol}")

        # Reconnecter si encore actif
        if self.running.get(symbol, False):
            logger.info(f"🔄 Reconnexion {symbol}...")
            time.sleep(5)  # Attendre avant de reconnecter
            self._create_connection(symbol)

    def _reconnect(self, symbol: str):
        """Reconnecte un WebSocket"""
        try:
            # Fermer l'ancienne connexion
            if symbol in self.connections:
                self.connections[symbol].close()
        except:
            pass

        # Créer nouvelle connexion
        self._create_connection(symbol)

    def _create_connection(self, symbol: str):
        """Crée une nouvelle connexion WebSocket"""
        try:
            url = self._create_url(symbol)

            # Créer WebSocket avec callbacks
            ws = websocket.WebSocketApp(
                url,
                on_open=lambda ws: self._on_open(ws, symbol),
                on_message=lambda ws, msg: self._on_message(ws, msg, symbol),
                on_error=lambda ws, error: self._on_error(ws, error, symbol),
                on_close=lambda ws, code, msg: self._on_close(ws, code, msg, symbol),
            )

            self.connections[symbol] = ws

            # Démarrer en thread séparé
            thread = threading.Thread(
                target=ws.run_forever, name=f"WebSocket-{symbol}", daemon=True
            )
            thread.start()

            logger.info(f"🚀 WebSocket démarré: {symbol}")

        except Exception as e:
            logger.error(f"❌ Erreur création WebSocket {symbol}: {e}")

    def subscribe(self, symbol: str, callback: Optional[Callable] = None) -> bool:
        """Démarre la souscription WebSocket pour un symbole"""
        try:
            symbol = symbol.upper()

            if symbol in self.running and self.running[symbol]:
                logger.warning(f"⚠️ WebSocket déjà actif pour {symbol}")
                return True

            # Enregistrer callback
            if callback:
                self.callbacks[symbol] = callback

            # Marquer comme actif
            self.running[symbol] = True

            # Créer connexion
            self._create_connection(symbol)

            return True

        except Exception as e:
            logger.error(f"❌ Erreur souscription {symbol}: {e}")
            return False

    def unsubscribe(self, symbol: str) -> bool:
        """Arrête la souscription WebSocket pour un symbole"""
        try:
            symbol = symbol.upper()

            # Marquer comme inactif
            self.running[symbol] = False

            # Fermer connexion
            if symbol in self.connections:
                self.connections[symbol].close()
                del self.connections[symbol]

            # Supprimer callback
            if symbol in self.callbacks:
                del self.callbacks[symbol]

            # Supprimer données
            if symbol in self.latest_data:
                del self.latest_data[symbol]

            logger.info(f"🔌 WebSocket fermé: {symbol}")
            return True

        except Exception as e:
            logger.error(f"❌ Erreur fermeture {symbol}: {e}")
            return False

    def get_latest_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Récupère les dernières données pour un symbole"""
        return self.latest_data.get(symbol.upper())

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Récupère le dernier prix pour un symbole"""
        data = self.get_latest_data(symbol)
        return data.get("price") if data else None

    def is_connected(self, symbol: str) -> bool:
        """Vérifie si WebSocket est connecté pour un symbole"""
        return symbol.upper() in self.connections and self.running.get(
            symbol.upper(), False
        )

    def get_all_connected_symbols(self) -> list:
        """Retourne la liste des symboles connectés"""
        return [symbol for symbol, running in self.running.items() if running]

    def cleanup(self):
        """Nettoie toutes les connexions WebSocket"""
        logger.info("🧹 Nettoyage WebSocket Manager...")
        for symbol in list(self.running.keys()):
            self.unsubscribe(symbol)
        logger.info("✅ WebSocket Manager nettoyé")


# Instance globale pour l'application
ws_manager = BinanceWebSocketManager()


def get_websocket_manager() -> BinanceWebSocketManager:
    """Fonction helper pour obtenir le gestionnaire WebSocket"""
    return ws_manager


def subscribe_symbol(symbol: str, callback: Optional[Callable] = None) -> bool:
    """Fonction helper pour souscrire à un symbole"""
    return ws_manager.subscribe(symbol, callback)


def unsubscribe_symbol(symbol: str) -> bool:
    """Fonction helper pour se désabonner d'un symbole"""
    return ws_manager.unsubscribe(symbol)
