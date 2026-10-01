"""
User model schema for authentication and Role-Based Access Control (RBAC).
"""
from __future__ import annotations

from typing import Optional
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50),
        default="Revenue Manager",
        nullable=False,
        index=True,
    )  # Administrator, Revenue Manager, Hotel Manager, Analyst, Read-only User
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    assigned_hotels: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="Comma-separated hotel IDs"
    )
