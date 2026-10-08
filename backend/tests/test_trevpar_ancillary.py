import pytest
from datetime import date, timedelta
from app.db.session import SessionLocal
from app.services.trevpar_service import trevpar_service
from app.tools.registry import tool_registry
from app.schemas.trevpar_ancillary import AncillaryRevenueCreate

def test_trevpar_service_summary():
    db = SessionLocal()
    try:
        today = date.today().strftime("%Y-%m-%d")
        start = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        summary = trevpar_service.calculate_trevpar_summary(db, hotel_id=1, start_date=start, end_date=today)
        assert summary.hotel_id == 1
        assert summary.trevpar > 0
        assert summary.nrevpar > 0
        assert summary.revpor > 0
        assert len(summary.categories_breakdown) >= 5
        print("\n[PASS] TRevPAR service summary test passed! TRevPAR: ₹", summary.trevpar)
    finally:
        db.close()

def test_trevpar_ancillary_logging_and_packages():
    db = SessionLocal()
    try:
        today = date.today().strftime("%Y-%m-%d")
        entry_req = AncillaryRevenueCreate(
            entry_date=today,
            category="FB",
            sub_category="Specialty Dining Bar",
            revenue_amount=25000.0,
            cover_count=60,
            cost_of_sales=6000.0,
            notes="Test F&B Entry"
        )
        res_entry = trevpar_service.record_ancillary_entry(db, hotel_id=1, req=entry_req)
        assert res_entry.ancillary_id > 0
        assert res_entry.revenue_amount == 25000.0
        print("[PASS] Record ancillary revenue entry passed! Ancillary ID:", res_entry.ancillary_id)

        pkgs = trevpar_service.generate_ancillary_packages(db, hotel_id=1)
        assert len(pkgs) >= 3
        print("[PASS] Generate AI ancillary packages passed! Count:", len(pkgs))
    finally:
        db.close()

def test_trevpar_agent_tools():
    db = SessionLocal()
    try:
        today = date.today().strftime("%Y-%m-%d")
        start = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Tool 25: calculate_trevpar_analytics
        tool25 = tool_registry.get_tool("calculate_trevpar_analytics")
        res25 = tool25.execute(db, hotel_id=1, start_date=start, end_date=today)
        assert "trevpar" in res25
        assert "categories_breakdown" in res25
        print("[PASS] Tool 25 (calculate_trevpar_analytics) executed cleanly!")

        # Tool 26: generate_ancillary_upsell_packages
        tool26 = tool_registry.get_tool("generate_ancillary_upsell_packages")
        res26 = tool26.execute(db, hotel_id=1)
        assert "ancillary_packages" in res26
        print("[PASS] Tool 26 (generate_ancillary_upsell_packages) executed cleanly!")
    finally:
        db.close()

if __name__ == "__main__":
    test_trevpar_service_summary()
    test_trevpar_ancillary_logging_and_packages()
    test_trevpar_agent_tools()
