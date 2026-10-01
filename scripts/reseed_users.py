#!/usr/bin/env python3
"""
Credential Reseeder Script — Guarantees all demo users exist with valid password hashes.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models.user import User
from app.core.security import get_password_hash


def reseed_users():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    demo_users = [
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

    for u in demo_users:
        user = db.query(User).filter(User.email == u["email"].lower()).first()
        if not user:
            user = User(
                email=u["email"].lower(),
                full_name=u["full_name"],
                role=u["role"],
                is_active=True,
            )
            db.add(user)

        user.password_hash = get_password_hash(u["password"])
        user.is_active = True

    db.commit()
    print("✅ Successfully re-seeded all demo user credentials in database!")
    db.close()


if __name__ == "__main__":
    reseed_users()
