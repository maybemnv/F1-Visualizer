"""Legends tab component."""

import dash_bootstrap_components as dbc
from dash import html

from dashboard.components.legends import compound_color_scheme_card, fresh_used_scheme_card


legends_tab = dbc.Tab(
    [compound_color_scheme_card, html.Br(), fresh_used_scheme_card],
    label="Graph Legends",
)
