"""
Redis caching service for indicator results - reduces redundant calculations.

Implements a caching layer for expensive indicator computations:
- TTL-based expiration (configurable per indicator)
- Symbol/timeframe/parameter-based keys
- Async Redis operations (non-blocking)
- Cache statistics and monitoring
- Fallback to calculation if cache miss

Architecture:
- CacheConfig: Configuration with TTL and size limits
- RedisCache: Async wrapper around Redis operations
- CacheManager: Singleton manager with pattern-based invalidation
"""

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)

# Simulate Redis for development (real Redis would use aioredis)
class MockRedis:
    """Mock Redis for development without Redis server."""

    def __init__(self) -> None:
        """Initialize mock Redis."""
        self._cache: Dict[str, tuple[Any, float]] = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self._cache:
            value, expiration = self._cache[key]
            if datetime.now().timestamp() < expiration:
                return value
            else:
                del self._cache[key]
        return None

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set value in cache with optional expiration."""
        expiration = datetime.now().timestamp() + (ex or 3600)
        self._cache[key] = (value, expiration)
        return True

    async def delete(self, key: str) -> int:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            return 1
        return 0

    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern (wildcard support)."""
        count = 0
        # Simple pattern matching (only * wildcard at end)
        if "*" in pattern:
            # Convert glob pattern to regex-like matching
            import fnmatch
            keys_to_delete = [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
            for key in keys_to_delete:
                del self._cache[key]
                count += len(keys_to_delete)
        else:
            # Exact match
            if pattern in self._cache:
                del self._cache[pattern]
                count = 1
        return count

    async def info(self) -> Dict[str, Any]:
        """Get cache info."""
        now = datetime.now().timestamp()
        valid_keys = sum(
            1 for _, exp in self._cache.values() if exp > now
        )
        return {
            "total_keys": len(self._cache),
            "valid_keys": valid_keys,
            "expired_keys": len(self._cache) - valid_keys,
        }


@dataclass
class CacheConfig:
    """Configuration for caching behavior."""

    default_ttl_sec: int = 300  # 5 minutes default
    sma_ttl_sec: int = 60  # 1 minute for fast indicators
    rsi_ttl_sec: int = 60
    macd_ttl_sec: int = 60
    atr_ttl_sec: int = 60
    supertrend_ttl_sec: int = 120
    volume_profile_ttl_sec: int = 300
    squeeze_ttl_sec: int = 120
    max_cache_size: int = 10000  # Max items
    enable_compression: bool = False  # For large payloads

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.default_ttl_sec < 0:
            raise ValueError("default_ttl_sec must be non-negative")
        if self.max_cache_size < 1:
            raise ValueError("max_cache_size must be >= 1")

    def get_ttl_for_indicator(self, indicator_name: str) -> int:
        """Get TTL for specific indicator."""
        attr_name = f"{indicator_name.lower()}_ttl_sec"
        return getattr(self, attr_name, self.default_ttl_sec)


class RedisCache:
    """Async Redis cache wrapper."""

    def __init__(self, redis_client: Optional[Any] = None, config: Optional[CacheConfig] = None) -> None:
        """Initialize Redis cache.

        Args:
            redis_client: Redis client (uses MockRedis if None)
            config: Cache configuration
        """
        self.redis = redis_client or MockRedis()
        self.config = config or CacheConfig()
        self.hit_count: int = 0
        self.miss_count: int = 0
        self.error_count: int = 0

    def _make_key(
        self,
        indicator: str,
        symbol: str,
        timeframe: str,
        params: Dict[str, Any],
    ) -> str:
        """Create cache key from parameters.

        Args:
            indicator: Indicator name
            symbol: Trading symbol
            timeframe: Timeframe (1m, 5m, 1h, etc)
            params: Indicator parameters

        Returns:
            Cache key string
        """
        # Create stable JSON representation
        params_json = json.dumps(params, sort_keys=True, default=str)
        key_str = f"{indicator}:{symbol}:{timeframe}:{params_json}"

        # Hash for shorter keys
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"cache:indicator:{indicator}:{symbol}:{timeframe}:{key_hash}"

    async def get(
        self,
        indicator: str,
        symbol: str,
        timeframe: str,
        params: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Get cached indicator result.

        Args:
            indicator: Indicator name
            symbol: Trading symbol
            timeframe: Timeframe
            params: Indicator parameters

        Returns:
            Cached result or None if not found/expired
        """
        try:
            key = self._make_key(indicator, symbol, timeframe, params)
            value = await self.redis.get(key)

            if value is not None:
                self.hit_count += 1
                logger.debug(f"Cache hit: {key}")
                return json.loads(value) if isinstance(value, str) else value

            self.miss_count += 1
            logger.debug(f"Cache miss: {key}")
            return None

        except Exception as e:
            self.error_count += 1
            logger.error(f"Cache get error: {e}")
            return None

    async def set(
        self,
        indicator: str,
        symbol: str,
        timeframe: str,
        params: Dict[str, Any],
        result: Dict[str, Any],
    ) -> bool:
        """Set cached indicator result.

        Args:
            indicator: Indicator name
            symbol: Trading symbol
            timeframe: Timeframe
            params: Indicator parameters
            result: Result to cache

        Returns:
            True if successful
        """
        try:
            key = self._make_key(indicator, symbol, timeframe, params)
            ttl = self.config.get_ttl_for_indicator(indicator)

            # Convert to JSON-serializable format
            json_result = json.dumps(result, default=str)

            await self.redis.set(key, json_result, ex=ttl)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            self.error_count += 1
            logger.error(f"Cache set error: {e}")
            return False

    async def invalidate_symbol(self, symbol: str) -> int:
        """Invalidate all cache entries for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Number of keys invalidated
        """
        try:
            pattern = f"cache:indicator:*:{symbol}:*"
            count = await self.redis.clear_pattern(pattern)
            logger.info(f"Invalidated {count} cache entries for {symbol}")
            return count

        except Exception as e:
            logger.error(f"Invalidate symbol error: {e}")
            return 0

    async def invalidate_indicator(self, indicator: str) -> int:
        """Invalidate all cache entries for an indicator.

        Args:
            indicator: Indicator name

        Returns:
            Number of keys invalidated
        """
        try:
            pattern = f"cache:indicator:{indicator}:*"
            count = await self.redis.clear_pattern(pattern)
            logger.info(f"Invalidated {count} cache entries for {indicator}")
            return count

        except Exception as e:
            logger.error(f"Invalidate indicator error: {e}")
            return 0

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            info = await self.redis.info()
            total = self.hit_count + self.miss_count
            hit_rate = (self.hit_count / total * 100) if total > 0 else 0

            return {
                "hits": self.hit_count,
                "misses": self.miss_count,
                "errors": self.error_count,
                "total_requests": total,
                "hit_rate_percent": hit_rate,
                "cache_size": info.get("total_keys", 0),
                "valid_keys": info.get("valid_keys", 0),
            }

        except Exception as e:
            logger.error(f"Get stats error: {e}")
            return {
                "hits": self.hit_count,
                "misses": self.miss_count,
                "errors": self.error_count,
            }

    async def clear(self) -> None:
        """Clear all cache entries."""
        try:
            # For MockRedis, clear internal dict
            if hasattr(self.redis, "_cache"):
                self.redis._cache.clear()
            logger.info("Cache cleared")

        except Exception as e:
            logger.error(f"Clear cache error: {e}")


class CacheManager:
    """Singleton manager for Redis cache."""

    _instance: Optional["CacheManager"] = None
    _cache: Optional[RedisCache] = None

    def __new__(cls) -> "CacheManager":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._cache = RedisCache()
        return cls._instance

    def get_cache(self) -> RedisCache:
        """Get cache instance."""
        if self._cache is None:
            self._cache = RedisCache()
        return self._cache

    async def get_or_compute(
        self,
        indicator: str,
        symbol: str,
        timeframe: str,
        params: Dict[str, Any],
        compute_func,
    ) -> Dict[str, Any]:
        """Get cached result or compute if not cached.

        Args:
            indicator: Indicator name
            symbol: Trading symbol
            timeframe: Timeframe
            params: Indicator parameters
            compute_func: Async function to compute result

        Returns:
            Cached or computed result
        """
        cache = self.get_cache()

        # Try cache first
        cached = await cache.get(indicator, symbol, timeframe, params)
        if cached is not None:
            return cached

        # Compute result
        result = await compute_func()

        # Store in cache
        await cache.set(indicator, symbol, timeframe, params, result)

        return result


def get_cache_manager() -> CacheManager:
    """Factory function for singleton access."""
    return CacheManager()
