from db.base import cursor, conn



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
    level INTEGER DEFAULT 1
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