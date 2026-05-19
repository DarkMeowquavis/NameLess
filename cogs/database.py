import aiosqlite

DB_PATH = "../namelessbot.db"

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    
    await db.execute('''CREATE TABLE IF NOT EXISTS players (
        user_id INTEGER PRIMARY KEY,
        void_coins INTEGER DEFAULT 0,
        items TEXT DEFAULT '{}',
        titles TEXT DEFAULT '["The Nameless"]',
        bio TEXT DEFAULT 'Just another nameless monster...',
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        last_daily INTEGER DEFAULT NULL,
        voice_time INTEGER DEFAULT 0,
        messages_sent INTEGER DEFAULT 0
    )''')

    # Settings for Logs Channel
    await db.execute('''CREATE TABLE IF NOT EXISTS settings (
        guild_id INTEGER PRIMARY KEY,
        logs_channel INTEGER DEFAULT NULL
    )''')
    
    # Add missing columns safely
    columns = ["xp", "level", "last_daily", "voice_time", "messages_sent"]
    for col in columns:
        try:
            await db.execute(f"ALTER TABLE players ADD COLUMN {col} INTEGER DEFAULT 0")
        except:
            pass
            
    await db.commit()
    return db