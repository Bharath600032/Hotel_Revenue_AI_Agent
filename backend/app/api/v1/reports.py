"""
Reports and Excel Export REST API endpoints.
"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.reports.generator import report_generator
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="/exports", tags=["Reports & Exports"])


@router.get("/download")
async def download_pricing_report(
    hotel_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst"])),
):
    """Download executive 365-day pricing recommendations report as a styled Excel file."""
    verify_hotel_access(hotel_id, current_user, db)
    excel_bytes = report_generator.generate_pricing_recommendations_excel(
        db, hotel_id=hotel_id, start_date=start_date, end_date=end_date
    )

    filename = f"Pricing_Recommendations_Hotel_{hotel_id}_{start_date}_to_{end_date}.xlsx"
    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    return Response(content=excel_bytes, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
