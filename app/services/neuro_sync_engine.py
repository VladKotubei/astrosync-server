from app.services.quantum_engine import calculate_quantum_state, ENERGY_MAP
from app.services.astro_basic import get_moon_phase
from datetime import datetime
import random

PLANET_FREQUENCY_MAP = {
    "Sun": 528, "Moon": 432, "Mercury": 480, "Venus": 396,
    "Mars": 417, "Jupiter": 444, "Saturn": 462,
}

ENERGY_BINAURAL_OFFSET = {
    "Focus": 14,          # Beta waves (12-30 Hz)
    "Rest": 4,            # Theta waves (4-8 Hz)
    "Communication": 10,  # Alpha waves (8-12 Hz)
    "Creativity": 8,      # Alpha waves (8-12 Hz)
}

PLANET_COLORS = {
    "Sun":     ["#FFD700", "#FF8C00", "#FF4500"],
    "Moon":    ["#C0C0C0", "#87CEEB", "#4169E1"],
    "Mercury": ["#00CED1", "#20B2AA", "#008B8B"],
    "Venus":   ["#FF69B4", "#FF1493", "#C71585"],
    "Mars":    ["#FF0000", "#DC143C", "#8B0000"],
    "Jupiter": ["#9370DB", "#8A2BE2", "#4B0082"],
    "Saturn":  ["#000000", "#7B2FBE", "#00F5FF"],
}

ENERGY_BREATHING = {
    "Focus":         {"in": 4, "hold": 4, "out": 4},
    "Rest":          {"in": 4, "hold": 7, "out": 8},
    "Communication": {"in": 4, "hold": 4, "out": 6},
    "Creativity":    {"in": 5, "hold": 3, "out": 5},
}

PRESET_NAMES = {
    "Sun": "Solar Vitality", "Moon": "Lunar Calm",
    "Mercury": "Mercury Flow", "Venus": "Venus Harmony",
    "Mars": "Mars Power", "Jupiter": "Jupiter Wisdom",
    "Saturn": "Saturn Focus",
}

AI_INSIGHTS = {
    "Focus": [
        "Intense planetary energy today. This frequency anchors your focus.",
        "Strong cosmic pressure detected. Use this session to stay grounded.",
        "High-energy transit active. Channel it into deep concentration.",
    ],
    "Rest": [
        "The cosmos invites stillness. Let this frequency guide you to calm.",
        "Lunar energy dominates. Perfect moment for deep restoration.",
        "Gentle planetary flow detected. Surrender to the rhythm of rest.",
    ],
    "Communication": [
        "Mercury's influence is strong. This frequency opens your expressive channels.",
        "Cosmic alignment favors connection. Let the vibrations clear your mind.",
        "Planetary currents support clarity. Tune in and find your voice.",
    ],
    "Creativity": [
        "Venus and Jupiter radiate inspiration. Let this session unlock your vision.",
        "Creative planetary alignment detected. Your imagination is amplified today.",
        "Harmonious cosmic energy flows. Channel it into something beautiful.",
    ],
}


def calculate_neuro_sync_recipe(latitude: float = 50.45,
                                longitude: float = 30.52) -> dict:
    """
    Calculates a daily Neuro-Sync recipe based on current planetary state.
    Returns a dict with: recommended_preset, base_hz, binaural_offset_hz,
    visual_theme, colors, breathing_pattern, active_planet, energy_type,
    moon_phase, ai_insight.
    """
    try:
        quantum_state = calculate_quantum_state(latitude, longitude)
        active_planet = quantum_state.get("active_planet", "Sun")
        energy_type = ENERGY_MAP.get(active_planet, "Focus")

        if active_planet not in PLANET_FREQUENCY_MAP:
            active_planet = "Sun"
        if energy_type not in ENERGY_BINAURAL_OFFSET:
            energy_type = "Focus"

        today_slash = datetime.now().strftime("%Y/%m/%d")
        moon_phase = get_moon_phase(today_slash)

        base_offset = ENERGY_BINAURAL_OFFSET[energy_type]
        if "New" in moon_phase:
            binaural_offset = 4
        elif "Full" in moon_phase:
            binaural_offset = base_offset + 2
        else:
            binaural_offset = base_offset

        return {
            "recommended_preset": PRESET_NAMES[active_planet],
            "base_hz": PLANET_FREQUENCY_MAP[active_planet],
            "binaural_offset_hz": binaural_offset,
            "visual_theme": "quantum_sphere",
            "colors": PLANET_COLORS[active_planet],
            "breathing_pattern": ENERGY_BREATHING[energy_type],
            "active_planet": active_planet,
            "energy_type": energy_type,
            "moon_phase": moon_phase,
            "ai_insight": random.choice(AI_INSIGHTS[energy_type]),
        }
    except Exception as e:
        return {
            "recommended_preset": "Grounding",
            "base_hz": 432,
            "binaural_offset_hz": 7,
            "visual_theme": "quantum_sphere",
            "colors": ["#7B2FBE", "#00F5FF", "#FFD700"],
            "breathing_pattern": {"in": 4, "hold": 4, "out": 4},
            "active_planet": "Sun",
            "energy_type": "Focus",
            "moon_phase": "Unknown",
            "ai_insight": "Stay grounded. Let the frequencies guide you.",
            "error": str(e),
        }
