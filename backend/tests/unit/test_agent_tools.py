"""
Unit tests for Agent Tools and Central Tool Registry.
"""
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import Hotel, RoomType
from app.tools.registry import tool_registry


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def test_registry_contains_22_tools():
    tools = tool_registry.list_tools()
    assert len(tools) == 22

    tool_names = {t.name for t in tools}
    expected_names = {
        "get_hotel_profile",
        "get_room_types",
        "get_inventory",
        "get_reservations",
        "get_booking_pace",
        "calculate_occupancy",
        "calculate_adr",
        "calculate_revpar",
        "get_historical_rates",
        "get_holiday_data",
        "get_event_data",
        "get_competitor_rates",
        "get_weather",
        "run_demand_forecast",
        "calculate_pricing_recommendation",
        "validate_price_guardrails",
        "get_hotel_policies",
        "search_knowledge_base",
        "generate_revenue_report",
        "export_recommendations",
        "request_human_approval",
        "record_feedback",
    }
    assert expected_names.issubset(tool_names)


def test_execute_hotel_profile_tool(db_session):
    hotel = Hotel(hotel_code="HTL_TOOL", hotel_name="Tool Test Hotel", city="Goa", total_rooms=80)
    db_session.add(hotel)
    db_session.commit()

    res = tool_registry.execute_tool(
        db_session,
        tool_name="get_hotel_profile",
        arguments={"hotel_id": hotel.hotel_id},
    )

    assert res["status"] == "SUCCESS"
    assert res["result"]["hotel_name"] == "Tool Test Hotel"
    assert res["result"]["city"] == "Goa"


def test_execute_pricing_recommendation_tool(db_session):
    hotel = Hotel(hotel_code="HTL_REC_TOOL", hotel_name="Rec Tool Hotel", city="Goa", total_rooms=100)
    db_session.add(hotel)
    db_session.commit()

    rt = RoomType(
        hotel_id=hotel.hotel_id,
        room_type_code="DELUXE",
        room_type_name="Deluxe Room",
        base_price=5000.0,
    )
    db_session.add(rt)
    db_session.commit()

    res = tool_registry.execute_tool(
        db_session,
        tool_name="calculate_pricing_recommendation",
        arguments={
            "hotel_id": hotel.hotel_id,
            "room_type_id": rt.room_type_id,
            "stay_date": "2026-10-20",
        },
    )

    assert res["status"] == "SUCCESS"
    assert "recommended_rate" in res["result"]
    assert res["result"]["recommended_rate"] > 0
