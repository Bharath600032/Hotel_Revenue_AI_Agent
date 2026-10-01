"""
Authentication REST API endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    UserCreate,
)
from app.services.auth_service import auth_service
from app.repositories.user_repository import user_repository
from app.api.deps import get_current_user, require_roles
from app.core.security import decode_token
from app.core.exceptions import AuthenticationError, DataValidationError
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user credentials and return access + refresh JWT tokens."""
    user = auth_service.authenticate_user(db, email=payload.email, password=payload.password)
    return auth_service.generate_token_response(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    decoded = decode_token(payload.refresh_token)
    if decoded.get("type") != "refresh":
        raise AuthenticationError("Invalid token type provided for refresh")

    user_id = int(decoded["sub"])
    user = user_repository.get_by_id(db, user_id=user_id)
    if not user or not user.is_active:
        raise AuthenticationError("User is inactive or no longer exists")

    return auth_service.generate_token_response(user)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve profile information for currently authenticated user."""
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles(["Administrator"])),
):
    """Admin-only endpoint to create new user accounts with RBAC roles."""
    existing = user_repository.get_by_email(db, email=payload.email)
    if existing:
        raise DataValidationError(f"User with email '{payload.email}' already exists.")

    new_user = user_repository.create(db, user_in=payload)
    return new_user
