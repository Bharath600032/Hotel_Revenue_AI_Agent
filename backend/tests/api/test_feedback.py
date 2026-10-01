"""
Integration tests for Feedback Loop & Model Performance Analytics REST APIs.
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate
from app.models import Hotel, PriceRecommendations

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


def test_submit_and_query_feedback_analytics():
    token = get_token()

    # 1. Create Hotel & Recommendation
    h_resp = client.post(
        "/api/v1/hotels",
        headers={"Authorization": f"Bearer {token}"},
        json={"hotel_code": "HTL_FB", "hotel_name": "Feedback Test Hotel", "city": "Goa"},
    )
    hotel_id = h_resp.json()["hotel_id"]

    db = TestingSessionLocal()
    rec = PriceRecommendations(
        hotel_id=hotel_id,
        room_type_id=1,
        stay_date=date(2026, 10, 20),
        recommended_rate=6200.0,
        min_rate=4500.0,
        max_rate=8000.0,
        current_rate=5000.0,
        occupancy=78.0,
        forecast_demand=90.0,
        competitor_median=6400.0,
        demand_index=1.24,
        price_reason="High demand",
        confidence_score=0.88,
        status="PENDING",
    )
    db.add(rec)
    db.commit()
    rec_id = rec.recommendation_id
    db.close()

    # 2. Submit Feedback
    fb_resp = client.post(
        f"/api/v1/hotels/{hotel_id}/feedback",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "recommendation_id": rec_id,
            "accepted": True,
            "comments": "Good rate recommendation during Tech Summit.",
            "actual_result": {"actual_occupancy": 82.5, "actual_adr": 6180.0},
        },
    )

    assert fb_resp.status_code == 201
    assert fb_resp.json()["accepted"] is True

    # 3. Query Analytics
    analytics_resp = client.get(
        f"/api/v1/hotels/{hotel_id}/feedback/analytics",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert analytics_resp.status_code == 200
    data = analytics_resp.json()
    assert data["total_recommendations_count"] == 1
    assert data["acceptance_rate_pct"] == 100.0
    assert data["average_actual_occupancy_pct"] == 82.5
