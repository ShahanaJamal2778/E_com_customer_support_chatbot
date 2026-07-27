"""
services/utils.py

Shared helpers used across every service module:
- A consistent response envelope so api.py never has to guess the shape
  of what a service returns.
- A small hierarchy of service-level exceptions so actions.py / api.py
  can distinguish "not found" from "validation error" from "server error"
  without parsing strings.
"""

from typing import Any, Optional


class ServiceError(Exception):
    """Base class for all service-layer errors."""


class ValidationError(ServiceError):
    """Raised when caller-supplied input fails validation."""


class NotFoundError(ServiceError):
    """Raised when a requested resource does not exist."""


class AuthError(ServiceError):
    """Raised for authentication / authorization failures."""


def ok(data: Any = None, message: str = "success") -> dict:
    """Build a successful response envelope."""
    return {"success": True, "message": message, "data": data}


def fail(message: str, data: Optional[Any] = None) -> dict:
    """Build a failed response envelope (used for expected/handled failures)."""
    return {"success": False, "message": message, "data": data}