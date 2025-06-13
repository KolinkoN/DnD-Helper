import disnake
from disnake.ext import commands
import sqlite3
import os
from dotenv import load_dotenv
import character_commands
import json
import leveling_system


with open("races.json", "r", encoding="utf-8") as f:
    races_data = json.load(f)

# Создаем словарь по имени расы для быстрого доступа:
races_by_name = {race["name"]: race for race in races_data}


load_dotenv(dotenv_path="TOKEN.env")

conn = sqlite3.connect('bot.db')
cursor = conn.cursor()


cursor.execute("""CREATE TABLE IF NOT EXISTS characters (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    char_class TEXT,
    race TEXT,
    size TEXT,
    strength INTEGER,
    dexterity INTEGER,
    constitution INTEGER,
    intelligence INTEGER,
    wisdom INTEGER,
    charisma INTEGER,
    level INTEGER DEFAULT 1,
    hp INTEGER DEFAULT 0
)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS character_spells (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    spell_name TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES characters (user_id) ON DELETE CASCADE
)
""")
conn.commit()

intents = disnake.Intents.default()
intents.message_content = True

bot = commands.InteractionBot(intents=intents)

bot.conn = conn
bot.cursor = cursor


@bot.slash_command(name="ping", description="Проверка связи")
async def ping(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message(f'Понг! {round(bot.latency * 1000)} мс')

@bot.event
async def on_ready():
    print(f"✅ Бот зашёл как {bot.user}")
    cmds = bot.application_commands
    print(f"Зарегистрированные команды: {[cmd.name for cmd in cmds]}")

@bot.slash_command()
async def user(inter):
    await inter.response.send_message(f"Ваш тег: {inter.author}\nВаш ID: {inter.author.id}")

bot.load_extension("roll_commands")
leveling_system.setup_spell_leveling(bot, conn, cursor)
character_commands.setup(bot, conn, cursor,races_by_name)

TOKEN = os.getenv('TOKEN')
bot.run(TOKEN)