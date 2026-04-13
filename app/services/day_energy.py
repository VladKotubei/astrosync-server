from datetime import datetime, date
from app.services.destiny_matrix import reduce_to_arcana
from app.services.astro_basic import get_moon_phase
from app.services.cache import daily_cache

ZONE_ORDER = ["karma", "love", "finance", "communication", "growth", "challenge", "mission"]

MOON_PHASE_MODIFIER = {
    "New Moon": 1,
    "Waxing Crescent": 2,
    "First Quarter": 3,
    "Waxing Gibbous": 3,
    "Full Moon": 4,
    "Waning Gibbous": 3,
    "Last Quarter": 2,
    "Waning Crescent": 1
}


def calculate_global_day_energy(target_date: str = None) -> dict:
    """
    Calculate global energy for a given date.
    Same result for all users on the same day.
    Cached for 24 hours.
    """
    if target_date is None:
        target_date = date.today().isoformat()

    cache_key = f"day_energy:{target_date}"
    cached = daily_cache.get(cache_key)
    if cached:
        return cached

    digits = target_date.replace("-", "")
    date_sum = sum(int(d) for d in digits)

    # get_moon_phase() returns a string like "New Moon 🌑" — strip the emoji
    # Convert YYYY-MM-DD to YYYY/MM/DD for flatlib compatibility
    flatlib_date = target_date.replace("-", "/")
    moon_raw = get_moon_phase(flatlib_date)
    moon_phase_name = moon_raw.rsplit(" ", 1)[0] if moon_raw else "New Moon"
    moon_modifier = MOON_PHASE_MODIFIER.get(moon_phase_name, 2)

    raw_energy = date_sum + moon_modifier
    energy_arcana = reduce_to_arcana(raw_energy)

    zone_index = energy_arcana % 7
    active_zone = ZONE_ORDER[zone_index]

    result = {
        "date": target_date,
        "energy_arcana": energy_arcana,
        "active_zone": active_zone,
        "moon_phase": moon_phase_name,
        "moon_modifier": moon_modifier,
        "intensity": round(min(energy_arcana / 22.0, 1.0), 2)
    }

    daily_cache.set(cache_key, result)
    return result
