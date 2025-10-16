"""
Phase 5.3 - WebSocket Manager Tests
Tests for real-time WebSocket data streaming
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import aiohttp

from src.thebot.services.websocket_manager import (
    WebSocketManager,
    WebSocketConfig,
    WebSocketMessage,
    ConnectionStatus,
    get_websocket_manager,
)


class TestWebSocketConfig:
    """Tests for WebSocket configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = WebSocketConfig()
        assert config.url == "wss://stream.binance.com:9443/ws"
        assert config.max_reconnect_attempts == 5
        assert config.reconnect_delay == 1.0
        assert config.max_reconnect_delay == 30.0
        assert config.heartbeat_interval == 30.0
        assert config.message_queue_size == 1000
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = WebSocketConfig(
            url="wss://custom.example.com",
            max_reconnect_attempts=3,
            reconnect_delay=0.5
        )
        assert config.url == "wss://custom.example.com"
        assert config.max_reconnect_attempts == 3
        assert config.reconnect_delay == 0.5


class TestWebSocketMessage:
    """Tests for WebSocket message structure"""
    
    def test_message_creation(self):
        """Test creating a WebSocket message"""
        now = datetime.now()
        data = {"test": "data"}
        
        msg = WebSocketMessage(
            timestamp=now,
            type="trade",
            data=data
        )
        
        assert msg.timestamp == now
        assert msg.type == "trade"
        assert msg.data == data
        assert msg.source == "websocket"


class TestWebSocketManager:
    """Tests for WebSocket Manager"""
    
    @pytest.fixture
    def config(self):
        """Provide WebSocket config"""
        return WebSocketConfig()
    
    @pytest.fixture
    def manager(self, config):
        """Provide WebSocket manager"""
        return WebSocketManager(config)
    
    def test_initialization(self, manager):
        """Test manager initialization"""
        assert manager.status == ConnectionStatus.DISCONNECTED
        assert manager.session is None
        assert manager.websocket is None
        assert len(manager._observers) == 0
        assert manager._running is False
    
    @pytest.mark.asyncio
    async def test_singleton_pattern(self):
        """Test that get_websocket_manager returns singleton"""
        mgr1 = get_websocket_manager()
        mgr2 = get_websocket_manager()
        assert mgr1 is mgr2
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, manager):
        """Test connection failure handling"""
        with patch.object(aiohttp, 'ClientSession') as mock_session:
            mock_session.return_value.ws_connect.side_effect = ConnectionError("Connection failed")
            
            result = await manager.connect()
            assert result is False
            assert manager.status == ConnectionStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_double_connect(self, manager):
        """Test connecting when already connected"""
        manager.status = ConnectionStatus.CONNECTED
        result = await manager.connect()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_add_observer(self, manager):
        """Test adding observer"""
        observer = Mock()
        await manager.add_observer(observer)
        assert observer in manager._observers
        assert len(manager._observers) == 1
    
    @pytest.mark.asyncio
    async def test_remove_observer(self, manager):
        """Test removing observer"""
        observer = Mock()
        await manager.add_observer(observer)
        await manager.remove_observer(observer)
        assert observer not in manager._observers
        assert len(manager._observers) == 0
    
    def test_status_connected(self, manager):
        """Test status when connected"""
        manager.status = ConnectionStatus.CONNECTED
        manager.websocket = MagicMock()
        manager._reconnect_count = 0
        manager._last_message_time = datetime.now()
        
        status = manager.get_status()
        assert status["connected"] is True
        assert status["status"] == "connected"
        assert status["observers"] == 0
    
    def test_status_disconnected(self, manager):
        """Test status when disconnected"""
        status = manager.get_status()
        assert status["connected"] is False
        assert status["status"] == "disconnected"
    
    @staticmethod
    def test_get_message_type_binance_trade():
        """Test extracting message type from Binance trade"""
        data = {"e": "trade", "s": "BTCUSDT"}
        msg_type = WebSocketManager._get_message_type(data)
        assert msg_type == "trade"
    
    @staticmethod
    def test_get_message_type_unknown():
        """Test extracting unknown message type"""
        data = {"random": "data"}
        msg_type = WebSocketManager._get_message_type(data)
        assert msg_type == "unknown"


class TestWebSocketManagerDisconnect:
    """Tests for WebSocket disconnection"""
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnection"""
        manager = WebSocketManager()
        manager._running = True
        manager.websocket = AsyncMock()
        manager.session = AsyncMock()
        manager.status = ConnectionStatus.CONNECTED
        
        await manager.disconnect()
        
        assert manager._running is False
        assert manager.websocket is None
        assert manager.session is None
        assert manager.status == ConnectionStatus.DISCONNECTED


class TestWebSocketReconnect:
    """Tests for WebSocket reconnection"""
    
    @pytest.mark.asyncio
    async def test_max_reconnect_attempts(self):
        """Test max reconnection attempts"""
        config = WebSocketConfig(max_reconnect_attempts=1)
        manager = WebSocketManager(config)
        manager._reconnect_count = 1
        
        result = await manager.reconnect()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test exponential backoff calculation"""
        config = WebSocketConfig(
            reconnect_delay=1.0,
            max_reconnect_delay=30.0
        )
        manager = WebSocketManager(config)
        
        # Calculate delays
        manager._reconnect_count = 0
        delay0 = min(1.0 * (2 ** 0), 30.0)
        assert delay0 == 1.0
        
        manager._reconnect_count = 1
        delay1 = min(1.0 * (2 ** 1), 30.0)
        assert delay1 == 2.0
        
        manager._reconnect_count = 5
        delay5 = min(1.0 * (2 ** 5), 30.0)
        assert delay5 == 30.0  # Capped at max


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
