"""Gap calculation and driver data utilities."""

from typing import Any

import pandas as pd


def add_gap(
    driver: str,
    df_laps: pd.DataFrame | None = None,
    modify_global: bool = False,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Calculate the gap to a certain driver.

    Args:
        driver: The driver to whom the gaps will be calculated
        df_laps: The dataframe to modify.
        modify_global: Copies the modified dataframe to the global variable DF_DICT

    Returns:
        Modified dataframe with the gap column under the name GapTo{driver}
    """
    if not modify_global and df_laps is None:
        raise ValueError("df_laps must be provided if not editing in-place.")

    if modify_global:
        if "season" not in kwargs or "session_type" not in kwargs:
            raise ValueError(
                "Setting modify_global=True requires specifying season and session_type."
            )
        from f1_visualization.data_loader import DF_DICT  # noqa: PLC0415

        season, session_type = kwargs["season"], kwargs["session_type"]
        df_laps = DF_DICT[season][session_type]

    if df_laps is None:
        raise ValueError("df_laps could not be resolved.")
    if driver.upper() not in df_laps["Driver"].unique():
        raise ValueError(f"Driver not available: {driver}")

    join_columns = ["LapNumber"]
    if "RoundNumber" in df_laps.columns:
        join_columns.insert(0, "RoundNumber")

    df_driver = df_laps[df_laps["Driver"] == driver][[*join_columns, "Time"]]
    timing_column_name = f"{driver}Time"
    df_driver = df_driver.rename(columns={"Time": timing_column_name})

    if "RoundNumber" in join_columns:
        df_driver[timing_column_name] = df_driver.groupby("RoundNumber")[
            timing_column_name
        ].ffill()
    else:
        df_driver[timing_column_name] = df_driver[timing_column_name].ffill()

    df_laps = df_laps.merge(df_driver, how="left", on=join_columns, validate="many_to_one")
    gap = df_laps["Time"] - df_laps[timing_column_name]
    if pd.api.types.is_timedelta64_dtype(gap):
        gap = gap.dt.total_seconds()
    df_laps[f"GapTo{driver}"] = gap
    df_laps = df_laps.drop(columns=timing_column_name)

    if modify_global:
        from f1_visualization.data_loader import DF_DICT  # noqa: PLC0415

        DF_DICT[kwargs["season"]][kwargs["session_type"]] = df_laps

    return df_laps
