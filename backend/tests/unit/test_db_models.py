"""
Unit tests for SQLAlchemy 2.0 ORM models and schema constraints.
"""
import pytest
from datetime import date, datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models import (
    User,
    Hotel,
    RoomType,
    RatePlan,
    RoomInventory,
    Reservation,
    CompetitorHotels,
    CompetitorRates,
    Holidays,
    Events,
    Weather,
    Forecasts,
    PriceRecommendations,
    AgentRuns,
    AgentToolCalls,
    AuditLogs,
    ModelRegistry,
    Feedback,
)


@pytest.fixture
def db_session():
    """In-memory SQLite session fixture for isolated database testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_create_hotel_and_room_types(db_session):
    """Test creating a hotel with room types and rate plans."""
    hotel = Hotel(
        hotel_code="HTL001",
        hotel_name="Grand Palace Resort",
        city="Goa",
        country="India",
        currency="INR",
        total_rooms=120,
    )
    db_session.add(hotel)
    db_session.commit()
    db_session.refresh(hotel)

    assert hotel.hotel_id is not None

    room_type = RoomType(
        hotel_id=hotel.hotel_id,
        room_type_code="DELUXE",
        room_type_name="Deluxe Sea View Room",
        base_price=5500.0,
        total_inventory=30,
    )
    db_session.add(room_type)
    db_session.commit()
    db_session.refresh(room_type)

    assert room_type.room_type_id is not None
    assert room_type.hotel.hotel_name == "Grand Palace Resort"


def test_create_price_recommendation_and_audit(db_session):
    """Test creating a price recommendation and audit log entry."""
    rec = PriceRecommendations(
        hotel_id=1,
        room_type_id=1,
        stay_date=date(2026, 10, 20),
        recommended_rate=6200.0,
        min_rate=4500.0,
        max_rate=8000.0,
        current_rate=5000.0,
        occupancy=78.5,
        forecast_demand=92.0,
        competitor_median=6400.0,
        price_reason="High demand + strong pickup pace + competitor positioning",
        confidence_score=0.89,
        requires_approval=True,
    )
    db_session.add(rec)
    db_session.commit()

    assert rec.recommendation_id is not None
    assert rec.status == "PENDING"
    assert rec.requires_approval is True

    audit = AuditLogs(
        user_id=1,
        action="CREATE_RECOMMENDATION",
        entity_type="PriceRecommendation",
        entity_id=str(rec.recommendation_id),
        new_value={"recommended_rate": 6200.0},
    )
    db_session.add(audit)
    db_session.commit()

    assert audit.audit_id is not None
    assert audit.action == "CREATE_RECOMMENDATION"
