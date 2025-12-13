"""Session selection callbacks."""

import fastf1 as f
from dash import Input, Output, State, callback

from dashboard.utils import get_last_available_round
from f1_visualization.consts import SPRINT_FORMATS
from f1_visualization.visualization import load_laps

# Load data once at module level
DF_DICT = load_laps()


@callback(
    Output("season", "options"),
    Input("season", "placeholder"),
)
def set_season_options(_: str) -> list[int]:
    """Get the list of seasons with available data."""
    return sorted(DF_DICT.keys(), reverse=True)


@callback(
    Output("event", "options"),
    Output("event", "value"),
    Output("event-schedule", "data"),
    Output("last-race-round", "data"),
    Output("last-sprint-round", "data"),
    Input("season", "value"),
    State("event", "value"),
    prevent_initial_call=True,
)
def set_event_options(
    season: int | None, old_event: str | None
) -> tuple[list[str], None, dict, int, int]:
    """Get the names of all events in the selected season."""
    if season is None:
        return [], None, {}, 0, 0
    schedule = f.get_event_schedule(season, include_testing=False)
    last_round_numbers = get_last_available_round(DF_DICT, season)
    schedule = schedule[schedule["RoundNumber"] <= max(last_round_numbers)]

    return (
        list(schedule["EventName"]),
        old_event if old_event in set(schedule["EventName"]) else None,
        schedule.set_index("EventName").to_dict(orient="index"),
        *last_round_numbers,
    )


@callback(
    Output("session", "options"),
    Output("session", "value"),
    Input("event", "value"),
    State("session", "value"),
    State("event-schedule", "data"),
    State("last-race-round", "data"),
    State("last-sprint-round", "data"),
    prevent_initial_call=True,
)
def set_session_options(
    event: str | None,
    old_session: str | None,
    schedule: dict,
    last_race_round: int,
    last_sprint_round: int,
) -> tuple[list[dict], str | None]:
    """
    Return the sessions contained in an event.

    Event schedule is passed in as a dictionary with the event names as keys.
    The values map column labels to the corresponding entry.
    """
    if event is None:
        return [], None
    round_number = schedule[event]["RoundNumber"]
    race_disabled = round_number > last_race_round
    sprint_disabled = (schedule[event]["EventFormat"] not in SPRINT_FORMATS) or (
        round_number > last_sprint_round
    )
    session_options = [
        {
            "label": "Race",
            "value": "R",
            "disabled": race_disabled,
        },
        {
            "label": "Sprint",
            "value": "S",
            "disabled": sprint_disabled,
        },
    ]

    session_value = old_session

    # Auto fill session value if there is only one available option
    if race_disabled and not sprint_disabled:
        session_value = "S"
    elif sprint_disabled and not race_disabled:
        session_value = "R"
    elif race_disabled and sprint_disabled:
        session_value = None

    return session_options, session_value


@callback(
    Output("load-session", "disabled"),
    Input("season", "value"),
    Input("event", "value"),
    Input("session", "value"),
    prevent_initial_call=True,
)
def enable_load_session(
    season: int | None, event: str | None, session_name: str | None
) -> bool:
    """Toggle load session button on when the previous three fields are filled."""
    return not (season is not None and event is not None and session_name is not None)
