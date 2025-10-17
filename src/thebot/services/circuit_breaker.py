"""
Circuit breaker service for error handling and fault tolerance.

Implements circuit breaker pattern to prevent cascading failures:
- CLOSED state: Normal operation, failures tracked
- OPEN state: Reject requests, fast-fail to prevent system overload
- HALF_OPEN state: Allow limited test requests to detect recovery
- Configurable thresholds for failure rates and timeouts
- Per-service breaker tracking
- Health monitoring

Architecture:
- CircuitBreakerConfig: Configuration with thresholds
- CircuitBreakerState: State management (CLOSED/OPEN/HALF_OPEN)
- CircuitBreaker: Individual breaker for a service
- CircuitBreakerManager: Singleton manager for all breakers
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class BreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5  # Number of failures before opening
    failure_rate_threshold: float = 0.5  # 50% failure rate threshold
    success_threshold: int = 2  # Successes in HALF_OPEN before closing
    timeout_sec: int = 60  # Time before attempting recovery
    max_half_open_calls: int = 3  # Max calls allowed in HALF_OPEN

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if not 0 < self.failure_rate_threshold < 1:
            raise ValueError("failure_rate_threshold must be between 0 and 1")
        if self.success_threshold < 1:
            raise ValueError("success_threshold must be >= 1")
        if self.timeout_sec < 1:
            raise ValueError("timeout_sec must be >= 1")
        if self.max_half_open_calls < 1:
            raise ValueError("max_half_open_calls must be >= 1")


class CircuitBreaker:
    """Individual circuit breaker for a service."""

    def __init__(
        self,
        service_name: str,
        config: CircuitBreakerConfig,
    ) -> None:
        """Initialize circuit breaker.

        Args:
            service_name: Name of service being protected
            config: Circuit breaker configuration
        """
        self.service_name = service_name
        self.config = config
        self.state = BreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float = 0
        self.last_state_change_time: float = 0
        self.half_open_calls = 0
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function through circuit breaker.

        Args:
            func: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            RuntimeError: If circuit is OPEN
        """
        self.total_calls += 1

        # Check if should transition states
        self._check_state_transition()

        if self.state == BreakerState.OPEN:
            raise RuntimeError(
                f"Circuit breaker {self.service_name} is OPEN. Service unavailable."
            )

        if self.state == BreakerState.HALF_OPEN:
            if self.half_open_calls >= self.config.max_half_open_calls:
                raise RuntimeError(
                    f"Circuit breaker {self.service_name} HALF_OPEN: max test calls exceeded"
                )
            self.half_open_calls += 1

        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Handle successful call."""
        self.failure_count = 0
        self.total_successes += 1

        if self.state == BreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._transition_to_closed()

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.total_failures += 1
        self.last_failure_time = time.time()

        # Check if should open circuit
        if self.state == BreakerState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self._transition_to_open()

        elif self.state == BreakerState.HALF_OPEN:
            # Any failure in HALF_OPEN reopens circuit
            self._transition_to_open()

    def _check_state_transition(self) -> None:
        """Check if should transition state."""
        if self.state == BreakerState.OPEN:
            # Check if timeout expired
            elapsed = time.time() - self.last_state_change_time
            if elapsed >= self.config.timeout_sec:
                self._transition_to_half_open()

    def _transition_to_open(self) -> None:
        """Transition circuit to OPEN state."""
        if self.state != BreakerState.OPEN:
            self.state = BreakerState.OPEN
            self.last_state_change_time = time.time()
            logger.warning(
                f"Circuit breaker {self.service_name} transitioned to OPEN "
                f"(failures: {self.failure_count})"
            )

    def _transition_to_half_open(self) -> None:
        """Transition circuit to HALF_OPEN state."""
        if self.state != BreakerState.HALF_OPEN:
            self.state = BreakerState.HALF_OPEN
            self.half_open_calls = 0
            self.success_count = 0
            self.last_state_change_time = time.time()
            logger.info(f"Circuit breaker {self.service_name} transitioned to HALF_OPEN")

    def _transition_to_closed(self) -> None:
        """Transition circuit to CLOSED state."""
        if self.state != BreakerState.CLOSED:
            self.state = BreakerState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_state_change_time = time.time()
            logger.info(f"Circuit breaker {self.service_name} transitioned to CLOSED")

    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        failure_rate = (
            self.total_failures / self.total_calls * 100 if self.total_calls > 0 else 0
        )

        return {
            "service_name": self.service_name,
            "state": self.state.value,
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "failure_rate_percent": failure_rate,
            "failure_count": self.failure_count,
            "last_failure": (
                datetime.fromtimestamp(self.last_failure_time).isoformat()
                if self.last_failure_time > 0
                else None
            ),
        }


class CircuitBreakerManager:
    """Singleton manager for circuit breakers."""

    _instance: Optional["CircuitBreakerManager"] = None
    _breakers: Dict[str, CircuitBreaker] = {}
    _default_config = CircuitBreakerConfig()

    def __new__(cls) -> "CircuitBreakerManager":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(
        self,
        service_name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ) -> CircuitBreaker:
        """Register a service with circuit breaker.

        Args:
            service_name: Name of service
            config: Circuit breaker configuration (uses default if None)

        Returns:
            CircuitBreaker instance
        """
        if service_name in self._breakers:
            logger.warning(f"Service {service_name} already registered, replacing")

        cfg = config or self._default_config
        breaker = CircuitBreaker(service_name, cfg)
        self._breakers[service_name] = breaker

        logger.info(
            f"Registered circuit breaker for {service_name}: "
            f"failures={cfg.failure_threshold}, timeout={cfg.timeout_sec}s"
        )

        return breaker

    def get_breaker(self, service_name: str) -> Optional[CircuitBreaker]:
        """Get breaker for service."""
        return self._breakers.get(service_name)

    async def call(
        self,
        service_name: str,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute function through registered breaker.

        Args:
            service_name: Name of service
            func: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            RuntimeError: If breaker is OPEN or service not registered
        """
        breaker = self.get_breaker(service_name)
        if breaker is None:
            # Auto-register if not found
            breaker = self.register(service_name)

        return await breaker.call(func, *args, **kwargs)

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all breakers."""
        return {
            service_name: breaker.get_status()
            for service_name, breaker in self._breakers.items()
        }

    def reset_breaker(self, service_name: str) -> bool:
        """Reset breaker to CLOSED state.

        Args:
            service_name: Name of service

        Returns:
            True if reset, False if not found
        """
        breaker = self.get_breaker(service_name)
        if breaker is None:
            return False

        breaker.state = BreakerState.CLOSED
        breaker.failure_count = 0
        breaker.success_count = 0
        logger.info(f"Reset circuit breaker for {service_name}")
        return True

    def reset_all(self) -> None:
        """Reset all breakers."""
        for breaker in self._breakers.values():
            breaker.state = BreakerState.CLOSED
            breaker.failure_count = 0
            breaker.success_count = 0
        logger.info("Reset all circuit breakers")


def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """Factory function for singleton access."""
    return CircuitBreakerManager()
