# --- AstroSync: Elite API Server v6.0 ---
from fastapi import FastAPI
from quantum_engine import calculate_quantum_state
from natal_chart import calculate_natal_chart, get_planet_meaning
from openai import OpenAI
from datetime import datetime
from compatibility import calculate_compatibility
import uvicorn
import sys
import os
from dotenv import load_dotenv

# Завантажуємо API ключ з .env
load_dotenv()

# Importing your custom modules
try:
    from numerology import (
        calculate_life_path, 
        get_personal_cycles,
        calculate_soul_number,
        calculate_personality_number,
        get_number_description
    )
    from astro_basic import get_zodiac_sign, get_moon_phase
    from astro_calendar import get_calendar_data, get_day_energy
    from destiny_matrix import get_full_destiny_matrix
except ImportError as e:
    print(f"❌ Error importing local modules: {e}")
    sys.exit(1)

app = FastAPI()

# !!! SECURE YOUR KEY !!!
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_smart_advice(name, zodiac, current_moon, p_day, p_year, language="en"):
    """Generates an elite strategy via OpenAI in selected language."""
    
    lang_instruction = "English" if language == "en" else "Ukrainian"
    
    system_prompt = f"You are an expert astro-strategist for the AstroSync app. Always respond in {lang_instruction}."
    user_prompt = f"""
    Client: {name}
    Zodiac: {zodiac}
    CONTEXT: Current Moon: {current_moon}, Personal Day: {p_day}, Personal Year: {p_year}.
    TASK: Write a 2-sentence strategy. Synthesize the moon and the day number.
    Tone: Professional, elite. 
    Language: {lang_instruction} (IMPORTANT: Reply ONLY in {lang_instruction}!)
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ OpenAI Error: {e}")
        return f"Focus on your personal power today (Day {p_day}). The universe supports your journey."

@app.get("/")
def home():
    return {"status": "AstroSync Online v6.0", "features": ["numerology", "astrology", "calendar"]}

@app.get("/horoscope")
def get_horoscope(name: str, date: str, language: str = "en"):
    """Основний ендпоінт з повною інформацією"""
    # 1. Format dates (YYYY/MM/DD for flatlib)
    birth_date_slash = date.replace("-", "/")
    current_date_slash = datetime.now().strftime("%Y/%m/%d")
    
    # 2. Calculations
    lp_number = calculate_life_path(date)
    soul_number = calculate_soul_number(name)
    personality_number = calculate_personality_number(name)
    
    zodiac = get_zodiac_sign(birth_date_slash)
    natal_moon = get_moon_phase(birth_date_slash)
    current_moon = get_moon_phase(current_date_slash)
    cycles = get_personal_cycles(date)
    
    # 3. AI Insight
    ai_advice = generate_smart_advice(name, zodiac, current_moon, cycles['personal_day'], cycles['personal_year'], language)
    return {
        "user_name": name,
        "numerology": {
            "life_path": lp_number,
            "soul_number": soul_number,
            "personality_number": personality_number,
            "personal_day": cycles['personal_day'],
            "personal_month": cycles['personal_month'],
            "personal_year": cycles['personal_year'],
            # Додаємо описи
            "life_path_description": get_number_description(lp_number, "life_path", language),
"soul_description": get_number_description(soul_number, "soul", language),
"personality_description": get_number_description(personality_number, "personality", language),
"day_description": get_number_description(cycles['personal_day'], "day", language)
        },
        "astrology": {
            "sun_sign": zodiac,
            "natal_moon_phase": natal_moon,
            "current_moon_phase": current_moon,
            "element": "Earth" if zodiac in ['Taurus', 'Virgo', 'Capricorn'] else "Water/Air/Fire"
        },
        "advice": ai_advice
    }

@app.get("/calendar")
def get_calendar(year: int, month: int):
    """
    Повертає календар на місяць з астро-подіями
    Використання: /calendar?year=2026&month=2
    """
    calendar_data = get_calendar_data(year, month)
    return {
        "year": year,
        "month": month,
        "days": calendar_data
    }

@app.get("/day-energy")
def get_today_energy():
    """Повертає енергію поточного дня"""
    today = datetime.now().strftime("%Y/%m/%d")
    energy = get_day_energy(today)
    
    return {
        "date": today.replace("/", "-"),
        "energy": energy
    }

@app.get("/natal-chart")
def get_natal_chart(
    birth_date: str,
    birth_time: str,
    latitude: float,
    longitude: float,
    language: str = "en"
):
    """
    Розраховує натальну карту
    
    Parameters:
    - birth_date: YYYY-MM-DD
    - birth_time: HH:MM
    - latitude: широта
    - longitude: довгота
    - language: мова (en, uk)
    """
    
    # Розраховуємо натальну карту
    chart = calculate_natal_chart(birth_date, birth_time, latitude, longitude)
    
    if not chart:
        return {"error": "Could not calculate natal chart"}
    
    # Додаємо трактування для кожної планети
    for planet_name, planet_data in chart['planets'].items():
        meaning = get_planet_meaning(
            planet_name,
            planet_data['sign'],
            planet_data['house'],
            language
        )
        planet_data['meaning'] = meaning
    
    return {
        "natal_chart": chart,
        "birth_info": {
            "date": birth_date,
            "time": birth_time,
            "latitude": latitude,
            "longitude": longitude
        }
    }
@app.post("/compatibility")
def get_compatibility(data: dict):
    """
    Розраховує сумісність між двома людьми
    
    Body:
    {
        "person1": {
            "name": "Alex",
            "birth_date": "1990-05-20",
            "birth_time": "14:30",
            "latitude": 50.45,
            "longitude": 30.52
        },
        "person2": {
            "name": "Jordan",
            "birth_date": "1992-08-15",
            "birth_time": "10:00",
            "latitude": 40.71,
            "longitude": -74.00
        }
    }
    """
    try:
        person1 = data.get('person1')
        person2 = data.get('person2')
        
        if not person1 or not person2:
            return {"error": "Missing person1 or person2 data"}
        
        result = calculate_compatibility(person1, person2)
        
        if not result:
            return {"error": "Could not calculate compatibility"}
        
        return result
        
    except Exception as e:
        return {"error": str(e)}
  
@app.get("/destiny-matrix")
def get_destiny_matrix(birth_date: str, language: str = "en"):
    result = get_full_destiny_matrix(birth_date, language)
    if not result:
        return {"error": "Could not calculate destiny matrix"}
    return result
@app.get("/quantum-field")
def get_quantum_field(latitude: float = 50.45, longitude: float = 30.52):
    """
    Повертає поточний квантово-кабалістичний стан.
    Доступно тільки для ELITE.
    """
    result = calculate_quantum_state(latitude, longitude)
    if not result:
        return {"error": "Quantum field fluctuation error"}
    return result
    
if __name__ == "__main__":
    import os
    # Хмара дасть свій порт через змінну середовища PORT.
    # Якщо її немає (локально), то буде 8000.
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting AstroSync on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)