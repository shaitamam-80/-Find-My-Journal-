"""
In-memory caching layer for verification results.

Caches verification results to reduce API calls and improve performance.
Different TTLs for different verification statuses.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

from app.models.journal import BadgeColor, VerificationStatus


@dataclass
class CacheEntry:
    """A single cache entry with TTL tracking."""
    value: VerificationStatus
    created_at: datetime
    expires_at: datetime


class VerificationCache:
    """
    In-memory cache for journal verification results.

    TTL varies by verification status:
    - GREEN (verified): 7 days - stable status
    - RED (high risk): 30 days - very stable
    - YELLOW (caution): 7 days - may change
    - GRAY (unverified): 3 days - retry sooner

    Usage:
        cache = VerificationCache()

        # Get cached result
        result = cache.get("0028-0836")

        # Cache a new result
        cache.set("0028-0836", verification_status)

        # Clear expired entries
        cache.cleanup()
    """

    # TTL configuration in seconds
    TTL_CONFIG: Dict[BadgeColor, int] = {
        BadgeColor.GREEN: 7 * 24 * 3600,    # 7 days
        BadgeColor.RED: 30 * 24 * 3600,     # 30 days
        BadgeColor.YELLOW: 7 * 24 * 3600,   # 7 days
        BadgeColor.GRAY: 3 * 24 * 3600,     # 3 days
    }

    # Default TTL for errors/fallbacks
    DEFAULT_TTL: int = 1 * 3600  # 1 hour

    def __init__(self, default_ttl: Optional[int] = None):
        """
        Initialize the cache.

        Args:
            default_ttl: Override default TTL in seconds (optional)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl or self.DEFAULT_TTL
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0,
        }

    def _get_ttl(self, status: VerificationStatus) -> int:
        """Get TTL based on verification status."""
        return self.TTL_CONFIG.get(status.badge_color, self._default_ttl)

    def get(self, key: str) -> Optional[VerificationStatus]:
        """
        Get cached verification status.

        Args:
            key: Cache key (ISSN or journal ID)

        Returns:
            Cached VerificationStatus or None if not found/expired
        """
        entry = self._cache.get(key)

        if entry is None:
            self._stats["misses"] += 1
            return None

        # Check if expired
        if datetime.now() > entry.expires_at:
            del self._cache[key]
            self._stats["misses"] += 1
            self._stats["evictions"] += 1
            return None

        self._stats["hits"] += 1
        return entry.value

    def set(
        self,
        key: str,
        value: VerificationStatus,
        ttl: Optional[int] = None,
    ) -> None:
        """
        Cache a verification status.

        Args:
            key: Cache key (ISSN or journal ID)
            value: VerificationStatus to cache
            ttl: Override TTL in seconds (optional)
        """
        actual_ttl = ttl or self._get_ttl(value)
        now = datetime.now()

        entry = CacheEntry(
            value=value,
            created_at=now,
            expires_at=now + timedelta(seconds=actual_ttl),
        )

        # Update the status with cache metadata
        value.checked_at = now
        value.cache_valid_until = entry.expires_at

        self._cache[key] = entry
        self._stats["sets"] += 1

    def delete(self, key: str) -> bool:
        """
        Remove an entry from cache.

        Args:
            key: Cache key to remove

        Returns:
            True if entry was removed, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> int:
        """
        Clear all cached entries.

        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        return count

    def cleanup(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of entries removed
        """
        now = datetime.now()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now > entry.expires_at
        ]

        for key in expired_keys:
            del self._cache[key]

        self._stats["evictions"] += len(expired_keys)
        return len(expired_keys)

    def size(self) -> int:
        """Get number of entries in cache."""
        return len(self._cache)

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        hit_rate = 0.0
        total = self._stats["hits"] + self._stats["misses"]
        if total > 0:
            hit_rate = self._stats["hits"] / total

        return {
            **self._stats,
            "size": self.size(),
            "hit_rate": round(hit_rate, 3),
        }


# Global cache instance
_cache_instance: Optional[VerificationCache] = None


def get_cache() -> VerificationCache:
    """Get the global cache instance (singleton pattern)."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = VerificationCache()
    return _cache_instance


def reset_cache() -> None:
    """Reset the global cache instance (for testing)."""
    global _cache_instance
    if _cache_instance:
        _cache_instance.clear()
    _cache_instance = None
