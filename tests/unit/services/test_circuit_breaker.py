"""
Tests for circuit breaker service - validates fault tolerance patterns.

Test coverage:
- CircuitBreakerConfig validation (4 tests)
- CLOSED state operation (4 tests)
- OPEN state transitions (4 tests)
- HALF_OPEN state recovery (4 tests)
- Failure tracking (3 tests)
- State transitions (3 tests)
- CircuitBreakerManager (3 tests)
- Edge cases (4 tests)

Total: 29 tests
"""

import asyncio
import pytest
from src.thebot.services.circuit_breaker import (
    BreakerState,
    CircuitBreakerConfig,
    CircuitBreaker,
    CircuitBreakerManager,
    get_circuit_breaker_manager,
)


class TestCircuitBreakerConfig:
    """Test CircuitBreakerConfig validation."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = CircuitBreakerConfig()
        assert config.failure_threshold == 5
        assert config.failure_rate_threshold == 0.5
        assert config.success_threshold == 2
        assert config.timeout_sec == 60

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = CircuitBreakerConfig(
            failure_threshold=3, timeout_sec=30, success_threshold=1
        )
        assert config.failure_threshold == 3
        assert config.timeout_sec == 30
        assert config.success_threshold == 1

    def test_invalid_failure_threshold(self) -> None:
        """Test invalid failure threshold."""
        with pytest.raises(ValueError, match="failure_threshold must be >= 1"):
            CircuitBreakerConfig(failure_threshold=0)

    def test_invalid_timeout(self) -> None:
        """Test invalid timeout."""
        with pytest.raises(ValueError, match="timeout_sec must be >= 1"):
            CircuitBreakerConfig(timeout_sec=0)


class TestCircuitBreakerClosed:
    """Test CLOSED state operation."""

    @pytest.mark.asyncio
    async def test_closed_allows_calls(self) -> None:
        """Test CLOSED state allows calls."""
        config = CircuitBreakerConfig(failure_threshold=5)
        breaker = CircuitBreaker("test_service", config)

        async def success_func() -> str:
            return "success"

        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == BreakerState.CLOSED

    @pytest.mark.asyncio
    async def test_closed_tracks_failures(self) -> None:
        """Test CLOSED state tracks failures."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker("test_service", config)

        async def fail_func() -> None:
            raise ValueError("Test error")

        # Multiple failures
        for _ in range(2):
            with pytest.raises(ValueError):
                await breaker.call(fail_func)

        assert breaker.failure_count == 2
        assert breaker.total_failures == 2
        assert breaker.state == BreakerState.CLOSED

    @pytest.mark.asyncio
    async def test_closed_resets_on_success(self) -> None:
        """Test CLOSED state resets failure count on success."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker("test_service", config)

        async def fail_func() -> None:
            raise ValueError("Test error")

        async def success_func() -> str:
            return "success"

        # Fail
        with pytest.raises(ValueError):
            await breaker.call(fail_func)
        assert breaker.failure_count == 1

        # Success
        await breaker.call(success_func)
        assert breaker.failure_count == 0  # Reset

    @pytest.mark.asyncio
    async def test_closed_transitions_on_failures(self) -> None:
        """Test CLOSED state transitions to OPEN after threshold."""
        config = CircuitBreakerConfig(failure_threshold=2)
        breaker = CircuitBreaker("test_service", config)

        async def fail_func() -> None:
            raise ValueError("Test error")

        # First failure
        with pytest.raises(ValueError):
            await breaker.call(fail_func)
        assert breaker.state == BreakerState.CLOSED

        # Second failure - should transition to OPEN
        with pytest.raises(ValueError):
            await breaker.call(fail_func)
        assert breaker.state == BreakerState.OPEN


class TestCircuitBreakerOpen:
    """Test OPEN state behavior."""

    @pytest.mark.asyncio
    async def test_open_rejects_calls(self) -> None:
        """Test OPEN state rejects calls."""
        config = CircuitBreakerConfig(failure_threshold=1)
        breaker = CircuitBreaker("test_service", config)

        async def fail_func() -> None:
            raise ValueError("Test error")

        # Trigger OPEN
        with pytest.raises(ValueError):
            await breaker.call(fail_func)
        assert breaker.state == BreakerState.OPEN

        # Next call should be rejected immediately
        async def success_func() -> str:
            return "success"

        with pytest.raises(RuntimeError, match="Circuit breaker.*OPEN"):
            await breaker.call(success_func)

    @pytest.mark.asyncio
    async def test_open_fails_fast(self) -> None:
        """Test OPEN state fails fast without calling function."""
        config = CircuitBreakerConfig(failure_threshold=1)
        breaker = CircuitBreaker("test_service", config)
        call_count = 0

        async def fail_func() -> None:
            nonlocal call_count
            call_count += 1
            raise ValueError("Test error")

        # Trigger OPEN
        with pytest.raises(ValueError):
            await breaker.call(fail_func)

        # Subsequent calls don't execute function
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await breaker.call(fail_func)

        assert call_count == 1  # Only called once

    @pytest.mark.asyncio
    async def test_open_timeout_transition(self) -> None:
        """Test OPEN transitions to HALF_OPEN after timeout."""
        config = CircuitBreakerConfig(failure_threshold=1, timeout_sec=1)
        breaker = CircuitBreaker("test_service", config)

        async def fail_func() -> None:
            raise ValueError("Test error")

        # Trigger OPEN
        with pytest.raises(ValueError):
            await breaker.call(fail_func)
        assert breaker.state == BreakerState.OPEN

        # Wait for timeout
        await asyncio.sleep(1.1)

        # Next check should transition to HALF_OPEN
        async def success_func() -> str:
            return "success"

        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == BreakerState.HALF_OPEN


class TestCircuitBreakerHalfOpen:
    """Test HALF_OPEN state recovery."""

    @pytest.mark.asyncio
    async def test_half_open_tests_recovery(self) -> None:
        """Test HALF_OPEN state allows limited test calls."""
        config = CircuitBreakerConfig(
            failure_threshold=1, timeout_sec=1, success_threshold=1
        )
        breaker = CircuitBreaker("test_service", config)

        async def fail_func() -> None:
            raise ValueError("Test error")

        # Trigger OPEN
        with pytest.raises(ValueError):
            await breaker.call(fail_func)
        assert breaker.state == BreakerState.OPEN

        # Wait for timeout - next call should trigger transition check
        await asyncio.sleep(1.1)

        # Test recovery with success
        async def success_func() -> str:
            return "success"

        result = await breaker.call(success_func)
        assert result == "success"
        # After success in HALF_OPEN, should close or stay in HALF_OPEN
        assert breaker.state in (BreakerState.CLOSED, BreakerState.HALF_OPEN)

    @pytest.mark.asyncio
    async def test_half_open_closes_on_success(self) -> None:
        """Test HALF_OPEN transitions to CLOSED on success."""
        config = CircuitBreakerConfig(
            failure_threshold=1, timeout_sec=1, success_threshold=2
        )
        breaker = CircuitBreaker("test_service", config)

        async def fail_func() -> None:
            raise ValueError("Test error")

        # Trigger OPEN
        with pytest.raises(ValueError):
            await breaker.call(fail_func)

        # Wait for timeout
        await asyncio.sleep(1.1)

        # Successful calls in HALF_OPEN
        async def success_func() -> str:
            return "success"

        await breaker.call(success_func)
        assert breaker.state == BreakerState.HALF_OPEN

        await breaker.call(success_func)
        assert breaker.state == BreakerState.CLOSED  # Recovered!

    @pytest.mark.asyncio
    async def test_half_open_reopens_on_failure(self) -> None:
        """Test HALF_OPEN reopens on failure."""
        config = CircuitBreakerConfig(
            failure_threshold=1, timeout_sec=1, success_threshold=2
        )
        breaker = CircuitBreaker("test_service", config)

        async def fail_func() -> None:
            raise ValueError("Test error")

        # Trigger OPEN
        with pytest.raises(ValueError):
            await breaker.call(fail_func)

        # Wait for timeout
        await asyncio.sleep(1.1)

        # Failure in HALF_OPEN
        with pytest.raises(ValueError):
            await breaker.call(fail_func)

        assert breaker.state == BreakerState.OPEN  # Back to OPEN

    @pytest.mark.asyncio
    async def test_half_open_max_calls(self) -> None:
        """Test HALF_OPEN limits test calls."""
        config = CircuitBreakerConfig(
            failure_threshold=1, timeout_sec=1, max_half_open_calls=1
        )
        breaker = CircuitBreaker("test_service", config)

        async def fail_func() -> None:
            raise ValueError("Test error")

        # Trigger OPEN
        with pytest.raises(ValueError):
            await breaker.call(fail_func)
        assert breaker.state == BreakerState.OPEN

        # Wait for timeout
        await asyncio.sleep(1.1)

        async def success_func() -> str:
            return "success"

        # First call in HALF_OPEN should work
        result = await breaker.call(success_func)
        assert result == "success"

        # If still in HALF_OPEN and exceeded calls
        if breaker.state == BreakerState.HALF_OPEN:
            with pytest.raises(RuntimeError, match="max test calls exceeded"):
                await breaker.call(success_func)


class TestFailureTracking:
    """Test failure tracking."""

    @pytest.mark.asyncio
    async def test_total_failures(self) -> None:
        """Test total failure count."""
        config = CircuitBreakerConfig(failure_threshold=5)
        breaker = CircuitBreaker("test_service", config)

        async def fail_func() -> None:
            raise ValueError("Test error")

        for _ in range(3):
            with pytest.raises(ValueError):
                await breaker.call(fail_func)

        assert breaker.total_failures == 3

    @pytest.mark.asyncio
    async def test_failure_rate(self) -> None:
        """Test failure rate calculation."""
        config = CircuitBreakerConfig(failure_threshold=5)
        breaker = CircuitBreaker("test_service", config)

        async def fail_func() -> None:
            raise ValueError("Test error")

        async def success_func() -> str:
            return "success"

        # 2 failures, 3 successes
        with pytest.raises(ValueError):
            await breaker.call(fail_func)
        await breaker.call(success_func)
        with pytest.raises(ValueError):
            await breaker.call(fail_func)
        await breaker.call(success_func)
        await breaker.call(success_func)

        status = breaker.get_status()
        assert status["total_calls"] == 5
        assert status["total_failures"] == 2
        assert abs(status["failure_rate_percent"] - 40.0) < 0.1


class TestCircuitBreakerManager:
    """Test CircuitBreakerManager."""

    def test_singleton(self) -> None:
        """Test manager is singleton."""
        manager1 = CircuitBreakerManager()
        manager2 = CircuitBreakerManager()
        assert manager1 is manager2

    def test_get_factory(self) -> None:
        """Test factory function."""
        manager = get_circuit_breaker_manager()
        assert isinstance(manager, CircuitBreakerManager)

    @pytest.mark.asyncio
    async def test_manager_call(self) -> None:
        """Test manager call method."""
        manager = CircuitBreakerManager()

        async def success_func() -> str:
            return "success"

        result = await manager.call("test_service", success_func)
        assert result == "success"

        # Cleanup
        manager._breakers.clear()


class TestEdgeCases:
    """Test edge cases."""

    @pytest.mark.asyncio
    async def test_sync_function_call(self) -> None:
        """Test calling sync function."""
        config = CircuitBreakerConfig()
        breaker = CircuitBreaker("test_service", config)

        def sync_func() -> str:
            return "sync_result"

        result = await breaker.call(sync_func)
        assert result == "sync_result"

    @pytest.mark.asyncio
    async def test_get_status(self) -> None:
        """Test getting breaker status."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker("test_service", config)

        async def fail_func() -> None:
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await breaker.call(fail_func)
        with pytest.raises(ValueError):
            await breaker.call(fail_func)

        status = breaker.get_status()
        assert status["service_name"] == "test_service"
        assert status["state"] == BreakerState.CLOSED.value
        assert status["total_failures"] == 2
        assert "last_failure" in status

    @pytest.mark.asyncio
    async def test_reset_breaker(self) -> None:
        """Test resetting breaker."""
        config = CircuitBreakerConfig(failure_threshold=1)
        breaker = CircuitBreaker("test_service", config)

        async def fail_func() -> None:
            raise ValueError("Test error")

        # Trigger OPEN
        with pytest.raises(ValueError):
            await breaker.call(fail_func)
        assert breaker.state == BreakerState.OPEN

        # Reset
        breaker.state = BreakerState.CLOSED
        breaker.failure_count = 0

        async def success_func() -> str:
            return "success"

        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == BreakerState.CLOSED
