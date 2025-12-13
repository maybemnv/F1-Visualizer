"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from f1_visualization.schemas import (
    LapDataSchema,
    SessionInfoSchema,
    TransformedLapSchema,
)


class TestLapDataSchema:
    """Tests for LapDataSchema validation."""

    def test_valid_lap_data(self):
        """Valid lap data should pass validation."""
        data = {
            "Driver": "VER",
            "DriverNumber": 1,
            "LapNumber": 5,
            "LapTime": 95.5,
            "Stint": 1,
            "Compound": "SOFT",
            "TyreLife": 5,
            "FreshTyre": "True",
            "Position": 1,
            "TrackStatus": "1",
            "IsAccurate": True,
            "RoundNumber": 1,
            "EventName": "Bahrain Grand Prix",
        }
        lap = LapDataSchema(**data)
        assert lap.Driver == "VER"
        assert lap.LapNumber == 5

    def test_driver_uppercase_validation(self):
        """Driver abbreviation should be uppercased."""
        data = {
            "Driver": "ver",
            "DriverNumber": 1,
            "LapNumber": 5,
            "Stint": 1,
            "Compound": "SOFT",
            "TyreLife": 5,
            "FreshTyre": "True",
            "TrackStatus": "1",
            "IsAccurate": True,
            "RoundNumber": 1,
            "EventName": "Bahrain Grand Prix",
        }
        lap = LapDataSchema(**data)
        assert lap.Driver == "VER"

    def test_invalid_lap_number(self):
        """Lap number must be >= 1."""
        data = {
            "Driver": "VER",
            "DriverNumber": 1,
            "LapNumber": 0,  # Invalid
            "Stint": 1,
            "Compound": "SOFT",
            "TyreLife": 5,
            "FreshTyre": "True",
            "TrackStatus": "1",
            "IsAccurate": True,
            "RoundNumber": 1,
            "EventName": "Bahrain Grand Prix",
        }
        with pytest.raises(ValidationError):
            LapDataSchema(**data)

    def test_invalid_compound(self):
        """Invalid compound should fail validation."""
        data = {
            "Driver": "VER",
            "DriverNumber": 1,
            "LapNumber": 5,
            "Stint": 1,
            "Compound": "SUPERSOFT",  # Invalid for current schema
            "TyreLife": 5,
            "FreshTyre": "True",
            "TrackStatus": "1",
            "IsAccurate": True,
            "RoundNumber": 1,
            "EventName": "Bahrain Grand Prix",
        }
        with pytest.raises(ValidationError):
            LapDataSchema(**data)

    def test_optional_lap_time(self):
        """LapTime can be None."""
        data = {
            "Driver": "VER",
            "DriverNumber": 1,
            "LapNumber": 5,
            "LapTime": None,
            "Stint": 1,
            "Compound": "SOFT",
            "TyreLife": 5,
            "FreshTyre": "True",
            "TrackStatus": "1",
            "IsAccurate": True,
            "RoundNumber": 1,
            "EventName": "Bahrain Grand Prix",
        }
        lap = LapDataSchema(**data)
        assert lap.LapTime is None


class TestSessionInfoSchema:
    """Tests for SessionInfoSchema validation."""

    def test_valid_session_info(self):
        """Valid session info should pass validation."""
        data = {
            "season": 2024,
            "round_number": 1,
            "session_type": "R",
            "event_name": "Bahrain Grand Prix",
            "drivers": ["VER", "HAM", "LEC"],
        }
        session = SessionInfoSchema(**data)
        assert session.season == 2024
        assert len(session.drivers) == 3

    def test_invalid_season(self):
        """Season before 2018 should fail."""
        data = {
            "season": 2010,  # Invalid - before F1 Visualizer support
            "round_number": 1,
            "session_type": "R",
            "event_name": "Bahrain Grand Prix",
            "drivers": ["VER"],
        }
        with pytest.raises(ValidationError):
            SessionInfoSchema(**data)

    def test_invalid_session_type(self):
        """Only R and S are valid session types."""
        data = {
            "season": 2024,
            "round_number": 1,
            "session_type": "Q",  # Invalid
            "event_name": "Bahrain Grand Prix",
            "drivers": ["VER"],
        }
        with pytest.raises(ValidationError):
            SessionInfoSchema(**data)

    def test_full_name_property(self):
        """full_name property should format correctly."""
        data = {
            "season": 2024,
            "round_number": 1,
            "session_type": "R",
            "event_name": "Bahrain Grand Prix",
            "drivers": ["VER"],
        }
        session = SessionInfoSchema(**data)
        assert "2024" in session.full_name
        assert "Race" in session.full_name


class TestTransformedLapSchema:
    """Tests for TransformedLapSchema with calculated fields."""

    def test_valid_transformed_lap(self):
        """Transformed lap with calculated fields should validate."""
        data = {
            "Driver": "VER",
            "DriverNumber": 1,
            "LapNumber": 5,
            "LapTime": 95.5,
            "Stint": 1,
            "Compound": "SOFT",
            "TyreLife": 5,
            "FreshTyre": "True",
            "Position": 1,
            "TrackStatus": "1",
            "IsAccurate": True,
            "RoundNumber": 1,
            "EventName": "Bahrain Grand Prix",
            "CompoundName": "C5",
            "IsSlick": True,
            "IsValid": True,
            "DeltaToRep": 0.5,
            "PctFromRep": 0.5,
            "DeltaToFastest": 0.0,
            "PctFromFastest": 0.0,
        }
        lap = TransformedLapSchema(**data)
        assert lap.IsSlick is True
        assert lap.CompoundName == "C5"
