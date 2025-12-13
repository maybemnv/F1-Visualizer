"""Plot rendering callbacks."""

from typing import TypeAlias

import fastf1 as f
import pandas as pd
from dash import Input, Output, State, callback
from plotly import graph_objects as go

import dashboard.graphs as pg
from dashboard.constants import MIN_LAPS_FOR_DISTPLOT
from f1_visualization.visualization import remove_low_data_drivers, teammate_comp_order

# Type alias for session info tuple
Session_info: TypeAlias = tuple[int, int, str, str, list[str], dict[str, int]]


@callback(
    Output("strategy-plot", "figure"),
    Input("drivers", "value"),
    Input("laps-data-sequencer", "children"),
    State("laps", "data"),
    State("session-info", "data"),
)
def render_strategy_plot(
    drivers: list[str], _: str, included_laps: dict, session_info: Session_info
) -> go.Figure:
    """Filter laps and configure strategy plot title."""
    if not included_laps or not drivers:
        return go.Figure()

    included_laps = pd.DataFrame.from_dict(included_laps)
    included_laps = included_laps[included_laps["Driver"].isin(drivers)]

    event_name = session_info[3]
    fig = pg.strategy_barplot(included_laps, drivers)
    fig.update_layout(title=event_name)
    return fig


@callback(
    Output("scatterplot", "figure"),
    Input("drivers", "value"),
    Input("scatter-y", "value"),
    Input("upper-bound-scatter", "value"),
    Input("lap-numbers-scatter", "value"),
    State("laps", "data"),
    State("session-info", "data"),
    State("teammate-comp", "value"),
)
def render_scatterplot(
    drivers: list[str],
    y: str,
    upper_bound: float,
    lap_numbers: list[int],
    included_laps: dict,
    session_info: Session_info,
    teammate_comp: bool,
) -> go.Figure:
    """Filter laps and configure scatterplot title."""
    if not included_laps or not drivers:
        return go.Figure()

    minimum, maximum = lap_numbers
    lap_interval = range(minimum, maximum + 1)
    included_laps = pd.DataFrame.from_dict(included_laps)
    included_laps = included_laps[
        (included_laps["Driver"].isin(drivers))
        & (included_laps["PctFromFastest"] < (upper_bound - 100))
        & (included_laps["LapNumber"].isin(lap_interval))
    ]

    if teammate_comp:
        drivers = teammate_comp_order(included_laps, drivers, y)

    fig = pg.stats_scatterplot(included_laps, drivers, y)
    event_name = session_info[3]
    fig.update_layout(title=event_name)

    return fig


@callback(
    Output("lineplot", "figure"),
    Input("drivers", "value"),
    Input("line-y", "value"),
    Input("upper-bound-line", "value"),
    Input("lap-numbers-line", "value"),
    Input("show-starting-grid", "value"),
    State("laps", "data"),
    State("session-info", "data"),
)
def render_lineplot(
    drivers: list[str],
    y: str,
    upper_bound: float,
    lap_numbers: list[int],
    starting_grid: list,
    included_laps: dict,
    session_info: Session_info,
) -> go.Figure:
    """Filter laps and configure lineplot title."""
    if not included_laps or not drivers:
        return go.Figure()

    minimum, maximum = lap_numbers
    lap_interval = range(minimum, maximum + 1)
    included_laps = pd.DataFrame.from_dict(included_laps)

    # Upper bound not filtered here because we need to identify SC/VSC laps
    included_laps = included_laps[
        (included_laps["Driver"].isin(drivers))
        & (included_laps["LapNumber"].isin(lap_interval))
    ]

    fig = pg.stats_lineplot(
        included_laps,
        drivers,
        y,
        upper_bound,
        f.get_session(*session_info[:3]),
        session_info[5] if starting_grid else {},
    )
    event_name = session_info[3]
    fig.update_layout(title=event_name)

    return fig


@callback(
    Output("distplot", "figure"),
    Input("drivers", "value"),
    Input("upper-bound-dist", "value"),
    Input("boxplot", "value"),
    Input("laps-data-sequencer", "children"),
    State("laps", "data"),
    State("session-info", "data"),
    State("teammate-comp", "value"),
)
def render_distplot(
    drivers: list[str],
    upper_bound: int,
    boxplot: bool,
    _: str,
    included_laps: dict,
    session_info: Session_info,
    teammate_comp: bool,
) -> go.Figure:
    """Filter laps and render distribution plot."""
    if not included_laps or not drivers:
        return go.Figure()

    included_laps = pd.DataFrame.from_dict(included_laps)
    included_laps = included_laps[
        (included_laps["Driver"].isin(drivers))
        & (included_laps["PctFromFastest"] < (upper_bound - 100))
    ]

    if teammate_comp:
        drivers = teammate_comp_order(included_laps, drivers, by="LapTime")
    drivers = remove_low_data_drivers(included_laps, drivers, MIN_LAPS_FOR_DISTPLOT)

    fig = pg.stats_distplot(included_laps, drivers, boxplot, f.get_session(*session_info[:3]))
    event_name = session_info[3]
    fig.update_layout(title=event_name)

    return fig


@callback(
    Output("compound-plot", "figure"),
    Input("compounds", "value"),
    Input("compound-unit", "value"),
    State("laps", "data"),
    State("session-info", "data"),
)
def render_compound_plot(
    compounds: list[str],
    show_seconds: bool,
    included_laps: dict,
    session_info: Session_info,
) -> go.Figure:
    """Filter laps and render compound performance plot."""
    if not included_laps or not compounds:
        return go.Figure()

    included_laps = pd.DataFrame.from_dict(included_laps)

    # TyreLife = 1 rows seem to always be outliers relative to the representative lap time
    included_laps = included_laps[
        (included_laps["Compound"].isin(compounds)) & (included_laps["TyreLife"] != 1)
    ]

    y = "DeltaToLapRep" if show_seconds else "PctFromLapRep"
    fig = pg.compounds_lineplot(included_laps, y, compounds)
    event_name = session_info[3]
    fig.update_layout(title=event_name)
    return fig
