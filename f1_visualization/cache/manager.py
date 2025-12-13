"""Multi-level cache manager with memory (LRU) and disk layers."""

import hashlib
import logging
import pickle
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from f1_visualization.schemas.settings import cache_settings, settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Multi-level cache manager with memory and disk layers.

    Memory Layer: LRU cache for frequently accessed data
    Disk Layer: Pickle/Parquet files with TTL expiration
    """

    def __init__(
        self,
        cache_dir: Path | None = None,
        memory_size: int | None = None,
        disk_ttl_hours: int | None = None,
    ):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory for disk cache files
            memory_size: Maximum size of LRU memory cache
            disk_ttl_hours: Time-to-live for disk cache entries in hours
        """
        self._cache_dir = cache_dir or settings.cache_dir
        self._memory_size = memory_size or cache_settings.memory_size
        self._disk_ttl = timedelta(hours=disk_ttl_hours or cache_settings.disk_ttl_hours)
        self._disk_format = cache_settings.disk_format

        # Create cache directory if it doesn't exist
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        # Setup memory cache
        self._memory_cache: dict[str, Any] = {}
        self._memory_access_order: list[str] = []

        logger.info(
            "CacheManager initialized: memory_size=%d, disk_ttl=%s, dir=%s",
            self._memory_size,
            self._disk_ttl,
            self._cache_dir,
        )

    def _generate_key(self, *args: Any, **kwargs: Any) -> str:
        """Generate a unique cache key from arguments."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()  # noqa: S324

    def _get_disk_path(self, key: str) -> Path:
        """Get disk cache file path for a key."""
        ext = ".parquet" if self._disk_format == "parquet" else ".pkl"
        return self._cache_dir / f"{key}{ext}"

    def _is_disk_cache_valid(self, path: Path) -> bool:
        """Check if disk cache file exists and is not expired."""
        if not path.exists():
            return False

        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        age = datetime.now(tz=timezone.utc) - mtime
        return age < self._disk_ttl

    def _evict_lru(self) -> None:
        """Evict least recently used entry from memory cache."""
        if self._memory_access_order:
            lru_key = self._memory_access_order.pop(0)
            self._memory_cache.pop(lru_key, None)
            logger.debug("Evicted LRU key from memory: %s", lru_key)

    def get(self, key: str) -> pd.DataFrame | None:
        """
        Get data from cache, checking memory first, then disk.

        Args:
            key: Cache key

        Returns:
            Cached DataFrame or None if not found/expired
        """
        # Check memory cache first
        if key in self._memory_cache:
            # Update access order (move to end)
            if key in self._memory_access_order:
                self._memory_access_order.remove(key)
            self._memory_access_order.append(key)
            logger.debug("Memory cache hit: %s", key)
            return self._memory_cache[key]

        # Check disk cache
        disk_path = self._get_disk_path(key)
        if self._is_disk_cache_valid(disk_path):
            try:
                if self._disk_format == "parquet":
                    data = pd.read_parquet(disk_path)
                else:
                    with open(disk_path, "rb") as f:
                        data = pickle.load(f)  # noqa: S301

                # Promote to memory cache
                self._set_memory(key, data)
                logger.debug("Disk cache hit, promoted to memory: %s", key)
                return data
            except (OSError, pickle.PickleError, pd.errors.EmptyDataError) as e:
                logger.warning("Failed to read disk cache %s: %s", key, e)
                disk_path.unlink(missing_ok=True)

        logger.debug("Cache miss: %s", key)
        return None

    def _set_memory(self, key: str, data: pd.DataFrame) -> None:
        """Set data in memory cache with LRU eviction."""
        # Evict if at capacity
        while len(self._memory_cache) >= self._memory_size:
            self._evict_lru()

        self._memory_cache[key] = data
        if key in self._memory_access_order:
            self._memory_access_order.remove(key)
        self._memory_access_order.append(key)

    def set(self, key: str, data: pd.DataFrame, disk: bool = True) -> None:
        """
        Set data in cache.

        Args:
            key: Cache key
            data: DataFrame to cache
            disk: Whether to also persist to disk
        """
        # Set in memory
        self._set_memory(key, data)
        logger.debug("Set memory cache: %s", key)

        # Set in disk if enabled
        if disk:
            disk_path = self._get_disk_path(key)
            try:
                if self._disk_format == "parquet":
                    data.to_parquet(disk_path, index=False)
                else:
                    with open(disk_path, "wb") as f:
                        pickle.dump(data, f)
                logger.debug("Set disk cache: %s", key)
            except (OSError, pickle.PickleError) as e:
                logger.warning("Failed to write disk cache %s: %s", key, e)

    def invalidate(self, key: str) -> None:
        """Invalidate a specific cache entry."""
        # Remove from memory
        self._memory_cache.pop(key, None)
        if key in self._memory_access_order:
            self._memory_access_order.remove(key)

        # Remove from disk
        disk_path = self._get_disk_path(key)
        disk_path.unlink(missing_ok=True)
        logger.info("Invalidated cache: %s", key)

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache entries matching a pattern.

        Args:
            pattern: Glob pattern to match cache keys

        Returns:
            Number of entries invalidated
        """
        count = 0

        # Memory cache
        keys_to_remove = [k for k in self._memory_cache if pattern in k]
        for key in keys_to_remove:
            self._memory_cache.pop(key, None)
            if key in self._memory_access_order:
                self._memory_access_order.remove(key)
            count += 1

        # Disk cache
        for path in self._cache_dir.glob(f"*{pattern}*"):
            path.unlink(missing_ok=True)
            count += 1

        logger.info("Invalidated %d entries matching pattern: %s", count, pattern)
        return count

    def clear(self) -> None:
        """Clear all cache entries."""
        self._memory_cache.clear()
        self._memory_access_order.clear()

        for path in self._cache_dir.glob("*.pkl"):
            path.unlink(missing_ok=True)
        for path in self._cache_dir.glob("*.parquet"):
            path.unlink(missing_ok=True)

        logger.info("Cache cleared")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        disk_files = list(self._cache_dir.glob("*.pkl")) + list(
            self._cache_dir.glob("*.parquet")
        )
        disk_size = sum(f.stat().st_size for f in disk_files if f.exists())

        return {
            "memory_entries": len(self._memory_cache),
            "memory_capacity": self._memory_size,
            "disk_entries": len(disk_files),
            "disk_size_mb": round(disk_size / 1_000_000, 2),
            "disk_ttl_hours": self._disk_ttl.total_seconds() / 3600,
        }


# Global cache manager instance
cache_manager = CacheManager()


@lru_cache(maxsize=256)
def cached_session_info(season: int, event: str, session_type: str) -> tuple:
    """LRU-cached wrapper for session info lookups."""
    from f1_visualization.session import get_session_info

    return get_session_info(season, event, session_type)
