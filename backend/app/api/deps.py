"""
FastAPI dependency functions for Database session, Authentication, and RBAC authorization middleware.
"""
from typing import Callable, List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_token
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.models.user import User
from app.repositories.user_repository import user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Extract and validate current authenticated user from JWT bearer token."""
    payload = decode_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError("Token payload missing subject ID claim")

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise AuthenticationError("Invalid user ID format in token")

    user = user_repository.get_by_id(db, user_id=user_id)
    if not user:
        raise AuthenticationError("Authenticated user no longer exists")
    if not user.is_active:
        raise AuthenticationError("User account is inactive")
    return user


def require_roles(allowed_roles: List[str]) -> Callable:
    """
    Dependency factory verifying that the authenticated user possesses one of the allowed RBAC roles.
    Allowed roles: Super Admin, Administrator, Revenue Manager, Hotel Manager, Analyst, Read-only User.
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Super Admin has global override permission across all resources
        if current_user.role == "Super Admin" or current_user.role in allowed_roles:
            return current_user
        raise PermissionDeniedError(
            f"Role '{current_user.role}' is not authorized to access this resource. Required: {allowed_roles}"
        )

    return role_checker


def verify_hotel_access(hotel_id: int, current_user: User, db: Optional[Session] = None) -> None:
    """
    Verify that user has authorization to view/modify data for the specified hotel_id.
    - INACTIVE hotels can ONLY be accessed or viewed by 'Super Admin'.
    - Active hotels: Super Admin, Administrators, and Revenue Managers have global access across all properties.
    - Other roles are constrained by user.assigned_hotels list.
    """
    if db is not None:
        from app.models.hotel import Hotel
        target_hotel = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
        if target_hotel and target_hotel.status != "ACTIVE" and current_user.role != "Super Admin":
            raise PermissionDeniedError(
                f"Hotel ID '{hotel_id}' ({target_hotel.hotel_name}) is INACTIVE. Only Super Admin can view details or process data for inactive properties."
            )

    if current_user.role == "Super Admin":
        return

    if current_user.role in ["Administrator", "Revenue Manager"]:
        return

    if not current_user.assigned_hotels:
        raise PermissionDeniedError(f"User is not assigned to hotel ID '{hotel_id}'.")

    assigned_ids = [
        int(h.strip())
        for h in current_user.assigned_hotels.split(",")
        if h.strip().isdigit()
    ]
    if hotel_id not in assigned_ids:
        raise PermissionDeniedError(f"Access denied for hotel ID '{hotel_id}'.")

