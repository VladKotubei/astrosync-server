# --- AstroSync: Calendar Module ---
import calendar
from datetime import datetime

def get_moon_phase_emoji(year, month, day):
    """
    Спрощений алгоритм для визначення фази місяця (для візуалізації).
    В реальному житті краще використовувати бібліотеку ephem або skyfield.
    """
    # Це спрощена імітація для демо-цілей. 
    # Вона розкидає фази так, щоб вони красиво виглядали в місяці.
    if day == 15: return "🌕" # Full Moon
    if day == 1: return "🌑"  # New Moon
    if day == 8: return "🌓"  # First Quarter
    if day == 22: return "🌗" # Last Quarter
    return None

def get_day_status(day):
    """
    Визначає "світлофор" дня на основі нумерології або астрології.
    """
    # Спрощена імітація розрахунку енергії
    good_days = [3, 7, 12, 18, 21, 25, 28]
    bad_days = [4, 9, 13, 19, 26]
    
    if day in good_days: return "good"
    if day in bad_days: return "bad"
    return "neutral"

def check_retrograde(year, month, day, language="en"):
    """
    Перевірка на ретроградні планети.
    """
    # Імітація: нехай з 10 по 20 число поточного місяця буде Ретроградний Меркурій
    if 10 <= day <= 20:
        return "Mercury Retrograde" if language == "en" else "Ретроградний Меркурій"
    return None

def get_calendar_data(year: int, month: int, language: str = "en") -> list:
    """
    Генерує масив днів для конкретного місяця.
    """
    cal = calendar.Calendar(firstweekday=0) # Понеділок - перший день тижня
    month_days = cal.monthdatescalendar(year, month)
    
    result = []
    
    for week in month_days:
        for date_obj in week:
            # Нам потрібні дні і з попереднього/наступного місяця, щоб заповнити сітку 7x5
            is_current_month = (date_obj.month == month)
            
            day_data = {
                "date": date_obj.strftime("%Y-%m-%d"),
                "day": date_obj.day,
                "is_current_month": is_current_month,
                "status": get_day_status(date_obj.day) if is_current_month else "neutral",
                "moon_phase": get_moon_phase_emoji(date_obj.year, date_obj.month, date_obj.day) if is_current_month else None,
                "retrograde": check_retrograde(date_obj.year, date_obj.month, date_obj.day, language) if is_current_month else None
            }
            result.append(day_data)
            
    return result

def get_day_energy(date_str: str, language: str = "en") -> str:
    """Повертає короткий опис енергії конкретного дня"""
    if language == "uk":
        return "Сьогодні ідеальний день для початку нових проектів та фінансових інвестицій."
    return "Today is a perfect day for starting new projects and making financial investments."