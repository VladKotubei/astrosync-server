"""
In-memory TTL cache for geocentric moon data (phase, illumination, distance,
next full moon).  These values are location-independent, so a single cached
entry covers all users querying the same calendar date.

─────────────────────────────────────────────────────────────────────────────
PRODUCTION SWAP → Redis
─────────────────────────────────────────────────────────────────────────────
Replace this class with a Redis-backed adapter that satisfies the same
get / set / invalidate interface, for example:

    import json
    import aioredis

    class CacheService:
        def __init__(self, redis_url: str = "redis://localhost:6379", ttl: int = 900):
            self._redis = aioredis.from_url(redis_url, decode_responses=True)
            self._ttl = ttl

        async def get(self, key: str):
            raw = await self._redis.get(key)
            return json.loads(raw) if raw is not None else None

        async def set(self, key: str, value) -> None:
            await self._redis.set(key, json.dumps(value, default=str), ex=self._ttl)

        async def invalidate(self, key: str) -> None:
            await self._redis.delete(key)

The FastAPI route handlers would then become `async def` coroutines and call
`await cache.get(key)` instead of the synchronous `cache.get(key)`.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from threading import Lock
from typing import Any, Optional

from cachetools import TTLCache

_DEFAULT_MAXSIZE = 512
_DEFAULT_TTL_SECONDS = 900  # 15 minutes


class CacheService:
    """Thread-safe in-memory TTL cache.

    Entries expire automatically after *ttl* seconds.  The underlying
    TTLCache is wrapped with a Lock so that concurrent FastAPI worker
    threads cannot cause cache corruption.
    """

    def __init__(self, maxsize: int = _DEFAULT_MAXSIZE, ttl: int = _DEFAULT_TTL_SECONDS) -> None:
        self._cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """Return the cached value, or *None* if absent / expired."""
        with self._lock:
            return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Store *value* under *key*, overwriting any existing entry."""
        with self._lock:
            self._cache[key] = value

    def invalidate(self, key: str) -> None:
        """Remove a specific key without waiting for TTL expiry."""
        with self._lock:
            self._cache.pop(key, None)

    @property
    def size(self) -> int:
        """Number of entries currently held in the cache."""
        with self._lock:
            return len(self._cache)


# Module-level singleton – imported and reused by the router
moon_cache = CacheService()
