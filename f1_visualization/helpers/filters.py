"""Data filtering and safety car detection helpers."""

import logging

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(filename)s\t%(levelname)s\t%(message)s")
logger = logging.getLogger(__name__)


def remove_low_data_drivers(
    included_laps: pd.DataFrame, drivers: tuple[str], min_laps: int
) -> tuple[str]:
    """
    Return drivers who appear at least min_laps times in included_laps.

    Guarantees the return value is in the same order as the drivers argument.
    """
    lap_counts = included_laps["Driver"].value_counts()
    qualifying_drivers = []

    for driver in drivers:
        if lap_counts.get(driver, 0) >= min_laps:
            qualifying_drivers.append(driver)
        else:
            logger.info("Dropping %s for having less than %d laps.", driver, min_laps)
    return tuple(qualifying_drivers)


def teammate_comp_order(
    included_laps: pd.DataFrame, drivers: tuple[str], by: str
) -> tuple[str]:
    """
    Reorder teammates by the median gap in some metric in descending order.

    For example, if by is LapTime, then the teammates with the biggest median laptime
    difference will appear first.

    Assumes:
        - teammates are next to each other in the drivers tuple
        - by is a column in included_laps.
    """
    metric_median = included_laps.groupby("Driver")[by].median(numeric_only=True)
    team_median_gaps = []

    odd_driver_out = [] if len(drivers) % 2 == 0 else [drivers[-1]]

    for i in range(0, len(drivers) - 1, 2):
        teammates = drivers[i], drivers[i + 1]
        if all(driver in metric_median for driver in teammates):
            median_gap = metric_median[teammates[0]] - metric_median[teammates[1]]
            if median_gap < 0:
                team_median_gaps.append([teammates, -median_gap])
            else:
                team_median_gaps.append([teammates[::-1], median_gap])
        else:
            team_median_gaps.append([teammates, 0])

    team_median_gaps.sort(key=lambda x: x[1], reverse=True)
    drivers = [driver for team in team_median_gaps for driver in team[0]]
    drivers.extend(odd_driver_out)
    return tuple(drivers)


def _lap_filter_sc(row: pd.Series) -> bool:
    """Check if any part of a lap is ran under safety car."""
    return "4" in row.loc["TrackStatus"] and row.loc["Position"] == 1


def _lap_filter_vsc(row: pd.Series) -> bool:
    """Check if any part of a lap is ran under virtual safety car."""
    return (("6" in row.loc["TrackStatus"]) or ("7" in row.loc["TrackStatus"])) and (
        "4" not in row.loc["TrackStatus"] and row.loc["Position"] == 1
    )


def find_sc_laps(df_laps: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """
    Find the unique lap numbers that is ran under SC or VSC.

    The resulting arrays are sorted before they are returned.
    """
    sc_laps = np.sort(df_laps[df_laps.apply(_lap_filter_sc, axis=1)]["LapNumber"].unique())
    vsc_laps = np.sort(df_laps[df_laps.apply(_lap_filter_vsc, axis=1)]["LapNumber"].unique())

    return sc_laps, vsc_laps
