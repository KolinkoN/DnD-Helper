import disnake
from disnake.ui import View, Button, Select
import random
import json
import sqlite3

MAGIC_CLASSES = {
    "Wizard", "Sorcerer", "Cleric", "Druid", "Warlock", "Bard", "Paladin", "Ranger", "Artificer"
}

with open("spells.json", "r", encoding="utf-8") as f:
    SPELLS = json.load(f)

def get_modifier(stat_value: int) -> int:
    return (stat_value - 10) // 2

def get_spells_for_class(class_name, level):
    return [
        name for name, data in SPELLS.items()
        if class_name in data.get("classes", []) and data["level"] <= level
    ]

def update_character_level_and_hp(user_id: int, new_level: int, new_hp: int):
    conn = sqlite3.connect("characters.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE characters SET level = ?, hp = ? WHERE user_id = ?",
        (new_level, new_hp, user_id)
    )
    conn.commit()
    conn.close()

def perform_level_up(cursor, character_name: str):
    character = cursor.execute(
        "SELECT level, hp, constitution, char_class, user_id FROM characters WHERE name = ?",
        (character_name,)
    ).fetchone()

    if not character:
        return None, "❌ Персонаж не найден."

    current_level, current_hp, con_stat, char_class, user_id = character

    if current_level >= 20:
        return None, f"❌ `{character_name}` уже достиг максимального уровня (20)."

    new_level = current_level + 1

    HIT_DICE = {
        "barbarian": 12, "fighter": 10, "paladin": 10, "ranger": 10,
        "cleric": 8, "druid": 8, "bard": 8, "monk": 8,
        "rogue": 8, "artificer": 8, "wizard": 6, "sorcerer": 6, "warlock": 8
    }

    hit_die = HIT_DICE.get(char_class.lower())
    if hit_die is None:
        return None, f"⚠️ Неизвестный класс `{char_class}`."

    con_mod = get_modifier(con_stat)
    roll = random.randint(1, hit_die)
    hp_gain = max(1, roll + con_mod)
    new_hp = current_hp + hp_gain

    cursor.execute(
        "UPDATE characters SET level = ?, hp = ? WHERE name = ?",
        (new_level, new_hp, character_name)
    )

    return {
        "new_level": new_level,
        "hp_gain": hp_gain,
        "roll": roll,
        "con_mod": con_mod,
        "new_hp": new_hp,
        "char_class": char_class,
        "user_id": user_id
    }, None

def setup_spell_leveling(bot, conn, cursor):
    class SpellSelectView(View):
        def __init__(self, inter, user_id, spell_options, max_select):
            super().__init__(timeout=120)
            self.inter = inter
            self.user_id = user_id
            self.selected_spells = []
            self.max_select = max_select

            options = [
                disnake.SelectOption(label=name[:100], value=name[:100])
                for name in spell_options
            ]

            self.select = Select(
                placeholder=f"Выберите до {max_select} заклинаний",
                options=options[:25],  # Discord лимит
                min_values=1,
                max_values=max_select
            )
            self.select.callback = self.select_callback
            self.add_item(self.select)

        async def select_callback(self, inter: disnake.MessageInteraction):
            if inter.user.id != self.user_id:
                await inter.response.send_message("Это не для вас!", ephemeral=True)
                return

            self.selected_spells = self.select.values

            # Удалим старые записи
            cursor.execute("DELETE FROM character_spells WHERE user_id = ?", (self.user_id,))
            # Вставим новые
            cursor.executemany(
                "INSERT INTO character_spells (user_id, spell_name) VALUES (?, ?)",
                [(self.user_id, spell) for spell in self.selected_spells]
            )
            conn.commit()

            await inter.response.edit_message(
                content=f"🎓 Вы выбрали: {', '.join(self.selected_spells)}",
                view=None
            )
            self.stop()

    @bot.slash_command(name="choose_spells", description="Выбрать заклинания при повышении уровня")
    async def choose_spells(inter: disnake.ApplicationCommandInteraction):
        char = cursor.execute("SELECT char_class, level FROM characters WHERE user_id = ?", (inter.user.id,)).fetchone()
        if not char:
            await inter.response.send_message("Сначала создайте персонажа.", ephemeral=True)
            return

        char_class, level = char
        if char_class not in MAGIC_CLASSES:
            await inter.response.send_message(f"Класс {char_class} не использует заклинания.", ephemeral=True)
            return

        available_spells = get_spells_for_class(char_class, level)
        if not available_spells:
            await inter.response.send_message("На вашем уровне пока нет доступных заклинаний.", ephemeral=True)
            return

        # Например, 2 спелла на 1 уровне, +1 за каждый последующий уровень
        max_spells = min(10, 2 + (level - 1))
        view = SpellSelectView(inter, inter.user.id, available_spells, max_spells)
        await inter.response.send_message(
            f"Выберите до {max_spells} заклинаний, доступных вашему классу ({char_class}) на {level} уровне:",
            view=view,
            ephemeral=True
        )