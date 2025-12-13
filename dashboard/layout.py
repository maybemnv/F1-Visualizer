"""Dash app layout - slim composition from modular components."""

import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard.components import add_gap_row, external_links, session_picker_row
from dashboard.components.tabs import (
    compound_plot_tab,
    distplot_tab,
    legends_tab,
    line_y_options,
    lineplot_tab,
    scatter_y_options,
    scatterplot_tab,
    strategy_tab,
)

# Re-export y_options for backward compatibility with callbacks
__all__ = ["app_layout", "scatter_y_options", "line_y_options"]


app_layout = dbc.Container([
    html.H1("F1 Visualizer"),
    session_picker_row,
    dcc.Store(id="event-schedule"),
    dcc.Store(id="session-info"),
    dcc.Store(id="last-race-round"),
    dcc.Store(id="last-sprint-round"),
    dcc.Store(id="laps"),
    html.Br(),
    dbc.Row(
        dcc.Loading(
            dcc.Dropdown(
                options=[],
                value=[],
                placeholder="Select drivers",
                disabled=True,
                multi=True,
                id="drivers",
            )
        )
    ),
    html.Br(),
    add_gap_row,
    html.Br(),
    dbc.Tabs([
        strategy_tab,
        scatterplot_tab,
        lineplot_tab,
        distplot_tab,
        compound_plot_tab,
        legends_tab,
    ]),
    html.Br(),
    dbc.Row(external_links),
    # This component exists solely to enforce callback order
    html.Span(id="laps-data-sequencer", hidden=True),
])
