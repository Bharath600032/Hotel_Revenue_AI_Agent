"""
Integration tests for Inventory, Reservation, and CSV Import REST APIs.
"""
import io
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


def test_import_and_query_reservations():
    token = get_token()

    # 1. Create Hotel & Room Type
    h_resp = client.post(
        "/api/v1/hotels",
        headers={"Authorization": f"Bearer {token}"},
        json={"hotel_code": "HTL_IMP", "hotel_name": "Import Test Hotel", "city": "Goa"},
    )
    hotel_id = h_resp.json()["hotel_id"]

    client.post(
        f"/api/v1/hotels/{hotel_id}/room-types",
        headers={"Authorization": f"Bearer {token}"},
        json={"room_type_code": "DELUXE", "room_type_name": "Deluxe Room", "base_price": 5000.0},
    )
    client.post(
        f"/api/v1/hotels/{hotel_id}/rate-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={"rate_plan_code": "STANDARD", "rate_plan_name": "Standard Rate"},
    )

    # 2. Upload CSV Import File
    csv_content = (
        "reservation_code,room_type_code,booking_date,checkin_date,checkout_date,room_rate\n"
        "RES-101,DELUXE,2026-09-01,2026-10-15,2026-10-18,5500\n"
        "RES-102,DELUXE,2026-09-02,2026-10-16,2026-10-19,5800\n"
    )

    file_obj = io.BytesIO(csv_content.encode("utf-8"))
    proc_resp = client.post(
        f"/api/v1/hotels/{hotel_id}/imports/process",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("reservations.csv", file_obj, "text/csv")},
    )

    assert proc_resp.status_code == 200
    report = proc_resp.json()
    assert report["success"] is True
    assert report["imported_count"] == 2
    assert report["failed_count"] == 0

    # 3. Query Reservations Endpoint
    res_list_resp = client.get(
        f"/api/v1/hotels/{hotel_id}/reservations",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_list_resp.status_code == 200
    res_list = res_list_resp.json()
    assert len(res_list) == 2
