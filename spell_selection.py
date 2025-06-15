import disnake
from disnake.ui import View, Select, Button
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
            options=options[:25],
            min_values=1,
            max_values=max_spells if max_spells > 0 else 1
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

        self.confirm_button = Button(label="Подтвердить выбор", style=disnake.ButtonStyle.success)
        self.confirm_button.callback = self.confirm_callback
        self.add_item(self.confirm_button)

    async def select_callback(self, inter: disnake.MessageInteraction):
        if inter.user.id != self.inter.user.id:
            await inter.response.send_message("Это не для вас!", ephemeral=True)
            return

        self.selected_spells = self.select.values
        await inter.response.defer()

    async def confirm_callback(self, inter: disnake.MessageInteraction):
        if inter.user.id != self.inter.user.id:
            await inter.response.send_message("Это не для вас!", ephemeral=True)
            return

        if not self.selected_spells:
            await inter.response.send_message("Пожалуйста, выберите хотя бы одно заклинание перед подтверждением.",
                                              ephemeral=True)
            return

        await inter.response.edit_message(
            content=f"Вы выбрали: {', '.join(self.selected_spells)}",
            view=None
        )
        self.stop()


async def handle_spell_selection(inter, character_name, char_class, level, max_spells=None, stat_mod=3,
                                 existing_spells=None):
    limits = spell_limits.get(char_class)
    if not limits:
        print(f"[INFO] Класс {char_class} не использует заклинания на уровне {level}.")
        return []

    if max_spells is None:
        if "known_spells" in limits and isinstance(limits["known_spells"], list):
            max_spells = limits["known_spells"][level] if level < len(limits["known_spells"]) else 0
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

    if existing_spells:
        available_spells = [spell for spell in available_spells if spell not in existing_spells]

    if not available_spells or max_spells == 0:
        if not inter.response.is_done():
            await inter.response.send_message("Нет доступных заклинаний или ваш класс их не использует.",
                                              ephemeral=True)
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


async def handle_cantrip_selection(inter, character_name, char_class, level, existing_spells=None):
    cantrip_count = await get_cantrip_count(char_class, level)
    if cantrip_count == 0:
        await inter.response.send_message("Ваш класс не может использовать заговоры.", ephemeral=True)
        return []

    # Получаем список заговоров
    available_cantrips = [
        name for name, spell in all_spells.items()
        if char_class in spell.get("classes", []) and spell["level"] == 0
    ]

    if existing_spells:
        available_cantrips = [spell for spell in available_cantrips if spell not in existing_spells]

    if not available_cantrips:
        await inter.response.send_message("Нет доступных заговоров для выбора.", ephemeral=True)
        return []

    # Если можно выбрать все
    if cantrip_count == -1:
        cantrip_count = len(available_cantrips)

    view = SpellSelectView(inter, character_name, char_class, available_cantrips, cantrip_count)
    await inter.response.send_message(
        f"Выберите до {cantrip_count} заговоров (0 уровень) для {char_class}:",
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
        return -1
    elif isinstance(limits.get("cantrips"), list):
        if level < len(limits["cantrips"]):
            return limits["cantrips"][level]
        else:
            return 0
    else:
        return 0
