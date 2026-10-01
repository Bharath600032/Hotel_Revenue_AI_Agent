"""
Unit tests for 3-tier Agent Memory Manager.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import Hotel
from app.agents.memory import agent_memory_manager


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


def test_short_term_memory_truncation():
    sess_id = "test_sess_1"
    agent_memory_manager.clear_short_term_memory(sess_id)

    # Add 12 turns
    for i in range(12):
        agent_memory_manager.add_conversation_turn(sess_id, "user", f"Message {i}")

    history = agent_memory_manager.get_conversation_history(sess_id)
    # Should be capped at 10 items
    assert len(history) == 10
    assert history[0]["content"] == "Message 2"
    assert history[-1]["content"] == "Message 11"


def test_operational_memory_retrieval(db_session):
    hotel = Hotel(hotel_code="HTL_MEM", hotel_name="Memory Hotel", city="Goa", currency="INR")
    db_session.add(hotel)
    db_session.commit()

    op_mem = agent_memory_manager.get_hotel_operational_memory(db_session, hotel.hotel_id)
    assert op_mem["hotel_name"] == "Memory Hotel"
    assert op_mem["preferred_price_floor"] == 1000.0

    prompt = agent_memory_manager.build_memory_context_prompt(db_session, "test_sess_2", hotel.hotel_id)
    assert "Memory Hotel" in prompt
    assert "Price Floor Limit" in prompt
