# --- AstroSync: Core Engine v1.0 ---
# Тут ми імпортуємо (підключаємо) ваші попередні файли як модулі
from numerology import calculate_life_path
from astro_basic import get_zodiac_sign

def generate_full_profile(name, birthdate):
    print(f"\n🚀 Аналіз профілю для: {name.upper()}")
    print("-" * 40)
    
    # 1. Викликаємо Нумерологію
    life_path = calculate_life_path(birthdate)
    print(f"🔢 Число Життєвого Шляху: {life_path}")
    
    # 2. Викликаємо Астрологію
    # (замінюємо тире на слеші, бо flatlib вередлива до формату)
    formatted_date = birthdate.replace("-", "/")
    zodiac = get_zodiac_sign(formatted_date)
    print(f"🌞 Знак Зодіаку: {zodiac}")
    
    print("-" * 40)
    
    # 3. ЕЛЕМЕНТАРНИЙ СИНТЕЗ (Tier 1 Logic)
    # Давайте спробуємо дати першу "розумну" пораду на основі поєднання даних
    
    print("💡 Перший висновок системи:")
    
    if life_path in [1, 5, 8] and zodiac in ['Aries', 'Leo', 'Sagittarius']:
        print(">> Вибухова енергія! Ви природжений лідер з вогняним темпераментом.")
        print(">> Порада: Вчіться делегувати, інакше вигорите.")
        
    elif life_path in [2, 6, 9] and zodiac in ['Cancer', 'Scorpio', 'Pisces']:
        print(">> Глибока емпатія. Ви відчуваєте людей краще, ніж вони самі.")
        print(">> Порада: Ставте кордони, щоб не переймати чужий негатив.")
        
    elif life_path in [4, 7] and zodiac in ['Taurus', 'Virgo', 'Capricorn']:
        print(">> Майстер структури. Ви бачите деталі, які інші пропускають.")
        print(">> Порада: Не бійтеся ризикувати, у вас міцний фундамент.")
        
    elif life_path == 3 and zodiac in ['Gemini', 'Libra', 'Aquarius']:
        print(">> Геній комунікації. Ваші ідеї можуть змінити світ.")
        print(">> Порада: Фокусуйтеся на одній справі за раз.")
        
    else:
        print(">> У вас рідкісне поєднання енергій. Ви — міст між логікою та інтуїцією.")
        print(">> Порада: Шукайте нестандартні рішення.")

# --- Блок запуску ---
if __name__ == "__main__":
    print("🤖 AstroSync System Online")
    
    u_name = input("Введіть ім'я: ")
    u_date = input("Введіть дату (РРРР-ММ-ДД): ")
    
    try:
        generate_full_profile(u_name, u_date)
    except Exception as e:
        print(f"Помилка: {e}")