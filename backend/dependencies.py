from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from config import JWT_SECRET, JWT_ALGORITHM

security = HTTPBearer()

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("sub") != "admin":
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload
