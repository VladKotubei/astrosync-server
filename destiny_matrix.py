# --- AstroSync: Destiny Matrix Module v1.0 ---
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
    
    Args:
        birth_date: "YYYY-MM-DD"
    
    Returns:
        dict з усіма ключовими числами матриці
    """
    try:
        parts = birth_date.split("-")
        day   = int(parts[2])
        month = int(parts[1])
        year  = int(parts[0])

        # --- КЛЮЧОВІ ТОЧКИ МАТРИЦІ ---

        # A = День народження
        A = reduce_to_arcana(day)

        # B = Місяць народження
        B = reduce_to_arcana(month)

        # C = Рік народження (сума всіх цифр)
        C = reduce_to_arcana(sum(int(d) for d in str(year)))

        # D = Сума A+B+C
        D = reduce_to_arcana(A + B + C)

        # --- ЦЕНТР МАТРИЦІ (Особистість) ---
        E = reduce_to_arcana(A + B + C + D)

        # --- ЛІНІЯ ДУШІ ---
        F = reduce_to_arcana(A + B)   # Особистий комфорт
        G = reduce_to_arcana(C + D)   # Соціальний потенціал

        # --- ЛІНІЯ МАТЕРІЇ (земне) ---
        H = reduce_to_arcana(A + D)   # Таланти
        I = reduce_to_arcana(B + C)   # Гроші/матерія

        # --- КАРМА ---
        K = reduce_to_arcana(A + E)   # Карма минулого
        L = reduce_to_arcana(D + E)   # Карма майбутнього

        # --- ЗОНИ ЖИТТЯ ---
        zones = {
            "self":       A,   # Я / Особистість
            "planet":     B,   # Планета / Призначення
            "society":    C,   # Суспільство / Оточення
            "result":     D,   # Результат / Підсумок
            "center":     E,   # Центр матриці — суть людини
            "comfort":    F,   # Особистий комфорт
            "potential":  G,   # Соціальний потенціал
            "talent":     H,   # Природні таланти
            "material":   I,   # Матеріальний світ
            "past_karma": K,   # Карма минулого
            "future_karma": L, # Карма майбутнього
        }

        return {
            "zones": zones,
            "birth_day":   day,
            "birth_month": month,
            "birth_year":  year,
        }

    except Exception as e:
        print(f"❌ Destiny Matrix error: {e}")
        return None


# --- ОПИСИ 22 АРКАНІВ ---
ARCANA_DATA = {
    1: {
        "name": "The Magician",
        "name_uk": "Маг",
        "keywords": ["Leadership", "Willpower", "Initiative"],
        "keywords_uk": ["Лідерство", "Сила волі", "Ініціатива"],
        "description": "You are a natural creator and leader. You have the power to manifest your desires into reality. Your energy is magnetic and your will is strong.",
        "description_uk": "Ти природжений творець і лідер. Маєш силу втілювати бажання в реальність. Твоя енергія магнетична, а воля — непохитна.",
        "shadow": "Manipulation, ego, scattered energy",
        "shadow_uk": "Маніпуляції, его, розпорошена енергія",
    },
    2: {
        "name": "The High Priestess",
        "name_uk": "Верховна Жриця",
        "keywords": ["Intuition", "Wisdom", "Mystery"],
        "keywords_uk": ["Інтуїція", "Мудрість", "Таємниця"],
        "description": "You possess deep intuition and inner knowing. Your wisdom comes from within, and you have a natural connection to hidden truths.",
        "description_uk": "Ти маєш глибоку інтуїцію та внутрішнє знання. Твоя мудрість — з середини, і ти маєш природний зв'язок з прихованими істинами.",
        "shadow": "Secrets, withdrawal, over-dependence on feelings",
        "shadow_uk": "Таємниці, відчуження, надмірна залежність від почуттів",
    },
    3: {
        "name": "The Empress",
        "name_uk": "Імператриця",
        "keywords": ["Creativity", "Abundance", "Nurturing"],
        "keywords_uk": ["Творчість", "Достаток", "Турбота"],
        "description": "You radiate abundance and creative power. You nurture growth in everything around you — people, projects, and ideas bloom in your presence.",
        "description_uk": "Ти випромінюєш достаток і творчу силу. Ти плекаєш зростання у всьому навколо — люди, проекти та ідеї розквітають у твоїй присутності.",
        "shadow": "Over-dependence, possessiveness, creative blocks",
        "shadow_uk": "Залежність, власницькість, творчі блоки",
    },
    4: {
        "name": "The Emperor",
        "name_uk": "Імператор",
        "keywords": ["Structure", "Authority", "Stability"],
        "keywords_uk": ["Структура", "Авторитет", "Стабільність"],
        "description": "You are the builder of foundations. You bring order and structure to chaos, and others naturally look to you for guidance and protection.",
        "description_uk": "Ти будівельник фундаментів. Ти вносиш порядок і структуру в хаос, і інші природно шукають у тебе керівництва та захисту.",
        "shadow": "Rigidity, control, stubbornness",
        "shadow_uk": "Жорсткість, контроль, впертість",
    },
    5: {
        "name": "The Hierophant",
        "name_uk": "Ієрофант",
        "keywords": ["Tradition", "Guidance", "Spiritual teaching"],
        "keywords_uk": ["Традиція", "Наставництво", "Духовне вчення"],
        "description": "You are a keeper of wisdom and tradition. You have a gift for teaching and guiding others along established paths of knowledge.",
        "description_uk": "Ти хранитель мудрості та традицій. Маєш дар навчати і спрямовувати інших шляхами знань.",
        "shadow": "Dogmatism, conformity, over-reliance on rules",
        "shadow_uk": "Догматизм, конформізм, надмірна залежність від правил",
    },
    6: {
        "name": "The Lovers",
        "name_uk": "Закохані",
        "keywords": ["Love", "Choice", "Harmony"],
        "keywords_uk": ["Кохання", "Вибір", "Гармонія"],
        "description": "You are guided by the heart. Relationships and meaningful choices define your path. You seek deep connections and authentic love.",
        "description_uk": "Тебе веде серце. Стосунки та значущий вибір визначають твій шлях. Ти шукаєш глибоких зв'язків і справжнього кохання.",
        "shadow": "Indecision, temptation, conflicting values",
        "shadow_uk": "Нерішучість, спокуса, суперечливі цінності",
    },
    7: {
        "name": "The Chariot",
        "name_uk": "Колісниця",
        "keywords": ["Victory", "Determination", "Control"],
        "keywords_uk": ["Перемога", "Рішучість", "Контроль"],
        "description": "You are a warrior of will. Through focus and determination you overcome all obstacles. Victory is yours when you harness your inner drive.",
        "description_uk": "Ти воїн волі. Через фокус і рішучість ти долаєш усі перешкоди. Перемога твоя, коли ти приборкуєш свій внутрішній рух.",
        "shadow": "Aggression, lack of direction, overconfidence",
        "shadow_uk": "Агресія, відсутність напряму, самовпевненість",
    },
    8: {
        "name": "Strength",
        "name_uk": "Сила",
        "keywords": ["Courage", "Patience", "Inner power"],
        "keywords_uk": ["Мужність", "Терпіння", "Внутрішня сила"],
        "description": "Your greatest strength lies within. You tame your own wild nature with grace and compassion. True power comes from patience, not force.",
        "description_uk": "Твоя найбільша сила — всередині. Ти приборкуєш свою власну дику природу з витонченістю і співчуттям. Справжня сила — з терпіння, не з примусу.",
        "shadow": "Self-doubt, suppression, fear of own power",
        "shadow_uk": "Невпевненість у собі, придушення, страх власної сили",
    },
    9: {
        "name": "The Hermit",
        "name_uk": "Відлюдник",
        "keywords": ["Wisdom", "Solitude", "Inner journey"],
        "keywords_uk": ["Мудрість", "Самотність", "Внутрішній шлях"],
        "description": "You are a seeker of deep truth. Your wisdom grows in silence and solitude. You are a lantern-bearer — your insights light the way for others.",
        "description_uk": "Ти шукач глибокої істини. Твоя мудрість зростає в тиші та самотності. Ти носій ліхтаря — твої прозріння освітлюють шлях для інших.",
        "shadow": "Isolation, withdrawal, overthinking",
        "shadow_uk": "Ізоляція, замкнутість, надмірні роздуми",
    },
    10: {
        "name": "Wheel of Fortune",
        "name_uk": "Колесо Фортуни",
        "keywords": ["Cycles", "Destiny", "Opportunity"],
        "keywords_uk": ["Цикли", "Доля", "Можливість"],
        "description": "Life moves in cycles and you understand this deeply. Fortune favors you when you align with the natural flow of change and opportunity.",
        "description_uk": "Життя рухається циклами, і ти глибоко це розумієш. Фортуна сприяє тобі, коли ти узгоджуєшся з природним потоком змін і можливостей.",
        "shadow": "Resistance to change, bad luck mentality, passivity",
        "shadow_uk": "Опір змінам, менталітет невезіння, пасивність",
    },
    11: {
        "name": "Justice",
        "name_uk": "Справедливість",
        "keywords": ["Balance", "Truth", "Karma"],
        "keywords_uk": ["Баланс", "Правда", "Карма"],
        "description": "You are guided by truth and fairness. You have a sharp sense of justice and the ability to see all sides of a situation with clarity.",
        "description_uk": "Тебе спрямовує правда і справедливість. Ти маєш гостре відчуття справедливості і здатність бачити всі сторони ситуації з ясністю.",
        "shadow": "Harsh judgment, rigidity, inability to forgive",
        "shadow_uk": "Жорсткий осуд, негнучкість, невміння прощати",
    },
    12: {
        "name": "The Hanged Man",
        "name_uk": "Повішений",
        "keywords": ["Surrender", "New perspective", "Sacrifice"],
        "keywords_uk": ["Відпускання", "Нова перспектива", "Жертва"],
        "description": "You see what others cannot. By pausing and surrendering control, you gain profound insights. Your greatest breakthroughs come through letting go.",
        "description_uk": "Ти бачиш те, чого інші не можуть. Зупиняючись і відпускаючи контроль, ти отримуєш глибокі прозріння. Твої найбільші прориви — через відпускання.",
        "shadow": "Martyrdom, stagnation, self-sacrifice",
        "shadow_uk": "Мартирство, стагнація, самопожертва",
    },
    13: {
        "name": "Death",
        "name_uk": "Смерть",
        "keywords": ["Transformation", "Endings", "Rebirth"],
        "keywords_uk": ["Трансформація", "Завершення", "Відродження"],
        "description": "You are a transformer. You have the power to release the old and embrace radical change. Every ending you experience leads to powerful rebirth.",
        "description_uk": "Ти трансформатор. Маєш силу відпускати старе і приймати радикальні зміни. Кожне завершення, яке ти переживаєш, веде до потужного відродження.",
        "shadow": "Fear of change, clinging to the past, stagnation",
        "shadow_uk": "Страх змін, чіплятися за минуле, стагнація",
    },
    14: {
        "name": "Temperance",
        "name_uk": "Поміркованість",
        "keywords": ["Balance", "Patience", "Alchemy"],
        "keywords_uk": ["Баланс", "Терпіння", "Алхімія"],
        "description": "You are an alchemist of life. You blend opposites into harmony and find the middle path. Your patience and moderation create lasting magic.",
        "description_uk": "Ти алхімік життя. Змішуєш протилежності в гармонію і знаходиш середній шлях. Твоє терпіння і поміркованість творять тривалу магію.",
        "shadow": "Imbalance, excess, lack of patience",
        "shadow_uk": "Дисбаланс, надмірність, відсутність терпіння",
    },
    15: {
        "name": "The Devil",
        "name_uk": "Диявол",
        "keywords": ["Shadow self", "Materialism", "Liberation"],
        "keywords_uk": ["Тінь", "Матеріалізм", "Звільнення"],
        "description": "You have tremendous power locked within your shadow. By facing your deepest fears and desires, you unlock extraordinary freedom and strength.",
        "description_uk": "У твоїй тіні замкнена величезна сила. Зіткнувшись зі своїми найглибшими страхами і бажаннями, ти відкриваєш надзвичайну свободу і силу.",
        "shadow": "Addiction, materialism, self-imprisonment",
        "shadow_uk": "Залежність, матеріалізм, самоув'язнення",
    },
    16: {
        "name": "The Tower",
        "name_uk": "Вежа",
        "keywords": ["Breakthrough", "Revelation", "Change"],
        "keywords_uk": ["Прорив", "Одкровення", "Зміна"],
        "description": "You are built for breakthroughs. The structures in your life that no longer serve you will fall to reveal something truer and stronger beneath.",
        "description_uk": "Ти створений для проривів. Структури у твоєму житті, які вже не служать тобі, впадуть, щоб відкрити щось більш справжнє і міцне під ними.",
        "shadow": "Chaos, sudden loss, resistance to necessary change",
        "shadow_uk": "Хаос, раптова втрата, опір необхідним змінам",
    },
    17: {
        "name": "The Star",
        "name_uk": "Зірка",
        "keywords": ["Hope", "Inspiration", "Healing"],
        "keywords_uk": ["Надія", "Натхнення", "Зцілення"],
        "description": "You are a beacon of hope and healing. Your presence inspires others and your optimism attracts miracles. You are here to shine and uplift.",
        "description_uk": "Ти маяк надії та зцілення. Твоя присутність надихає інших, а твій оптимізм притягує дива. Ти тут, щоб сяяти і піднімати.",
        "shadow": "Disillusionment, disconnection from hope",
        "shadow_uk": "Розчарування, відрив від надії",
    },
    18: {
        "name": "The Moon",
        "name_uk": "Місяць",
        "keywords": ["Intuition", "Dreams", "Subconscious"],
        "keywords_uk": ["Інтуїція", "Мрії", "Підсвідомість"],
        "description": "You navigate the world through feeling and intuition. Your dreams carry important messages. Trust the whispers of your subconscious — they guide you true.",
        "description_uk": "Ти орієнтуєшся у світі через відчуття та інтуїцію. Твої сни несуть важливі послання. Довіряй шепоту свого підсвідомого — він веде тебе вірно.",
        "shadow": "Illusion, anxiety, confusion, fear of the unknown",
        "shadow_uk": "Ілюзія, тривога, заплутаність, страх невідомого",
    },
    19: {
        "name": "The Sun",
        "name_uk": "Сонце",
        "keywords": ["Joy", "Vitality", "Success"],
        "keywords_uk": ["Радість", "Життєвість", "Успіх"],
        "description": "You radiate warmth, joy, and life-giving energy. Success comes naturally to you when you express your authentic self fully and without fear.",
        "description_uk": "Ти випромінюєш тепло, радість і животворну енергію. Успіх приходить до тебе природно, коли ти повністю і без страху виражаєш своє справжнє я.",
        "shadow": "Ego, arrogance, superficiality",
        "shadow_uk": "Его, зарозумілість, поверховість",
    },
    20: {
        "name": "Judgement",
        "name_uk": "Суд",
        "keywords": ["Awakening", "Calling", "Renewal"],
        "keywords_uk": ["Пробудження", "Покликання", "Оновлення"],
        "description": "You are here for a higher calling. A powerful awakening is part of your path — a moment when everything changes and your true purpose becomes clear.",
        "description_uk": "Ти тут для вищого покликання. Потужне пробудження — частина твого шляху — момент, коли все змінюється і твоя справжня мета стає ясною.",
        "shadow": "Self-doubt about purpose, ignoring the call",
        "shadow_uk": "Сумніви щодо мети, ігнорування покликання",
    },
    21: {
        "name": "The World",
        "name_uk": "Світ",
        "keywords": ["Completion", "Integration", "Mastery"],
        "keywords_uk": ["Завершення", "Інтеграція", "Майстерність"],
        "description": "You carry the energy of completion and mastery. You have come to integrate all of life's lessons into wisdom. The whole world is your canvas.",
        "description_uk": "Ти несеш енергію завершення і майстерності. Ти прийшов інтегрувати всі уроки життя в мудрість. Весь світ — твоє полотно.",
        "shadow": "Incompletion, fear of endings, stagnation",
        "shadow_uk": "Незавершеність, страх кінців, стагнація",
    },
    22: {
        "name": "The Fool",
        "name_uk": "Блазень",
        "keywords": ["New beginnings", "Freedom", "Spontaneity"],
        "keywords_uk": ["Нові початки", "Свобода", "Спонтанність"],
        "description": "You are the eternal beginner — free, fearless, and full of possibility. Your greatest gift is the courage to leap into the unknown with an open heart.",
        "description_uk": "Ти вічний початківець — вільний, безстрашний і повний можливостей. Твій найбільший дар — сміливість стрибнути в невідоме з відкритим серцем.",
        "shadow": "Recklessness, naivety, avoidance of responsibility",
        "shadow_uk": "Необережність, наївність, уникнення відповідальності",
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
    Повний розрахунок матриці долі з описами арканів
    """
    matrix = calculate_destiny_matrix(birth_date)
    if not matrix:
        return None

    zones_with_info = {}
    for zone_key, arcana_number in matrix["zones"].items():
        zones_with_info[zone_key] = {
            "arcana_number": arcana_number,
            "arcana_info": get_arcana_info(arcana_number, language)
        }

    return {
        "birth_date": birth_date,
        "zones": zones_with_info,
        "language": language
    }


# --- ТЕСТ ---
if __name__ == "__main__":
    print("🔮 Тестуємо Destiny Matrix...")
    result = get_full_destiny_matrix("1990-05-20", "en")

    if result:
        print("\n✅ Матриця розрахована!")
        for zone, data in result["zones"].items():
            info = data["arcana_info"]
            print(f"  {zone:15} → Аркан {data['arcana_number']:2}: {info['name']}")
    else:
        print("❌ Помилка")