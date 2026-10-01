"""
Unit and Integration tests for Single Autonomous Revenue AI Agent Orchestrator.
"""
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import Hotel, RoomType, User, AgentRuns, AgentToolCalls
from app.agents.orchestrator import single_agent_orchestrator


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


def test_agent_orchestrator_execution(db_session):
    # Setup test User & Hotel
    user = User(email="testagent@hotel.com", password_hash="pass", full_name="Agent Test User")
    hotel = Hotel(hotel_code="HTL_AGENT", hotel_name="Agent Test Hotel", city="Goa")
    db_session.add_all([user, hotel])
    db_session.commit()

    rt = RoomType(hotel_id=hotel.hotel_id, room_type_code="DELUXE", room_type_name="Deluxe Room", base_price=5000.0)
    db_session.add(rt)
    db_session.commit()

    # Execute Agent Request
    result = single_agent_orchestrator.execute_request(
        db_session,
        user_id=user.user_id,
        hotel_id=hotel.hotel_id,
        user_message="What should the Deluxe Room rate be for 20 October 2026?",
    )

    assert "agent_run_id" in result
    assert result["agent_run_id"].startswith("run_")
    assert "answer" in result
    assert isinstance(result["tools_used"], list)
    assert len(result["tools_used"]) >= 1

    # Verify Database Tracking
    db_run = db_session.query(AgentRuns).filter(AgentRuns.agent_run_id == result["agent_run_id"]).first()
    assert db_run is not None
    assert db_run.status == "COMPLETED"

    tool_calls = db_session.query(AgentToolCalls).filter(AgentToolCalls.agent_run_id == result["agent_run_id"]).all()
    assert len(tool_calls) >= 1
