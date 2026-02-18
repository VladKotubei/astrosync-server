# --- AstroSync: Quantum Sephirot Engine v1.0 ---
from datetime import datetime
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const

# Відповідність Планет до Сефір (Дерево Життя)
SEPHIROT_MAP = {
    "Sun": {"name": "Tiphereth", "meaning": "Harmony & Beauty", "action": "Shine, Lead, Heal"},
    "Moon": {"name": "Yesod", "meaning": "Foundation & Dreams", "action": "Connect, Imagine, Reflect"},
    "Mercury": {"name": "Hod", "meaning": "Splendor & Intellect", "action": "Communicate, Analyze, Learn"},
    "Venus": {"name": "Netzach", "meaning": "Victory & Emotion", "action": "Love, Create, Enjoy"},
    "Mars": {"name": "Gevurah", "meaning": "Severity & Strength", "action": "Discipline, Cut off, Defend"},
    "Jupiter": {"name": "Chesed", "meaning": "Mercy & Expansion", "action": "Give, Expand, Explore"},
    "Saturn": {"name": "Binah", "meaning": "Understanding & Structure", "action": "Plan, Structure, Limit"}
}

# Порядок планетних годин (Халдейський ряд)
CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

def get_current_planetary_hour(latitude, longitude):
    """
    Визначає поточну планетну годину.
    Спрощена версія: розбиває добу на 24 рівні частини від сходу сонця (приблизно 6:00).
    Для Elite версії тут можна додати точний розрахунок сходу/заходу.
    """
    now = datetime.now()
    
    # Приблизний схід сонця о 6:00 (для спрощення)
    sunrise_hour = 6 
    
    # Скільки годин пройшло від сходу
    hours_passed = now.hour - sunrise_hour
    if hours_passed < 0:
        hours_passed += 24
        
    # Визначаємо правителя дня (від дня тижня)
    # 0=Mon(Moon), 1=Tue(Mars), 2=Wed(Merc), 3=Thu(Jup), 4=Fri(Ven), 5=Sat(Sat), 6=Sun(Sun)
    weekday = now.weekday()
    day_rulers = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    day_ruler = day_rulers[weekday]
    
    # Знаходимо індекс правителя дня в Халдейському ряду
    start_index = CHALDEAN_ORDER.index(day_ruler)
    
    # Зсуваємося на кількість годин, що пройшли
    current_planet_index = (start_index + hours_passed) % 7
    current_planet = CHALDEAN_ORDER[current_planet_index]
    
    return current_planet

def calculate_quantum_state(latitude=50.45, longitude=30.52):
    """
    Головна функція: розраховує стан квантового поля на зараз.
    """
    try:
        # 1. Отримуємо поточну планету-управителя часу
        active_planet = get_current_planetary_hour(latitude, longitude)
        
        # 2. Отримуємо відповідну Сефіру
        sephira = SEPHIROT_MAP.get(active_planet, SEPHIROT_MAP["Sun"])
        
        # 3. Генеруємо "Квантову інструкцію" (Manifestation Guide)
        quantum_instruction = f"The Universe is vibrating on the frequency of {active_planet}. " \
                              f"Access the sphere of {sephira['name']} ({sephira['meaning']}). " \
                              f"Best tactical action now: {sephira['action']}."
        
        return {
            "active_planet": active_planet,
            "sephira_name": sephira['name'],
            "sephira_meaning": sephira['meaning'],
            "action_verb": sephira['action'],
            "quantum_message": quantum_instruction,
            "probability_level": "High"  # Можна рандомізувати або прив'язати до аспектів
        }
        
    except Exception as e:
        print(f"❌ Quantum Engine Error: {e}")
        return None

# --- ТЕСТ ---
if __name__ == "__main__":
    print("⚛️ Initializing Quantum Sephirot Engine...")
    state = calculate_quantum_state()
    if state:
        print(f"\n🌀 Current Field Status:")
        print(f"   Planet: {state['active_planet']}")
        print(f"   Sephira: {state['sephira_name']}")
        print(f"   Instruction: {state['quantum_message']}")