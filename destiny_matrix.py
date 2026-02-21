# --- AstroSync: Destiny Matrix Module v2.0 (ELITE) ---
# Система матриці долі з 22 Старшими Арканами Таро

def reduce_to_arcana(n):
    """
    Зводимо число до діапазону 1-22 (Аркани Таро)
    Якщо більше 22 — додаємо цифри
    """
    while n > 22:
        n = sum(int(d) for d in str(n))
    return n if n > 0 else 22


def calculate_destiny_matrix(birth_date: str) -> dict:
    """
    Розраховує матрицю долі за датою народження
    Включає старі зони та НОВІ (Гроші, Любов, Карма, Рід)
    """
    try:
        parts = birth_date.split("-")
        day   = int(parts[2])
        month = int(parts[1])
        year  = int(parts[0])

        # --- БАЗОВИЙ ХРЕСТ (Прямий квадрат) ---
        A = reduce_to_arcana(day)                           # Ліва (Я / Візитка)
        B = reduce_to_arcana(month)                         # Верх (Талант / Небо)
        C = reduce_to_arcana(sum(int(d) for d in str(year)))# Права (Матерія / Гроші)
        D = reduce_to_arcana(A + B + C)                     # Низ (Минула карма)
        
        # --- ЦЕНТР МАТРИЦІ (Особистість) ---
        E = reduce_to_arcana(A + B + C + D)

        # --- СТАРІ ЛІНІЇ (Збережено для зворотної сумісності) ---
        F = reduce_to_arcana(A + B)   # Особистий комфорт
        G = reduce_to_arcana(C + D)   # Соціальний потенціал
        H = reduce_to_arcana(A + D)   # Таланти
        I = reduce_to_arcana(B + C)   # Гроші/матерія
        K = reduce_to_arcana(A + E)   # Карма минулого
        L = reduce_to_arcana(D + E)   # Карма майбутнього

        # --- РОДОВИЙ КВАДРАТ (Діагоналі) ---
        TL = reduce_to_arcana(A + B) # Верх-Ліво (Рід батька дух)
        TR = reduce_to_arcana(B + C) # Верх-Право (Рід матері дух)
        BL = reduce_to_arcana(A + D) # Низ-Ліво (Рід батька матерія)
        BR = reduce_to_arcana(C + D) # Низ-Право (Рід матері матерія)

        # --- КАРМІЧНИЙ ХВІСТ (Точна формула Darikarma) ---
        tail_middle = reduce_to_arcana(E + D)               # Точка між Центром(E) і Низом(D)
        tail_bottom_inner = reduce_to_arcana(D + tail_middle) # Точка між Низом і Серединою хвоста
        
        # --- КАНАЛ ГРОШЕЙ ---
        money_middle = reduce_to_arcana(E + C)              # Професія/Реалізація
        money_entrance = reduce_to_arcana(money_middle + C) # Вхід в канал фінансів
        
        # --- ТОЧКА БАЛАНСУ ---
        # Точка між лінією кохання і лінією грошей
        balance = reduce_to_arcana(tail_middle + money_middle)

        # --- КАНАЛ КОХАННЯ ---
        love_entrance = reduce_to_arcana(balance + tail_middle) # Вхід у стосунки / ідеальний партнер

        # Формуємо рядок Кармічного Хвоста (напр. 15-20-5)
        karmic_tail_str = f"{D}-{tail_bottom_inner}-{tail_middle}"

        zones = {
            "core": {
                "day": A, "month": B, "year": C, "bottom": D, "center": E
            },
            "money_channel": {
                "entrance": money_entrance,   
                "profession": money_middle,   
                "balance": balance            
            },
            "love_channel": {
                "entrance": love_entrance,    
                "ideal_partner": tail_middle, 
                "balance": balance            
            },
            "karmic_tail": {
                "bottom": D,
                "inner": tail_bottom_inner,
                "middle": tail_middle,
                "combo": karmic_tail_str
            },
            "generational": {
                "father_spirit": TL, "mother_spirit": TR,
                "father_material": BL, "mother_material": BR
            },
            "old_zones": {
                "self": A, "planet": B, "society": C, "result": D, "center": E,
                "comfort": F, "potential": G, "talent": H, "material": I,
                "past_karma": K, "future_karma": L
            }
        }

        return zones

    except Exception as e:
        print(f"❌ Destiny Matrix error: {e}")
        return None

# --- РОЗШИФРОВКА КАРМІЧНИХ ХВОСТІВ ЗІ ШПАРГАЛКИ ---
def get_karmic_tail_meaning(tail_combo: str, language: str = "en") -> dict:
    tails = {
        "3-7-22": {"uk": {"name": "В'язень", "desc": "Відчуття обмеженості, страх змін. Кармічна задача — навчитися жити вільно і не боятися нового."}, "en": {"name": "Prisoner", "desc": "Feeling restricted, fear of change."}},
        "6-8-20": {"uk": {"name": "Розчарування роду", "desc": "Складні стосунки з родичами, конфлікти. Кармічна задача — пробачити сім'ю і прийняти своє коріння."}, "en": {"name": "Family Disappointment", "desc": "Complex family relations. Task: forgive your roots."}},
        "9-3-21": {"uk": {"name": "Наглядач", "desc": "Схильність до маніпуляцій, бажання управляти іншими. Важливо відпустити гіперконтроль."}, "en": {"name": "Overseer", "desc": "Tendency to manipulate and control others."}},
        "15-20-5": {"uk": {"name": "Бунтар", "desc": "Неприйняття правил і авторитетів, конфлікти. У минулому житті ви руйнували родину. Задача — створити міцні традиції."}, "en": {"name": "Rebel", "desc": "Rejection of rules, conflicts with family."}},
        "18-9-9": {"uk": {"name": "Магічна карма / Відлюдник", "desc": "Страх своїх здібностей, самотність, замкнутість. У минулому ви володіли знаннями, але злякалися їх. Час розкрити свій потенціал."}, "en": {"name": "Magic Karma / Hermit", "desc": "Fear of own abilities, loneliness. Time to unlock potential."}},
        "21-4-10": {"uk": {"name": "Пригнічена душа", "desc": "Жертовна позиція, невіра в себе, страх діяти. Задача — знайти внутрішню силу і стати лідером свого життя."}, "en": {"name": "Oppressed Soul", "desc": "Victim mentality, lack of self-belief."}},
        "12-19-7": {"uk": {"name": "Воїн", "desc": "Агресивність, конфліктність, любов до ризику. Треба навчитися досягати цілей мирним шляхом."}, "en": {"name": "Warrior", "desc": "Aggression, conflict. Need to learn peaceful achievement."}},
        "15-5-8": {"uk": {"name": "Зрада / Пристрасті", "desc": "Схильність до зрад, сімейні трикутники, складнощі у стосунках. Задача — бути чесним із собою та партнером."}, "en": {"name": "Betrayal / Passions", "desc": "Tendency for betrayal, relationship triangles."}}
    }
    
    if tail_combo in tails:
        return tails[tail_combo][language]
    
    # Якщо унікальний комбо не знайдено, даємо загальний опис
    if language == "uk":
        return {"name": "Індивідуальна карма", "description": f"Ваш кармічний код: {tail_combo}. Пропрацюйте нижню точку вашої матриці для розблокування енергії."}
    else:
        return {"name": "Individual Karma", "description": f"Your karmic code: {tail_combo}. Work on your bottom energy point to unblock your path."}

# --- ОПИСИ 22 АРКАНІВ ---
# (Ми зберегли ТВОЮ базу арканів)
ARCANA_DATA = {
    1: {
        "name": "The Magician",
        "name_uk": "Маг",
        "keywords": ["Leadership", "Willpower", "Initiative"],
        "keywords_uk": ["Лідерство", "Сила волі", "Ініціатива"],
        "description": "You are a natural creator and leader. You have the power to manifest your desires into reality.",
        "description_uk": "Ти природжений творець і лідер. Маєш силу втілювати бажання в реальність. Твоя енергія магнетична.",
        "shadow": "Manipulation, ego, scattered energy",
        "shadow_uk": "Маніпуляції, его, розпорошена енергія",
    },
    2: {
        "name": "The High Priestess",
        "name_uk": "Верховна Жриця",
        "keywords": ["Intuition", "Wisdom", "Mystery"],
        "keywords_uk": ["Інтуїція", "Мудрість", "Таємниця"],
        "description": "You possess deep intuition and inner knowing. Your wisdom comes from within.",
        "description_uk": "Ти маєш глибоку інтуїцію та внутрішнє знання. Твоя мудрість — з середини.",
        "shadow": "Secrets, withdrawal, over-dependence on feelings",
        "shadow_uk": "Таємниці, відчуження, надмірна залежність від почуттів",
    },
    3: {
        "name": "The Empress",
        "name_uk": "Імператриця",
        "keywords": ["Creativity", "Abundance", "Nurturing"],
        "keywords_uk": ["Творчість", "Достаток", "Турбота"],
        "description": "You radiate abundance and creative power. You nurture growth in everything around you.",
        "description_uk": "Ти випромінюєш достаток і творчу силу. Ти плекаєш зростання у всьому навколо.",
        "shadow": "Over-dependence, possessiveness, creative blocks",
        "shadow_uk": "Залежність, власницькість, творчі блоки",
    },
    4: {
        "name": "The Emperor",
        "name_uk": "Імператор",
        "keywords": ["Structure", "Authority", "Stability"],
        "keywords_uk": ["Структура", "Авторитет", "Стабільність"],
        "description": "You are the builder of foundations. You bring order and structure to chaos.",
        "description_uk": "Ти будівельник фундаментів. Ти вносиш порядок і структуру в хаос.",
        "shadow": "Rigidity, control, stubbornness",
        "shadow_uk": "Жорсткість, контроль, впертість",
    },
    5: {
        "name": "The Hierophant",
        "name_uk": "Ієрофант",
        "keywords": ["Tradition", "Guidance", "Spiritual teaching"],
        "keywords_uk": ["Традиція", "Наставництво", "Духовне вчення"],
        "description": "You are a keeper of wisdom and tradition. You have a gift for teaching.",
        "description_uk": "Ти хранитель мудрості та традицій. Маєш дар навчати і спрямовувати інших.",
        "shadow": "Dogmatism, conformity, over-reliance on rules",
        "shadow_uk": "Догматизм, конформізм, надмірна залежність від правил",
    },
    6: {
        "name": "The Lovers",
        "name_uk": "Закохані",
        "keywords": ["Love", "Choice", "Harmony"],
        "keywords_uk": ["Кохання", "Вибір", "Гармонія"],
        "description": "You are guided by the heart. Relationships and meaningful choices define your path.",
        "description_uk": "Тебе веде серце. Стосунки та значущий вибір визначають твій шлях.",
        "shadow": "Indecision, temptation, conflicting values",
        "shadow_uk": "Нерішучість, спокуса, суперечливі цінності",
    },
    7: {
        "name": "The Chariot",
        "name_uk": "Колісниця",
        "keywords": ["Victory", "Determination", "Control"],
        "keywords_uk": ["Перемога", "Рішучість", "Контроль"],
        "description": "You are a warrior of will. Through focus and determination you overcome all obstacles.",
        "description_uk": "Ти воїн волі. Через фокус і рішучість ти долаєш усі перешкоди.",
        "shadow": "Aggression, lack of direction, overconfidence",
        "shadow_uk": "Агресія, відсутність напряму, самовпевненість",
    },
    8: {
        "name": "Strength",
        "name_uk": "Справедливість (Система 22)",
        "keywords": ["Courage", "Patience", "Inner power"],
        "keywords_uk": ["Закон", "Карма", "Баланс"],
        "description": "True power comes from patience and finding balance.",
        "description_uk": "Енергія карми та закону. Ти маєш здатність бачити об'єктивність і рівновагу в усьому.",
        "shadow": "Self-doubt, suppression, fear of own power",
        "shadow_uk": "Жорсткість, засудження, невміння прощати",
    },
    9: {
        "name": "The Hermit",
        "name_uk": "Відлюдник",
        "keywords": ["Wisdom", "Solitude", "Inner journey"],
        "keywords_uk": ["Мудрість", "Самотність", "Внутрішній шлях"],
        "description": "You are a seeker of deep truth. Your wisdom grows in silence.",
        "description_uk": "Ти шукач глибокої істини. Твоя мудрість зростає в тиші та самотності.",
        "shadow": "Isolation, withdrawal, overthinking",
        "shadow_uk": "Ізоляція, замкнутість, надмірні роздуми",
    },
    10: {
        "name": "Wheel of Fortune",
        "name_uk": "Колесо Фортуни",
        "keywords": ["Cycles", "Destiny", "Opportunity"],
        "keywords_uk": ["Цикли", "Удача", "Потік"],
        "description": "Life moves in cycles and you understand this deeply. Fortune favors you.",
        "description_uk": "Життя рухається циклами, і ти маєш неймовірну удачу, коли довіряєш потоку.",
        "shadow": "Resistance to change, bad luck mentality, passivity",
        "shadow_uk": "Опір змінам, менталітет невезіння, пасивність",
    },
    11: {
        "name": "Justice",
        "name_uk": "Сила (Система 22)",
        "keywords": ["Balance", "Truth", "Karma"],
        "keywords_uk": ["Сила волі", "Могутність", "Перешкоди"],
        "description": "You are guided by truth and fairness.",
        "description_uk": "Ти маєш неймовірний фізичний та енергетичний потенціал, здатність долати будь-які перешкоди.",
        "shadow": "Harsh judgment, rigidity, inability to forgive",
        "shadow_uk": "Агресія, тиск на інших, трудоголізм",
    },
    12: {
        "name": "The Hanged Man",
        "name_uk": "Повішений (Служіння)",
        "keywords": ["Surrender", "New perspective", "Sacrifice"],
        "keywords_uk": ["Служіння", "Інший погляд", "Емпатія"],
        "description": "You see what others cannot. By pausing you gain profound insights.",
        "description_uk": "Ти бачиш те, чого інші не можуть. Твоя ціль — допомагати іншим через емпатію та милосердя.",
        "shadow": "Martyrdom, stagnation, self-sacrifice",
        "shadow_uk": "Синдром жертви, маніпуляція стражданнями, невміння казати 'ні'",
    },
    13: {
        "name": "Death",
        "name_uk": "Трансформація",
        "keywords": ["Transformation", "Endings", "Rebirth"],
        "keywords_uk": ["Трансформація", "Зміни", "Відродження"],
        "description": "You are a transformer. You have the power to release the old.",
        "description_uk": "Ти створений для постійних змін. Де ти — там завжди трансформація і відмирання старого.",
        "shadow": "Fear of change, clinging to the past, stagnation",
        "shadow_uk": "Страх змін, чіплятися за минуле, руйнівна поведінка",
    },
    14: {
        "name": "Temperance",
        "name_uk": "Поміркованість (Душа)",
        "keywords": ["Balance", "Patience", "Alchemy"],
        "keywords_uk": ["Душа", "Гармонія", "Мистецтво"],
        "description": "You are an alchemist of life. You blend opposites into harmony.",
        "description_uk": "Ти тонка, творча душа. Здатний лікувати людей словом та мистецтвом.",
        "shadow": "Imbalance, excess, lack of patience",
        "shadow_uk": "Дисбаланс, залежності, крайнощі",
    },
    15: {
        "name": "The Devil",
        "name_uk": "Диявол (Спокуса)",
        "keywords": ["Shadow self", "Materialism", "Liberation"],
        "keywords_uk": ["Харизма", "Розкіш", "Спокуса"],
        "description": "You have tremendous power locked within your shadow.",
        "description_uk": "Ти бачиш людей наскрізь. Маєш потужну сексуальну і фінансову енергію.",
        "shadow": "Addiction, materialism, self-imprisonment",
        "shadow_uk": "Маніпуляції, залежності, жадоба влади",
    },
    16: {
        "name": "The Tower",
        "name_uk": "Вежа (Духовне пробудження)",
        "keywords": ["Breakthrough", "Revelation", "Change"],
        "keywords_uk": ["Руйнування ілюзій", "Пробудження", "Зміна"],
        "description": "You are built for breakthroughs.",
        "description_uk": "Ти створений для духовного пробудження. Здатен будувати нове на уламках старого.",
        "shadow": "Chaos, sudden loss, resistance to necessary change",
        "shadow_uk": "Агресія, хаос, руйнування свого життя",
    },
    17: {
        "name": "The Star",
        "name_uk": "Зірка",
        "keywords": ["Hope", "Inspiration", "Healing"],
        "keywords_uk": ["Популярність", "Талант", "Надія"],
        "description": "You are a beacon of hope and healing.",
        "description_uk": "Ти маяк надії та популярності. Маєш яскравий талант, який потрібно показувати людям.",
        "shadow": "Disillusionment, disconnection from hope",
        "shadow_uk": "Гординя, синдром самозванця, сіре життя",
    },
    18: {
        "name": "The Moon",
        "name_uk": "Місяць",
        "keywords": ["Intuition", "Dreams", "Subconscious"],
        "keywords_uk": ["Магія", "Матеріалізація", "Інтуїція"],
        "description": "You navigate the world through feeling and intuition.",
        "description_uk": "Ти маєш найсильнішу силу думки. Твої страхи або мрії миттєво стають реальністю.",
        "shadow": "Illusion, anxiety, confusion, fear of the unknown",
        "shadow_uk": "Життя в ілюзіях, страхи, депресії, чорна магія",
    },
    19: {
        "name": "The Sun",
        "name_uk": "Сонце",
        "keywords": ["Joy", "Vitality", "Success"],
        "keywords_uk": ["Сонце", "Багатство", "Успіх"],
        "description": "You radiate warmth, joy, and life-giving energy.",
        "description_uk": "Ти випромінюєш тепло і щастя. Тобі судилося світити великій кількості людей і бути багатим.",
        "shadow": "Ego, arrogance, superficiality",
        "shadow_uk": "Егоцентризм, вигорання, гординя",
    },
    20: {
        "name": "Judgement",
        "name_uk": "Страшний Суд (Рід)",
        "keywords": ["Awakening", "Calling", "Renewal"],
        "keywords_uk": ["Рід", "Яснознання", "Оновлення"],
        "description": "You are here for a higher calling.",
        "description_uk": "Ти маєш сильний зв'язок зі своїми предками. Твоя місія — зцілити свій Рід.",
        "shadow": "Self-doubt about purpose, ignoring the call",
        "shadow_uk": "Конфлікти з сім'єю, судження інших, відсутність коріння",
    },
    21: {
        "name": "The World",
        "name_uk": "Світ",
        "keywords": ["Completion", "Integration", "Mastery"],
        "keywords_uk": ["Миротворець", "Глобальність", "Світ"],
        "description": "You carry the energy of completion and mastery.",
        "description_uk": "Ти людина світу. Твоя місія — мислити глобально, подорожувати і об'єднувати людей.",
        "shadow": "Incompletion, fear of endings, stagnation",
        "shadow_uk": "Закритість від світу, борги, вузьке мислення",
    },
    22: {
        "name": "The Fool",
        "name_uk": "Блазень (Свобода)",
        "keywords": ["New beginnings", "Freedom", "Spontaneity"],
        "keywords_uk": ["Свобода", "Подорожі", "Легкість"],
        "description": "You are the eternal beginner — free, fearless, and full of possibility.",
        "description_uk": "Вища ступінь духовної свободи. Твоє завдання — жити легко, подорожувати і не прив'язуватись до матеріального.",
        "shadow": "Recklessness, naivety, avoidance of responsibility",
        "shadow_uk": "Безвідповідальність, інфантильність, залежності",
    },
}

def get_arcana_info(number: int, language: str = "en") -> dict:
    """Повертає інформацію про аркан за номером"""
    data = ARCANA_DATA.get(number, ARCANA_DATA[1])
    
    if language == "uk":
        return {
            "number": number,
            "name": data["name_uk"],
            "keywords": data["keywords_uk"],
            "description": data["description_uk"],
            "shadow": data["shadow_uk"],
        }
    else:
        return {
            "number": number,
            "name": data["name"],
            "keywords": data["keywords"],
            "description": data["description"],
            "shadow": data["shadow"],
        }


def get_full_destiny_matrix(birth_date: str, language: str = "en") -> dict:
    """
    Готує повний словник з усіма розшифровками для iOS додатку
    """
    matrix = calculate_destiny_matrix(birth_date)
    if not matrix:
        return None

    # Допоміжна функція: замінює числа на повний словник з текстами
    def enrich_block(block):
        enriched = {}
        for k, v in block.items():
            if isinstance(v, int):
                enriched[k] = get_arcana_info(v, language)
            else:
                enriched[k] = v
        return enriched

    # Заповнюємо зони текстами
    zones_with_info = {
        "core": enrich_block(matrix["core"]),
        "money_channel": enrich_block(matrix["money_channel"]),
        "love_channel": enrich_block(matrix["love_channel"]),
        "generational": enrich_block(matrix["generational"]),
        "old_zones": enrich_block(matrix["old_zones"])
    }
    
    # Окремо додаємо Кармічний хвіст з його назвою
    kt_info = enrich_block({
        "bottom": matrix["karmic_tail"]["bottom"],
        "inner": matrix["karmic_tail"]["inner"],
        "middle": matrix["karmic_tail"]["middle"]
    })
    kt_info["combo"] = matrix["karmic_tail"]["combo"]
    kt_info["meaning"] = get_karmic_tail_meaning(kt_info["combo"], language)
    
    zones_with_info["karmic_tail"] = kt_info

    return {
        "birth_date": birth_date,
        "matrix": zones_with_info,
        "language": language
    }


# --- ТЕСТ ---
if __name__ == "__main__":
    import json
    print("🔮 Тестуємо Destiny Matrix 2.0...")
    result = get_full_destiny_matrix("1990-05-20", "uk")

    if result:
        print("\n✅ Успіх! Кармічний хвіст:")
        print(json.dumps(result["matrix"]["karmic_tail"]["meaning"], indent=2, ensure_ascii=False))
        print("\n✅ Грошовий канал (Вхід):")
        print(result["matrix"]["money_channel"]["entrance"]["name"])
    else:
        print("❌ Помилка")