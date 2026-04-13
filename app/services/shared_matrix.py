from functools import reduce as _reduce

from app.services.destiny_matrix import calculate_destiny_matrix, reduce_to_arcana


def calculate_shared_matrix(birth_date_a: str, birth_date_b: str) -> dict:
    matrix_a = calculate_destiny_matrix(birth_date_a)
    matrix_b = calculate_destiny_matrix(birth_date_b)

    if matrix_a is None or matrix_b is None:
        raise ValueError("Invalid birth date")

    love = reduce_to_arcana(matrix_a["core"]["center"] + matrix_b["core"]["center"])
    finance = reduce_to_arcana(matrix_a["money_channel"]["profession"] + matrix_b["money_channel"]["profession"])
    communication = reduce_to_arcana(matrix_a["core"]["day"] + matrix_b["core"]["day"])
    growth = reduce_to_arcana(matrix_a["core"]["month"] + matrix_b["core"]["month"])
    challenge = reduce_to_arcana(matrix_a["core"]["year"] + matrix_b["core"]["year"])
    mission = reduce_to_arcana(matrix_a["core"]["bottom"] + matrix_b["core"]["bottom"])
    karma = reduce_to_arcana(matrix_a["karmic_tail"]["middle"] + matrix_b["karmic_tail"]["middle"])

    return {
        "person_a": birth_date_a,
        "person_b": birth_date_b,
        "zones": {
            "love": {"arcana": love, "name": "Love & Romance"},
            "finance": {"arcana": finance, "name": "Money & Prosperity"},
            "communication": {"arcana": communication, "name": "Communication"},
            "growth": {"arcana": growth, "name": "Spiritual Growth"},
            "challenge": {"arcana": challenge, "name": "Main Challenge"},
            "mission": {"arcana": mission, "name": "Shared Mission"},
            "karma": {"arcana": karma, "name": "Karmic Bond"},
        },
        "total_compatibility": reduce_to_arcana(
            love + finance + communication + growth + challenge + mission + karma
        ),
    }
