"""
Phase 5.3 - Data Stream Service
Real-time market data streaming and aggregation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
import pandas as pd

from src.thebot.core.types import TimeFrame, MarketData
from src.thebot.services.websocket_manager import (
    WebSocketManager,
    WebSocketMessage,
    get_websocket_manager
)

logger = logging.getLogger(__name__)


@dataclass
class StreamConfig:
    """Data stream configuration"""
    symbols: List[str] = field(default_factory=lambda: ["BTCUSDT"])
    timeframes: List[TimeFrame] = field(default_factory=lambda: [TimeFrame.H1])
    stream_types: List[str] = field(default_factory=lambda: ["trades", "klines"])
    buffer_size: int = 500
    update_interval: float = 0.1  # 100ms


@dataclass
class SymbolData:
    """Container for symbol market data"""
    symbol: str
    latest_price: Decimal = Decimal("0")
    bid: Decimal = Decimal("0")
    ask: Decimal = Decimal("0")
    volume: Decimal = Decimal("0")
    timestamp: Optional[datetime] = None
    klines: Dict[str, List[Any]] = field(default_factory=dict)
    last_update: Optional[datetime] = None


class DataStream:
    """
    Manages real-time market data streaming
    Aggregates WebSocket messages and maintains data buffers
    """

    def __init__(self, config: Optional[StreamConfig] = None):
        """
        Initialize Data Stream
        
        Args:
            config: Stream configuration
        """
        self.config = config or StreamConfig()
        self.websocket = get_websocket_manager()
        
        self._symbol_data: Dict[str, SymbolData] = {
            symbol: SymbolData(symbol=symbol)
            for symbol in self.config.symbols
        }
        self._observers: List[Callable[[str, SymbolData], None]] = []
        self._running = False
        self._last_update_time = datetime.now()
        
        logger.info(f"✅ DataStream initialized for {len(self.config.symbols)} symbols")

    async def start(self) -> bool:
        """
        Start data streaming
        
        Returns:
            bool: True if started successfully
        """
        try:
            logger.info("🚀 Starting data stream...")
            
            # Connect WebSocket
            if not await self.websocket.connect():
                logger.error("Failed to connect WebSocket")
                return False
            
            # Subscribe to streams
            for stream_type in self.config.stream_types:
                await self.websocket.subscribe(stream_type, self.config.symbols)
            
            # Add observer
            await self.websocket.add_observer(self._on_message)
            
            self._running = True
            
            # Start processing
            asyncio.create_task(self._process_updates())
            
            logger.info("✅ Data stream started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start data stream: {e}")
            return False

    async def stop(self) -> None:
        """Stop data streaming"""
        self._running = False
        await self.websocket.disconnect()
        logger.info("✅ Data stream stopped")

    async def add_observer(
        self,
        observer: Callable[[str, SymbolData], None]
    ) -> None:
        """
        Add observer for data updates
        
        Args:
            observer: Callback function (symbol, data)
        """
        self._observers.append(observer)
        logger.debug(f"✅ Observer added (total: {len(self._observers)})")

    async def remove_observer(
        self,
        observer: Callable[[str, SymbolData], None]
    ) -> None:
        """
        Remove observer
        
        Args:
            observer: Callback function
        """
        if observer in self._observers:
            self._observers.remove(observer)
            logger.debug(f"✅ Observer removed (total: {len(self._observers)})")

    def get_symbol_data(self, symbol: str) -> Optional[SymbolData]:
        """
        Get current data for symbol
        
        Args:
            symbol: Symbol name
            
        Returns:
            SymbolData or None
        """
        return self._symbol_data.get(symbol)

    def get_all_data(self) -> Dict[str, SymbolData]:
        """
        Get all symbol data
        
        Returns:
            Dictionary of symbol data
        """
        return self._symbol_data.copy()

    async def subscribe_symbol(self, symbol: str) -> bool:
        """
        Subscribe to additional symbol
        
        Args:
            symbol: Symbol to subscribe
            
        Returns:
            bool: Success
        """
        if symbol in self._symbol_data:
            logger.warning(f"Already subscribed to {symbol}")
            return True
        
        # Add to config
        self.config.symbols.append(symbol)
        self._symbol_data[symbol] = SymbolData(symbol=symbol)
        
        # Subscribe in WebSocket
        for stream_type in self.config.stream_types:
            await self.websocket.subscribe(stream_type, [symbol])
        
        logger.info(f"✅ Subscribed to {symbol}")
        return True

    async def unsubscribe_symbol(self, symbol: str) -> bool:
        """
        Unsubscribe from symbol
        
        Args:
            symbol: Symbol to unsubscribe
            
        Returns:
            bool: Success
        """
        if symbol not in self._symbol_data:
            logger.warning(f"Not subscribed to {symbol}")
            return False
        
        # Remove from config
        self.config.symbols.remove(symbol)
        del self._symbol_data[symbol]
        
        # Unsubscribe from WebSocket
        for stream_type in self.config.stream_types:
            await self.websocket.unsubscribe(stream_type, [symbol])
        
        logger.info(f"✅ Unsubscribed from {symbol}")
        return True

    async def _on_message(self, message: WebSocketMessage) -> None:
        """
        Handle WebSocket message
        
        Args:
            message: WebSocket message
        """
        try:
            data = message.data
            
            # Handle different message types
            if message.type == "trade":
                await self._handle_trade_message(data)
            elif message.type == "kline":
                await self._handle_kline_message(data)
            elif message.type in ["24hrTicker", "bookTicker"]:
                await self._handle_ticker_message(data)
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def _handle_trade_message(self, data: Dict) -> None:
        """Handle trade message"""
        try:
            # Extract symbol (format: btcusdt from "t@btcusdt")
            symbol = data.get("s", "").upper()
            if symbol not in self._symbol_data:
                return
            
            symbol_data = self._symbol_data[symbol]
            
            # Update price info
            price_str = data.get("p", data.get("price", "0"))
            price = Decimal(str(price_str))
            
            if price > 0:
                symbol_data.latest_price = price
                symbol_data.timestamp = datetime.fromtimestamp(
                    data.get("T", data.get("time", 0)) / 1000
                )
                symbol_data.last_update = datetime.now()
                
                # Notify observers
                await self._notify_observers(symbol, symbol_data)
        
        except Exception as e:
            logger.error(f"Error handling trade message: {e}")

    async def _handle_kline_message(self, data: Dict) -> None:
        """Handle kline (candle) message"""
        try:
            # Extract symbol
            symbol = data.get("s", data.get("symbol", "")).upper()
            if symbol not in self._symbol_data:
                return
            
            symbol_data = self._symbol_data[symbol]
            
            # Extract candle data
            kline = data.get("k", {})
            timeframe_str = kline.get("i", "")
            
            # Initialize timeframe buffer if needed
            if timeframe_str not in symbol_data.klines:
                symbol_data.klines[timeframe_str] = []
            
            candle = {
                "time": kline.get("t"),
                "open": Decimal(str(kline.get("o", "0"))),
                "high": Decimal(str(kline.get("h", "0"))),
                "low": Decimal(str(kline.get("l", "0"))),
                "close": Decimal(str(kline.get("c", "0"))),
                "volume": Decimal(str(kline.get("v", "0"))),
                "complete": kline.get("x", False),
            }
            
            # Add to buffer (keep last N candles)
            symbol_data.klines[timeframe_str].append(candle)
            if len(symbol_data.klines[timeframe_str]) > self.config.buffer_size:
                symbol_data.klines[timeframe_str].pop(0)
            
            symbol_data.last_update = datetime.now()
            
            # Notify observers
            await self._notify_observers(symbol, symbol_data)
        
        except Exception as e:
            logger.error(f"Error handling kline message: {e}")

    async def _handle_ticker_message(self, data: Dict) -> None:
        """Handle ticker message (bid/ask)"""
        try:
            # Extract symbol
            symbol = data.get("s", data.get("symbol", "")).upper()
            if symbol not in self._symbol_data:
                return
            
            symbol_data = self._symbol_data[symbol]
            
            # Update bid/ask
            if "b" in data:  # bid
                symbol_data.bid = Decimal(str(data["b"]))
            if "a" in data:  # ask
                symbol_data.ask = Decimal(str(data["a"]))
            
            # Update volume
            if "v" in data:
                symbol_data.volume = Decimal(str(data["v"]))
            
            symbol_data.last_update = datetime.now()
        
        except Exception as e:
            logger.error(f"Error handling ticker message: {e}")

    async def _notify_observers(
        self,
        symbol: str,
        data: SymbolData
    ) -> None:
        """
        Notify all observers of data update
        
        Args:
            symbol: Symbol name
            data: Updated symbol data
        """
        for observer in self._observers:
            try:
                if asyncio.iscoroutinefunction(observer):
                    await observer(symbol, data)
                else:
                    observer(symbol, data)
            except Exception as e:
                logger.error(f"Observer error: {e}")

    async def _process_updates(self) -> None:
        """Process updates at configured interval"""
        while self._running:
            try:
                await asyncio.sleep(self.config.update_interval)
                
                # Check for stale data
                now = datetime.now()
                for symbol, data in self._symbol_data.items():
                    if data.last_update:
                        elapsed = (now - data.last_update).total_seconds()
                        if elapsed > 30:  # No update for 30 seconds
                            logger.warning(f"No updates for {symbol} ({elapsed:.0f}s)")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Update processing error: {e}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get stream status
        
        Returns:
            Status dictionary
        """
        return {
            "running": self._running,
            "symbols": len(self._symbol_data),
            "observers": len(self._observers),
            "websocket": self.websocket.get_status(),
            "symbols_data": {
                symbol: {
                    "price": str(data.latest_price),
                    "bid": str(data.bid),
                    "ask": str(data.ask),
                    "last_update": data.last_update.isoformat() if data.last_update else None,
                }
                for symbol, data in self._symbol_data.items()
            }
        }


# Global singleton instance
_data_stream: Optional[DataStream] = None


def get_data_stream(config: Optional[StreamConfig] = None) -> DataStream:
    """
    Get or create data stream singleton
    
    Args:
        config: Optional stream configuration
        
    Returns:
        DataStream instance
    """
    global _data_stream
    
    if _data_stream is None:
        _data_stream = DataStream(config)
    
    return _data_stream


logger.info("✅ Data Stream module loaded")
