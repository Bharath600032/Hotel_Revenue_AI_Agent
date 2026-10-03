"""
Events & Holidays Intelligence Engine for calculating calendar demand multipliers.
"""
from datetime import date
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models.events import Holidays, Events
from app.models.hotel import Hotel
from app.schemas.event_holiday import CalendarImpactResponse, HolidayResponse, EventResponse
from app.core.exceptions import ResourceNotFoundError


class EventHolidayEngine:
    """Calculates demand multipliers based on national/regional holidays and major city events."""

    @staticmethod
    def calculate_holiday_multiplier(holidays: List[Holidays]) -> Tuple[float, str]:
        if not holidays:
            return 1.0, "No active holidays."

        max_importance = max(h.importance for h in holidays)
        # Importance 1: 1.02 (+2%), 2: 1.05 (+5%), 3: 1.08 (+8%), 4: 1.15 (+15%), 5: 1.25 (+25%)
        multiplier_map = {1: 1.02, 2: 1.05, 3: 1.08, 4: 1.15, 5: 1.25}
        mult = multiplier_map.get(max_importance, 1.08)
        names = ", ".join(h.holiday_name for h in holidays)
        return mult, f"Holiday demand uplift from: {names} (Importance {max_importance}/5)."

    @staticmethod
    def calculate_event_multiplier(events: List[Events]) -> Tuple[float, str]:
        if not events:
            return 1.0, "No active events."

        max_importance = max(e.importance for e in events)
        total_attendance = sum(e.expected_attendance or 0 for e in events)

        # Base multiplier from importance
        mult = 1.0 + (max_importance * 0.05)  # 1->1.05, 3->1.15, 5->1.25

        # Additional attendance uplift
        if total_attendance > 50000:
            mult += 0.15
        elif total_attendance > 20000:
            mult += 0.10
        elif total_attendance > 5000:
            mult += 0.05

        names = ", ".join(e.event_name for e in events)
        return round(mult, 2), f"Event demand surge from: {names} (Est. attendance: {total_attendance:,})."

    def evaluate_calendar_impact(
        self, db: Session, hotel_id: int, stay_date: date
    ) -> CalendarImpactResponse:
        """Evaluate combined holiday + event demand impact for target hotel and stay date."""
        hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        if not hotel:
            raise ResourceNotFoundError("Hotel", hotel_id)

        # 1. Fetch active holidays
        active_holidays = (
            db.query(Holidays)
            .filter(
                Holidays.country == hotel.country,
                Holidays.holiday_date == stay_date,
            )
            .all()
        )

        # 2. Fetch active events in city
        active_events = (
            db.query(Events)
            .filter(
                Events.city.ilike(f"%{hotel.city}%"),
                Events.start_date <= stay_date,
                Events.end_date >= stay_date,
            )
            .all()
        )

        h_mult, h_exp = self.calculate_holiday_multiplier(active_holidays)
        e_mult, e_exp = self.calculate_event_multiplier(active_events)

        # 3. Fetch weather demand multiplier
        from app.weather.engine import weather_engine
        w_mult, w_exp = weather_engine.get_daily_weather_multiplier(db, hotel_id=hotel_id, stay_date=stay_date)

        # Composite demand multiplier = (max(h_mult, e_mult) + (min(h_mult, e_mult) - 1.0) * 0.5) * w_mult
        base_cal_mult = max(h_mult, e_mult) + (min(h_mult, e_mult) - 1.0) * 0.5
        composite_mult = round(base_cal_mult * w_mult, 2)

        # Classify demand level
        if composite_mult >= 1.30:
            classification = "EXTREME_DEMAND"
        elif composite_mult >= 1.15:
            classification = "HIGH_DEMAND"
        elif composite_mult > 1.02:
            classification = "MODERATE_UPLIFT"
        elif composite_mult < 0.95:
            classification = "DEPRESSED_DEMAND"
        else:
            classification = "NORMAL"

        explanation = f"{h_exp} {e_exp} [Weather Impact: {w_exp}]".strip()

        return CalendarImpactResponse(
            hotel_id=hotel_id,
            stay_date=stay_date,
            active_holidays=[HolidayResponse.model_validate(h) for h in active_holidays],
            active_events=[EventResponse.model_validate(e) for e in active_events],
            holiday_demand_multiplier=h_mult,
            event_demand_multiplier=e_mult,
            weather_demand_multiplier=w_mult,
            composite_demand_multiplier=composite_mult,
            demand_classification=classification,
            explanation=explanation,
        )


event_holiday_engine = EventHolidayEngine()
