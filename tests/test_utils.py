"""Tests for dashboard utility functions."""

import pandas as pd
import pytest

from dashboard.utils import (
    add_gap,
    configure_lap_numbers_slider,
    style_compound_options,
)


class TestConfigureLapNumbersSlider:
    """Tests for configure_lap_numbers_slider function."""

    def test_empty_data_returns_defaults(self):
        """Empty data should return default slider config."""
        max_val, value, marks = configure_lap_numbers_slider({})
        
        assert max_val == 60
        assert value == [1, 60]
        assert 1 in marks
        assert 60 in marks

    def test_valid_data_returns_correct_config(self):
        """Valid data should configure slider based on lap count."""
        data = {"LapNumber": {0: 1, 1: 2, 2: 50}}
        max_val, value, marks = configure_lap_numbers_slider(data)
        
        assert max_val == 50
        assert value == [1, 50]
        assert 1 in marks
        assert 50 in marks


class TestStyleCompoundOptions:
    """Tests for style_compound_options function."""

    def test_valid_compounds_sorted_correctly(self):
        """Compounds should be sorted from SOFT to HARD."""
        compounds = ["HARD", "SOFT", "MEDIUM"]
        result = style_compound_options(compounds)
        
        # Should be sorted: SOFT, MEDIUM, HARD
        values = [opt["value"] for opt in result]
        assert values == ["SOFT", "MEDIUM", "HARD"]

    def test_unknown_compounds_filtered(self):
        """Unknown compounds should be filtered out."""
        compounds = ["SOFT", "UNKNOWN_COMPOUND"]
        result = style_compound_options(compounds)
        
        values = [opt["value"] for opt in result]
        assert "UNKNOWN_COMPOUND" not in values
        assert "SOFT" in values

    def test_empty_compounds_returns_empty(self):
        """Empty input should return empty list."""
        result = style_compound_options([])
        assert result == []


class TestAddGap:
    """Tests for add_gap function."""

    def test_add_gap_creates_column(self, sample_laps_df):
        """add_gap should create GapTo{driver} column."""
        result = add_gap("VER", sample_laps_df)
        
        assert "GapToVER" in result.columns
        # Gap to self should be 0
        ver_gaps = result[result["Driver"] == "VER"]["GapToVER"]
        assert (ver_gaps == 0).all()

    def test_add_gap_preserves_original_columns(self, sample_laps_df):
        """add_gap should not remove original columns."""
        original_cols = set(sample_laps_df.columns)
        result = add_gap("VER", sample_laps_df)
        
        for col in original_cols:
            assert col in result.columns
