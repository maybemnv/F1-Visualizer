"""Data loading and processing callbacks."""

from collections import Counter
from typing import TypeAlias

import pandas as pd
from dash import Input, Output, State, callback

from dashboard.constants import MIN_COMPOUND_LAP_RATIO
from dashboard.layout import line_y_options, scatter_y_options
from dashboard.utils import df_convert_timedelta, style_compound_options
from f1_visualization.visualization import get_session_info, load_laps

# Type alias for session info tuple
Session_info: TypeAlias = tuple[int, int, str, str, list[str], dict[str, int]]

# Load data once at module level
DF_DICT = load_laps()


@callback(
    Output("session-info", "data"),
    Input("load-session", "n_clicks"),
    State("season", "value"),
    State("event", "value"),
    State("session", "value"),
    State("teammate-comp", "value"),
    prevent_initial_call=True,
)
def get_session_metadata(
    _: int,  # ignores actual value of n_clicks
    season: int,
    event: str,
    session_name: str,
    teammate_comp: bool,
) -> Session_info:
    """
    Store session metadata into browser cache.

    Can assume that season, event, and session are all set (not None).
    """
    round_number, event_name, drivers, session = get_session_info(
        season, event, session_name, teammate_comp=teammate_comp
    )
    event_name = f"{season} {event_name}"

    starting_grid = {}
    if pd.notna(session.results["GridPosition"]).all():
        starting_grid = dict(
            zip(session.results["Abbreviation"], session.results["GridPosition"], strict=True)
        )

    # This order enables calling f.get_session by unpacking the first three items
    return season, round_number, session_name, event_name, drivers, starting_grid


@callback(
    Output("laps", "data"),
    Input("load-session", "n_clicks"),
    State("season", "value"),
    State("event", "value"),
    State("session", "value"),
    prevent_initial_call=True,
)
def get_session_laps(
    _: int,  # ignores actual_value of n_clicks
    season: int,
    event: str,
    session_name: str,
) -> dict:
    """
    Save the laps of the selected session into browser cache.

    Can assume that season, event, and session are all set (not None).
    """
    included_laps = DF_DICT[season][session_name]
    included_laps = included_laps[included_laps["EventName"] == event]
    included_laps = df_convert_timedelta(included_laps)

    return included_laps.to_dict()


@callback(
    Output("scatter-y", "options"),
    Output("line-y", "options"),
    Output("scatter-y", "value"),
    Output("line-y", "value"),
    Input("laps", "data"),
    prevent_initial_call=True,
)
def set_y_axis_dropdowns(
    data: dict,
) -> tuple[list[dict[str, str]], list[dict[str, str]], str, str]:
    """Update y axis options based on the columns in the laps dataframe."""

    def readable_gap_col_name(col: str) -> str:
        """Convert Pandas GapTox column names to the more readable Gap to x."""
        return f"Gap to {col[-3:]} (s)"

    gap_cols = filter(lambda x: x.startswith("Gap"), data.keys())
    gap_col_options = [{"label": readable_gap_col_name(col), "value": col} for col in gap_cols]
    return (
        scatter_y_options + gap_col_options,
        line_y_options + gap_col_options,
        "LapTime",
        "Position",
    )


@callback(
    Output("compounds", "options"),
    Output("compounds", "value"),
    Output("compounds", "disabled"),
    Input("laps", "data"),
    prevent_initial_call=True,
)
def set_compounds_dropdown(data: dict) -> tuple[list[dict], list, bool]:
    """Update compound plot dropdown options based on the laps dataframe."""
    compound_lap_count = Counter(data["Compound"].values())
    eligible_compounds = [
        compound
        for compound, count in compound_lap_count.items()
        if count >= (compound_lap_count.total() // MIN_COMPOUND_LAP_RATIO)
    ]
    return style_compound_options(eligible_compounds), [], False


@callback(
    Output("laps-data-sequencer", "children"),
    Input("laps", "data"),
    prevent_initial_call=True,
)
def after_laps_data_callback(included_laps: dict) -> str:
    """
    Populate an invisible element that serves as input for other callbacks.

    This serves to ensure those other callbacks are only fired after laps data is loaded.
    """
    return str(included_laps.keys())


@callback(
    Output("session-data", "data"),
    Input("session-info", "data"),
    prevent_initial_call=True,
)
def update_session_data_store(session_info: Session_info | None) -> dict:
    """Update session-data store for analysis tab."""
    if not session_info:
        return {}

    season, round_number, session_name, event_name, drivers, starting_grid = session_info
    return {
        "season": season,
        "round_number": round_number,
        "session_type": session_name,
        "event_name": event_name,
        "drivers": drivers,
        "starting_grid": starting_grid,
    }

