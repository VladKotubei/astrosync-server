# --- AstroSync: Calendar Module ---
import calendar
import hashlib
from datetime import date as date_type
from typing import Optional, List

from app.services.transit_calculator import check_retrograde_for_calendar, get_sign_transits

def get_moon_phase_emoji(year, month, day):
    """
    Точний розрахунок фази місяця на основі числа Юліанського дня (Jean Meeus).
    Не потребує зовнішніх бібліотек.
    """
    y, m = year, month
    if m <= 2:
        y -= 1
        m += 12
    A = int(y / 100)
    B = 2 - A + int(A / 4)
    jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + day + B - 1524.5

    # Еталонний новий місяць: 6 січня 2000, 18:14 UTC → JD 2451549.75
    known_new_moon_jd = 2451549.75
    synodic_month = 29.53058867

    days_since = jd - known_new_moon_jd
    phase = (days_since % synodic_month) / synodic_month
    if phase < 0:
        phase += 1.0

    if phase < 0.0625 or phase >= 0.9375:
        return "🌑"
    elif phase < 0.1875:
        return "🌒"
    elif phase < 0.3125:
        return "🌓"
    elif phase < 0.4375:
        return "🌔"
    elif phase < 0.5625:
        return "🌕"
    elif phase < 0.6875:
        return "🌖"
    elif phase < 0.8125:
        return "🌗"
    else:
        return "🌘"

def get_day_status(day):
    """
    Визначає "світлофор" дня на основі нумерології або астрології.
    """
    good_days = [3, 7, 12, 18, 21, 25, 28]
    bad_days = [4, 9, 13, 19, 26]
    if day in good_days: return "good"
    if day in bad_days: return "bad"
    return "neutral"

_LUNAR_EVENT_MAP = {
    "🌑": "New Moon",
    "🌓": "First Quarter",
    "🌕": "Full Moon",
    "🌗": "Last Quarter",
}


_TAG_POOL = ["Finance", "Love", "Caution", "Career", "Health",
             "Creativity", "Travel", "Communication", "Spiritual", "Rest"]


def _get_lunar_event(emoji: Optional[str]) -> Optional[str]:
    if emoji is None:
        return None
    return _LUNAR_EVENT_MAP.get(emoji)


def _get_energy_tags(d: date_type, status: str, retro_phase: Optional[str]) -> Optional[List[str]]:
    seed = int(hashlib.md5(d.isoformat().encode()).hexdigest(), 16)

    tags: List[str] = []

    if status == "good":
        tags.append("Finance")
    elif status == "bad":
        tags.append("Caution")

    if retro_phase in ("pre_shadow", "peak", "post_shadow"):
        tags.append("Caution")
        tags.append("Communication")

    if d.weekday() == 4:  # Friday → Venus day
        tags.append("Love")
    if d.weekday() == 1:  # Tuesday → Mars day
        tags.append("Career")

    remaining = [t for t in _TAG_POOL if t not in tags]
    extra_count = (seed % 2) + 1
    for i in range(extra_count):
        tags.append(remaining[(seed >> (i + 4)) % len(remaining)])

    seen = set()
    unique = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            unique.append(t)

    return unique if unique else None


def get_calendar_data(year: int, month: int, language: str = "en") -> list:
    """Generate the array of calendar days for a given month.

    Retrograde phases and planetary sign transits are computed dynamically
    via the Swiss Ephemeris (pyswisseph) — works for any year, past or future.
    """
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(year, month)

    result = []
    for week in month_days:
        for date_obj in week:
            is_current = date_obj.month == month

            if is_current:
                retro_label, retro_phase, extra_events = (
                    check_retrograde_for_calendar(date_obj, language)
                )
                sign_transits = get_sign_transits(date_obj)
                planetary_events = sign_transits + extra_events
            else:
                retro_label, retro_phase = None, None
                planetary_events = None

            moon_emoji = (
                get_moon_phase_emoji(date_obj.year, date_obj.month, date_obj.day)
                if is_current else None
            )
            day_status = get_day_status(date_obj.day) if is_current else "neutral"

            result.append({
                "date": date_obj.strftime("%Y-%m-%d"),
                "day": date_obj.day,
                "is_current_month": is_current,
                "status": day_status,
                "moon_phase": moon_emoji,
                "lunar_event": _get_lunar_event(moon_emoji) if is_current else None,
                "retrograde": retro_label,
                "retrograde_phase": retro_phase,
                "planetary_events": planetary_events,
                "energy_tags": (
                    _get_energy_tags(date_obj, day_status, retro_phase)
                    if is_current else None
                ),
            })

    return result

def get_day_energy(date_str: str, language: str = "en") -> str:
    """Повертає короткий опис енергії конкретного дня"""
    if language == "uk":
        return "Сьогодні ідеальний день для початку нових проектів та фінансових інвестицій."
    return "Today is a perfect day for starting new projects and making financial investments."