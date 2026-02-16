import aiosqlite
from config import DATABASE_PATH

db_connection = None

async def connect_db():
    global db_connection
    db_connection = await aiosqlite.connect(DATABASE_PATH)
    db_connection.row_factory = aiosqlite.Row
    
    # Create items table
    await db_connection.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image_filename TEXT,
            sold INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    await db_connection.commit()

async def close_db():
    global db_connection
    if db_connection:
        await db_connection.close()

def get_db():
    if db_connection is None:
        raise RuntimeError("Database not initialised — lifespan has not run")
    return db_connection
