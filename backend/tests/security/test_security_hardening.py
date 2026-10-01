"""
Security hardening tests: Security headers, SQL injection resistance, and secret protection.
"""
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_security_headers_present():
    """Verify HTTP security headers are injected into API responses."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_secret_key_protection():
    """Verify secrets are represented as SecretStr and do not leak in str(settings)."""
    settings_str = str(settings)
    assert settings.SECRET_KEY.get_secret_value() not in settings_str
    assert "super-secret" not in settings_str


def test_sql_injection_resilience():
    """Verify SQL injection payloads in parameters do not execute or break SQL syntax."""
    malicious_email = "admin@hotel.com' OR '1'='1"
    response = client.post(
        "/api/v1/auth/login",
        json={"email": malicious_email, "password": "anypassword"},
    )
    # Should fail authentication gracefully without SQL syntax exception (500)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"
