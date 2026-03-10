# --- AstroSync: Destiny Matrix Module v2.1 (ELITE PROGNOSTICS) ---

def reduce_to_arcana(n):
    """Зводить число до діапазону 1-22"""
    while n > 22:
        n = sum(int(d) for d in str(n))
    return n if n > 0 else 22

def calculate_destiny_matrix(birth_date: str) -> dict:
    try:
        parts = birth_date.split("-")
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])

        # --- БАЗОВИЙ ХРЕСТ ---
        A = reduce_to_arcana(day)                           # Ліва (0 років)
        B = reduce_to_arcana(month)                         # Верх (20 років)
        C = reduce_to_arcana(sum(int(d) for d in str(year)))# Права (40 років)
        D = reduce_to_arcana(A + B + C)                     # Низ (60 років)
        
        # Центр (Зона Комфорту)
        E = reduce_to_arcana(A + B + C + D)

        # --- РОДОВІ ДІАГОНАЛІ ---
        TL = reduce_to_arcana(A + B) # Верх-Ліво (10 років)
        TR = reduce_to_arcana(B + C) # Верх-Право (30 років)
        BL = reduce_to_arcana(A + D) # Низ-Ліво (70 років)
        BR = reduce_to_arcana(C + D) # Низ-Право (50 років)

        # --- КАРМІЧНИЙ ХВІСТ ---
        tail_middle = reduce_to_arcana(E + D)
        tail_bottom_inner = reduce_to_arcana(D + tail_middle)
        
        # --- КАНАЛ ГРОШЕЙ ---
        money_middle = reduce_to_arcana(E + C)
        money_entrance = reduce_to_arcana(money_middle + C)
        
        # --- ТОЧКА БАЛАНСУ ---
        balance = reduce_to_arcana(tail_middle + money_middle)

        # --- КАНАЛ КОХАННЯ ---
        love_entrance = reduce_to_arcana(balance + tail_middle)

        # --- ЛІНІЯ ЖИТТЯ (ПРОГНОСТИКА ПО РОКАХ) ---
        # 1. Основні точки (Десятиліття)
        age_0 = A; age_10 = TL; age_20 = B; age_30 = TR
        age_40 = C; age_50 = BR; age_60 = D; age_70 = BL
        
        # 2. Проміжні точки (по 5 років)
        age_5 = reduce_to_arcana(age_0 + age_10)
        age_15 = reduce_to_arcana(age_10 + age_20)
        age_25 = reduce_to_arcana(age_20 + age_30)
        age_35 = reduce_to_arcana(age_30 + age_40)
        age_45 = reduce_to_arcana(age_40 + age_50)
        age_55 = reduce_to_arcana(age_50 + age_60)
        age_65 = reduce_to_arcana(age_60 + age_70)
        age_75 = reduce_to_arcana(age_70 + age_0)

        karmic_tail_str = f"{D}-{tail_bottom_inner}-{tail_middle}"

        zones = {
            "core": {
                "day": A, "month": B, "year": C, "bottom": D, "center": E
            },
            "money_channel": {
                "entrance": money_entrance, "profession": money_middle, "balance": balance            
            },
            "love_channel": {
                "entrance": love_entrance, "ideal_partner": tail_middle, "balance": balance            
            },
            "karmic_tail": {
                "bottom": D, "inner": tail_bottom_inner, "middle": tail_middle, "combo": karmic_tail_str
            },
            "generational": {
                "father_spirit": TL, "mother_spirit": TR,
                "father_material": BL, "mother_material": BR
            },
            # НОВИЙ БЛОК ДЛЯ РОКІВ
            "life_line": {
                "age_0": age_0, "age_5": age_5, "age_10": age_10, "age_15": age_15,
                "age_20": age_20, "age_25": age_25, "age_30": age_30, "age_35": age_35,
                "age_40": age_40, "age_45": age_45, "age_50": age_50, "age_55": age_55,
                "age_60": age_60, "age_65": age_65, "age_70": age_70, "age_75": age_75
            }
        }
        return zones
    except Exception as e:
        print(f"❌ Destiny Matrix error: {e}")
        return None

# --- РОЗШИФРОВКА КАРМІЧНИХ ХВОСТІВ ---
def get_karmic_tail_meaning(tail_combo: str, language: str = "en") -> dict:
    tails = {
        "3-7-22": {"uk": {"name": "В'язень", "desc": "Відчуття обмеженості, страх змін."}, "en": {"name": "Prisoner", "desc": "Feeling restricted, fear of change."}},
        "6-8-20": {"uk": {"name": "Розчарування роду", "desc": "Складні стосунки з родичами."}, "en": {"name": "Family Disappointment", "desc": "Complex family relations."}},
        "9-3-21": {"uk": {"name": "Наглядач", "desc": "Схильність до маніпуляцій, гіперконтроль."}, "en": {"name": "Overseer", "desc": "Tendency to manipulate."}},
        "15-20-5": {"uk": {"name": "Бунтар", "desc": "Неприйняття правил і авторитетів, конфлікти."}, "en": {"name": "Rebel", "desc": "Rejection of rules, conflicts."}},
        "18-9-9": {"uk": {"name": "Магічна карма / Відлюдник", "desc": "Страх своїх здібностей, самотність."}, "en": {"name": "Magic Karma / Hermit", "desc": "Fear of own abilities."}},
        "21-4-10": {"uk": {"name": "Пригнічена душа", "desc": "Жертовна позиція, невіра в себе."}, "en": {"name": "Oppressed Soul", "desc": "Victim mentality."}},
        "12-19-7": {"uk": {"name": "Воїн", "desc": "Агресивність, конфліктність."}, "en": {"name": "Warrior", "desc": "Aggression, conflict."}},
        "15-5-8": {"uk": {"name": "Зрада / Пристрасті", "desc": "Схильність до зрад, трикутники."}, "en": {"name": "Betrayal / Passions", "desc": "Tendency for betrayal."}}
    }
    
    if tail_combo in tails: return tails[tail_combo][language]
    
    if language == "uk": return {"name": "Індивідуальна карма", "description": f"Ваш кармічний код: {tail_combo}."}
    else: return {"name": "Individual Karma", "description": f"Your karmic code: {tail_combo}."}

# --- ОПИСИ 22 АРКАНІВ (СКОРОЧЕНО ДЛЯ ПРИКЛАДУ, ЗБЕРІГАЙ СВОЮ БАЗУ) ---
ARCANA_DATA = {
    1: {"name": "The Magician", "name_uk": "Маг", "keywords": ["Leadership"], "keywords_uk": ["Лідерство"], "description": "Desc", "description_uk": "Опис", "shadow": "Shadow", "shadow_uk": "Тінь"},
    2: {"name": "The High Priestess", "name_uk": "Верховна Жриця", "keywords": ["Intuition"], "keywords_uk": ["Інтуїція"], "description": "Desc", "description_uk": "Опис", "shadow": "Shadow", "shadow_uk": "Тінь"},
    # ... Туди далі йде твоя база з 22 арканів (нічого не видаляй зі своєї старої бази, просто залиш її тут) ...
}

# (Щоб не ламати твій файл, залиш тут свій старий словник ARCANA_DATA від 1 до 22)

# --- ДОДАЄМО ЗАГЛУШКУ ЯКЩО АРКАНУ НЕМАЄ В БАЗІ ---
def get_arcana_info(number: int, language: str = "en") -> dict:
    data = ARCANA_DATA.get(number)
    if not data: # Якщо аркан не знайдено (щоб не падало)
        data = {"name": f"Arcana {number}", "name_uk": f"Аркан {number}", "keywords": [], "keywords_uk": [], "description": "", "description_uk": "", "shadow": "", "shadow_uk": ""}
        
    if language == "uk":
        return {"number": number, "name": data["name_uk"], "keywords": data["keywords_uk"], "description": data["description_uk"], "shadow": data["shadow_uk"]}
    else:
        return {"number": number, "name": data["name"], "keywords": data["keywords"], "description": data["description"], "shadow": data["shadow"]}


def calculate_chakras(matrix: dict) -> list:
    core = matrix.get("core", {})
    gen = matrix.get("generational", {})

    A = core.get("day", 0)
    B = core.get("month", 0)
    C = core.get("year", 0)
    D = core.get("bottom", 0)
    E = core.get("center", 0)

    TL = gen.get("father_spirit", 0)
    TR = gen.get("mother_spirit", 0)
    BL = gen.get("father_material", 0)
    BR = gen.get("mother_material", 0)

    def make_chakra(name, name_uk, phys, eng):
        phys_val = reduce_to_arcana(phys)
        eng_val = reduce_to_arcana(eng)
        emot_val = reduce_to_arcana(phys_val + eng_val)
        return {"name": name, "nameUk": name_uk, "physical": phys_val, "energy": eng_val, "emotions": emot_val}

    return [
        make_chakra("Sahasrara", "Сахасрара", A, B),
        make_chakra("Ajna", "Аджна", TL, TR),
        make_chakra("Vishuddha", "Вішуддха", reduce_to_arcana(A + E), reduce_to_arcana(B + E)),
        make_chakra("Anahata", "Анахата", E, E),
        make_chakra("Manipura", "Маніпура", reduce_to_arcana(E + C), reduce_to_arcana(E + D)),
        make_chakra("Svadhisthana", "Свадхістхана", BL, BR),
        make_chakra("Muladhara", "Муладхара", C, D),
    ]


def get_full_destiny_matrix(birth_date: str, language: str = "en") -> dict:
    matrix = calculate_destiny_matrix(birth_date)
    if not matrix: return None

    def enrich_block(block):
        enriched = {}
        for k, v in block.items():
            if isinstance(v, int): enriched[k] = get_arcana_info(v, language)
            else: enriched[k] = v
        return enriched

    zones_with_info = {
        "core": enrich_block(matrix["core"]),
        "money_channel": enrich_block(matrix["money_channel"]),
        "love_channel": enrich_block(matrix["love_channel"]),
        "generational": enrich_block(matrix["generational"]),
        "life_line": enrich_block(matrix["life_line"]) # НОВА ЗОНА ДОДАЄТЬСЯ В JSON
    }
    
    kt_info = enrich_block({ "bottom": matrix["karmic_tail"]["bottom"], "inner": matrix["karmic_tail"]["inner"], "middle": matrix["karmic_tail"]["middle"] })
    kt_info["combo"] = matrix["karmic_tail"]["combo"]
    kt_info["meaning"] = get_karmic_tail_meaning(kt_info["combo"], language)
    zones_with_info["karmic_tail"] = kt_info

    chakra_health = calculate_chakras(matrix)

    return {"birth_date": birth_date, "matrix": zones_with_info, "chakra_health": chakra_health, "language": language}