# --- AstroSync: Angel Numbers Engine ---

def calculate_angel_number(birth_date: str):
    """
    Математично перетворює дату народження на Число Ангела.
    """
    # 1. Прибираємо всі зайві символи з дати (залишаємо тільки цифри)
    clean_date = birth_date.replace("-", "").replace(".", "").replace("/", "")
    
    # 2. Додаємо всі цифри разом
    total = sum(int(digit) for digit in clean_date)
    
    # 3. Зводимо до однієї цифри (від 1 до 9)
    while total > 9:
        total = sum(int(digit) for digit in str(total))
        
    # 4. Формуємо число ангела (наприклад, якщо сума 1 -> вийде "111")
    angel_number = f"{total}{total}{total}"
    
    return {
        "angel_number": angel_number,
        "base_digit": total
    }