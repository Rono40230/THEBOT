"""
Signal Notification and Alert Management Service

This module provides real-time signal notification and alert management,
including toast notifications, audio alerts, and signal history tracking.

Key Features:
- Real-time signal detection and notification
- Toast notifications via dcc.Toast (Dash Bootstrap Components)
- Audio alerts with configurable sound
- Signal history persistence
- Observer pattern for alert subscribers
- Async-safe notification delivery

Architecture:
- SignalConfig: Configuration for alerts
- SignalAlert: Data structure for alert details
- AlertManager: Main service managing notifications
- get_alert_manager(): Singleton factory
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Literal
from collections import deque
from decimal import Decimal


logger = logging.getLogger(__name__)


class AlertType:
    """Alert type constants"""
    BUY = "BUY"
    SELL = "SELL"
    WARNING = "WARNING"
    INFO = "INFO"


class AlertStatus:
    """Alert status constants"""
    ACTIVE = "ACTIVE"
    DISMISSED = "DISMISSED"
    EXPIRED = "EXPIRED"


@dataclass
class SignalConfig:
    """Configuration for signal alerts and notifications
    
    Attributes:
        enable_toast: Enable toast notifications
        enable_audio: Enable audio alerts
        enable_browser: Enable browser notifications
        history_size: Maximum number of signals to keep in history
        toast_duration: Toast display duration in milliseconds
        audio_path: Path to alert sound file
        notification_timeout: Time before alert auto-expires (seconds)
    """
    enable_toast: bool = True
    enable_audio: bool = True
    enable_browser: bool = False
    history_size: int = 100
    toast_duration: int = 5000
    audio_path: str = "/assets/alert.mp3"
    notification_timeout: int = 30
    
    def __post_init__(self) -> None:
        """Validate configuration"""
        if self.history_size <= 0:
            raise ValueError("history_size must be positive")
        if self.toast_duration <= 0:
            raise ValueError("toast_duration must be positive")
        if self.notification_timeout <= 0:
            raise ValueError("notification_timeout must be positive")


@dataclass
class SignalAlert:
    """Signal alert data structure
    
    Attributes:
        id: Unique alert identifier (timestamp-based)
        signal_type: BUY or SELL
        symbol: Trading pair (e.g., "BTCUSDT")
        price: Price at signal time
        indicator: Indicator that generated signal
        timeframe: Timeframe of signal
        strength: Signal strength 0.0-1.0
        message: Alert message text
        timestamp: When alert was created
        status: ACTIVE, DISMISSED, or EXPIRED
        dismissed_at: When alert was dismissed
    """
    id: str
    signal_type: str  # BUY or SELL
    symbol: str
    price: Decimal
    indicator: str
    timeframe: str
    strength: float
    message: str
    timestamp: datetime
    status: str = AlertStatus.ACTIVE
    dismissed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "signal_type": self.signal_type,
            "symbol": self.symbol,
            "price": str(self.price),
            "indicator": self.indicator,
            "timeframe": self.timeframe,
            "strength": self.strength,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "dismissed_at": self.dismissed_at.isoformat() if self.dismissed_at else None,
        }
    
    def is_expired(self, timeout_seconds: int) -> bool:
        """Check if alert has expired
        
        Args:
            timeout_seconds: Expiration timeout in seconds
            
        Returns:
            True if alert has expired
        """
        elapsed = (datetime.now() - self.timestamp).total_seconds()
        return elapsed > timeout_seconds


class AlertManager:
    """Manages signal notifications and alerts
    
    This service:
    - Creates and tracks alerts
    - Manages notification delivery
    - Maintains alert history
    - Supports observer pattern for subscriptions
    - Handles audio/toast notifications
    
    Thread-safe via async/await patterns.
    """
    
    def __init__(self, config: Optional[SignalConfig] = None) -> None:
        """Initialize AlertManager
        
        Args:
            config: SignalConfig instance (defaults to SignalConfig())
        """
        self.config = config or SignalConfig()
        self.alerts: Dict[str, SignalAlert] = {}  # id -> alert
        self.history: deque = deque(maxlen=self.config.history_size)
        self.observers: List[Callable] = []
        self.async_observers: List[Callable] = []
        self._lock = asyncio.Lock()
        logger.info(
            f"AlertManager initialized with config: "
            f"toast={self.config.enable_toast}, "
            f"audio={self.config.enable_audio}, "
            f"history_size={self.config.history_size}"
        )
    
    async def create_alert(
        self,
        signal_type: str,
        symbol: str,
        price: Decimal,
        indicator: str,
        timeframe: str,
        strength: float = 0.5,
        message: Optional[str] = None,
    ) -> SignalAlert:
        """Create and broadcast a new signal alert
        
        Args:
            signal_type: BUY or SELL
            symbol: Trading pair (e.g., "BTCUSDT")
            price: Price at signal time
            indicator: Indicator name
            timeframe: Timeframe (e.g., "1h")
            strength: Signal strength 0.0-1.0
            message: Optional custom message
            
        Returns:
            Created SignalAlert instance
            
        Raises:
            ValueError: Invalid signal_type or strength
        """
        if signal_type not in [AlertType.BUY, AlertType.SELL]:
            raise ValueError(f"Invalid signal_type: {signal_type}")
        if not 0.0 <= strength <= 1.0:
            raise ValueError(f"strength must be 0.0-1.0, got {strength}")
        
        async with self._lock:
            # Generate unique alert ID
            alert_id = f"{symbol}_{signal_type}_{int(datetime.now().timestamp() * 1000)}"
            
            # Build message if not provided
            if message is None:
                message = f"{signal_type} signal on {symbol} at {price} ({indicator}, {timeframe})"
            
            # Create alert
            alert = SignalAlert(
                id=alert_id,
                signal_type=signal_type,
                symbol=symbol,
                price=price,
                indicator=indicator,
                timeframe=timeframe,
                strength=strength,
                message=message,
                timestamp=datetime.now(),
                status=AlertStatus.ACTIVE,
            )
            
            # Store alert
            self.alerts[alert_id] = alert
            self.history.append(alert)
            
            logger.info(
                f"Alert created: {signal_type} {symbol} @ {price} "
                f"({indicator}, strength={strength:.2f})"
            )
            
            # Notify observers
            await self._notify_observers(alert)
            
            return alert
    
    async def dismiss_alert(self, alert_id: str) -> Optional[SignalAlert]:
        """Dismiss an active alert
        
        Args:
            alert_id: Alert ID to dismiss
            
        Returns:
            Updated SignalAlert, or None if not found
        """
        async with self._lock:
            if alert_id not in self.alerts:
                logger.warning(f"Alert not found: {alert_id}")
                return None
            
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.DISMISSED
            alert.dismissed_at = datetime.now()
            
            logger.info(f"Alert dismissed: {alert_id}")
            return alert
    
    async def expire_stale_alerts(self) -> int:
        """Mark expired alerts as expired based on timeout
        
        Returns:
            Number of alerts expired
        """
        async with self._lock:
            expired_count = 0
            now = datetime.now()
            
            for alert_id, alert in list(self.alerts.items()):
                if alert.status == AlertStatus.ACTIVE:
                    elapsed = (now - alert.timestamp).total_seconds()
                    if elapsed > self.config.notification_timeout:
                        alert.status = AlertStatus.EXPIRED
                        expired_count += 1
                        logger.debug(f"Alert expired: {alert_id}")
            
            return expired_count
    
    def get_alert(self, alert_id: str) -> Optional[SignalAlert]:
        """Get alert by ID (synchronous)
        
        Args:
            alert_id: Alert ID
            
        Returns:
            SignalAlert or None if not found
        """
        return self.alerts.get(alert_id)
    
    def get_active_alerts(self) -> List[SignalAlert]:
        """Get all active alerts (synchronous)
        
        Returns:
            List of active SignalAlert instances
        """
        return [
            alert for alert in self.alerts.values()
            if alert.status == AlertStatus.ACTIVE
        ]
    
    def get_alert_history(self, limit: Optional[int] = None) -> List[SignalAlert]:
        """Get alert history (synchronous)
        
        Args:
            limit: Maximum number of alerts to return (None = all)
            
        Returns:
            List of SignalAlert instances in chronological order
        """
        history_list = list(self.history)
        if limit:
            history_list = history_list[-limit:]
        return history_list
    
    def get_recent_signals(
        self,
        symbol: Optional[str] = None,
        signal_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[SignalAlert]:
        """Get recent signals with optional filtering (synchronous)
        
        Args:
            symbol: Filter by symbol (e.g., "BTCUSDT")
            signal_type: Filter by BUY or SELL
            limit: Maximum number of signals
            
        Returns:
            List of recent SignalAlert instances
        """
        signals = list(self.history)
        
        if symbol:
            signals = [s for s in signals if s.symbol == symbol]
        if signal_type:
            signals = [s for s in signals if s.signal_type == signal_type]
        
        return signals[-limit:]
    
    def add_observer(self, observer: Callable[[SignalAlert], None]) -> None:
        """Add synchronous observer for alerts
        
        Args:
            observer: Callable that receives SignalAlert
        """
        if observer not in self.observers:
            self.observers.append(observer)
            logger.debug(f"Observer added (sync): {observer.__name__}")
    
    def add_async_observer(
        self, observer: Callable[[SignalAlert], Any]
    ) -> None:
        """Add async observer for alerts
        
        Args:
            observer: Async callable that receives SignalAlert
        """
        if observer not in self.async_observers:
            self.async_observers.append(observer)
            logger.debug(f"Observer added (async): {observer.__name__}")
    
    def remove_observer(self, observer: Callable) -> None:
        """Remove observer
        
        Args:
            observer: Observer to remove
        """
        if observer in self.observers:
            self.observers.remove(observer)
            logger.debug(f"Observer removed (sync): {observer.__name__}")
        if observer in self.async_observers:
            self.async_observers.remove(observer)
            logger.debug(f"Observer removed (async): {observer.__name__}")
    
    async def _notify_observers(self, alert: SignalAlert) -> None:
        """Notify all observers of new alert (internal)
        
        Args:
            alert: SignalAlert to broadcast
        """
        # Synchronous observers
        for observer in self.observers:
            try:
                observer(alert)
            except Exception as e:
                logger.error(f"Observer error: {observer.__name__}: {e}")
        
        # Asynchronous observers (concurrent)
        if self.async_observers:
            tasks = [
                observer(alert) for observer in self.async_observers
            ]
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                logger.error(f"Async observer error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get AlertManager status (synchronous)
        
        Returns:
            Status dictionary with metrics
        """
        active_alerts = self.get_active_alerts()
        dismissed_alerts = [
            a for a in self.alerts.values()
            if a.status == AlertStatus.DISMISSED
        ]
        expired_alerts = [
            a for a in self.alerts.values()
            if a.status == AlertStatus.EXPIRED
        ]
        
        return {
            "active_count": len(active_alerts),
            "dismissed_count": len(dismissed_alerts),
            "expired_count": len(expired_alerts),
            "total_count": len(self.alerts),
            "history_size": len(self.history),
            "config": {
                "enable_toast": self.config.enable_toast,
                "enable_audio": self.config.enable_audio,
                "enable_browser": self.config.enable_browser,
                "history_size": self.config.history_size,
            },
            "observers": len(self.observers) + len(self.async_observers),
            "timestamp": datetime.now().isoformat(),
        }


# Global singleton instance
_alert_manager: Optional[AlertManager] = None


def get_alert_manager(config: Optional[SignalConfig] = None) -> AlertManager:
    """Get or create AlertManager singleton
    
    Args:
        config: Optional SignalConfig for initialization
        
    Returns:
        AlertManager singleton instance
    """
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager(config)
    return _alert_manager
