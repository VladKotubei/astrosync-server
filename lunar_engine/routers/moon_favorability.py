"""
GET /api/v1/moon-favorability — Moon transit aspect scoring.

Query parameters
----------------
date       : str   "YYYY-MM-DD"  — transit date
natal_date : str   "YYYY-MM-DD"  — user's birth date
natal_time : str   "HH:MM"       — user's birth time
natal_lat  : float               — birth-location latitude
natal_lon  : float               — birth-location longitude
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from lunar_engine.models import MoonFavorabilityResponse
from lunar_engine.services.favorability_calculator import (
    calculate_moon_favorability,
    natal_params_to_jd,
)

router = APIRouter(prefix="/api/v1", tags=["Lunar Engine"])


@router.get(
    "/moon-favorability",
    response_model=MoonFavorabilityResponse,
    summary="Score how the transiting Moon aspects natal planets",
)
async def get_moon_favorability(
    date: str = Query(
        ..., description='Transit date in "YYYY-MM-DD" format'
    ),
    natal_date: str = Query(
        ..., description='Birth date in "YYYY-MM-DD" format'
    ),
    natal_time: str = Query(
        ..., description='Birth time in "HH:MM" format'
    ),
    natal_lat: float = Query(
        ..., ge=-90.0, le=90.0, description="Birth-location latitude"
    ),
    natal_lon: float = Query(
        ..., ge=-180.0, le=180.0, description="Birth-location longitude"
    ),
) -> MoonFavorabilityResponse:

    try:
        transit_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transit date: '{date}'. Expected YYYY-MM-DD.",
        )

    try:
        natal_jd = natal_params_to_jd(natal_date, natal_time, natal_lat, natal_lon)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid natal parameters: {exc}")

    result = calculate_moon_favorability(transit_date, natal_jd)
    return MoonFavorabilityResponse(**result)
