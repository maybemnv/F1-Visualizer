"""Pytest fixtures and common test utilities."""

import pandas as pd
import pytest


@pytest.fixture
def sample_laps_df() -> pd.DataFrame:
    """Create a sample laps DataFrame for testing."""
    return pd.DataFrame({
        "Driver": ["VER", "VER", "VER", "HAM", "HAM", "HAM"],
        "LapNumber": [1, 2, 3, 1, 2, 3],
        "LapTime": [95.5, 94.2, 94.1, 96.0, 94.5, 94.3],
        "Time": pd.to_timedelta(["0:01:35.5", "0:03:09.7", "0:04:43.8", 
                                  "0:01:36.0", "0:03:10.5", "0:04:44.8"]),
        "PitInTime": [pd.NaT, pd.NaT, pd.NaT, pd.NaT, pd.NaT, pd.NaT],
        "PitOutTime": [pd.NaT, pd.NaT, pd.NaT, pd.NaT, pd.NaT, pd.NaT],
        "Compound": ["SOFT", "SOFT", "SOFT", "MEDIUM", "MEDIUM", "MEDIUM"],
        "CompoundName": ["C5", "C5", "C5", "C4", "C4", "C4"],
        "Stint": [1, 1, 1, 1, 1, 1],
        "TyreLife": [1, 2, 3, 1, 2, 3],
        "FreshTyre": ["True", "True", "True", "True", "True", "True"],
        "Position": [1, 1, 1, 2, 2, 2],
        "TrackStatus": ["1", "1", "1", "1", "1", "1"],
        "IsSlick": [True, True, True, True, True, True],
        "IsAccurate": [True, True, True, True, True, True],
        "IsValid": [True, True, True, True, True, True],
        "RoundNumber": [1, 1, 1, 1, 1, 1],
        "EventName": ["Bahrain Grand Prix", "Bahrain Grand Prix", "Bahrain Grand Prix",
                      "Bahrain Grand Prix", "Bahrain Grand Prix", "Bahrain Grand Prix"],
        "PctFromFastest": [0.0, 0.0, 0.0, 0.5, 0.3, 0.2],
        "PctFromLapRep": [0.0, 0.0, 0.0, 0.5, 0.3, 0.2],
        "DeltaToLapRep": [0.0, 0.0, 0.0, 0.5, 0.3, 0.2],
    })


@pytest.fixture
def sample_session_info():
    """Create sample session info tuple."""
    return (2024, 1, "R", "2024 Bahrain Grand Prix - Race", ["VER", "HAM", "LEC"], {})


@pytest.fixture
def sample_compounds_list():
    """Sample compound options list."""
    return ["SOFT", "MEDIUM", "HARD"]
