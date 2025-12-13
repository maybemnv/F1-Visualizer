"""Gap calculation and driver data utilities."""

import pandas as pd

from f1_visualization.data_loader import DF_DICT


def add_gap(
    driver: str,
    df_laps: pd.DataFrame | None = None,
    modify_global: bool = False,
    **kwargs,  # noqa: ANN003
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
    assert not (not modify_global and df_laps is None), (
        "df_laps must be provided if not editing in-place."
    )

    if modify_global:
        assert "season" in kwargs and "session_type" in kwargs, (
            "Setting modify_global=True requires specifying season and session_type."
        )
        season, session_type = kwargs["season"], kwargs["session_type"]
        df_laps = DF_DICT[season][session_type]

    assert driver.upper() in df_laps["Driver"].unique(), "Driver not available."

    df_driver = df_laps[df_laps["Driver"] == driver][["RoundNumber", "LapNumber", "Time"]]
    timing_column_name = f"{driver}Time"
    df_driver = df_driver.rename(columns={"Time": timing_column_name})

    df_driver[timing_column_name] = df_driver[timing_column_name].ffill()

    df_laps = df_laps.merge(
        df_driver, how="left", on=["RoundNumber", "LapNumber"], validate="many_to_one"
    )
    df_laps[f"GapTo{driver}"] = (
        df_laps["Time"] - df_laps[timing_column_name]
    ).dt.total_seconds()
    df_laps = df_laps.drop(columns=timing_column_name)

    if modify_global:
        DF_DICT[kwargs["season"]][kwargs["session_type"]] = df_laps

    return df_laps
