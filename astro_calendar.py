# --- AstroSync: Calendar Module ---
import calendar
import math
from datetime import date as date_type, datetime

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

# Точні дати ретроградного Меркурія 2026:
# (початок_тіні, початок_піку, кінець_піку, кінець_тіні)
_MERCURY_RETRO_2026 = [
    (date_type(2026, 2, 12), date_type(2026, 2, 26), date_type(2026, 3, 20), date_type(2026, 4,  3)),
    (date_type(2026, 6, 15), date_type(2026, 6, 29), date_type(2026, 7, 23), date_type(2026, 8,  6)),
    (date_type(2026, 10, 10), date_type(2026, 10, 24), date_type(2026, 11, 13), date_type(2026, 11, 27)),
]

def check_retrograde(year, month, day, language="en"):
    """
    Повертає (label, phase) де phase — одне з: "none", "pre_shadow", "peak", "post_shadow".
    Тіньові фази ~2 тижні до і після кожного піку.
    """
    if year != 2026:
        return None, "none"

    d = date_type(year, month, day)
    for pre_start, peak_start, peak_end, post_end in _MERCURY_RETRO_2026:
        if pre_start <= d < peak_start:
            label = "Mercury Shadow ☿" if language == "en" else "Тінь Меркурія ☿"
            return label, "pre_shadow"
        elif peak_start <= d <= peak_end:
            label = "Mercury Retrograde ☿" if language == "en" else "Ретроградний Меркурій ☿"
            return label, "peak"
        elif peak_end < d <= post_end:
            label = "Mercury Shadow ☿" if language == "en" else "Тінь Меркурія ☿"
            return label, "post_shadow"

    return None, "none"

def get_calendar_data(year: int, month: int, language: str = "en") -> list:
    """
    Генерує масив днів для конкретного місяця.
    """
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(year, month)

    result = []
    for week in month_days:
        for date_obj in week:
            is_current_month = (date_obj.month == month)

            if is_current_month:
                retro_label, retro_phase = check_retrograde(date_obj.year, date_obj.month, date_obj.day, language)
            else:
                retro_label, retro_phase = None, "none"

            day_data = {
                "date": date_obj.strftime("%Y-%m-%d"),
                "day": date_obj.day,
                "is_current_month": is_current_month,
                "status": get_day_status(date_obj.day) if is_current_month else "neutral",
                "moon_phase": get_moon_phase_emoji(date_obj.year, date_obj.month, date_obj.day) if is_current_month else None,
                "retrograde": retro_label,
                "retrograde_phase": retro_phase,
            }
            result.append(day_data)

    return result

def get_day_energy(date_str: str, language: str = "en") -> str:
    """Повертає короткий опис енергії конкретного дня"""
    if language == "uk":
        return "Сьогодні ідеальний день для початку нових проектів та фінансових інвестицій."
    return "Today is a perfect day for starting new projects and making financial investments."