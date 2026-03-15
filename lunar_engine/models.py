from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class MoonDataResponse(BaseModel):
    """
    Geocentric + topocentric lunar snapshot for a given date and location.

    phase:          0.0 = New Moon  →  0.5 = Full Moon  →  1.0 = back to New
    illumination:   percentage of the lunar disc that is lit (0.0 – 100.0)
    distance:       Earth–Moon centre-to-centre distance in kilometres
    next_full_moon: UTC datetime of the upcoming full moon
    moonrise:       rise time in the caller's requested timezone (None in polar regions)
    moonset:        set  time in the caller's requested timezone (None in polar regions)
    """

    phase: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Lunar phase fraction (0.0 = new moon, 0.5 = full moon)",
    )
    illumination: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Percentage of the Moon's visible disc that is illuminated",
    )
    distance: float = Field(
        ...,
        gt=0.0,
        description="Earth–Moon distance in kilometres",
    )
    next_full_moon: datetime = Field(
        ...,
        description="UTC datetime of the next full moon",
    )
    moonrise: Optional[datetime] = Field(
        None,
        description="Moonrise time adjusted to the requested timezone (None if Moon does not rise)",
    )
    moonset: Optional[datetime] = Field(
        None,
        description="Moonset time adjusted to the requested timezone (None if Moon does not set)",
    )

    model_config = ConfigDict()

    @field_serializer("next_full_moon", "moonrise", "moonset")
    def _serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        return dt.isoformat() if dt is not None else None
