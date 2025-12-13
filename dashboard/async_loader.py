"""Async data loading utilities for dashboard."""

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

import pandas as pd

logger = logging.getLogger(__name__)


class LoadingState(Enum):
    """State of async data loading."""

    IDLE = "idle"
    LOADING = "loading"
    SUCCESS = "success"
    ERROR = "error"


@dataclass
class LoadingResult:
    """Result of an async loading operation."""

    state: LoadingState
    data: Any | None = None
    error: str | None = None
    progress: float = 0.0  # 0.0 to 1.0


class AsyncDataLoader:
    """
    Async data loader using thread pool for non-blocking data fetches.

    Works with Dash's callback system by storing results that can be
    polled by subsequent callbacks.
    """

    def __init__(self, max_workers: int = 2):
        """
        Initialize async loader.

        Args:
            max_workers: Maximum concurrent loading operations
        """
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._results: dict[str, LoadingResult] = {}
        self._futures: dict[str, Any] = {}

        logger.info("AsyncDataLoader initialized with %d workers", max_workers)

    def _generate_key(self, *args: Any) -> str:
        """Generate unique key for loading operation."""
        return "_".join(str(a) for a in args)

    def start_loading(
        self,
        key: str,
        func: Callable[..., pd.DataFrame],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Start async loading operation.

        Args:
            key: Unique key to identify this loading operation
            func: Function to call that returns data
            *args: Arguments to pass to func
            **kwargs: Keyword arguments to pass to func
        """
        if key in self._futures and not self._futures[key].done():
            logger.debug("Loading already in progress for %s", key)
            return

        self._results[key] = LoadingResult(state=LoadingState.LOADING, progress=0.1)

        def _load() -> pd.DataFrame:
            try:
                logger.debug("Starting load for %s", key)
                result = func(*args, **kwargs)
                self._results[key] = LoadingResult(
                    state=LoadingState.SUCCESS,
                    data=result,
                    progress=1.0,
                )
                logger.debug("Load complete for %s", key)
                return result
            except Exception as e:
                logger.exception("Load failed for %s", key)
                self._results[key] = LoadingResult(
                    state=LoadingState.ERROR,
                    error=str(e),
                    progress=0.0,
                )
                raise

        future = self._executor.submit(_load)
        self._futures[key] = future

    def get_result(self, key: str) -> LoadingResult:
        """
        Get result of loading operation.

        Args:
            key: Key of the loading operation

        Returns:
            LoadingResult with current state and data
        """
        return self._results.get(
            key, LoadingResult(state=LoadingState.IDLE)
        )

    def is_loading(self, key: str) -> bool:
        """Check if loading operation is in progress."""
        result = self.get_result(key)
        return result.state == LoadingState.LOADING

    def is_complete(self, key: str) -> bool:
        """Check if loading operation is complete (success or error)."""
        result = self.get_result(key)
        return result.state in (LoadingState.SUCCESS, LoadingState.ERROR)

    def clear(self, key: str | None = None) -> None:
        """
        Clear loading results.

        Args:
            key: Specific key to clear, or None to clear all
        """
        if key:
            self._results.pop(key, None)
            self._futures.pop(key, None)
        else:
            self._results.clear()
            self._futures.clear()

    def shutdown(self) -> None:
        """Shutdown the executor."""
        self._executor.shutdown(wait=False)
        logger.info("AsyncDataLoader shutdown")


# Global async loader instance
async_loader = AsyncDataLoader()


def get_loading_component_style(state: LoadingState) -> dict:
    """
    Get CSS style for loading indicator based on state.

    Args:
        state: Current loading state

    Returns:
        CSS style dictionary for dash components
    """
    base_style = {"transition": "opacity 0.3s ease"}

    if state == LoadingState.LOADING:
        return {**base_style, "opacity": "0.5", "pointerEvents": "none"}
    if state == LoadingState.ERROR:
        return {**base_style, "border": "2px solid red"}
    return {**base_style, "opacity": "1"}
