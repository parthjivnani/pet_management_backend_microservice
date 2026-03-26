from jose import JWTError, jwt
from core.config import configs


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, configs.JWT_SECRET_KEY, algorithms=[configs.ALGORITHM])
    except JWTError:
        return None
