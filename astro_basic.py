# --- AstroSync: Astro Engine vFinal ---
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const

def get_zodiac_sign(date_string):
    date = Datetime(date_string, '12:00', '+00:00')
    pos = GeoPos(0, 0)
    chart = Chart(date, pos)
    sun = chart.get(const.SUN)
    return sun.sign

def get_moon_phase(date_string):
    # Розрахунок фази
    date = Datetime(date_string, '12:00', '+00:00')
    pos = GeoPos(0, 0)
    chart = Chart(date, pos)
    sun = chart.get(const.SUN)
    moon = chart.get(const.MOON)
    
    # Кут між Сонцем і Місяцем
    phase_angle = (moon.lon - sun.lon) % 360
    
    # Повертаємо назву та емодзі
    if phase_angle < 45: return "New Moon 🌑"
    elif phase_angle < 90: return "Waxing Crescent 🌒"
    elif phase_angle < 135: return "First Quarter 🌓"
    elif phase_angle < 180: return "Waxing Gibbous 🌔"
    elif phase_angle < 225: return "Full Moon 🌕"
    elif phase_angle < 270: return "Waning Gibbous 🌖"
    elif phase_angle < 315: return "Last Quarter 🌗"
    else: return "Waning Crescent 🌘"