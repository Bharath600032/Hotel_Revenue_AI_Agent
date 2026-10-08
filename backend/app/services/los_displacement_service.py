"""
Service module for Length of Stay (LOS) rules and Group Displacement Analysis.
"""
from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.hotel import Hotel, RoomType
from app.models.inventory import RoomInventory
from app.models.los_displacement import LengthOfStayRules, GroupDisplacementLog
from app.schemas.los_displacement import (
    GroupDisplacementRequest,
    GroupDisplacementResponse,
    LOSRuleResponse,
    LOSRuleUpdate,
)
from app.repositories.hotel_repository import hotel_repository
from app.services.revenue_calculator import revenue_calculator
from app.events.engine import event_holiday_engine


class LOSDisplacementService:
    def evaluate_group_displacement(
        self, db: Session, hotel_id: int, req: GroupDisplacementRequest, user_id: int
    ) -> GroupDisplacementResponse:
        """
        Evaluate net financial impact of a corporate group request vs displaced transient demand.
        """
        hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        if not hotel:
            raise HTTPException(status_code=404, detail=f"Hotel ID {hotel_id} not found.")

        try:
            s_dt = date.fromisoformat(req.checkin_date)
            e_dt = date.fromisoformat(req.checkout_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD.")

        if e_dt <= s_dt:
            raise HTTPException(status_code=400, detail="Check-out date must be strictly after check-in date.")

        nights = (e_dt - s_dt).days
        total_room_nights = req.rooms_requested * nights

        # Resolve Room Type
        rts = hotel_repository.get_room_types_by_hotel(db, hotel_id)
        if not rts:
            raise HTTPException(status_code=404, detail="No active room types found for this hotel.")

        target_rt = None
        if req.room_type_id:
            target_rt = next((rt for rt in rts if rt.room_type_id == req.room_type_id), None)

        if not target_rt:
            target_rt = rts[0]

        base_rate = target_rt.base_price

        # Ancillary Revenue inputs
        f_and_b = req.f_and_b_revenue or 0.0
        meeting_rental = req.meeting_room_rental or 0.0
        other_ancillary = req.other_ancillary_revenue or 0.0
        total_ancillary = f_and_b + meeting_rental + other_ancillary

        # Calculate daily expected transient rate displacement & build daily breakdown
        total_displaced_revenue = 0.0
        daily_breakdown = []
        cur_date = s_dt
        while cur_date < e_dt:
            # Check calendar & demand impact for current stay date
            impact = event_holiday_engine.evaluate_calendar_impact(db, hotel_id=hotel_id, stay_date=cur_date)
            summary = revenue_calculator.calculate_period_summary(db, hotel_id=hotel_id, start_date=cur_date, end_date=cur_date)
            
            occ_pct = summary.occupancy_pct
            demand_mult = impact.composite_demand_multiplier
            
            # Occupancy surge multiplier on dynamic transient ADR
            occ_mult = 1.25 if occ_pct >= 85 else (1.10 if occ_pct >= 70 else 1.0)
            daily_transient_rate = base_rate * demand_mult * occ_mult

            total_rooms = getattr(hotel, "total_rooms", 100)
            already_occupied = getattr(summary, "total_occupied_rooms", 0)
            avail_cap = max(0, total_rooms - already_occupied)

            # Live unconstrained transient demand projection
            unconstrained_transient_demand = max(already_occupied, round(total_rooms * (occ_pct / 100.0)))

            # Real transient displacement occurs ONLY when total projected volume exceeds physical capacity
            total_projected_demand = unconstrained_transient_demand + req.rooms_requested
            displaced_rooms = max(0, min(req.rooms_requested, total_projected_demand - total_rooms))

            # Actual transient revenue lost from displaced retail bookings
            daily_displaced_rev = displaced_rooms * daily_transient_rate
            total_displaced_revenue += daily_displaced_rev

            daily_breakdown.append({
                "stay_date": cur_date.strftime("%Y-%m-%d"),
                "transient_rate": round(daily_transient_rate, 2),
                "transient_demand_pct": round(occ_pct, 1),
                "available_capacity": avail_cap,
                "group_rooms": req.rooms_requested,
                "displaced_transient_rooms": displaced_rooms,
                "transient_revenue_lost": round(daily_displaced_rev, 2),
            })
            cur_date += timedelta(days=1)

        gross_group_room_revenue = total_room_nights * req.offered_rate
        total_gross_group_revenue = gross_group_room_revenue + total_ancillary
        net_impact = total_gross_group_revenue - total_displaced_revenue

        # Variable marginal cost per room night (housekeeping, linen, utilities)
        marginal_cost_per_night = 800.0

        # Real-time breakeven rate floor considering ancillary revenue offset
        net_room_revenue_needed = max(0.0, total_displaced_revenue - total_ancillary)
        raw_breakeven = net_room_revenue_needed / total_room_nights if total_room_nights > 0 else 0.0
        breakeven_rate = max(marginal_cost_per_night, round(raw_breakeven, 2))
        counter_offer_rate = max(round(breakeven_rate * 1.08 / 50) * 50, round(base_rate * 0.85 / 50) * 50)

        group_label = req.group_name or "Corporate Group Lead"

        # Real-Time Decision & Rationale Matrix
        if net_impact >= 0 and req.offered_rate >= marginal_cost_per_night:
            decision = "ACCEPT"
            rationale = (
                f"REAL-TIME ANALYSIS: Proposed group rate ₹{req.offered_rate:,.0f} with ₹{total_ancillary:,.0f} ancillary revenue "
                f"yields a net positive gain of +₹{net_impact:,.0f} over displaced transient demand (Total displaced revenue: ₹{total_displaced_revenue:,.0f}). "
                f"Recommendation: ACCEPT group booking for '{group_label}'."
            )
        elif req.offered_rate >= breakeven_rate * 0.75:
            decision = "COUNTER_OFFER"
            rationale = (
                f"REAL-TIME ANALYSIS: Proposed group rate ₹{req.offered_rate:,.0f} creates a net revenue deficit of -₹{abs(net_impact):,.0f} "
                f"due to transient displacement (₹{total_displaced_revenue:,.0f}). Recommend COUNTER-OFFER at ₹{counter_offer_rate:,.0f}/night "
                f"(Exact breakeven rate floor: ₹{breakeven_rate:,.0f}/night)."
            )
        else:
            decision = "REJECT"
            rationale = (
                f"REAL-TIME ANALYSIS: Proposed group rate ₹{req.offered_rate:,.0f} causes severe revenue cannibalization (-₹{abs(net_impact):,.0f} deficit). "
                f"Displaces high-yielding transient bookings. Minimum breakeven threshold is ₹{breakeven_rate:,.0f}/night."
            )

        # Log to Database
        db_log = GroupDisplacementLog(
            hotel_id=hotel_id,
            room_type_id=target_rt.room_type_id,
            group_name=group_label,
            rooms_requested=req.rooms_requested,
            checkin_date=s_dt,
            checkout_date=e_dt,
            nights=nights,
            offered_rate=req.offered_rate,
            transient_revenue_displaced=round(total_displaced_revenue, 2),
            proposed_group_revenue=round(gross_group_room_revenue, 2),
            net_displacement_impact=round(net_impact, 2),
            breakeven_group_rate=round(breakeven_rate, 2),
            counter_offer_rate=round(counter_offer_rate, 2),
            decision=decision,
            rationale=rationale,
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)

        return GroupDisplacementResponse(
            hotel_id=hotel_id,
            room_type_id=target_rt.room_type_id,
            group_name=group_label,
            rooms_requested=req.rooms_requested,
            checkin_date=str(s_dt),
            checkout_date=str(e_dt),
            start_date=str(s_dt),
            end_date=str(e_dt),
            nights=nights,
            total_nights=nights,
            total_room_nights=total_room_nights,
            total_room_nights_requested=total_room_nights,
            offered_rate=req.offered_rate,
            offered_group_rate=req.offered_rate,
            proposed_group_revenue=round(gross_group_room_revenue, 2),
            gross_group_room_revenue=round(gross_group_room_revenue, 2),
            ancillary_revenue=round(total_ancillary, 2),
            total_gross_group_revenue=round(total_gross_group_revenue, 2),
            transient_revenue_displaced=round(total_displaced_revenue, 2),
            total_transient_revenue_displaced=round(total_displaced_revenue, 2),
            net_displacement_impact=round(net_impact, 2),
            net_revenue_impact=round(net_impact, 2),
            breakeven_group_rate=round(breakeven_rate, 2),
            counter_offer_rate=round(counter_offer_rate, 2),
            recommended_counter_offer_rate=round(counter_offer_rate, 2),
            decision=decision,
            recommendation=decision,
            rationale=rationale,
            decision_rationale=rationale,
            daily_breakdown=daily_breakdown,
            displacement_id=db_log.displacement_id,
            created_at=db_log.created_at,
        )

    def get_group_displacement_logs(self, db: Session, hotel_id: int, limit: int = 50) -> List[GroupDisplacementResponse]:
        logs = (
            db.query(GroupDisplacementLog)
            .filter(GroupDisplacementLog.hotel_id == hotel_id)
            .order_by(GroupDisplacementLog.created_at.desc())
            .limit(limit)
            .all()
        )
        results = []
        for log in logs:
            tot_rn = (log.rooms_requested or 0) * (log.nights or 1)
            results.append(
                GroupDisplacementResponse(
                    displacement_id=log.displacement_id,
                    hotel_id=log.hotel_id,
                    room_type_id=log.room_type_id,
                    group_name=log.group_name or "Corporate Lead",
                    rooms_requested=log.rooms_requested or 1,
                    checkin_date=str(log.checkin_date),
                    checkout_date=str(log.checkout_date),
                    start_date=str(log.checkin_date),
                    end_date=str(log.checkout_date),
                    nights=log.nights or 1,
                    total_nights=log.nights or 1,
                    total_room_nights=tot_rn,
                    total_room_nights_requested=tot_rn,
                    offered_rate=log.offered_rate or 0.0,
                    offered_group_rate=log.offered_rate or 0.0,
                    proposed_group_revenue=log.proposed_group_revenue or 0.0,
                    gross_group_room_revenue=log.proposed_group_revenue or 0.0,
                    ancillary_revenue=0.0,
                    total_gross_group_revenue=log.proposed_group_revenue or 0.0,
                    transient_revenue_displaced=log.transient_revenue_displaced or 0.0,
                    total_transient_revenue_displaced=log.transient_revenue_displaced or 0.0,
                    net_displacement_impact=log.net_displacement_impact or 0.0,
                    net_revenue_impact=log.net_displacement_impact or 0.0,
                    breakeven_group_rate=log.breakeven_group_rate or 0.0,
                    counter_offer_rate=log.counter_offer_rate or 0.0,
                    recommended_counter_offer_rate=log.counter_offer_rate or 0.0,
                    decision=log.decision or "ACCEPT",
                    recommendation=log.decision or "ACCEPT",
                    rationale=log.rationale or "Audit log entry.",
                    decision_rationale=log.rationale or "Audit log entry.",
                    daily_breakdown=[],
                    created_at=log.created_at,
                )
            )
        return results

    def get_los_rules(self, db: Session, hotel_id: int, start_date: str, days: int = 14) -> List[LOSRuleResponse]:
        """
        Fetch dynamic Length of Stay (LOS) & CTA rules for a date range.
        Auto-generates dynamic MLOS rules based on projected demand & weekend peak signals.
        """
        try:
            s_dt = date.fromisoformat(start_date)
        except ValueError:
            s_dt = date.today()

        e_dt = s_dt + timedelta(days=days)

        # Existing DB rules
        db_rules = (
            db.query(LengthOfStayRules)
            .filter(
                LengthOfStayRules.hotel_id == hotel_id,
                LengthOfStayRules.stay_date >= s_dt,
                LengthOfStayRules.stay_date < e_dt,
            )
            .all()
        )
        rules_map = {r.stay_date: r for r in db_rules}

        results = []
        cur_date = s_dt
        while cur_date < e_dt:
            if cur_date in rules_map:
                r = rules_map[cur_date]
                results.append(
                    LOSRuleResponse(
                        rule_id=r.los_rule_id,
                        los_rule_id=r.los_rule_id,
                        hotel_id=r.hotel_id,
                        room_type_id=r.room_type_id,
                        stay_date=str(r.stay_date),
                        min_length_of_stay=r.min_length_of_stay,
                        max_length_of_stay=r.max_length_of_stay,
                        closed_to_arrival=r.closed_to_arrival,
                        closed_to_departure=r.closed_to_departure,
                        reason=r.reason,
                        is_system_recommended=False,
                        recommendation_reason=r.reason or "Active custom hotel rule.",
                    )
                )
            else:
                # Calculate dynamic MLOS recommendation
                impact = event_holiday_engine.evaluate_calendar_impact(db, hotel_id=hotel_id, stay_date=cur_date)
                is_weekend = cur_date.weekday() in [4, 5]  # Friday, Saturday
                has_event = impact.composite_demand_multiplier > 1.15
                
                min_los = 1
                reason = "Standard 1-night stay allowed"
                if has_event and is_weekend:
                    min_los = 3
                    reason = "High-impact local event & weekend peak demand — MLOS 3 nights enforced to eliminate gap nights"
                elif has_event or is_weekend:
                    min_los = 2
                    reason = "High demand window — MLOS 2 nights enforced to optimize stay length"

                results.append(
                    LOSRuleResponse(
                        rule_id=0,
                        los_rule_id=0,
                        hotel_id=hotel_id,
                        stay_date=str(cur_date),
                        min_length_of_stay=min_los,
                        closed_to_arrival=False,
                        closed_to_departure=False,
                        reason=reason,
                        is_system_recommended=True,
                        ai_confidence=0.95,
                        recommendation_reason=reason,
                    )
                )
            cur_date += timedelta(days=1)

        return results

    def update_los_rule(
        self, db: Session, hotel_id: int, stay_date: str, req: LOSRuleUpdate, user_id: int
    ) -> LOSRuleResponse:
        """
        Update or create custom MLOS, CTA, CTD restrictions for a stay date.
        """
        try:
            s_dt = date.fromisoformat(stay_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid stay date YYYY-MM-DD")

        db_rule = (
            db.query(LengthOfStayRules)
            .filter(LengthOfStayRules.hotel_id == hotel_id, LengthOfStayRules.stay_date == s_dt)
            .first()
        )

        if not db_rule:
            db_rule = LengthOfStayRules(
                hotel_id=hotel_id,
                stay_date=s_dt,
                min_length_of_stay=req.min_length_of_stay or 1,
                max_length_of_stay=req.max_length_of_stay,
                closed_to_arrival=req.closed_to_arrival if req.closed_to_arrival is not None else False,
                closed_to_departure=req.closed_to_departure if req.closed_to_departure is not None else False,
                reason=req.reason or "Management custom override",
            )
            db.add(db_rule)
        else:
            if req.min_length_of_stay is not None:
                db_rule.min_length_of_stay = req.min_length_of_stay
            if req.max_length_of_stay is not None:
                db_rule.max_length_of_stay = req.max_length_of_stay
            if req.closed_to_arrival is not None:
                db_rule.closed_to_arrival = req.closed_to_arrival
            if req.closed_to_departure is not None:
                db_rule.closed_to_departure = req.closed_to_departure
            if req.reason is not None:
                db_rule.reason = req.reason

        db.commit()
        db.refresh(db_rule)

        return LOSRuleResponse(
            los_rule_id=db_rule.los_rule_id,
            hotel_id=db_rule.hotel_id,
            stay_date=str(db_rule.stay_date),
            min_length_of_stay=db_rule.min_length_of_stay,
            max_length_of_stay=db_rule.max_length_of_stay,
            closed_to_arrival=db_rule.closed_to_arrival,
            closed_to_departure=db_rule.closed_to_departure,
            reason=db_rule.reason,
        )


los_displacement_service = LOSDisplacementService()
