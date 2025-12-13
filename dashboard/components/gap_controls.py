"""Gap calculation controls component."""

import dash_bootstrap_components as dbc
from dash import dcc, html


add_gap_row = dbc.Row(
    dbc.Card([
        dbc.CardHeader("Calculate gaps between drivers"),
        dbc.CardBody([
            dbc.Row(
                dcc.Dropdown(
                    options=[],
                    value=[],
                    placeholder="Select drivers",
                    disabled=True,
                    multi=True,
                    id="gap-drivers",
                )
            ),
            html.Br(),
            dbc.Row(
                dbc.Col(
                    dbc.Button(
                        "Add Gap",
                        color="success",
                        disabled=True,
                        n_clicks=0,
                        id="add-gap",
                    ),
                )
            ),
        ]),
    ])
)
