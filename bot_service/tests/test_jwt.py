from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings
from app.core.jwt import decode_and_validate


def make_token(
    sub: str = "42",
    role: str = "user",
    expire_delta: timedelta = timedelta(hours=1),
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": role,
        "iat": now,
        "exp": now + expire_delta,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def test_valid_token_returns_payload():
    token = make_token()
    payload = decode_and_validate(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "user"


def test_invalid_token_raises():
    with pytest.raises(ValueError):
        decode_and_validate("not.a.valid.token")


def test_expired_token_raises():
    token = make_token(expire_delta=timedelta(seconds=-1))
    with pytest.raises(ValueError, match="expired"):
        decode_and_validate(token)
