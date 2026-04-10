# --- AstroSync: Natal Chart Module v3.0 (Elite Engine) ---
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const

# Знаки зодіаку в порядку від Овна — для конвертації в absolute_degree (0–360°)
ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer',
    'Leo', 'Virgo', 'Libra', 'Scorpio',
    'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Конфігурація мажорних аспектів: назва → (ідеальний кут°, орбіс°)
ASPECTS_CONFIG = {
    'Conjunction': (0,   8),
    'Sextile':     (60,  6),
    'Square':      (90,  8),
    'Trine':       (120, 8),
    'Opposition':  (180, 8),
}


# ---------------------------------------------------------------------------
# ДОПОМІЖНІ ФУНКЦІЇ
# ---------------------------------------------------------------------------

def sign_to_absolute(sign: str, sign_degree: float) -> float:
    """
    Конвертує знак зодіаку + градус у знаку в абсолютний градус екліптики (0–360°).

    Алгоритм: індекс знаку від Овна × 30° + градус у знаку.
    Приклад: Taurus 15.5° → 1 × 30 + 15.5 = 45.5°

    Потрібно для iOS UI: малювання планет на колі натальної карти.
    """
    idx = ZODIAC_SIGNS.index(sign) if sign in ZODIAC_SIGNS else 0
    return round(idx * 30.0 + sign_degree, 2)


def build_planet_dict(planet_obj, house_str: str) -> dict:
    """
    Формує стандартний словник небесного тіла з усіма Elite-полями.

    Ключі:
        sign            — назва знаку зодіаку (str)
        sign_degree     — градус всередині знаку, 0.0–29.99 (float)
        absolute_degree — абсолютний градус екліптики, 0.0–359.99 (float)
        house           — будинок у форматі "House_N" (str)
        is_retrograde   — True якщо планета ретроградна (bool)
        degree          — псевдонім sign_degree для зворотної сумісності з server.py
        longitude       — псевдонім absolute_degree для зворотної сумісності
    """
    sign_deg = round(planet_obj.signlon, 2)
    abs_deg  = sign_to_absolute(planet_obj.sign, sign_deg)

    # Ретроградність: flatlib зберігає напрямок руху в атрибуті movement
    is_retro = False
    try:
        is_retro = planet_obj.movement() == const.RETROGRADE
    except Exception:
        pass

    return {
        # --- Elite поля ---
        "sign":            planet_obj.sign,
        "sign_degree":     sign_deg,
        "absolute_degree": abs_deg,
        "house":           house_str,
        "is_retrograde":   is_retro,
        # --- Зворотна сумісність зі старим server.py ---
        "degree":          sign_deg,
        "longitude":       abs_deg,
    }


def get_house_for_planet(chart, planet_lon: float) -> str:
    """
    Визначає номер будинку для планети за її абсолютною довготою.

    Алгоритм обходить 12 куспідів по колу та враховує перехід через 0°
    (ситуація коли куспід 12-го будинку > куспіда 1-го числово).
    """
    try:
        house_ids = [
            const.HOUSE1,  const.HOUSE2,  const.HOUSE3,  const.HOUSE4,
            const.HOUSE5,  const.HOUSE6,  const.HOUSE7,  const.HOUSE8,
            const.HOUSE9,  const.HOUSE10, const.HOUSE11, const.HOUSE12
        ]
        cusps = [chart.get(h).lon for h in house_ids]

        for i in range(12):
            cur  = cusps[i]
            nxt  = cusps[(i + 1) % 12]
            if nxt < cur:                       # Перехід через 0°
                if planet_lon >= cur or planet_lon < nxt:
                    return f"House_{i + 1}"
            else:
                if cur <= planet_lon < nxt:
                    return f"House_{i + 1}"

        return "House_1"                        # Резервне значення
    except Exception:
        return "Unknown"


# ---------------------------------------------------------------------------
# РОЗРАХУНОК АСПЕКТІВ
# ---------------------------------------------------------------------------

def calculate_aspects(planets_data: dict) -> list:
    """
    Обчислює мажорні геометричні аспекти між усіма унікальними парами планет.

    Алгоритм:
        1. Бере absolute_degree кожної планети
        2. Перебирає всі унікальні пари (без повторень: A-B, не B-A)
        3. Обчислює кутову різницю та нормалізує до діапазону 0–180°
        4. Порівнює з таблицею ASPECTS_CONFIG — перший підходящий аспект зберігається

    Args:
        planets_data: словник {назва: {..., "absolute_degree": float}}

    Returns:
        Список dict із полями planet1, planet2, aspect_name, angle, orb
    """
    aspects      = []
    planet_names = list(planets_data.keys())

    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1 = planet_names[i]
            p2 = planet_names[j]

            deg1 = planets_data[p1].get("absolute_degree", 0.0)
            deg2 = planets_data[p2].get("absolute_degree", 0.0)

            # Нормалізуємо різницю до діапазону 0–180°
            diff = abs(deg1 - deg2)
            if diff > 180:
                diff = 360.0 - diff

            # Шукаємо перший аспект в межах орбісу
            for asp_name, (ideal_angle, orb_limit) in ASPECTS_CONFIG.items():
                actual_orb = abs(diff - ideal_angle)
                if actual_orb <= orb_limit:
                    aspects.append({
                        "planet1":     p1,
                        "planet2":     p2,
                        "aspect_name": asp_name,
                        "angle":       round(diff, 2),
                        "orb":         round(actual_orb, 2),
                    })
                    break

    return aspects


# ---------------------------------------------------------------------------
# ГОЛОВНА ФУНКЦІЯ
# ---------------------------------------------------------------------------

def calculate_natal_chart(birth_date: str, birth_time: str,
                          latitude: float, longitude: float) -> dict | None:
    """
    Розраховує повну натальну карту рівня Elite за допомогою flatlib (Swiss Ephemeris).

    Бекенд повертає ВИКЛЮЧНО математичну базу у форматі JSON.
    Текстові трактування генерує AI Coach через OpenAI API.

    Args:
        birth_date: дата народження "YYYY-MM-DD"
        birth_time: час народження "HH:MM"
        latitude:   географічна широта (float)
        longitude:  географічна довгота (float)

    Returns:
        Структурований dict або None у разі помилки.

        Структура відповіді:
            metadata  — версія двигуна
            angles    — ascendant та mc з absolute_degree
            planets   — всі небесні тіла з Elite-полями
            houses    — 12 будинків з absolute_degree
            aspects   — список мажорних аспектів
            (+ старі ключі ascendant/mc/chart_type для зворотної сумісності з server.py)
    """
    try:
        print(f"📊 [Elite v3] Calculating natal chart...")
        print(f"   Date: {birth_date} {birth_time} | Location: {latitude}, {longitude}")

        # Форматуємо дату: flatlib очікує "YYYY/MM/DD"
        date_formatted = birth_date.replace("-", "/")

        # Ініціалізуємо flatlib-об'єкти
        date  = Datetime(date_formatted, birth_time, '+00:00')
        pos   = GeoPos(latitude, longitude)
        chart = Chart(date, pos)

        # ---------------------------------------------------------------
        # КУТИ: Ascendant та Midheaven (MC)
        # ---------------------------------------------------------------
        asc = chart.get(const.ASC)
        mc  = chart.get(const.MC)

        asc_sign_deg = round(asc.signlon, 2)
        mc_sign_deg  = round(mc.signlon, 2)
        asc_abs      = sign_to_absolute(asc.sign, asc_sign_deg)
        mc_abs       = sign_to_absolute(mc.sign,  mc_sign_deg)

        angles = {
            "ascendant": {
                "sign":            asc.sign,
                "sign_degree":     asc_sign_deg,
                "absolute_degree": asc_abs,
                "degree":          round(asc.lon, 2),   # backward compat
            },
            "mc": {
                "sign":            mc.sign,
                "sign_degree":     mc_sign_deg,
                "absolute_degree": mc_abs,
                "degree":          round(mc.lon, 2),    # backward compat
            },
        }

        # ---------------------------------------------------------------
        # ПЛАНЕТИ: основні + вищі (Uranus, Neptune, Pluto, North Node)
        # ---------------------------------------------------------------
        BODIES = [
            (const.SUN,        "Sun"),
            (const.MOON,       "Moon"),
            (const.MERCURY,    "Mercury"),
            (const.VENUS,      "Venus"),
            (const.MARS,       "Mars"),
            (const.JUPITER,    "Jupiter"),
            (const.SATURN,     "Saturn"),
            (const.URANUS,     "Uranus"),
            (const.NEPTUNE,    "Neptune"),
            (const.PLUTO,      "Pluto"),
            (const.NORTH_NODE, "North Node"),
        ]

        planets_data = {}

        for body_const, body_name in BODIES:
            try:
                body      = chart.get(body_const)
                house_str = get_house_for_planet(chart, body.lon)
                planets_data[body_name] = build_planet_dict(body, house_str)
            except Exception as e:
                # Пропускаємо тіло якщо воно недоступне — не зупиняємо весь розрахунок
                print(f"[natal_chart] Пропущено '{body_name}': {e}")

        # Chiron: окремий блок через нестабільну підтримку в різних версіях flatlib
        try:
            chiron_id = getattr(const, 'CHIRON', 'Chiron')
            chiron    = chart.get(chiron_id)
            house_str = get_house_for_planet(chart, chiron.lon)
            planets_data["Chiron"] = build_planet_dict(chiron, house_str)
        except Exception as e:
            print(f"[natal_chart] Chiron недоступний у цій версії flatlib: {e}")

        # ---------------------------------------------------------------
        # БУДИНКИ: 12 куспідів
        # ---------------------------------------------------------------
        HOUSE_IDS = [
            const.HOUSE1,  const.HOUSE2,  const.HOUSE3,  const.HOUSE4,
            const.HOUSE5,  const.HOUSE6,  const.HOUSE7,  const.HOUSE8,
            const.HOUSE9,  const.HOUSE10, const.HOUSE11, const.HOUSE12
        ]

        houses_data = {}
        for i, house_id in enumerate(HOUSE_IDS, start=1):
            house     = chart.get(house_id)
            h_sig_deg = round(house.signlon, 2)
            h_abs     = sign_to_absolute(house.sign, h_sig_deg)
            houses_data[f"House_{i}"] = {
                "sign":            house.sign,
                "sign_degree":     h_sig_deg,
                "absolute_degree": h_abs,
                "degree":          round(house.lon, 2),  # backward compat
            }

        # ---------------------------------------------------------------
        # АСПЕКТИ
        # ---------------------------------------------------------------
        aspects = calculate_aspects(planets_data)

        print(f"✅ Chart OK: {len(planets_data)} bodies, {len(aspects)} aspects")

        return {
            # --- Метадані двигуна ---
            "metadata": {
                "engine":  "flatlib/Swiss Ephemeris",
                "version": "elite_v3",
            },

            # --- Elite структура ---
            "angles":  angles,
            "planets": planets_data,
            "houses":  houses_data,
            "aspects": aspects,

            # --- Зворотна сумісність зі старим форматом (server.py не чіпаємо) ---
            "ascendant":  {"sign": asc.sign, "degree": round(asc.lon, 2)},
            "mc":         {"sign": mc.sign,  "degree": round(mc.lon, 2)},
            "chart_type": "natal",
        }

    except Exception as e:
        print(f"❌ [natal_chart] Error: {e}")
        import traceback
        traceback.print_exc()
        return None


# ---------------------------------------------------------------------------
# ЗАСТАРІЛА ФУНКЦІЯ (залишена для сумісності з імпортом у server.py)
# ---------------------------------------------------------------------------

def get_planet_meaning(planet: str, sign: str, house: str, language: str = "en") -> str:
    """
    [ЗАСТАРІЛО — не розширювати]

    Залишена виключно щоб не зламати імпорт у server.py (рядок 5).
    Тексти тепер генерує AI Coach через OpenAI API динамічно.
    Повертає порожній рядок.
    """
    return ""


# ---------------------------------------------------------------------------
# ЛОКАЛЬНИЙ ТЕСТ
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("🔮 Testing Elite Natal Chart Engine v3...")
    result = calculate_natal_chart("1990-05-20", "14:30", 50.45, 30.52)

    if result:
        print(f"\n✅ SUCCESS! Engine: {result['metadata']['engine']}")
        asc_data = result['angles']['ascendant']
        print(f"Ascendant: {asc_data['sign']} {asc_data['sign_degree']}° (abs: {asc_data['absolute_degree']}°)")

        print(f"\nPlanets ({len(result['planets'])} bodies):")
        for name, data in result['planets'].items():
            retro = " ℞" if data['is_retrograde'] else ""
            print(f"  {name:12}: {data['sign']:13} {data['sign_degree']:5}° "
                  f"(abs: {data['absolute_degree']:6}°) {data['house']}{retro}")

        print(f"\nAspects ({len(result['aspects'])} found):")
        for asp in result['aspects'][:8]:
            print(f"  {asp['planet1']:12} {asp['aspect_name']:12} {asp['planet2']:12} "
                  f"angle:{asp['angle']:6}° orb:{asp['orb']}°")
    else:
        print("\n❌ FAILED")