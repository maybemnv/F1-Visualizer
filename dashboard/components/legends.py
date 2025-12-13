"""Legend and color scheme components."""

import dash_bootstrap_components as dbc
from dash import html


compound_color_scheme_card = dbc.Card(
    [
        dbc.CardHeader(html.B("Compounds Color Scheme"), style={"textAlign": "center"}),
        dbc.ListGroup(
            [
                dbc.ListGroupItem(
                    html.B("SOFT"),
                    color="#da291c",
                    style={"textAlign": "center"},
                ),
                dbc.ListGroupItem(
                    html.B("MEDIUM"),
                    color="#ffd12e",
                    style={"textAlign": "center"},
                ),
                dbc.ListGroupItem(
                    html.B("HARD"),
                    color="#f0f0ec",
                    style={"textAlign": "center"},
                ),
                dbc.ListGroupItem(
                    html.B("INTERMEDIATE"),
                    color="#43b02a",
                    style={"textAlign": "center"},
                ),
                dbc.ListGroupItem(
                    html.B("WET"),
                    color="#0067ad",
                    style={"textAlign": "center"},
                ),
                dbc.ListGroupItem(
                    html.B("UNKNOWN"),
                    color="#00ffff",
                    style={"textAlign": "center"},
                ),
            ],
        ),
    ],
)


fresh_used_scheme_card = dbc.Card([
    dbc.Accordion(
        [
            dbc.AccordionItem(
                dbc.Progress(
                    value=100,
                    color="warning",
                    style={"height": "40px"},
                ),
                title="Fresh Tyre Bar",
            ),
            dbc.AccordionItem(
                html.P("⚫", style={"textAlign": "center"}),
                title="Fresh Tyre Marker",
            ),
            dbc.AccordionItem(
                dbc.Progress(
                    value=100,
                    color="warning",
                    striped=True,
                    style={"height": "40px"},
                ),
                title="Used Tyre Bar (Striped)",
            ),
            dbc.AccordionItem(
                html.P(html.B("X"), style={"textAlign": "center"}),
                title="Used Tyre Marker",
            ),
        ],
        start_collapsed=True,
        always_open=True,
    ),
])


external_links = dbc.Alert(
    [
        "Made by ",
        html.A(
            "Manav",
            href="https://portfolio-manavs-projects-1f5448b0.vercel.app/",
            className="alert-link",
        ),
        " ✌️",
        html.Hr(),
        "All data provided by ",
        html.A(
            "FastF1",
            href="https://github.com/theOehrly/Fast-F1",
            className="alert-link",
        ),
        html.Hr(),
        "Feature requests and bug reports etc. are welcome at the ",
        html.A(
            "source repository",
            href="https://github.com/maybemnv/F1-Visualizer",
            className="alert-link",
        ),
    ],
    color="info",
)
