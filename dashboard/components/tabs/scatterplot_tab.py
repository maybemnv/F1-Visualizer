"""Scatterplot tab component."""

import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard.components.tabs.common import lap_numbers_slider, upper_bound_slider


scatter_y_options = [
    {"label": "Lap Time", "value": "LapTime"},
    {"label": "Seconds to Same Condition (Dry/Wet) Median", "value": "DeltaToRep"},
    {"label": "Percent from Same Condition (Dry/Wet) Median", "value": "PctFromRep"},
    {"label": "Seconds to Fastest", "value": "DeltaToFastest"},
    {"label": "Percent from Fastest", "value": "PctFromFastest"},
    {"label": "Seconds to Same Lap Median", "value": "DeltaToLapRep"},
    {"label": "Percent from Same Lap Median", "value": "PctFromLapRep"},
    {"label": "Fuel-Adjusted Lap Time", "value": "FuelAdjLapTime"},
]


scatterplot_tab = dbc.Tab(
    dbc.Card(
        dbc.CardBody([
            dbc.Row(
                dcc.Dropdown(
                    options=scatter_y_options,
                    value="LapTime",
                    placeholder="Select the variable to put in y-axis",
                    clearable=False,
                    id="scatter-y",
                )
            ),
            html.Br(),
            dbc.Row(dcc.Loading(dcc.Graph(id="scatterplot"))),
            html.Br(),
            html.P("Filter out slow laps (default is 107% of the fastest lap):"),
            dbc.Row(upper_bound_slider(slider_id="upper-bound-scatter")),
            html.Br(),
            html.P("Select the range of lap numbers to include:"),
            dbc.Row(lap_numbers_slider(slider_id="lap-numbers-scatter")),
        ])
    ),
    label="Stats Scatterplot",
)
