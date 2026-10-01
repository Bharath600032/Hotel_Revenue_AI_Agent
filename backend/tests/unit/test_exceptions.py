"""
Unit tests for custom application exceptions.
"""
import pytest
from app.core.exceptions import (
    HotelRevenueException,
    AuthenticationError,
    PermissionDeniedError,
    ResourceNotFoundError,
    GuardrailViolationError,
    InsufficientDataError,
)


def test_custom_exceptions():
    """Verify custom exception status codes and error code mappings."""
    exc = ResourceNotFoundError(entity_name="Hotel", entity_id=101)
    assert exc.status_code == 404
    assert exc.error_code == "RESOURCE_NOT_FOUND"
    assert exc.details["entity_id"] == "101"

    exc_guard = GuardrailViolationError("Rate too high", proposed_rate=12000.0, limit_value=10000.0)
    assert exc_guard.status_code == 400
    assert exc_guard.error_code == "GUARDRAIL_VIOLATION"
    assert exc_guard.details["proposed_rate"] == 12000.0

    exc_data = InsufficientDataError()
    assert exc_data.status_code == 400
    assert "Insufficient data available" in exc_data.message
