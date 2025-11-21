from datetime import datetime, timedelta
from typing import Iterable
from jose import jwt
from ..core.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM, SECRET_KEY_REFRESH, REFRESH_TOKEN_EXPIRE_DAYS


def create_access_token(sub: str,  role: Iterable[str] | None = None, expires_delta: timedelta | None = None) -> str:
    now = datetime.utcnow()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(sub), "role": list(role or []),
                 "iat": now, "exp": now + expires_delta}
    print("payload", to_encode)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# def create_refresh_token(sub: str, expires_delta: timedelta | None = None) -> str:
#     now = datetime.utcnow()
#     if expires_delta is None:
#         expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
#     to_encode = {"sub": str(sub), "iat": now, "exp": now + expires_delta}
#     return jwt.encode(to_encode, SECRET_KEY_REFRESH, algorithm=ALGORITHM)


def decode_token(token: str, refresh: bool = False) -> dict:
    secret = (
        SECRET_KEY_REFRESH if refresh
        else SECRET_KEY
    )
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiresSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
