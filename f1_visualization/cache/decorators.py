"""Caching decorators for data functions."""

import functools
import logging
from typing import Callable, ParamSpec, TypeVar

import pandas as pd

from f1_visualization.cache.manager import cache_manager

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def cached_dataframe(key_prefix: str = "", disk: bool = True) -> Callable:
    """
    Decorator to cache DataFrame-returning functions.

    Args:
        key_prefix: Prefix for cache keys
        disk: Whether to persist to disk cache

    Example:
        @cached_dataframe("laps")
        def get_laps(season: int, session: str) -> pd.DataFrame:
            ...
    """

    def decorator(func: Callable[P, pd.DataFrame]) -> Callable[P, pd.DataFrame]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> pd.DataFrame:
            # Generate cache key
            key = cache_manager._generate_key(key_prefix, func.__name__, *args, **kwargs)

            # Try to get from cache
            cached = cache_manager.get(key)
            if cached is not None:
                logger.debug("Cache hit for %s", func.__name__)
                return cached

            # Call function and cache result
            logger.debug("Cache miss for %s, computing...", func.__name__)
            result = func(*args, **kwargs)

            if isinstance(result, pd.DataFrame) and not result.empty:
                cache_manager.set(key, result, disk=disk)

            return result

        return wrapper

    return decorator


def cached_result(key_prefix: str = "", ttl_seconds: int | None = None) -> Callable:
    """
    Decorator to cache any function result using memory cache.

    Args:
        key_prefix: Prefix for cache keys
        ttl_seconds: Optional TTL (not implemented yet, uses default)
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        _cache: dict[str, R] = {}

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = cache_manager._generate_key(key_prefix, func.__name__, *args, **kwargs)

            if key in _cache:
                return _cache[key]

            result = func(*args, **kwargs)
            _cache[key] = result
            return result

        wrapper.cache_clear = _cache.clear  # type: ignore[attr-defined]
        return wrapper

    return decorator


def invalidate_on_update(pattern: str) -> Callable:
    """
    Decorator to invalidate cache entries when data is updated.

    Args:
        pattern: Cache key pattern to invalidate
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(*args, **kwargs)
            cache_manager.invalidate_pattern(pattern)
            return result

        return wrapper

    return decorator
