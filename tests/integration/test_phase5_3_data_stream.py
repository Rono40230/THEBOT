"""
Phase 5.3 - Data Stream Tests
Tests for real-time market data streaming
"""

import pytest
import asyncio
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch

from src.thebot.services.data_stream import (
    DataStream,
    StreamConfig,
    SymbolData,
    get_data_stream,
)
from src.thebot.services.websocket_manager import WebSocketMessage
from src.thebot.core.types import TimeFrame


class TestStreamConfig:
    """Tests for Stream configuration"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = StreamConfig()
        assert len(config.symbols) == 1
        assert config.symbols[0] == "BTCUSDT"
        assert TimeFrame.H1 in config.timeframes
        assert "trades" in config.stream_types
        assert config.buffer_size == 500
        assert config.update_interval == 0.1
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = StreamConfig(
            symbols=["BTCUSDT", "ETHUSDT"],
            buffer_size=1000,
            update_interval=0.05
        )
        assert len(config.symbols) == 2
        assert config.buffer_size == 1000
        assert config.update_interval == 0.05


class TestSymbolData:
    """Tests for Symbol data container"""
    
    def test_initialization(self):
        """Test symbol data initialization"""
        data = SymbolData(symbol="BTCUSDT")
        assert data.symbol == "BTCUSDT"
        assert data.latest_price == Decimal("0")
        assert data.bid == Decimal("0")
        assert data.ask == Decimal("0")
        assert data.volume == Decimal("0")
        assert data.timestamp is None
        assert len(data.klines) == 0


class TestDataStream:
    """Tests for Data Stream"""
    
    @pytest.fixture
    def config(self):
        """Provide stream config"""
        return StreamConfig(symbols=["BTCUSDT"])
    
    @pytest.fixture
    def stream(self, config):
        """Provide data stream"""
        return DataStream(config)
    
    def test_initialization(self, stream):
        """Test stream initialization"""
        assert len(stream._symbol_data) == 1
        assert "BTCUSDT" in stream._symbol_data
        assert stream._running is False
        assert len(stream._observers) == 0
    
    @pytest.mark.asyncio
    async def test_singleton_pattern(self):
        """Test singleton pattern"""
        stream1 = get_data_stream()
        stream2 = get_data_stream()
        assert stream1 is stream2
    
    @pytest.mark.asyncio
    async def test_add_observer(self, stream):
        """Test adding observer"""
        observer = AsyncMock()
        await stream.add_observer(observer)
        assert observer in stream._observers
        assert len(stream._observers) == 1
    
    @pytest.mark.asyncio
    async def test_remove_observer(self, stream):
        """Test removing observer"""
        observer = AsyncMock()
        await stream.add_observer(observer)
        await stream.remove_observer(observer)
        assert observer not in stream._observers
    
    def test_get_symbol_data(self, stream):
        """Test getting symbol data"""
        data = stream.get_symbol_data("BTCUSDT")
        assert data is not None
        assert data.symbol == "BTCUSDT"
    
    def test_get_symbol_data_not_found(self, stream):
        """Test getting non-existent symbol data"""
        data = stream.get_symbol_data("NONEXISTENT")
        assert data is None
    
    def test_get_all_data(self, stream):
        """Test getting all symbol data"""
        all_data = stream.get_all_data()
        assert len(all_data) == 1
        assert "BTCUSDT" in all_data
    
    @pytest.mark.asyncio
    async def test_subscribe_symbol(self, stream):
        """Test subscribing to new symbol"""
        with patch.object(stream.websocket, 'subscribe', new_callable=AsyncMock):
            result = await stream.subscribe_symbol("ETHUSDT")
            assert result is True
            assert "ETHUSDT" in stream._symbol_data
            assert len(stream._symbol_data) == 2
    
    @pytest.mark.asyncio
    async def test_subscribe_existing_symbol(self, stream):
        """Test subscribing to existing symbol"""
        result = await stream.subscribe_symbol("BTCUSDT")
        assert result is True
        assert len(stream._symbol_data) == 1  # Still 1
    
    @pytest.mark.asyncio
    async def test_unsubscribe_symbol(self, stream):
        """Test unsubscribing from symbol"""
        with patch.object(stream.websocket, 'unsubscribe', new_callable=AsyncMock):
            result = await stream.unsubscribe_symbol("BTCUSDT")
            assert result is True
            assert "BTCUSDT" not in stream._symbol_data
    
    @pytest.mark.asyncio
    async def test_handle_trade_message(self, stream):
        """Test handling trade message"""
        data_dict = {
            "s": "BTCUSDT",
            "p": "50000.00",
            "T": int(datetime.now().timestamp() * 1000)
        }
        
        await stream._handle_trade_message(data_dict)
        
        symbol_data = stream.get_symbol_data("BTCUSDT")
        assert symbol_data.latest_price == Decimal("50000.00")
    
    @pytest.mark.asyncio
    async def test_handle_kline_message(self, stream):
        """Test handling kline message"""
        data_dict = {
            "s": "BTCUSDT",
            "k": {
                "i": "1h",
                "t": int(datetime.now().timestamp() * 1000),
                "o": "50000",
                "h": "51000",
                "l": "49000",
                "c": "50500",
                "v": "100",
                "x": True
            }
        }
        
        await stream._handle_kline_message(data_dict)
        
        symbol_data = stream.get_symbol_data("BTCUSDT")
        assert "1h" in symbol_data.klines
        assert len(symbol_data.klines["1h"]) == 1
        
        candle = symbol_data.klines["1h"][0]
        assert candle["close"] == Decimal("50500")
        assert candle["volume"] == Decimal("100")
    
    @pytest.mark.asyncio
    async def test_handle_ticker_message(self, stream):
        """Test handling ticker message"""
        data_dict = {
            "s": "BTCUSDT",
            "b": "50000.00",  # bid
            "a": "50100.00",  # ask
            "v": "1000000"    # volume
        }
        
        await stream._handle_ticker_message(data_dict)
        
        symbol_data = stream.get_symbol_data("BTCUSDT")
        assert symbol_data.bid == Decimal("50000.00")
        assert symbol_data.ask == Decimal("50100.00")
        assert symbol_data.volume == Decimal("1000000")
    
    @pytest.mark.asyncio
    async def test_observer_notification_sync(self, stream):
        """Test notifying synchronous observer"""
        observer = Mock()
        await stream.add_observer(observer)
        
        symbol_data = stream.get_symbol_data("BTCUSDT")
        await stream._notify_observers("BTCUSDT", symbol_data)
        
        observer.assert_called_once()
        assert observer.call_args[0][0] == "BTCUSDT"
    
    @pytest.mark.asyncio
    async def test_observer_notification_async(self, stream):
        """Test notifying async observer"""
        observer = AsyncMock()
        await stream.add_observer(observer)
        
        symbol_data = stream.get_symbol_data("BTCUSDT")
        await stream._notify_observers("BTCUSDT", symbol_data)
        
        observer.assert_called_once()
    
    def test_get_status(self, stream):
        """Test getting stream status"""
        stream._running = True
        status = stream.get_status()
        
        assert status["running"] is True
        assert status["symbols"] == 1
        assert status["observers"] == 0
        assert "BTCUSDT" in status["symbols_data"]
    
    @pytest.mark.asyncio
    async def test_message_buffer_overflow(self, stream):
        """Test handling message buffer overflow"""
        config = StreamConfig(symbols=["BTCUSDT"], buffer_size=2)
        stream_small = DataStream(config)
        
        # Add 3 candles (exceeds buffer)
        for i in range(3):
            data_dict = {
                "s": "BTCUSDT",
                "k": {
                    "i": "1h",
                    "t": int(datetime.now().timestamp() * 1000) + i,
                    "o": "50000",
                    "h": "51000",
                    "l": "49000",
                    "c": "50500",
                    "v": "100",
                    "x": True
                }
            }
            await stream_small._handle_kline_message(data_dict)
        
        symbol_data = stream_small.get_symbol_data("BTCUSDT")
        assert len(symbol_data.klines["1h"]) == 2  # Only 2, oldest removed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
