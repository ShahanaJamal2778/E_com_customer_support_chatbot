"""
services/auth_service.py

Handles registration, login/logout, and password hashing/verification.
All SQL lives here behind the Supabase client - no other layer (routes,
actions, predict.py) is allowed to touch the `users` table's auth fields
directly.
"""

from typing import Optional
import bcrypt

from database.supabase import supabase
from services.utils import ok, ValidationError, AuthError, ServiceError


class DatabaseError(ServiceError):
    """Wraps unexpected lower-level (network/db) exceptions with context."""

    def __init__(self, original: Exception):
        super().__init__(f"A database error occurred: {original}")
        self.original = original


def _hash_password(plain_password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, AttributeError):
        return False


def register(email: str, full_name: str, password: str, phone: Optional[str] = None) -> dict:
    """
    Register a new user.

    Args:
        email: user's email address (must be unique).
        full_name: user's display name.
        password: plaintext password (will be hashed before storage).
        phone: optional phone number.

    Returns:
        dict envelope with the created user (password hash excluded).
    """
    if not email or "@" not in email:
        raise ValidationError("A valid email address is required.")
    if not full_name or not full_name.strip():
        raise ValidationError("Full name is required.")
    if not password or len(password) < 6:
        raise ValidationError("Password must be at least 6 characters.")

    existing = (
        supabase.table("users").select("id").eq("email", email).execute()
    )
    if existing.data:
        raise ValidationError("An account with this email already exists.")

    try:
        response = (
            supabase.table("users")
            .insert(
                {
                    "email": email,
                    "full_name": full_name,
                    "phone": phone,
                    "password_hash": _hash_password(password),
                }
            )
            .execute()
        )
    except Exception as exc:  # pragma: no cover - network/db failure
        raise DatabaseError(exc)

    if not response.data:
        raise DatabaseError(Exception("Registration failed."))

    user = dict(response.data[0])
    user.pop("password_hash", None)
    return ok(user, "Registration successful.")


def login(email: str, password: str) -> dict:
    """
    Authenticate a user by email + password.

    Returns:
        dict envelope with the user record (password hash excluded).
    """
    if not email or not password:
        raise ValidationError("Email and password are required.")

    response = supabase.table("users").select("*").eq("email", email).execute()
    if not response.data:
        raise AuthError("Invalid email or password.")

    user = dict(response.data[0])
    if not verify_password(password, user.get("password_hash", "")):
        raise AuthError("Invalid email or password.")

    user.pop("password_hash", None)
    return ok(user, "Login successful.")


def logout(user_id: str) -> dict:
    """
    Log a user out.

    Since this project uses stateless token/session auth handled at the
    API layer, this simply acknowledges the logout. Kept as a service
    function so the API and chatbot flows have a single call site, and
    so session/token invalidation can be added here later without
    touching callers.
    """
    if not user_id:
        raise ValidationError("user_id is required.")
    return ok({"user_id": user_id}, "Logged out successfully.")