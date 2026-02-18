# --- AstroSync: Compatibility Module v1.0 ---
from natal_chart import calculate_natal_chart

def calculate_compatibility(person1_data, person2_data):
    """
    Розраховує сумісність між двома людьми
    
    Args:
        person1_data: dict з ключами: name, birth_date, birth_time, latitude, longitude
        person2_data: dict з ключами: name, birth_date, birth_time, latitude, longitude
    
    Returns:
        dict: результати сумісності
    """
    try:
        print(f"💕 Calculating compatibility between {person1_data['name']} and {person2_data['name']}")
        
        # Розраховуємо обидві натальні карти
        chart1 = calculate_natal_chart(
            person1_data['birth_date'],
            person1_data['birth_time'],
            person1_data['latitude'],
            person1_data['longitude']
        )
        
        chart2 = calculate_natal_chart(
            person2_data['birth_date'],
            person2_data['birth_time'],
            person2_data['latitude'],
            person2_data['longitude']
        )
        
        if not chart1 or not chart2:
            return None
        
        # Розраховуємо сумісність
        scores = calculate_synastry_scores(chart1, chart2)
        
        # Генеруємо аналіз
        analysis = generate_compatibility_analysis(
            chart1, 
            chart2, 
            scores,
            person1_data['name'],
            person2_data['name']
        )
        
        return {
            "person1": {
                "name": person1_data['name'],
                "sun_sign": chart1['planets']['Sun']['sign'],
                "moon_sign": chart1['planets']['Moon']['sign'],
                "ascendant": chart1['ascendant']['sign']
            },
            "person2": {
                "name": person2_data['name'],
                "sun_sign": chart2['planets']['Sun']['sign'],
                "moon_sign": chart2['planets']['Moon']['sign'],
                "ascendant": chart2['ascendant']['sign']
            },
            "compatibility_score": scores['total'],
            "category_scores": scores['categories'],
            "strengths": analysis['strengths'],
            "challenges": analysis['challenges'],
            "advice": analysis['advice']
        }
        
    except Exception as e:
        print(f"❌ Error calculating compatibility: {e}")
        import traceback
        traceback.print_exc()
        return None


def calculate_synastry_scores(chart1, chart2):
    """
    Розраховує бали сумісності за категоріями
    """
    scores = {
        'romantic': 0,      # Романтика (Sun, Venus, Mars)
        'emotional': 0,     # Емоційна (Moon)
        'mental': 0,        # Ментальна (Mercury)
        'spiritual': 0,     # Духовна (Jupiter)
        'practical': 0      # Практична (Saturn)
    }
    
    # 1. Романтична сумісність (Sun + Venus + Mars)
    sun_compat = compare_signs(
        chart1['planets']['Sun']['sign'],
        chart2['planets']['Sun']['sign']
    )
    venus_compat = compare_signs(
        chart1['planets']['Venus']['sign'],
        chart2['planets']['Venus']['sign']
    )
    mars_compat = compare_signs(
        chart1['planets']['Mars']['sign'],
        chart2['planets']['Mars']['sign']
    )
    scores['romantic'] = (sun_compat + venus_compat + mars_compat) / 3
    
    # 2. Емоційна сумісність (Moon)
    moon_compat = compare_signs(
        chart1['planets']['Moon']['sign'],
        chart2['planets']['Moon']['sign']
    )
    scores['emotional'] = moon_compat
    
    # 3. Ментальна сумісність (Mercury)
    mercury_compat = compare_signs(
        chart1['planets']['Mercury']['sign'],
        chart2['planets']['Mercury']['sign']
    )
    scores['mental'] = mercury_compat
    
    # 4. Духовна сумісність (Jupiter)
    jupiter_compat = compare_signs(
        chart1['planets']['Jupiter']['sign'],
        chart2['planets']['Jupiter']['sign']
    )
    scores['spiritual'] = jupiter_compat
    
    # 5. Практична сумісність (Saturn)
    saturn_compat = compare_signs(
        chart1['planets']['Saturn']['sign'],
        chart2['planets']['Saturn']['sign']
    )
    scores['practical'] = saturn_compat
    
    # Загальний бал (зважений)
    total = (
        scores['romantic'] * 0.30 +      # 30% - романтика
        scores['emotional'] * 0.25 +     # 25% - емоції
        scores['mental'] * 0.20 +        # 20% - розум
        scores['spiritual'] * 0.15 +     # 15% - духовність
        scores['practical'] * 0.10       # 10% - практичність
    )
    
    return {
        'total': round(total, 1),
        'categories': {k: round(v, 1) for k, v in scores.items()}
    }


def compare_signs(sign1, sign2):
    """
    Порівнює два знаки зодіаку і повертає бал від 0 до 100
    
    Логіка:
    - Той самий знак: 100
    - Той самий елемент (Fire, Earth, Air, Water): 80
    - Сумісні елементи (Fire-Air, Earth-Water): 70
    - Тригон (120°): 85
    - Секстиль (60°): 75
    - Квадрат (90°): 50
    - Опозиція (180°): 60
    - Інше: 40
    """
    if sign1 == sign2:
        return 100
    
    # Елементи знаків
    elements = {
        'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
        'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
        'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
        'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water'
    }
    
    elem1 = elements.get(sign1)
    elem2 = elements.get(sign2)
    
    # Той самий елемент
    if elem1 == elem2:
        return 80
    
    # Сумісні елементи
    compatible_pairs = [
        ('Fire', 'Air'),
        ('Air', 'Fire'),
        ('Earth', 'Water'),
        ('Water', 'Earth')
    ]
    
    if (elem1, elem2) in compatible_pairs:
        return 70
    
    # Тригон (120°) - знаки одного елемента
    trine_groups = [
        ['Aries', 'Leo', 'Sagittarius'],
        ['Taurus', 'Virgo', 'Capricorn'],
        ['Gemini', 'Libra', 'Aquarius'],
        ['Cancer', 'Scorpio', 'Pisces']
    ]
    
    for group in trine_groups:
        if sign1 in group and sign2 in group:
            return 85
    
    # Опозиція (180°)
    oppositions = [
        ('Aries', 'Libra'), ('Taurus', 'Scorpio'), ('Gemini', 'Sagittarius'),
        ('Cancer', 'Capricorn'), ('Leo', 'Aquarius'), ('Virgo', 'Pisces')
    ]
    
    if (sign1, sign2) in oppositions or (sign2, sign1) in oppositions:
        return 60
    
    return 50  # За замовчуванням


def generate_compatibility_analysis(chart1, chart2, scores, name1, name2):
    """
    Генерує текстовий аналіз сумісності
    """
    total_score = scores['total']
    
    strengths = []
    challenges = []
    
    # Аналіз за категоріями
    if scores['categories']['romantic'] >= 70:
        strengths.append(f"Strong romantic chemistry between {name1} and {name2}")
    elif scores['categories']['romantic'] < 50:
        challenges.append(f"Different approaches to romance and self-expression")
    
    if scores['categories']['emotional'] >= 70:
        strengths.append(f"Deep emotional understanding and connection")
    elif scores['categories']['emotional'] < 50:
        challenges.append(f"Different emotional needs and expressions")
    
    if scores['categories']['mental'] >= 70:
        strengths.append(f"Excellent mental connection and communication")
    elif scores['categories']['mental'] < 50:
        challenges.append(f"Different communication styles")
    
    # Загальна порада
    if total_score >= 80:
        advice = "This is an excellent match with strong potential for a harmonious relationship. Your energies complement each other beautifully."
    elif total_score >= 60:
        advice = "A good match with solid compatibility. With effort and understanding, this relationship can thrive."
    elif total_score >= 40:
        advice = "Moderate compatibility. This relationship will require work and compromise, but growth is possible."
    else:
        advice = "Challenging compatibility. This relationship will need significant effort and mutual understanding."
    
    return {
        'strengths': strengths if strengths else ["You can learn from each other's differences"],
        'challenges': challenges if challenges else ["Minor differences in approach"],
        'advice': advice
    }


# --- ТЕСТ ---
if __name__ == "__main__":
    print("💕 Testing compatibility...")
    
    person1 = {
        "name": "Alex",
        "birth_date": "1990-05-20",
        "birth_time": "14:30",
        "latitude": 50.45,
        "longitude": 30.52
    }
    
    person2 = {
        "name": "Jordan",
        "birth_date": "1992-08-15",
        "birth_time": "10:00",
        "latitude": 40.71,
        "longitude": -74.00
    }
    
    result = calculate_compatibility(person1, person2)
    
    if result:
        print(f"\n✅ Compatibility: {result['compatibility_score']}%")
        print(f"Strengths: {result['strengths']}")
        print(f"Challenges: {result['challenges']}")
    else:
        print("\n❌ Failed")