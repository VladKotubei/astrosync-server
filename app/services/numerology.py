# --- AstroSync: Advanced Numerology Module v3.0 ---
from datetime import datetime

def reduce_number(n):
    """Допоміжна функція: зводить число до однієї цифри (крім 11, 22, 33)"""
    while n > 9 and n not in [11, 22, 33]:
        n = sum(int(digit) for digit in str(n))
    return n

def calculate_life_path(birthdate):
    """Рахує незмінне число долі"""
    clean_date = birthdate.replace("-", "").replace(".", "").replace("/", "")
    total = sum(int(digit) for digit in clean_date)
    return reduce_number(total)

def calculate_soul_number(name):
    """
    Число Душі - сума голосних букв імені
    Показує внутрішні бажання та мотивацію
    """
    vowels = "AEIOUaeiouАЕЄИІЇОУЮЯаеєиіїоуюя"
    vowel_values = {
        'A': 1, 'E': 5, 'I': 9, 'O': 6, 'U': 3,
        'a': 1, 'e': 5, 'i': 9, 'o': 6, 'u': 3,
        'А': 1, 'Е': 6, 'Є': 6, 'И': 1, 'І': 1, 'Ї': 1, 'О': 7, 'У': 3, 'Ю': 7, 'Я': 1,
        'а': 1, 'е': 6, 'є': 6, 'и': 1, 'і': 1, 'ї': 1, 'о': 7, 'у': 3, 'ю': 7, 'я': 1
    }
    
    total = 0
    for char in name:
        if char in vowels:
            total += vowel_values.get(char, 0)
    
    return reduce_number(total) if total > 0 else 0

def calculate_personality_number(name):
    """
    Число Особистості - сума приголосних букв імені
    Показує як тебе бачать інші люди
    """
    consonants = "BCDFGHJKLMNPQRSTVWXYZbcdfghjklmnpqrstvwxyzБВГҐДЖЗЙКЛМНПРСТФХЦЧШЩбвгґджзйклмнпрстфхцчшщ"
    consonant_values = {
        'B': 2, 'C': 3, 'D': 4, 'F': 8, 'G': 3, 'H': 5, 'J': 1, 'K': 2, 'L': 3, 'M': 4,
        'N': 5, 'P': 7, 'Q': 8, 'R': 9, 'S': 1, 'T': 2, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
        'b': 2, 'c': 3, 'd': 4, 'f': 8, 'g': 3, 'h': 5, 'j': 1, 'k': 2, 'l': 3, 'm': 4,
        'n': 5, 'p': 7, 'q': 8, 'r': 9, 's': 1, 't': 2, 'v': 4, 'w': 5, 'x': 6, 'y': 7, 'z': 8,
        'Б': 2, 'В': 3, 'Г': 3, 'Ґ': 3, 'Д': 4, 'Ж': 8, 'З': 8, 'Й': 1, 'К': 2, 'Л': 3, 'М': 4,
        'Н': 5, 'П': 7, 'Р': 9, 'С': 1, 'Т': 2, 'Ф': 8, 'Х': 5, 'Ц': 3, 'Ч': 7, 'Ш': 8, 'Щ': 9,
        'б': 2, 'в': 3, 'г': 3, 'ґ': 3, 'д': 4, 'ж': 8, 'з': 8, 'й': 1, 'к': 2, 'л': 3, 'м': 4,
        'н': 5, 'п': 7, 'р': 9, 'с': 1, 'т': 2, 'ф': 8, 'х': 5, 'ц': 3, 'ч': 7, 'ш': 8, 'щ': 9
    }
    
    total = 0
    for char in name:
        if char in consonants:
            total += consonant_values.get(char, 0)
    
    return reduce_number(total) if total > 0 else 0

def get_personal_cycles(birthdate):
    """Рахує динамічні цикли на СЬОГОДНІ"""
    today = datetime.now()
    
    # Розбираємо дату народження (очікуємо формат РРРР-ММ-ДД)
    parts = birthdate.replace("/", "-").split("-")
    birth_month = int(parts[1])
    birth_day = int(parts[2])
    
    # 1. Персональний Рік = Поточний Рік + День Нар + Місяць Нар
    current_year = today.year
    py_raw = current_year + birth_month + birth_day
    personal_year = reduce_number(py_raw)
    
    # 2. Персональний Місяць = Персональний Рік + Поточний Місяць
    pm_raw = personal_year + today.month
    personal_month = reduce_number(pm_raw)
    
    # 3. Персональний День = Персональний Місяць + Поточний День
    pd_raw = personal_month + today.day
    personal_day = reduce_number(pd_raw)
    
    return {
        "personal_year": personal_year,
        "personal_month": personal_month,
        "personal_day": personal_day
    }

def get_number_description(number, number_type="life_path", language="en"):
    """
    Повертає детальний опис числа
    number_type: "life_path", "soul", "personality", "day"
    language: "en", "uk"
    """
    from app.services.translations import get_description
    return get_description(number, number_type, language)
    """
    Повертає детальний опис числа
    number_type: "life_path", "soul", "personality", "day"
    """
    descriptions = {
        "life_path": {
            1: "The Leader. Independent, ambitious, and innovative. You're a natural pioneer who creates your own path.",
            2: "The Peacemaker. Diplomatic, sensitive, and cooperative. You excel at building harmony and partnerships.",
            3: "The Creative. Expressive, optimistic, and artistic. You bring joy and inspiration to others.",
            4: "The Builder. Practical, disciplined, and hardworking. You create solid foundations and lasting structures.",
            5: "The Adventurer. Dynamic, freedom-loving, and versatile. You thrive on change and new experiences.",
            6: "The Nurturer. Responsible, caring, and family-oriented. You bring healing and balance to your community.",
            7: "The Seeker. Analytical, spiritual, and introspective. You search for deeper truths and wisdom.",
            8: "The Powerhouse. Ambitious, authoritative, and material-focused. You achieve great success through determination.",
            9: "The Humanitarian. Compassionate, idealistic, and philanthropic. You serve the greater good.",
            11: "The Visionary. Intuitive, inspirational, and enlightened. You're a spiritual messenger with profound insights.",
            22: "The Master Builder. Practical visionary who turns dreams into reality on a grand scale.",
            33: "The Master Teacher. Selfless, nurturing guide who uplifts humanity through compassion."
        },
        "soul": {
            1: "You crave independence and leadership. Deep down, you want to be first and make your mark.",
            2: "You desire peace and partnership. Your soul seeks harmony and meaningful connections.",
            3: "You yearn for creative expression. Your inner self wants to inspire and bring joy.",
            4: "You need stability and structure. Your soul finds peace in building and organizing.",
            5: "You seek freedom and adventure. Your inner spirit craves variety and exploration.",
            6: "You desire to nurture and help others. Your soul finds purpose in service and care.",
            7: "You crave knowledge and spiritual growth. Your inner self seeks deeper understanding.",
            8: "You desire success and recognition. Your soul wants to achieve and prosper.",
            9: "You yearn to make a difference. Your inner self wants to serve humanity.",
            11: "You desire spiritual enlightenment. Your soul seeks to inspire and uplift.",
            22: "You dream of building something lasting. Your inner visionary wants to create legacy.",
            33: "You seek to heal and teach. Your soul's purpose is compassionate service."
        },
        "personality": {
            1: "Others see you as confident and independent. You appear as a natural leader.",
            2: "Others see you as diplomatic and gentle. You appear as a peacemaker.",
            3: "Others see you as charming and creative. You appear as an entertainer.",
            4: "Others see you as reliable and practical. You appear as the rock others depend on.",
            5: "Others see you as exciting and unpredictable. You appear as an adventurer.",
            6: "Others see you as caring and responsible. You appear as the helper everyone trusts.",
            7: "Others see you as mysterious and intelligent. You appear as the wise observer.",
            8: "Others see you as powerful and successful. You appear as someone who gets things done.",
            9: "Others see you as compassionate and idealistic. You appear as the humanitarian.",
            11: "Others see you as inspiring and charismatic. You appear as the visionary leader.",
            22: "Others see you as capable of greatness. You appear as someone destined for big things.",
            33: "Others see you as a natural healer. You appear as the compassionate guide."
        },
        "day": {
            1: "Today is about new beginnings. Take initiative and start something fresh.",
            2: "Today calls for cooperation. Focus on partnerships and diplomatic solutions.",
            3: "Today favors creativity. Express yourself and enjoy social connections.",
            4: "Today requires practical work. Build foundations and organize your life.",
            5: "Today brings change. Embrace new experiences and stay flexible.",
            6: "Today is for relationships. Nurture your loved ones and create harmony.",
            7: "Today is introspective. Seek knowledge and spend time in reflection.",
            8: "Today favors ambition. Make power moves toward your financial goals.",
            9: "Today calls for completion. Let go of what no longer serves you.",
            11: "Today is spiritually charged. Pay attention to intuitive insights.",
            22: "Today supports big visions. Work on your master plan.",
            33: "Today is about compassionate service. Help others selflessly."
        }
    }
    
    return descriptions.get(number_type, {}).get(number, "A unique energy guides you today.")

# --- Тест ---
if __name__ == "__main__":
    print("🔮 Тестуємо розширену нумерологію v3.0...")
    
    name = "Alex"
    birthdate = "1990-05-20"
    
    print(f"\nІм'я: {name}")
    print(f"Дата: {birthdate}")
    print("-" * 50)
    
    lp = calculate_life_path(birthdate)
    soul = calculate_soul_number(name)
    personality = calculate_personality_number(name)
    cycles = get_personal_cycles(birthdate)
    
    print(f"Число Життєвого Шляху: {lp}")
    print(f"  → {get_number_description(lp, 'life_path')}\n")
    
    print(f"Число Душі: {soul}")
    print(f"  → {get_number_description(soul, 'soul')}\n")
    
    print(f"Число Особистості: {personality}")
    print(f"  → {get_number_description(personality, 'personality')}\n")
    
    print(f"Персональний День: {cycles['personal_day']}")
    print(f"  → {get_number_description(cycles['personal_day'], 'day')}")