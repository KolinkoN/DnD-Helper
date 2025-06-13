import disnake
import random
import json
import leveling_system
from disnake.ext import commands
from disnake.ui import View, Button
from disnake import ButtonStyle
from spell_selection import handle_spell_selection, SpellSelectView
from hp_calculator import calculate_starting_hp


with open("races.json", "r", encoding="utf-8") as f:
    races_data = json.load(f)
# Преобразуем в словарь по имени
races_by_name = {race["name"]: race for race in races_data}
with open("hit_dice.json", "r") as f:
    HIT_DICE = json.load(f)

def roll_stat():
    rolls = [random.randint(1, 6) for _ in range(4)]
    rolls.sort()
    return sum(rolls[1:]), rolls

def setup(bot, conn, cursor, races_by_name):
    class SizeSelectView(View):
        def __init__(self, inter, name, char_class, race, size_options, race_data):
            super().__init__(timeout=60)
            self.inter = inter
            self.name = name
            self.char_class = char_class
            self.race = race
            self.size_options = size_options
            self.race_data = race_data
            self.selected_size = None
            self.message = None

            options = [disnake.SelectOption(label=size, description=f"Размер {size}") for size in size_options]

            self.select = disnake.ui.Select(
                placeholder="Выберите размер персонажа",
                options=options,
                min_values=1,
                max_values=1
            )
            self.add_item(self.select)
            self.select.callback = self.select_callback

        async def select_callback(self, inter: disnake.MessageInteraction):
            if inter.user.id != self.inter.user.id:
                await inter.response.send_message("Это не для вас!", ephemeral=True)
                return

            self.selected_size = self.select.values[0]
            await inter.response.edit_message(content=f"Выбран размер: {self.selected_size}", view=None)

            roll_view = CharacterRollView(inter, self.name, self.char_class, self.race, self.selected_size, self.race_data)
            await roll_view.generate_and_show()
            self.stop()

    class CharacterRollView(View):
        def __init__(self, inter, name, char_class, race, size, race_data):
            super().__init__(timeout=60)
            self.inter = inter
            self.name = name
            self.char_class = char_class
            self.race = race
            self.size = size
            self.race_data = race_data
            self.stats = []
            self.message = None
            self.reroll_count = 0
            self.max_rerolls = 2

        async def generate_and_show(self):
            self.stats = [roll_stat() for _ in range(6)]
            stat_names = ["Сила", "Ловкость", "Телосложение", "Интеллект", "Мудрость", "Харизма"]

            detailed = [
                f"{i + 1}. **{stat_names[i]}**: 🎲 {', '.join(map(str, rolls))} → **{value} ({get_modifier(value):+})**"
                for i, (value, rolls) in enumerate(self.stats)
            ]

            hit_die = HIT_DICE.get(self.char_class, 8)
            con_value = self.stats[2][0]
            con_mod = get_modifier(con_value)
            hp_roll = hit_die + con_mod
            hp_text = f"🎯 HP: 1d{hit_die} (выпало {roll}) + модификатор {con_mod:+} = **{hp_roll}**"

            embed = disnake.Embed(
                title=f"🎲 Характеристики для {self.name}",
                description="\n".join(detailed + ["", hp_text]),
                color=0x3498db
            )
            embed.set_footer(
                text=f"Метод: 4d6, убрать минимум | Перебросов осталось: {self.max_rerolls - self.reroll_count}"
            )

            if self.message:
                try:
                    await self.message.edit(embed=embed, view=self)
                except disnake.NotFound:
                    self.message = await self.inter.channel.send(embed=embed, view=self)
            else:
                if not self.inter.response.is_done():
                    self.message = await self.inter.response.send_message(embed=embed, view=self, ephemeral=True)
                else:
                    try:
                        self.message = await self.inter.original_message()
                        await self.message.edit(embed=embed, view=self)
                    except disnake.NotFound:
                        self.message = await self.inter.channel.send(embed=embed, view=self)

            self.hp_roll = hp_roll  # сохраняем для использования при принятии
            self.hp_text = hp_text

        @disnake.ui.button(label="🎲 Перебросить", style=disnake.ButtonStyle.secondary)
        async def reroll(self, button: Button, inter: disnake.MessageInteraction):
            if inter.user.id != self.inter.user.id:
                await inter.response.send_message("Это не для вас!", ephemeral=True)
                return

            if self.reroll_count >= self.max_rerolls:
                await inter.response.send_message("❌ Лимит перебросов достигнут!", ephemeral=True)
                return

            await inter.response.defer()

            new_view = CharacterRollView(inter, self.name, self.char_class, self.race, self.size, self.race_data)
            new_view.reroll_count = self.reroll_count + 1
            # НЕ копируем hp_roll и hp_text, они пересчитаются при генерации заново
            await new_view.generate_and_show()

            self.stop()
        @disnake.ui.button(label="✅ Принять", style=disnake.ButtonStyle.success)
        async def accept(self, button: Button, inter: disnake.MessageInteraction):
            if inter.user.id != self.inter.user.id:
                await inter.response.send_message("Это не для вас!", ephemeral=True)
                return

            values = [s[0] for s in self.stats]
            stat_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
            stat_dict = dict(zip(stat_names, values))

            bonus = self.race_data.get("bonus_value", {})
            for key, val in bonus.items():
                if key in stat_dict:
                    stat_dict[key] += val

            # Шаг 6 — используем уже сгенерированное self.hp_roll
            final_hp = self.hp_roll

            cursor.execute("""
                           INSERT INTO characters (user_id, name, char_class, race, size,
                                                   strength, dexterity, constitution, intelligence, wisdom, charisma,
                                                   level, hp)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           """, (
                               self.inter.user.id, self.name, self.char_class, self.race, self.size,
                               stat_dict["STR"], stat_dict["DEX"], stat_dict["CON"],
                               stat_dict["INT"], stat_dict["WIS"], stat_dict["CHA"],
                               1, final_hp
                           ))
            conn.commit()

            magical_classes = {
                "Bard", "Cleric", "Druid", "Sorcerer", "Warlock", "Wizard",
                "Paladin", "Ranger", "Artificer"
            }

            if self.char_class in magical_classes:
                selected_spells = await handle_spell_selection(inter, self.name, self.char_class, 1, max_spells=4)
                if selected_spells:
                    for spell in selected_spells:
                        cursor.execute("INSERT INTO character_spells (user_id, spell_name) VALUES (?, ?)",
                                       (inter.user.id, spell))
                    conn.commit()
                if not inter.response.is_done():
                    await inter.response.send_message(f"🎉 Персонаж **{self.name}** создан!", ephemeral=True)
                else:
                    await inter.followup.send(f"🎉 Персонаж **{self.name}** создан!", ephemeral=True)
            else:
                if not inter.response.is_done():
                    await inter.response.send_message(f"🎉 Персонаж **{self.name}** создан!", ephemeral=True)
                else:
                    await inter.followup.send(f"🎉 Персонаж **{self.name}** создан!", ephemeral=True)
            self.stop()

    class ClassSelectView(View):
        def __init__(self, inter, name, race, race_data):
            super().__init__(timeout=60)
            self.inter = inter
            self.name = name
            self.race = race
            self.race_data = race_data
            self.class_selected = None

            class_names = [
                "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk",
                "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard", "Artificer"
            ]

            for cls in class_names:
                self.add_item(self.ClassButton(cls))

        class ClassButton(Button):
            def __init__(self, class_name):
                super().__init__(label=class_name, style=ButtonStyle.primary)
                self.class_name = class_name

            async def callback(self, inter: disnake.MessageInteraction):
                view: ClassSelectView = self.view
                if inter.user.id != view.inter.user.id:
                    await inter.response.send_message("Это не для вас!", ephemeral=True)
                    return

                await inter.response.edit_message(content=f"Выбран класс: {self.class_name}", view=None)
                race_data = view.race_data
                size_options = race_data.get("size", [])

                if len(size_options) == 1:
                    size = size_options[0]
                    roll_view = CharacterRollView(inter, view.name, self.class_name, view.race, size, race_data)
                    await roll_view.generate_and_show()
                else:
                    size_view = SizeSelectView(inter, view.name, self.class_name, view.race, size_options, race_data)
                    await inter.channel.send("Выберите размер персонажа:", view=size_view)
                view.stop()

        async def on_timeout(self):
            try:
                await self.inter.edit_original_response(content="⏳ Время выбора истекло.", view=None)
            except:
                pass

    @bot.slash_command(name="create_character", description="Создать персонажа", guild_ids=[1378783701139198083])
    async def create_character(inter: disnake.ApplicationCommandInteraction, name: str,
                               race: str = commands.Param(autocomplete=True)):
        exists = cursor.execute("SELECT 1 FROM characters WHERE user_id = ?", (inter.user.id,)).fetchone()
        if exists:
            if not inter.response.is_done():
                await inter.response.send_message("У вас уже есть персонаж!", ephemeral=True)
            else:
                await inter.followup.send("У вас уже есть персонаж!", ephemeral=True)
            return

        race_data = races_by_name.get(race)
        if not race_data:
            if not inter.response.is_done():
                await inter.response.send_message("Раса не найдена.", ephemeral=True)
            else:
                await inter.followup.send("Раса не найдена.", ephemeral=True)
            return

        view = ClassSelectView(inter, name, race, race_data)

        # Здесь заменяем:
        # await inter.response.send_message(content="Выберите класс персонажа:", view=view, ephemeral=True)
        # на проверку, была ли уже отправлена реакция:
        if not inter.response.is_done():
            await inter.response.send_message(content="Выберите класс персонажа:", view=view, ephemeral=True)
        else:
            await inter.followup.send(content="Выберите класс персонажа:", view=view, ephemeral=True)

    @create_character.autocomplete("race")
    async def autocomplete_race(inter: disnake.ApplicationCommandInteraction, user_input: str):
        suggestions = []
        user_input_lower = user_input.lower()

        for race_name, data in races_by_name.items():
            if user_input_lower in race_name.lower():
                bonuses = data.get("bonus_value", {})
                bonus_text = ", ".join(f"{k}+{v}" for k, v in bonuses.items()) if bonuses else "без бонусов"

                # Показываем максимум 100 символов
                label = f"{race_name} ({bonus_text})"
                if len(label) > 100:
                    label = label[:97] + "..."

                # Ограничиваем длину значения
                value = race_name[:100]

                suggestions.append(disnake.OptionChoice(name=label, value=value))

                if len(suggestions) >= 20:
                    break

        return suggestions

    class ConfirmDeleteView(View):
        def __init__(self, user_id):
            super().__init__(timeout=30)
            self.user_id = user_id

        @disnake.ui.button(label="Удалить", style=disnake.ButtonStyle.danger)
        async def confirm(self, button: Button, inter: disnake.MessageInteraction):
            if inter.user.id != self.user_id:
                await inter.response.send_message("Это не ваша команда!", ephemeral=True)
                return
            cursor.execute("DELETE FROM characters WHERE user_id = ?", (self.user_id,))
            cursor.execute("DELETE FROM character_spells WHERE user_id = ?", (self.user_id,))
            conn.commit()
            await inter.response.edit_message(content="Персонаж удалён!", embed=None, view=None)
            self.stop()

        @disnake.ui.button(label="Отмена", style=disnake.ButtonStyle.secondary)
        async def cancel(self, button: Button, inter: disnake.MessageInteraction):
            if inter.user.id != self.user_id:
                await inter.response.send_message("Это не ваша команда!", ephemeral=True)
                return
            await inter.response.edit_message(content="Удаление отменено.", embed=None, view=None)
            self.stop()

    @bot.slash_command(name="show_character", description="Показать информацию о вашем персонаже",
                       guild_ids=[1378783701139198083])
    async def show_character(inter: disnake.ApplicationCommandInteraction):
        character = cursor.execute(
            "SELECT name, char_class, race, size, strength, dexterity, constitution, intelligence, wisdom, charisma, level, hp FROM characters WHERE user_id = ?",
            (inter.user.id,)).fetchone()
        if not character:
            await inter.response.send_message(
                "Персонаж не найден. Создайте персонажа с помощью команды /create_character.", ephemeral=True)
            return

        name, char_class, race, size, STR, DEX, CON, INT, WIS, CHA, level, hp = character

        embed = disnake.Embed(title=f"Персонаж: {name}", color=0x00ff00)
        embed.add_field(name="Класс", value=char_class, inline=True)
        embed.add_field(name="Раса", value=race, inline=True)
        embed.add_field(name="Размер", value=size, inline=True)
        embed.add_field(name="Уровень", value=f"{level}", inline=True)
        embed.add_field(name="Хиты (HP)", value=str(hp), inline=True)

        embed.add_field(name="Характеристики", value=(
            f"Сила: {STR} ({get_modifier(STR):+})\n"
            f"Ловкость: {DEX} ({get_modifier(DEX):+})\n"
            f"Телосложение: {CON} ({get_modifier(CON):+})\n"
            f"Интеллект: {INT} ({get_modifier(INT):+})\n"
            f"Мудрость: {WIS} ({get_modifier(WIS):+})\n"
            f"Харизма: {CHA} ({get_modifier(CHA):+})"
        ), inline=False)

        spells = cursor.execute(
            "SELECT spell_name FROM character_spells WHERE user_id = ?",
            (inter.user.id,)
        ).fetchall()

        if spells:
            spell_list = "\n".join(f"• {s[0]}" for s in spells)
            embed.add_field(name="Заклинания", value=spell_list, inline=False)

        await inter.response.send_message(embed=embed, ephemeral=True)

    @bot.slash_command(name="list_races", description="Показать все доступные расы")
    async def list_races(inter: disnake.ApplicationCommandInteraction):
        race_list = "\n".join(f"• {r['name']} (размер: {', '.join(r['size'])})" for r in races_by_name.values())
        embed = disnake.Embed(
            title="📜 Доступные расы",
            description=race_list,
            color=0xFFD700
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

    def get_character_names():
        cursor.execute("SELECT name FROM characters")
        return [row[0] for row in cursor.fetchall()]

    def get_modifier(stat_value: int) -> int:
        return (stat_value - 10) // 2

    @bot.slash_command(name="level_up", description="Повысить уровень персонажа (только для Мастера)",
                       guild_ids=[1378783701139198083])
    @commands.has_role("Мастер")
    async def level_up(
            inter: disnake.ApplicationCommandInteraction,
            character_name: str = commands.Param(
                name="имя_персонажа",
                description="Выберите имя персонажа",
                choices=get_character_names()
            )
    ):
        character = cursor.execute(
            "SELECT level, hp, con, char_class FROM characters WHERE name = ?", (character_name,)
        ).fetchone()

        if not character:
            await inter.response.send_message(f"Персонаж `{character_name}` не найден.", ephemeral=True)
            return

        current_level, current_hp, con_stat, char_class = character

        if current_level >= 20:
            await inter.response.send_message(f"❌ `{character_name}` уже достиг максимального уровня (20).",
                                              ephemeral=True)
            return

        new_level = current_level + 1

        hit_die = HIT_DICE.get(char_class.lower(), 8)

        con_mod = get_modifier(con_stat)

        roll = random.randint(1, hit_die)

        hp_gain = max(1, roll + con_mod)

        new_hp = current_hp + hp_gain

        # Обновляем уровень и HP персонажа в базе
        cursor.execute(
            "UPDATE characters SET level = ?, hp = ? WHERE name = ?",
            (new_level, new_hp, character_name)
        )

        # Обновление заклинаний (если есть)
        char_info = cursor.execute("SELECT user_id FROM characters WHERE name = ?", (character_name,)).fetchone()
        if char_info:
            user_id = char_info[0]
            selected_spells = await handle_spell_selection(inter, character_name, char_class, new_level, max_spells=2)
            for spell in selected_spells:
                cursor.execute("INSERT INTO character_spells (user_id, spell_name) VALUES (?, ?)", (user_id, spell))

        conn.commit()

        await inter.response.send_message(
            f"✅ Уровень `{character_name}` повышен до {new_level}! HP увеличено на {hp_gain} и теперь составляет {new_hp}.",
            ephemeral=False
        )

    @bot.slash_command(name="delete_character", description="Удалить персонажа")
    async def delete_character(inter: disnake.ApplicationCommandInteraction):
        character = cursor.execute("SELECT name FROM characters WHERE user_id = ?", (inter.user.id,)).fetchone()

        if not character:

            await inter.response.send_message("Персонаж не найден.", ephemeral=True)
            return

        view = ConfirmDeleteView(inter.user.id)
        await inter.response.send_message(
            f"Вы действительно хотите удалить персонажа **{character[0]}**? Это действие нельзя будет отменить.",
            view=view,
            ephemeral=True
        )
        await view.wait()