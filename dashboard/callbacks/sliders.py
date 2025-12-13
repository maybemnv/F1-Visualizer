"""Slider configuration callbacks."""

from typing import TypeAlias

from dash import Input, Output, State, callback

from dashboard.utils import configure_lap_numbers_slider

# Type alias for session info tuple
Session_info: TypeAlias = tuple[int, int, str, str, list[str], dict[str, int]]


@callback(
    Output("lap-numbers-scatter", "max"),
    Output("lap-numbers-scatter", "value"),
    Output("lap-numbers-scatter", "marks"),
    Input("laps", "data"),
)
def set_scatterplot_slider(data: dict) -> tuple[int, list[int], dict[int, str]]:
    """Set up scatterplot tab lap numbers slider."""
    return configure_lap_numbers_slider(data)


@callback(
    Output("lap-numbers-line", "max"),
    Output("lap-numbers-line", "value"),
    Output("lap-numbers-line", "marks"),
    Input("laps", "data"),
)
def set_lineplot_slider(data: dict) -> tuple[int, list[int], dict[int, str]]:
    """Set up lineplot tab lap numbers slider."""
    return configure_lap_numbers_slider(data)


@callback(
    Output("show-starting-grid", "options"),
    Output("show-starting-grid", "value"),
    Input("line-y", "value"),
    Input("session-info", "data"),
    State("show-starting-grid", "value"),
)
def set_starting_grid_switch(
    y: str, session_info: Session_info, current_setting: list | None
) -> tuple[list[dict], list | None]:
    """
    Enable show starting grid switch only when y-axis is position.

    Lock the switch to the off position when the data is not available.
    """
    if session_info is None:
        # Default configuration
        return [
            {
                "label": "Show starting position",
                "value": 1,
                "disabled": False,
            }
        ], [1]
    if not session_info[5]:
        # The starting position is only known if session_info[5] is populated
        return [
            {
                "label": "Show starting position",
                "value": 1,
                "disabled": True,
            }
        ], []
    return [
        {
            "label": "Show starting position",
            "value": 1,
            "disabled": y != "Position",
        }
    ], current_setting
