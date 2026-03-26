from datetime import datetime, timedelta
from jose import JWTError, jwt
from core.config import configs


def create_access_token(data: dict, expire_minutes: int | None = None) -> str:
    to_encode = data.copy()
    if expire_minutes is not None:
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    else:
        expire = datetime.utcnow() + timedelta(days=configs.ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, configs.JWT_SECRET_KEY, algorithm=configs.ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, configs.JWT_SECRET_KEY, algorithms=[configs.ALGORITHM])
        return payload
    except JWTError:
        return None
