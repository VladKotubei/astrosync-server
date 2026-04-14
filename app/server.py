# --- AstroSync: Elite API Server v6.0 ---
# NOTE: Legacy endpoints (/, /horoscope, etc.) remain at root for backward compatibility.
# All NEW endpoints MUST use /api/v1/ prefix.
from fastapi import FastAPI
from pydantic import BaseModel
from app.services.quantum_engine import calculate_quantum_state, generate_daily_timeline
from app.services.natal_chart import calculate_natal_chart, get_planet_meaning
from openai import OpenAI
from app.services.palm_reader import validate_palm_image, visual_scan, deep_scan, guest_compatibility_scan
from datetime import datetime
from app.services.compatibility import calculate_compatibility, calculate_lite_compatibility
from app.services.angel_numbers import calculate_angel_number
from app.services.shared_matrix import calculate_shared_matrix
from app.services.day_energy import calculate_global_day_energy
from app.services.cache import permanent_cache, daily_cache
import json
import uvicorn
import sys
import os
from dotenv import load_dotenv
from app.api.lunar_engine.routers.moon_data import router as moon_data_router
from app.api.lunar_engine.routers.moon_favorability import router as moon_favorability_router

# Завантажуємо API ключ з .env
load_dotenv()

# Importing your custom modules
try:
    from app.services.numerology import (
        calculate_life_path, 
        get_personal_cycles,
        calculate_soul_number,
        calculate_personality_number,
        get_number_description
    )
    from app.services.astro_basic import get_zodiac_sign, get_moon_phase
    from app.services.astro_calendar import get_calendar_data, get_day_energy
    from app.services.destiny_matrix import get_full_destiny_matrix
except ImportError as e:
    print(f"❌ Error importing local modules: {e}")
    sys.exit(1)

app = FastAPI()
app.include_router(moon_data_router)
app.include_router(moon_favorability_router)

# !!! SECURE YOUR KEY !!!
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 🌍 Словник підтримуваних мов
LANGUAGES = {
    "en": "English",
    "uk": "Ukrainian",
    "es": "Spanish",
    "it": "Italian",
    "de": "German",
    "pl": "Polish",
    "ru": "Russian"
}

def generate_smart_advice(name, zodiac, current_moon, p_day, p_year, language="en", palm_context=None):
    """Generates an elite structured strategy via OpenAI."""
    
    # Визначаємо мову для ШІ
    lang_instruction = LANGUAGES.get(language, "English")
    
    system_prompt = f"You are an elite astrologer and life coach for successful individuals. Your primary language is English, but you must respond EXACTLY in {lang_instruction}."
    
    palm_block = ""
    if palm_context:
        palm_block = f"""
    Palm Reading Context (from biometric scan):
    {palm_context}
    
    IMPORTANT: Naturally weave palm reading insights into the forecast.
    For example: "Given your strong Mars line, today's energy supports bold decisions..."
    Do NOT make the palm reading the main focus — it should enhance the existing forecast.
    """

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
    {palm_block}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7 
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ OpenAI Error: {e}")
        # Красиві заглушки на випадок помилки сервера OpenAI різними мовами
        fallbacks = {
            "en": "⚡️ Energy: Focus on your personal power.\n🎯 Focus: Discipline and structure.\n🚫 Avoid: Chaos and distractions.\n💡 Insight: The universe supports your journey when you know your destination.",
            "uk": "⚡️ Енергія: Фокус на внутрішній силі.\n🎯 Фокус: Дисципліна та структура.\n🚫 Уникати: Хаосу та відволікань.\n💡 Інсайт: Всесвіт підтримує ваш шлях, коли ви знаєте свою мету.",
            "es": "⚡️ Energía: Concéntrate en tu fuerza interior.\n🎯 Enfoque: Disciplina y estructura.\n🚫 Evitar: Caos y distracciones.\n💡 Perspicacia: El universo te apoya cuando conoces tu destino.",
            "it": "⚡️ Energia: Concentrati sulla tua forza interiore.\n🎯 Focus: Disciplina e struttura.\n🚫 Evita: Caos e distrazioni.\n💡 Intuizione: L'universo ti supporta quando conosci la tua meta.",
            "de": "⚡️ Energie: Fokus auf deine innere Kraft.\n🎯 Fokus: Disziplin und Struktur.\n🚫 Vermeiden: Chaos und Ablenkungen.\n💡 Erkenntnis: Das Universum unterstützt deinen Weg, wenn du dein Ziel kennst.",
            "pl": "⚡️ Energia: Skup się na swojej wewnętrznej sile.\n🎯 Cel: Dyscyplina i struktura.\n🚫 Unikaj: Chaosu i rozpraszaczy.\n💡 Refleksja: Wszechświat wspiera twoją podróż, gdy znasz swój cel.",
            "ru": "⚡️ Энергия: Фокус на внутренней силе.\n🎯 Фокус: Дисциплина и структура.\n🚫 Избегать: Хаоса и отвлечений.\n💡 Инсайт: Вселенная поддерживает ваш путь, когда вы знаете свою цель."
        }
        return fallbacks.get(language, fallbacks["en"])

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "7.0", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
def home():
    return {"status": "AstroSync Online v6.0", "features": ["numerology", "astrology", "calendar"]}

@app.get("/horoscope")
def get_horoscope(name: str, date: str, language: str = "en", palm_context: str = None):
    """Основний ендпоінт з повною інформацією"""
    birth_date_slash = date.replace("-", "/")
    current_date_slash = datetime.now().strftime("%Y/%m/%d")
    
    lp_number = calculate_life_path(date)
    soul_number = calculate_soul_number(name)
    personality_number = calculate_personality_number(name)
    
    zodiac = get_zodiac_sign(birth_date_slash)
    natal_moon = get_moon_phase(birth_date_slash)
    current_moon = get_moon_phase(current_date_slash)
    cycles = get_personal_cycles(date)
    
    ai_advice = generate_smart_advice(name, zodiac, current_moon, cycles['personal_day'], cycles['personal_year'], language, palm_context)
    return {
        "user_name": name,
        "numerology": {
            "life_path": lp_number,
            "soul_number": soul_number,
            "personality_number": personality_number,
            "personal_day": cycles['personal_day'],
            "personal_month": cycles['personal_month'],
            "personal_year": cycles['personal_year'],
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
def get_calendar(year: int, month: int, language: str = "en"):
    calendar_data = get_calendar_data(year, month, language)
    return {"year": year, "month": month, "days": calendar_data}

@app.get("/day-energy")
def get_today_energy():
    today = datetime.now().strftime("%Y/%m/%d")
    energy = get_day_energy(today)
    return {"date": today.replace("/", "-"), "energy": energy}

@app.get("/natal-chart")
def get_natal_chart(birth_date: str, birth_time: str, latitude: float, longitude: float, tz: str = "UTC", language: str = "en"):
    # tz приймається для сумісності, але поки не передається в calculate_natal_chart (там UTC)
    chart = calculate_natal_chart(birth_date, birth_time, latitude, longitude)
 
    if not chart:
        return {"error": "Could not calculate natal chart"}
 
    # 🌍 Переклади назв планет — включно з вищими планетами Elite-рівня
    PLANET_TRANSLATIONS = {
        "uk": {
            "Sun": "Сонце", "Moon": "Місяць", "Mercury": "Меркурій",
            "Venus": "Венера", "Mars": "Марс", "Jupiter": "Юпітер",
            "Saturn": "Сатурн", "Uranus": "Уран", "Neptune": "Нептун",
            "Pluto": "Плутон", "Chiron": "Хірон", "North Node": "Вузол Місяця"
        },
        "ru": {
            "Sun": "Солнце", "Moon": "Луна", "Mercury": "Меркурий",
            "Venus": "Венера", "Mars": "Марс", "Jupiter": "Юпитер",
            "Saturn": "Сатурн", "Uranus": "Уран", "Neptune": "Нептун",
            "Pluto": "Плутон", "Chiron": "Хирон", "North Node": "Северный Узел"
        },
        "es": {
            "Sun": "Sol", "Moon": "Luna", "Mercury": "Mercurio",
            "Venus": "Venus", "Mars": "Marte", "Jupiter": "Júpiter",
            "Saturn": "Saturno", "Uranus": "Urano", "Neptune": "Neptuno",
            "Pluto": "Plutón", "Chiron": "Quirón", "North Node": "Nodo Norte"
        },
        "it": {
            "Sun": "Sole", "Moon": "Luna", "Mercury": "Mercurio",
            "Venus": "Venere", "Mars": "Marte", "Jupiter": "Giove",
            "Saturn": "Saturno", "Uranus": "Urano", "Neptune": "Nettuno",
            "Pluto": "Plutone", "Chiron": "Chirone", "North Node": "Nodo Nord"
        },
        "de": {
            "Sun": "Sonne", "Moon": "Mond", "Mercury": "Merkur",
            "Venus": "Venus", "Mars": "Mars", "Jupiter": "Jupiter",
            "Saturn": "Saturn", "Uranus": "Uranus", "Neptune": "Neptun",
            "Pluto": "Pluto", "Chiron": "Chiron", "North Node": "Mondknoten"
        },
        "pl": {
            "Sun": "Słońce", "Moon": "Księżyc", "Mercury": "Merkury",
            "Venus": "Wenus", "Mars": "Mars", "Jupiter": "Jowisz",
            "Saturn": "Saturn", "Uranus": "Uran", "Neptune": "Neptun",
            "Pluto": "Pluton", "Chiron": "Chiron", "North Node": "Węzeł Północny"
        },
    }
 
    def format_planet(name, data):
        """Форматує дані однієї планети для відповіді iOS."""
        house_str = data.get("house", "House_1")
        house_num = int(house_str.split("_")[1]) if "_" in house_str else 1
        local_name = PLANET_TRANSLATIONS.get(language, {}).get(name, name)
        return {
            "name":            local_name,
            "sign":            data.get("sign", ""),
            "house":           house_num,
            "degree":          data.get("sign_degree", data.get("degree", 0.0)),
            "absolute_degree": data.get("absolute_degree", 0.0),
            "is_retrograde":   data.get("is_retrograde", False),
        }
 
    planets_data = chart.get("planets", {})
 
    # --- Big Three: Sun, Moon, Ascendant (зворотна сумісність з iOS) ---
    big_three = []
    if "Sun"  in planets_data: big_three.append(format_planet("Sun",  planets_data["Sun"]))
    if "Moon" in planets_data: big_three.append(format_planet("Moon", planets_data["Moon"]))
 
    # Асцендент — беремо з нової Elite-структури, з fallback на стару
    asc_data   = chart.get("angles", {}).get("ascendant") or chart.get("ascendant", {})
    asc_sign   = asc_data.get("sign", "Unknown")
    asc_abs    = asc_data.get("absolute_degree", asc_data.get("degree", 0.0))
    asc_sigdeg = asc_data.get("sign_degree", asc_data.get("degree", 0.0))
 
    ASC_NAMES = {
        "uk": "Асцендент", "ru": "Асцендент",
        "es": "Ascendente", "it": "Ascendente",
        "de": "Aszendent",  "pl": "Ascendent",
    }
    big_three.append({
        "name":            ASC_NAMES.get(language, "Ascendant"),
        "sign":            asc_sign,
        "house":           1,
        "degree":          asc_sigdeg,
        "absolute_degree": asc_abs,
        "is_retrograde":   False,
    })
 
    # --- Усі інші планети (Elite: включно з вищими) ---
    PLANET_ORDER = [
        "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
        "Uranus", "Neptune", "Pluto", "Chiron", "North Node"
    ]
    other_planets = [
        format_planet(p, planets_data[p])
        for p in PLANET_ORDER if p in planets_data
    ]
 
    # --- Будинки: передаємо absolute_degree для iOS-кола ---
    houses_out = {
        key: {
            "sign":            hdata.get("sign", ""),
            "absolute_degree": hdata.get("absolute_degree", hdata.get("degree", 0.0)),
        }
        for key, hdata in chart.get("houses", {}).items()
    }
 
    return {
        # Зворотна сумісність зі старим iOS-кодом
        "big_three": big_three,
        "planets":   other_planets,
        # Elite-дані для нового NatalChartView
        "aspects":   chart.get("aspects", []),
        "houses":    houses_out,
        "metadata":  chart.get("metadata", {}),
    }
    
@app.post("/compatibility")
def get_compatibility(data: dict):
    try:
        person1, person2 = data.get('person1'), data.get('person2')
        if not person1 or not person2: return {"error": "Missing person1 or person2 data"}
        result = calculate_compatibility(person1, person2)
        if not result: return {"error": "Could not calculate compatibility"}
        return result
    except Exception as e: return {"error": str(e)}

# --- Synastry Lite (Free / Viral) ---
class CompatibilityLiteRequest(BaseModel):
    name1: str
    date1: str  # Format: 'YYYY-MM-DD'
    name2: str
    date2: str  # Format: 'YYYY-MM-DD'
    language: str = "en"

@app.post("/compatibility-lite")
def get_compatibility_lite(request: CompatibilityLiteRequest):
    """
    Lightweight, free compatibility check for the Synastry Lite feature.
    Returns a short, viral summary perfect for social media sharing.
    Completely separate from the Pro /compatibility endpoint.
    """
    try:
        # Step 1 — calculate base compatibility (Sun sign only)
        result = calculate_lite_compatibility(
            request.name1,
            request.date1,
            request.name2,
            request.date2
        )
        if not result:
            return {"error": "Could not calculate lite compatibility"}

        name1 = result["name1"]
        sign1 = result["sign1"]
        name2 = result["name2"]
        sign2 = result["sign2"]
        score = int(result["score"])

        # Step 2 — generate a viral 2-sentence summary via OpenAI
        lang_instruction = LANGUAGES.get(request.language, "English")

        system_prompt = (
            f"You are a witty, emotional astrology copywriter writing short viral "
            f"social media captions. You MUST respond EXACTLY in {lang_instruction}. "
            f"Keep it under 2 sentences. Use 1-2 tasteful emojis. No hashtags. "
            f"No quotation marks around the answer. Make it feel personal, warm, "
            f"and perfect for an Instagram story or TikTok screenshot."
        )

        user_prompt = (
            f"Two people just checked their zodiac compatibility:\n"
            f"- {name1} ({sign1})\n"
            f"- {name2} ({sign2})\n"
            f"- Compatibility score: {score}/100\n\n"
            f"Write a punchy 2-sentence viral caption about their match. "
            f"If the score is high (80+), celebrate it. If medium (50-79), be playful "
            f"and hopeful. If low (<50), be humorous and kind, never negative."
        )

        viral_summary = None
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=120,
                temperature=0.9
            )
            viral_summary = response.choices[0].message.content.strip().strip('"').strip("'")
        except Exception as e:
            print(f"⚠️ OpenAI Error in /compatibility-lite: {e}")
            fallbacks = {
                "en": f"✨ {name1} and {name2} scored {score}/100 — the stars have spoken! A cosmic mix worth exploring. 💫",
                "uk": f"✨ {name1} і {name2} набрали {score}/100 — зірки все сказали! Космічний союз, який варто дослідити. 💫",
                "es": f"✨ {name1} y {name2} obtuvieron {score}/100 — ¡las estrellas han hablado! Una mezcla cósmica por explorar. 💫",
                "it": f"✨ {name1} e {name2} hanno totalizzato {score}/100 — le stelle hanno parlato! Un mix cosmico da esplorare. 💫",
                "de": f"✨ {name1} und {name2} erreichen {score}/100 — die Sterne haben gesprochen! Eine kosmische Mischung zum Entdecken. 💫",
                "pl": f"✨ {name1} i {name2} zdobyli {score}/100 — gwiazdy przemówiły! Kosmiczne połączenie warte odkrycia. 💫",
                "ru": f"✨ {name1} и {name2} набрали {score}/100 — звёзды сказали своё слово! Космический союз, который стоит исследовать. 💫"
            }
            viral_summary = fallbacks.get(request.language, fallbacks["en"])

        # Step 3 — return final JSON for the iOS client
        return {
            "score": score,
            "name1": name1,
            "sign1": sign1,
            "name2": name2,
            "sign2": sign2,
            "viral_summary": viral_summary
        }

    except Exception as e:
        print(f"❌ Error in /compatibility-lite: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/destiny-matrix")
def get_destiny_matrix(birth_date: str, language: str = "en"):
    result = get_full_destiny_matrix(birth_date, language)
    if not result: return {"error": "Could not calculate destiny matrix"}
    return result

@app.get("/quantum-field")
def get_quantum_field(latitude: float = 50.45, longitude: float = 30.52):
    result = calculate_quantum_state(latitude, longitude)
    if not result: return {"error": "Quantum field fluctuation error"}
    return result

@app.get("/daily-timeline")
def get_daily_timeline(date: str):
    """
    Returns a 24-hour planetary timeline for the Smart Planner 'Daily Energy' tab.
    Expects `date` as a query parameter in YYYY-MM-DD format.
    """
    result = generate_daily_timeline(date)
    if not result or "error" in result:
        return {"error": "Could not generate daily timeline"}
    return result

def evaluate_planner_task(task: str, target_date: str, birth_date: str, language: str = "en"):
    lang_instruction = LANGUAGES.get(language, "English")
    system_prompt = f"""You are an elite astrological time-management coach. 
    You evaluate if a specific date is favorable for a user's specific task based on astrology and numerology.
    You MUST respond ONLY with a valid JSON object. Do not include any markdown formatting like ```json."""
    
    user_prompt = f"""
    Task to evaluate: "{task}"
    Target Date for Task: {target_date}
    User's Birth Date: {birth_date}
    
    Analyze the astrological and numerological compatibility of this task for this specific date.
    Return a JSON object with EXACTLY these three keys:
    1. "score": an integer from 0 to 100 representing how favorable the day is.
    2. "verdict": 2 short sentences explaining the astrological/numerological reason why, in {lang_instruction}. Use 1-2 emojis.
    3. "advice": 1 practical sentence on what to do, in {lang_instruction}.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            max_tokens=300, temperature=0.7, response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"⚠️ Planner AI Error: {e}")
        return {
            "score": 50,
            "verdict": "Енергія дня нейтральна." if language in ["uk", "ru"] else "The energy is neutral.",
            "advice": "Дійте обережно." if language in ["uk", "ru"] else "Proceed with caution."
        }

@app.post("/smart-planner")
def smart_planner_endpoint(data: dict):
    task, target_date, birth_date, language = data.get("task"), data.get("target_date"), data.get("birth_date"), data.get("language", "en")
    if not all([task, target_date, birth_date]): return {"error": "Missing required fields"}
    return evaluate_planner_task(task, target_date, birth_date, language)

@app.get("/daily-insight")
def get_daily_insight(date: str, language: str = "en"):
    lang_instruction = LANGUAGES.get(language, "English")
    system_prompt = f"You are an elite astro-coach. Respond strictly in {lang_instruction}."
    
    user_prompt = f"Analyze the general astrological energy for the date: {date}. Write a short, inspiring 2-sentence forecast for this specific day. Use 1-2 emojis."
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            max_tokens=150, temperature=0.7
        )
        insight = response.choices[0].message.content.strip()
    except Exception as e:
        insight = "Енергія цього дня вимагає балансу." if language in ["uk", "ru"] else "This day requires balance."
        
    return {"date": date, "insight": insight}

class AICoachRequest(BaseModel):
    question: str
    name: str = "Мандрівник"
    language: str = "uk"
    module_name: str = ""
    context_data: str = ""
    palm_context: str = ""

class PalmScanRequest(BaseModel):
    image_base64: str
    language: str = "en"

class GuestScanRequest(BaseModel):
    guest_image_base64: str
    owner_palm_data: dict
    language: str = "en"

@app.post('/ai-appcoach')
def ai_appcoach(request: AICoachRequest):
    try:
        question      = request.question
        name          = request.name
        language      = request.language
        module_name   = request.module_name.strip()
        context_data  = request.context_data
        palm_context  = request.palm_context
        user_context  = ""

        lang_prompt = LANGUAGES.get(language, "English")

        # Merge legacy matrix context + new screen context into one block
        full_context = "\n".join(filter(None, [user_context, context_data])) or "No data"

        # --- Module-specific expert personas ---
        MODULE_EXPERTS = {
            # Ukrainian names
            "Натальна Карта": (
                "You are an elite Vedic and Western astrologer. "
                "Your ONLY domain is Natal Charts (birth charts): planetary positions, houses, aspects, and their life implications. "
                "You interpret the Big Three (Sun, Moon, Ascendant) and all planetary placements with depth and precision."
            ),
            "Матриця Долі": (
                "You are the world's leading Destiny Matrix expert (22 Major Arcana system). "
                "Your ONLY domain is the Destiny Matrix: arcana meanings, karma, family lines (father/mother), "
                "comfort zone, social mask, talents, material karma, and life purpose calculations."
            ),
            "Сумісність": (
                "You are a Synastry and Relationship Astrology specialist. "
                "Your ONLY domain is astrological compatibility between two people: synastry overlays, "
                "karmic connections, romantic/emotional/spiritual/mental scores, and relationship advice."
            ),
            "Ангельські Числа": (
                "You are a master numerologist specialising exclusively in Angel Numbers. "
                "Your ONLY domain is angel numbers: their vibrational meaning, spiritual messages, "
                "and how they guide daily decisions and the life path."
            ),
            "Smart Планувальник": (
                "You are an astrological time-management coach. "
                "Your ONLY domain is the Smart Planner: evaluating whether specific dates are favorable "
                "for specific tasks using astrology and numerology, and optimising life planning."
            ),
            "Нумерологія": (
                "You are a master numerologist covering Pythagorean, Chaldean, Kabbalistic, and Chinese systems. "
                "Your ONLY domain is numerology: life path numbers, soul numbers, name vibrations, "
                "personal year charts, and their influence on personality and destiny."
            ),
            "AstroSync": (
                "You are the ultimate AstroSync App Expert — a guide across all esoteric modules: "
                "astrology, numerology, Destiny Matrix, compatibility, and cosmic planning."
            ),
            # English names (mirror)
            "Natal Chart": (
                "You are an elite Vedic and Western astrologer. "
                "Your ONLY domain is Natal Charts: planetary positions, houses, aspects, and their life implications."
            ),
            "Destiny Matrix": (
                "You are the world's leading Destiny Matrix expert (22 Major Arcana system). "
                "Your ONLY domain is the Destiny Matrix: arcana meanings, karma, family lines, and life purpose."
            ),
            "Compatibility": (
                "You are a Synastry and Relationship Astrology specialist. "
                "Your ONLY domain is astrological compatibility: synastry, karmic bonds, and relationship scores."
            ),
            "Angel Numbers": (
                "You are a master numerologist specialising exclusively in Angel Numbers: "
                "vibrational meaning, spiritual messages, and daily guidance."
            ),
            "Smart Planner": (
                "You are an astrological time-management coach. "
                "Your ONLY domain is the Smart Planner: favorable dates for tasks via astrology and numerology."
            ),
            "Numerology": (
                "You are a master numerologist covering Pythagorean, Chaldean, Kabbalistic, and Chinese systems."
            ),
        }

        default_persona = (
            "You are the ultimate AstroSync App Expert and Destiny Matrix Guide. "
            "You explain personal esoteric calculations across astrology, numerology, and destiny."
        )
        expert_persona = MODULE_EXPERTS.get(module_name, default_persona)
        display_module = module_name if module_name else "AstroSync"

        system_prompt = f"""
{expert_persona}

CURRENT SCREEN: {display_module}
USER'S DATA FROM THE APP:
{full_context}
{"" if not palm_context else f'''
Palm Reading Context:
{palm_context}
Consider the user's palm reading data when suggesting practices.
Breaks in lines suggest areas needing grounding practices.
Strong lines suggest areas of natural talent to leverage.
'''}
STRICT OPERATING RULES:
1. SCOPE LOCK — You are a narrow specialist. ONLY answer questions directly related to {display_module} and esoteric topics connected to it.
   If the user asks about ANYTHING outside this scope (cooking, politics, coding, sports, general knowledge, other app modules), FIRMLY refuse:
   "I am your {display_module} expert. I can only help with questions about {display_module}."
2. DATA INTEGRITY — ONLY use numbers/data from the context block above. NEVER invent or guess arcana numbers, planet positions, or scores.
3. NO DATA RULE — If context says "No data" or is empty, tell the user to provide their birth date in Settings.
4. LANGUAGE — Answer strictly in {lang_prompt}. Never switch languages mid-reply.
5. TONE — Be engaging, empathetic, structured, and deeply insightful. Use 1-2 relevant emojis per response.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.35,
            max_tokens=1000
        )
        return {"answer": response.choices[0].message.content}

    except Exception as e:
        errors = {
            "en": "The expert is busy. Try again in a minute.",
            "uk": "Експерт зараз аналізує дані. Спробуйте через хвилинку.",
            "es": "El experto está ocupado. Inténtalo de nuevo.",
            "it": "L'esperto è occupato. Riprova tra poco.",
            "de": "Der Experte ist beschäftigt. Versuchen Sie es gleich noch einmal.",
            "pl": "Ekspert jest zajęty. Spróbuj ponownie za chwilę.",
            "ru": "Эксперт сейчас занят. Попробуйте через минуту."
        }
        return {"answer": errors.get(request.language, errors["en"])}
    
@app.get("/angel-numbers")
def get_angel_numbers(birth_date: str, language: str = "en"):
    """Ендпоінт для розрахунку Числа Ангела та генерації преміум-тексту"""
    
    # 1. Отримуємо математичний розрахунок (наприклад, "111")
    calc_result = calculate_angel_number(birth_date)
    angel_num = calc_result["angel_number"]
    
    # 2. Генеруємо преміум-розшифровку через ШІ
    lang_instruction = LANGUAGES.get(language, "English")
    system_prompt = f"You are an elite numerologist. The user's angel number is {angel_num}. Write a mystical and inspiring 3-sentence reading about what this number means for their destiny. Respond strictly in {lang_instruction}."
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=250, temperature=0.7
        )
        premium_text = response.choices[0].message.content.strip()
    except Exception:
        premium_text = "Твоя доля кличе тебе. Довірся Всесвіту та енергії чисел."
        
    # 3. Віддаємо дані в додаток
    return {
        "angel_number": angel_num,
        "premium_description": premium_text
    }
@app.get("/moon-widget")
def get_moon_widget(language: str = "en"):
    """Ендпоінт для віджета Місяця на Головному Екрані"""
    # Отримуємо сьогоднішню дату
    today_slash = datetime.now().strftime("%Y/%m/%d")
    
    # Визначаємо фазу місяця (функція вже є у твоєму astro_basic.py)
    current_moon = get_moon_phase(today_slash)
    
    # Просимо ШІ дати дуже коротку пораду на день (1 речення)
    lang_instruction = LANGUAGES.get(language, "English")
    system_prompt = f"You are a lunar astrologer. The current moon phase is {current_moon}. Write ONE short, mystical, and inspiring sentence of advice for today based on this phase. Respond strictly in {lang_instruction}."
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=60, temperature=0.7
        )
        moon_advice = response.choices[0].message.content.strip()
    except Exception:
        moon_advice = "Слухай свою інтуїцію сьогодні. Енергія місяця на твоєму боці." if language in ["uk", "ru"] else "Listen to your intuition today."
        
    return {
        "moon_phase": current_moon,
        "advice": moon_advice
    }

@app.get("/api/v1/shared-matrix")
def get_shared_matrix(birth_date_a: str, birth_date_b: str):
    """
    Calculate shared destiny matrix for two people.
    Results are cached for 7 days (static math, never changes).
    """
    sorted_dates = tuple(sorted([birth_date_a, birth_date_b]))
    cache_key = f"shared_matrix:{sorted_dates[0]}:{sorted_dates[1]}"

    cached = permanent_cache.get(cache_key)
    if cached:
        return cached

    try:
        result = calculate_shared_matrix(birth_date_a, birth_date_b)
        permanent_cache.set(cache_key, result)
        return result
    except ValueError as e:
        return {"error": str(e)}

@app.get("/api/v1/global-day-energy")
def get_global_day_energy(date: str = None):
    """
    Returns today's global energy (same for all users).
    Includes which matrix zone is active today.
    Cached for 24 hours.
    """
    try:
        return calculate_global_day_energy(date)
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/v1/dynamic-synastry")
def get_dynamic_synastry(birth_date_a: str, birth_date_b: str, date: str = None):
    """
    Dynamic Synastry: Shared Matrix + Today's Active Zone.
    Returns the full pair matrix with today's highlighted zone.
    """
    try:
        sorted_dates = tuple(sorted([birth_date_a, birth_date_b]))
        cache_key = f"shared_matrix:{sorted_dates[0]}:{sorted_dates[1]}"
        matrix = permanent_cache.get(cache_key)
        if not matrix:
            matrix = calculate_shared_matrix(birth_date_a, birth_date_b)
            permanent_cache.set(cache_key, matrix)

        energy = calculate_global_day_energy(date)

        active_zone_key = energy["active_zone"]
        active_zone_data = matrix["zones"].get(active_zone_key, {})

        return {
            "matrix": matrix,
            "day_energy": energy,
            "active_zone": {
                "key": active_zone_key,
                "name": active_zone_data.get("name", ""),
                "arcana": active_zone_data.get("arcana", 0),
                "intensity": energy["intensity"]
            }
        }
    except Exception as e:
        return {"error": str(e)}

# --- Quantum Palm: Biometric Palmistry ---

@app.post("/api/v1/palm/validate")
async def palm_validate(request: PalmScanRequest):
    """Validate if image contains a human palm. Free call — no subscription check."""
    try:
        result = await validate_palm_image(client, request.image_base64)
        return result
    except Exception as e:
        return {"error": "validation_failed", "message": str(e)}

@app.post("/api/v1/palm/visual-scan")
async def palm_visual_scan(request: PalmScanRequest):
    """Quick weekly energy scan from palm image. Premium only."""
    try:
        validation = await validate_palm_image(client, request.image_base64)
        if not validation.get("is_valid_palm"):
            return {"error": "biometric_not_recognized", "message": "Biometric data not recognized. Please ensure your palm is clearly visible and try again."}
        result = await visual_scan(client, request.image_base64, request.language)
        return result
    except Exception as e:
        return {"error": "scan_failed", "message": str(e)}

@app.post("/api/v1/palm/deep-scan")
async def palm_deep_scan(request: PalmScanRequest):
    """Full monthly palm analysis. Premium only."""
    try:
        validation = await validate_palm_image(client, request.image_base64)
        if not validation.get("is_valid_palm"):
            return {"error": "biometric_not_recognized", "message": "Biometric data not recognized. Please ensure your palm is clearly visible and try again."}
        result = await deep_scan(client, request.image_base64, request.language)
        return result
    except Exception as e:
        return {"error": "scan_failed", "message": str(e)}

@app.post("/api/v1/palm/guest-compatibility")
async def palm_guest_compatibility(request: GuestScanRequest):
    """Compare guest palm with owner's stored palm data. Premium only."""
    try:
        validation = await validate_palm_image(client, request.guest_image_base64)
        if not validation.get("is_valid_palm"):
            return {"error": "biometric_not_recognized", "message": "Biometric data not recognized. Please ensure the palm is clearly visible and try again."}
        result = await guest_compatibility_scan(client, request.guest_image_base64, request.owner_palm_data, request.language)
        return result
    except Exception as e:
        return {"error": "scan_failed", "message": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting AstroSync on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)