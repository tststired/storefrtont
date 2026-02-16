from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from database import connect_db, close_db
from config import UPLOADS_DIR
from routes import auth, items

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    yield
    await close_db()

app = FastAPI(title="JimmyStore API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(items.router, prefix="/items", tags=["items"])
