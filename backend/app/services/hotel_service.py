"""
Hotel Service enforcing domain logic, code uniqueness, and audit tracking.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.hotel import Hotel, RoomType, RatePlan
from app.models.audit import AuditLogs
from app.models.inventory import RoomInventory, Reservation, DailyBookingSnapshot
from app.models.rates import CompetitorHotels, CompetitorRates, HistoricalRates
from app.models.ai import PriceRecommendations, Forecasts, AgentRuns, AgentToolCalls, Feedback
from app.repositories.hotel_repository import hotel_repository
from app.schemas.hotel import HotelCreate, HotelUpdate
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate
from app.schemas.rate_plan import RatePlanCreate, RatePlanUpdate
from app.core.exceptions import ResourceNotFoundError, DataValidationError


class HotelService:
    # --- Hotel Operations ---
    def get_hotel(self, db: Session, hotel_id: int) -> Hotel:
        hotel = hotel_repository.get_by_id(db, hotel_id)
        if not hotel:
            raise ResourceNotFoundError("Hotel", hotel_id)
        return hotel

    def list_hotels(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        city: Optional[str] = None,
    ) -> List[Hotel]:
        return hotel_repository.get_multi(db, skip=skip, limit=limit, city=city)

    def create_hotel(self, db: Session, hotel_in: HotelCreate, user_id: int) -> Hotel:
        existing = hotel_repository.get_by_code(db, hotel_in.hotel_code)
        if existing:
            raise DataValidationError(f"Hotel code '{hotel_in.hotel_code}' is already registered.")

        hotel = hotel_repository.create(db, hotel_in)

        # Log audit entry
        audit = AuditLogs(
            user_id=user_id,
            action="CREATE_HOTEL",
            entity_type="Hotel",
            entity_id=str(hotel.hotel_id),
            new_value={"hotel_code": hotel.hotel_code, "hotel_name": hotel.hotel_name},
        )
        db.add(audit)
        db.commit()

        # Auto-provision dedicated AI Agent, room types, compset & autonomous pricing pipeline for new hotel
        from app.agents.hotel_agent_factory import hotel_agent_factory
        try:
            hotel_agent_factory.provision_new_hotel(db, hotel_id=hotel.hotel_id)
        except Exception as e:
            # Non-blocking log if seeder is running
            pass

        return hotel

    def update_hotel(self, db: Session, hotel_id: int, hotel_in: HotelUpdate, user_id: int) -> Hotel:
        hotel = self.get_hotel(db, hotel_id)
        old_val = {"hotel_name": hotel.hotel_name, "total_rooms": hotel.total_rooms}
        updated = hotel_repository.update(db, hotel, hotel_in)

        audit = AuditLogs(
            user_id=user_id,
            action="UPDATE_HOTEL",
            entity_type="Hotel",
            entity_id=str(hotel_id),
            old_value=old_val,
            new_value=hotel_in.model_dump(exclude_unset=True),
        )
        db.add(audit)
        return updated

    def delete_hotel(self, db: Session, hotel_id: int, user_id: int) -> bool:
        target_hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        if not target_hotel:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"Hotel ID {hotel_id} not found")

        hotel_name = target_hotel.hotel_name
        hotel_code = target_hotel.hotel_code

        # Expunge objects from session so SQLAlchemy doesn't attempt relationship cascade on stale instances
        db.expunge_all()

        # 1. Delete Feedback records linked to this hotel's price recommendations
        rec_ids = [r[0] for r in db.query(PriceRecommendations.recommendation_id).filter(PriceRecommendations.hotel_id == hotel_id).all()]
        if rec_ids:
            db.query(Feedback).filter(Feedback.recommendation_id.in_(rec_ids)).delete(synchronize_session=False)

        # 2. Delete Price Recommendations & Forecasts
        db.query(PriceRecommendations).filter(PriceRecommendations.hotel_id == hotel_id).delete(synchronize_session=False)
        db.query(Forecasts).filter(Forecasts.hotel_id == hotel_id).delete(synchronize_session=False)

        # 3. Delete Agent Runs and Tool Calls
        run_ids = [r[0] for r in db.query(AgentRuns.agent_run_id).filter(AgentRuns.hotel_id == hotel_id).all()]
        if run_ids:
            db.query(AgentToolCalls).filter(AgentToolCalls.agent_run_id.in_(run_ids)).delete(synchronize_session=False)
        db.query(AgentRuns).filter(AgentRuns.hotel_id == hotel_id).delete(synchronize_session=False)

        # 4. Delete Competitor Rates via Competitor IDs
        comp_ids = [c[0] for c in db.query(CompetitorHotels.competitor_id).filter(CompetitorHotels.hotel_id == hotel_id).all()]
        if comp_ids:
            db.query(CompetitorRates).filter(CompetitorRates.competitor_id.in_(comp_ids)).delete(synchronize_session=False)
        db.query(CompetitorHotels).filter(CompetitorHotels.hotel_id == hotel_id).delete(synchronize_session=False)

        # 5. Delete Inventory, Reservations, Snapshots, Historical Rates
        db.query(RoomInventory).filter(RoomInventory.hotel_id == hotel_id).delete(synchronize_session=False)
        db.query(Reservation).filter(Reservation.hotel_id == hotel_id).delete(synchronize_session=False)
        db.query(DailyBookingSnapshot).filter(DailyBookingSnapshot.hotel_id == hotel_id).delete(synchronize_session=False)
        db.query(HistoricalRates).filter(HistoricalRates.hotel_id == hotel_id).delete(synchronize_session=False)

        # 6. Delete Rate Plans & Room Types
        db.query(RatePlan).filter(RatePlan.hotel_id == hotel_id).delete(synchronize_session=False)
        db.query(RoomType).filter(RoomType.hotel_id == hotel_id).delete(synchronize_session=False)

        # 7. Unlink hotel_id from past AuditLogs
        db.query(AuditLogs).filter(AuditLogs.hotel_id == hotel_id).update({"hotel_id": None}, synchronize_session=False)

        # 8. Delete Hotel record directly via query
        db.query(Hotel).filter(Hotel.hotel_id == hotel_id).delete(synchronize_session=False)

        # 9. Create Audit Log entry for deletion
        audit = AuditLogs(
            user_id=user_id,
            action="DELETE_HOTEL",
            entity_type="Hotel",
            entity_id=str(hotel_id),
            old_value={"hotel_name": hotel_name, "hotel_code": hotel_code},
        )
        db.add(audit)
        db.commit()
        return True

    # --- RoomType Operations ---
    def create_room_type(self, db: Session, hotel_id: int, rt_in: RoomTypeCreate, user_id: int) -> RoomType:
        self.get_hotel(db, hotel_id)  # Ensure hotel exists
        rt = hotel_repository.create_room_type(db, hotel_id, rt_in)

        audit = AuditLogs(
            user_id=user_id,
            action="CREATE_ROOM_TYPE",
            entity_type="RoomType",
            entity_id=str(rt.room_type_id),
            new_value={"room_type_code": rt.room_type_code, "base_price": rt.base_price},
        )
        db.add(audit)
        db.commit()

        return rt

    def list_room_types(self, db: Session, hotel_id: int) -> List[RoomType]:
        self.get_hotel(db, hotel_id)
        return hotel_repository.get_room_types_by_hotel(db, hotel_id)

    # --- RatePlan Operations ---
    def create_rate_plan(self, db: Session, hotel_id: int, rp_in: RatePlanCreate, user_id: int) -> RatePlan:
        self.get_hotel(db, hotel_id)
        rp = hotel_repository.create_rate_plan(db, hotel_id, rp_in)

        audit = AuditLogs(
            user_id=user_id,
            action="CREATE_RATE_PLAN",
            entity_type="RatePlan",
            entity_id=str(rp.rate_plan_id),
            new_value={"rate_plan_code": rp.rate_plan_code, "multiplier": rp.multiplier},
        )
        db.add(audit)
        db.commit()

        return rp

    def list_rate_plans(self, db: Session, hotel_id: int) -> List[RatePlan]:
        self.get_hotel(db, hotel_id)
        return hotel_repository.get_rate_plans_by_hotel(db, hotel_id)


hotel_service = HotelService()
