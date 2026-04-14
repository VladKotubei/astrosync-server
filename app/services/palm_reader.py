"""
Palm image analysis service powered by OpenAI Vision API.

Provides four levels of palm reading for the AstroSync app:

    validate_palm_image      – Quick check that the uploaded image actually
                               contains a human palm (GPT-4o-mini, low detail).

    visual_scan              – Weekly energy snapshot: dominant element, aura
                               colour and an inspiring quote (GPT-4o-mini).

    deep_scan                – Full monthly reading covering every major and
                               minor line, karmic zones and practice
                               recommendations (GPT-4o, high detail).

    guest_compatibility_scan – Compare a guest's palm against the owner's
                               stored reading data (GPT-4o, high detail).

All functions expect the *synchronous* ``openai.OpenAI`` client that is
already initialised in ``server.py``.
"""

from __future__ import annotations

import json
import logging

from openai import OpenAI

logger = logging.getLogger(__name__)

_IRON_RULES = """\
ABSOLUTE RULES — NEVER VIOLATE:
1. NEVER predict death, illness, accidents, or fatal events
2. A short life line means ONLY "impulsive life energy, tendency for quick decisions"
3. ALL negative signs are "Karmic Growth Zones" — challenges for personal development
4. Breaks in lines = "transition periods leading to transformation"
5. Crosses = "points of karmic lessons that strengthen character"
6. Islands = "periods of deep introspection and inner work"
7. You are an esoteric entertainer, NOT a medical professional
8. Frame everything positively as growth opportunities
9. Never use words: death, disease, illness, accident, danger, fatal, terminal"""

_DEEP_IRON_RULES = """\
ABSOLUTE RULES — NEVER VIOLATE:
1. NEVER predict death, illness, accidents, or fatal events
2. A short life line means ONLY "impulsive life energy, tendency for quick decisions and sprint tasks"
3. ALL negative signs (crosses, breaks, islands) are interpreted as "Karmic Growth Zones"
4. Breaks in lines = "transition periods leading to transformation"
5. Crosses = "points of karmic lessons that strengthen character"
6. Islands = "periods of deep introspection and inner work"
7. You are an esoteric entertainer, NOT a medical professional
8. Frame everything positively as growth opportunities
9. Never use words: death, disease, illness, accident, danger, fatal, terminal"""

_COMPAT_IRON_RULES = """\
ABSOLUTE RULES — NEVER VIOLATE:
1. NEVER predict death, illness, accidents, or fatal events
2. ALL negative signs are "Karmic Growth Zones"
3. Frame everything positively as growth opportunities
4. You are an esoteric entertainer, NOT a medical professional
5. Never use words: death, disease, illness, accident, danger, fatal, terminal"""


def _image_content(image_base64: str, *, detail: str = "low") -> dict:
    """Build an ``image_url`` content block for the OpenAI chat API."""
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{image_base64}",
            "detail": detail,
        },
    }


# ---------------------------------------------------------------------------
# 1. Validation
# ---------------------------------------------------------------------------

async def validate_palm_image(client: OpenAI, image_base64: str) -> dict:
    """Validate if the image contains a human palm using GPT-4o-mini with vision."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an image classifier. Determine if this image "
                        "shows a human palm (open hand, palm side facing camera). "
                        'Respond ONLY with JSON: {"is_valid_palm": true/false, '
                        '"confidence": 0.0-1.0, "reason": "brief explanation"}'
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Classify this image."},
                        _image_content(image_base64, detail="low"),
                    ],
                },
            ],
        )

        result: dict = json.loads(response.choices[0].message.content)

        if result.get("confidence", 0.0) < 0.7:
            result["is_valid_palm"] = False

        return result

    except Exception:
        logger.error("Palm image validation failed", exc_info=True)
        return {
            "is_valid_palm": False,
            "confidence": 0.0,
            "reason": "Analysis failed",
        }


# ---------------------------------------------------------------------------
# 2. Visual (weekly) scan
# ---------------------------------------------------------------------------

async def visual_scan(
    client: OpenAI,
    image_base64: str,
    language: str = "en",
) -> dict:
    """Quick weekly energy scan using GPT-4o-mini with vision."""
    system_prompt = (
        "You are a mystical palm energy reader for the AstroSync app.\n"
        "Analyze the palm image and provide a quick energy reading.\n\n"
        f"{_IRON_RULES}\n\n"
        f"Respond in {language} language.\n"
        "Respond ONLY with JSON:\n"
        "{\n"
        '  "energy_quote": "short inspiring quote based on palm energy (1-2 sentences)",\n'
        '  "dominant_energy": "fire/water/earth/air",\n'
        '  "color_aura": "#hex_color representing the palm\'s energy"\n'
        "}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Read this palm's energy."},
                        _image_content(image_base64, detail="low"),
                    ],
                },
            ],
        )

        return json.loads(response.choices[0].message.content)

    except Exception:
        logger.error("Visual scan failed", exc_info=True)
        raise ValueError("Visual scan failed")


# ---------------------------------------------------------------------------
# 3. Deep (monthly) scan
# ---------------------------------------------------------------------------

async def deep_scan(
    client: OpenAI,
    image_base64: str,
    language: str = "en",
) -> dict:
    """Full monthly palm analysis using GPT-4o (not mini!) with vision."""
    system_prompt = (
        "You are an expert mystical palmist for the AstroSync app.\n"
        "Perform a comprehensive palm reading analyzing all major and minor lines.\n\n"
        f"{_DEEP_IRON_RULES}\n\n"
        f"Respond in {language} language.\n"
        "Respond ONLY with JSON matching this EXACT schema:\n"
        "{\n"
        '  "scan_date": "ISO date string (today\'s date)",\n'
        '  "palm_data": {\n'
        '    "life_line": {"strength": "strong/medium/faint/absent", "type": "descriptive type name", "description": "2-3 sentences"},\n'
        '    "heart_line": {"strength": "...", "type": "...", "description": "..."},\n'
        '    "head_line": {"strength": "...", "type": "...", "description": "..."},\n'
        '    "fate_line": {"strength": "...", "type": "...", "description": "..."},\n'
        '    "mars_line": {"strength": "...", "type": "...", "description": "..."},\n'
        '    "sun_line": {"strength": "...", "type": "...", "description": "..."},\n'
        '    "special_marks": ["list of notable marks found on the palm"],\n'
        '    "dominant_element": "fire/water/earth/air",\n'
        '    "energy_signature": "short archetype name (e.g. \'impulsive_creator\', \'calm_healer\')"\n'
        "  },\n"
        '  "ai_report": "Full detailed report (5-8 paragraphs) about the person\'s palm reading",\n'
        '  "karmic_zones": ["list of 2-4 areas for personal growth"],\n'
        '  "asceticism_recommendations": ["list of 3-5 recommended practices"]\n'
        "}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Perform a deep palm reading."},
                        _image_content(image_base64, detail="high"),
                    ],
                },
            ],
        )

        return json.loads(response.choices[0].message.content)

    except Exception:
        logger.error("Deep scan failed", exc_info=True)
        raise ValueError("Deep scan failed")


# ---------------------------------------------------------------------------
# 4. Guest compatibility scan
# ---------------------------------------------------------------------------

async def guest_compatibility_scan(
    client: OpenAI,
    guest_image_base64: str,
    owner_palm_data: dict,
    language: str = "en",
) -> dict:
    """Compare guest's palm with owner's stored palm data using GPT-4o with vision."""
    system_prompt = (
        "You are a mystical palm compatibility analyst for the AstroSync app.\n"
        "Compare the guest's palm image with the owner's palm reading data.\n\n"
        f"{_COMPAT_IRON_RULES}\n\n"
        "Owner's palm data for comparison:\n"
        f"{json.dumps(owner_palm_data, ensure_ascii=False)}\n\n"
        f"Respond in {language} language.\n"
        "Respond ONLY with JSON:\n"
        "{\n"
        '  "compatibility_score": 0-100,\n'
        '  "compatibility_type": "fun label (e.g. \'Startup Dream Team\', \'Creative Powerhouse\')",\n'
        '  "strengths": ["3-4 compatibility strengths"],\n'
        '  "challenges": ["2-3 areas to work on together"],\n'
        '  "team_dynamic": "2-3 sentence description of how these two work together",\n'
        '  "fun_fact": "one quirky or surprising comparison between the two palms"\n'
        "}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this guest's palm for compatibility."},
                        _image_content(guest_image_base64, detail="high"),
                    ],
                },
            ],
        )

        return json.loads(response.choices[0].message.content)

    except Exception:
        logger.error("Compatibility scan failed", exc_info=True)
        raise ValueError("Compatibility scan failed")
