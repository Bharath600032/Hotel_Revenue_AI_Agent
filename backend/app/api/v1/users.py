"""
Super Admin User Management & Access Control REST API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.db.session import get_db
from app.api.deps import get_current_user, require_roles
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.core.security import get_password_hash
from app.core.exceptions import ResourceNotFoundError, DataValidationError

router = APIRouter(prefix="/admin/users", tags=["Super Admin User Management"])


class AdminUserResponse(BaseModel):
    user_id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    assigned_hotels: Optional[str] = None

    class Config:
        from_attributes = True


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str  # Super Admin, Administrator, Revenue Manager, Hotel Manager, Analyst, Read-only User
    assigned_hotels: Optional[str] = None  # Comma-separated hotel IDs e.g. "1,2,3"


class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    assigned_hotels: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


@router.get("", response_model=List[AdminUserResponse])
async def list_all_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles(["Super Admin", "Administrator"])),
):
    """Super Admin endpoint to list all user accounts and assigned hotel access permissions."""
    return db.query(User).order_by(User.user_id).all()


@router.post("", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles(["Super Admin", "Administrator"])),
):
    """Super Admin endpoint to create new user account with role & hotel permissions."""
    existing = user_repository.get_by_email(db, email=payload.email)
    if existing:
        raise DataValidationError(f"User with email '{payload.email}' already exists.")

    new_user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        is_active=True,
        assigned_hotels=payload.assigned_hotels,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.put("/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles(["Super Admin", "Administrator"])),
):
    """Super Admin endpoint to update user role, assigned hotel access, or active status."""
    target_user = db.query(User).filter(User.user_id == user_id).first()
    if not target_user:
        raise ResourceNotFoundError("User", user_id)

    if payload.full_name is not None:
        target_user.full_name = payload.full_name
    if payload.role is not None:
        target_user.role = payload.role
    if payload.assigned_hotels is not None:
        target_user.assigned_hotels = payload.assigned_hotels
    if payload.is_active is not None:
        target_user.is_active = payload.is_active
    if payload.password:
        target_user.password_hash = get_password_hash(payload.password)

    db.commit()
    db.refresh(target_user)
    return target_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles(["Super Admin", "Administrator"])),
):
    """Super Admin endpoint to delete a user account."""
    target_user = db.query(User).filter(User.user_id == user_id).first()
    if not target_user:
        raise ResourceNotFoundError("User", user_id)

    db.delete(target_user)
    db.commit()
