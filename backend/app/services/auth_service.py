"""
Authentication service handling credential validation and JWT token issuance.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.exceptions import AuthenticationError
from app.schemas.user import TokenResponse, UserResponse
from app.core.config import settings


class AuthService:
    def authenticate_user(self, db: Session, email: str, password: str) -> User:
        """Authenticate user credentials and return User instance."""
        user = user_repository.get_by_email(db, email=email)
        if not user:
            raise AuthenticationError("Invalid email or password.")
        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")
        if not user.is_active:
            raise AuthenticationError("User account is deactivated.")
        return user

    def generate_token_response(self, user: User) -> TokenResponse:
        """Generate JWT access and refresh token response payload for user."""
        hotel_ids = []
        if user.assigned_hotels:
            try:
                hotel_ids = [int(h.strip()) for h in user.assigned_hotels.split(",") if h.strip()]
            except ValueError:
                hotel_ids = []

        access_token = create_access_token(
            subject=user.user_id,
            role=user.role,
            hotel_ids=hotel_ids,
        )
        refresh_token = create_refresh_token(subject=user.user_id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )


auth_service = AuthService()
