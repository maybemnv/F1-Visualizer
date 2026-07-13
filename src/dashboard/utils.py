"""Utility functions extracted from app.py for reusability."""

from collections.abc import Iterable
from contextlib import suppress
from typing import TypeAlias

import pandas as pd
from dash import html

from dashboard.constants import COMPOUND_ORDER
from f1_visualization.consts import VISUAL_CONFIG
from f1_visualization.helpers import add_gap

LapDataBySeason: TypeAlias = dict[int, dict[str, pd.DataFrame]]
COMPOUND_PALETTE = VISUAL_CONFIG["relative"]["high_contrast_palette"]

__all__ = [
    "add_gap",
    "configure_lap_numbers_slider",
    "df_convert_timedelta",
    "get_last_available_round",
    "style_compound_options",
]


def get_last_available_round(df_dict: LapDataBySeason, season: int) -> tuple[int, int]:
    """
    Get the last available sprint and race round number in a given season.

    These keys should not be accessed directly without error handling.

    For example, df_dict[season]["S"] can raise before the first sprint weekend.
    Alternatively, if the first race weekend is a sprint weekend, df_dict[season]["R"]
    will raise even if there is sprint data available.

    Args:
        df_dict: Dictionary containing loaded lap data.
        season: The season year.

    Returns:
        Tuple of (last_race_round, last_sprint_round).
    """
    last_race_round, last_sprint_round = 0, 0

    with suppress(KeyError):
        last_race_round = df_dict[season]["R"]["RoundNumber"].max()

    with suppress(KeyError):
        last_sprint_round = df_dict[season]["S"]["RoundNumber"].max()

    return last_race_round, last_sprint_round


def df_convert_timedelta(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert Timedelta columns to float seconds for JSON serialization.

    Assumes df follows transformed_laps schema. The pd.Timedelta type is not
    JSON serializable, so columns with this data type need to be converted.

    Args:
        df: DataFrame with Timedelta columns.

    Returns:
        DataFrame with Timedelta columns converted to float seconds.
    """
    timedelta_columns = ["Time", "PitInTime", "PitOutTime"]
    # Usually the Time column has no NaT values, included for consistency
    df[timedelta_columns] = df[timedelta_columns].ffill()

    for column in timedelta_columns:
        df[column] = df[column].dt.total_seconds()
    return df


def configure_lap_numbers_slider(data: dict) -> tuple[int, list[int], dict[int, str]]:
    """
    Configure range slider based on the number of laps in a session.

    Args:
        data: Dictionary representation of laps DataFrame.

    Returns:
        Tuple of (max_laps, default_value, tick_marks).
    """
    if not data:
        return 60, [1, 60], {i: str(i) for i in [1, *list(range(5, 61, 5))]}

    try:
        num_laps = max(data["LapNumber"].values())
    except TypeError:
        # The LapNumber column contains NaN, falls back to Pandas
        # This has never been the case in existing data
        df = pd.DataFrame.from_dict(data)
        num_laps = df["LapNumber"].max()

    marks = {i: str(i) for i in [1, *list(range(5, int(num_laps + 1), 5))]}
    return num_laps, [1, num_laps], marks


def style_compound_options(compounds: Iterable[str]) -> list[dict]:
    """
    Create compound dropdown options with color styling.

    Args:
        compounds: Iterable of compound names.

    Returns:
        List of dropdown option dictionaries with styled labels.
    """
    # Discard unknown compounds
    compounds = [compound for compound in compounds if compound in COMPOUND_ORDER]

    # Sort compounds by their position in COMPOUND_ORDER
    compound_index = [COMPOUND_ORDER.index(compound) for compound in compounds]
    sorted_compounds = sorted(zip(compounds, compound_index, strict=True), key=lambda x: x[1])
    compounds = [compound for compound, _ in sorted_compounds]

    return [
        {
            "label": html.Span(compound, style={"color": COMPOUND_PALETTE[compound]}),
            "value": compound,
        }
        for compound in compounds
    ]
