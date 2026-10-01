"""
Competitor Intelligence REST API endpoints.
"""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.competitor import (
    CompetitorHotelResponse,
    CompetitorHotelCreate,
    CompetitorRateResponse,
    CompetitorRateCreate,
    CompetitorAnalysisResponse,
)
from app.models.rates import CompetitorHotels, CompetitorRates
from app.competitors.engine import competitor_engine
from app.api.deps import get_current_user, require_roles, verify_hotel_access
from app.models.user import User

router = APIRouter(prefix="/hotels/{hotel_id}/competitors", tags=["Competitor Intelligence"])


@router.get("", response_model=List[CompetitorHotelResponse])
async def list_competitor_hotels(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Retrieve list of registered competitor hotels for property."""
    verify_hotel_access(hotel_id, current_user)
    from app.agents.hotel_agent_factory import hotel_agent_factory
    hotel_agent_factory.ensure_hotel_live_data(db, hotel_id)
    return db.query(CompetitorHotels).filter(CompetitorHotels.hotel_id == hotel_id).all()


@router.post("", response_model=CompetitorHotelResponse, status_code=status.HTTP_201_CREATED)
async def add_competitor_hotel(
    hotel_id: int,
    payload: CompetitorHotelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager"])),
):
    """Add a new competitor hotel to the property's competitive set."""
    verify_hotel_access(hotel_id, current_user)
    comp = CompetitorHotels(hotel_id=hotel_id, **payload.model_dump())
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return comp


@router.put("/{competitor_id}", response_model=CompetitorHotelResponse)
async def update_competitor_hotel(
    hotel_id: int,
    competitor_id: int,
    payload: CompetitorHotelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager"])),
):
    """Update competitor hotel details."""
    verify_hotel_access(hotel_id, current_user)
    comp = db.query(CompetitorHotels).filter(
        CompetitorHotels.hotel_id == hotel_id,
        CompetitorHotels.competitor_id == competitor_id
    ).first()
    if not comp:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Competitor ID {competitor_id} not found")
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(comp, field, value)
    db.commit()
    db.refresh(comp)
    return comp


@router.delete("/{competitor_id}", status_code=status.HTTP_200_OK)
async def delete_competitor_hotel(
    hotel_id: int,
    competitor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager"])),
):
    """Delete a competitor hotel from compset."""
    verify_hotel_access(hotel_id, current_user)
    comp = db.query(CompetitorHotels).filter(
        CompetitorHotels.hotel_id == hotel_id,
        CompetitorHotels.competitor_id == competitor_id
    ).first()
    if not comp:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Competitor ID {competitor_id} not found")
    
    # Delete associated competitor rates
    db.query(CompetitorRates).filter(CompetitorRates.competitor_id == competitor_id).delete()
    db.delete(comp)
    db.commit()
    return {"status": "DELETED", "competitor_id": competitor_id}



@router.post("/rates", response_model=CompetitorRateResponse, status_code=status.HTTP_201_CREATED)
async def ingest_competitor_rate(
    hotel_id: int,
    payload: CompetitorRateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager"])),
):
    """Ingest a competitor rate record."""
    verify_hotel_access(hotel_id, current_user)
    rate_rec = CompetitorRates(**payload.model_dump())
    db.add(rate_rec)
    db.commit()
    db.refresh(rate_rec)
    return rate_rec


@router.post("/sync-google-rates")
async def sync_google_competitor_rates(
    hotel_id: int,
    stay_date: Optional[date] = Query(None, description="Target stay date to fetch Google rates for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Super Admin", "Administrator", "Revenue Manager", "Hotel Manager"])),
):
    """Fetch live competitor room rates from Google Search & Travel for all active competitors of the property."""
    verify_hotel_access(hotel_id, current_user)
    from app.competitors.google_scraper import google_hotel_scraper
    synced = google_hotel_scraper.sync_google_rates_for_hotel(db, hotel_id=hotel_id, stay_date=stay_date)
    return {
        "status": "SUCCESS",
        "hotel_id": hotel_id,
        "stay_date": (stay_date or date.today()).isoformat(),
        "synced_count": len(synced),
        "rates": synced,
        "message": f"Successfully fetched live Google rates for {len(synced)} competitor properties.",
    }


@router.get("/analysis", response_model=CompetitorAnalysisResponse)
async def get_competitor_analysis(
    hotel_id: int,
    stay_date: date = Query(..., description="Target stay date"),
    my_rate: float = Query(..., gt=0.0, description="Hotel's current rate for comparison"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Analyze competitive set median, min, max, price gap %, and detect data anomalies."""
    verify_hotel_access(hotel_id, current_user)
    return competitor_engine.analyze_market_rates(
        db, hotel_id=hotel_id, stay_date=stay_date, my_rate=my_rate
    )

