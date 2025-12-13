"""Tests for dashboard graph generation functions."""

import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

# Note: These tests use mocking to avoid requiring actual F1 data


class TestStrategyBarplot:
    """Tests for strategy_barplot function."""

    def test_returns_figure_type(self, sample_laps_df):
        """strategy_barplot should return a Plotly figure."""
        from dashboard.graphs import strategy_barplot
        
        fig = strategy_barplot(sample_laps_df, ["VER", "HAM"])
        
        # Check it's a plotly figure
        assert hasattr(fig, 'update_layout')
        assert hasattr(fig, 'data')

    def test_creates_traces_for_each_driver(self, sample_laps_df):
        """Each driver should have traces in the figure."""
        from dashboard.graphs import strategy_barplot
        
        fig = strategy_barplot(sample_laps_df, ["VER", "HAM"])
        
        # Should have at least one trace per driver
        assert len(fig.data) >= 2


class TestStatsScatterplot:
    """Tests for stats_scatterplot function."""

    def test_returns_figure_type(self, sample_laps_df):
        """stats_scatterplot should return a Plotly figure."""
        from dashboard.graphs import stats_scatterplot
        
        fig = stats_scatterplot(sample_laps_df, ["VER"], "LapTime")
        
        assert hasattr(fig, 'update_layout')

    def test_creates_subplot_for_each_driver(self, sample_laps_df):
        """Each driver should have a subplot."""
        from dashboard.graphs import stats_scatterplot
        
        fig = stats_scatterplot(sample_laps_df, ["VER", "HAM"], "LapTime")
        
        # Check that figure has multiple subplots
        assert len(fig.data) >= 2


class TestStatsLineplot:
    """Tests for stats_lineplot function."""

    def test_returns_figure_type(self, sample_laps_df):
        """stats_lineplot should return a Plotly figure."""
        from dashboard.graphs import stats_lineplot
        
        # Create mock session
        mock_session = MagicMock()
        mock_session.results = pd.DataFrame({
            "Abbreviation": ["VER", "HAM"],
            "GridPosition": [1, 2]
        })
        
        with patch('dashboard.graphs.find_sc_laps', return_value=([], [])):
            with patch('dashboard.graphs.get_driver_style', return_value={"color": "red", "dash": "solid"}):
                fig = stats_lineplot(
                    sample_laps_df,
                    ["VER"],
                    "Position",
                    107,
                    mock_session,
                    {}
                )
        
        assert hasattr(fig, 'update_layout')


class TestCompoundsLineplot:
    """Tests for compounds_lineplot function."""

    def test_returns_figure_type(self, sample_laps_df):
        """compounds_lineplot should return a Plotly figure."""
        from dashboard.graphs import compounds_lineplot
        
        fig = compounds_lineplot(sample_laps_df, "DeltaToLapRep", ["SOFT", "MEDIUM"])
        
        assert hasattr(fig, 'update_layout')
