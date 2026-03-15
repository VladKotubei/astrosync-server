"""
Lunar calculation engine powered by pyswisseph (Swiss Ephemeris Python bindings).

All heavy maths lives here, keeping routers thin.

Coordinate convention throughout:
  - longitude  east positive, west  negative  (−180 … +180)
  - latitude   north positive, south negative  ( −90 … +90)

pyswisseph API note (version 2.8.x)
------------------------------------
  calc_ut(jd, body, flag)  → ((lon, lat, dist, v_lon, v_lat, v_dist), retflag)
  pheno_ut(jd, body, flag) → (phase_angle°, illumination_frac, elongation°,
                               disc_diam", magnitude)   # flat 5-tuple, no retflag
  rise_trans(jd, body, lon, lat, alt, press, temp, rsmi, flag)
                           → ((retcode,), (jd_event, ...))
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

import swisseph as swe

# ─── Ephemeris flag ──────────────────────────────────────────────────────────
# FLG_MOSEPH (Moshier, fully built-in) requires no external .se1 files.
# Accuracy: ±2 arc-minutes for the Moon – sufficient for all astrological use.
# Swap to swe.FLG_SWIEPH once Swiss Ephemeris data files are deployed.
_EPHE_FLAG: int = swe.FLG_MOSEPH

# ─── Physical constants ──────────────────────────────────────────────────────
_AU_TO_KM: float = 149_597_870.7       # 1 AU → km  (IAU 2012)
_JD_UNIX_EPOCH: float = 2_440_587.5   # Julian Day at 1970-01-01 00:00:00 UTC

# ─── Moon synodic motion ─────────────────────────────────────────────────────
# Mean synodic angular velocity used as Newton's-method Jacobian.
_SYNODIC_RATE: float = 360.0 / 29.530588853  # ≈ 12.190749 °/day

# ─── Rise / set flags ────────────────────────────────────────────────────────
_CALC_RISE: int = swe.CALC_RISE   # = 1
_CALC_SET: int = swe.CALC_SET    # = 2

# Standard atmosphere for atmospheric-refraction correction
_ATPRESS: float = 1013.25   # hPa
_ATTEMP: float = 10.0       # °C


# ═══════════════════════════════════════════════════════════════════════════════
# Julian Day ↔ datetime helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _dt_to_jd(dt: datetime) -> float:
    """Convert a timezone-aware datetime to a Julian Day number (UT)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp() / 86_400.0 + _JD_UNIX_EPOCH


def _jd_to_utc_dt(jd: float) -> datetime:
    """Convert a Julian Day number (UT) to a UTC-aware datetime."""
    unix_ts = (jd - _JD_UNIX_EPOCH) * 86_400.0
    return datetime.fromtimestamp(unix_ts, tz=timezone.utc)


# ═══════════════════════════════════════════════════════════════════════════════
# Phase helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _moon_sun_elongation(jd: float) -> float:
    """Return Moon–Sun ecliptic elongation in degrees, clamped to [0, 360)."""
    sun_pos, _ = swe.calc_ut(jd, swe.SUN, _EPHE_FLAG)
    moon_pos, _ = swe.calc_ut(jd, swe.MOON, _EPHE_FLAG)
    return (moon_pos[0] - sun_pos[0]) % 360.0


# ═══════════════════════════════════════════════════════════════════════════════
# Next full moon
# ═══════════════════════════════════════════════════════════════════════════════

def _find_next_full_moon(jd_start: float) -> float:
    """Return the Julian Day of the next full moon (elongation = 180°).

    Algorithm:
    1. Estimate how far the Moon must travel (in synodic degrees) to reach 180°.
    2. Seed Newton's method from that estimate.
    3. Iterate up to 10 times; typically converges to < 0.1 s in 3–4 steps.

    If the elongation is already within 1° of 180°, we jump forward by one
    synodic period so we find the *next* full moon, not the current one.
    """
    e0 = _moon_sun_elongation(jd_start)
    degrees_to_full = (180.0 - e0) % 360.0

    if degrees_to_full < 1.0:
        degrees_to_full += 360.0

    jd = jd_start + degrees_to_full / _SYNODIC_RATE

    for _ in range(10):
        e = _moon_sun_elongation(jd)
        residual = e - 180.0
        # Wrap residual to (−180, +180] for a consistent Newton step direction
        if residual > 180.0:
            residual -= 360.0
        elif residual < -180.0:
            residual += 360.0
        correction = residual / _SYNODIC_RATE
        jd -= correction
        if abs(correction) < 1e-7:     # sub-second precision reached
            break

    return jd


# ═══════════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_global_moon_data(date_utc: datetime) -> Dict[str, Any]:
    """Compute location-independent lunar quantities for *date_utc*.

    Returns a plain dict (no datetime objects) so the result can be stored
    in the cache and eventually serialised through Redis without extra work.

    Keys: phase, illumination, distance, next_full_moon (datetime, UTC).
    """
    jd = _dt_to_jd(date_utc)

    # ── Moon cartesian position ───────────────────────────────────────────
    # calc_ut → ((lon°, lat°, dist_AU, v_lon, v_lat, v_dist), retflag)
    moon_pos, _ = swe.calc_ut(jd, swe.MOON, _EPHE_FLAG)

    # ── Illumination via Swiss Ephemeris phenomena ────────────────────────
    # pheno_ut → (phase_angle°, illumination_frac, elongation°,
    #              disc_diam", magnitude)  — flat 5-tuple, no retflag
    moon_attr = swe.pheno_ut(jd, swe.MOON, _EPHE_FLAG)
    illumination_pct = round(moon_attr[1] * 100.0, 4)

    # ── Phase fraction (elongation-based, 0.0 – 1.0) ─────────────────────
    #   0.0  = New Moon      0.25 = First Quarter
    #   0.5  = Full Moon     0.75 = Last Quarter
    elongation = _moon_sun_elongation(jd)
    phase = round(elongation / 360.0, 6)

    # ── Distance ─────────────────────────────────────────────────────────
    distance_km = round(moon_pos[2] * _AU_TO_KM, 2)

    # ── Next full moon ────────────────────────────────────────────────────
    nfm_jd = _find_next_full_moon(jd)
    next_full_moon_utc = _jd_to_utc_dt(nfm_jd)

    return {
        "phase": phase,
        "illumination": illumination_pct,
        "distance": distance_km,
        "next_full_moon": next_full_moon_utc,
    }


def calculate_local_moon_data(
    date_utc: datetime,
    latitude: float,
    longitude: float,
    tz: ZoneInfo,
) -> Dict[str, Optional[datetime]]:
    """Compute moonrise and moonset for *date_utc* at the given coordinates.

    Searches within a 24-hour window starting at *date_utc* (UTC midnight of
    the requested local date).  Results are converted into the caller's
    timezone.

    Returns None for either value in polar regions where the Moon does not
    rise or set on the requested date.

    pyswisseph rise_trans signature:
        rise_trans(jd, body, lon, lat, alt, press, temp, rsmi, flag)
        → ((retcode,), (jd_event, ...))
    """
    jd_start = _dt_to_jd(date_utc)

    moonrise_dt: Optional[datetime] = None
    moonset_dt: Optional[datetime] = None

    try:
        ret_tuple, tret = swe.rise_trans(
            jd_start, swe.MOON,
            longitude, latitude, 0.0,
            _ATPRESS, _ATTEMP,
            _CALC_RISE, _EPHE_FLAG,
        )
        if ret_tuple[0] == 0 and tret[0] > 0.0:
            moonrise_dt = _jd_to_utc_dt(tret[0]).astimezone(tz)
    except Exception:
        pass

    try:
        ret_tuple, tret = swe.rise_trans(
            jd_start, swe.MOON,
            longitude, latitude, 0.0,
            _ATPRESS, _ATTEMP,
            _CALC_SET, _EPHE_FLAG,
        )
        if ret_tuple[0] == 0 and tret[0] > 0.0:
            moonset_dt = _jd_to_utc_dt(tret[0]).astimezone(tz)
    except Exception:
        pass

    return {
        "moonrise": moonrise_dt,
        "moonset": moonset_dt,
    }
