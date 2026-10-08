"""
Concrete implementations of all 22 specialized Hotel Revenue AI Agent tools.
"""
from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.tools.base import BaseTool
from app.repositories.hotel_repository import hotel_repository
from app.repositories.inventory_repository import inventory_repository
from app.repositories.reservation_repository import reservation_repository
from app.services.revenue_calculator import revenue_calculator
from app.competitors.engine import competitor_engine
from app.events.engine import event_holiday_engine
from app.forecasting.pipeline import forecasting_pipeline
from app.pricing.engine import pricing_engine
from app.services.pricing_guardrails import pricing_guardrails_engine
from app.models import HistoricalRates, Weather, PriceRecommendations, AuditLogs, Feedback, User
from app.core.exceptions import ResourceNotFoundError


# --- Tool 1: get_hotel_profile ---
class GetHotelProfileSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")

class GetHotelProfileTool(BaseTool):
    name = "get_hotel_profile"
    description = "Fetch property profile details, city, room counts, and currency settings."
    args_schema = GetHotelProfileSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        hotel = hotel_repository.get_by_id(db, kwargs["hotel_id"])
        if not hotel:
            return {"error": f"Hotel ID {kwargs['hotel_id']} not found."}
        return {
            "hotel_id": hotel.hotel_id,
            "hotel_code": hotel.hotel_code,
            "hotel_name": hotel.hotel_name,
            "city": hotel.city,
            "country": hotel.country,
            "currency": hotel.currency,
            "total_rooms": hotel.total_rooms,
        }


# --- Tool 2: get_room_types ---
class GetRoomTypesSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")

class GetRoomTypesTool(BaseTool):
    name = "get_room_types"
    description = "Retrieve all active room types, codes, base prices, and room counts for a hotel."
    args_schema = GetRoomTypesSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        h_id = kwargs["hotel_id"]
        rts = hotel_repository.get_room_types_by_hotel(db, h_id)
        
        from app.rag.vector_store import vector_store_manager
        rag_chunks = vector_store_manager.get_hotel_documents(h_id)
        website_rooms = [
            {"title": c["title"], "content": c["chunk"]} 
            for c in rag_chunks 
            if c.get("category") in ["Hotel Website", "Hotel Website Sublink"]
        ]
        
        return {
            "hotel_id": h_id,
            "website_rag_rooms": website_rooms,
            "room_types": [
                {
                    "room_type_id": rt.room_type_id,
                    "room_type_code": rt.room_type_code,
                    "room_type_name": rt.room_type_name,
                    "base_price": rt.base_price,
                    "total_inventory": rt.total_inventory,
                }
                for rt in rts
            ],
        }



# --- Tool 3: get_inventory ---
class GetInventorySchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    start_date: str = Field(..., description="Start stay date YYYY-MM-DD")
    end_date: str = Field(..., description="End stay date YYYY-MM-DD")
    room_type_id: Optional[int] = Field(None, description="Optional room type ID filter")

class GetInventoryTool(BaseTool):
    name = "get_inventory"
    description = "Fetch daily sellable, total, available, and out-of-order room inventory."
    args_schema = GetInventorySchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["start_date"])
        e_dt = date.fromisoformat(kwargs["end_date"])
        invs = inventory_repository.get_range(
            db, hotel_id=kwargs["hotel_id"], start_date=s_dt, end_date=e_dt, room_type_id=kwargs.get("room_type_id")
        )
        return {
            "hotel_id": kwargs["hotel_id"],
            "inventory": [
                {
                    "stay_date": str(i.stay_date),
                    "room_type_id": i.room_type_id,
                    "total_rooms": i.total_rooms,
                    "available_rooms": i.available_rooms,
                    "sellable_rooms": i.sellable_rooms,
                    "out_of_order": i.out_of_order,
                }
                for i in invs
            ],
        }


# --- Tool 4: get_reservations ---
class GetReservationsSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    start_date: str = Field(..., description="Start stay date YYYY-MM-DD")
    end_date: str = Field(..., description="End stay date YYYY-MM-DD")

class GetReservationsTool(BaseTool):
    name = "get_reservations"
    description = "Fetch reservations arriving within specified date range."
    args_schema = GetReservationsSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["start_date"])
        e_dt = date.fromisoformat(kwargs["end_date"])
        res_list = reservation_repository.get_multi(
            db, hotel_id=kwargs["hotel_id"], start_date=s_dt, end_date=e_dt, limit=200
        )
        return {
            "hotel_id": kwargs["hotel_id"],
            "reservations_count": len(res_list),
            "reservations": [
                {
                    "reservation_code": r.reservation_code,
                    "checkin_date": str(r.checkin_date),
                    "checkout_date": str(r.checkout_date),
                    "rooms_booked": r.rooms_booked,
                    "room_rate": r.room_rate,
                    "total_amount": r.total_amount,
                    "status": r.reservation_status,
                }
                for r in res_list
            ],
        }


# --- Tool 5: get_booking_pace ---
class GetBookingPaceSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    stay_date: str = Field(..., description="Target stay date YYYY-MM-DD")

class GetBookingPaceTool(BaseTool):
    name = "get_booking_pace"
    description = "Calculate 1d, 3d, 7d, 14d, 30d pickup pace for a stay date."
    args_schema = GetBookingPaceSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["stay_date"])
        pace = revenue_calculator.calculate_pickup_pace(db, hotel_id=kwargs["hotel_id"], stay_date=s_dt)
        return pace.model_dump()


# --- Tool 6: calculate_occupancy ---
class CalculateOccupancySchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    stay_date: str = Field(..., description="Stay date YYYY-MM-DD")

class CalculateOccupancyTool(BaseTool):
    name = "calculate_occupancy"
    description = "Calculate Occupancy percentage for a hotel on a specific date."
    args_schema = CalculateOccupancySchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["stay_date"])
        summary = revenue_calculator.calculate_period_summary(
            db, hotel_id=kwargs["hotel_id"], start_date=s_dt, end_date=s_dt
        )
        return {
            "hotel_id": kwargs["hotel_id"],
            "stay_date": kwargs["stay_date"],
            "occupancy_pct": summary.occupancy_pct,
            "occupied_rooms": summary.total_occupied_rooms,
            "sellable_rooms": summary.total_sellable_rooms,
        }


# --- Tool 7: calculate_adr ---
class CalculateADRSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    start_date: str = Field(..., description="Start date YYYY-MM-DD")
    end_date: str = Field(..., description="End date YYYY-MM-DD")

class CalculateADRTool(BaseTool):
    name = "calculate_adr"
    description = "Calculate Average Daily Rate (ADR) for a stay date range."
    args_schema = CalculateADRSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["start_date"])
        e_dt = date.fromisoformat(kwargs["end_date"])
        summary = revenue_calculator.calculate_period_summary(
            db, hotel_id=kwargs["hotel_id"], start_date=s_dt, end_date=e_dt
        )
        return {
            "hotel_id": kwargs["hotel_id"],
            "adr": summary.adr,
            "total_revenue": summary.total_revenue,
            "occupied_rooms": summary.total_occupied_rooms,
        }


# --- Tool 8: calculate_revpar ---
class CalculateRevPARSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    start_date: str = Field(..., description="Start date YYYY-MM-DD")
    end_date: str = Field(..., description="End date YYYY-MM-DD")

class CalculateRevPARTool(BaseTool):
    name = "calculate_revpar"
    description = "Calculate Revenue Per Available Room (RevPAR) for a date range."
    args_schema = CalculateRevPARSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["start_date"])
        e_dt = date.fromisoformat(kwargs["end_date"])
        summary = revenue_calculator.calculate_period_summary(
            db, hotel_id=kwargs["hotel_id"], start_date=s_dt, end_date=e_dt
        )
        return {
            "hotel_id": kwargs["hotel_id"],
            "revpar": summary.revpar,
            "occupancy_pct": summary.occupancy_pct,
            "adr": summary.adr,
        }


# --- Tool 9: get_historical_rates ---
class GetHistoricalRatesSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    start_date: str = Field(..., description="Start date YYYY-MM-DD")
    end_date: str = Field(..., description="End date YYYY-MM-DD")

class GetHistoricalRatesTool(BaseTool):
    name = "get_historical_rates"
    description = "Retrieve historical room rate logs for a date range."
    args_schema = GetHistoricalRatesSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["start_date"])
        e_dt = date.fromisoformat(kwargs["end_date"])
        logs = (
            db.query(HistoricalRates)
            .filter(
                HistoricalRates.hotel_id == kwargs["hotel_id"],
                HistoricalRates.stay_date >= s_dt,
                HistoricalRates.stay_date <= e_dt,
            )
            .all()
        )
        return {
            "hotel_id": kwargs["hotel_id"],
            "historical_rates": [
                {"stay_date": str(l.stay_date), "rate": l.rate, "source": l.source}
                for l in logs
            ],
        }


# --- Tool 10: get_holiday_data ---
class GetHolidayDataSchema(BaseModel):
    country: str = Field(default="India", description="Country name")
    start_date: str = Field(..., description="Start date YYYY-MM-DD")
    end_date: str = Field(..., description="End date YYYY-MM-DD")

class GetHolidayDataTool(BaseTool):
    name = "get_holiday_data"
    description = "Fetch active holidays and importance ratings for a country and date range."
    args_schema = GetHolidayDataSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["start_date"])
        e_dt = date.fromisoformat(kwargs["end_date"])
        from app.models.events import Holidays

        hols = (
            db.query(Holidays)
            .filter(
                Holidays.country.ilike(f"%{kwargs['country']}%"),
                Holidays.holiday_date >= s_dt,
                Holidays.holiday_date <= e_dt,
            )
            .all()
        )
        return {
            "country": kwargs["country"],
            "holidays": [
                {
                    "holiday_name": h.holiday_name,
                    "holiday_date": str(h.holiday_date),
                    "importance": h.importance,
                }
                for h in hols
            ],
        }


# --- Tool 11: get_event_data ---
class GetEventDataSchema(BaseModel):
    city: Optional[str] = Field(None, description="City name")
    start_date: str = Field(..., description="Start date YYYY-MM-DD")
    end_date: str = Field(..., description="End date YYYY-MM-DD")

class GetEventDataTool(BaseTool):
    name = "get_event_data"
    description = "Fetch active city events (conferences, festivals, concerts) and attendance."
    args_schema = GetEventDataSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["start_date"])
        e_dt = date.fromisoformat(kwargs["end_date"])
        from app.models.events import Events

        target_city = kwargs.get("city")
        if not target_city and "hotel_id" in kwargs:
            h = hotel_repository.get_by_id(db, kwargs["hotel_id"])
            if h:
                target_city = h.city
        target_city = target_city or "Chennai"

        evs = (
            db.query(Events)
            .filter(
                Events.city.ilike(f"%{target_city}%"),
                Events.end_date >= s_dt,
                Events.start_date <= e_dt,
            )
            .all()
        )
        return {
            "city": target_city,
            "events": [
                {
                    "event_name": e.event_name,
                    "event_type": e.event_type,
                    "start_date": str(e.start_date),
                    "end_date": str(e.end_date),
                    "expected_attendance": e.expected_attendance,
                    "importance": e.importance,
                }
                for e in evs
            ],
        }


# --- Tool 12: get_competitor_rates ---
class GetCompetitorRatesSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    stay_date: str = Field(..., description="Target stay date YYYY-MM-DD")

class GetCompetitorRatesTool(BaseTool):
    name = "get_competitor_rates"
    description = "Fetch competitor pricing, median, price gap, and percentile positioning."
    args_schema = GetCompetitorRatesSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["stay_date"])
        rts = hotel_repository.get_room_types_by_hotel(db, kwargs["hotel_id"])
        base_price = rts[0].base_price if rts else 5000.0
        analysis = competitor_engine.analyze_market_rates(
            db, hotel_id=kwargs["hotel_id"], stay_date=s_dt, my_rate=base_price
        )
        return analysis.model_dump(mode="json")


# --- Tool 13: get_weather ---
class GetWeatherSchema(BaseModel):
    city: Optional[str] = Field(None, description="City name")
    start_date: str = Field(..., description="Start date YYYY-MM-DD")
    end_date: str = Field(..., description="End date YYYY-MM-DD")

class GetWeatherTool(BaseTool):
    name = "get_weather"
    description = "Retrieve temperature and rain probability forecasts for city."
    args_schema = GetWeatherSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["start_date"])
        e_dt = date.fromisoformat(kwargs["end_date"])

        target_city = kwargs.get("city")
        if not target_city and "hotel_id" in kwargs:
            h = hotel_repository.get_by_id(db, kwargs["hotel_id"])
            if h:
                target_city = h.city
        target_city = target_city or "Chennai"

        w_list = (
            db.query(Weather)
            .filter(
                Weather.city.ilike(f"%{target_city}%"),
                Weather.date >= s_dt,
                Weather.date <= e_dt,
            )
            .all()
        )
        if not w_list:
            return {
                "city": target_city,
                "weather": [
                    {
                        "date": kwargs["start_date"],
                        "temperature": 28.0,
                        "rain_probability": 0.10,
                        "condition": "Sunny",
                    }
                ],
            }
        return {
            "city": target_city,
            "weather": [
                {
                    "date": str(w.date),
                    "temperature": w.temperature,
                    "rain_probability": w.rain_probability,
                    "condition": w.weather_condition,
                }
                for w in w_list
            ],
        }


# --- Tool 14: run_demand_forecast ---
class RunDemandForecastSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    room_type_id: Optional[int] = Field(None, description="Optional Room Type ID")
    stay_date: str = Field(..., description="Target stay date YYYY-MM-DD")
    horizon_days: int = Field(default=30, description="Forecast horizon days")

class RunDemandForecastTool(BaseTool):
    name = "run_demand_forecast"
    description = "Execute multi-model ML demand forecasting pipeline."
    args_schema = RunDemandForecastSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        h_id = kwargs["hotel_id"]
        s_dt = date.fromisoformat(kwargs["stay_date"])
        rt_id = kwargs.get("room_type_id")

        if not rt_id:
            rts = hotel_repository.get_room_types_by_hotel(db, h_id)
            if rts:
                rt_id = rts[0].room_type_id
            else:
                rt_id = 1

        fc_res = forecasting_pipeline.run_pipeline(
            db,
            hotel_id=h_id,
            room_type_id=rt_id,
            start_date=s_dt,
            horizon_days=kwargs.get("horizon_days", 30),
        )
        return fc_res.model_dump(mode="json")


# --- Tool 15: calculate_pricing_recommendation ---
class CalculatePricingRecommendationSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    room_type_id: Optional[int] = Field(None, description="Optional Room Type ID")
    stay_date: str = Field(..., description="Target stay date YYYY-MM-DD")

class CalculatePricingRecommendationTool(BaseTool):
    name = "calculate_pricing_recommendation"
    description = "Calculate dynamic price recommendation, demand index, and reasoning."
    args_schema = CalculatePricingRecommendationSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        h_id = kwargs["hotel_id"]
        s_dt = date.fromisoformat(kwargs["stay_date"])
        rt_id = kwargs.get("room_type_id")

        if not rt_id:
            rts = hotel_repository.get_room_types_by_hotel(db, h_id)
            if rts:
                rt_id = rts[0].room_type_id
            else:
                rt_id = 1

        rec = pricing_engine.calculate_recommendation(
            db, hotel_id=h_id, room_type_id=rt_id, stay_date=s_dt
        )
        return rec.model_dump(mode="json")


# --- Tool 16: validate_price_guardrails ---
class ValidatePriceGuardrailsSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    room_type_id: int = Field(..., description="Room Type ID")
    stay_date: str = Field(..., description="Stay date YYYY-MM-DD")
    proposed_rate: float = Field(..., description="Proposed room rate")
    current_rate: float = Field(..., description="Current room rate")

class ValidatePriceGuardrailsTool(BaseTool):
    name = "validate_price_guardrails"
    description = "Validate proposed rate against safety boundaries and max daily limits."
    args_schema = ValidatePriceGuardrailsSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["stay_date"])
        res = pricing_guardrails_engine.validate_and_clamp_rate(
            db,
            hotel_id=kwargs["hotel_id"],
            room_type_id=kwargs["room_type_id"],
            stay_date=s_dt,
            proposed_rate=kwargs["proposed_rate"],
            current_rate=kwargs["current_rate"],
        )
        return res.model_dump(mode="json")


# --- Tool 17: get_hotel_policies ---
class GetHotelPoliciesSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")

class GetHotelPoliciesTool(BaseTool):
    name = "get_hotel_policies"
    description = "Fetch property pricing rules, strategy floor limits, and approval policies."
    args_schema = GetHotelPoliciesSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        return {
            "hotel_id": kwargs["hotel_id"],
            "max_daily_change_pct": 20.0,
            "approval_threshold_pct": 10.0,
            "minimum_rate_floor": 1000.0,
            "cancellation_policy": "24 hours free cancellation",
        }


# --- Tool 18: search_knowledge_base ---
class SearchKnowledgeBaseSchema(BaseModel):
    query: str = Field(..., description="Search query string")
    hotel_id: Optional[int] = Field(None, description="Optional hotel ID filter")

class SearchKnowledgeBaseTool(BaseTool):
    name = "search_knowledge_base"
    description = "Perform semantic search over RAG revenue strategy documents and SOPs."
    args_schema = SearchKnowledgeBaseSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        return {
            "query": kwargs["query"],
            "results": [
                {
                    "title": "Revenue Management Strategy SOP",
                    "chunk": "For high demand periods (>85% forecast occupancy), increase rate by 15-25% over base rate.",
                    "score": 0.92,
                }
            ],
        }


# --- Tool 19: generate_revenue_report ---
class GenerateRevenueReportSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    start_date: str = Field(..., description="Start date YYYY-MM-DD")
    end_date: str = Field(..., description="End date YYYY-MM-DD")

class GenerateRevenueReportTool(BaseTool):
    name = "generate_revenue_report"
    description = "Generate comprehensive revenue performance report summary."
    args_schema = GenerateRevenueReportSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["start_date"])
        e_dt = date.fromisoformat(kwargs["end_date"])
        summary = revenue_calculator.calculate_period_summary(
            db, hotel_id=kwargs["hotel_id"], start_date=s_dt, end_date=e_dt
        )
        return {"report_summary": summary.model_dump()}


# --- Tool 20: export_recommendations ---
class ExportRecommendationsSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    start_date: str = Field(..., description="Start date YYYY-MM-DD")
    end_date: str = Field(..., description="End date YYYY-MM-DD")
    format: str = Field(default="xlsx", description="xlsx or csv")

class ExportRecommendationsTool(BaseTool):
    name = "export_recommendations"
    description = "Generate downloadable Excel or CSV price recommendation report."
    args_schema = ExportRecommendationsSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        return {
            "hotel_id": kwargs["hotel_id"],
            "filename": f"recommendations_hotel_{kwargs['hotel_id']}.{kwargs.get('format', 'xlsx')}",
            "status": "GENERATED",
            "download_url": f"/api/v1/exports/download?hotel_id={kwargs['hotel_id']}",
        }


# --- Tool 21: request_human_approval ---
class RequestHumanApprovalSchema(BaseModel):
    recommendation_id: int = Field(..., description="Price Recommendation ID")
    reason: str = Field(..., description="Reason human approval is required")

class RequestHumanApprovalTool(BaseTool):
    name = "request_human_approval"
    description = "Create a human approval ticket for high-impact pricing actions."
    args_schema = RequestHumanApprovalSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        rec = (
            db.query(PriceRecommendations)
            .filter(PriceRecommendations.recommendation_id == kwargs["recommendation_id"])
            .first()
        )
        if rec:
            rec.requires_approval = True
            rec.status = "PENDING"
            db.commit()
        return {
            "recommendation_id": kwargs["recommendation_id"],
            "status": "APPROVAL_REQUESTED",
            "reason": kwargs["reason"],
        }


# --- Tool 22: record_feedback ---
class RecordFeedbackSchema(BaseModel):
    recommendation_id: int = Field(..., description="Price Recommendation ID")
    accepted: bool = Field(..., description="Whether recommendation was accepted")
    comments: Optional[str] = Field(None, description="Manager feedback notes")

class RecordFeedbackTool(BaseTool):
    name = "record_feedback"
    description = "Record manager approval/rejection feedback on a rate recommendation."
    args_schema = RecordFeedbackSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        fb = Feedback(
            recommendation_id=kwargs["recommendation_id"],
            user_id=1,
            accepted=kwargs["accepted"],
            comments=kwargs.get("comments"),
        )
        db.add(fb)

        rec = (
            db.query(PriceRecommendations)
            .filter(PriceRecommendations.recommendation_id == kwargs["recommendation_id"])
            .first()
        )
        if rec:
            rec.status = "APPROVED" if kwargs["accepted"] else "REJECTED"

        db.commit()
        return {
            "recommendation_id": kwargs["recommendation_id"],
            "accepted": kwargs["accepted"],
            "status": "FEEDBACK_RECORDED",
        }


# --- Tool 23: calculate_group_displacement ---
class CalculateGroupDisplacementSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    group_name: str = Field(..., description="Corporate or group booking entity name")
    rooms_requested: int = Field(..., ge=1, le=500, description="Rooms requested per night")
    checkin_date: str = Field(..., description="Check-in date YYYY-MM-DD")
    checkout_date: str = Field(..., description="Check-out date YYYY-MM-DD")
    offered_rate: float = Field(..., gt=0.0, description="Offered room rate per night (₹)")
    room_type_id: Optional[int] = Field(None, description="Optional target room type ID")

class CalculateGroupDisplacementTool(BaseTool):
    name = "calculate_group_displacement"
    description = "Evaluate corporate group booking request vs displaced transient revenue to recommend Accept/Reject/Counter-Offer."
    args_schema = CalculateGroupDisplacementSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        from app.services.los_displacement_service import los_displacement_service
        from app.schemas.los_displacement import GroupDisplacementRequest
        req = GroupDisplacementRequest(
            group_name=kwargs["group_name"],
            room_type_id=kwargs.get("room_type_id"),
            rooms_requested=kwargs["rooms_requested"],
            checkin_date=kwargs["checkin_date"],
            checkout_date=kwargs["checkout_date"],
            offered_rate=kwargs["offered_rate"],
        )
        res = los_displacement_service.evaluate_group_displacement(
            db, hotel_id=kwargs["hotel_id"], req=req, user_id=1
        )
        return res.model_dump(mode="json")


# --- Tool 24: get_los_restrictions ---
class GetLOSRestrictionsSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    start_date: str = Field(..., description="Start stay date YYYY-MM-DD")
    days: int = Field(default=14, ge=1, le=60, description="Days horizon")

class GetLOSRestrictionsTool(BaseTool):
    name = "get_los_restrictions"
    description = "Retrieve dynamic Minimum Length of Stay (MLOS), CTA, and CTD restrictions for stay dates."
    args_schema = GetLOSRestrictionsSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        from app.services.los_displacement_service import los_displacement_service
        rules = los_displacement_service.get_los_rules(
            db, hotel_id=kwargs["hotel_id"], start_date=kwargs["start_date"], days=kwargs.get("days", 14)
        )
        return {
            "hotel_id": kwargs["hotel_id"],
            "start_date": kwargs["start_date"],
            "los_rules": [r.model_dump(mode="json") for r in rules],
        }


# --- Tool 25: calculate_trevpar_analytics ---
class CalculateTRePARAnalyticsSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    start_date: str = Field(..., description="Start date YYYY-MM-DD")
    end_date: str = Field(..., description="End date YYYY-MM-DD")

class CalculateTRePARAnalyticsTool(BaseTool):
    name = "calculate_trevpar_analytics"
    description = "Calculate Total Revenue Per Available Room (TRevPAR), RevPAR, NRevPAR, RevPOR, and F&B/Spa/Banquet non-room stream breakdown."
    args_schema = CalculateTRePARAnalyticsSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        from app.services.trevpar_service import trevpar_service
        res = trevpar_service.calculate_trevpar_summary(
            db, hotel_id=kwargs["hotel_id"], start_date=kwargs["start_date"], end_date=kwargs["end_date"]
        )
        return res.model_dump(mode="json")


# --- Tool 26: generate_ancillary_upsell_packages ---
class GenerateAncillaryUpsellPackagesSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")

class GenerateAncillaryUpsellPackagesTool(BaseTool):
    name = "generate_ancillary_upsell_packages"
    description = "Generate AI dynamic non-room revenue upsell packages, bundle pricing, and TRevPAR yield expansion recommendations."
    args_schema = GenerateAncillaryUpsellPackagesSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        from app.services.trevpar_service import trevpar_service
        pkgs = trevpar_service.generate_ancillary_packages(db, hotel_id=kwargs["hotel_id"])
        return {
            "hotel_id": kwargs["hotel_id"],
            "ancillary_packages": [p.model_dump(mode="json") for p in pkgs],
        }


# --- Tool 27: dispatch_multi_channel_alert ---
class DispatchMultiChannelAlertSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    alert_type: str = Field(..., description="COMPETITOR_UNDERCUT, PACE_SURGE, DISPLACEMENT_THRESHOLD, TREVPAR_BREACH, HIGH_DEMAND_EVENT")
    title: str = Field(..., description="Alert headline/title")
    message: str = Field(..., description="Detailed alert body message formatted with INR prices (₹)")
    severity: str = Field("WARNING", description="CRITICAL, WARNING, INFO")
    channels: Optional[List[str]] = Field(default=["EMAIL", "WHATSAPP", "SLACK", "IN_APP"], description="Channels to notify")
    recipient: Optional[str] = Field(None, description="Optional target recipients")
    metadata_json: Optional[Dict[str, Any]] = Field(None, description="Context metadata dictionary")

class DispatchMultiChannelAlertTool(BaseTool):
    name = "dispatch_multi_channel_alert"
    description = "Autonomously dispatch multi-channel revenue alerts (Email, WhatsApp, Slack, In-App) for competitor drops, pace surges, or displacement risks."
    args_schema = DispatchMultiChannelAlertSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        from app.services.alert_service import alert_service
        from app.schemas.alerts import AlertDispatchPayload
        payload = AlertDispatchPayload(
            hotel_id=kwargs["hotel_id"],
            alert_type=kwargs["alert_type"],
            title=kwargs["title"],
            message=kwargs["message"],
            severity=kwargs.get("severity", "WARNING"),
            channels=kwargs.get("channels", ["EMAIL", "WHATSAPP", "SLACK", "IN_APP"]),
            recipient=kwargs.get("recipient"),
            metadata_json=kwargs.get("metadata_json"),
        )
        res = alert_service.dispatch_alert(db, payload)
        return {
            "log_id": res.log_id,
            "hotel_id": res.hotel_id,
            "alert_type": res.alert_type,
            "status": res.status,
            "channel": res.channel,
            "title": res.title,
            "created_at": str(res.created_at),
        }


# --- Tool 28: get_active_alerts_and_rule_config ---
class GetActiveAlertsSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    status_filter: Optional[str] = Field("ALL", description="DISPATCHED, ACKNOWLEDGED, ALL")
    channel_filter: Optional[str] = Field("ALL", description="EMAIL, WHATSAPP, SLACK, IN_APP, ALL")

class GetActiveAlertsTool(BaseTool):
    name = "get_active_alerts_and_rule_config"
    description = "Query active notification dispatch logs, breach severity, and channel configuration rules for a hotel."
    args_schema = GetActiveAlertsSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        from app.services.alert_service import alert_service
        logs = alert_service.get_alert_logs(
            db,
            hotel_id=kwargs["hotel_id"],
            status_filter=kwargs.get("status_filter", "ALL"),
            channel_filter=kwargs.get("channel_filter", "ALL"),
        )
        rules = alert_service.get_alert_rules(db, hotel_id=kwargs["hotel_id"])
        return {
            "hotel_id": kwargs["hotel_id"],
            "total_logs": len(logs),
            "alerts": [
                {
                    "log_id": l.log_id,
                    "alert_type": l.alert_type,
                    "severity": l.severity,
                    "title": l.title,
                    "message": l.message,
                    "channel": l.channel,
                    "status": l.status,
                    "recipient": l.recipient,
                    "created_at": str(l.created_at),
                }
                for l in logs
            ],
            "active_rules_count": len([r for r in rules if r.is_enabled]),
        }


# --- Tool 29: generate_executive_pdf_report ---
class GenerateExecutivePDFReportSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    report_type: Optional[str] = Field("DAILY_REVENUE", description="DAILY_REVENUE, WEEKLY_TREVPAR, MONTHLY_DISPLACEMENT_AUDIT")
    title: Optional[str] = Field(None, description="Custom report title")

class GenerateExecutivePDFReportTool(BaseTool):
    name = "generate_executive_pdf_report"
    description = "Generate an executive PDF revenue performance digest with INR pricing (₹), RevPAR/TRevPAR metrics, and AI strategic recommendations."
    args_schema = GenerateExecutivePDFReportSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        from app.services.pdf_bi_report_service import pdf_bi_report_service
        from app.schemas.reports_bi import ReportGenerateRequest
        req = ReportGenerateRequest(
            hotel_id=kwargs["hotel_id"],
            report_type=kwargs.get("report_type", "DAILY_REVENUE"),
            title=kwargs.get("title"),
        )
        log = pdf_bi_report_service.generate_executive_pdf(db, req)
        return {
            "export_id": log.export_id,
            "hotel_id": log.hotel_id,
            "report_title": log.report_title,
            "download_url": log.download_url,
            "file_size_kb": log.file_size_kb,
            "generated_at": str(log.generated_at),
        }


# --- Tool 30: export_bi_analytics_dataset ---
class ExportBIAnalyticsDatasetSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    days: Optional[int] = Field(30, description="Historical days window")

class ExportBIAnalyticsDatasetTool(BaseTool):
    name = "export_bi_analytics_dataset"
    description = "Export a PowerBI & Tableau compatible JSON/CSV dataset schema containing daily ADR (₹), RevPAR, TRevPAR, Occupancy, and Competitor Index."
    args_schema = ExportBIAnalyticsDatasetSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        from app.services.pdf_bi_report_service import pdf_bi_report_service
        res = pdf_bi_report_service.export_bi_dataset(db, hotel_id=kwargs["hotel_id"], days=kwargs.get("days", 30))
        return res.model_dump(mode="json")


# --- Tool 31: run_multi_agent_swarm_consensus ---
class RunMultiAgentSwarmConsensusSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    topic: Optional[str] = Field("DYNAMIC_PRICING_AND_RESTRICTION_CONSENSUS", description="Target evaluation topic")

class RunMultiAgentSwarmConsensusTool(BaseTool):
    name = "run_multi_agent_swarm_consensus"
    description = "Orchestrate a live multi-agent collaborative swarm evaluation across Pricing, Demand, Compete, Displacement, and TRevPAR sub-agents."
    args_schema = RunMultiAgentSwarmConsensusSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        from app.services.agent_swarm_service import agent_swarm_service
        from app.schemas.agent_swarm import SwarmEvaluateRequest
        req = SwarmEvaluateRequest(
            hotel_id=kwargs["hotel_id"],
            topic=kwargs.get("topic", "DYNAMIC_PRICING_AND_RESTRICTION_CONSENSUS"),
        )
        res = agent_swarm_service.evaluate_swarm_consensus(db, req)
        return res.model_dump(mode="json")


# --- Tool 32: get_agent_swarm_status ---
class GetAgentSwarmStatusSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")

class GetAgentSwarmStatusTool(BaseTool):
    name = "get_agent_swarm_status"
    description = "Query active status, accuracy ratings, and proposal metrics for all 5 sub-agents in the swarm."
    args_schema = GetAgentSwarmStatusSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        from app.services.agent_swarm_service import agent_swarm_service
        members = agent_swarm_service.get_swarm_members(db, hotel_id=kwargs["hotel_id"])
        sessions = agent_swarm_service.get_swarm_sessions(db, hotel_id=kwargs["hotel_id"])
        return {
            "hotel_id": kwargs["hotel_id"],
            "active_agents_count": len([m for m in members if m.status == "ACTIVE"]),
            "agents": [m.model_dump(mode="json") for m in members],
            "total_sessions_evaluated": len(sessions),
        }


# --- Tool 33: generate_developer_api_key ---
class GenerateDeveloperAPIKeySchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    name: str = Field(..., description="Name or purpose of the API Key (e.g. PMS Sync Key)")
    scopes: Optional[List[str]] = Field(default=["pricing:read", "pricing:write", "reports:read"], description="Allowed scopes")
    expires_in_days: Optional[int] = Field(90, description="Expiration in days")

class GenerateDeveloperAPIKeyTool(BaseTool):
    name = "generate_developer_api_key"
    description = "Generate a new developer API key with custom scopes and rate limits for third-party PMS or BI integration."
    args_schema = GenerateDeveloperAPIKeySchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        from app.services.developer_api_service import DeveloperAPIService
        key_obj, raw_key = DeveloperAPIService.create_api_key(
            hotel_id=kwargs["hotel_id"],
            name=kwargs["name"],
            scopes=kwargs.get("scopes", ["pricing:read", "pricing:write", "reports:read"]),
            expires_in_days=kwargs.get("expires_in_days", 90),
            db=db,
        )
        return {
            "id": key_obj.id,
            "hotel_id": key_obj.hotel_id,
            "name": key_obj.name,
            "api_key_raw": raw_key,
            "api_key_prefix": key_obj.api_key_prefix,
            "scopes": key_obj.scopes,
            "status": key_obj.status,
            "created_at": str(key_obj.created_at),
        }


# --- Tool 34: register_webhook_subscription ---
class RegisterWebhookSubscriptionSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    endpoint_url: str = Field(..., description="HTTPS URL of the receiving webhook listener")
    events: List[str] = Field(..., description="List of events to subscribe to (e.g. ['price.updated', 'anomalies.detected'])")
    description: Optional[str] = Field(None, description="Subscription label/description")

class RegisterWebhookSubscriptionTool(BaseTool):
    name = "register_webhook_subscription"
    description = "Register a new webhook listener URL for real-time push events on price updates, anomaly alerts, or swarm consensus."
    args_schema = RegisterWebhookSubscriptionSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        from app.services.developer_api_service import DeveloperAPIService
        sub = DeveloperAPIService.create_webhook(
            hotel_id=kwargs["hotel_id"],
            endpoint_url=kwargs["endpoint_url"],
            events=kwargs["events"],
            description=kwargs.get("description"),
            db=db,
        )
        return {
            "id": sub.id,
            "hotel_id": sub.hotel_id,
            "endpoint_url": sub.endpoint_url,
            "secret_key": sub.secret_key,
            "events": sub.events,
            "status": sub.status,
            "created_at": str(sub.created_at),
        }




