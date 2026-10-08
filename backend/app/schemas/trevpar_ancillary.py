"""
Pydantic v2 schemas for Total Revenue Management (TRevPAR) & Non-Room Revenue Streams.
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict


class AncillaryCategoryBreakdown(BaseModel):
    category: str  # Food & Beverage, Spa & Wellness, Banquets & Events, Parking, Laundry, Miscellaneous
    revenue_amount: float
    percentage_of_total_ancillary: float
    revpor: float  # Ancillary Revenue Per Occupied Room
    cover_count: int


class TRevPARSummaryResponse(BaseModel):
    hotel_id: int
    start_date: str
    end_date: str
    total_sellable_rooms: int
    total_occupied_rooms: int
    occupancy_pct: float
    
    # Financial metrics in INR (₹)
    room_revenue: float
    total_ancillary_revenue: float
    total_gross_revenue: float
    
    adr: float  # Average Daily Rate
    revpar: float  # Revenue Per Available Room
    trevpar: float  # Total Revenue Per Available Room
    nrevpar: float  # Net RevPAR (after commissions/distribution costs)
    revpor: float  # Revenue Per Occupied Room (Room + Non-Room)
    ancillary_revpor: float  # Non-Room Revenue Per Occupied Room
    
    distribution_commission_costs: float
    categories_breakdown: List[AncillaryCategoryBreakdown]


class AncillaryPackageRecommendationResponse(BaseModel):
    package_id: int
    hotel_id: int
    package_name: str
    category: str
    description: str
    standalone_price: float  # ₹
    recommended_bundle_price: float  # ₹
    discount_pct: float
    projected_conversion_uplift_pct: float
    expected_trevpar_gain_per_room: float  # ₹
    strategy_reasoning: str


class AncillaryRevenueCreate(BaseModel):
    entry_date: str = Field(..., description="Date YYYY-MM-DD")
    category: str = Field(..., description="FB, SPA, BANQUET, PARKING, LAUNDRY, OTHER")
    sub_category: Optional[str] = Field("General", description="Subcategory description")
    revenue_amount: float = Field(..., ge=0.0, description="Revenue in INR (₹)")
    cover_count: Optional[int] = Field(0, ge=0, description="Covers / Treatments / Guests")
    cost_of_sales: Optional[float] = Field(0.0, ge=0.0, description="Direct cost of sales (₹)")
    notes: Optional[str] = Field(None, description="Notes or source venue")


class AncillaryRevenueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ancillary_id: int
    hotel_id: int
    entry_date: date
    category: str
    sub_category: Optional[str] = None
    revenue_amount: float
    cover_count: int
    cost_of_sales: float
    notes: Optional[str] = None
    created_at: datetime
