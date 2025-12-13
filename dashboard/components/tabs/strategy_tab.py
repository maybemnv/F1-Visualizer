"""Strategy tab component."""

import dash_bootstrap_components as dbc
from dash import dcc


strategy_tab = dbc.Tab(
    dbc.Card(dbc.CardBody(dcc.Loading(dcc.Graph(id="strategy-plot")))),
    label="Strategy",
)
