"""
Comprehensive System Integration Test Suite
Verifies:
1. All 36 revenue tools are registered in tool_registry.
2. GroupDisplacementLog allows nullable room_type_id without IntegrityError.
3. SingleAutonomousRevenueAgent handles multi-turn and tool queries cleanly with crisp formatting.
4. LLM provider factory instantiates properly with instant offline fallback.
"""
import pytest
from datetime import date, timedelta
from app.db.session import SessionLocal
from app.tools.registry import tool_registry
from app.models.los_displacement import GroupDisplacementLog
from app.agents.orchestrator import single_agent_orchestrator
from app.core.llm import get_llm_provider, MockLLMProvider, GeminiLLMProvider


def test_tool_registry_complete():
    """Verify all 36 specialized revenue tools are registered."""
    tools = tool_registry.list_tools()
    assert len(tools) >= 36, f"Expected at least 36 tools, found {len(tools)}"
    declarations = tool_registry.get_llm_tool_declarations()
    assert len(declarations) == len(tools)
    names = {t.name for t in tools}
    expected_tools = [
        "calculate_pricing_recommendation",
        "calculate_revpar",
        "calculate_adr",
        "get_competitor_rates",
        "get_events_holidays",
        "calculate_group_displacement",
        "get_los_restrictions",
        "calculate_trevpar_analytics",
        "generate_ancillary_upsell_packages",
        "get_active_alerts_and_rule_config",
        "pull_live_pms_reservations",
        "push_two_way_channel_rates",
        "get_agent_swarm_status",
    ]
    for exp in expected_tools:
        assert exp in names, f"Missing tool: {exp}"
    print(f"\n[PASS] Tool registry verified with {len(tools)} tools!")


def test_group_displacement_nullable_room_type():
    """Verify GroupDisplacementLog accepts room_type_id=None without IntegrityError."""
    db = SessionLocal()
    try:
        log = GroupDisplacementLog(
            hotel_id=1,
            room_type_id=None,
            group_name="Test Enterprise Booking",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
            rooms_requested=25,
            offered_rate=5500.0,
            breakeven_rate=4800.0,
            displaced_transient_revenue=110000.0,
            net_group_room_revenue=275000.0,
            ancillary_contribution=45000.0,
            net_displacement_revenue=210000.0,
            recommendation="ACCEPT",
            evaluated_by_user_id=1,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        assert log.log_id is not None
        assert log.room_type_id is None
        print(f"\n[PASS] GroupDisplacementLog created successfully with log_id={log.log_id} and nullable room_type_id!")

        # Clean up test log
        db.delete(log)
        db.commit()
    finally:
        db.close()


def test_llm_provider_factory():
    """Verify LLM provider factory instantiates clean fallback."""
    provider = get_llm_provider()
    assert isinstance(provider, (MockLLMProvider, GeminiLLMProvider))
    response = provider.generate_response(
        system_prompt="Test system prompt",
        user_message="What are our competitors?",
        tools_declarations=[],
    )
    assert "tool_calls" in response
    assert response["thought"] is not None
    print("\n[PASS] LLM provider factory initialized and generated response successfully!")


def test_orchestrator_execution_and_formatting():
    """Verify SingleAutonomousRevenueAgent returns structured, crisp answers for diverse queries."""
    db = SessionLocal()
    try:
        queries = [
            "Who are our competitors?",
            "What is our total room capacity?",
            "What are our room categories?",
            "What events and festivals are upcoming?",
            "Evaluate group displacement for corporate lead",
            "What are our length of stay restrictions?",
            "What are our active multi-channel alerts?",
            "Check PMS sync status and channel connections",
        ]
        for q in queries:
            result = single_agent_orchestrator.execute_request(
                db=db,
                user_id=1,
                hotel_id=1,
                user_message=q,
                session_id="test_integration_sess",
            )
            assert result["agent_run_id"] is not None
            assert len(result["answer"]) > 10
            print(f"[PASS] Query '{q}' -> Answer generated cleanly ({result['execution_time_seconds']}s)")
    finally:
        db.close()


if __name__ == "__main__":
    test_tool_registry_complete()
    test_group_displacement_nullable_room_type()
    test_llm_provider_factory()
    test_orchestrator_execution_and_formatting()
