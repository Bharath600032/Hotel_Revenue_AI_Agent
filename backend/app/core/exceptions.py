"""
Custom application exception hierarchy for Hotel Autonomous Revenue AI Agent.
Mapped directly to HTTP response status codes and structured JSON errors.
"""
from typing import Any, Dict, Optional
from fastapi import status


class HotelRevenueException(Exception):
    """Base exception class for all hotel revenue system errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_SERVER_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class AuthenticationError(HotelRevenueException):
    """Raised when authentication fails or JWT token is invalid/expired."""

    def __init__(self, message: str = "Invalid authentication credentials"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_FAILED",
        )


class PermissionDeniedError(HotelRevenueException):
    """Raised when an authenticated user lacks RBAC permissions for an operation."""

    def __init__(self, message: str = "Permission denied for this operation"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="PERMISSION_DENIED",
        )


class ResourceNotFoundError(HotelRevenueException):
    """Raised when a requested database entity or resource is not found."""

    def __init__(self, entity_name: str, entity_id: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{entity_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={"entity_name": entity_name, "entity_id": str(entity_id)},
        )


class DataValidationError(HotelRevenueException):
    """Raised when imported data fails validation or violates domain constraints."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="DATA_VALIDATION_ERROR",
            details=details,
        )


class GuardrailViolationError(HotelRevenueException):
    """Raised when a proposed price recommendation violates safety guardrail limits."""

    def __init__(self, message: str, proposed_rate: float, limit_value: float):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="GUARDRAIL_VIOLATION",
            details={"proposed_rate": proposed_rate, "limit_value": limit_value},
        )


class InsufficientDataError(HotelRevenueException):
    """Raised when insufficient historical hotel data is available for accurate ML forecasting."""

    def __init__(self, message: str = "Insufficient data available for this recommendation."):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INSUFFICIENT_DATA",
        )


class LLMProviderError(HotelRevenueException):
    """Raised when an external or local LLM provider call fails."""

    def __init__(self, provider: str, message: str):
        super().__init__(
            message=f"LLM Provider '{provider}' error: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="LLM_PROVIDER_ERROR",
            details={"provider": provider},
        )


class DatabaseError(HotelRevenueException):
    """Raised on critical database query or transaction failures."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
        )
