from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL, DB_NAME

client: AsyncIOMotorClient = None
db = None

async def connect_db():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

async def close_db():
    global client
    if client:
        client.close()  # Motor's close() is synchronous; do not await

def get_db():
    if db is None:
        raise RuntimeError("Database not initialised — lifespan has not run")
    return db
