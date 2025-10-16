"""
Phase 5.3 - WebSocket Manager Service
Real-time market data streaming via WebSocket
"""

import asyncio
import json
import logging
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """WebSocket connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    timestamp: datetime
    type: str
    data: Dict[str, Any]
    source: str = "websocket"


@dataclass
class WebSocketConfig:
    """WebSocket configuration"""
    url: str = "wss://stream.binance.com:9443/ws"
    max_reconnect_attempts: int = 5
    reconnect_delay: float = 1.0
    max_reconnect_delay: float = 30.0
    heartbeat_interval: float = 30.0
    message_queue_size: int = 1000


class WebSocketManager:
    """
    Manages WebSocket connections for real-time market data
    Handles connection, reconnection, message broadcasting
    """

    def __init__(self, config: Optional[WebSocketConfig] = None):
        """
        Initialize WebSocket Manager
        
        Args:
            config: WebSocket configuration
        """
        self.config = config or WebSocketConfig()
        self.status = ConnectionStatus.DISCONNECTED
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[aiohttp.ClientWebSocketResponse] = None
        
        self._observers: List[Callable[[WebSocketMessage], None]] = []
        self._message_queue: asyncio.Queue[WebSocketMessage] = asyncio.Queue(
            maxsize=self.config.message_queue_size
        )
        self._reconnect_count = 0
        self._last_message_time: Optional[datetime] = None
        self._running = False
        self._subscriptions: Dict[str, List[str]] = {}
        
        logger.info("✅ WebSocketManager initialized")

    async def connect(self) -> bool:
        """
        Connect to WebSocket server
        
        Returns:
            bool: True if connection successful
        """
        if self.status == ConnectionStatus.CONNECTED:
            logger.warning("Already connected")
            return True
        
        try:
            self.status = ConnectionStatus.CONNECTING
            logger.info(f"🔗 Connecting to {self.config.url}...")
            
            if self.session is None:
                self.session = aiohttp.ClientSession()
            
            self.websocket = await self.session.ws_connect(
                self.config.url,
                autoclose=False,
                autoping=True,
            )
            
            self.status = ConnectionStatus.CONNECTED
            self._reconnect_count = 0
            self._last_message_time = datetime.now()
            self._running = True
            
            logger.info("✅ WebSocket connected")
            
            # Start message processing
            asyncio.create_task(self._process_messages())
            asyncio.create_task(self._heartbeat())
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            self.status = ConnectionStatus.ERROR
            return False

    async def disconnect(self) -> None:
        """Disconnect from WebSocket"""
        self._running = False
        
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        if self.session:
            await self.session.close()
            self.session = None
        
        self.status = ConnectionStatus.DISCONNECTED
        logger.info("✅ WebSocket disconnected")

    async def reconnect(self) -> bool:
        """
        Attempt to reconnect with exponential backoff
        
        Returns:
            bool: True if reconnection successful
        """
        if self._reconnect_count >= self.config.max_reconnect_attempts:
            logger.error("❌ Max reconnection attempts reached")
            return False
        
        self.status = ConnectionStatus.RECONNECTING
        
        # Exponential backoff
        delay = min(
            self.config.reconnect_delay * (2 ** self._reconnect_count),
            self.config.max_reconnect_delay
        )
        
        logger.info(f"⏳ Reconnecting in {delay:.1f}s (attempt {self._reconnect_count + 1})")
        await asyncio.sleep(delay)
        
        self._reconnect_count += 1
        
        if await self.connect():
            # Resubscribe to streams
            await self._resubscribe()
            return True
        
        # Retry
        return await self.reconnect()

    async def subscribe(self, stream: str, symbols: List[str]) -> bool:
        """
        Subscribe to WebSocket stream
        
        Args:
            stream: Stream type (e.g., 'trades', 'klines')
            symbols: List of symbols (e.g., ['BTCUSDT', 'ETHUSDT'])
            
        Returns:
            bool: True if subscription successful
        """
        if not self.websocket or self.status != ConnectionStatus.CONNECTED:
            logger.warning("WebSocket not connected")
            return False
        
        try:
            # Build subscription list
            streams = [f"{symbol.lower()}@{stream}" for symbol in symbols]
            
            # Subscribe
            await self.websocket.send_json({
                "method": "SUBSCRIBE",
                "params": streams,
                "id": 1
            })
            
            # Track subscription
            if stream not in self._subscriptions:
                self._subscriptions[stream] = []
            self._subscriptions[stream].extend(symbols)
            
            logger.info(f"✅ Subscribed to {stream}: {symbols}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Subscription error: {e}")
            return False

    async def unsubscribe(self, stream: str, symbols: List[str]) -> bool:
        """
        Unsubscribe from WebSocket stream
        
        Args:
            stream: Stream type
            symbols: List of symbols
            
        Returns:
            bool: True if unsubscription successful
        """
        if not self.websocket or self.status != ConnectionStatus.CONNECTED:
            return False
        
        try:
            streams = [f"{symbol.lower()}@{stream}" for symbol in symbols]
            
            await self.websocket.send_json({
                "method": "UNSUBSCRIBE",
                "params": streams,
                "id": 2
            })
            
            # Update tracking
            if stream in self._subscriptions:
                self._subscriptions[stream] = [
                    s for s in self._subscriptions[stream] if s not in symbols
                ]
            
            logger.info(f"✅ Unsubscribed from {stream}: {symbols}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Unsubscription error: {e}")
            return False

    async def add_observer(self, observer: Callable[[WebSocketMessage], None]) -> None:
        """
        Add observer for WebSocket messages
        
        Args:
            observer: Callback function
        """
        self._observers.append(observer)
        logger.debug(f"✅ Observer added (total: {len(self._observers)})")

    async def remove_observer(self, observer: Callable[[WebSocketMessage], None]) -> None:
        """
        Remove observer
        
        Args:
            observer: Callback function
        """
        if observer in self._observers:
            self._observers.remove(observer)
            logger.debug(f"✅ Observer removed (total: {len(self._observers)})")

    async def _process_messages(self) -> None:
        """Process incoming WebSocket messages"""
        try:
            while self._running and self.websocket:
                msg = await self.websocket.receive()
                
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        
                        # Parse message
                        ws_message = WebSocketMessage(
                            timestamp=datetime.now(),
                            type=self._get_message_type(data),
                            data=data
                        )
                        
                        # Update last message time
                        self._last_message_time = ws_message.timestamp
                        
                        # Add to queue
                        try:
                            self._message_queue.put_nowait(ws_message)
                        except asyncio.QueueFull:
                            logger.warning("Message queue full, dropping oldest message")
                            try:
                                self._message_queue.get_nowait()
                                self._message_queue.put_nowait(ws_message)
                            except:
                                pass
                        
                        # Notify observers
                        for observer in self._observers:
                            try:
                                if asyncio.iscoroutinefunction(observer):
                                    await observer(ws_message)
                                else:
                                    observer(ws_message)
                            except Exception as e:
                                logger.error(f"Observer error: {e}")
                    
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON parse error: {e}")
                
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {self.websocket.exception()}")
                    self.status = ConnectionStatus.ERROR
                    
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    logger.info("WebSocket closed by server")
                    await self.reconnect()
        
        except asyncio.CancelledError:
            logger.debug("Message processing cancelled")
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            await self.reconnect()

    async def _heartbeat(self) -> None:
        """Monitor connection health"""
        while self._running and self.websocket:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)
                
                if self.status != ConnectionStatus.CONNECTED:
                    continue
                
                # Check if received message recently
                if self._last_message_time:
                    elapsed = (datetime.now() - self._last_message_time).total_seconds()
                    if elapsed > self.config.heartbeat_interval * 2:
                        logger.warning(f"No messages for {elapsed:.1f}s, checking connection...")
                        
                        # Try sending ping
                        try:
                            await self.websocket.ping()
                        except Exception as e:
                            logger.error(f"Heartbeat ping failed: {e}")
                            await self.reconnect()
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")

    async def _resubscribe(self) -> None:
        """Resubscribe to all streams after reconnection"""
        for stream, symbols in self._subscriptions.items():
            await self.subscribe(stream, symbols)

    async def get_message(self, timeout: Optional[float] = None) -> Optional[WebSocketMessage]:
        """
        Get next message from queue
        
        Args:
            timeout: Wait timeout in seconds
            
        Returns:
            WebSocketMessage or None if timeout
        """
        try:
            return await asyncio.wait_for(
                self._message_queue.get(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            return None

    def get_status(self) -> Dict[str, Any]:
        """
        Get connection status
        
        Returns:
            Status dictionary
        """
        return {
            "status": self.status.value,
            "connected": self.status == ConnectionStatus.CONNECTED,
            "observers": len(self._observers),
            "subscriptions": self._subscriptions,
            "queue_size": self._message_queue.qsize(),
            "last_message": self._last_message_time.isoformat() if self._last_message_time else None,
            "reconnect_attempts": self._reconnect_count,
        }

    @staticmethod
    def _get_message_type(data: Dict) -> str:
        """Extract message type from data"""
        if "e" in data:  # Binance format
            return data["e"]
        elif "data" in data and isinstance(data["data"], dict):
            return data["data"].get("type", "unknown")
        return "unknown"


# Global singleton instance
_websocket_manager: Optional[WebSocketManager] = None


def get_websocket_manager(config: Optional[WebSocketConfig] = None) -> WebSocketManager:
    """
    Get or create WebSocket manager singleton
    
    Args:
        config: Optional WebSocket configuration
        
    Returns:
        WebSocketManager instance
    """
    global _websocket_manager
    
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager(config)
    
    return _websocket_manager


logger.info("✅ WebSocket Manager module loaded")
