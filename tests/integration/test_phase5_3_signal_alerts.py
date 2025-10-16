"""
Unit tests for Signal Notification and Alert Management Service

Tests cover:
- SignalConfig validation
- SignalAlert data structure
- AlertManager initialization
- Alert creation and lifecycle
- Observer pattern (sync and async)
- Alert history and filtering
- Status reporting
- Error handling
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from src.thebot.services.signal_notification import (
    SignalConfig,
    SignalAlert,
    AlertManager,
    AlertType,
    AlertStatus,
    get_alert_manager,
)


# ============================================================================
# Tests: SignalConfig
# ============================================================================

class TestSignalConfig:
    """Test SignalConfig dataclass and validation"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = SignalConfig()
        assert config.enable_toast is True
        assert config.enable_audio is True
        assert config.enable_browser is False
        assert config.history_size == 100
        assert config.toast_duration == 5000
        assert config.notification_timeout == 30
        assert config.audio_path == "/assets/alert.mp3"
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = SignalConfig(
            enable_toast=False,
            enable_audio=False,
            history_size=50,
            toast_duration=3000,
            notification_timeout=60,
        )
        assert config.enable_toast is False
        assert config.enable_audio is False
        assert config.history_size == 50
        assert config.toast_duration == 3000
        assert config.notification_timeout == 60
    
    def test_invalid_history_size(self):
        """Test validation of history_size"""
        with pytest.raises(ValueError, match="history_size must be positive"):
            SignalConfig(history_size=0)
        
        with pytest.raises(ValueError, match="history_size must be positive"):
            SignalConfig(history_size=-1)
    
    def test_invalid_toast_duration(self):
        """Test validation of toast_duration"""
        with pytest.raises(ValueError, match="toast_duration must be positive"):
            SignalConfig(toast_duration=0)
    
    def test_invalid_notification_timeout(self):
        """Test validation of notification_timeout"""
        with pytest.raises(ValueError, match="notification_timeout must be positive"):
            SignalConfig(notification_timeout=0)


# ============================================================================
# Tests: SignalAlert
# ============================================================================

class TestSignalAlert:
    """Test SignalAlert data structure"""
    
    def test_alert_creation(self):
        """Test basic alert creation"""
        alert = SignalAlert(
            id="BTC_BUY_123",
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000.50"),
            indicator="RSI",
            timeframe="1h",
            strength=0.75,
            message="RSI bullish signal",
            timestamp=datetime.now(),
        )
        assert alert.id == "BTC_BUY_123"
        assert alert.signal_type == AlertType.BUY
        assert alert.symbol == "BTCUSDT"
        assert alert.price == Decimal("45000.50")
        assert alert.status == AlertStatus.ACTIVE
    
    def test_alert_to_dict(self):
        """Test alert serialization to dict"""
        now = datetime.now()
        alert = SignalAlert(
            id="BTC_BUY_123",
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000.50"),
            indicator="RSI",
            timeframe="1h",
            strength=0.75,
            message="Test alert",
            timestamp=now,
        )
        
        alert_dict = alert.to_dict()
        assert alert_dict["id"] == "BTC_BUY_123"
        assert alert_dict["signal_type"] == AlertType.BUY
        assert alert_dict["price"] == "45000.50"
        assert alert_dict["status"] == AlertStatus.ACTIVE
        assert alert_dict["dismissed_at"] is None
    
    def test_alert_is_expired(self):
        """Test alert expiration checking"""
        now = datetime.now()
        old_time = now - timedelta(seconds=35)
        
        alert = SignalAlert(
            id="TEST",
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000"),
            indicator="RSI",
            timeframe="1h",
            strength=0.5,
            message="Test",
            timestamp=old_time,
        )
        
        # Alert should be expired (timeout=30s, alert is 35s old)
        assert alert.is_expired(30) is True
        
        # Alert should not be expired with higher timeout
        assert alert.is_expired(40) is False


# ============================================================================
# Tests: AlertManager
# ============================================================================

class TestAlertManagerInit:
    """Test AlertManager initialization"""
    
    def test_default_initialization(self):
        """Test AlertManager with default config"""
        manager = AlertManager()
        assert manager.config.enable_toast is True
        assert manager.config.history_size == 100
        assert len(manager.alerts) == 0
        assert len(manager.history) == 0
    
    def test_custom_config_initialization(self):
        """Test AlertManager with custom config"""
        config = SignalConfig(
            enable_toast=False,
            history_size=50,
        )
        manager = AlertManager(config)
        assert manager.config.enable_toast is False
        assert manager.config.history_size == 50
    
    def test_singleton_pattern(self):
        """Test singleton pattern for AlertManager"""
        # Reset singleton
        import src.thebot.services.signal_notification as module
        module._alert_manager = None
        
        manager1 = get_alert_manager()
        manager2 = get_alert_manager()
        assert manager1 is manager2


@pytest.mark.asyncio
class TestAlertManagerCreation:
    """Test alert creation"""
    
    async def test_create_alert_buy(self):
        """Test creating a BUY alert"""
        manager = AlertManager()
        alert = await manager.create_alert(
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000.50"),
            indicator="RSI",
            timeframe="1h",
            strength=0.85,
        )
        
        assert alert.signal_type == AlertType.BUY
        assert alert.symbol == "BTCUSDT"
        assert alert.price == Decimal("45000.50")
        assert alert.status == AlertStatus.ACTIVE
        assert len(manager.alerts) == 1
        assert len(manager.history) == 1
    
    async def test_create_alert_sell(self):
        """Test creating a SELL alert"""
        manager = AlertManager()
        alert = await manager.create_alert(
            signal_type=AlertType.SELL,
            symbol="ETHUSDT",
            price=Decimal("2500.00"),
            indicator="MACD",
            timeframe="4h",
            strength=0.65,
            message="MACD bearish crossover",
        )
        
        assert alert.signal_type == AlertType.SELL
        assert alert.message == "MACD bearish crossover"
    
    async def test_create_alert_invalid_type(self):
        """Test creating alert with invalid signal_type"""
        manager = AlertManager()
        with pytest.raises(ValueError, match="Invalid signal_type"):
            await manager.create_alert(
                signal_type="INVALID",
                symbol="BTCUSDT",
                price=Decimal("45000"),
                indicator="RSI",
                timeframe="1h",
            )
    
    async def test_create_alert_invalid_strength(self):
        """Test creating alert with invalid strength"""
        manager = AlertManager()
        with pytest.raises(ValueError, match="strength must be 0.0-1.0"):
            await manager.create_alert(
                signal_type=AlertType.BUY,
                symbol="BTCUSDT",
                price=Decimal("45000"),
                indicator="RSI",
                timeframe="1h",
                strength=1.5,
            )
    
    async def test_create_multiple_alerts(self):
        """Test creating multiple alerts"""
        manager = AlertManager()
        
        alert1 = await manager.create_alert(
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000"),
            indicator="RSI",
            timeframe="1h",
        )
        
        alert2 = await manager.create_alert(
            signal_type=AlertType.SELL,
            symbol="ETHUSDT",
            price=Decimal("2500"),
            indicator="MACD",
            timeframe="1h",
        )
        
        assert len(manager.alerts) == 2
        assert alert1.id != alert2.id


@pytest.mark.asyncio
class TestAlertManagerDismissal:
    """Test alert dismissal"""
    
    async def test_dismiss_alert(self):
        """Test dismissing an active alert"""
        manager = AlertManager()
        alert = await manager.create_alert(
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000"),
            indicator="RSI",
            timeframe="1h",
        )
        
        dismissed = await manager.dismiss_alert(alert.id)
        assert dismissed is not None
        assert dismissed.status == AlertStatus.DISMISSED
        assert dismissed.dismissed_at is not None
    
    async def test_dismiss_nonexistent_alert(self):
        """Test dismissing alert that doesn't exist"""
        manager = AlertManager()
        result = await manager.dismiss_alert("NONEXISTENT")
        assert result is None


@pytest.mark.asyncio
class TestAlertManagerHistory:
    """Test alert history and retrieval"""
    
    async def test_get_alert(self):
        """Test retrieving alert by ID"""
        manager = AlertManager()
        alert = await manager.create_alert(
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000"),
            indicator="RSI",
            timeframe="1h",
        )
        
        retrieved = manager.get_alert(alert.id)
        assert retrieved is not None
        assert retrieved.id == alert.id
    
    async def test_get_active_alerts(self):
        """Test retrieving all active alerts"""
        manager = AlertManager()
        
        alert1 = await manager.create_alert(
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000"),
            indicator="RSI",
            timeframe="1h",
        )
        
        alert2 = await manager.create_alert(
            signal_type=AlertType.SELL,
            symbol="ETHUSDT",
            price=Decimal("2500"),
            indicator="MACD",
            timeframe="1h",
        )
        
        await manager.dismiss_alert(alert1.id)
        
        active = manager.get_active_alerts()
        assert len(active) == 1
        assert active[0].id == alert2.id
    
    async def test_get_alert_history(self):
        """Test retrieving alert history"""
        manager = AlertManager()
        
        for i in range(5):
            await manager.create_alert(
                signal_type=AlertType.BUY if i % 2 == 0 else AlertType.SELL,
                symbol="BTCUSDT",
                price=Decimal("45000"),
                indicator="RSI",
                timeframe="1h",
            )
        
        history = manager.get_alert_history()
        assert len(history) == 5
    
    async def test_get_alert_history_with_limit(self):
        """Test retrieving alert history with limit"""
        manager = AlertManager()
        
        for i in range(10):
            await manager.create_alert(
                signal_type=AlertType.BUY,
                symbol="BTCUSDT",
                price=Decimal("45000"),
                indicator="RSI",
                timeframe="1h",
            )
        
        history = manager.get_alert_history(limit=5)
        assert len(history) == 5
    
    async def test_get_recent_signals_all(self):
        """Test retrieving recent signals without filter"""
        manager = AlertManager()
        
        for i in range(3):
            await manager.create_alert(
                signal_type=AlertType.BUY,
                symbol="BTCUSDT",
                price=Decimal("45000"),
                indicator="RSI",
                timeframe="1h",
            )
        
        signals = manager.get_recent_signals()
        assert len(signals) == 3
    
    async def test_get_recent_signals_by_symbol(self):
        """Test retrieving recent signals filtered by symbol"""
        manager = AlertManager()
        
        await manager.create_alert(
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000"),
            indicator="RSI",
            timeframe="1h",
        )
        
        await manager.create_alert(
            signal_type=AlertType.BUY,
            symbol="ETHUSDT",
            price=Decimal("2500"),
            indicator="RSI",
            timeframe="1h",
        )
        
        signals = manager.get_recent_signals(symbol="BTCUSDT")
        assert len(signals) == 1
        assert signals[0].symbol == "BTCUSDT"
    
    async def test_get_recent_signals_by_type(self):
        """Test retrieving recent signals filtered by type"""
        manager = AlertManager()
        
        await manager.create_alert(
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000"),
            indicator="RSI",
            timeframe="1h",
        )
        
        await manager.create_alert(
            signal_type=AlertType.SELL,
            symbol="BTCUSDT",
            price=Decimal("44000"),
            indicator="RSI",
            timeframe="1h",
        )
        
        buy_signals = manager.get_recent_signals(signal_type=AlertType.BUY)
        assert len(buy_signals) == 1
        assert buy_signals[0].signal_type == AlertType.BUY


@pytest.mark.asyncio
class TestAlertManagerObservers:
    """Test observer pattern"""
    
    async def test_add_sync_observer(self):
        """Test adding synchronous observer"""
        manager = AlertManager()
        observed_alerts = []
        
        def observer(alert: SignalAlert) -> None:
            observed_alerts.append(alert)
        
        manager.add_observer(observer)
        
        alert = await manager.create_alert(
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000"),
            indicator="RSI",
            timeframe="1h",
        )
        
        assert len(observed_alerts) == 1
        assert observed_alerts[0].id == alert.id
    
    async def test_add_async_observer(self):
        """Test adding asynchronous observer"""
        manager = AlertManager()
        observed_alerts = []
        
        async def async_observer(alert: SignalAlert) -> None:
            observed_alerts.append(alert)
            await asyncio.sleep(0.01)  # Simulate async work
        
        manager.add_async_observer(async_observer)
        
        alert = await manager.create_alert(
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000"),
            indicator="RSI",
            timeframe="1h",
        )
        
        assert len(observed_alerts) == 1
        assert observed_alerts[0].id == alert.id
    
    async def test_multiple_observers(self):
        """Test multiple observers on single alert"""
        manager = AlertManager()
        calls1 = []
        calls2 = []
        
        def observer1(alert: SignalAlert) -> None:
            calls1.append(alert)
        
        def observer2(alert: SignalAlert) -> None:
            calls2.append(alert)
        
        manager.add_observer(observer1)
        manager.add_observer(observer2)
        
        await manager.create_alert(
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000"),
            indicator="RSI",
            timeframe="1h",
        )
        
        assert len(calls1) == 1
        assert len(calls2) == 1
    
    async def test_remove_observer(self):
        """Test removing observer"""
        manager = AlertManager()
        observed_alerts = []
        
        def observer(alert: SignalAlert) -> None:
            observed_alerts.append(alert)
        
        manager.add_observer(observer)
        manager.remove_observer(observer)
        
        await manager.create_alert(
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000"),
            indicator="RSI",
            timeframe="1h",
        )
        
        assert len(observed_alerts) == 0


@pytest.mark.asyncio
class TestAlertManagerExpiration:
    """Test alert expiration"""
    
    async def test_expire_stale_alerts(self):
        """Test expiring stale alerts"""
        config = SignalConfig(notification_timeout=1)
        manager = AlertManager(config)
        
        alert = await manager.create_alert(
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000"),
            indicator="RSI",
            timeframe="1h",
        )
        
        # Manually set timestamp to past
        alert.timestamp = datetime.now() - timedelta(seconds=2)
        
        expired_count = await manager.expire_stale_alerts()
        assert expired_count == 1
        assert manager.alerts[alert.id].status == AlertStatus.EXPIRED


@pytest.mark.asyncio
class TestAlertManagerStatus:
    """Test status reporting"""
    
    async def test_get_status(self):
        """Test getting manager status"""
        manager = AlertManager()
        
        alert1 = await manager.create_alert(
            signal_type=AlertType.BUY,
            symbol="BTCUSDT",
            price=Decimal("45000"),
            indicator="RSI",
            timeframe="1h",
        )
        
        alert2 = await manager.create_alert(
            signal_type=AlertType.SELL,
            symbol="ETHUSDT",
            price=Decimal("2500"),
            indicator="MACD",
            timeframe="1h",
        )
        
        await manager.dismiss_alert(alert1.id)
        
        status = manager.get_status()
        assert status["active_count"] == 1
        assert status["dismissed_count"] == 1
        assert status["total_count"] == 2
        assert status["history_size"] == 2
        assert status["config"]["enable_toast"] is True


# ============================================================================
# Tests: History size limit
# ============================================================================

@pytest.mark.asyncio
class TestAlertHistoryLimit:
    """Test history size limiting"""
    
    async def test_history_size_limit(self):
        """Test that history respects max size"""
        config = SignalConfig(history_size=5)
        manager = AlertManager(config)
        
        # Create 10 alerts
        for i in range(10):
            await manager.create_alert(
                signal_type=AlertType.BUY,
                symbol="BTCUSDT",
                price=Decimal("45000"),
                indicator="RSI",
                timeframe="1h",
            )
        
        # History should only contain last 5
        assert len(manager.history) == 5
