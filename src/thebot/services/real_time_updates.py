"""
Real-Time Data Subscription System - Gère les mises à jour temps réel
Responsable: Notifier les composants UI des changements de données
Architecture: Observer pattern + Async streams
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

from src.thebot.core.logger import logger
from src.thebot.core.types import TimeFrame


@dataclass
class DataUpdateEvent:
    """Événement de mise à jour de données"""
    symbol: str
    timeframe: TimeFrame
    timestamp: datetime
    data: Any
    indicators: Dict[str, Any]
    signals: List[Dict[str, Any]]


class RealTimeDataSubscriber:
    """
    Gestionnaire de souscriptions temps réel
    Gère les observateurs et les notifications
    """

    def __init__(self):
        """Initialiser le gestionnaire"""
        self.subscribers: Dict[str, Set[Callable]] = {}
        self.active_streams: Dict[str, asyncio.Task] = {}
        logger.info("✅ RealTimeDataSubscriber initialized")

    def subscribe(
        self,
        symbol: str,
        timeframe: TimeFrame,
        callback: Callable[[DataUpdateEvent], None]
    ) -> str:
        """
        S'abonner aux mises à jour d'un symbol
        
        Args:
            symbol: Symbol (ex: 'BTCUSDT')
            timeframe: Timeframe (ex: TimeFrame.H1)
            callback: Fonction callback à appeler
            
        Returns:
            Identifiant de souscription
        """
        try:
            sub_key = f"{symbol}_{timeframe.value}"
            
            if sub_key not in self.subscribers:
                self.subscribers[sub_key] = set()
            
            self.subscribers[sub_key].add(callback)
            
            logger.info(f"✅ Subscribed to {sub_key}")
            return sub_key
            
        except Exception as e:
            logger.error(f"❌ Subscription error: {e}")
            raise

    def unsubscribe(
        self,
        symbol: str,
        timeframe: TimeFrame,
        callback: Callable[[DataUpdateEvent], None]
    ) -> bool:
        """
        Se désabonner
        
        Args:
            symbol: Symbol
            timeframe: Timeframe
            callback: Fonction callback
            
        Returns:
            True si succès
        """
        try:
            sub_key = f"{symbol}_{timeframe.value}"
            
            if sub_key in self.subscribers:
                self.subscribers[sub_key].discard(callback)
                
                if not self.subscribers[sub_key]:
                    del self.subscribers[sub_key]
                
                logger.info(f"✅ Unsubscribed from {sub_key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Unsubscription error: {e}")
            return False

    async def notify(self, event: DataUpdateEvent) -> None:
        """
        Notifier tous les observateurs d'un événement
        
        Args:
            event: Événement à notifier
        """
        try:
            sub_key = f"{event.symbol}_{event.timeframe.value}"
            
            if sub_key in self.subscribers:
                callbacks = self.subscribers[sub_key].copy()
                
                for callback in callbacks:
                    try:
                        # Appeler le callback
                        if asyncio.iscoroutinefunction(callback):
                            await callback(event)
                        else:
                            callback(event)
                            
                    except Exception as e:
                        logger.error(f"❌ Callback error: {e}")
                        continue
                
                logger.debug(f"✅ Notified {len(callbacks)} subscribers for {sub_key}")
                
        except Exception as e:
            logger.error(f"❌ Notification error: {e}")

    def get_subscriber_count(
        self,
        symbol: str,
        timeframe: TimeFrame
    ) -> int:
        """
        Obtenir le nombre d'observateurs
        
        Args:
            symbol: Symbol
            timeframe: Timeframe
            
        Returns:
            Nombre d'observateurs
        """
        sub_key = f"{symbol}_{timeframe.value}"
        return len(self.subscribers.get(sub_key, set()))

    def get_active_subscriptions(self) -> List[str]:
        """
        Lister les souscriptions actives
        
        Returns:
            Liste des clés de souscription
        """
        return list(self.subscribers.keys())

    def clear(self) -> None:
        """Effacer toutes les souscriptions"""
        self.subscribers.clear()
        logger.info("✅ All subscriptions cleared")


class SignalAggregator:
    """
    Agrégateur de signaux - Combine les signaux de plusieurs indicateurs
    """

    def __init__(self):
        """Initialiser l'agrégateur"""
        self.signal_history: Dict[str, List[Dict[str, Any]]] = {}
        self.alerts: Dict[str, List[Dict[str, Any]]] = {}
        logger.info("✅ SignalAggregator initialized")

    def add_signal(
        self,
        symbol: str,
        timeframe: TimeFrame,
        indicator_name: str,
        signal_data: Dict[str, Any]
    ) -> None:
        """
        Ajouter un signal
        
        Args:
            symbol: Symbol
            timeframe: Timeframe
            indicator_name: Nom de l'indicateur
            signal_data: Données du signal
        """
        try:
            history_key = f"{symbol}_{timeframe.value}"
            
            if history_key not in self.signal_history:
                self.signal_history[history_key] = []
            
            signal_entry = {
                'indicator': indicator_name,
                'timestamp': datetime.now().isoformat(),
                **signal_data
            }
            
            self.signal_history[history_key].append(signal_entry)
            logger.info(f"✅ Signal added: {indicator_name} on {symbol}")
            
        except Exception as e:
            logger.error(f"❌ Error adding signal: {e}")

    def get_signals(
        self,
        symbol: str,
        timeframe: TimeFrame,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupérer les signaux
        
        Args:
            symbol: Symbol
            timeframe: Timeframe
            limit: Nombre max de signaux
            
        Returns:
            Liste des signaux
        """
        history_key = f"{symbol}_{timeframe.value}"
        signals = self.signal_history.get(history_key, [])
        return signals[-limit:]

    def get_signal_statistics(
        self,
        symbol: str,
        timeframe: TimeFrame
    ) -> Dict[str, Any]:
        """
        Obtenir les statistiques de signaux
        
        Args:
            symbol: Symbol
            timeframe: Timeframe
            
        Returns:
            Statistiques
        """
        history_key = f"{symbol}_{timeframe.value}"
        signals = self.signal_history.get(history_key, [])
        
        if not signals:
            return {
                'total_signals': 0,
                'by_indicator': {},
                'by_direction': {}
            }
        
        # Compter par indicateur
        by_indicator = {}
        by_direction = {}
        
        for signal in signals:
            indicator = signal.get('indicator', 'unknown')
            direction = signal.get('direction', 'unknown')
            
            by_indicator[indicator] = by_indicator.get(indicator, 0) + 1
            by_direction[direction] = by_direction.get(direction, 0) + 1
        
        return {
            'total_signals': len(signals),
            'by_indicator': by_indicator,
            'by_direction': by_direction,
            'last_signal': signals[-1] if signals else None
        }

    def clear_history(
        self,
        symbol: Optional[str] = None,
        timeframe: Optional[TimeFrame] = None
    ) -> None:
        """
        Effacer l'historique de signaux
        
        Args:
            symbol: Symbol spécifique ou None pour tout
            timeframe: Timeframe spécifique ou None pour tout
        """
        if symbol and timeframe:
            history_key = f"{symbol}_{timeframe}"
            if history_key in self.signal_history:
                del self.signal_history[history_key]
        else:
            self.signal_history.clear()
        
        logger.info("✅ Signal history cleared")


# Instances globales
real_time_subscriber = RealTimeDataSubscriber()
signal_aggregator = SignalAggregator()


def get_subscriber() -> RealTimeDataSubscriber:
    """Obtenir l'instance du subscriber"""
    return real_time_subscriber


def get_signal_aggregator() -> SignalAggregator:
    """Obtenir l'instance de l'agrégateur"""
    return signal_aggregator
