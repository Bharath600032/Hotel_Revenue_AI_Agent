"""
Database table initialization and seeding helper for DEMO and development environments.
"""
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models import User, Hotel, RoomType, RatePlan
from app.core.security import get_password_hash
from app.core.logging import get_logger

logger = get_logger("app.db.init_db")


def init_db(db: Session) -> None:
    """Initialize database tables and seed default role accounts."""
    logger.info("creating_database_tables")
    Base.metadata.create_all(bind=engine)

    # Auto-migrate SQLite schema for missing columns
    try:
        from sqlalchemy import text
        db.execute(text("ALTER TABLE competitor_rates ADD COLUMN ota_name VARCHAR(100) DEFAULT 'Booking.com'"))
        db.commit()
        logger.info("migrated_competitor_rates_ota_name_column")
    except Exception:
        db.rollback()


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
            "full_name": "Revenue Administrator",
            "role": "Administrator",
        },
    ]

    for u_data in users_to_seed:
        user = db.query(User).filter(User.email == u_data["email"]).first()
        if not user:
            logger.info("seeding_user", email=u_data["email"], role=u_data["role"])
            user = User(
                email=u_data["email"],
                password_hash=get_password_hash(u_data["password"]),
                full_name=u_data["full_name"],
                role=u_data["role"],
                is_active=True,
                assigned_hotels="1,2,3,4,5",
            )
            db.add(user)
        else:
            # Ensure credentials and active status match
            user.password_hash = get_password_hash(u_data["password"])
            user.role = u_data["role"]
            user.is_active = True
    db.commit()

    # Seed live metric data and competitor rates for all hotel properties
    from app.agents.hotel_agent_factory import hotel_agent_factory
    all_hotels = db.query(Hotel).all()
    for h in all_hotels:
        try:
            hotel_agent_factory.ensure_hotel_live_data(db, h.hotel_id)
        except Exception as err:
            logger.warning("hotel_live_data_seeding_failed", hotel_id=h.hotel_id, error=str(err))


if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
    db.close()
