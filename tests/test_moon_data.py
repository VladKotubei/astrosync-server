"""
Unit tests for GET /api/v1/moon-data

Run:
    pytest tests/test_moon_data.py -v

Coverage areas
--------------
1.  Coordinate validation  – latitude / longitude out-of-range → 400
2.  Timezone validation    – unrecognised timezone string → 400
3.  Date validation        – malformed date string → 400
4.  Happy-path response    – valid request returns correct JSON structure
                             and value ranges
5.  Cache behaviour        – two identical requests hit the cache (no double
                             calculation)
6.  Polar edge-case        – extreme latitude returns 200 (moonrise/moonset
                             may be None, but the response is still valid)
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from lunar_engine.routers.moon_data import router
from lunar_engine.services.cache_service import moon_cache

# ─── Minimal test application ────────────────────────────────────────────────
_app = FastAPI(title="AstroSync Lunar Engine – Test")
_app.include_router(router)

client = TestClient(_app)

# ─── Fixtures ────────────────────────────────────────────────────────────────

VALID_PARAMS = {
    "date": "2026-03-14",
    "latitude": 48.8566,
    "longitude": 2.3522,
    "timezone": "Europe/Paris",
}


@pytest.fixture(autouse=True)
def clear_cache():
    """Flush the in-memory cache before every test for full isolation."""
    moon_cache._cache.clear()
    yield
    moon_cache._cache.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# 1 · Parameter validation
# ═══════════════════════════════════════════════════════════════════════════════

class TestCoordinateValidation:
    def test_latitude_too_low(self):
        resp = client.get("/api/v1/moon-data", params={**VALID_PARAMS, "latitude": -91.0})
        assert resp.status_code == 422, resp.text

    def test_latitude_too_high(self):
        resp = client.get("/api/v1/moon-data", params={**VALID_PARAMS, "latitude": 91.0})
        assert resp.status_code == 422, resp.text

    def test_longitude_too_low(self):
        resp = client.get("/api/v1/moon-data", params={**VALID_PARAMS, "longitude": -181.0})
        assert resp.status_code == 422, resp.text

    def test_longitude_too_high(self):
        resp = client.get("/api/v1/moon-data", params={**VALID_PARAMS, "longitude": 181.0})
        assert resp.status_code == 422, resp.text

    def test_latitude_at_boundary_south(self):
        """Exactly −90 is valid (South Pole)."""
        resp = client.get("/api/v1/moon-data", params={**VALID_PARAMS, "latitude": -90.0})
        assert resp.status_code == 200, resp.text

    def test_latitude_at_boundary_north(self):
        """Exactly +90 is valid (North Pole)."""
        resp = client.get("/api/v1/moon-data", params={**VALID_PARAMS, "latitude": 90.0})
        assert resp.status_code == 200, resp.text

    def test_longitude_at_boundary_west(self):
        resp = client.get("/api/v1/moon-data", params={**VALID_PARAMS, "longitude": -180.0})
        assert resp.status_code == 200, resp.text

    def test_longitude_at_boundary_east(self):
        resp = client.get("/api/v1/moon-data", params={**VALID_PARAMS, "longitude": 180.0})
        assert resp.status_code == 200, resp.text


class TestTimezoneValidation:
    def test_invalid_timezone(self):
        resp = client.get("/api/v1/moon-data", params={**VALID_PARAMS, "timezone": "Mars/Olympus"})
        assert resp.status_code == 400, resp.text
        assert "timezone" in resp.json()["detail"].lower()

    def test_empty_timezone(self):
        resp = client.get("/api/v1/moon-data", params={**VALID_PARAMS, "timezone": ""})
        assert resp.status_code in (400, 422), resp.text

    def test_valid_utc_timezone(self):
        resp = client.get("/api/v1/moon-data", params={**VALID_PARAMS, "timezone": "UTC"})
        assert resp.status_code == 200, resp.text


class TestDateValidation:
    def test_invalid_date_format(self):
        resp = client.get("/api/v1/moon-data", params={**VALID_PARAMS, "date": "not-a-date"})
        assert resp.status_code == 400, resp.text

    def test_date_with_time_component(self):
        """ISO 8601 datetime strings are also accepted."""
        resp = client.get(
            "/api/v1/moon-data",
            params={**VALID_PARAMS, "date": "2026-03-14T12:00:00"},
        )
        assert resp.status_code == 200, resp.text

    def test_missing_date_param(self):
        params = {k: v for k, v in VALID_PARAMS.items() if k != "date"}
        resp = client.get("/api/v1/moon-data", params=params)
        assert resp.status_code == 422, resp.text


# ═══════════════════════════════════════════════════════════════════════════════
# 2 · Happy-path response structure and value ranges
# ═══════════════════════════════════════════════════════════════════════════════

class TestHappyPath:
    def test_response_status_200(self):
        resp = client.get("/api/v1/moon-data", params=VALID_PARAMS)
        assert resp.status_code == 200, resp.text

    def test_response_content_type_json(self):
        resp = client.get("/api/v1/moon-data", params=VALID_PARAMS)
        assert "application/json" in resp.headers["content-type"]

    def test_response_has_all_required_fields(self):
        resp = client.get("/api/v1/moon-data", params=VALID_PARAMS)
        body = resp.json()
        required = {"phase", "illumination", "distance", "next_full_moon"}
        assert required.issubset(body.keys()), f"Missing keys: {required - body.keys()}"

    def test_phase_in_range(self):
        body = client.get("/api/v1/moon-data", params=VALID_PARAMS).json()
        assert 0.0 <= body["phase"] <= 1.0, f"phase out of range: {body['phase']}"

    def test_illumination_in_range(self):
        body = client.get("/api/v1/moon-data", params=VALID_PARAMS).json()
        assert 0.0 <= body["illumination"] <= 100.0, body["illumination"]

    def test_distance_positive(self):
        body = client.get("/api/v1/moon-data", params=VALID_PARAMS).json()
        # Moon never closer than ~356,000 km or further than ~407,000 km
        assert 300_000 < body["distance"] < 450_000, body["distance"]

    def test_next_full_moon_is_iso_datetime_string(self):
        body = client.get("/api/v1/moon-data", params=VALID_PARAMS).json()
        from datetime import datetime
        dt = datetime.fromisoformat(body["next_full_moon"])
        assert dt is not None

    def test_moonrise_moonset_are_present_or_null(self):
        body = client.get("/api/v1/moon-data", params=VALID_PARAMS).json()
        assert "moonrise" in body
        assert "moonset" in body

    def test_moonrise_moonset_include_timezone_offset(self):
        """For a non-UTC timezone the rise/set strings must carry an offset."""
        body = client.get("/api/v1/moon-data", params=VALID_PARAMS).json()
        for field in ("moonrise", "moonset"):
            if body[field] is not None:
                # A timezone-aware ISO string contains "+" or ends with "Z"
                assert "+" in body[field] or body[field].endswith("Z"), (
                    f"{field} has no timezone offset: {body[field]}"
                )

    def test_different_timezones_give_different_rise_set_strings(self):
        """Same date+coordinates but different timezone → different ISO offsets."""
        params_ny = {**VALID_PARAMS, "timezone": "America/New_York"}
        params_jp = {**VALID_PARAMS, "timezone": "Asia/Tokyo"}

        body_ny = client.get("/api/v1/moon-data", params=params_ny).json()
        body_jp = client.get("/api/v1/moon-data", params=params_jp).json()

        if body_ny["moonrise"] and body_jp["moonrise"]:
            assert body_ny["moonrise"] != body_jp["moonrise"]


# ═══════════════════════════════════════════════════════════════════════════════
# 3 · Cache behaviour
# ═══════════════════════════════════════════════════════════════════════════════

class TestCacheBehaviour:
    def test_cache_is_populated_after_first_request(self):
        assert moon_cache.size == 0
        client.get("/api/v1/moon-data", params=VALID_PARAMS)
        assert moon_cache.size > 0

    def test_second_request_reuses_cache(self):
        client.get("/api/v1/moon-data", params=VALID_PARAMS)
        size_after_first = moon_cache.size

        client.get("/api/v1/moon-data", params=VALID_PARAMS)
        size_after_second = moon_cache.size

        assert size_after_first == size_after_second, (
            "Cache grew on the second identical request – entry was not reused"
        )

    def test_different_dates_produce_separate_cache_entries(self):
        params_a = {**VALID_PARAMS, "date": "2026-03-14"}
        params_b = {**VALID_PARAMS, "date": "2026-04-14"}

        client.get("/api/v1/moon-data", params=params_a)
        client.get("/api/v1/moon-data", params=params_b)

        assert moon_cache.size == 2


# ═══════════════════════════════════════════════════════════════════════════════
# 4 · Polar edge-case
# ═══════════════════════════════════════════════════════════════════════════════

class TestPolarEdgeCase:
    def test_north_pole_returns_200(self):
        params = {**VALID_PARAMS, "latitude": 90.0, "longitude": 0.0}
        resp = client.get("/api/v1/moon-data", params=params)
        assert resp.status_code == 200, resp.text

    def test_north_pole_moonrise_moonset_are_null_or_datetime(self):
        params = {**VALID_PARAMS, "latitude": 90.0, "longitude": 0.0}
        body = client.get("/api/v1/moon-data", params=params).json()
        for field in ("moonrise", "moonset"):
            assert body[field] is None or isinstance(body[field], str), (
                f"{field} has unexpected type: {type(body[field])}"
            )
