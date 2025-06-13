import random

# Таблица базовых хитов по классу на 1 уровне
HIT_DICE_BY_CLASS = {
    "Barbarian": 12,
    "Fighter": 10,
    "Paladin": 10,
    "Ranger": 10,
    "Cleric": 8,
    "Druid": 8,
    "Bard": 8,
    "Monk": 8,
    "Rogue": 8,
    "Artificer": 8,
    "Wizard": 6,
    "Sorcerer": 6,
    "Warlock": 8
}


def get_modifier(stat_value: int) -> int:
    return (stat_value - 10) // 2


def calculate_starting_hp(char_class: str, con_score: int) -> int:
    hit_die = HIT_DICE_BY_CLASS.get(char_class)
    if hit_die is None:
        raise ValueError(f"Неизвестный класс: {char_class}")

    return hit_die + get_modifier(con_score)

def roll_hit_points(class_name: str, con_score: int) -> int:
    """Бросает кубик хита + модификатор телосложения, минимум 1."""
    hit_die = HIT_DICE_BY_CLASS.get(class_name)
    if not hit_die:
        raise ValueError(f"Неизвестный класс: {class_name}")
    roll = random.randint(1, hit_die)
    total = max(1, roll + get_modifier(con_score))
    return total