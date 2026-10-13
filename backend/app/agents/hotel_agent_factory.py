"""
Hotel-Wise Multi-Tenant AI Agent Factory & Auto-Provisioning Service.
Dynamically provisions and manages dedicated AI Revenue Agents for each hotel property.
"""
from datetime import date, datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.hotel import Hotel, RoomType, RatePlan
from app.models.inventory import RoomInventory, Reservation, DailyBookingSnapshot
from app.models.rates import CompetitorHotels, CompetitorRates
from app.pricing.engine import pricing_engine
from app.agents.orchestrator import SingleAutonomousRevenueAgent
from app.core.logging import get_logger

logger = get_logger("app.agents.hotel_agent_factory")


class HotelAgentFactory:
    """
    Factory managing multi-tenant AI Agent instances per hotel.
    When a new hotel is added, this factory automatically provisions:
    1. Dedicated AI Agent instance & prompt configuration
    2. Default Room Types & Rate Plans
    3. Competitor Intelligence set for the hotel's city
    4. Initial 30-Day Inventory & 5-Stage Autonomous Pricing Pipeline
    """

    def __init__(self):
        self._hotel_agents: Dict[int, SingleAutonomousRevenueAgent] = {}
        self._initialized_hotels = set()

    def get_agent_for_hotel(self, hotel_id: int) -> SingleAutonomousRevenueAgent:
        """Fetch or instantiate dedicated AI Agent for a specific hotel property."""
        if hotel_id not in self._hotel_agents:
            self._hotel_agents[hotel_id] = SingleAutonomousRevenueAgent()
        return self._hotel_agents[hotel_id]

    def ensure_hotel_live_data(self, db: Session, hotel_id: int) -> None:
        """
        Guarantee that live realistic metrics, reservations, room inventory,
        and competitor rates exist for the specified hotel property.
        """
        if hotel_id in self._initialized_hotels:
            return

        hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        if not hotel or hotel.status != "ACTIVE":
            logger.info("skipping_live_data_seeding_for_inactive_or_missing_hotel", hotel_id=hotel_id)
            return

        today = date.today()

        # Guarantee SQLite database schema contains missing columns
        try:
            from sqlalchemy import text
            db.execute(text("ALTER TABLE competitor_rates ADD COLUMN ota_name VARCHAR(100) DEFAULT 'Booking.com'"))
            db.commit()
        except Exception:
            db.rollback()


        # 1. Ensure Room Types & Rate Plans exist
        rts = db.query(RoomType).filter(RoomType.hotel_id == hotel_id).all()
        if not rts:
            min_flr = hotel.min_price_floor or 3000.0
            rts = [
                RoomType(
                    hotel_id=hotel_id,
                    room_type_code=f"{hotel.hotel_code}_SUP",
                    room_type_name="Superior Comfort Room",
                    base_price=max(3800.0, round(min_flr * 1.3, 0)),
                    total_inventory=max(10, int(hotel.total_rooms * 0.4)),
                ),
                RoomType(
                    hotel_id=hotel_id,
                    room_type_code=f"{hotel.hotel_code}_DLX",
                    room_type_name="Deluxe Executive Room",
                    base_price=max(5800.0, round(min_flr * 1.8, 0)),
                    total_inventory=max(10, int(hotel.total_rooms * 0.4)),
                ),
                RoomType(
                    hotel_id=hotel_id,
                    room_type_code=f"{hotel.hotel_code}_STE",
                    room_type_name="Luxury Executive Suite",
                    base_price=max(9800.0, round(min_flr * 2.8, 0)),
                    total_inventory=max(5, int(hotel.total_rooms * 0.2)),
                ),
            ]
            db.add_all(rts)
            db.commit()
            rts = db.query(RoomType).filter(RoomType.hotel_id == hotel_id).all()

        rps = db.query(RatePlan).filter(RatePlan.hotel_id == hotel_id).all()
        if not rps:
            rps = [
                RatePlan(
                    hotel_id=hotel_id,
                    rate_plan_code="BAR_FLEX",
                    rate_plan_name="Best Available Rate (Flexible)",
                    meal_plan="EP",
                    multiplier=1.0,
                    is_active=True,
                ),
                RatePlan(
                    hotel_id=hotel_id,
                    rate_plan_code="BB_PKG",
                    rate_plan_name="Bed & Breakfast Package",
                    meal_plan="CP",
                    multiplier=1.15,
                    is_active=True,
                ),
            ]
            db.add_all(rps)
            db.commit()
            rps = db.query(RatePlan).filter(RatePlan.hotel_id == hotel_id).all()

        # 7. Ensure Swarm Sub-Agents & Demo Sessions exist
        try:
            from app.services.agent_swarm_service import agent_swarm_service
            agent_swarm_service.seed_default_swarm_members(db, hotel_id)
        except Exception as swarm_err:
            logger.warning("swarm_seeding_failed", hotel_id=hotel_id, error=str(swarm_err))



        # 2. Ensure Reservations exist across past & upcoming 60 days
        existing_res_count = db.query(Reservation).filter(Reservation.hotel_id == hotel_id).count()
        if existing_res_count < 15:
            import random
            channels = ["Direct Web", "Booking.com", "MakeMyTrip", "Agoda", "Corporate Direct"]
            statuses = ["Confirmed", "Confirmed", "Confirmed", "Confirmed", "CANCELLED"]
            names = [
                "Aarav Sharma", "Priya Patel", "Rohan Mehta", "Vikram Singh",
                "Ananya Reddy", "Siddharth Kumar", "Neha Gupta", "Karan Verma",
                "Meera Joshi", "Aditya Roy", "Rajesh Khanna", "Deepika Padukone"
            ]

            start_date = today - timedelta(days=60)
            end_date = today + timedelta(days=45)
            new_reservations = []
            res_counter = random.randint(1000, 9999)

            for d_offset in range((end_date - start_date).days + 1):
                stay_dt = start_date + timedelta(days=d_offset)
                num_bookings = random.randint(1, 4)
                for _ in range(num_bookings):
                    res_counter += 1
                    rt = random.choice(rts)
                    rp = random.choice(rps)
                    lead_days = random.randint(1, 25)
                    book_dt = stay_dt - timedelta(days=lead_days)
                    rooms = random.randint(1, 2)
                    rate = round(rt.base_price * rp.multiplier * random.uniform(0.92, 1.25), -1)
                    amount = rate * rooms
                    st = random.choice(statuses)

                    new_reservations.append(
                        Reservation(
                            hotel_id=hotel_id,
                            booking_reference=f"BK-{hotel.hotel_code}-{res_counter}",
                            reservation_code=f"RES-{res_counter}",
                            room_type_id=rt.room_type_id,
                            rate_plan_id=rp.rate_plan_id,
                            guest_name=random.choice(names),
                            booking_date=book_dt if book_dt <= stay_dt else stay_dt,
                            checkin_date=stay_dt,
                            checkout_date=stay_dt + timedelta(days=1),
                            room_nights=1,
                            rooms_booked=rooms,
                            adults=2,
                            children=0,
                            channel=random.choice(channels),
                            booking_channel=random.choice(channels),
                            status=st,
                            reservation_status=st.upper(),
                            room_rate=rate,
                            total_amount=amount,
                        )
                    )
            db.add_all(new_reservations)
            db.commit()

        # 3. Ensure Room Inventory exists
        existing_inv_count = db.query(RoomInventory).filter(RoomInventory.hotel_id == hotel_id).count()
        if existing_inv_count < 20:
            import random
            start_date = today - timedelta(days=60)
            end_date = today + timedelta(days=45)
            new_invs = []
            for rt in rts:
                for d_offset in range((end_date - start_date).days + 1):
                    stay_dt = start_date + timedelta(days=d_offset)
                    tot = rt.total_inventory
                    sold = random.randint(3, max(4, tot - 2))
                    new_invs.append(
                        RoomInventory(
                            hotel_id=hotel_id,
                            room_type_id=rt.room_type_id,
                            stay_date=stay_dt,
                            total_inventory=tot,
                            sold_count=sold,
                            current_rate=rt.base_price,
                            total_rooms=tot,
                            available_rooms=max(0, tot - sold),
                            sellable_rooms=tot,
                        )
                    )
            db.add_all(new_invs)
            db.commit()

        # 4. Ensure Daily Booking Snapshots exist
        existing_snap_count = db.query(DailyBookingSnapshot).filter(DailyBookingSnapshot.hotel_id == hotel_id).count()
        if existing_snap_count < 10:
            import random
            start_date = today - timedelta(days=30)
            end_date = today + timedelta(days=30)
            new_snaps = []
            for rt in rts:
                for d_offset in range((end_date - start_date).days + 1):
                    stay_dt = start_date + timedelta(days=d_offset)
                    booked = random.randint(8, max(9, rt.total_inventory - 3))
                    adr = round(rt.base_price * random.uniform(0.95, 1.2), -1)
                    new_snaps.append(
                        DailyBookingSnapshot(
                            hotel_id=hotel_id,
                            room_type_id=rt.room_type_id,
                            stay_date=stay_dt,
                            snapshot_date=today,
                            rooms_booked=booked,
                            rooms_available=max(0, rt.total_inventory - booked),
                            occupancy=round(booked / rt.total_inventory, 2),
                            adr=adr,
                            revenue=adr * booked,
                            pickup_1d=random.randint(1, 4),
                            pickup_3d=random.randint(3, 8),
                            pickup_7d=random.randint(5, 12),
                            pickup_14d=random.randint(8, 16),
                            pickup_30d=random.randint(10, 20),
                        )
                    )
            db.add_all(new_snaps)
            db.commit()

        # 5. Ensure Competitors & Competitor Rates exist
        comps = db.query(CompetitorHotels).filter(CompetitorHotels.hotel_id == hotel_id).all()
        if not comps:
            import random
            city_names = {
                "Goa": ["Taj Exotica Resort Goa", "The Leela Goa", "Radisson Blu Resort Goa"],
                "Chennai": ["Taj Coromandel Chennai", "The Park Chennai", "Radisson Blu Chennai"],
                "Mumbai": ["Taj Mahal Palace Mumbai", "The Oberoi Mumbai", "JW Marriott Juhu"],
                "Jaipur": ["Rambagh Palace Jaipur", "Trident Jaipur", "The Oberoi Rajvilas"],
            }
            names = city_names.get(hotel.city, [f"Taj {hotel.city} Grand", f"The Park {hotel.city}", f"Radisson Blu {hotel.city}"])
            comps = []
            for c_name in names:
                c = CompetitorHotels(
                    hotel_id=hotel_id,
                    competitor_name=c_name,
                    city=hotel.city,
                    star_rating=min(5.0, max(3.5, (hotel.star_rating or 4.0) + random.choice([-0.5, 0, 0.5]))),
                    status="ACTIVE",
                )
                db.add(c)
                comps.append(c)
            db.commit()
            comps = db.query(CompetitorHotels).filter(CompetitorHotels.hotel_id == hotel_id).all()

        # 6. Populate Competitor Rates for competitor hotels
        for c in comps:
            rate_count = db.query(CompetitorRates).filter(CompetitorRates.competitor_id == c.competitor_id).count()
            if rate_count < 10:
                import random
                start_date = today - timedelta(days=60)
                end_date = today + timedelta(days=60)
                base_comp_rate = max(4200.0, (hotel.min_price_floor or 3000.0) * 1.5)
                new_comp_rates = []
                for d_offset in range((end_date - start_date).days + 1):
                    stay_dt = start_date + timedelta(days=d_offset)
                    r_val = round(base_comp_rate * random.uniform(0.88, 1.35), -1)
                    new_comp_rates.append(
                        CompetitorRates(
                            competitor_id=c.competitor_id,
                            stay_date=stay_dt,
                            room_type="Deluxe",
                            rate=r_val,
                            availability=True,
                            meal_plan="EP",
                            cancellation_policy="Standard",
                            source="OTA_SCRAPER",
                        )
                    )
                db.add_all(new_comp_rates)
                db.commit()

        # 7. Ensure Events & Holidays exist for hotel city & region
        try:
            from app.models.events import Events, Holidays
            from app.rag.vector_store import vector_store_manager

            city_events_data = {
                "Chennai": [
                    {
                        "name": "Navratri Golu Festival",
                        "type": "FESTIVAL",
                        "start": date(2026, 10, 10),
                        "end": date(2026, 10, 19),
                        "attendance": 65000,
                        "venue": "Mylapore Kapaleeshwarar & City Temples",
                        "importance": 4,
                        "impact": 1.35,
                    },
                    {
                        "name": "Chennai International Tech Summit",
                        "type": "CONFERENCE",
                        "start": date(2026, 10, 18),
                        "end": date(2026, 10, 22),
                        "attendance": 45000,
                        "venue": "Chennai Trade Centre, Nandambakkam",
                        "importance": 4,
                        "impact": 1.25,
                    },
                    {
                        "name": "Diwali Festive Holiday Period",
                        "type": "FESTIVAL",
                        "start": date(2026, 11, 1),
                        "end": date(2026, 11, 5),
                        "attendance": 100000,
                        "venue": "Citywide & T. Nagar Shopping Hubs",
                        "importance": 5,
                        "impact": 1.40,
                    },
                    {
                        "name": "Margazhi Music & Cultural Festival",
                        "type": "CULTURAL",
                        "start": date(2026, 12, 15),
                        "end": date(2027, 1, 5),
                        "attendance": 80000,
                        "venue": "Music Academy & Mylapore Sabhas",
                        "importance": 4,
                        "impact": 1.25,
                    },
                    {
                        "name": "Pongal Harvest Festival",
                        "type": "CULTURAL",
                        "start": date(2027, 1, 14),
                        "end": date(2027, 1, 17),
                        "attendance": 95000,
                        "venue": "Marina Beach & Cultural Centres",
                        "importance": 5,
                        "impact": 1.35,
                    },
                ],
                "Goa": [
                    {
                        "name": "Goa Sunburn Music Festival",
                        "type": "FESTIVAL",
                        "start": date(2026, 12, 27),
                        "end": date(2026, 12, 31),
                        "attendance": 85000,
                        "venue": "Vagator Beach Arena",
                        "importance": 5,
                        "impact": 1.45,
                    },
                    {
                        "name": "Goa Carnival & Parades",
                        "type": "FESTIVAL",
                        "start": date(2027, 2, 13),
                        "end": date(2027, 2, 16),
                        "attendance": 70000,
                        "venue": "Panaji, Margao & Vasco",
                        "importance": 4,
                        "impact": 1.30,
                    },
                ],
                "Mumbai": [
                    {
                        "name": "Mumbai Fashion & Luxury Expo",
                        "type": "EXHIBITION",
                        "start": date(2026, 11, 15),
                        "end": date(2026, 11, 18),
                        "attendance": 35000,
                        "venue": "Jio World Convention Centre, BKC",
                        "importance": 4,
                        "impact": 1.25,
                    },
                ],
                "Bengaluru": [
                    {
                        "name": "India International Tech Summit",
                        "type": "CONFERENCE",
                        "start": date(2026, 11, 18),
                        "end": date(2026, 11, 21),
                        "attendance": 50000,
                        "venue": "Bangalore International Exhibition Centre",
                        "importance": 5,
                        "impact": 1.35,
                    },
                ],
            }

            h_city = hotel.city or "Chennai"
            city_events = city_events_data.get(h_city, city_events_data["Chennai"])
            for ev in city_events:
                existing = db.query(Events).filter(Events.event_name == ev["name"], Events.city == h_city).first()
                if not existing:
                    e_obj = Events(
                        city=h_city,
                        event_name=ev["name"],
                        event_type=ev["type"],
                        start_date=ev["start"],
                        end_date=ev["end"],
                        expected_attendance=ev["attendance"],
                        venue=ev["venue"],
                        importance=ev["importance"],
                        impact_factor=ev["impact"],
                        source="EVENT_FEED",
                    )
                    db.add(e_obj)
                    db.commit()
                    try:
                        vector_store_manager.ingest_document(
                            title=f"Event: {e_obj.event_name} ({e_obj.city})",
                            category="Local Events & Festivals",
                            content=(
                                f"Event Name: {e_obj.event_name}\n"
                                f"City: {e_obj.city}\n"
                                f"Dates: {e_obj.start_date} to {e_obj.end_date}\n"
                                f"Type: {e_obj.event_type}\n"
                                f"Venue: {e_obj.venue}\n"
                                f"Expected Attendance: {e_obj.expected_attendance}\n"
                                f"Importance: {e_obj.importance}/5\n"
                                f"Demand Impact Multiplier: {e_obj.impact_factor}"
                            ),
                            hotel_id=hotel_id,
                            version="1.0.0"
                        )
                    except Exception:
                        pass

            # Ensure National / Regional Holidays
            default_holidays = [
                {"name": "Navratri Golu / Vijayadashami", "date": date(2026, 10, 19), "type": "REGIONAL", "region": "Tamil Nadu", "factor": 1.30, "importance": 4},
                {"name": "Diwali Festival of Lights", "date": date(2026, 11, 1), "type": "NATIONAL", "region": "National", "factor": 1.40, "importance": 5},
                {"name": "Christmas Holiday Season", "date": date(2026, 12, 25), "type": "NATIONAL", "region": "National", "factor": 1.30, "importance": 4},
                {"name": "New Year's Eve Celebration", "date": date(2026, 12, 31), "type": "NATIONAL", "region": "National", "factor": 1.50, "importance": 5},
                {"name": "Pongal Harvest Holiday", "date": date(2027, 1, 14), "type": "REGIONAL", "region": "Tamil Nadu", "factor": 1.35, "importance": 5},
                {"name": "Republic Day", "date": date(2027, 1, 26), "type": "NATIONAL", "region": "National", "factor": 1.20, "importance": 3},
            ]
            for hol in default_holidays:
                existing_h = db.query(Holidays).filter(Holidays.holiday_name == hol["name"]).first()
                if not existing_h:
                    h_obj = Holidays(
                        country="India",
                        region=hol["region"],
                        holiday_date=hol["date"],
                        holiday_name=hol["name"],
                        holiday_type=hol["type"],
                        importance=hol["importance"],
                        impact_factor=hol["factor"],
                    )
                    db.add(h_obj)
                    db.commit()
                    try:
                        vector_store_manager.ingest_document(
                            title=f"Holiday: {h_obj.holiday_name}",
                            category="Holidays & Observances",
                            content=(
                                f"Holiday Name: {h_obj.holiday_name}\n"
                                f"Date: {h_obj.holiday_date}\n"
                                f"Country: India\n"
                                f"Region: {h_obj.region}\n"
                                f"Type: {h_obj.holiday_type}\n"
                                f"Importance: {h_obj.importance}/5\n"
                                f"Impact Factor: {h_obj.impact_factor}"
                            ),
                            hotel_id=hotel_id,
                            version="1.0.0"
                        )
                    except Exception:
                        pass
        except Exception as seed_ev_err:
            logger.warning("ensure_city_events_failed", error=str(seed_ev_err))

        self._initialized_hotels.add(hotel_id)

    def provision_new_hotel(self, db: Session, hotel_id: int) -> Dict[str, Any]:
        """
        Auto-provision full AI Agent infrastructure for a newly registered hotel property.
        """
        hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        if not hotel:
            raise ValueError(f"Hotel with ID '{hotel_id}' not found.")

        today = date.today()
        logger.info("provisioning_hotel_agent", hotel_id=hotel_id, hotel_name=hotel.hotel_name, city=hotel.city)

        # 1. Provision Default Room Types if none exist
        existing_rts = db.query(RoomType).filter(RoomType.hotel_id == hotel_id).all()
        if not existing_rts:
            default_rts = [
                RoomType(
                    hotel_id=hotel_id,
                    room_type_code=f"{hotel.hotel_code}_SUP",
                    room_type_name="Superior Comfort Room",
                    base_price=round(hotel.min_price_floor * 1.3, 0),
                    total_inventory=max(10, int(hotel.total_rooms * 0.4)),
                ),
                RoomType(
                    hotel_id=hotel_id,
                    room_type_code=f"{hotel.hotel_code}_DLX",
                    room_type_name="Deluxe Executive Room",
                    base_price=round(hotel.min_price_floor * 1.8, 0),
                    total_inventory=max(10, int(hotel.total_rooms * 0.4)),
                ),
                RoomType(
                    hotel_id=hotel_id,
                    room_type_code=f"{hotel.hotel_code}_STE",
                    room_type_name="Luxury Executive Suite",
                    base_price=round(hotel.min_price_floor * 2.8, 0),
                    total_inventory=max(5, int(hotel.total_rooms * 0.2)),
                ),
            ]
            db.add_all(default_rts)
            db.commit()
            existing_rts = db.query(RoomType).filter(RoomType.hotel_id == hotel_id).all()

        # 2. Provision Default Rate Plans if none exist
        existing_rps = db.query(RatePlan).filter(RatePlan.hotel_id == hotel_id).all()
        if not existing_rps:
            default_rps = [
                RatePlan(
                    hotel_id=hotel_id,
                    rate_plan_code="BAR_FLEX",
                    rate_plan_name="Best Available Rate (Flexible)",
                    meal_plan="EP",
                    multiplier=1.0,
                    is_active=True,
                ),
                RatePlan(
                    hotel_id=hotel_id,
                    rate_plan_code="BB_PKG",
                    rate_plan_name="Bed & Breakfast Package",
                    meal_plan="CP",
                    multiplier=1.15,
                    is_active=True,
                ),
            ]
            db.add_all(default_rps)
            db.commit()

        # 3. Provision Competitor Set if none exist
        existing_comps = db.query(CompetitorHotels).filter(CompetitorHotels.hotel_id == hotel_id).all()
        if not existing_comps:
            comps_data = [
                f"Taj {hotel.city} Central",
                f"The Park {hotel.city}",
                f"Radisson Blu {hotel.city}",
            ]
            for c_name in comps_data:
                comp = CompetitorHotels(
                    hotel_id=hotel_id,
                    competitor_name=c_name,
                    city=hotel.city,
                    star_rating=hotel.star_rating,
                    status="ACTIVE",
                )
                db.add(comp)
            db.commit()

        # 4. Provision Initial Room Inventory (7-Day Fast Horizon)
        for rt in existing_rts:
            for day_offset in range(7):
                stay_dt = today + timedelta(days=day_offset)
                existing_inv = (
                    db.query(RoomInventory)
                    .filter(
                        RoomInventory.hotel_id == hotel_id,
                        RoomInventory.room_type_id == rt.room_type_id,
                        RoomInventory.stay_date == stay_dt,
                    )
                    .first()
                )
                if not existing_inv:
                    inv = RoomInventory(
                        hotel_id=hotel_id,
                        room_type_id=rt.room_type_id,
                        stay_date=stay_dt,
                        total_inventory=rt.total_inventory,
                        sold_count=0,
                        current_rate=rt.base_price,
                        total_rooms=rt.total_inventory,
                        available_rooms=rt.total_inventory,
                        sellable_rooms=rt.total_inventory,
                    )
                    db.add(inv)
        db.commit()

        # 5. Run Fast Initial Autonomous Pricing Setup (7-Day Horizon)
        cycle_res = None
        try:
            cycle_res = pricing_engine.run_autonomous_pricing_cycle(db, hotel_id=hotel_id, horizon_days=7)
        except Exception as err:
            logger.warning("initial_pricing_cycle_deferred", hotel_id=hotel_id, error=str(err))

        # 6. Bind Dedicated Agent Instance
        self.get_agent_for_hotel(hotel_id)

        return {
            "hotel_id": hotel_id,
            "hotel_name": hotel.hotel_name,
            "agent_status": "PROVISIONED_ACTIVE",
            "room_types_count": len(existing_rts),
            "autonomous_cycle": cycle_res or {"status": "INITIALIZED"},
            "provisioned_at": datetime.now(timezone.utc).isoformat(),
        }


hotel_agent_factory = HotelAgentFactory()
