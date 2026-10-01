"""
Integration tests for Hotels, Room Types, and Rate Plans REST APIs.
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
    # Seed Read-Only User without assigned hotels
    user_repository.create(
        db,
        UserCreate(
            email="readonly@hotel.com",
            password="ReadonlyPassword123!",
            full_name="Readonly User",
            role="Read-only User",
            assigned_hotels="99",
        ),
    )
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def get_token(email: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return response.json()["access_token"]


def test_create_and_get_hotel():
    token = get_token("admin@hotel.com", "AdminPassword123!")

    # Create Hotel
    create_resp = client.post(
        "/api/v1/hotels",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "hotel_code": "HTL_GOA",
            "hotel_name": "Goa Beach Resort",
            "city": "Goa",
            "total_rooms": 80,
        },
    )
    assert create_resp.status_code == 201
    hotel_data = create_resp.json()
    assert hotel_data["hotel_code"] == "HTL_GOA"
    hotel_id = hotel_data["hotel_id"]

    # List Hotels
    list_resp = client.get(
        "/api/v1/hotels",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # Get Single Hotel
    get_resp = client.get(
        f"/api/v1/hotels/{hotel_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["hotel_name"] == "Goa Beach Resort"


def test_create_room_type_and_rate_plan():
    token = get_token("admin@hotel.com", "AdminPassword123!")

    # Create Hotel first
    h_resp = client.post(
        "/api/v1/hotels",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "hotel_code": "HTL_MUM",
            "hotel_name": "Mumbai City Hotel",
            "city": "Mumbai",
            "total_rooms": 150,
        },
    )
    hotel_id = h_resp.json()["hotel_id"]

    # Create Room Type
    rt_resp = client.post(
        f"/api/v1/hotels/{hotel_id}/room-types",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "room_type_code": "EXECUTIVE",
            "room_type_name": "Executive Suite",
            "base_price": 8500.0,
            "total_inventory": 20,
        },
    )
    assert rt_resp.status_code == 201
    assert rt_resp.json()["base_price"] == 8500.0

    # Create Rate Plan
    rp_resp = client.post(
        f"/api/v1/hotels/{hotel_id}/rate-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "rate_plan_code": "BB_FLEX",
            "rate_plan_name": "Bed & Breakfast Flexible",
            "meal_plan": "CP",
            "multiplier": 1.15,
        },
    )
    assert rp_resp.status_code == 201
    assert rp_resp.json()["meal_plan"] == "CP"


def test_read_only_user_hotel_access_control():
    admin_token = get_token("admin@hotel.com", "AdminPassword123!")

    # Create Hotel ID 1
    h_resp = client.post(
        "/api/v1/hotels",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "hotel_code": "HTL_DEL",
            "hotel_name": "Delhi Palace",
            "city": "Delhi",
            "total_rooms": 100,
        },
    )
    hotel_id = h_resp.json()["hotel_id"]

    # Login as Read-Only User assigned only to hotel ID 99
    readonly_token = get_token("readonly@hotel.com", "ReadonlyPassword123!")

    # Accessing hotel ID 1 should be denied 403 Forbidden
    get_resp = client.get(
        f"/api/v1/hotels/{hotel_id}",
        headers={"Authorization": f"Bearer {readonly_token}"},
    )
    assert get_resp.status_code == 403
