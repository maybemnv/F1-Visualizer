"""Driver-related callbacks."""

from typing import TypeAlias

import pandas as pd
from dash import Input, Output, State, callback

from dashboard.utils import add_gap

# Type alias for session info tuple
Session_info: TypeAlias = tuple[int, int, str, str, list[str], dict[str, int]]


@callback(
    Output("drivers", "options"),
    Output("drivers", "value"),
    Output("drivers", "disabled"),
    Output("gap-drivers", "options"),
    Output("gap-drivers", "value"),
    Output("gap-drivers", "disabled"),
    Input("session-info", "data"),
    prevent_initial_call=True,
)
def set_driver_dropdowns(
    session_info: Session_info,
) -> tuple[list[str], list[str], bool, list[str], list[str], bool]:
    """Configure driver dropdowns."""
    drivers = session_info[4]
    return drivers, drivers, False, drivers, [], False


@callback(
    Output("add-gap", "disabled"),
    Input("load-session", "n_clicks"),
    prevent_initial_call=True,
)
def enable_add_gap(n_clicks: int) -> bool:
    """Enable the add-gap button after a session has been loaded."""
    return n_clicks == 0


@callback(
    Output("laps", "data", allow_duplicate=True),
    Input("add-gap", "n_clicks"),
    State("gap-drivers", "value"),
    State("laps", "data"),
    running=[
        (Output("gap-drivers", "disabled"), True, False),
        (Output("add-gap", "disabled"), True, False),
        (Output("add-gap", "children"), "Calculating...", "Add Gap"),
        (Output("add-gap", "color"), "warning", "success"),
    ],
    prevent_initial_call=True,
)
def add_gap_to_driver(_: int, drivers: list[str], data: dict) -> dict:
    """Amend the dataframe in cache and add driver gap columns."""
    laps = pd.DataFrame.from_dict(data)
    for driver in drivers:
        if f"GapTo{driver}" not in laps.columns:
            laps = add_gap(driver, laps)

    return laps.to_dict()
