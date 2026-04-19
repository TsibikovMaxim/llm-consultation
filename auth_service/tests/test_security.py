import pytest

from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_differs_from_plain():
    hashed = hash_password("secret123")
    assert hashed != "secret123"


def test_verify_correct_password():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed) is True


def test_verify_wrong_password():
    hashed = hash_password("secret123")
    assert verify_password("wrong_password", hashed) is False


def test_create_and_decode_token():
    token = create_access_token(sub="42", role="user")
    payload = decode_token(token)

    assert payload["sub"] == "42"
    assert payload["role"] == "user"
    assert "iat" in payload
    assert "exp" in payload


def test_token_sub_and_role_match():
    token = create_access_token(sub="99", role="admin")
    payload = decode_token(token)

    assert payload["sub"] == "99"
    assert payload["role"] == "admin"
