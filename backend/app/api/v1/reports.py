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


@router.get("/documentation")
async def download_documentation(
    format: str = Query("html", description="Download format: 'html' or 'md'"),
):
    """Download full application documentation as a standalone HTML or Markdown file."""
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    if format.lower() in ("md", "markdown"):
        target_path = os.path.join(base_dir, "DOCUMENTATION.md")
        filename = "Hotel_Revenue_AI_Agent_Documentation.md"
        media_type = "text/markdown; charset=utf-8"
    else:
        target_path = os.path.join(base_dir, "DOCUMENTATION.html")
        filename = "Hotel_Revenue_AI_Agent_Documentation.html"
        media_type = "text/html; charset=utf-8"

    if not os.path.exists(target_path):
        # Fallback to docs/ folder
        target_path = os.path.join(base_dir, "docs", "COMPLETE_APPLICATION_DOCUMENTATION.md" if format.lower() in ("md", "markdown") else "DOCUMENTATION.html")

    if not os.path.exists(target_path):
        return Response(content="Documentation file not found.", status_code=404)

    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "Content-Type": media_type,
    }
    return Response(content=content, media_type=media_type, headers=headers)

