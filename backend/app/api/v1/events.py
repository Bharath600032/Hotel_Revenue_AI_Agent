"""
Events & Holidays REST API endpoints.
"""
import io
import pandas as pd
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.event_holiday import (
    HolidayResponse,
    HolidayCreate,
    EventResponse,
    EventCreate,
    CalendarImpactResponse,
)
from app.models.events import Holidays, Events
from app.events.engine import event_holiday_engine
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="", tags=["Events & Holidays"])


# --- Holidays Endpoints ---
@router.get("/holidays", response_model=List[HolidayResponse])
async def list_holidays(
    country: str = Query("India"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve national/regional holiday calendar."""
    query = db.query(Holidays).filter(Holidays.country.ilike(f"%{country}%"))
    if start_date:
        query = query.filter(Holidays.holiday_date >= start_date)
    if end_date:
        query = query.filter(Holidays.holiday_date <= end_date)
    return query.order_by(Holidays.holiday_date).all()


@router.post("/holidays", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
async def create_holiday(
    payload: HolidayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager"])),
):
    """Create a new holiday record."""
    h = Holidays(**payload.model_dump())
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


# --- Events Endpoints ---
@router.get("/events", response_model=List[EventResponse])
async def list_events(
    city: str = Query(...),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve city events (conferences, festivals, concerts)."""
    query = db.query(Events).filter(Events.city.ilike(f"%{city}%"))
    if start_date:
        query = query.filter(Events.end_date >= start_date)
    if end_date:
        query = query.filter(Events.start_date <= end_date)
    return query.order_by(Events.start_date).all()


@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager"])),
):
    """Create a new city event entry manually."""
    event_data = payload.model_dump()
    if not event_data.get("source"):
        event_data["source"] = "MANUAL"
    e = Events(**event_data)
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


@router.delete("/events/{event_id}", status_code=status.HTTP_200_OK)
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager"])),
):
    """Delete an event entry."""
    e = db.query(Events).filter(Events.event_id == event_id).first()
    if not e:
        raise HTTPException(status_code=404, detail=f"Event ID {event_id} not found")
    db.delete(e)
    db.commit()
    return {"status": "DELETED", "event_id": event_id}


@router.post("/events/upload", status_code=status.HTTP_201_CREATED)
async def upload_events_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager"])),
):
    """
    Bulk upload city events data from Excel (.xlsx, .xls) or CSV (.csv) file.
    Expected columns: Event Name, City, Start Date, End Date, Event Type, Expected Attendance, Venue, Importance.
    """
    filename = file.filename.lower() if file.filename else ""
    if not (filename.endswith(".xlsx") or filename.endswith(".xls") or filename.endswith(".csv")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload an Excel (.xlsx, .xls) or CSV (.csv) file."
        )

    try:
        contents = await file.read()
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse uploaded Excel/CSV file: {str(err)}"
        )

    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded Excel file contains no data rows."
        )

    # Normalize column names for flexible header matching
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    def get_val(row, keys: List[str], default=None):
        for k in keys:
            if k in row and pd.notna(row[k]):
                return row[k]
        return default

    created_events = []
    skipped_count = 0

    for idx, row in df.iterrows():
        event_name = get_val(row, ["event_name", "event", "name", "title"])
        city = get_val(row, ["city", "location", "town"])
        start_date_val = get_val(row, ["start_date", "start", "from_date", "date"])
        end_date_val = get_val(row, ["end_date", "end", "to_date"])

        if not event_name or not city or not start_date_val:
            skipped_count += 1
            continue

        if not end_date_val:
            end_date_val = start_date_val

        try:
            start_dt = pd.to_datetime(start_date_val).date()
            end_dt = pd.to_datetime(end_date_val).date()
        except Exception:
            skipped_count += 1
            continue

        event_type = str(get_val(row, ["event_type", "type", "category"], default="CONFERENCE")).upper()
        attendance_raw = get_val(row, ["expected_attendance", "attendance", "capacity", "count"])
        try:
            attendance = int(attendance_raw) if attendance_raw is not None and pd.notna(attendance_raw) else None
        except Exception:
            attendance = None

        venue = str(get_val(row, ["venue", "location_detail"], default="")) or None
        importance_raw = get_val(row, ["importance", "impact", "score"])
        try:
            importance = int(importance_raw) if importance_raw is not None and pd.notna(importance_raw) else 3
        except Exception:
            importance = 3

        event_obj = Events(
            city=str(city).strip(),
            event_name=str(event_name).strip(),
            event_type=event_type,
            start_date=start_dt,
            end_date=end_dt,
            expected_attendance=attendance,
            venue=venue,
            importance=min(5, max(1, importance)),
            source="EXCEL_UPLOAD",
        )
        db.add(event_obj)
        created_events.append(event_obj)

    db.commit()

    return {
        "status": "SUCCESS",
        "total_inserted": len(created_events),
        "skipped_rows": skipped_count,
        "total_rows_processed": len(df),
        "message": f"Successfully imported {len(created_events)} events from '{file.filename}'."
    }


# --- Calendar Impact Endpoint ---
@router.get("/hotels/{hotel_id}/calendar-impact", response_model=CalendarImpactResponse)
async def get_calendar_impact(
    hotel_id: int,
    stay_date: date = Query(..., description="Target stay date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Evaluate combined holiday and event demand multiplier for property and stay date."""
    verify_hotel_access(hotel_id, current_user)
    return event_holiday_engine.evaluate_calendar_impact(db, hotel_id=hotel_id, stay_date=stay_date)
