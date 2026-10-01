"""
Integration tests for Agent Chat REST API endpoints.
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


def test_agent_chat_api_endpoint():
    token = get_token()

    # 1. Create Hotel & Room Type
    h_resp = client.post(
        "/api/v1/hotels",
        headers={"Authorization": f"Bearer {token}"},
        json={"hotel_code": "HTL_CHAT", "hotel_name": "Chat Test Hotel", "city": "Goa"},
    )
    hotel_id = h_resp.json()["hotel_id"]

    client.post(
        f"/api/v1/hotels/{hotel_id}/room-types",
        headers={"Authorization": f"Bearer {token}"},
        json={"room_type_code": "DELUXE", "room_type_name": "Deluxe Room", "base_price": 5000.0},
    )

    # 2. Call Agent Chat Endpoint
    chat_resp = client.post(
        "/api/v1/agent/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "hotel_id": hotel_id,
            "message": "What should the Deluxe Room rate be for 20 September 2026?",
        },
    )

    assert chat_resp.status_code == 200
    res_data = chat_resp.json()
    assert "answer" in res_data
    assert "agent_run_id" in res_data
    assert res_data["agent_run_id"].startswith("run_")
    assert isinstance(res_data["tools_used"], list)

    agent_run_id = res_data["agent_run_id"]

    # 3. Query Agent Runs
    runs_resp = client.get(
        "/api/v1/agent/runs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert runs_resp.status_code == 200
    assert len(runs_resp.json()) >= 1

    # 4. Query Agent Tool Calls Trace
    calls_resp = client.get(
        f"/api/v1/agent/runs/{agent_run_id}/calls",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert calls_resp.status_code == 200
    assert len(calls_resp.json()) >= 1
