#!/usr/bin/env python3
"""
Synthetic Demo Data Seeder for Hotel Autonomous Revenue AI Agent.

Seeds database with:
- 5 Realistic Hotel Properties across prime Indian hospitality destinations
- 4 Room Types per property (Standard, Deluxe, Executive, Suite/Villa)
- 3 Rate Plans per property (BAR Flexible, B&B Package, Non-Refundable)
- 365 Days of Historical & Future Room Inventory, Rates, and Occupancy
- 1,000+ Historical & Future Guest Reservations with realistic channel mix
- Competitor Rate Feeds (3 Competitor Hotels per property, 90-day pricing window)
- Local Events, National Holidays & Attendance-based Demand Multipliers
- Weather Forecast Records (Temperature, Precipitation, Conditions)
- Initial Price Recommendations & Immutable Compliance Audit Logs
"""

import sys
import os
import random
from datetime import date, datetime, timedelta
from pathlib import Path

# Add backend directory to path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models import (
    User,
    Hotel,
    RoomType,
    RatePlan,
    RoomInventory,
    HistoricalRate,
    Reservation,
    DailyBookingSnapshot,
    CompetitorHotel,
    CompetitorRate,
    Event,
    Holiday,
    WeatherForecast,
    PriceRecommendation,
    AuditLog,
)

from app.core.security import get_password_hash


HOTELS_DATA = [
    {
        "hotel_code": "HTL_CUTEORANGE",
        "hotel_name": "Cute Orange Hotel",
        "city": "Chennai",
        "country": "India",
        "total_rooms": 45,
        "star_rating": 4.0,
        "currency": "INR",
        "min_price_floor": 2500.0,
        "max_price_ceiling": 18000.0,
        "max_daily_price_change_pct": 20.0,
        "require_approval_above_change_pct": 10.0,
        "room_types": [
            {"code": "CUTE_SUP", "name": "Superior Comfort Room", "base_price": 3200.0, "total": 20},
            {"code": "CUTE_DLX", "name": "Deluxe Executive Room", "base_price": 4500.0, "total": 15},
            {"code": "CUTE_STE", "name": "Luxury Orange Suite", "base_price": 7200.0, "total": 10},
        ],
        "competitors": ["Taj Coromandel Chennai", "The Park Chennai", "Radisson Blu City Centre Chennai"],
    },
    {
        "hotel_code": "HTL_GOA",
        "hotel_name": "Grand Azure Beach Resort & Spa",
        "city": "Goa",
        "country": "India",
        "total_rooms": 120,
        "star_rating": 5.0,
        "currency": "INR",
        "min_price_floor": 4500.0,
        "max_price_ceiling": 35000.0,
        "max_daily_price_change_pct": 20.0,
        "require_approval_above_change_pct": 10.0,
        "room_types": [
            {"code": "STD_GARDEN", "name": "Standard Garden View", "base_price": 5500.0, "total": 40},
            {"code": "DLX_OCEAN", "name": "Deluxe Ocean View", "base_price": 8500.0, "total": 40},
            {"code": "EXEC_SUITE", "name": "Executive Ocean Suite", "base_price": 14000.0, "total": 25},
            {"code": "ROYAL_VILLA", "name": "Royal Beachfront Villa", "base_price": 25000.0, "total": 15},
        ],
        "competitors": ["Taj Exotica Goa", "The Leela Goa", "W Goa"],
    },
    {
        "hotel_code": "HTL_MUM",
        "hotel_name": "Imperial Tower Financial Center",
        "city": "Mumbai",
        "country": "India",
        "total_rooms": 180,
        "star_rating": 5.0,
        "currency": "INR",
        "min_price_floor": 6000.0,
        "max_price_ceiling": 40000.0,
        "max_daily_price_change_pct": 20.0,
        "require_approval_above_change_pct": 10.0,
        "room_types": [
            {"code": "CORP_KING", "name": "Corporate Deluxe King", "base_price": 9000.0, "total": 70},
            {"code": "EXEC_CLUB", "name": "Executive Club Lounge Access", "base_price": 13500.0, "total": 60},
            {"code": "PREM_SUITE", "name": "Premier Skyline Suite", "base_price": 22000.0, "total": 35},
            {"code": "PRES_SUITE", "name": "Presidential Penthouse", "base_price": 38000.0, "total": 15},
        ],
        "competitors": ["The St. Regis Mumbai", "Trident Nariman Point", "Four Seasons Mumbai"],
    },
    {
        "hotel_code": "HTL_JAI",
        "hotel_name": "Royal Rajputana Heritage Palace",
        "city": "Jaipur",
        "country": "India",
        "total_rooms": 90,
        "star_rating": 5.0,
        "currency": "INR",
        "min_price_floor": 5000.0,
        "max_price_ceiling": 45000.0,
        "max_daily_price_change_pct": 25.0,
        "require_approval_above_change_pct": 10.0,
        "room_types": [
            {"code": "HERITAGE_RM", "name": "Heritage Courtyard Room", "base_price": 7000.0, "total": 35},
            {"code": "ROYAL_DLX", "name": "Royal Deluxe Chamber", "base_price": 11000.0, "total": 30},
            {"code": "MAHARAJA_STE", "name": "Maharaja Heritage Suite", "base_price": 24000.0, "total": 15},
            {"code": "PALACE_HAVELI", "name": "Private Palace Haveli", "base_price": 42000.0, "total": 10},
        ],
        "competitors": ["Rambagh Palace Jaipur", "Oberoi Rajvilas", "Fairmont Jaipur"],
    },
    {
        "hotel_code": "HTL_BLR",
        "hotel_name": "Silicon Valley Tech Park Hotel",
        "city": "Bengaluru",
        "country": "India",
        "total_rooms": 150,
        "star_rating": 4.5,
        "currency": "INR",
        "min_price_floor": 4000.0,
        "max_price_ceiling": 25000.0,
        "max_daily_price_change_pct": 20.0,
        "require_approval_above_change_pct": 10.0,
        "room_types": [
            {"code": "SMART_STUDIO", "name": "Smart Tech Studio", "base_price": 5200.0, "total": 60},
            {"code": "EXEC_CORP", "name": "Executive Corporate Room", "base_price": 7800.0, "total": 50},
            {"code": "WORK_SUITE", "name": "Innovation Work Suite", "base_price": 12500.0, "total": 25},
            {"code": "LOFT_STE", "name": "Skyline Loft Suite", "base_price": 18500.0, "total": 15},
        ],
        "competitors": ["The Leela Palace Bengaluru", "JW Marriott Bengaluru", "The Oberoi Bengaluru"],
    },
    {
        "hotel_code": "HTL_KER",
        "hotel_name": "Backwater Serenity Eco Luxury Resort",
        "city": "Kumarakom",
        "country": "India",
        "total_rooms": 60,
        "star_rating": 5.0,
        "currency": "INR",
        "min_price_floor": 6000.0,
        "max_price_ceiling": 50000.0,
        "max_daily_price_change_pct": 20.0,
        "require_approval_above_change_pct": 10.0,
        "room_types": [
            {"code": "ECO_COTTAGE", "name": "Garden Eco Cottage", "base_price": 8500.0, "total": 20},
            {"code": "LAKE_VILLA", "name": "Vembanad Lakeview Villa", "base_price": 15000.0, "total": 20},
            {"code": "POOL_VILLA", "name": "Private Pool Heritage Villa", "base_price": 28000.0, "total": 12},
            {"code": "HOUSEBOAT_STE", "name": "Luxury Backwater Houseboat Suite", "base_price": 45000.0, "total": 8},
        ],
        "competitors": ["Kumarakom Lake Resort", "Zuri Kumarakom", "Taj Kumarakom Resort"],
    },
]

CHANNELS = ["Direct", "OTA", "Corporate", "GDS", "Wholesale"]
GUEST_NAMES = [
    "Aarav Sharma", "Ananya Iyer", "Rohan Mehta", "Priya Nair", "Vikram Patel",
    "Siddharth Verma", "Kavya Reddy", "Arjun Kapoor", "Neha Gupta", "Aditya Joshi",
    "Rahul Mukerjee", "Divya Deshmukh", "Karan Malhotra", "Ritu Sengupta", "Amitabh Roy",
    "Pooja Saxena", "Tarun Bansal", "Sneha Kulkarni", "Deepak Rao", "Sunita Menon",
]

EVENTS_DATA = [
    {"name": "Goa Sunburn Music Festival", "city": "Goa", "attendance": 85000, "factor": 1.45, "offset_days": 105},
    {"name": "India International Tech Summit", "city": "Bengaluru", "attendance": 45000, "factor": 1.35, "offset_days": 40},
    {"name": "Mumbai Fashion & Luxury Expo", "city": "Mumbai", "attendance": 30000, "factor": 1.25, "offset_days": 60},
    {"name": "Jaipur Literature Festival", "city": "Jaipur", "attendance": 120000, "factor": 1.50, "offset_days": 130},
    {"name": "Kerala Backwater Regatta & Snake Boat Race", "city": "Kumarakom", "attendance": 50000, "factor": 1.40, "offset_days": 150},
]

HOLIDAYS_DATA = [
    {"name": "Diwali Festival of Lights", "factor": 1.40, "offset_days": 45},
    {"name": "New Year's Eve Celebration", "factor": 1.60, "offset_days": 110},
    {"name": "Holi Festival of Colors", "factor": 1.25, "offset_days": 180},
    {"name": "Independence Day Long Weekend", "factor": 1.20, "offset_days": -25},
    {"name": "Christmas Holiday Season", "factor": 1.50, "offset_days": 104},
]


def seed_demo_data():
    print("==================================================")
    print("      HOTEL REVENUE AI AGENT - DEMO DATA SEEDER   ")
    print("==================================================")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Seed Users
    print("\n[1/7] Seeding System Users & Roles...")
    users_to_seed = [
        {
            "email": "superadmin@cuteorange.in",
            "password": "SuperAdmin123!",
            "full_name": "Super Administrator",
            "role": "Super Admin",
        },
        {
            "email": "admin@revenueagent.ai",
            "password": "Admin123!Pass",
            "full_name": "Chief Revenue Administrator",
            "role": "Administrator",
        },
        {
            "email": "manager@revenueagent.ai",
            "password": "Manager123!Pass",
            "full_name": "Senior Revenue Manager",
            "role": "Revenue Manager",
        },
        {
            "email": "analyst@revenueagent.ai",
            "password": "Analyst123!Pass",
            "full_name": "Pricing Analyst",
            "role": "Analyst",
        },
        {
            "email": "admin@hotelrevenue.ai",
            "password": "AdminPass123!",
            "full_name": "Demo Hotel Administrator",
            "role": "Administrator",
        },
    ]

    for u_data in users_to_seed:
        existing_user = db.query(User).filter(User.email == u_data["email"]).first()
        if existing_user:
            existing_user.password_hash = get_password_hash(u_data["password"])
            existing_user.is_active = True
        else:
            db.add(
                User(
                    email=u_data["email"],
                    password_hash=get_password_hash(u_data["password"]),
                    full_name=u_data["full_name"],
                    role=u_data["role"],
                    is_active=True,
                )
            )
    db.commit()
    print(" -> Users created/updated: Admin, Revenue Manager, Analyst")


    today = date.today()

    # 2. Seed Hotels, Room Types, Rate Plans, Competitors
    print("\n[2/7] Seeding 5 Properties, Room Types, Rate Plans & Competitor Sets...")
    hotel_entities = []

    for h_info in HOTELS_DATA:
        hotel = db.query(Hotel).filter(Hotel.hotel_code == h_info["hotel_code"]).first()
        if not hotel:
            hotel = Hotel(
                hotel_code=h_info["hotel_code"],
                hotel_name=h_info["hotel_name"],
                city=h_info["city"],
                country=h_info["country"],
                total_rooms=h_info["total_rooms"],
                star_rating=h_info["star_rating"],
                currency=h_info["currency"],
                min_price_floor=h_info["min_price_floor"],
                max_price_ceiling=h_info["max_price_ceiling"],
                max_daily_price_change_pct=h_info["max_daily_price_change_pct"],
                require_approval_above_change_pct=h_info["require_approval_above_change_pct"],
                automation_enabled=True,
            )
            db.add(hotel)
            db.commit()
            db.refresh(hotel)

            # Room Types
            for rt in h_info["room_types"]:
                db.add(RoomType(
                    hotel_id=hotel.hotel_id,
                    room_type_code=rt["code"],
                    room_type_name=rt["name"],
                    base_price=rt["base_price"],
                    total_inventory=rt["total"],
                ))

            # Rate Plans
            db.add(RatePlan(
                hotel_id=hotel.hotel_id,
                rate_plan_code="BAR_FLEX",
                rate_plan_name="Best Available Rate (Flexible Cancellation)",
                meal_plan="EP",
                multiplier=1.0,
                is_active=True,
            ))
            db.add(RatePlan(
                hotel_id=hotel.hotel_id,
                rate_plan_code="BB_PKG",
                rate_plan_name="Bed & Breakfast Buffet Package",
                meal_plan="CP",
                multiplier=1.15,
                is_active=True,
            ))
            db.add(RatePlan(
                hotel_id=hotel.hotel_id,
                rate_plan_code="NON_REF",
                rate_plan_name="Advance Purchase Non-Refundable (15% Off)",
                meal_plan="EP",
                multiplier=0.85,
                is_active=True,
            ))

            # Competitors
            for c_name in h_info["competitors"]:
                comp = CompetitorHotel(
                    hotel_id=hotel.hotel_id,
                    competitor_name=c_name,
                    star_rating=5.0,
                    distance_km=round(random.uniform(0.5, 4.5), 1),
                    is_active=True,
                )
                db.add(comp)

            db.commit()
            print(f" -> Property created: {hotel.hotel_name} ({hotel.city})")

        hotel_entities.append(hotel)

    # 3. Seed Events & Holidays
    print("\n[3/7] Seeding Local Events & National Holidays...")
    for ev in EVENTS_DATA:
        ev_date = today + timedelta(days=ev["offset_days"])
        if not db.query(Event).filter(Event.event_name == ev["name"]).first():
            db.add(Event(
                city=ev["city"],
                event_name=ev["name"],
                start_date=ev_date,
                end_date=ev_date + timedelta(days=3),
                expected_attendance=ev["attendance"],
                impact_factor=ev["factor"],
            ))
    for hol in HOLIDAYS_DATA:
        h_date = today + timedelta(days=hol["offset_days"])
        if not db.query(Holiday).filter(Holiday.holiday_name == hol["name"]).first():
            db.add(Holiday(
                holiday_date=h_date,
                holiday_name=hol["name"],
                country="India",
                impact_factor=hol["factor"],
            ))
    db.commit()
    print(" -> Events and Holidays created.")

    # 4. Seed Inventory, Reservations, Snapshots, Competitor Rates (365 Days)
    print("\n[4/7] Generating 365 Days of Inventory, Rates, Competitor Feeds & Reservations...")

    for hotel in hotel_entities:
        room_types = db.query(RoomType).filter(RoomType.hotel_id == hotel.hotel_id).all()
        rate_plans = db.query(RatePlan).filter(RatePlan.hotel_id == hotel.hotel_id).all()
        competitors = db.query(CompetitorHotel).filter(CompetitorHotel.hotel_id == hotel.hotel_id).all()

        bar_plan = next((rp for rp in rate_plans if rp.rate_plan_code == "BAR_FLEX"), rate_plans[0])

        # Generate 180 past days + 180 future days
        start_date = today - timedelta(days=90)
        end_date = today + timedelta(days=180)
        curr_date = start_date

        res_count = 0
        inv_count = 0

        while curr_date <= end_date:
            day_offset = (curr_date - today).days

            # Seasonality multiplier
            day_of_week = curr_date.weekday()
            is_weekend = day_of_week in [4, 5, 6]
            seasonal_factor = 1.25 if is_weekend else 0.95

            for rt in room_types:
                # Target rate
                curr_rate = round(rt.base_price * seasonal_factor * random.uniform(0.95, 1.10), 2)
                sold = random.randint(int(rt.total_inventory * 0.3), int(rt.total_inventory * 0.92))

                inv = RoomInventory(
                    hotel_id=hotel.hotel_id,
                    room_type_id=rt.room_type_id,
                    stay_date=curr_date,
                    total_inventory=rt.total_inventory,
                    sold_count=sold if curr_date <= today else random.randint(5, sold),
                    current_rate=curr_rate,
                    out_of_order=0,
                )
                db.add(inv)
                inv_count += 1

                # Reservations
                if curr_date <= today + timedelta(days=30):
                    num_res = random.randint(1, 4)
                    for r_idx in range(num_res):
                        lead_time = random.randint(1, 45)
                        b_date = curr_date - timedelta(days=lead_time)
                        guest = random.choice(GUEST_NAMES)
                        chan = random.choice(CHANNELS)
                        res = Reservation(
                            hotel_id=hotel.hotel_id,
                            room_type_id=rt.room_type_id,
                            rate_plan_id=bar_plan.rate_plan_id,
                            booking_reference=f"RES-{hotel.hotel_code}-{curr_date.strftime('%m%d')}-{rt.room_type_id}-{r_idx}",
                            guest_name=guest,
                            booking_date=b_date,
                            checkin_date=curr_date,
                            checkout_date=curr_date + timedelta(days=1),
                            room_nights=1,
                            room_rate=curr_rate,
                            total_amount=curr_rate,
                            status="Confirmed",
                            channel=chan,
                        )
                        db.add(res)
                        res_count += 1

            # Competitor rates (-30 to +60 days)
            if -30 <= day_offset <= 60:
                for comp in competitors:
                    comp_rate = round(hotel.min_price_floor * random.uniform(1.2, 2.5), 2)
                    cr = CompetitorRate(
                        competitor_id=comp.competitor_id,
                        stay_date=curr_date,
                        room_type_category="Standard / Deluxe",
                        scraped_rate=comp_rate,
                        scraped_timestamp=today,
                    )
                    db.add(cr)

            # Weather
            wf = WeatherForecast(
                city=hotel.city,
                forecast_date=curr_date,
                temp_celsius=round(random.uniform(22.0, 34.0), 1),
                rainfall_mm=round(random.uniform(0.0, 15.0), 1),
                condition=random.choice(["Sunny", "Clear", "Partly Cloudy", "Light Rain"]),
            )
            db.add(wf)

            curr_date += timedelta(days=1)

        db.commit()
        print(f" -> {hotel.hotel_code}: Seeded {inv_count} Inventory records, {res_count} Reservations")

    # 5. Seed Price Recommendations & Audit Logs
    print("\n[5/7] Seeding Pricing Recommendations & Guardrail Verification Logs...")
    primary_hotel = hotel_entities[0]
    rt_primary = db.query(RoomType).filter(RoomType.hotel_id == primary_hotel.hotel_id).first()

    for i in range(5):
        target_d = today + timedelta(days=i + 1)
        rec = PriceRecommendation(
            hotel_id=primary_hotel.hotel_id,
            room_type_id=rt_primary.room_type_id,
            stay_date=target_d,
            current_rate=rt_primary.base_price,
            recommended_rate=rt_primary.base_price * (1.12 + (i * 0.02)),
            min_price_floor=primary_hotel.min_price_floor,
            max_price_ceiling=primary_hotel.max_price_ceiling,
            demand_score=0.82 + (i * 0.03),
            competitor_median_rate=rt_primary.base_price * 1.15,
            price_change_pct=12.0 + (i * 2.0),
            requires_approval=True,
            status="Pending",
            reasoning=f"High occupancy forecast ({75+i*4}%) combined with local event demand uplift.",
        )
        db.add(rec)

    db.add(AuditLog(
        user_id=1,
        hotel_id=primary_hotel.hotel_id,
        action="SEED_DEMO_DATA",
        entity_type="SYSTEM",
        details="Seeded complete synthetic dataset across 5 properties, 365 inventory days, and competitor feeds.",
    ))
    db.commit()

    print("\n==================================================")
    print("         SUCCESS: DEMO DATA SEEDING COMPLETE      ")
    print("==================================================")
    print(f" Database successfully populated with 5 hotels, 20 room types,")
    print(f" 365 inventory days per property, competitor feeds, and event datasets.")
    db.close()


if __name__ == "__main__":
    seed_demo_data()
