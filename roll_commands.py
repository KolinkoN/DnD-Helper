import re
import random
import disnake
from disnake.ext import commands


def setup(bot: commands.InteractionBot):
    @bot.slash_command(name="roll", description="Бросок кубиков (обычный, преимущество, помеха, урон)")
    async def roll(
        inter: disnake.ApplicationCommandInteraction,
        expression: str = commands.Param(description="Например: d20+5, 2d6, 1d8-1"),
        mode: str = commands.Param(choices=["обычный", "преимущество", "помеха"], default="обычный"),
        damage: bool = commands.Param(default=False, description="Если True — бросок урона, итог может быть 0")
    ):
        await inter.response.defer()

        original_expression = expression.strip().replace(" ", "")
        if original_expression.startswith("d"):
            original_expression = "1" + original_expression

        match = re.fullmatch(r"(\d{1,2})d(\d{1,3})([+-]\d{1,4}+)?", original_expression)
        if not match:
            await inter.edit_original_response("❌ Неверный формат. Пример: 2d6+1 или d20-2.")
            return

        dice_count, dice_sides, modifier = match.groups()
        dice_count = int(dice_count)
        dice_sides = int(dice_sides)
        modifier = int(modifier) if modifier else 0

        if dice_count == 0:
            await inter.edit_original_response("❌ Нельзя бросить 0 кубов .")
            return

        if dice_count > 50:
            await inter.edit_original_response("❌ Максимум кубов: 50.")
            return

        if dice_sides not in {2, 4, 6, 8, 10, 12, 20, 100}:
            await inter.edit_original_response("❌ Допустимые значения граней: 2, 4, 6, 8, 10, 12, 20, 100.")
            return

        # Проверки на некорректные комбинации
        if damage and mode != "обычный":
            await inter.edit_original_response("❌ Нельзя использовать преимущество/помеху при броске урона.")
            return

        if mode != "обычный" and not (dice_count == 1 and dice_sides == 20):
            await inter.edit_original_response("❌ Преимущество и помеха доступны только для одиночного броска d20.")
            return

        # Генерация бросков
        if dice_count == 1 and dice_sides == 20 and mode in ("преимущество", "помеха"):
            r1 = random.randint(1, 20)
            r2 = random.randint(1, 20)
            rolls = [r1, r2]
            result = max(r1, r2) if mode == "преимущество" else min(r1, r2)
        else:
            rolls = [random.randint(1, dice_sides) for _ in range(dice_count)]
            result = sum(rolls)

        total = result + modifier

        # Если это не урон — минимальный результат 1
        if damage:
            total = max(0, total)
        else:
            total = max(1, total)

        rolls_str = ", ".join(map(str, rolls))
        mod_sign = f"{modifier:+}"

        embed = disnake.Embed(
            title="🎲 Damage Roll" if damage else "🎲 Roll Dice",
            color=0xFF4500 if damage else 0x00FF00
        )
        embed.add_field(name="Выражение", value=f"{dice_count}d{dice_sides}{mod_sign} ({mode})", inline=False)
        embed.add_field(name="Броски", value=f"[{rolls_str}]", inline=True)
        embed.add_field(name="Модификатор", value=mod_sign, inline=True)
        embed.add_field(name="Итог", value=str(total), inline=False)

        if not damage and dice_count == 1 and dice_sides == 20 and mode == "обычный":
            if rolls[0] == 20:
                embed.description = "🎯 **Критический успех!**"
            elif rolls[0] == 1:
                embed.description = "💀 **Критический провал!**"

        await inter.edit_original_response(embed=embed)