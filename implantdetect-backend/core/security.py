import hmac
import hashlib
from jose import jwt
from typing import Optional
from jose.exceptions import JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone

from core.configuration import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token de acesso JWT com dados e uma data de expiração opcional.
    """
    
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_access_token(token: str) -> Optional[dict]:
    """
    Verifica a validade de um token de acesso JWT.
    """
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload

    except JWTError:
        return None


def hash_password(password: str) -> str:
    """
    Hashes a plain password using SHA-256 and a secret key as salt.
    """
    salted = (password + settings.SECRET_KEY).encode()
    return hashlib.sha256(salted).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a SHA-256 hash.
    """
    return hmac.compare_digest(hash_password(plain_password), hashed_password)


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Obtém o usuário atual a partir do token de acesso.
    """
    
    payload = verify_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    return payload