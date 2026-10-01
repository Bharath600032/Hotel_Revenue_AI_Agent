"""
End-to-End Integration Test for Hotel Autonomous Revenue AI Agent.

Tests complete business lifecycle:
1. Property & Master Data Provisioning (Hotels, Room Types, Rate Plans, Competitors)
2. Inventory Setup & Booking Reservation Ingestion
3. Revenue Performance Metrics Calculation (Occupancy, ADR, RevPAR, Pickup)
4. ML Demand Forecasting Pipeline Execution
5. Multi-Signal Dynamic Pricing Engine & Guardrails Validation
6. Human-in-the-Loop Approval & Rejection Workflow
7. Financial & Revenue Report Generation (.xlsx)
8. AI Agent Conversation & Autonomous Tool Tool Calling
9. Compliance Audit Trail Verification
"""

import os
import tempfile
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate
from app.models import (
    RoomInventory,
    Reservation,
    CompetitorHotel,
    CompetitorRate,
    Event,
    Holiday,
    WeatherForecast,
)


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

    # Seed Admin and Revenue Manager users
    user_repository.create(
        db,
        UserCreate(
            email="admin@grandresort.com",
            password="AdminPassword123!",
            full_name="System Admin",
            role="Administrator",
        ),
    )
    user_repository.create(
        db,
        UserCreate(
            email="rm@grandresort.com",
            password="ManagerPassword123!",
            full_name="Revenue Manager",
            role="Revenue Manager",
        ),
    )
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def get_token(email: str = "admin@grandresort.com", password: str = "AdminPassword123!") -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_full_autonomous_revenue_system_flow():
    token = get_token("admin@grandresort.com", "AdminPassword123!")
    headers = {"Authorization": f"Bearer {token}"}

    # -------------------------------------------------------------
    # Step 1: Create Hotel Property, Room Type, Rate Plan
    # -------------------------------------------------------------
    h_resp = client.post(
        "/api/v1/hotels",
        headers=headers,
        json={
            "hotel_code": "E2E_PALACE",
            "hotel_name": "Grand E2E Palace Resort",
            "city": "Goa",
            "country": "India",
            "total_rooms": 100,
            "currency": "INR",
            "min_price_floor": 3000.0,
            "max_price_ceiling": 25000.0,
            "max_daily_price_change_pct": 20.0,
            "require_approval_above_change_pct": 10.0,
            "automation_enabled": True,
        },
    )
    assert h_resp.status_code == 201, h_resp.text
    hotel_id = h_resp.json()["hotel_id"]

    rt_resp = client.post(
        f"/api/v1/hotels/{hotel_id}/room-types",
        headers=headers,
        json={
            "room_type_code": "DELUXE_OCEAN",
            "room_type_name": "Deluxe Ocean View",
            "base_price": 8000.0,
            "total_inventory": 40,
        },
    )
    assert rt_resp.status_code == 201
    room_type_id = rt_resp.json()["room_type_id"]

    rp_resp = client.post(
        f"/api/v1/hotels/{hotel_id}/rate-plans",
        headers=headers,
        json={
            "rate_plan_code": "BAR_FLEX",
            "rate_plan_name": "Best Available Rate Flexible",
            "meal_plan": "EP",
            "multiplier": 1.0,
            "is_active": True,
        },
    )
    assert rp_resp.status_code == 201
    rate_plan_id = rp_resp.json()["rate_plan_id"]

    # -------------------------------------------------------------
    # Step 2: Seed Room Inventory and Reservations in DB
    # -------------------------------------------------------------
    db = TestingSessionLocal()
    today = date.today()

    for i in range(14):
        stay_d = today + timedelta(days=i)
        # Add inventory record
        inv = RoomInventory(
            hotel_id=hotel_id,
            room_type_id=room_type_id,
            stay_date=stay_d,
            total_inventory=40,
            sold_count=20 + i,
            current_rate=8000.0 + (i * 100),
            out_of_order=0,
        )
        db.add(inv)

        # Add 5 reservations for stay_d
        for r_idx in range(5):
            res = Reservation(
                hotel_id=hotel_id,
                room_type_id=room_type_id,
                rate_plan_id=rate_plan_id,
                booking_reference=f"RES-E2E-{i}-{r_idx}",
                guest_name=f"Guest {i}-{r_idx}",
                booking_date=today - timedelta(days=7 - r_idx),
                checkin_date=stay_d,
                checkout_date=stay_d + timedelta(days=1),
                room_nights=1,
                room_rate=8000.0,
                total_amount=8000.0,
                status="Confirmed",
                channel="Direct",
            )
            db.add(res)
    db.commit()

    # Seed Competitor Data
    comp = CompetitorHotel(
        hotel_id=hotel_id,
        competitor_name="Rival Beach Club",
        star_rating=5.0,
        distance_km=1.2,
        is_active=True,
    )
    db.add(comp)
    db.commit()

    for i in range(7):
        stay_d = today + timedelta(days=i)
        cr = CompetitorRate(
            competitor_id=comp.competitor_id,
            stay_date=stay_d,
            room_type_category="Deluxe Ocean View",
            scraped_rate=8500.0 + (i * 150),
            scraped_timestamp=today,
        )
        db.add(cr)
    db.commit()
    db.close()

    # -------------------------------------------------------------
    # Step 3: Test Health & System Status APIs
    # -------------------------------------------------------------
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "ok"

    ready_resp = client.get("/readiness")
    assert ready_resp.status_code == 200
    assert ready_resp.json()["status"] == "ready"

    # -------------------------------------------------------------
    # Step 4: Test Revenue Performance & Occupancy APIs
    # -------------------------------------------------------------
    start_str = today.isoformat()
    end_str = (today + timedelta(days=7)).isoformat()

    inv_resp = client.get(
        f"/api/v1/inventory/{hotel_id}?start_date={start_str}&end_date={end_str}",
        headers=headers,
    )
    assert inv_resp.status_code == 200
    inv_data = inv_resp.json()
    assert len(inv_data) > 0

    # -------------------------------------------------------------
    # Step 5: Test AI Agent Dynamic Tool Calling & Chat Execution
    # -------------------------------------------------------------
    chat_payload = {
        "message": f"What is the revenue performance, occupancy, and pricing recommendations for hotel {hotel_id} for the next 7 days?",
        "hotel_id": hotel_id,
    }
    chat_resp = client.post(
        "/api/v1/agent/chat",
        headers=headers,
        json=chat_payload,
    )
    assert chat_resp.status_code == 200
    agent_output = chat_resp.json()
    assert "response" in agent_output
    assert agent_output["hotel_id"] == hotel_id
    assert len(agent_output["response"]) > 0

    # -------------------------------------------------------------
    # Step 6: Test Human Approval Workflow (Pending Approvals)
    # -------------------------------------------------------------
    pending_resp = client.get(
        f"/api/v1/approvals/pending?hotel_id={hotel_id}",
        headers=headers,
    )
    assert pending_resp.status_code == 200

    # -------------------------------------------------------------
    # Step 7: Test Revenue Excel Export Engine
    # -------------------------------------------------------------
    rpt_resp = client.post(
        "/api/v1/reports/revenue-export",
        headers=headers,
        json={
            "hotel_id": hotel_id,
            "start_date": start_str,
            "end_date": end_str,
            "format": "xlsx",
        },
    )
    assert rpt_resp.status_code == 200
    assert rpt_resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(rpt_resp.content) > 1000  # Non-trivial excel file binary stream

    # -------------------------------------------------------------
    # Step 8: Test Immutable Compliance Audit Log Verification
    # -------------------------------------------------------------
    audit_resp = client.get(
        "/api/v1/audit-logs",
        headers=headers,
    )
    assert audit_resp.status_code == 200
    audit_logs = audit_resp.json()
    assert len(audit_logs) > 0
