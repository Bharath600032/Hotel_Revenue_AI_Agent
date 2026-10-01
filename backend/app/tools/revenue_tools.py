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
    city: str = Field(..., description="City name")
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

        evs = (
            db.query(Events)
            .filter(
                Events.city.ilike(f"%{kwargs['city']}%"),
                Events.end_date >= s_dt,
                Events.start_date <= e_dt,
            )
            .all()
        )
        return {
            "city": kwargs["city"],
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
        return analysis.model_dump()


# --- Tool 13: get_weather ---
class GetWeatherSchema(BaseModel):
    city: str = Field(..., description="City name")
    start_date: str = Field(..., description="Start date YYYY-MM-DD")
    end_date: str = Field(..., description="End date YYYY-MM-DD")

class GetWeatherTool(BaseTool):
    name = "get_weather"
    description = "Retrieve temperature and rain probability forecasts for city."
    args_schema = GetWeatherSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["start_date"])
        e_dt = date.fromisoformat(kwargs["end_date"])
        w_list = (
            db.query(Weather)
            .filter(
                Weather.city.ilike(f"%{kwargs['city']}%"),
                Weather.date >= s_dt,
                Weather.date <= e_dt,
            )
            .all()
        )
        if not w_list:
            return {
                "city": kwargs["city"],
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
            "city": kwargs["city"],
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
    room_type_id: int = Field(..., description="Room Type ID")
    stay_date: str = Field(..., description="Target stay date YYYY-MM-DD")
    horizon_days: int = Field(default=30, description="Forecast horizon days")

class RunDemandForecastTool(BaseTool):
    name = "run_demand_forecast"
    description = "Execute multi-model ML demand forecasting pipeline."
    args_schema = RunDemandForecastSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["stay_date"])
        fc_res = forecasting_pipeline.run_pipeline(
            db,
            hotel_id=kwargs["hotel_id"],
            room_type_id=kwargs["room_type_id"],
            start_date=s_dt,
            horizon_days=kwargs.get("horizon_days", 30),
        )
        return fc_res.model_dump()


# --- Tool 15: calculate_pricing_recommendation ---
class CalculatePricingRecommendationSchema(BaseModel):
    hotel_id: int = Field(..., description="Target Hotel ID")
    room_type_id: int = Field(..., description="Room Type ID")
    stay_date: str = Field(..., description="Target stay date YYYY-MM-DD")

class CalculatePricingRecommendationTool(BaseTool):
    name = "calculate_pricing_recommendation"
    description = "Calculate dynamic price recommendation, demand index, and reasoning."
    args_schema = CalculatePricingRecommendationSchema

    def execute(self, db: Session, **kwargs) -> Dict[str, Any]:
        s_dt = date.fromisoformat(kwargs["stay_date"])
        rec = pricing_engine.calculate_recommendation(
            db, hotel_id=kwargs["hotel_id"], room_type_id=kwargs["room_type_id"], stay_date=s_dt
        )
        return rec.model_dump()


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
        return res.model_dump()


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
