"""Strategy tab component."""

import dash_bootstrap_components as dbc
from dash import dcc

from dashboard.components.tabs.common import responsive_graph

strategy_tab = dbc.Tab(
    dbc.Card(dbc.CardBody(dcc.Loading(responsive_graph("strategy-plot")))),
    label="Strategy",
)
