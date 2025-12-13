"""Tests for f1_visualization helper functions."""

import numpy as np
import pandas as pd
import pytest

from f1_visualization.helpers.filters import (
    find_sc_laps,
    remove_low_data_drivers,
    teammate_comp_order,
)


class TestRemoveLowDataDrivers:
    """Tests for remove_low_data_drivers function."""

    def test_removes_drivers_with_few_laps(self, sample_laps_df):
        """Drivers with fewer laps than min_laps should be removed."""
        # Each driver has 3 laps in sample_laps_df
        result = remove_low_data_drivers(sample_laps_df, ("VER", "HAM"), min_laps=5)
        
        assert result == ()

    def test_keeps_drivers_with_enough_laps(self, sample_laps_df):
        """Drivers with enough laps should be kept."""
        result = remove_low_data_drivers(sample_laps_df, ("VER", "HAM"), min_laps=3)
        
        assert "VER" in result
        assert "HAM" in result

    def test_preserves_order(self, sample_laps_df):
        """Order of remaining drivers should be preserved."""
        result = remove_low_data_drivers(sample_laps_df, ("HAM", "VER"), min_laps=2)
        
        assert result == ("HAM", "VER")


class TestFindScLaps:
    """Tests for find_sc_laps function."""

    def test_no_sc_returns_empty_arrays(self, sample_laps_df):
        """No SC periods should return empty arrays."""
        sc_laps, vsc_laps = find_sc_laps(sample_laps_df)
        
        assert len(sc_laps) == 0
        assert len(vsc_laps) == 0

    def test_detects_sc_laps(self):
        """SC laps should be detected correctly."""
        df = pd.DataFrame({
            "TrackStatus": ["1", "4", "4", "1"],
            "LapNumber": [1, 2, 3, 4],
            "Position": [1, 1, 1, 1]
        })
        
        sc_laps, vsc_laps = find_sc_laps(df)
        
        assert 2 in sc_laps
        assert 3 in sc_laps

    def test_detects_vsc_laps(self):
        """VSC laps should be detected correctly."""
        df = pd.DataFrame({
            "TrackStatus": ["1", "6", "7", "1"],
            "LapNumber": [1, 2, 3, 4],
            "Position": [1, 1, 1, 1]
        })
        
        sc_laps, vsc_laps = find_sc_laps(df)
        
        assert 2 in vsc_laps
        assert 3 in vsc_laps


class TestTeammateCompOrder:
    """Tests for teammate_comp_order function."""

    def test_orders_by_performance_gap(self, sample_laps_df):
        """Teammates should be ordered by performance gap."""
        # VER is faster than HAM in the sample data
        result = teammate_comp_order(sample_laps_df, ("VER", "HAM"), by="LapTime")
        
        # Faster driver should be first in pair
        assert result[0] == "VER"

    def test_handles_single_driver(self, sample_laps_df):
        """Single driver should be handled correctly."""
        result = teammate_comp_order(sample_laps_df, ("VER",), by="LapTime")
        
        assert result == ("VER",)
