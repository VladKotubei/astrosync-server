"""
Moon Favorability calculator powered by pyswisseph.

Scores how the transiting Moon aspects a user's natal Sun, Moon,
Mercury, Venus, and Mars.  Positive aspects (trine, sextile) add points;
hard aspects (square, opposition) subtract them.  Conjunctions are
context-sensitive (benefic vs. malefic natal body).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Tuple

import swisseph as swe

_EPHE_FLAG: int = swe.FLG_MOSEPH

_NATAL_BODIES: Dict[str, int] = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
}

_BENEFICS = {"Venus", "Sun", "Moon", "Mercury"}
_MALEFICS = {"Mars"}

_JD_UNIX_EPOCH: float = 2_440_587.5

_ASPECT_ORBS: List[Tuple[str, float, float]] = [
    ("conjunction", 0.0,   5.0),
    ("sextile",     60.0,  5.0),
    ("square",      90.0,  5.0),
    ("trine",       120.0, 5.0),
    ("opposition",  180.0, 5.0),
]


def _dt_to_jd(dt: datetime) -> float:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp() / 86_400.0 + _JD_UNIX_EPOCH


def _planet_longitude(jd: float, body: int) -> float:
    pos, _ = swe.calc_ut(jd, body, _EPHE_FLAG)
    return pos[0]


def _angular_distance(lon_a: float, lon_b: float) -> float:
    """Shortest arc between two ecliptic longitudes (0-180)."""
    diff = abs(lon_a - lon_b) % 360.0
    return diff if diff <= 180.0 else 360.0 - diff


def _detect_aspect(angle: float) -> str | None:
    for name, exact, orb in _ASPECT_ORBS:
        if abs(angle - exact) <= orb:
            return name
    return None


def _score_aspect(aspect: str, natal_body_name: str) -> int:
    if aspect in ("trine", "sextile"):
        return 1
    if aspect in ("square", "opposition"):
        return -1
    if aspect == "conjunction":
        return 1 if natal_body_name in _BENEFICS else -1
    return 0


def calculate_moon_favorability(
    transit_date: datetime,
    natal_jd: float,
) -> Dict[str, object]:
    """Return favorability status and numeric score.

    Parameters
    ----------
    transit_date : datetime (UTC)
        The calendar date for which the transiting Moon is evaluated (noon UTC).
    natal_jd : float
        Julian Day computed from the user's birth date, time, and location.
    """
    transit_dt = transit_date.replace(hour=12, minute=0, second=0, tzinfo=timezone.utc)
    transit_jd = _dt_to_jd(transit_dt)

    transit_moon_lon = _planet_longitude(transit_jd, swe.MOON)

    score = 0
    details: list[dict] = []

    for name, body_id in _NATAL_BODIES.items():
        natal_lon = _planet_longitude(natal_jd, body_id)
        angle = _angular_distance(transit_moon_lon, natal_lon)
        aspect = _detect_aspect(angle)

        if aspect is not None:
            pts = _score_aspect(aspect, name)
            score += pts
            details.append({
                "natal_planet": name,
                "aspect": aspect,
                "angle": round(angle, 2),
                "points": pts,
            })

    if score >= 2:
        status = "favorable"
    elif score <= -2:
        status = "unfavorable"
    else:
        status = "neutral"

    return {"status": status, "score": score, "details": details}


def natal_params_to_jd(
    natal_date: str,
    natal_time: str,
    natal_lat: float,
    natal_lon: float,
) -> float:
    """Build a Julian Day from user-supplied birth parameters.

    The birth time is treated as local mean solar time at the given
    longitude — the same simplified approach the rest of AstroSync uses
    when no explicit timezone is provided.
    """
    dt = datetime.strptime(f"{natal_date} {natal_time}", "%Y-%m-%d %H:%M")
    dt = dt.replace(tzinfo=timezone.utc)
    return _dt_to_jd(dt)
