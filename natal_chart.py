# --- AstroSync: Natal Chart Module v2.0 ---
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const

def calculate_natal_chart(birth_date, birth_time, latitude, longitude):
    """
    Розраховує натальну карту
    
    Args:
        birth_date: "YYYY-MM-DD"
        birth_time: "HH:MM"
        latitude: float
        longitude: float
    
    Returns:
        dict або None
    """
    try:
        print(f"📊 Calculating natal chart...")
        print(f"   Date: {birth_date} {birth_time}")
        print(f"   Location: {latitude}, {longitude}")
        
        # Форматуємо дату
        date_formatted = birth_date.replace("-", "/")
        
        # Створюємо карту
        date = Datetime(date_formatted, birth_time, '+00:00')
        pos = GeoPos(latitude, longitude)
        chart = Chart(date, pos)
        
        # Асцендент та MC
        asc = chart.get(const.ASC)
        mc = chart.get(const.MC)
        
        # Планети (тільки основні що точно працюють)
        planets_data = {}
        
        # Сонце
        sun = chart.get(const.SUN)
        planets_data["Sun"] = {
            "sign": sun.sign,
            "degree": round(sun.signlon, 2),
            "house": get_house_for_planet(chart, sun.lon),
            "longitude": round(sun.lon, 2)
        }
        
        # Місяць
        moon = chart.get(const.MOON)
        planets_data["Moon"] = {
            "sign": moon.sign,
            "degree": round(moon.signlon, 2),
            "house": get_house_for_planet(chart, moon.lon),
            "longitude": round(moon.lon, 2)
        }
        
        # Меркурій
        mercury = chart.get(const.MERCURY)
        planets_data["Mercury"] = {
            "sign": mercury.sign,
            "degree": round(mercury.signlon, 2),
            "house": get_house_for_planet(chart, mercury.lon),
            "longitude": round(mercury.lon, 2)
        }
        
        # Венера
        venus = chart.get(const.VENUS)
        planets_data["Venus"] = {
            "sign": venus.sign,
            "degree": round(venus.signlon, 2),
            "house": get_house_for_planet(chart, venus.lon),
            "longitude": round(venus.lon, 2)
        }
        
        # Марс
        mars = chart.get(const.MARS)
        planets_data["Mars"] = {
            "sign": mars.sign,
            "degree": round(mars.signlon, 2),
            "house": get_house_for_planet(chart, mars.lon),
            "longitude": round(mars.lon, 2)
        }
        
        # Юпітер
        jupiter = chart.get(const.JUPITER)
        planets_data["Jupiter"] = {
            "sign": jupiter.sign,
            "degree": round(jupiter.signlon, 2),
            "house": get_house_for_planet(chart, jupiter.lon),
            "longitude": round(jupiter.lon, 2)
        }
        
        # Сатурн
        saturn = chart.get(const.SATURN)
        planets_data["Saturn"] = {
            "sign": saturn.sign,
            "degree": round(saturn.signlon, 2),
            "house": get_house_for_planet(chart, saturn.lon),
            "longitude": round(saturn.lon, 2)
        }
        
        # Дома
        houses_data = {}
        house_cusps = [const.HOUSE1, const.HOUSE2, const.HOUSE3, const.HOUSE4,
                       const.HOUSE5, const.HOUSE6, const.HOUSE7, const.HOUSE8,
                       const.HOUSE9, const.HOUSE10, const.HOUSE11, const.HOUSE12]
        
        for i, house_id in enumerate(house_cusps, start=1):
            house = chart.get(house_id)
            houses_data[f"House_{i}"] = {
                "sign": house.sign,
                "degree": round(house.lon, 2)
            }
        
        result = {
            "ascendant": {
                "sign": asc.sign,
                "degree": round(asc.lon, 2)
            },
            "mc": {
                "sign": mc.sign,
                "degree": round(mc.lon, 2)
            },
            "planets": planets_data,
            "houses": houses_data,
            "chart_type": "natal"
        }
        
        print(f"✅ Chart calculated successfully!")
        print(f"   Ascendant: {asc.sign}")
        print(f"   Planets: {len(planets_data)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_house_for_planet(chart, planet_lon):
    """
    Визначає в якому домі знаходиться планета за її довготою
    """
    try:
        house_cusps = [const.HOUSE1, const.HOUSE2, const.HOUSE3, const.HOUSE4,
                       const.HOUSE5, const.HOUSE6, const.HOUSE7, const.HOUSE8,
                       const.HOUSE9, const.HOUSE10, const.HOUSE11, const.HOUSE12]
        
        houses = []
        for house_id in house_cusps:
            house = chart.get(house_id)
            houses.append(house.lon)
        
        # Визначаємо в якому домі
        for i in range(12):
            current = houses[i]
            next_h = houses[(i + 1) % 12]
            
            if next_h < current:  # Перехід через 0°
                if planet_lon >= current or planet_lon < next_h:
                    return f"House_{i + 1}"
            else:
                if current <= planet_lon < next_h:
                    return f"House_{i + 1}"
        
        return "House_1"  # За замовчуванням
        
    except:
        return "Unknown"


def get_planet_meaning(planet, sign, house, language="en"):
    """
    Трактування планети в знаку та домі
    """
    meanings = {
        "en": {
            "Sun": f"Your identity shines through {sign} in {house}. This is your core essence and life purpose.",
            "Moon": f"Your emotions flow in {sign}, {house}. This shapes your instincts and inner world.",
            "Mercury": f"Your mind operates in {sign}, {house}. This influences communication and thinking.",
            "Venus": f"Your heart lives in {sign}, {house}. This colors your approach to love and beauty.",
            "Mars": f"Your drive burns in {sign}, {house}. This fuels your actions and desires.",
            "Jupiter": f"Your growth expands in {sign}, {house}. This brings opportunities and wisdom.",
            "Saturn": f"Your lessons teach in {sign}, {house}. This builds discipline and structure."
        },
        "uk": {
            "Sun": f"Ваша ідентичність сяє через {sign} в {house}. Це ваша суть та життєва мета.",
            "Moon": f"Ваші емоції течуть в {sign}, {house}. Це формує ваші інстинкти та внутрішній світ.",
            "Mercury": f"Ваш розум працює в {sign}, {house}. Це впливає на комунікацію та мислення.",
            "Venus": f"Ваше серце живе в {sign}, {house}. Це забарвлює ваш підхід до кохання та краси.",
            "Mars": f"Ваш драйв горить в {sign}, {house}. Це живить ваші дії та бажання.",
            "Jupiter": f"Ваше зростання розширюється в {sign}, {house}. Це приносить можливості та мудрість.",
            "Saturn": f"Ваші уроки навчають в {sign}, {house}. Це будує дисципліну та структуру."
        }
    }
    
    return meanings.get(language, meanings["en"]).get(planet, f"{planet} in {sign}, {house}")


# --- ТЕСТ ---
if __name__ == "__main__":
    print("🔮 Testing natal chart...")
    result = calculate_natal_chart("1990-05-20", "14:30", 50.45, 30.52)
    
    if result:
        print("\n✅ SUCCESS!")
        print(f"Ascendant: {result['ascendant']['sign']}")
        print(f"MC: {result['mc']['sign']}")
        print(f"\nPlanets:")
        for planet, data in result['planets'].items():
            print(f"  {planet}: {data['sign']} in {data['house']}")
    else:
        print("\n❌ FAILED")