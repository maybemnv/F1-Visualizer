"""Dash app layout - enhanced UI with professional styling."""

import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard.components import add_gap_row, external_links, session_picker_row
from dashboard.components.tabs import (
    analysis_tab,
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

# Store for session data (used by analysis callbacks)
session_data_store = dcc.Store(id="session-data", data={})

# Header with logo and title
header = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Img(
                            src="/assets/logos/white_filled.svg",
                            height="40px",
                            className="me-2",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.NavbarBrand(
                            "F1 Visualizer",
                            className="fs-4 fw-bold",
                        ),
                        width="auto",
                    ),
                ],
                align="center",
                className="g-0",
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavItem(
                            dbc.NavLink(
                                "Dashboard",
                                href="#",
                                active=True,
                            )
                        ),
                        dbc.NavItem(
                            dbc.NavLink(
                                "Documentation",
                                href="https://github.com/maybemnv/F1-Visualizer",
                                target="_blank",
                            )
                        ),
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ],
        fluid=True,
    ),
    color="dark",
    dark=True,
    className="mb-4",
    sticky="top",
)

# Session controls card
session_controls = dbc.Card(
    [
        dbc.CardHeader(
            html.H5("Session Selection", className="mb-0"),
            className="bg-primary text-white",
        ),
        dbc.CardBody(
            [
                session_picker_row,
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Drivers", className="fw-semibold"),
                                dcc.Loading(
                                    dcc.Dropdown(
                                        options=[],
                                        value=[],
                                        placeholder="Select drivers",
                                        disabled=True,
                                        multi=True,
                                        id="drivers",
                                    ),
                                    type="circle",
                                ),
                            ],
                            md=8,
                        ),
                        dbc.Col(
                            add_gap_row,
                            md=4,
                        ),
                    ],
                    className="mt-3",
                ),
            ]
        ),
    ],
    className="mb-4 shadow-sm",
)

# Main visualization tabs with improved styling
visualization_tabs = dbc.Card(
    [
        dbc.CardBody(
            dbc.Tabs(
                [
                    strategy_tab,
                    scatterplot_tab,
                    lineplot_tab,
                    distplot_tab,
                    compound_plot_tab,
                    analysis_tab,
                    legends_tab,
                ],
                id="main-tabs",
                active_tab="strategy-tab",
                className="nav-fill",
            ),
            className="p-0",
        ),
    ],
    className="shadow-sm",
)

# Footer with F1 styling
footer = html.Footer(
    dbc.Container(
        [
            # Gradient divider (CSS handles the animation)
            html.Div(className="racing-stripe"),
            dbc.Row(
                [
                    # Brand and description
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.Img(
                                        src="/assets/logos/white_filled.svg",
                                        height="30px",
                                        className="me-2",
                                    ),
                                    html.Span(
                                        "F1 Visualizer",
                                        className="fw-bold",
                                    ),
                                ],
                                className="d-flex align-items-center mb-2",
                            ),
                            html.P(
                                "Interactive Formula 1 race data visualization and analysis platform.",
                                className="text-muted small mb-0",
                            ),
                        ],
                        md=4,
                        className="mb-3 mb-md-0",
                    ),
                    # Quick links
                    dbc.Col(
                        [
                            html.H6("Resources", className="fw-bold mb-2"),
                            html.Ul(
                                [
                                    html.Li(
                                        html.A(
                                            "Documentation",
                                            href="https://github.com/maybemnv/F1-Visualizer",
                                            target="_blank",
                                        )
                                    ),
                                    html.Li(
                                        html.A(
                                            "FastF1 Library",
                                            href="https://github.com/theOehrly/Fast-F1",
                                            target="_blank",
                                        )
                                    ),
                                    html.Li(
                                        html.A(
                                            "Data Schema",
                                            href="https://github.com/maybemnv/F1-Visualizer/blob/master/SCHEMA.md",
                                            target="_blank",
                                        )
                                    ),
                                ],
                                className="list-unstyled small",
                            ),
                        ],
                        md=3,
                        className="mb-3 mb-md-0",
                    ),
                    # Social links
                    dbc.Col(
                        [
                            html.H6("Connect", className="fw-bold mb-2"),
                            html.Div(
                                [
                                    html.A(
                                        html.I(className="fab fa-github"),
                                        href="https://github.com/maybemnv/F1-Visualizer",
                                        target="_blank",
                                        className="social-icon",
                                        title="GitHub",
                                    ),
                                    html.A(
                                        html.I(className="fab fa-linkedin"),
                                        href="https://linkedin.com/in/maybemnv",
                                        target="_blank",
                                        className="social-icon",
                                        title="LinkedIn",
                                    ),
                                ],
                            ),
                        ],
                        md=2,
                    ),
                    # Data source attribution
                    dbc.Col(
                        [
                            html.P(
                                [
                                    "Data sourced from ",
                                    html.A(
                                        "FastF1",
                                        href="https://github.com/theOehrly/Fast-F1",
                                        target="_blank",
                                    ),
                                ],
                                className="text-muted small mb-1",
                            ),
                            html.P(
                                "Not affiliated with Formula 1 or FIA",
                                className="text-muted small mb-0",
                            ),
                        ],
                        md=3,
                        className="text-md-end",
                    ),
                ],
                align="start",
                className="py-4",
            ),
            # Bottom bar
            html.Hr(className="my-0"),
            dbc.Row(
                dbc.Col(
                    html.P(
                        "Built with Dash, Plotly, and scikit-learn",
                        className="text-center text-muted small py-2 mb-0",
                    ),
                ),
            ),
        ],
        fluid=True,
    ),
)

# Hidden stores and sequencer
stores = html.Div(
    [
        dcc.Store(id="event-schedule"),
        dcc.Store(id="session-info"),
        dcc.Store(id="last-race-round"),
        dcc.Store(id="last-sprint-round"),
        dcc.Store(id="laps"),
        session_data_store,
        html.Span(id="laps-data-sequencer", hidden=True),
    ]
)

# Main layout
app_layout = html.Div(
    [
        header,
        dbc.Container(
            [
                session_controls,
                visualization_tabs,
            ],
            fluid=True,
            className="px-4",
        ),
        stores,
        footer,
    ],
    className="min-vh-100 d-flex flex-column",
)
