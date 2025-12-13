"""Analysis tab component for ML-based driver performance analysis."""

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_analysis_tab() -> dbc.Tab:
    """Create the Analysis tab with ML visualizations."""
    return dbc.Tab(
        label="Analysis",
        tab_id="analysis-tab",
        children=[
            dbc.Container(
                [
                    # Header
                    dbc.Row(
                        dbc.Col(
                            html.H4(
                                "ML Driver Performance Analysis",
                                className="text-center my-3",
                            )
                        )
                    ),
                    # Controls row
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Analysis Type"),
                                    dcc.Dropdown(
                                        id="analysis-type-dropdown",
                                        options=[
                                            {"label": "Driving Style Clusters", "value": "clustering"},
                                            {"label": "Performance Anomalies", "value": "anomaly"},
                                            {"label": "Driver Rankings", "value": "ranking"},
                                        ],
                                        value="clustering",
                                        clearable=False,
                                    ),
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Number of Clusters"),
                                    dcc.Slider(
                                        id="n-clusters-slider",
                                        min=2,
                                        max=6,
                                        step=1,
                                        value=4,
                                        marks={i: str(i) for i in range(2, 7)},
                                    ),
                                ],
                                md=4,
                                id="clusters-control",
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Anomaly Sensitivity"),
                                    dcc.Slider(
                                        id="anomaly-sensitivity-slider",
                                        min=0.05,
                                        max=0.3,
                                        step=0.05,
                                        value=0.1,
                                        marks={0.05: "Low", 0.15: "Med", 0.3: "High"},
                                    ),
                                ],
                                md=4,
                                id="anomaly-control",
                                style={"display": "none"},
                            ),
                        ],
                        className="mb-4",
                    ),
                    # Run analysis button
                    dbc.Row(
                        dbc.Col(
                            dbc.Button(
                                "Run Analysis",
                                id="run-analysis-btn",
                                color="primary",
                                className="mb-3",
                            ),
                            width="auto",
                        ),
                        justify="center",
                    ),
                    # Loading spinner
                    dcc.Loading(
                        id="analysis-loading",
                        type="circle",
                        children=[
                            # Main visualization
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Graph(
                                            id="analysis-main-graph",
                                            style={"height": "500px"},
                                        ),
                                        md=8,
                                    ),
                                    dbc.Col(
                                        html.Div(id="analysis-summary-card"),
                                        md=4,
                                    ),
                                ],
                                className="mb-4",
                            ),
                            # Results table
                            dbc.Row(
                                dbc.Col(
                                    html.Div(id="analysis-results-table"),
                                    width=12,
                                )
                            ),
                        ],
                    ),
                ],
                fluid=True,
                className="p-3",
            )
        ],
    )


def create_cluster_summary_card(cluster_summary: dict) -> dbc.Card:
    """Create summary card for clustering results."""
    items = []
    for cluster_id, info in cluster_summary.items():
        items.append(
            dbc.ListGroupItem(
                [
                    html.Strong(f"Cluster {cluster_id}: "),
                    html.Span(info.get("style", "Unknown")),
                ],
                color="light",
            )
        )

    return dbc.Card(
        [
            dbc.CardHeader("Driving Styles"),
            dbc.CardBody(dbc.ListGroup(items)),
        ]
    )


def create_ranking_table(rankings: list) -> dbc.Table:
    """Create table for driver rankings."""
    header = html.Thead(
        html.Tr([
            html.Th("Rank"),
            html.Th("Driver"),
            html.Th("Score"),
            html.Th("Avg Position"),
            html.Th("Consistency"),
            html.Th("Races"),
        ])
    )

    rows = []
    for r in rankings[:20]:  # Top 20
        rows.append(
            html.Tr([
                html.Td(r.rank),
                html.Td(html.Strong(r.driver)),
                html.Td(f"{r.score:.2f}"),
                html.Td(f"{r.avg_position:.1f}"),
                html.Td(f"{r.consistency:.1f}%"),
                html.Td(r.races_completed),
            ])
        )

    return dbc.Table(
        [header, html.Tbody(rows)],
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
    )


def create_anomaly_list(anomalies: list) -> html.Div:
    """Create list of detected anomalies."""
    items = []
    for a in anomalies[:15]:  # Top 15 anomalies
        color = "danger" if "Slow" in a.anomaly_type.value else "warning"
        if "Fast" in a.anomaly_type.value:
            color = "success"

        items.append(
            dbc.Alert(
                [
                    html.Strong(f"{a.driver} - Lap {a.lap_number}: "),
                    html.Span(a.anomaly_type.value),
                    html.Br(),
                    html.Small(f"Score: {a.anomaly_score:.2f}"),
                ],
                color=color,
                className="mb-2 py-2",
            )
        )

    if not items:
        return html.Div(
            dbc.Alert("No anomalies detected", color="info"),
        )

    return html.Div(items)


# Export the main component
analysis_tab = create_analysis_tab()
