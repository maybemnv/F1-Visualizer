"""Data loading utilities for F1 lap data."""

import logging
from collections.abc import Iterator, MutableMapping

import pandas as pd

from f1_visualization.consts import DATA_PATH, SESSION_NAMES

logger = logging.getLogger(__name__)


def _correct_dtype(df_laps: pd.DataFrame) -> pd.DataFrame:
    """
    Fix incorrectly parsed data types.

    Requires:
        df_laps has the following columns: [`Time`, `PitInTime`, `PitOutTime`,
                                            `TrackStatus`, `FreshTyre`]
    """
    df_laps[["Time", "PitInTime", "PitOutTime"]] = df_laps[
        ["Time", "PitInTime", "PitOutTime"]
    ].apply(pd.to_timedelta)

    df_laps["TrackStatus"] = df_laps["TrackStatus"].astype(str)
    df_laps["FreshTyre"] = df_laps["FreshTyre"].fillna("Unknown").astype(str)

    return df_laps


def load_laps() -> dict[int, dict[str, pd.DataFrame]]:
    """Load transformed data by season."""
    dfs: dict[int, dict[str, pd.DataFrame]] = {}
    files = sorted(DATA_PATH.glob("**/transformed_*.csv"))

    if not files:
        logger.warning("No transformed lap CSV files found in %s", DATA_PATH)
        return dfs

    for file in files:
        season = int(file.stem.split("_")[-1])
        session_type = SESSION_NAMES[file.parent.name]
        df = pd.read_csv(
            file,
            header=0,
            true_values=["True"],
            false_values=["False"],
        )
        _correct_dtype(df)

        if season not in dfs:
            dfs[season] = {}

        dfs[season][session_type] = df

    return dfs


class LapDataStore(MutableMapping[int, dict[str, pd.DataFrame]]):
    """Lazy mapping that loads transformed lap data on first access."""

    def __init__(self) -> None:
        """Initialize an unloaded lap data store."""
        self._data: dict[int, dict[str, pd.DataFrame]] | None = None

    def _ensure_loaded(self) -> dict[int, dict[str, pd.DataFrame]]:
        """Load data once and return the cached mapping."""
        if self._data is None:
            self._data = load_laps()
        return self._data

    def __getitem__(self, key: int) -> dict[str, pd.DataFrame]:
        """Return lap data for one season."""
        return self._ensure_loaded()[key]

    def __setitem__(self, key: int, value: dict[str, pd.DataFrame]) -> None:
        """Set lap data for one season."""
        self._ensure_loaded()[key] = value

    def __delitem__(self, key: int) -> None:
        """Delete lap data for one season."""
        del self._ensure_loaded()[key]

    def __iter__(self) -> Iterator[int]:
        """Iterate over loaded seasons."""
        return iter(self._ensure_loaded())

    def __len__(self) -> int:
        """Return the number of loaded seasons."""
        return len(self._ensure_loaded())

    def reload(self) -> None:
        """Force lap data to be reloaded on the next access."""
        self._data = None


DF_DICT = LapDataStore()
