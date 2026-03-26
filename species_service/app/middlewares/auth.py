from fastapi import Depends, HTTPException, status, Header
from utils.jwt import decode_token
from core.messages import UNAUTHORIZED, FORBIDDEN


async def get_current_user(authorization: str = Header(..., alias="Authorization")):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED)
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED)
    return payload


async def require_admin(user: dict = Depends(get_current_user)):
    print("Current user:", user)  # Debugging statement
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=FORBIDDEN)
    return user
