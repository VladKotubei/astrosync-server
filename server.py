# --- AstroSync: Elite API Server v6.0 ---
from fastapi import FastAPI
from quantum_engine import calculate_quantum_state
from natal_chart import calculate_natal_chart, get_planet_meaning
from openai import OpenAI
from datetime import datetime
from compatibility import calculate_compatibility
from datetime import datetime
import json
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
    """Generates an elite structured strategy via OpenAI."""
    
    # Головна мова додатку - Англійська. Українська тільки якщо чітко вказано "uk"
    lang_instruction = "Ukrainian" if language == "uk" else "English"
    
    system_prompt = f"You are an elite astrologer and life coach for successful individuals. Your primary language is English, but you must respond EXACTLY in {lang_instruction}."
    
    user_prompt = f"""
    Client Data:
    - Name: {name}
    - Zodiac Sign: {zodiac}
    - Current Moon Phase: {current_moon}
    - Numerology Personal Day: {p_day}
    - Numerology Personal Year: {p_year}

    Task: Write a short, powerful, and stylish daily forecast in {lang_instruction}.
    Do not use fluff, clichés, or generic greetings. Be specific, actionable, and profound.
    
    You MUST use exactly this structure with these emojis (translate the category names if the requested language is {lang_instruction}, but keep the emojis):

    ⚡️ Energy: (1 short sentence about the main vibe based on the Moon and Personal Day)
    🎯 Focus: (What specifically to do today / where to direct energy)
    🚫 Avoid: (What actions, thoughts, or people to stay away from today)
    💡 Insight: (A deep, philosophical or motivational thought of the day)
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7 # Трохи креативності, але без "галюцинацій"
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ OpenAI Error: {e}")
        # Якщо сталася помилка сервера, віддаємо красиву заглушку правильною мовою
        if language == "uk":
            return "⚡️ Енергія: Фокус на внутрішній силі.\n🎯 Фокус: Дисципліна та структура.\n🚫 Уникати: Хаосу та відволікань.\n💡 Інсайт: Всесвіт підтримує ваш шлях, коли ви знаєте свою мету."
        return "⚡️ Energy: Focus on your personal power.\n🎯 Focus: Discipline and structure.\n🚫 Avoid: Chaos and distractions.\n💡 Insight: The universe supports your journey when you know your destination."

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
    tz: str = "UTC",  # Додали підтримку часового поясу!
    language: str = "en"
):
    """
    Розраховує натальну карту та віддає її у форматі для iOS (big_three + planets)
    """
    # 1. Рахуємо карту через твій модуль
    chart = calculate_natal_chart(birth_date, birth_time, latitude, longitude)
    
    if not chart:
        return {"error": "Could not calculate natal chart"}

    # 2. Функція-помічник для форматування кожної планети
    def format_planet(name, data):
        house_str = data.get("house", "House_1")
        # Перетворюємо "House_10" на число 10
        house_num = int(house_str.split("_")[1]) if "_" in house_str else 1
        
        # Переклад назв планет для української
        uk_names = {
            "Sun": "Сонце", "Moon": "Місяць", "Mercury": "Меркурій",
            "Venus": "Венера", "Mars": "Марс", "Jupiter": "Юпітер", "Saturn": "Сатурн"
        }
        local_name = uk_names.get(name, name) if language == "uk" else name
        
        return {
            "name": local_name,
            "sign": data["sign"],
            "house": house_num,
            "degree": data.get("degree", 0.0),
            "is_retrograde": False, 
            "description": get_planet_meaning(name, data["sign"], house_str, language)
        }

    planets_data = chart.get("planets", {})
    
    # 3. Збираємо Велику Трійку (Сонце, Місяць, Асцендент)
    big_three = []
    if "Sun" in planets_data:
        big_three.append(format_planet("Sun", planets_data["Sun"]))
    if "Moon" in planets_data:
        big_three.append(format_planet("Moon", planets_data["Moon"]))
        
    asc_sign = chart.get("ascendant", {}).get("sign", "Unknown")
    asc_degree = chart.get("ascendant", {}).get("degree", 0.0)
    asc_desc = f"Ваш Асцендент у знаку {asc_sign} формує вашу зовнішню особистість." if language == "uk" else f"Your Ascendant in {asc_sign} shapes your outward personality."
    
    big_three.append({
        "name": "Асцендент" if language == "uk" else "Ascendant",
        "sign": asc_sign,
        "house": 1,
        "degree": asc_degree,
        "is_retrograde": False,
        "description": asc_desc
    })

    # 4. Збираємо інші планети
    other_planets = []
    for p in ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        if p in planets_data:
            other_planets.append(format_planet(p, planets_data[p]))

    # 5. Віддаємо ідеальний формат!
    return {
        "big_three": big_three,
        "planets": other_planets
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
# --- SMART PLANNER (ШІ-Астролог для задач) ---

def evaluate_planner_task(task: str, target_date: str, birth_date: str, language: str = "en"):
    """
    Аналізує конкретну задачу на конкретний день і повертає JSON з оцінкою (0-100).
    """
    lang_instruction = "Ukrainian" if language == "uk" else "English"
    
    system_prompt = f"""You are an elite astrological time-management coach. 
    You evaluate if a specific date is favorable for a user's specific task based on astrology and numerology.
    You MUST respond ONLY with a valid JSON object. Do not include any markdown formatting like ```json."""
    
    user_prompt = f"""
    Task to evaluate: "{task}"
    Target Date for Task: {target_date}
    User's Birth Date: {birth_date}
    
    Analyze the astrological and numerological compatibility of this task for this specific date.
    Return a JSON object with EXACTLY these three keys:
    1. "score": an integer from 0 to 100 representing how favorable the day is (100 is perfect, 0 is terrible).
    2. "verdict": 2 short sentences explaining the astrological/numerological reason why, in {lang_instruction}. Use 1-2 emojis.
    3. "advice": 1 practical sentence on what to do (e.g., "Do it confidently" or "Reschedule to next week"), in {lang_instruction}.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=300,
            temperature=0.7,
            response_format={"type": "json_object"} # ⬅️ Змушуємо ШІ віддавати чистий код
        )
        # Перетворюємо відповідь ШІ у словник Python
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"⚠️ Planner AI Error: {e}")
        # Запасний варіант, якщо ШІ не відповів
        return {
            "score": 50,
            "verdict": "Енергія дня нейтральна. Зірки радять покладатися на власну інтуїцію." if language == "uk" else "The energy is neutral. Rely on your intuition.",
            "advice": "Дійте обережно і майте запасний план." if language == "uk" else "Proceed with caution and have a backup plan."
        }

@app.post("/smart-planner")
def smart_planner_endpoint(data: dict):
    """
    Ендпоінт для iOS додатку. Приймає JSON із задачею і повертає аналіз.
    """
    task = data.get("task")
    target_date = data.get("target_date")
    birth_date = data.get("birth_date")
    language = data.get("language", "en")
    
    if not all([task, target_date, birth_date]):
        return {"error": "Missing required fields (task, target_date, birth_date)"}
        
    result = evaluate_planner_task(task, target_date, birth_date, language)
    return result
@app.get("/daily-insight")
def get_daily_insight(date: str, language: str = "en"):
    """
    Генерує унікальну пораду від ШІ для конкретного дня у календарі.
    Доступно тільки для PRO та ELITE користувачів додатку.
    """
    lang_instruction = "Ukrainian" if language == "uk" else "English"
    system_prompt = f"You are an elite astro-coach. Respond strictly in {lang_instruction}."
    
    user_prompt = f"""
    Analyze the general astrological energy for the date: {date}.
    Write a short, inspiring 2-sentence forecast for this specific day. 
    Use 1-2 emojis. Keep it professional and actionable. Do not use generic greetings.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        insight = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Daily Insight AI Error: {e}")
        insight = "Енергія цього дня вимагає балансу та обережності у прийнятті рішень." if language == "uk" else "The energy of this day requires balance and caution in decision making."
        
    return {"date": date, "insight": insight}
@app.post('/ai-astrologer')
def ai_astrologer(data: dict):
    try:
        question = data.get('question', '')
        name = data.get('name', 'Мандрівник')
        language = data.get('language', 'uk')
        user_context = data.get('user_context', 'No data') # Отримуємо контекст
        
        lang_prompt = "Ukrainian" if language == "uk" else "English"
        
        system_prompt = f"""
        You are the ultimate AstroSync App Expert and Destiny Matrix Guide.
        Your main job is to explain the user's personal esoteric calculations.
        
        Here is the user's personal calculated data sent from the app:
        {user_context}
        
        RULES & SAFETY:
        1. IF the user asks about their Matrix, destiny, karmic tail, or family lines, ONLY use the numbers provided in the context above! Do not invent numbers.
        2. IF the user_context says "No data", DO NOT invent or imagine any Tarot cards. Explicitly tell the user: "Щоб я міг точно розрахувати вашу Матрицю Долі, будь ласка, переконайтеся, що ви ввели правильну дату народження у своєму профілі." (Translate to English if needed).
        3. Answer strictly in {lang_prompt}.
        4. Keep it engaging, empathetic, and structured.
        5. CRITICAL SAFETY: Never encourage self-harm, violence, or dangerous financial/medical decisions.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.4, # Зменшили креативність, щоб він говорив чітко по фактах
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        return {"answer": answer}
        
    except Exception as e:
        print(f"❌ Error in Astro Expert: {e}")
        error_msg = "Експерт зараз аналізує дані інших зірок. Спробуйте через хвилинку." if data.get('language') == "uk" else "The expert is busy. Try again in a minute."
        return {"answer": error_msg}
    
if __name__ == "__main__":
    import os
    # Хмара дасть свій порт через змінну середовища PORT.
    # Якщо її немає (локально), то буде 8000.
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting AstroSync on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)