from dotenv import load_dotenv
import os

load_dotenv()

def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Required environment variable '{key}' is not set")
    return value

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = _require("ADMIN_PASS")
JWT_SECRET = _require("JWT_SECRET")
JWT_ALGORITHM = "HS256"
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "jimmystore")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
