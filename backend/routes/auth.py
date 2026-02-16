from fastapi import APIRouter, HTTPException, status
import jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from config import ADMIN_USER, ADMIN_PASS, JWT_SECRET, JWT_ALGORITHM

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    if body.username != ADMIN_USER or body.password != ADMIN_PASS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    expire = datetime.now(timezone.utc) + timedelta(days=7)
    token = jwt.encode(
        {"sub": "admin", "exp": expire},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    return TokenResponse(access_token=token)
