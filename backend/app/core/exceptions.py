"""
Custom exceptions for Find My Journal API.
Provides consistent error handling across the application.
"""
from fastapi import HTTPException, status
from typing import Optional, Any


class AppException(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(message)


class DatabaseError(AppException):
    """Database operation failed."""
    pass


class NotFoundError(AppException):
    """Resource not found."""
    pass


class ValidationError(AppException):
    """Input validation failed."""
    pass


class RateLimitError(AppException):
    """Rate limit exceeded."""
    pass


class AuthenticationError(AppException):
    """Authentication failed."""
    pass


def raise_not_found(resource: str, identifier: str) -> None:
    """Raise 404 HTTPException with consistent format."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found: {identifier}"
    )


def raise_database_error(operation: str, error: Exception) -> None:
    """Raise 500 HTTPException for database errors."""
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Database error during {operation}: {str(error)}"
    )


def raise_rate_limit(limit: int, used: int, message: str = "Rate limit exceeded") -> None:
    """Raise 429 HTTPException for rate limits."""
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": message,
            "limit": limit,
            "used": used,
        }
    )
