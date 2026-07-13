"""Pydantic schemas for session information validation."""

from pydantic import BaseModel, Field


class SessionInfoSchema(BaseModel):
    """Schema for session metadata."""

    season: int = Field(..., ge=2018, le=2030, description="Championship season")
    round_number: int = Field(..., ge=1, le=30, description="Round number")
    session_type: str = Field(..., pattern="^[RS]$", description="R for Race, S for Sprint")
    event_name: str = Field(..., min_length=1, description="Full event name")
    drivers: list[str] = Field(..., min_length=1, description="List of driver abbreviations")
    starting_grid: dict[str, int] = Field(
        default_factory=dict, description="Starting grid positions"
    )

    @property
    def full_name(self) -> str:
        """Get full session name."""
        session_name = "Race" if self.session_type == "R" else "Sprint"
        return f"{self.season} {self.event_name} - {session_name}"


class DriverInfoSchema(BaseModel):
    """Schema for driver information."""

    abbreviation: str = Field(..., min_length=2, max_length=3)
    number: int = Field(..., ge=1, le=99)
    team: str = Field(..., min_length=1)
    full_name: str | None = None


class EventScheduleSchema(BaseModel):
    """Schema for event schedule data."""

    round_number: int = Field(..., ge=1, le=30)
    event_name: str = Field(..., min_length=1)
    event_format: str = Field(..., description="conventional or sprint_shootout")
    country: str | None = None
    location: str | None = None

    model_config = {"extra": "allow"}
