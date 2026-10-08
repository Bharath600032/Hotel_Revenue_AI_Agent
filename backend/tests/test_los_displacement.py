import pytest
from datetime import date, timedelta
from app.db.session import SessionLocal
from app.services.los_displacement_service import los_displacement_service
from app.tools.registry import tool_registry
from app.schemas.los_displacement import GroupDisplacementRequest

def test_group_displacement_service_acceptance():
    db = SessionLocal()
    try:
        today = date.today().strftime("%Y-%m-%d")
        end_date = (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")
        
        req = GroupDisplacementRequest(
            hotel_id=1,
            group_name="Tech Conference Group",
            start_date=today,
            end_date=end_date,
            rooms_requested=10,
            offered_rate=3500.0,
            f_and_b_revenue=85000.0,
            meeting_room_rental=45000.0,
            other_ancillary_revenue=15000.0
        )
        
        result = los_displacement_service.evaluate_group_displacement(db, hotel_id=1, req=req, user_id=1)
        assert result.hotel_id == 1
        assert result.total_nights == 3
        assert result.total_room_nights_requested == 30
        assert result.offered_group_rate == 3500.0
        assert result.breakeven_group_rate >= 0
        assert result.recommendation in ['ACCEPT', 'REJECT', 'COUNTER_OFFER']
        assert len(result.daily_breakdown) == 3
        print("\n[PASS] Group displacement service test passed successfully! Recommendation:", result.recommendation)
    finally:
        db.close()

def test_group_displacement_tools():
    db = SessionLocal()
    try:
        # Test Tool 23: CalculateGroupDisplacementTool
        tool23 = tool_registry.get_tool("calculate_group_displacement")
        today = date.today().strftime("%Y-%m-%d")
        end_date = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        res23 = tool23.execute(
            db,
            hotel_id=1,
            group_name="Summit Lead",
            checkin_date=today,
            checkout_date=end_date,
            rooms_requested=15,
            offered_rate=4500.0
        )
        assert "recommendation" in res23
        assert "breakeven_group_rate" in res23
        print("\n[PASS] Tool 23 (calculate_group_displacement) executed cleanly!")

        # Test Tool 24: GetLOSRestrictionsTool
        tool24 = tool_registry.get_tool("get_los_restrictions")
        res24 = tool24.execute(
            db,
            hotel_id=1,
            start_date=today,
            days=14
        )
        assert "los_rules" in res24
        assert len(res24["los_rules"]) >= 1
        print("\n[PASS] Tool 24 (get_los_restrictions) executed cleanly!")
    finally:
        db.close()

if __name__ == "__main__":
    test_group_displacement_service_acceptance()
    test_group_displacement_tools()
