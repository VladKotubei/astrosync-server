# --- AstroSync: Astro Calendar Module v1.0 ---
from datetime import datetime, timedelta
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const

def get_moon_phase_for_date(date_string):
    """Повертає фазу місяця для конкретної дати"""
    date = Datetime(date_string, '12:00', '+00:00')
    pos = GeoPos(0, 0)
    chart = Chart(date, pos)
    sun = chart.get(const.SUN)
    moon = chart.get(const.MOON)
    
    phase_angle = (moon.lon - sun.lon) % 360
    
    if phase_angle < 45: return "New Moon"
    elif phase_angle < 90: return "Waxing Crescent"
    elif phase_angle < 135: return "First Quarter"
    elif phase_angle < 180: return "Waxing Gibbous"
    elif phase_angle < 225: return "Full Moon"
    elif phase_angle < 270: return "Waning Gibbous"
    elif phase_angle < 315: return "Last Quarter"
    else: return "Waning Crescent"

def is_favorable_day(date_string):
    """
    Визначає чи день сприятливий (для Basic тарифу - проста логіка)
    
    Сприятливі дні:
    - Waxing Moon (зростаючий місяць) - добре для початку справ
    - Full Moon (повня) - пік енергії
    
    Несприятливі дні:
    - Waning Moon (спадаючий місяць) - час завершення
    - New Moon (молодик) - низька енергія
    """
    phase = get_moon_phase_for_date(date_string)
    
    favorable_phases = ["Waxing Crescent", "First Quarter", "Waxing Gibbous", "Full Moon"]
    
    return phase in favorable_phases

def get_day_energy(date_string):
    """
    Повертає рівень енергії дня та рекомендацію
    """
    phase = get_moon_phase_for_date(date_string)
    
    energy_map = {
        "New Moon": {
            "energy": "low",
            "level": 30,
            "color": "gray",
            "advice": "Rest and reflect. Set intentions for the lunar cycle ahead."
        },
        "Waxing Crescent": {
            "energy": "rising",
            "level": 50,
            "color": "green",
            "advice": "Take action on new projects. Energy is building."
        },
        "First Quarter": {
            "energy": "active",
            "level": 70,
            "color": "green",
            "advice": "Push through challenges. Your power is strong."
        },
        "Waxing Gibbous": {
            "energy": "peak",
            "level": 85,
            "color": "green",
            "advice": "Refine and perfect. You're close to manifestation."
        },
        "Full Moon": {
            "energy": "maximum",
            "level": 100,
            "color": "orange",
            "advice": "Peak power day! Complete important tasks and celebrate."
        },
        "Waning Gibbous": {
            "energy": "releasing",
            "level": 75,
            "color": "yellow",
            "advice": "Share your wisdom. Let go of what doesn't serve you."
        },
        "Last Quarter": {
            "energy": "declining",
            "level": 50,
            "color": "yellow",
            "advice": "Review and release. Prepare for the next cycle."
        },
        "Waning Crescent": {
            "energy": "resting",
            "level": 35,
            "color": "gray",
            "advice": "Rest and recover. Final release before new beginnings."
        }
    }
    
    return energy_map.get(phase, energy_map["New Moon"])

def get_calendar_data(year, month):
    """
    Повертає дані календаря на місяць
    Для Basic - тільки загальні астро-події
    """
    from calendar import monthrange
    
    days_in_month = monthrange(year, month)[1]
    calendar_data = []
    
    for day in range(1, days_in_month + 1):
        date_str = f"{year}/{month:02d}/{day:02d}"
        
        energy = get_day_energy(date_str)
        phase = get_moon_phase_for_date(date_str)
        
        calendar_data.append({
            "day": day,
            "date": date_str.replace("/", "-"),
            "moon_phase": phase,
            "is_favorable": is_favorable_day(date_str),
            "energy_level": energy["level"],
            "energy_color": energy["color"],
            "advice": energy["advice"]
        })
    
    return calendar_data

# --- Тест ---
if __name__ == "__main__":
    print("📅 Тестуємо календар...")
    
    # Поточний місяць
    now = datetime.now()
    data = get_calendar_data(now.year, now.month)
    
    print(f"\nКалендар на {now.year}-{now.month:02d}:")
    print("-" * 70)
    
    for day_data in data[:7]:  # Показуємо перші 7 днів
        fav = "✅" if day_data["is_favorable"] else "⚠️"
        print(f"{fav} {day_data['date']} | {day_data['moon_phase']:20} | Energy: {day_data['energy_level']}%")