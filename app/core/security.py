"""
This module define the secuirty for authentication
Implements the following:
    - hash raw password (using bcrypt)
    - verify hash for password
    - creates jwt access token
    - verifies jwt access token
    - get current user dependency
"""

from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import get_settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

settings = get_settings()
oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")
password_hash = PasswordHash.recommended()


# hash password
def hash_password(raw_pwd: str) -> str:
    """hashes the password using bcrypt"""
    return password_hash.hash(raw_pwd)


def verify_password(raw_pwd: str, pwd_hash: str) -> bool:
    "heck whether the raw password and the password hash matches"
    return password_hash.verify(raw_pwd, pwd_hash)


def create_access_token(payload: dict):
    to_encode = payload.copy()
    to_encode.update(
        {
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINS)
        }
    )
    token = jwt.encode(
        payload=to_encode, key=settings.SECRET, algorithm=settings.ALGORITHM
    )
    return token


def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET, algorithms=[settings.ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token"
        )


def get_current_user(token: str = Depends(oauth2_schema)):
    """
    returns the current user object from the jwt token if valid
    Args: token -: jwt access token for user
    """
    payload = verify_access_token(token=token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )
    return user_id
