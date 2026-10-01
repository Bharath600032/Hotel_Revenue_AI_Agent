"""
Integration tests for Observability, Health Probes, and Audit Log REST APIs.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate

engine = create_engine("sqlite:///:memory:", echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Seed Admin User
    user_repository.create(
        db,
        UserCreate(
            email="admin@hotel.com",
            password="AdminPassword123!",
            full_name="Admin User",
            role="Administrator",
        ),
    )
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def get_token():
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@hotel.com", "password": "AdminPassword123!"},
    )
    return resp.json()["access_token"]


def test_health_probes():
    # Top-level health
    h_resp = client.get("/health")
    assert h_resp.status_code == 200
    assert h_resp.json()["status"] == "healthy"

    # API v1 health
    v1_h = client.get("/api/v1/health")
    assert v1_h.status_code == 200
    assert v1_h.json()["status"] == "healthy"

    # Readiness
    r_resp = client.get("/api/v1/readiness")
    assert r_resp.status_code == 200
    assert r_resp.json()["status"] == "ready"

    # Liveness
    l_resp = client.get("/api/v1/liveness")
    assert l_resp.status_code == 200
    assert l_resp.json()["status"] == "alive"


def test_audit_logs_api():
    token = get_token()

    # Perform an action that logs an audit entry
    client.post(
        "/api/v1/hotels",
        headers={"Authorization": f"Bearer {token}"},
        json={"hotel_code": "HTL_OBS", "hotel_name": "Observability Hotel", "city": "Goa"},
    )

    # Query audit logs
    audit_resp = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert audit_resp.status_code == 200
    logs = audit_resp.json()
    assert len(logs) >= 1
    assert logs[0]["action"] == "CREATE_HOTEL"
