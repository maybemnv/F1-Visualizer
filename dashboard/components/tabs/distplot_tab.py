"""Distribution plot tab component."""

import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard.components.tabs.common import upper_bound_slider


distplot_caveat = dbc.Alert(
    [
        html.H4("Caveats", className="alert-heading"),
        html.P(
            "Only drivers who have completed more than 5 laps are shown. "
            "Try adjusting the slow lap filter if no plot is shown."
        ),
    ],
    color="info",
    dismissable=True,
)


distplot_tab = dbc.Tab(
    dbc.Card(
        dbc.CardBody([
            distplot_caveat,
            html.Br(),
            dbc.Row(
                dcc.Dropdown(
                    options=[
                        {"label": " Show boxplot", "value": True},
                        {"label": " Show violin plot", "value": False},
                    ],
                    value=True,
                    clearable=False,
                    id="boxplot",
                )
            ),
            html.Br(),
            dbc.Row(dcc.Loading(dcc.Graph(id="distplot"))),
            html.Br(),
            html.P("Filter out slow laps (default is 107% of the fastest lap):"),
            dbc.Row(upper_bound_slider(slider_id="upper-bound-dist")),
        ])
    ),
    label="Lap Time Distribution Plot",
)
