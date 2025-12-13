"""Session picker component."""

import dash_bootstrap_components as dbc
from dash import dcc


session_picker_row = dbc.Row(
    [
        dbc.Col(
            dcc.Dropdown(
                options=[],
                placeholder="Select a season",
                value=None,
                id="season",
            )
        ),
        dbc.Col(
            dcc.Dropdown(
                options=[],
                placeholder="Select a event",
                value=None,
                id="event",
            ),
        ),
        dbc.Col(
            dcc.Dropdown(
                options=[],
                placeholder="Select a session",
                value=None,
                id="session",
            ),
        ),
        dbc.Col(
            dcc.Dropdown(
                options=[
                    {"label": "Finishing order", "value": False},
                    {"label": "Teammate side-by-side", "value": True},
                ],
                value=False,
                clearable=False,
                id="teammate-comp",
            )
        ),
        dbc.Col(
            dbc.Button(
                children="Load Session / Reorder Drivers",
                n_clicks=0,
                disabled=True,
                color="success",
                id="load-session",
            )
        ),
    ],
)
