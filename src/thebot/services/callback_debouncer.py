"""
Debouncing service for Dash callbacks - reduces unnecessary callback executions.

Implements debouncing strategies to minimize redundant callback invocations:
- Leading debounce (execute immediately, ignore next N calls for duration)
- Trailing debounce (wait for silence, then execute once)
- Throttle (execute at most once per time interval)

Architecture:
- DebounceConfig: Configuration dataclass with validation
- DebouncedCallback: Wrapper for debounced functions
- CallbackDebouncer: Singleton manager for all debounced callbacks
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Coroutine, Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class DebounceConfig:
    """Configuration for debouncing behavior."""

    strategy: str = "trailing"  # leading, trailing, throttle
    delay_ms: int = 100  # Delay in milliseconds
    max_pending: int = 10  # Max pending calls to queue

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.strategy not in ("leading", "trailing", "throttle"):
            raise ValueError(f"Invalid strategy: {self.strategy}")
        if self.delay_ms < 0:
            raise ValueError("delay_ms must be non-negative")
        if self.max_pending < 1:
            raise ValueError("max_pending must be >= 1")


class DebouncedCallback:
    """Wrapper for a debounced callback function."""

    def __init__(
        self,
        callback_id: str,
        func: Callable[..., Any],
        config: DebounceConfig,
    ) -> None:
        """Initialize debounced callback.

        Args:
            callback_id: Unique identifier for callback
            func: Function to debounce
            config: Debounce configuration
        """
        self.callback_id = callback_id
        self.func = func
        self.config = config
        self.last_call_time: float = 0
        self.last_exec_time: float = 0
        self.pending_calls: int = 0
        self.pending_task: Optional[asyncio.Task[Any]] = None
        self.call_count: int = 0
        self.exec_count: int = 0

    async def execute_debounced(self, *args: Any, **kwargs: Any) -> Any:
        """Execute function with debouncing.

        Args:
            *args: Positional arguments for callback
            **kwargs: Keyword arguments for callback

        Returns:
            Result from function call or None if debounced
        """
        self.call_count += 1
        now = time.time()

        if self.config.strategy == "leading":
            return await self._execute_leading(now, *args, **kwargs)
        elif self.config.strategy == "trailing":
            return await self._execute_trailing(now, *args, **kwargs)
        else:  # throttle
            return await self._execute_throttle(now, *args, **kwargs)

    async def _execute_leading(self, now: float, *args: Any, **kwargs: Any) -> Any:
        """Execute immediately, ignore calls within delay period."""
        delay_sec = self.config.delay_ms / 1000.0

        if now - self.last_exec_time >= delay_sec:
            # Execute immediately
            self.last_exec_time = now
            self.exec_count += 1
            result = self._call_func(*args, **kwargs)
            if asyncio.iscoroutine(result):
                return await result
            return result

        # Ignore this call
        logger.debug(
            f"Callback {self.callback_id}: ignoring call "
            f"(within {self.config.delay_ms}ms)"
        )
        return None

    async def _execute_trailing(self, now: float, *args: Any, **kwargs: Any) -> Any:
        """Wait for silence, then execute once."""
        delay_sec = self.config.delay_ms / 1000.0

        # Cancel pending execution if exists
        if self.pending_task is not None:
            self.pending_task.cancel()

        # Check pending queue
        if self.pending_calls >= self.config.max_pending:
            logger.warning(
                f"Callback {self.callback_id}: pending queue full "
                f"({self.pending_calls}), dropping call"
            )
            return None

        self.pending_calls += 1

        # Schedule delayed execution
        async def delayed_exec() -> Any:
            try:
                await asyncio.sleep(delay_sec)
                self.pending_calls -= 1
                self.last_exec_time = time.time()
                self.exec_count += 1
                result = self._call_func(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    return await result
                return result
            except asyncio.CancelledError:
                self.pending_calls -= 1
                logger.debug(f"Callback {self.callback_id}: trailing task cancelled")
                raise

        self.pending_task = asyncio.create_task(delayed_exec())
        return await self.pending_task

    async def _execute_throttle(self, now: float, *args: Any, **kwargs: Any) -> Any:
        """Execute at most once per delay period."""
        delay_sec = self.config.delay_ms / 1000.0

        if now - self.last_exec_time >= delay_sec:
            self.last_exec_time = now
            self.exec_count += 1
            result = self._call_func(*args, **kwargs)
            if asyncio.iscoroutine(result):
                return await result
            return result

        logger.debug(
            f"Callback {self.callback_id}: throttled "
            f"(next available in {delay_sec}s)"
        )
        return None

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        """Call the underlying function."""
        try:
            return self.func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in callback {self.callback_id}: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get callback statistics."""
        return {
            "callback_id": self.callback_id,
            "strategy": self.config.strategy,
            "delay_ms": self.config.delay_ms,
            "call_count": self.call_count,
            "exec_count": self.exec_count,
            "reduction_percent": (
                (1 - self.exec_count / self.call_count) * 100
                if self.call_count > 0
                else 0
            ),
            "pending_calls": self.pending_calls,
        }


class CallbackDebouncer:
    """Singleton manager for debounced callbacks."""

    _instance: Optional["CallbackDebouncer"] = None
    _callbacks: Dict[str, DebouncedCallback] = {}
    _default_config = DebounceConfig()

    def __new__(cls) -> "CallbackDebouncer":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(
        self,
        callback_id: str,
        func: Callable[..., Any],
        config: Optional[DebounceConfig] = None,
    ) -> Callable[..., Any]:
        """Register a callback for debouncing.

        Args:
            callback_id: Unique identifier for callback
            func: Function to debounce
            config: Debounce configuration (uses default if None)

        Returns:
            Debounced wrapper function
        """
        if callback_id in self._callbacks:
            logger.warning(f"Callback {callback_id} already registered, replacing")

        cfg = config or self._default_config
        debounced = DebouncedCallback(callback_id, func, cfg)
        self._callbacks[callback_id] = debounced

        logger.info(
            f"Registered callback {callback_id}: "
            f"strategy={cfg.strategy}, delay={cfg.delay_ms}ms"
        )

        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await debounced.execute_debounced(*args, **kwargs)

        return wrapper

    def get_callback(self, callback_id: str) -> Optional[DebouncedCallback]:
        """Get callback by ID."""
        return self._callbacks.get(callback_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all callbacks."""
        stats = {}
        for callback_id, callback in self._callbacks.items():
            stats[callback_id] = callback.get_stats()

        total_calls = sum(s["call_count"] for s in stats.values())
        total_execs = sum(s["exec_count"] for s in stats.values())

        return {
            "callbacks": stats,
            "total_calls": total_calls,
            "total_execs": total_execs,
            "total_reduction_percent": (
                (1 - total_execs / total_calls) * 100 if total_calls > 0 else 0
            ),
            "callback_count": len(stats),
        }

    def reset_stats(self) -> None:
        """Reset statistics for all callbacks."""
        for callback in self._callbacks.values():
            callback.call_count = 0
            callback.exec_count = 0
        logger.info("Reset all callback statistics")


def get_callback_debouncer() -> CallbackDebouncer:
    """Factory function for singleton access."""
    return CallbackDebouncer()
