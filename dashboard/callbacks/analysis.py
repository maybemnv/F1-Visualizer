"""Callbacks for ML analysis tab."""

import logging

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, callback, html
from sklearn.decomposition import PCA

from dashboard.components.tabs.analysis_tab import (
    create_anomaly_list,
    create_cluster_summary_card,
    create_ranking_table,
)
from f1_visualization.data_loader import DF_DICT
from f1_visualization.ml import (
    cluster_drivers,
    detect_anomalies,
    extract_season_features,
    rank_drivers,
)

logger = logging.getLogger(__name__)


@callback(
    Output("clusters-control", "style"),
    Output("anomaly-control", "style"),
    Input("analysis-type-dropdown", "value"),
)
def toggle_controls(analysis_type: str) -> tuple[dict, dict]:
    """Show/hide controls based on analysis type."""
    clusters_style = {"display": "block"} if analysis_type == "clustering" else {"display": "none"}
    anomaly_style = {"display": "block"} if analysis_type == "anomaly" else {"display": "none"}
    return clusters_style, anomaly_style


@callback(
    Output("analysis-main-graph", "figure"),
    Output("analysis-summary-card", "children"),
    Output("analysis-results-table", "children"),
    Input("run-analysis-btn", "n_clicks"),
    State("session-data", "data"),
    State("analysis-type-dropdown", "value"),
    State("n-clusters-slider", "value"),
    State("anomaly-sensitivity-slider", "value"),
    prevent_initial_call=True,
)
def run_analysis(
    n_clicks: int,
    session_data: dict | None,
    analysis_type: str,
    n_clusters: int,
    anomaly_sensitivity: float,
) -> tuple[go.Figure, html.Div, html.Div]:
    """Run ML analysis based on selected type."""
    if not session_data:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="Load a session first", showarrow=False)
        return empty_fig, html.Div(), html.Div()

    season = session_data.get("season", 2024)
    session_type = session_data.get("session_type", "R")

    try:
        df_laps = DF_DICT[season][session_type]
    except KeyError:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="Data not available", showarrow=False)
        return empty_fig, html.Div(), html.Div()

    if analysis_type == "clustering":
        return _run_clustering_analysis(df_laps, season, n_clusters)
    elif analysis_type == "anomaly":
        round_number = session_data.get("round_number", 1)
        return _run_anomaly_analysis(df_laps, round_number, anomaly_sensitivity)
    elif analysis_type == "ranking":
        return _run_ranking_analysis(df_laps, season)
    else:
        empty_fig = go.Figure()
        return empty_fig, html.Div(), html.Div()


def _run_clustering_analysis(
    df_laps: pd.DataFrame,
    season: int,
    n_clusters: int,
) -> tuple[go.Figure, html.Div, html.Div]:
    """Run driving style clustering analysis."""
    logger.info("Running clustering analysis for season %d", season)

    features_df = extract_season_features(df_laps, season)

    if features_df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="Insufficient data for clustering", showarrow=False)
        return empty_fig, html.Div(), html.Div()

    # Aggregate per driver
    driver_features = features_df.groupby("driver").agg({
        "median_lap_time": "mean",
        "lap_time_std": "mean",
        "positions_gained": "mean",
        "avg_position": "mean",
        "pct_from_fastest": "mean",
        "consistency_score": "mean",
    }).reset_index()

    # Run clustering
    results, summary = cluster_drivers(driver_features, n_clusters=n_clusters)

    # Create scatter plot with PCA
    feature_cols = ["pct_from_fastest", "consistency_score", "positions_gained"]
    available_cols = [c for c in feature_cols if c in driver_features.columns]

    if len(available_cols) >= 2:  # noqa: PLR2004
        X = driver_features[available_cols].fillna(0).values
        
        if X.shape[1] > 2:  # noqa: PLR2004
            pca = PCA(n_components=2)
            X_2d = pca.fit_transform(X)
        else:
            X_2d = X[:, :2]

        driver_features["PC1"] = X_2d[:, 0]
        driver_features["PC2"] = X_2d[:, 1]
        driver_features["cluster"] = [r.driving_style.value for r in results]

        fig = px.scatter(
            driver_features,
            x="PC1",
            y="PC2",
            color="cluster",
            text="driver",
            title="Driver Clustering by Driving Style",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_traces(textposition="top center", marker={"size": 12})
        fig.update_layout(
            template="plotly_dark",
            showlegend=True,
            legend_title="Driving Style",
        )
    else:
        fig = go.Figure()
        fig.add_annotation(text="Insufficient features", showarrow=False)

    summary_card = create_cluster_summary_card(summary)

    # Results text
    results_text = html.Div([
        html.H5("Driver Assignments"),
        html.Ul([
            html.Li(f"{r.driver}: {r.driving_style.value}")
            for r in sorted(results, key=lambda x: x.driving_style.value)
        ]),
    ])

    return fig, summary_card, results_text


def _run_anomaly_analysis(
    df_laps: pd.DataFrame,
    round_number: int,
    contamination: float,
) -> tuple[go.Figure, html.Div, html.Div]:
    """Run anomaly detection analysis."""
    logger.info("Running anomaly analysis for round %d", round_number)

    round_laps = df_laps[df_laps["RoundNumber"] == round_number].copy()

    if round_laps.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="No data for this round", showarrow=False)
        return empty_fig, html.Div(), html.Div()

    anomalies = detect_anomalies(round_laps, contamination=contamination)

    # Create visualization
    fig = go.Figure()

    # Plot all laps as background
    for driver in round_laps["Driver"].unique():
        driver_laps = round_laps[round_laps["Driver"] == driver]
        fig.add_trace(
            go.Scatter(
                x=driver_laps["LapNumber"],
                y=driver_laps["LapTime"],
                mode="lines",
                name=driver,
                opacity=0.3,
                line={"width": 1},
            )
        )

    # Highlight anomalies
    for a in anomalies:
        color = "red" if "Slow" in a.anomaly_type.value else "yellow"
        if "Fast" in a.anomaly_type.value:
            color = "green"

        lap_data = round_laps[
            (round_laps["Driver"] == a.driver) &
            (round_laps["LapNumber"] == a.lap_number)
        ]
        if not lap_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=[a.lap_number],
                    y=[lap_data["LapTime"].iloc[0]],
                    mode="markers",
                    marker={"size": 15, "color": color, "symbol": "x"},
                    name=f"{a.driver} L{a.lap_number}",
                    showlegend=False,
                    hovertext=f"{a.driver}: {a.anomaly_type.value}",
                )
            )

    fig.update_layout(
        title="Lap Times with Detected Anomalies",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (s)",
        template="plotly_dark",
        showlegend=True,
    )

    summary = html.Div([
        html.H5("Anomaly Summary"),
        html.P(f"Detected: {len(anomalies)} anomalies"),
        html.P(f"Sensitivity: {contamination:.0%}"),
    ])

    results = create_anomaly_list(anomalies)

    return fig, summary, results


def _run_ranking_analysis(
    df_laps: pd.DataFrame,
    season: int,
) -> tuple[go.Figure, html.Div, html.Div]:
    """Run driver ranking analysis."""
    logger.info("Running ranking analysis for season %d", season)

    rankings = rank_drivers(df_laps, season)

    if not rankings:
        empty_fig = go.Figure()
        empty_fig.add_annotation(text="Insufficient data for ranking", showarrow=False)
        return empty_fig, html.Div(), html.Div()

    # Create bar chart
    df_rankings = pd.DataFrame([
        {"driver": r.driver, "score": r.score, "rank": r.rank}
        for r in rankings[:15]
    ])

    fig = px.bar(
        df_rankings,
        x="driver",
        y="score",
        color="score",
        color_continuous_scale="Viridis",
        title=f"{season} ML Driver Rankings",
    )
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Driver",
        yaxis_title="Performance Score",
        showlegend=False,
    )

    summary = html.Div([
        html.H5("Ranking Summary"),
        html.P(f"Season: {season}"),
        html.P(f"Drivers ranked: {len(rankings)}"),
        html.P(f"Top performer: {rankings[0].driver}"),
    ])

    results = create_ranking_table(rankings)

    return fig, summary, results
