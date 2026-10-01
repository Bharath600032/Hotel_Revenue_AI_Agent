"""
Integration tests for Human Approval Workflow REST API endpoints.
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
from app.models import Hotel, PriceRecommendations, AuditLogs

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


def test_approval_and_override_workflow():
    token = get_token()

    # 1. Create Hotel
    h_resp = client.post(
        "/api/v1/hotels",
        headers={"Authorization": f"Bearer {token}"},
        json={"hotel_code": "HTL_APP", "hotel_name": "Approval Test Hotel", "city": "Goa"},
    )
    hotel_id = h_resp.json()["hotel_id"]

    # 2. Seed Pending Price Recommendation
    db = TestingSessionLocal()
    rec = PriceRecommendations(
        hotel_id=hotel_id,
        room_type_id=1,
        stay_date=date(2026, 10, 20),
        recommended_rate=6500.0,
        min_rate=4500.0,
        max_rate=8000.0,
        current_rate=5000.0,
        occupancy=80.0,
        forecast_demand=90.0,
        competitor_median=6400.0,
        demand_index=1.30,
        price_reason="High demand uplift",
        confidence_score=0.88,
        status="PENDING",
        requires_approval=True,
    )
    db.add(rec)
    db.commit()
    rec_id = rec.recommendation_id
    db.close()

    # 3. Query Pending Approval Queue
    q_resp = client.get(
        f"/api/v1/hotels/{hotel_id}/approvals/pending",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert q_resp.status_code == 200
    assert len(q_resp.json()) == 1

    # 4. Override Recommendation with custom rate ₹6,200
    over_resp = client.post(
        f"/api/v1/hotels/{hotel_id}/approvals/{rec_id}/override",
        headers={"Authorization": f"Bearer {token}"},
        json={"override_rate": 6200.0, "reason": "Competitive positioning adjustment"},
    )
    assert over_resp.status_code == 200
    assert over_resp.json()["status"] == "OVERRIDDEN"
    assert over_resp.json()["final_rate"] == 6200.0

    # 5. Verify Audit Log Entry
    db_verify = TestingSessionLocal()
    audit = db_verify.query(AuditLogs).filter(AuditLogs.action == "OVERRIDE_PRICE_RECOMMENDATION").first()
    assert audit is not None
    assert audit.new_value["override_rate"] == 6200.0
    db_verify.close()
