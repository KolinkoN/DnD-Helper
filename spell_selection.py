import disnake
from disnake.ui import View, Select
from disnake import SelectOption
import json

# Загружаем заклинания
with open("spells.json", "r", encoding="utf-8") as f:
    all_spells = json.load(f)

# Загружаем ограничения по классам
with open("spell_limits.json", "r", encoding="utf-8") as f:
    spell_limits = json.load(f)


class SpellSelectView(View):
    def __init__(self, inter, character_name, char_class, spell_list, max_spells):
        super().__init__(timeout=120)
        self.inter = inter
        self.character_name = character_name
        self.char_class = char_class
        self.spell_list = spell_list
        self.max_spells = max_spells
        self.selected_spells = []

        options = [
            SelectOption(label=spell, description=f"Уровень {all_spells[spell]['level']}")
            for spell in spell_list
        ]

        self.select = Select(
            placeholder=f"Выберите до {max_spells} заклинаний",
            options=options[:25],  # Ограничение Discord
            min_values=1,
            max_values=max_spells
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, inter: disnake.MessageInteraction):
        if inter.user.id != self.inter.user.id:
            await inter.response.send_message("Это не для вас!", ephemeral=True)
            return

        self.selected_spells = self.select.values
        await inter.response.edit_message(
            content=f"Вы выбрали: {', '.join(self.selected_spells)}",
            view=None
        )
        self.stop()


async def handle_spell_selection(inter, character_name, char_class, level, max_spells=None, stat_mod=3):
    limits = spell_limits.get(char_class)
    if not limits:
        # Класс не использует магию — просто молча выходим
        print(f"[INFO] Класс {char_class} не использует заклинания на уровне {level}.")
        return []

    if max_spells is None:
        if "known_spells" in limits:
            max_spells = limits["known_spells"].get(str(level), 0)
        elif "prepared_spells" in limits:
            try:
                max_spells = eval(
                    limits["prepared_spells"],
                    {},
                    {"level": level, "WIS_mod": stat_mod, "CHA_mod": stat_mod, "INT_mod": stat_mod}
                )
            except Exception:
                max_spells = level
        else:
            max_spells = 0

    available_spells = [
        name for name, spell in all_spells.items()
        if char_class in spell.get("classes", []) and spell["level"] <= level and spell["level"] > 0
    ]

    if not available_spells or max_spells == 0:
        if not inter.response.is_done():
            await inter.response.send_message("Нет доступных заклинаний или ваш класс их не использует.", ephemeral=True)
        else:
            await inter.followup.send("Нет доступных заклинаний или ваш класс их не использует.", ephemeral=True)
        return []

    view = SpellSelectView(inter, character_name, char_class, available_spells, max_spells)
    if not inter.response.is_done():
        await inter.response.send_message(
            f"Выберите до {max_spells} заклинаний для {char_class} (уровень {level}):",
            view=view,
            ephemeral=True
        )
    else:
        await inter.followup.send(
            f"Выберите до {max_spells} заклинаний для {char_class} (уровень {level}):",
            view=view,
            ephemeral=True
        )

    await view.wait()
    return view.selected_spells


async def get_cantrip_count(char_class, level):
    limits = spell_limits.get(char_class)
    if not limits:
        return 0

    if limits.get("cantrips") == "all":
        return -1  # Специальное значение: "все заговоры"
    elif isinstance(limits.get("cantrips"), list):
        return limits["cantrips"][level]
    else:
        return 0