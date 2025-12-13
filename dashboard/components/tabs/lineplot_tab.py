"""Lineplot tab component."""

import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard.components.tabs.common import lap_numbers_slider, upper_bound_slider
from dashboard.components.tabs.scatterplot_tab import scatter_y_options


line_y_options = [{"label": "Position", "value": "Position"}, *scatter_y_options]


lineplot_tab = dbc.Tab(
    dbc.Card(
        dbc.CardBody([
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            options=line_y_options,
                            value="Position",
                            placeholder="Select the variable to put in y-axis",
                            clearable=False,
                            id="line-y",
                        ),
                        width=9,
                    ),
                    dbc.Col(
                        dbc.Checklist(
                            options=[
                                {
                                    "label": "Show starting positions",
                                    "value": 1,
                                    "disabled": False,
                                }
                            ],
                            value=[],
                            id="show-starting-grid",
                            inline=True,
                            switch=True,
                        ),
                        width=3,
                    ),
                ],
            ),
            html.Br(),
            dbc.Row(dcc.Loading(dcc.Graph(id="lineplot"))),
            html.Br(),
            html.P("Filter out slow laps (default is 107% of the fastest lap):"),
            dbc.Row(upper_bound_slider(slider_id="upper-bound-line")),
            html.Br(),
            html.P("Select the range of lap numbers to include:"),
            dbc.Row(lap_numbers_slider(slider_id="lap-numbers-line")),
        ])
    ),
    label="Stats Lineplot",
)
