"""
AuraSync Engine — calculates the user's daily aura based on
planetary hours, day ruler, and moon phase / zodiac sign.
"""

import json
from datetime import datetime, timezone

from app.services.quantum_engine import ENERGY_MAP, CHALDEAN_ORDER
from app.api.lunar_engine.services.moon_calculator import calculate_global_moon_data


PLANET_HUE = {
    "Sun": {"colors": ["#FFD700", "#FF8C00", "#1A0A2E"], "base_speed": 1.2},
    "Moon": {"colors": ["#C0C0FF", "#4169E1", "#0A0A2E"], "base_speed": 0.6},
    "Mercury": {"colors": ["#00FFD1", "#00B4D8", "#0A1A2E"], "base_speed": 1.5},
    "Venus": {"colors": ["#FF69B4", "#7B2FBE", "#1A0A2E"], "base_speed": 0.8},
    "Mars": {"colors": ["#FF2A55", "#FF6B00", "#1A0A2E"], "base_speed": 1.8},
    "Jupiter": {"colors": ["#FFD700", "#8B6914", "#1A0A2E"], "base_speed": 1.0},
    "Saturn": {"colors": ["#708090", "#2F4F4F", "#0A0A1E"], "base_speed": 0.4},
}

ZODIAC_ELEMENT = {
    "Aries": "fire", "Leo": "fire", "Sagittarius": "fire",
    "Taurus": "earth", "Virgo": "earth", "Capricorn": "earth",
    "Gemini": "air", "Libra": "air", "Aquarius": "air",
    "Cancer": "water", "Scorpio": "water", "Pisces": "water",
}

ELEMENT_MODIFIER = {
    "fire": {"saturation": 1.2, "brightness": 1.1},
    "earth": {"saturation": 0.8, "brightness": 0.9},
    "air": {"saturation": 1.0, "brightness": 1.15},
    "water": {"saturation": 0.9, "brightness": 0.85},
}

AURA_ARCHETYPES = {
    "mystic_fire": {
        "title_uk": "Містичний Вогонь",
        "title_en": "Mystic Fire",
        "insight_uk": "Твоя енергія сьогодні пробивна. Використай її для найскладніших задач.",
        "insight_en": "Your energy is piercing today. Channel it into your toughest challenges.",
        "asceticism_tag": "grounding",
    },
    "quantum_calm": {
        "title_uk": "Квантовий Штиль",
        "title_en": "Quantum Calm",
        "insight_uk": "День для внутрішньої роботи. Довірся інтуїції.",
        "insight_en": "A day for inner work. Trust your intuition.",
        "asceticism_tag": "meditation",
    },
    "solar_warrior": {
        "title_uk": "Сонячний Воїн",
        "title_en": "Solar Warrior",
        "insight_uk": "Лідерська енергія на максимумі. Приймай рішення сміливо.",
        "insight_en": "Leadership energy at its peak. Make bold decisions.",
        "asceticism_tag": "focus",
    },
    "lunar_dreamer": {
        "title_uk": "Місячний Мрійник",
        "title_en": "Lunar Dreamer",
        "insight_uk": "Підсвідомість активна. Записуй ідеї та сни.",
        "insight_en": "Your subconscious is active. Write down ideas and dreams.",
        "asceticism_tag": "creativity",
    },
    "mercury_flash": {
        "title_uk": "Ртутний Спалах",
        "title_en": "Mercury Flash",
        "insight_uk": "Швидкість думки зашкалює. Ідеальний день для переговорів.",
        "insight_en": "Thought speed is off the charts. Perfect day for negotiations.",
        "asceticism_tag": "focus",
    },
    "venus_bloom": {
        "title_uk": "Цвітіння Венери",
        "title_en": "Venus Bloom",
        "insight_uk": "Краса та гармонія у всьому. Створюй, кохай, насолоджуйся.",
        "insight_en": "Beauty and harmony in everything. Create, love, enjoy.",
        "asceticism_tag": "creativity",
    },
    "mars_surge": {
        "title_uk": "Марсіанський Шторм",
        "title_en": "Mars Surge",
        "insight_uk": "Потужна фізична енергія. Час для спорту та рішучих дій.",
        "insight_en": "Powerful physical energy. Time for sports and decisive action.",
        "asceticism_tag": "grounding",
    },
    "jupiter_grace": {
        "title_uk": "Ласка Юпітера",
        "title_en": "Jupiter Grace",
        "insight_uk": "Удача на твоєму боці. Розширюй горизонти.",
        "insight_en": "Luck is on your side. Expand your horizons.",
        "asceticism_tag": "creativity",
    },
    "saturn_anchor": {
        "title_uk": "Якір Сатурна",
        "title_en": "Saturn Anchor",
        "insight_uk": "Структура і дисципліна — твої суперсили сьогодні.",
        "insight_en": "Structure and discipline are your superpowers today.",
        "asceticism_tag": "grounding",
    },
    "eclipse_shift": {
        "title_uk": "Затемнення",
        "title_en": "Eclipse Shift",
        "insight_uk": "Трансформаційний день. Старе відмирає — нове народжується.",
        "insight_en": "Transformational day. The old fades — the new is born.",
        "asceticism_tag": "meditation",
    },
    "nebula_flow": {
        "title_uk": "Потік Небули",
        "title_en": "Nebula Flow",
        "insight_uk": "Все тече, все змінюється. Адаптуйся замість контролю.",
        "insight_en": "Everything flows, everything changes. Adapt instead of controlling.",
        "asceticism_tag": "rest",
    },
    "stellar_focus": {
        "title_uk": "Зоряний Фокус",
        "title_en": "Stellar Focus",
        "insight_uk": "Концентрація як лазер. Один головний проєкт — і в нього все.",
        "insight_en": "Concentration like a laser. One main project — give it everything.",
        "asceticism_tag": "focus",
    },
    "cosmic_rest": {
        "title_uk": "Космічний Спокій",
        "title_en": "Cosmic Rest",
        "insight_uk": "Всесвіт каже: зупинись і відновися. Без провини.",
        "insight_en": "The universe says: stop and recharge. No guilt.",
        "asceticism_tag": "rest",
    },
    "aurora_pulse": {
        "title_uk": "Пульс Аврори",
        "title_en": "Aurora Pulse",
        "insight_uk": "Творча іскра запалює все навколо. Ділись натхненням.",
        "insight_en": "Creative spark ignites everything around. Share your inspiration.",
        "asceticism_tag": "healing",
    },
    "void_silence": {
        "title_uk": "Тиша Порожнечі",
        "title_en": "Void Silence",
        "insight_uk": "У тиші народжуються найглибші відповіді. Медитуй.",
        "insight_en": "In silence, the deepest answers are born. Meditate.",
        "asceticism_tag": "meditation",
    },
}


def _get_day_ruler(date: datetime) -> str:
    weekday = date.weekday()
    day_rulers = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    return day_rulers[weekday]


def _select_archetype(planet: str, energy_type: str, moon_phase: float) -> str:
    if 0.45 < moon_phase < 0.55:
        return "eclipse_shift"
    if moon_phase < 0.05 or moon_phase > 0.95:
        return "void_silence"

    if energy_type == "Rest" and planet not in ("Moon", "Saturn"):
        return "cosmic_rest"
    if energy_type == "Creativity" and planet not in ("Venus", "Jupiter"):
        return "aurora_pulse"

    planet_map = {
        "Sun": "solar_warrior",
        "Moon": "lunar_dreamer",
        "Mercury": "mercury_flash",
        "Venus": "venus_bloom",
        "Mars": "mars_surge",
        "Jupiter": "jupiter_grace",
        "Saturn": "saturn_anchor",
    }
    return planet_map.get(planet, "nebula_flow")


def calculate_daily_aura(
    birth_date: str,
    current_date: str,
    language: str = "uk",
) -> dict:
    try:
        parsed = datetime.strptime(current_date, "%Y-%m-%d")

        day_ruler = _get_day_ruler(parsed)

        moon_data = calculate_global_moon_data(
            datetime(parsed.year, parsed.month, parsed.day, 12, 0, tzinfo=timezone.utc)
        )
        moon_phase = moon_data["phase"]
        illumination = moon_data["illumination"]
        moon_sign = moon_data["zodiac_sign"]

        energy_type = ENERGY_MAP[day_ruler]

        archetype_key = _select_archetype(day_ruler, energy_type, moon_phase)
        archetype = AURA_ARCHETYPES[archetype_key]

        planet_visual = PLANET_HUE[day_ruler]

        pulse_speed = planet_visual["base_speed"]
        blur_radius = round(illumination * 0.8, 1)
        blend_mode = "screen"

        element = ZODIAC_ELEMENT.get(moon_sign, "fire")
        element_mod = ELEMENT_MODIFIER[element]

        lang = language if language in ("uk", "en") else "en"

        return {
            "aura_id": archetype_key,
            "title": archetype[f"title_{lang}"],
            "colors": planet_visual["colors"],
            "animation_params": {
                "pulse_speed": pulse_speed,
                "blur_radius": blur_radius,
                "blend_mode": blend_mode,
            },
            "energy_type": energy_type,
            "recommended_asceticism_tag": archetype["asceticism_tag"],
            "ai_insight": archetype[f"insight_{lang}"],
            "moon_phase": moon_phase,
            "dominant_planet": day_ruler,
            "moon_sign": moon_sign,
            "element_modifier": element_mod,
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    result = calculate_daily_aura("1990-05-15", "2026-04-14", "uk")
    print(json.dumps(result, indent=2, ensure_ascii=False))
