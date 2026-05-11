from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)
import pytest
import jwt
from fastapi import HTTPException
from app.core.config import get_settings
from datetime import datetime, timedelta, timezone

settings = get_settings()


def test_hash_password():
    password = "test-password@123"
    password_hash = hash_password(password)
    assert password != password_hash


def test_verify_hash():
    password = "test-password@123"
    password_hash = hash_password(password)
    assert verify_password(password, password_hash) is True


def test_verify_wrong_password():

    password = "secret123"

    hashed = hash_password(password)

    assert verify_password("wrongpass", hashed) is False


def test_create_access_token():

    data = {"sub": "aman"}

    token = create_access_token(data)

    assert token is not None
    assert isinstance(token, str)


def test_verify_token():

    data = {"sub": "aman"}

    token = create_access_token(data)

    payload = verify_access_token(token)

    assert payload["sub"] == "aman"


def test_verify_invalid_token():
    """
    Should raise HTTPException
    for invalid JWT token.
    """

    invalid_token = "this.is.invalid"

    with pytest.raises(HTTPException) as exc:
        verify_access_token(invalid_token)

    assert exc.value.status_code == 401
    assert exc.value.detail == "invalid or expired token"


def test_verify_expired_token():
    """
    Should raise HTTPException
    for expired JWT token.
    """

    expired_token = jwt.encode(
        {"sub": "123", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.SECRET,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc:
        verify_access_token(expired_token)

    assert exc.value.status_code == 401
    assert exc.value.detail == "invalid or expired token"
