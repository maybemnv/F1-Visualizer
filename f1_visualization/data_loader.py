"""Data loading utilities for F1 lap data."""

import logging

import pandas as pd

from f1_visualization.consts import DATA_PATH, SESSION_NAMES

logging.basicConfig(level=logging.INFO, format="%(filename)s\t%(levelname)s\t%(message)s")
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
    df_laps["FreshTyre"] = df_laps["FreshTyre"].astype(str)

    return df_laps


def load_laps() -> dict[int, dict[str, pd.DataFrame]]:
    """Load transformed data by season."""
    dfs = {}

    for file in DATA_PATH.glob("**/transformed_*.csv"):
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


# Load data once at module level
DF_DICT = load_laps()
