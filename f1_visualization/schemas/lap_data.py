"""Pydantic schemas for lap data validation."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class LapDataSchema(BaseModel):
    """Schema for validating individual lap data records."""

    Driver: str = Field(..., min_length=2, max_length=3, description="Driver abbreviation")
    DriverNumber: str | int = Field(..., description="Driver number")
    LapNumber: int = Field(..., ge=1, description="Lap number, starting from 1")
    LapTime: float | None = Field(None, gt=0, description="Lap time in seconds")
    Stint: int = Field(..., ge=1, description="Stint number")
    Compound: Literal["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET", "UNKNOWN"] = Field(
        ..., description="Tyre compound"
    )
    TyreLife: int = Field(..., ge=1, description="Tyre age in laps")
    FreshTyre: str = Field(..., description="Whether tyre is fresh")
    Position: int | None = Field(None, ge=1, le=25, description="Race position")
    TrackStatus: str = Field(..., description="Track status code")
    IsAccurate: bool = Field(..., description="Whether lap time is accurate")
    RoundNumber: int = Field(..., ge=1, description="Round number in season")
    EventName: str = Field(..., min_length=1, description="Event name")

    @field_validator("Driver")
    @classmethod
    def validate_driver_format(cls, v: str) -> str:
        """Ensure driver abbreviation is uppercase."""
        return v.upper()

    @field_validator("Compound")
    @classmethod
    def validate_compound(cls, v: str) -> str:
        """Ensure compound is uppercase."""
        return v.upper() if v else "UNKNOWN"

    model_config = {"extra": "allow"}  # Allow extra fields from FastF1


class TransformedLapSchema(LapDataSchema):
    """Schema for transformed lap data with calculated fields."""

    CompoundName: str | None = Field(None, description="Absolute compound name (C1-C5)")
    IsSlick: bool = Field(..., description="Whether tyre is slick compound")
    IsValid: bool = Field(..., description="Whether lap is valid for analysis")
    DeltaToRep: float | None = Field(None, description="Delta to representative time")
    PctFromRep: float | None = Field(None, description="Percent from representative time")
    DeltaToFastest: float | None = Field(None, description="Delta to fastest lap")
    PctFromFastest: float | None = Field(None, description="Percent from fastest lap")
    DeltaToLapRep: float | None = Field(None, description="Delta to lap representative")
    PctFromLapRep: float | None = Field(None, description="Percent from lap representative")
    FuelAdjLapTime: float | None = Field(None, gt=0, description="Fuel-adjusted lap time")


class LapDataBatch(BaseModel):
    """Schema for batch validation of lap data."""

    laps: list[LapDataSchema]

    @property
    def drivers(self) -> set[str]:
        """Get unique drivers in batch."""
        return {lap.Driver for lap in self.laps}

    @property
    def rounds(self) -> set[int]:
        """Get unique rounds in batch."""
        return {lap.RoundNumber for lap in self.laps}
