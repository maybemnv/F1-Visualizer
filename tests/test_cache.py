"""Tests for cache functionality."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from f1_visualization.cache.manager import CacheManager


@pytest.fixture
def temp_cache_dir():
    """Create a temporary directory for cache tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def cache_manager(temp_cache_dir):
    """Create a cache manager with temporary directory."""
    return CacheManager(
        cache_dir=temp_cache_dir,
        memory_size=10,
        disk_ttl_hours=24,
    )


@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "Driver": ["VER", "HAM", "LEC"],
        "LapTime": [95.5, 96.0, 96.5],
        "Position": [1, 2, 3],
    })


class TestCacheManager:
    """Tests for CacheManager functionality."""

    def test_set_and_get_memory(self, cache_manager, sample_df):
        """Data should be retrievable from memory cache."""
        cache_manager.set("test_key", sample_df, disk=False)
        
        result = cache_manager.get("test_key")
        
        assert result is not None
        assert len(result) == 3
        pd.testing.assert_frame_equal(result, sample_df)

    def test_set_and_get_disk(self, cache_manager, sample_df):
        """Data should be retrievable from disk cache."""
        cache_manager.set("test_key", sample_df, disk=True)
        
        # Clear memory cache to force disk read
        cache_manager._memory_cache.clear()
        cache_manager._memory_access_order.clear()
        
        result = cache_manager.get("test_key")
        
        assert result is not None
        pd.testing.assert_frame_equal(result, sample_df)

    def test_cache_miss_returns_none(self, cache_manager):
        """Non-existent key should return None."""
        result = cache_manager.get("nonexistent_key")
        assert result is None

    def test_lru_eviction(self, cache_manager, sample_df):
        """LRU eviction should remove oldest entries."""
        # Fill cache beyond capacity (memory_size=10)
        for i in range(15):
            cache_manager.set(f"key_{i}", sample_df, disk=False)
        
        # First 5 keys should be evicted
        for i in range(5):
            assert cache_manager.get(f"key_{i}") is None
        
        # Later keys should still exist
        for i in range(5, 15):
            assert cache_manager.get(f"key_{i}") is not None

    def test_invalidate_single_key(self, cache_manager, sample_df):
        """Single key invalidation should work."""
        cache_manager.set("key_a", sample_df)
        cache_manager.set("key_b", sample_df)
        
        cache_manager.invalidate("key_a")
        
        assert cache_manager.get("key_a") is None
        assert cache_manager.get("key_b") is not None

    def test_invalidate_pattern(self, cache_manager, sample_df):
        """Pattern-based invalidation should work."""
        cache_manager.set("laps_2024_r1", sample_df)
        cache_manager.set("laps_2024_r2", sample_df)
        cache_manager.set("session_2024", sample_df)
        
        count = cache_manager.invalidate_pattern("laps_2024")
        
        assert count >= 2
        assert cache_manager.get("session_2024") is not None

    def test_clear(self, cache_manager, sample_df):
        """Clear should remove all entries."""
        cache_manager.set("key_1", sample_df)
        cache_manager.set("key_2", sample_df)
        
        cache_manager.clear()
        
        assert cache_manager.get("key_1") is None
        assert cache_manager.get("key_2") is None

    def test_get_stats(self, cache_manager, sample_df):
        """Stats should reflect cache state."""
        cache_manager.set("key_1", sample_df)
        cache_manager.set("key_2", sample_df)
        
        stats = cache_manager.get_stats()
        
        assert stats["memory_entries"] == 2
        assert stats["disk_entries"] == 2
        assert stats["memory_capacity"] == 10


class TestCacheDecorators:
    """Tests for caching decorators."""

    def test_cached_dataframe_decorator(self, temp_cache_dir, sample_df):
        """@cached_dataframe should cache function results."""
        from f1_visualization.cache.decorators import cached_dataframe
        from f1_visualization.cache.manager import cache_manager as global_cache

        # Reset global cache to use temp dir
        global_cache._cache_dir = temp_cache_dir
        
        call_count = 0

        @cached_dataframe("test")
        def get_data(season: int) -> pd.DataFrame:
            nonlocal call_count
            call_count += 1
            return sample_df

        # First call should execute function
        result1 = get_data(2024)
        assert call_count == 1
        
        # Second call should use cache
        result2 = get_data(2024)
        assert call_count == 1  # Should not increase
        
        pd.testing.assert_frame_equal(result1, result2)
