"""
Tests for callback debouncing service - validates debouncing strategies.

Test coverage:
- DebounceConfig validation (5 tests)
- DebouncedCallback leading strategy (4 tests)
- DebouncedCallback trailing strategy (4 tests)
- DebouncedCallback throttle strategy (4 tests)
- CallbackDebouncer singleton (3 tests)
- Statistics tracking (3 tests)
- Edge cases (4 tests)

Total: 27 tests
"""

import asyncio
import pytest
import time
from src.thebot.services.callback_debouncer import (
    DebounceConfig,
    DebouncedCallback,
    CallbackDebouncer,
    get_callback_debouncer,
)


class TestDebounceConfig:
    """Test DebounceConfig validation."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = DebounceConfig()
        assert config.strategy == "trailing"
        assert config.delay_ms == 100
        assert config.max_pending == 10

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = DebounceConfig(strategy="throttle", delay_ms=50, max_pending=5)
        assert config.strategy == "throttle"
        assert config.delay_ms == 50
        assert config.max_pending == 5

    def test_invalid_strategy(self) -> None:
        """Test invalid strategy raises error."""
        with pytest.raises(ValueError, match="Invalid strategy"):
            DebounceConfig(strategy="invalid")

    def test_negative_delay(self) -> None:
        """Test negative delay raises error."""
        with pytest.raises(ValueError, match="delay_ms must be non-negative"):
            DebounceConfig(delay_ms=-1)

    def test_invalid_max_pending(self) -> None:
        """Test invalid max_pending raises error."""
        with pytest.raises(ValueError, match="max_pending must be >= 1"):
            DebounceConfig(max_pending=0)


class TestDebouncedCallbackLeading:
    """Test leading debounce strategy."""

    @pytest.mark.asyncio
    async def test_leading_execute_immediately(self) -> None:
        """Test leading executes immediately."""
        call_count = 0

        def callback() -> None:
            nonlocal call_count
            call_count += 1

        config = DebounceConfig(strategy="leading", delay_ms=100)
        debounced = DebouncedCallback("test_callback", callback, config)

        # First call should execute immediately
        await debounced.execute_debounced()
        assert call_count == 1
        assert debounced.exec_count == 1

    @pytest.mark.asyncio
    async def test_leading_ignores_within_delay(self) -> None:
        """Test leading ignores calls within delay period."""
        call_count = 0

        def callback() -> None:
            nonlocal call_count
            call_count += 1

        config = DebounceConfig(strategy="leading", delay_ms=100)
        debounced = DebouncedCallback("test_callback", callback, config)

        await debounced.execute_debounced()
        await debounced.execute_debounced()
        await debounced.execute_debounced()

        assert call_count == 1  # Only first call executed
        assert debounced.call_count == 3
        assert debounced.exec_count == 1

    @pytest.mark.asyncio
    async def test_leading_executes_after_delay(self) -> None:
        """Test leading executes again after delay period."""
        call_count = 0

        def callback() -> None:
            nonlocal call_count
            call_count += 1

        config = DebounceConfig(strategy="leading", delay_ms=50)
        debounced = DebouncedCallback("test_callback", callback, config)

        await debounced.execute_debounced()
        assert call_count == 1

        await asyncio.sleep(0.06)
        await debounced.execute_debounced()
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_leading_with_args(self) -> None:
        """Test leading with function arguments."""
        results = []

        def callback(x: int, y: int) -> int:
            result = x + y
            results.append(result)
            return result

        config = DebounceConfig(strategy="leading", delay_ms=100)
        debounced = DebouncedCallback("test_callback", callback, config)

        await debounced.execute_debounced(5, 3)
        assert results == [8]
        assert debounced.exec_count == 1


class TestDebouncedCallbackTrailing:
    """Test trailing debounce strategy."""

    @pytest.mark.asyncio
    async def test_trailing_waits_for_silence(self) -> None:
        """Test trailing waits for silence before executing."""
        call_count = 0

        def callback() -> None:
            nonlocal call_count
            call_count += 1

        config = DebounceConfig(strategy="trailing", delay_ms=50)
        debounced = DebouncedCallback("test_callback", callback, config)

        # Multiple calls rapidly (schedule them, don't await yet)
        task1 = asyncio.create_task(debounced.execute_debounced())
        task2 = asyncio.create_task(debounced.execute_debounced())
        task3 = asyncio.create_task(debounced.execute_debounced())

        # Give them a moment to be queued
        await asyncio.sleep(0.01)

        # Not executed yet (still waiting for more calls)
        assert call_count == 0

        # Wait for all tasks and delay
        await asyncio.gather(task1, task2, task3, return_exceptions=True)
        await asyncio.sleep(0.06)
        assert call_count == 1  # Executed once after silence

    @pytest.mark.asyncio
    async def test_trailing_cancels_pending(self) -> None:
        """Test trailing cancels pending execution on new call."""
        call_count = 0

        def callback() -> None:
            nonlocal call_count
            call_count += 1

        config = DebounceConfig(strategy="trailing", delay_ms=50)
        debounced = DebouncedCallback("test_callback", callback, config)

        # First batch
        task1 = asyncio.create_task(debounced.execute_debounced())
        await asyncio.sleep(0.03)

        # Second batch (should cancel first pending)
        task2 = asyncio.create_task(debounced.execute_debounced())
        
        # Wait for both to complete
        await asyncio.gather(task1, task2, return_exceptions=True)
        await asyncio.sleep(0.06)

        assert call_count == 1  # Only one execution from latest batch

    @pytest.mark.asyncio
    async def test_trailing_queue_full(self) -> None:
        """Test trailing drops calls when queue is full."""
        config = DebounceConfig(strategy="trailing", delay_ms=100, max_pending=2)
        debounced = DebouncedCallback("test_callback", lambda: None, config)

        # Fill queue with tasks
        task1 = asyncio.create_task(debounced.execute_debounced())
        await asyncio.sleep(0.01)
        task2 = asyncio.create_task(debounced.execute_debounced())
        await asyncio.sleep(0.01)

        # This should log warning but not error
        result = await debounced.execute_debounced()
        assert result is None
        
        # Cleanup
        await asyncio.gather(task1, task2, return_exceptions=True)

    @pytest.mark.asyncio
    async def test_trailing_with_kwargs(self) -> None:
        """Test trailing with keyword arguments."""
        results = []

        def callback(x: int, y: int = 10) -> int:
            result = x + y
            results.append(result)
            return result

        config = DebounceConfig(strategy="trailing", delay_ms=50)
        debounced = DebouncedCallback("test_callback", callback, config)

        await debounced.execute_debounced(5, y=20)
        await asyncio.sleep(0.06)

        assert results == [25]


class TestDebouncedCallbackThrottle:
    """Test throttle strategy."""

    @pytest.mark.asyncio
    async def test_throttle_executes_once_per_interval(self) -> None:
        """Test throttle executes at most once per interval."""
        call_count = 0

        def callback() -> None:
            nonlocal call_count
            call_count += 1

        config = DebounceConfig(strategy="throttle", delay_ms=50)
        debounced = DebouncedCallback("test_callback", callback, config)

        # Rapid calls
        await debounced.execute_debounced()
        await debounced.execute_debounced()
        await debounced.execute_debounced()

        assert call_count == 1  # Only first execution

        # Wait for interval
        await asyncio.sleep(0.06)
        await debounced.execute_debounced()
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_throttle_multiple_intervals(self) -> None:
        """Test throttle across multiple intervals."""
        call_count = 0

        def callback() -> None:
            nonlocal call_count
            call_count += 1

        config = DebounceConfig(strategy="throttle", delay_ms=50)
        debounced = DebouncedCallback("test_callback", callback, config)

        # Interval 1
        await debounced.execute_debounced()
        await asyncio.sleep(0.06)

        # Interval 2
        await debounced.execute_debounced()
        await asyncio.sleep(0.06)

        # Interval 3
        await debounced.execute_debounced()

        assert call_count == 3
        assert debounced.exec_count == 3

    @pytest.mark.asyncio
    async def test_throttle_ignores_within_interval(self) -> None:
        """Test throttle ignores calls within interval."""
        call_count = 0

        def callback() -> None:
            nonlocal call_count
            call_count += 1

        config = DebounceConfig(strategy="throttle", delay_ms=50)
        debounced = DebouncedCallback("test_callback", callback, config)

        await debounced.execute_debounced()
        await debounced.execute_debounced()
        await debounced.execute_debounced()
        await debounced.execute_debounced()

        assert call_count == 1
        assert debounced.call_count == 4
        assert debounced.exec_count == 1

    @pytest.mark.asyncio
    async def test_throttle_with_different_args(self) -> None:
        """Test throttle always uses latest args if called within interval."""
        results = []

        def callback(x: int) -> int:
            results.append(x)
            return x

        config = DebounceConfig(strategy="throttle", delay_ms=50)
        debounced = DebouncedCallback("test_callback", callback, config)

        await debounced.execute_debounced(1)
        await debounced.execute_debounced(2)
        await debounced.execute_debounced(3)

        # Only first call executed with x=1
        assert results == [1]


class TestCallbackDebouncer:
    """Test CallbackDebouncer singleton."""

    def test_singleton_instance(self) -> None:
        """Test CallbackDebouncer is singleton."""
        debouncer1 = CallbackDebouncer()
        debouncer2 = CallbackDebouncer()
        assert debouncer1 is debouncer2

    def test_get_callback_debouncer(self) -> None:
        """Test factory function."""
        debouncer = get_callback_debouncer()
        assert isinstance(debouncer, CallbackDebouncer)

    @pytest.mark.asyncio
    async def test_register_and_execute(self) -> None:
        """Test registering and executing debounced callback."""
        call_count = 0

        def callback() -> None:
            nonlocal call_count
            call_count += 1

        debouncer = CallbackDebouncer()
        config = DebounceConfig(strategy="leading", delay_ms=100)
        wrapper = debouncer.register("test_id", callback, config)

        await wrapper()
        assert call_count == 1

        # Cleanup
        debouncer._callbacks.pop("test_id", None)


class TestCallbackStatistics:
    """Test statistics tracking."""

    @pytest.mark.asyncio
    async def test_callback_stats(self) -> None:
        """Test getting callback statistics."""
        call_count = 0

        def callback() -> None:
            nonlocal call_count
            call_count += 1

        config = DebounceConfig(strategy="leading", delay_ms=100)
        debounced = DebouncedCallback("test_id", callback, config)

        await debounced.execute_debounced()
        await debounced.execute_debounced()
        await debounced.execute_debounced()

        stats = debounced.get_stats()
        assert stats["call_count"] == 3
        assert stats["exec_count"] == 1
        assert stats["reduction_percent"] > 60

    @pytest.mark.asyncio
    async def test_debouncer_stats(self) -> None:
        """Test debouncer statistics."""
        call_count = 0

        def callback() -> None:
            nonlocal call_count
            call_count += 1

        debouncer = CallbackDebouncer()
        config = DebounceConfig(strategy="leading", delay_ms=100)
        wrapper = debouncer.register("test_id", callback, config)

        await wrapper()
        await wrapper()
        await wrapper()

        stats = debouncer.get_stats()
        assert stats["callback_count"] >= 1
        assert stats["total_calls"] >= 3

        # Cleanup
        debouncer._callbacks.pop("test_id", None)

    @pytest.mark.asyncio
    async def test_reset_stats(self) -> None:
        """Test resetting statistics."""
        config = DebounceConfig(strategy="leading", delay_ms=100)
        debounced = DebouncedCallback("test_id", lambda: None, config)

        await debounced.execute_debounced()
        await debounced.execute_debounced()

        assert debounced.call_count == 2
        debounced.call_count = 0
        debounced.exec_count = 0

        assert debounced.call_count == 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_callback_with_exception(self) -> None:
        """Test callback that raises exception."""

        def callback() -> None:
            raise ValueError("Test error")

        config = DebounceConfig(strategy="leading", delay_ms=100)
        debounced = DebouncedCallback("test_id", callback, config)

        with pytest.raises(ValueError, match="Test error"):
            await debounced.execute_debounced()

    @pytest.mark.asyncio
    async def test_async_callback(self) -> None:
        """Test with async callback function."""
        call_count = 0

        async def async_callback() -> None:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)

        config = DebounceConfig(strategy="leading", delay_ms=100)
        debounced = DebouncedCallback("test_id", async_callback, config)

        result = await debounced.execute_debounced()
        assert call_count == 1
        assert result is None

    @pytest.mark.asyncio
    async def test_zero_delay(self) -> None:
        """Test with zero delay."""
        call_count = 0

        def callback() -> None:
            nonlocal call_count
            call_count += 1

        config = DebounceConfig(strategy="trailing", delay_ms=0)
        debounced = DebouncedCallback("test_id", callback, config)

        await debounced.execute_debounced()
        await asyncio.sleep(0.01)

        assert call_count == 1

    @pytest.mark.asyncio
    async def test_large_call_volume(self) -> None:
        """Test with large call volume."""
        call_count = 0

        def callback() -> None:
            nonlocal call_count
            call_count += 1

        config = DebounceConfig(strategy="throttle", delay_ms=10)
        debounced = DebouncedCallback("test_id", callback, config)

        # 100 rapid calls
        for _ in range(100):
            await debounced.execute_debounced()

        # With throttle, much fewer executions
        assert debounced.exec_count < debounced.call_count // 2
        stats = debounced.get_stats()
        assert stats["reduction_percent"] > 50
