"""Tests for async data loading."""

import time

import pandas as pd
import pytest

from dashboard.async_loader import AsyncDataLoader, LoadingState


@pytest.fixture
def async_loader():
    """Create async loader for tests."""
    loader = AsyncDataLoader(max_workers=2)
    yield loader
    loader.shutdown()


@pytest.fixture
def sample_df():
    """Sample DataFrame for testing."""
    return pd.DataFrame({
        "Driver": ["VER", "HAM"],
        "LapTime": [95.5, 96.0],
    })


class TestAsyncLoader:
    """Tests for AsyncDataLoader functionality."""

    def test_loading_state_idle_initially(self, async_loader):
        """New keys should have IDLE state."""
        result = async_loader.get_result("new_key")
        assert result.state == LoadingState.IDLE

    def test_start_loading_sets_loading_state(self, async_loader, sample_df):
        """Starting load should set LOADING state."""
        def slow_func():
            time.sleep(0.5)
            return sample_df

        async_loader.start_loading("test_key", slow_func)
        
        result = async_loader.get_result("test_key")
        assert result.state == LoadingState.LOADING

    def test_successful_load_sets_success_state(self, async_loader, sample_df):
        """Completed load should set SUCCESS state with data."""
        def quick_func():
            return sample_df

        async_loader.start_loading("test_key", quick_func)
        
        # Wait for completion
        time.sleep(0.2)
        
        result = async_loader.get_result("test_key")
        assert result.state == LoadingState.SUCCESS
        assert result.data is not None
        pd.testing.assert_frame_equal(result.data, sample_df)

    def test_failed_load_sets_error_state(self, async_loader):
        """Failed load should set ERROR state with message."""
        def failing_func():
            raise ValueError("Test error")

        async_loader.start_loading("test_key", failing_func)
        
        # Wait for completion
        time.sleep(0.2)
        
        result = async_loader.get_result("test_key")
        assert result.state == LoadingState.ERROR
        assert "Test error" in result.error

    def test_is_loading(self, async_loader, sample_df):
        """is_loading should return True during loading."""
        def slow_func():
            time.sleep(0.5)
            return sample_df

        async_loader.start_loading("test_key", slow_func)
        
        assert async_loader.is_loading("test_key") is True
        
        # Wait for completion
        time.sleep(0.7)
        
        assert async_loader.is_loading("test_key") is False

    def test_is_complete(self, async_loader, sample_df):
        """is_complete should return True after load finishes."""
        def quick_func():
            return sample_df

        async_loader.start_loading("test_key", quick_func)
        
        # Wait for completion
        time.sleep(0.2)
        
        assert async_loader.is_complete("test_key") is True

    def test_clear_single_key(self, async_loader, sample_df):
        """Clearing single key should work."""
        def quick_func():
            return sample_df

        async_loader.start_loading("key_a", quick_func)
        async_loader.start_loading("key_b", quick_func)
        time.sleep(0.2)
        
        async_loader.clear("key_a")
        
        assert async_loader.get_result("key_a").state == LoadingState.IDLE
        assert async_loader.get_result("key_b").state == LoadingState.SUCCESS

    def test_clear_all(self, async_loader, sample_df):
        """Clearing all should reset all results."""
        def quick_func():
            return sample_df

        async_loader.start_loading("key_a", quick_func)
        async_loader.start_loading("key_b", quick_func)
        time.sleep(0.2)
        
        async_loader.clear()
        
        assert async_loader.get_result("key_a").state == LoadingState.IDLE
        assert async_loader.get_result("key_b").state == LoadingState.IDLE

    def test_duplicate_start_ignored(self, async_loader, sample_df):
        """Starting load twice for same key should be ignored."""
        call_count = 0

        def slow_func():
            nonlocal call_count
            call_count += 1
            time.sleep(0.3)
            return sample_df

        async_loader.start_loading("test_key", slow_func)
        async_loader.start_loading("test_key", slow_func)  # Should be ignored
        
        time.sleep(0.5)
        
        assert call_count == 1
