"""Compound performance plot tab component."""

import dash_bootstrap_components as dbc
from dash import dcc, html


compound_plot_explanation = dbc.Alert(
    [
        html.H4("Methodology", className="alert-heading"),
        html.P(
            "The metric behind this graph is delta to lap representative time (DLRT). "
            "It is a measure of how good a lap time is compared to other cars on track "
            "at the same time, thus accounting for fuel load and track evolution."
        ),
        html.Hr(),
        html.P(
            "Since this metric is relative, this plot is best used for understanding "
            "how different compounds degrade at different rates."
        ),
    ],
    color="info",
    dismissable=True,
)


compound_plot_caveats = dbc.Alert(
    [
        html.H4("Caveats", className="alert-heading"),
        html.P(
            "The driver selections does not apply to this plot. "
            "This plot always considers laps driven by all drivers."
        ),
        html.Hr(),
        html.P(
            "Tyre life does not always correspond to stint length. "
            "As the same tyre may have been used in qualifying sessions."
        ),
        html.Hr(),
        html.P(
            "Only compounds that completed at least 5% of all laps can be shown. "
            "Outlier laps are filtered out."
        ),
        html.Hr(),
        html.P(
            "For each compound, the range of shown tyre life is limited by "
            "the number of drivers who completed a stint of that length. This is to avoid "
            "the plot being stretched by one driver doing a very long stint."
        ),
    ],
    color="info",
    dismissable=True,
)


compound_plot_tab = dbc.Tab(
    dbc.Card(
        dbc.CardBody([
            compound_plot_explanation,
            compound_plot_caveats,
            html.Br(),
            dbc.Row(
                dbc.Col(
                    dcc.Dropdown(
                        options=[
                            {"label": "Show delta as seconds", "value": True},
                            {"label": "Show delta as percentages", "value": False},
                        ],
                        value=True,
                        clearable=False,
                        placeholder="Select a unit",
                        id="compound-unit",
                    )
                )
            ),
            html.Br(),
            dbc.Row(
                dcc.Loading(
                    dcc.Dropdown(
                        options=[],
                        value=[],
                        placeholder="Select compounds",
                        disabled=True,
                        multi=True,
                        id="compounds",
                    )
                )
            ),
            html.Br(),
            dbc.Row(dcc.Loading(dcc.Graph(id="compound-plot"))),
        ])
    ),
    label="Compound Performance Plot",
)
