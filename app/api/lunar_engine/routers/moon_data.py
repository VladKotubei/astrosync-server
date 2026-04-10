"""
GET /api/v1/moon-data  –  Lunar Engine endpoint.

Query parameters
----------------
date      : ISO 8601 string  "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM:SS"
latitude  : float  −90.0 … +90.0
longitude : float  −180.0 … +180.0
timezone  : IANA timezone string, e.g. "Europe/Kyiv", "America/New_York"

Response: MoonDataResponse JSON (see models.py)

Caching strategy
----------------
Geocentric quantities (phase, illumination, distance, next_full_moon,
zodiac_sign, moon_longitude, sign_index) are identical for every user on
the same date, so they are stored in the module-level CacheService singleton
with a 15-minute TTL.

Topocentric quantities (moonrise, moonset) depend on geographic coordinates
and are always recalculated per request.
"""

from __future__ import annotations

from datetime import datetime
from datetime import timezone as dt_timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, HTTPException, Query

from app.api.lunar_engine.models import MoonDataResponse
from app.api.lunar_engine.services.cache_service import moon_cache
from app.api.lunar_engine.services.moon_calculator import (
    calculate_global_moon_data,
    calculate_local_moon_data,
)

router = APIRouter(prefix="/api/v1", tags=["Lunar Engine"])


@router.get(
    "/moon-data",
    response_model=MoonDataResponse,
    summary="Get precise lunar data for a date and location",
    response_description="Geocentric (phase, illumination, distance, zodiac sign) + topocentric (rise/set) lunar snapshot",
)
async def get_moon_data(
    date: str = Query(
        ...,
        description='Date in ISO 8601 format: "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM:SS"',
    ),
    latitude: float = Query(
        ...,
        ge=-90.0,
        le=90.0,
        description="Geographic latitude in decimal degrees (−90 … +90)",
    ),
    longitude: float = Query(
        ...,
        ge=-180.0,
        le=180.0,
        description="Geographic longitude in decimal degrees (−180 … +180)",
    ),
    tz_name: str = Query(
        ...,
        alias="timezone",
        description='IANA timezone string, e.g. "Europe/Paris"',
    ),
) -> MoonDataResponse:
    # ── 1. Validate timezone ──────────────────────────────────────────────
    # ZoneInfo raises ZoneInfoNotFoundError for unknown keys and ValueError
    # for structurally invalid keys (e.g. empty string, absolute paths).
    try:
        tz = ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, KeyError, ValueError):
        raise HTTPException(
            status_code=400,
            detail=f"Unknown timezone: '{tz_name}'. "
                   "Use a valid IANA timezone identifier (e.g. 'America/New_York').",
        )

    # ── 2. Parse date ─────────────────────────────────────────────────────
    try:
        parsed = datetime.fromisoformat(date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date: '{date}'. Expected ISO 8601, e.g. '2026-03-14'.",
        )

    # ── 3. Anchor to local midnight → convert to UTC ──────────────────────
    # If the caller passes a bare date ("2026-03-14") we treat it as midnight
    # in their timezone, so astronomical events are reported for that local day.
    local_midnight = parsed.replace(
        hour=0, minute=0, second=0, microsecond=0, tzinfo=tz
    )
    date_utc = local_midnight.astimezone(dt_timezone.utc)

    # ── 4. Global data (cached, location-independent) ────────────────────
    # Cache key is the UTC datetime rounded to the minute so that two
    # requests differing by only a few seconds share the same entry.
    cache_key = f"moon_global:{date_utc.strftime('%Y-%m-%dT%H:%M')}"

    global_data = moon_cache.get(cache_key)
    if global_data is None:
        global_data = calculate_global_moon_data(date_utc)
        moon_cache.set(cache_key, global_data)

    # ── 5. Local data (per-request, coordinate-dependent) ────────────────
    local_data = calculate_local_moon_data(date_utc, latitude, longitude, tz)

    return MoonDataResponse(**global_data, **local_data)
