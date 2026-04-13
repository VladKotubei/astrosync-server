"""
Shared in-memory TTL caches for the AstroSync backend.

Three pre-configured singletons cover the most common caching scenarios:

    general_cache     – 1 hour TTL, 1024 entries.
                        Use for transient or frequently-refreshed data such as
                        transit calculations, current planetary positions, or
                        any request-scoped lookups that benefit from short-term
                        deduplication.

    daily_cache       – 24 hour TTL, 256 entries.
                        Use for values that change once per calendar day:
                        daily horoscopes, biorhythm energy scores, angel-number
                        interpretations tied to a date, etc.

    permanent_cache   – 7 day TTL, 512 entries.
                        Use for data that is essentially static or very slow to
                        change: destiny matrices, natal chart fragments,
                        numerology base numbers, and compatibility tables.

Import the singleton you need:

    from app.services.cache import daily_cache

    result = daily_cache.get(key)
    if result is None:
        result = expensive_computation()
        daily_cache.set(key, result)
"""

from __future__ import annotations

from threading import Lock
from typing import Any, Optional

from cachetools import TTLCache


class CacheService:
    """Thread-safe in-memory TTL cache.

    Entries expire automatically after *ttl* seconds.  The underlying
    TTLCache is wrapped with a Lock so that concurrent FastAPI worker
    threads cannot cause cache corruption.
    """

    def __init__(self, maxsize: int = 512, ttl: int = 900) -> None:
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


general_cache = CacheService(maxsize=1024, ttl=3600)
daily_cache = CacheService(maxsize=256, ttl=86400)
permanent_cache = CacheService(maxsize=512, ttl=604800)
