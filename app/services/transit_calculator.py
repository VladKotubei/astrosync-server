"""
AstroSync Transit Calculator — production-grade ephemeris service.

Determines planetary retrograde periods and shadow phases dynamically using
pyswisseph (Swiss Ephemeris, Moshier mode).  Works for any year, past or future.
No hardcoded dates.

Caching strategy
────────────────
Yearly ephemeris data is computed once per (planet, year) pair and held in an
in-memory ``TTLCache`` (``cachetools``, 1-hour TTL, 64-entry LRU).  A cold-cache
request for a new year costs ~3 000 Swiss-Ephemeris evaluations — roughly 5 ms
on commodity hardware — and every subsequent hit for that year is O(1).

Inner planets (Mercury, Venus)
    Full shadow-phase analysis: ``pre_shadow`` → ``peak`` → ``post_shadow``.
    These drive the ``retrograde_phase`` key in the CalendarDay JSON response.

Outer planets (Mars – Pluto)
    Simple negative-speed check.  Retrogrades surface as entries in the
    ``planetary_events`` array without triggering the primary UI warning.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date as date_type, timedelta
from typing import Dict, List, Optional, Tuple

import swisseph as swe
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# ── Ephemeris flag ───────────────────────────────────────────────────────────
# FLG_MOSEPH  = built-in Moshier analytical ephemeris (no external data files).
# FLG_SPEED   = request speed values in the output tuple.
_EPHE_FLAG: int = swe.FLG_MOSEPH | swe.FLG_SPEED

# ── Planet registries ────────────────────────────────────────────────────────
_INNER_PLANETS: Dict[str, int] = {
    "Mercury": swe.MERCURY,
    "Venus":   swe.VENUS,
}

_OUTER_PLANETS: Dict[str, int] = {
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
    "Uranus":  swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto":   swe.PLUTO,
}

_SIGN_TRANSIT_PLANETS: Dict[str, int] = {
    "Venus":   swe.VENUS,
    "Mars":    swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn":  swe.SATURN,
}

_ZODIAC_SIGNS: Tuple[str, ...] = (
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

# ── Localised retrograde labels ──────────────────────────────────────────────
_RETRO_LABELS: Dict[str, Dict[str, Dict[str, str]]] = {
    "en": {
        "Mercury": {"peak": "Mercury Retrograde ☿", "shadow": "Mercury Shadow ☿"},
        "Venus":   {"peak": "Venus Retrograde ♀",   "shadow": "Venus Shadow ♀"},
    },
    "other": {
        "Mercury": {"peak": "Ретроградний Меркурій ☿", "shadow": "Тінь Меркурія ☿"},
        "Venus":   {"peak": "Ретроградна Венера ♀",    "shadow": "Тінь Венери ♀"},
    },
}

# ── Caches ───────────────────────────────────────────────────────────────────
# Inner-planet retrogrades: (planet_name, year) → List[RetrogradePeriod]
_retro_cache: TTLCache = TTLCache(maxsize=64, ttl=3600)
# Outer-planet daily speeds: ("outer", year) → Dict[date, Dict[name, speed]]
_outer_speed_cache: TTLCache = TTLCache(maxsize=16, ttl=3600)


# ═════════════════════════════════════════════════════════════════════════════
# Data structures
# ═════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RetrogradePeriod:
    """One complete retrograde cycle with shadow boundaries."""

    planet: str
    pre_shadow_start: date_type
    station_retrograde: date_type
    station_direct: date_type
    post_shadow_end: date_type
    sr_longitude: float
    sd_longitude: float


# ═════════════════════════════════════════════════════════════════════════════
# Low-level ephemeris helpers
# ═════════════════════════════════════════════════════════════════════════════

def _date_to_jd(d: date_type) -> float:
    """Calendar date → Julian Day at noon UT."""
    return swe.julday(d.year, d.month, d.day, 12.0)


def _planet_state(d: date_type, body: int) -> Tuple[float, float]:
    """Return ``(ecliptic_longitude°, speed°/day)`` for *body* on *d* at noon UT.

    ``speed`` is the daily apparent motion in ecliptic longitude.
    A negative value means the planet appears to move backward (retrograde).
    """
    pos, _ = swe.calc_ut(_date_to_jd(d), body, _EPHE_FLAG)
    return pos[0], pos[3]


def _angle_diff(a: float, b: float) -> float:
    """Signed shortest-arc difference *a* − *b*, wrapped to (−180, +180].

    Correctly handles the 0°/360° ecliptic boundary.
    """
    d = (a - b) % 360.0
    return d - 360.0 if d > 180.0 else d


def _daily_ephemeris(
    body: int,
    start: date_type,
    end: date_type,
) -> List[Tuple[date_type, float, float]]:
    """Compute ``(date, longitude°, speed°/day)`` for every day in [start, end]."""
    rows: List[Tuple[date_type, float, float]] = []
    cur = start
    while cur <= end:
        lon, spd = _planet_state(cur, body)
        rows.append((cur, lon, spd))
        cur += timedelta(days=1)
    return rows


# ═════════════════════════════════════════════════════════════════════════════
# Shadow-phase computation (Mercury & Venus)
# ═════════════════════════════════════════════════════════════════════════════

def _find_lon_crossing(
    daily: List[Tuple[date_type, float, float]],
    target: float,
    start: int,
    step: int,
) -> date_type:
    """Walk *daily* from index *start* in direction *step* until the planet's
    ecliptic longitude crosses *target*°.

    Uses the signed angular-difference zero-crossing method so that the
    0°/360° ecliptic boundary is handled transparently.  Picks the date
    whose longitude is closest to *target*.
    """
    prev = _angle_diff(daily[start][1], target)
    idx = start + step

    while 0 <= idx < len(daily):
        cur = _angle_diff(daily[idx][1], target)
        # Zero-crossing with small arc (< 30°) ⇒ genuine longitude match
        if prev * cur <= 0 and abs(prev - cur) < 30.0:
            return daily[idx][0] if abs(cur) <= abs(prev) else daily[idx - step][0]
        prev = cur
        idx += step

    # Fallback to scan boundary (should not happen with an adequate window)
    return daily[max(0, min(idx - step, len(daily) - 1))][0]


def _inner_retrogrades(
    name: str,
    body: int,
    year: int,
) -> List[RetrogradePeriod]:
    """Compute all retrograde periods with shadow boundaries for an inner
    planet in *year*.

    The scan window extends from Nov 1 of the prior year to Feb 28 of the
    following year so that shadow phases overlapping the year boundary are
    captured.

    Algorithm
    ---------
    1. Build a daily (longitude, speed) ephemeris for the scan window.
    2. Identify retrograde intervals: contiguous runs of negative speed.
       The first negative-speed day is the *station retrograde* (SR);
       the last is the *station direct* (SD).
    3. For each (SR, SD) pair record the ecliptic longitudes SR° and SD°.
    4. Pre-shadow start: scan backward from SR to find when the planet
       (moving direct) first crossed SD° — i.e. entered the degree range
       it will eventually retrograde through.
    5. Post-shadow end: scan forward from SD to find when the planet
       (moving direct again) reaches SR° — fully clearing the retrograde
       zone.
    """
    scan_start = date_type(year - 1, 11, 1)
    scan_end = date_type(year + 1, 2, 28)
    daily = _daily_ephemeris(body, scan_start, scan_end)

    intervals: List[Tuple[int, int]] = []
    in_retro = False
    sr_i = 0
    for i, (_, _, spd) in enumerate(daily):
        if spd < 0 and not in_retro:
            sr_i = i
            in_retro = True
        elif spd >= 0 and in_retro:
            intervals.append((sr_i, i - 1))
            in_retro = False
    if in_retro:
        intervals.append((sr_i, len(daily) - 1))

    periods: List[RetrogradePeriod] = []
    for si, di in intervals:
        sr_date, sr_lon, _ = daily[si]
        sd_date, sd_lon, _ = daily[di]

        periods.append(RetrogradePeriod(
            planet=name,
            pre_shadow_start=_find_lon_crossing(daily, sd_lon, si, -1),
            station_retrograde=sr_date,
            station_direct=sd_date,
            post_shadow_end=_find_lon_crossing(daily, sr_lon, di, +1),
            sr_longitude=round(sr_lon, 4),
            sd_longitude=round(sd_lon, 4),
        ))

    year_start = date_type(year, 1, 1)
    year_end = date_type(year, 12, 31)
    return [
        p for p in periods
        if p.post_shadow_end >= year_start and p.pre_shadow_start <= year_end
    ]


# ═════════════════════════════════════════════════════════════════════════════
# Outer-planet daily-speed cache
# ═════════════════════════════════════════════════════════════════════════════

def _load_outer_speeds(year: int) -> Dict[date_type, Dict[str, float]]:
    """Pre-compute daily ecliptic speed for every outer planet for *year*."""
    result: Dict[date_type, Dict[str, float]] = {}
    cur = date_type(year, 1, 1)
    end = date_type(year, 12, 31)
    while cur <= end:
        result[cur] = {
            n: _planet_state(cur, pid)[1] for n, pid in _OUTER_PLANETS.items()
        }
        cur += timedelta(days=1)
    return result


# ═════════════════════════════════════════════════════════════════════════════
# Public API
# ═════════════════════════════════════════════════════════════════════════════

def get_inner_retrogrades(planet: str, year: int) -> List[RetrogradePeriod]:
    """Return the cached list of retrograde periods (with shadow dates) for
    *planet* (``"Mercury"`` or ``"Venus"``) in *year*.
    """
    key = (planet, year)
    if key not in _retro_cache:
        body = _INNER_PLANETS.get(planet)
        if body is None:
            raise ValueError(f"{planet} is not a tracked inner planet")
        _retro_cache[key] = _inner_retrogrades(planet, body, year)
        logger.info(
            "Cached %s retrogrades for %d (%d periods)",
            planet, year, len(_retro_cache[key]),
        )
    return _retro_cache[key]


def classify_inner_retrograde(planet: str, d: date_type) -> Optional[str]:
    """Classify *d* within the retrograde cycle of *planet*.

    Returns ``"pre_shadow"``, ``"peak"``, ``"post_shadow"``, or ``None``.
    """
    for p in get_inner_retrogrades(planet, d.year):
        if p.station_retrograde <= d <= p.station_direct:
            return "peak"
        if p.pre_shadow_start <= d < p.station_retrograde:
            return "pre_shadow"
        if p.station_direct < d <= p.post_shadow_end:
            return "post_shadow"
    return None


def get_outer_retrograde_events(d: date_type) -> List[str]:
    """Return ``["Mars Retrograde", …]`` for every outer planet whose
    ecliptic speed is negative on *d*.
    """
    key = ("outer", d.year)
    if key not in _outer_speed_cache:
        _outer_speed_cache[key] = _load_outer_speeds(d.year)
        logger.info("Cached outer-planet speeds for %d", d.year)

    speeds = _outer_speed_cache[key].get(d)
    if speeds is None:
        return [
            f"{n} Retrograde"
            for n, pid in _OUTER_PLANETS.items()
            if _planet_state(d, pid)[1] < 0
        ]
    return [f"{n} Retrograde" for n, spd in speeds.items() if spd < 0]


def get_sign_transits(d: date_type) -> List[str]:
    """Return the current zodiac-sign transit for each display planet on *d*.

    Example output: ``["Venus in Pisces", "Mars in Cancer", …]``.
    Planets included: Venus, Mars, Jupiter, Saturn.
    """
    out: List[str] = []
    for name, body in _SIGN_TRANSIT_PLANETS.items():
        lon, _ = _planet_state(d, body)
        out.append(f"{name} in {_ZODIAC_SIGNS[int(lon // 30) % 12]}")
    return out


def check_retrograde_for_calendar(
    d: date_type,
    language: str = "en",
) -> Tuple[Optional[str], Optional[str], List[str]]:
    """Unified retrograde check consumed by :func:`get_calendar_data`.

    Returns
    -------
    retrograde_label : str | None
        Human-readable label for the primary UI indicator.
        Mercury takes priority over Venus when both are active.
    retrograde_phase : str | None
        One of ``"pre_shadow"`` / ``"peak"`` / ``"post_shadow"`` or ``None``.
    extra_events : list[str]
        Outer-planet retrogrades (e.g. ``"Mars Retrograde"``), plus the
        lower-priority inner planet if both are simultaneously in a phase.
    """
    label: Optional[str] = None
    phase: Optional[str] = None
    extra: List[str] = []

    lang_key = "en" if language == "en" else "other"
    labels = _RETRO_LABELS[lang_key]

    for planet in ("Mercury", "Venus"):
        p = classify_inner_retrograde(planet, d)
        if p is None:
            continue

        kind = "peak" if p == "peak" else "shadow"

        if label is None:
            label = labels[planet][kind]
            phase = p
        else:
            extra.append(f"{planet} {'Retrograde' if p == 'peak' else 'Shadow'}")

    extra.extend(get_outer_retrograde_events(d))
    return label, phase, extra
