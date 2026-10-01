"""
Unit tests for core security, password hashing, and JWT token functionality.
"""
import pytest
from datetime import timedelta
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import AuthenticationError


def test_password_hashing():
    """Test password hashing and verification."""
    password = "SecretPassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_create_and_decode_access_token():
    """Test creating and decoding JWT access tokens."""
    token = create_access_token(
        subject=42,
        role="Revenue Manager",
        hotel_ids=[1, 2],
    )
    assert isinstance(token, str)

    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "Revenue Manager"
    assert payload["hotels"] == [1, 2]
    assert payload["type"] == "access"


def test_create_and_decode_refresh_token():
    """Test creating and decoding JWT refresh tokens."""
    token = create_refresh_token(subject=42)
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "refresh"


def test_expired_token_raises_exception():
    """Test that expired tokens raise AuthenticationError."""
    token = create_access_token(
        subject=42,
        role="Analyst",
        expires_delta=timedelta(seconds=-10),  # expired 10s ago
    )
    with pytest.raises(AuthenticationError):
        decode_token(token)
