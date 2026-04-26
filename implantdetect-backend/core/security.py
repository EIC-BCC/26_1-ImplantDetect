import hmac
import hashlib
from jose import jwt
from typing import Optional, TypedDict
from jose.exceptions import JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone

from core.logging import get_logger
from core.configuration import settings

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/login")


class JWTPayload(TypedDict):
    sub: str
    exp: int


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_access_token(token: str) -> Optional[JWTPayload]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def hash_password(password: str) -> str:
    salted = (password + settings.SECRET_KEY).encode()
    return hashlib.sha256(salted).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hmac.compare_digest(hash_password(plain_password), hashed_password)


def get_current_user(token: str = Depends(oauth2_scheme)) -> JWTPayload:
    payload = verify_access_token(token)
    if not payload:
        logger.warning("Tentativa de acesso com token inválido ou expirado.")
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    return payload
