"""
Dynamic Revenue Pricing Engine.
Combines current occupancy, forecast demand, pickup pace, competitor positioning, and event/holiday signals.
"""
from datetime import date
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.hotel import Hotel, RoomType
from app.models.inventory import RoomInventory, Reservation
from app.models.ai import PriceRecommendations
from app.services.revenue_calculator import revenue_calculator
from app.competitors.engine import competitor_engine
from app.events.engine import event_holiday_engine
from app.forecasting.pipeline import forecasting_pipeline
from app.schemas.pricing import PriceRecommendationResponse
from app.core.exceptions import ResourceNotFoundError
from app.core.config import settings


class PricingEngine:
    """Core multi-signal dynamic pricing engine."""

    @staticmethod
    def calculate_occupancy_multiplier(occ_pct: float) -> Tuple[float, str]:
        if occ_pct >= 90.0:
            return 1.30, "Critical high occupancy (>=90%)"
        elif occ_pct >= 80.0:
            return 1.20, "Strong occupancy (80-89%)"
        elif occ_pct >= 70.0:
            return 1.10, "Healthy occupancy (70-79%)"
        elif occ_pct >= 50.0:
            return 1.0, "Moderate occupancy (50-69%)"
        elif occ_pct >= 30.0:
            return 0.95, "Low occupancy (30-49%)"
        else:
            return 0.90, "Very low occupancy (<30%)"

    @staticmethod
    def calculate_pickup_multiplier(pickup_3d: int) -> Tuple[float, str]:
        if pickup_3d >= 10:
            return 1.12, "Surge pickup pace (+10 rooms in 3 days)"
        elif pickup_3d >= 5:
            return 1.06, "Strong pickup pace (+5 rooms in 3 days)"
        elif pickup_3d <= -3:
            return 0.95, "Negative pickup pace (cancellations detected)"
        else:
            return 1.0, "Normal booking pace"

    def calculate_recommendation(
        self, db: Session, hotel_id: int, room_type_id: int, stay_date: date
    ) -> PriceRecommendationResponse:
        """
        Calculate data-driven rate recommendation for a specific room type and stay date.
        """
        hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        if not hotel:
            raise ResourceNotFoundError("Hotel", hotel_id)

        room_type = db.query(RoomType).filter(RoomType.room_type_id == room_type_id).first()
        if not room_type:
            raise ResourceNotFoundError("RoomType", room_type_id)

        # 1. Fetch Current Occupancy & Revenue Metrics
        summary = revenue_calculator.calculate_period_summary(
            db, hotel_id=hotel_id, start_date=stay_date, end_date=stay_date
        )
        current_occ = summary.occupancy_pct

        # 2. Fetch Pickup Pace
        pace = revenue_calculator.calculate_pickup_pace(db, hotel_id=hotel_id, stay_date=stay_date)

        # 3. Fetch Forecast Demand
        fc_res = forecasting_pipeline.run_pipeline(
            db, hotel_id=hotel_id, room_type_id=room_type_id, start_date=stay_date, horizon_days=1
        )
        forecast_val = fc_res.predictions[0].predicted_demand if fc_res.predictions else (room_type.total_inventory * 0.7)
        fc_confidence = fc_res.predictions[0].confidence_score if fc_res.predictions else 0.85

        # 4. Fetch Competitor Market Analysis
        base_rate = room_type.base_price
        comp_analysis = competitor_engine.analyze_market_rates(
            db, hotel_id=hotel_id, stay_date=stay_date, my_rate=base_rate
        )

        # 5. Fetch Calendar Impact (Events & Holidays)
        calendar_impact = event_holiday_engine.evaluate_calendar_impact(
            db, hotel_id=hotel_id, stay_date=stay_date
        )

        # --- Compute Multipliers ---
        occ_mult, occ_reason = self.calculate_occupancy_multiplier(current_occ)
        pickup_mult, pickup_reason = self.calculate_pickup_multiplier(pace.pickup_3d)
        calendar_mult = calendar_impact.composite_demand_multiplier

        # Day of week multiplier
        dow_idx = stay_date.weekday()
        dow_mult = 1.10 if dow_idx in [4, 5] else 1.0

        # Competitor positioning adjustment
        comp_median = comp_analysis.competitor_median
        comp_mult = 1.0
        if not comp_analysis.anomaly_detected and comp_median > 0:
            if comp_analysis.price_gap_pct < -15.0:
                comp_mult = 1.08  # Underpriced relative to market, pull up rate
            elif comp_analysis.price_gap_pct > 25.0:
                comp_mult = 0.95  # Overpriced relative to market, adjust down

        # Composite Demand Index
        demand_index = round(occ_mult * pickup_mult * calendar_mult * dow_mult * comp_mult, 2)

        # Calculate Raw Proposed Rate
        raw_rate = base_rate * demand_index

        # Enforce Safe Floors and Ceilings
        min_rate = max(settings.DEFAULT_MIN_RATE_FLOOR, base_rate * 0.70)
        max_rate = min(settings.DEFAULT_MAX_RATE_CEILING, base_rate * 2.50)
        recommended_rate = round(min(max_rate, max(min_rate, raw_rate)), 0)

        # Check approval threshold (> 10% change from base_rate)
        price_change_pct = abs(recommended_rate - base_rate) / base_rate
        requires_approval = price_change_pct >= settings.APPROVAL_THRESHOLD_PCT

        # Synthesize Human-Readable Reason
        reasons_list = [occ_reason]
        if pace.pickup_3d != 0:
            reasons_list.append(pickup_reason)
        if calendar_impact.explanation:
            reasons_list.append(calendar_impact.explanation)
        if comp_median > 0:
            reasons_list.append(f"Competitor median positioned at ₹{comp_median:,.0f} (Gap: {comp_analysis.price_gap_pct:+.1f}%)")

        price_reason = " + ".join(reasons_list)

        # Stage 3 & 4 Status Decision
        initial_status = "PENDING" if requires_approval else "PUBLISHED"

        # Persist Recommendation to DB
        db_rec = (
            db.query(PriceRecommendations)
            .filter(
                PriceRecommendations.hotel_id == hotel_id,
                PriceRecommendations.room_type_id == room_type_id,
                PriceRecommendations.stay_date == stay_date,
            )
            .first()
        )

        if not db_rec:
            db_rec = PriceRecommendations(
                hotel_id=hotel_id,
                room_type_id=room_type_id,
                stay_date=stay_date,
                recommended_rate=recommended_rate,
                min_rate=min_rate,
                max_rate=max_rate,
                current_rate=base_rate,
                occupancy=current_occ,
                forecast_demand=forecast_val,
                competitor_median=comp_median,
                demand_index=demand_index,
                price_reason=price_reason,
                confidence_score=fc_confidence,
                status=initial_status,
                requires_approval=requires_approval,
            )
            db.add(db_rec)
        else:
            db_rec.recommended_rate = recommended_rate
            db_rec.min_rate = min_rate
            db_rec.max_rate = max_rate
            db_rec.current_rate = base_rate
            db_rec.occupancy = current_occ
            db_rec.forecast_demand = forecast_val
            db_rec.competitor_median = comp_median
            db_rec.demand_index = demand_index
            db_rec.price_reason = price_reason
            db_rec.confidence_score = fc_confidence
            db_rec.requires_approval = requires_approval
            if initial_status == "PUBLISHED":
                db_rec.status = "PUBLISHED"

        # If safe rate (< 10%), execute Stage 4 automatically by updating RoomInventory
        if not requires_approval:
            inventory = (
                db.query(RoomInventory)
                .filter(
                    RoomInventory.hotel_id == hotel_id,
                    RoomInventory.room_type_id == room_type_id,
                    RoomInventory.stay_date == stay_date,
                )
                .first()
            )
            if inventory:
                inventory.current_rate = recommended_rate

        db.commit()
        db.refresh(db_rec)

        return PriceRecommendationResponse.model_validate(db_rec)

    def run_autonomous_pricing_cycle(
        self, db: Session, hotel_id: int, horizon_days: int = 30
    ) -> Dict[str, Any]:
        """
        Executes the full 5-Stage Controlled Autonomous Pricing Cycle:
        Stage 1: AI Analyzes Data (occupancy, pace, compset, events, demand forecast)
        Stage 2: AI Recommends Price (dynamic multi-factor rate calculation + guardrails)
        Stage 3: Controlled Approval Gate (<10% auto-pass, >=10% queued for Manager)
        Stage 4: System Publishes Price (deploys safe rates directly to RoomInventory)
        Stage 5: Controlled Autonomous Feedback Loop & Metrics Summary
        """
        from datetime import date, timedelta, datetime, timezone
        from app.models.hotel import Hotel

        hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        if hotel and hotel.status != "ACTIVE":
            return {
                "hotel_id": hotel_id,
                "status": "SKIPPED_INACTIVE",
                "message": f"Hotel '{hotel.hotel_name}' is INACTIVE. Autonomous pricing cycle skipped.",
                "stage_1_data_points_analyzed": 0,
                "stage_2_recommendations_generated": 0,
                "stage_3_pending_approvals": 0,
                "stage_4_auto_published": 0,
                "stage_5_autonomous_mode": "INACTIVE_SKIPPED",
            }

        today = date.today()
        room_types = db.query(RoomType).filter(RoomType.hotel_id == hotel_id).all()

        analyzed_count = 0
        recommended_count = 0
        pending_approval_count = 0
        auto_published_count = 0

        for rt in room_types:
            for day_offset in range(horizon_days):
                stay_dt = today + timedelta(days=day_offset)
                rec = self.calculate_recommendation(
                    db, hotel_id=hotel_id, room_type_id=rt.room_type_id, stay_date=stay_dt
                )
                analyzed_count += 1
                recommended_count += 1

                if rec.status == "PENDING" or rec.requires_approval:
                    pending_approval_count += 1
                else:
                    auto_published_count += 1

        return {
            "hotel_id": hotel_id,
            "horizon_days": horizon_days,
            "stage_1_data_points_analyzed": analyzed_count,
            "stage_2_recommendations_generated": recommended_count,
            "stage_3_pending_approvals": pending_approval_count,
            "stage_4_auto_published": auto_published_count,
            "stage_5_autonomous_mode": "ACTIVE_CONTROLLED",
            "guardrail_threshold_pct": round(settings.APPROVAL_THRESHOLD_PCT * 100, 1),
            "last_run_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_pipeline_status(self, db: Session, hotel_id: int) -> Dict[str, Any]:
        """Fetch real-time metrics across all 5 pricing pipeline stages for the hotel."""
        from datetime import datetime, timezone

        recs = db.query(PriceRecommendations).filter(PriceRecommendations.hotel_id == hotel_id).all()
        
        pending_count = sum(
            1 for r in recs if r.status and r.status.upper() in ["PENDING", "PENDING_APPROVAL"]
        )
        published_count = sum(
            1 for r in recs if r.status and r.status.upper() in ["PUBLISHED", "APPROVED", "APPLIED", "OVERRIDDEN"]
        )
        rejected_count = sum(
            1 for r in recs if r.status and r.status.upper() in ["REJECTED"]
        )

        return {
            "hotel_id": hotel_id,
            "total_recommendations": len(recs),
            "stage_1_status": "ACTIVE",
            "stage_2_status": "ACTIVE",
            "stage_3_pending_approvals": pending_count,
            "stage_4_published_prices": published_count,
            "stage_5_autonomous_mode": "ACTIVE_CONTROLLED",
            "rejected_count": rejected_count,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }


pricing_engine = PricingEngine()

