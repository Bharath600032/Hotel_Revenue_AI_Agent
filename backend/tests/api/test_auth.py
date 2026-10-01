"""
Integration tests for Auth & RBAC API endpoints.
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

# Setup test in-memory sqlite database
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
    # Seed Revenue Manager
    user_repository.create(
        db,
        UserCreate(
            email="manager@hotel.com",
            password="ManagerPassword123!",
            full_name="Revenue Manager",
            role="Revenue Manager",
        ),
    )
    # Seed Analyst
    user_repository.create(
        db,
        UserCreate(
            email="analyst@hotel.com",
            password="AnalystPassword123!",
            full_name="Analyst User",
            role="Analyst",
        ),
    )
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_login_success():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "manager@hotel.com", "password": "ManagerPassword123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "manager@hotel.com"
    assert data["user"]["role"] == "Revenue Manager"


def test_login_invalid_password():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "manager@hotel.com", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"


def test_get_me_authenticated():
    # Login as Analyst
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@hotel.com", "password": "AnalystPassword123!"},
    )
    token = login_resp.json()["access_token"]

    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "analyst@hotel.com"


def test_register_user_admin_only_authorization():
    # Login as Revenue Manager (non-admin)
    login_mgr = client.post(
        "/api/v1/auth/login",
        json={"email": "manager@hotel.com", "password": "ManagerPassword123!"},
    )
    token_mgr = login_mgr.json()["access_token"]

    # Attempt to register new user as Revenue Manager -> should fail 403 Forbidden
    reg_fail = client.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {token_mgr}"},
        json={
            "email": "newuser@hotel.com",
            "password": "NewUserPass123!",
            "full_name": "New Staff",
            "role": "Analyst",
        },
    )
    assert reg_fail.status_code == 403

    # Login as Admin
    login_admin = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@hotel.com", "password": "AdminPassword123!"},
    )
    token_admin = login_admin.json()["access_token"]

    # Register as Admin -> should succeed 201 Created
    reg_ok = client.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {token_admin}"},
        json={
            "email": "newuser@hotel.com",
            "password": "NewUserPass123!",
            "full_name": "New Staff",
            "role": "Analyst",
        },
    )
    assert reg_ok.status_code == 201
    assert reg_ok.json()["email"] == "newuser@hotel.com"


def test_refresh_token_flow():
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@hotel.com", "password": "AdminPassword123!"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json()
