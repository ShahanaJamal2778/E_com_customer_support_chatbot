"""
services/user_service.py

All user profile, address, wishlist, and review operations.
No SQL is allowed outside this module for these concerns.
"""

from typing import Optional

from database.supabase import supabase
from services.auth_service import verify_password, _hash_password
from services.utils import ok, ValidationError, NotFoundError, AuthError


def get_user(user_id: str) -> dict:
    """Fetch a single user by id (password hash excluded)."""
    if not user_id:
        raise ValidationError("user_id is required.")

    response = supabase.table("users").select("*").eq("id", user_id).execute()
    if not response.data:
        raise NotFoundError(f"No user found with id {user_id}.")

    user = dict(response.data[0])
    user.pop("password_hash", None)
    return ok(user)


def change_password(user_id: str, old_password: str, new_password: str) -> dict:
    """Change a user's password after verifying the current one."""
    if not user_id or not old_password or not new_password:
        raise ValidationError("user_id, old_password, and new_password are required.")
    if len(new_password) < 6:
        raise ValidationError("New password must be at least 6 characters.")

    response = supabase.table("users").select("*").eq("id", user_id).execute()
    if not response.data:
        raise NotFoundError(f"No user found with id {user_id}.")

    user = response.data[0]
    if not verify_password(old_password, user.get("password_hash", "")):
        raise AuthError("Current password is incorrect.")

    supabase.table("users").update(
        {"password_hash": _hash_password(new_password)}
    ).eq("id", user_id).execute()
    return ok(message="Password updated successfully.")


def update_profile(user_id: str, fields: dict) -> dict:
    """
    Generic profile update. Prefer the more specific update_* helpers
    below for single-field updates from the chatbot; this is used by
    the web profile-edit form which can submit several fields at once.
    """
    if not user_id:
        raise ValidationError("user_id is required.")

    allowed = {"full_name", "phone", "email", "address", "city"}
    payload = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not payload:
        raise ValidationError("No valid profile fields were provided.")

    response = supabase.table("users").update(payload).eq("id", user_id).execute()
    if not response.data:
        raise NotFoundError(f"No user found with id {user_id}.")
    return ok(response.data[0], "Profile updated successfully.")


def update_name(user_id: str, full_name: str) -> dict:
    """Update a user's display name."""
    if not full_name or not full_name.strip():
        raise ValidationError("full_name is required.")
    return update_profile(user_id, {"full_name": full_name.strip()})


def update_phone(user_id: str, phone: str) -> dict:
    """Update a user's phone number."""
    if not phone or not phone.strip():
        raise ValidationError("phone is required.")
    return update_profile(user_id, {"phone": phone.strip()})


def update_email(user_id: str, email: str) -> dict:
    """Update a user's email address."""
    if not email or "@" not in email:
        raise ValidationError("A valid email is required.")
    return update_profile(user_id, {"email": email.strip()})


def update_shipping_address(user_id: str, address: str) -> dict:
    """Update a user's shipping address."""
    if not address or not address.strip():
        raise ValidationError("address is required.")
    return update_profile(user_id, {"address": address.strip()})


def change_city(user_id: str, city: str) -> dict:
    """Update a user's city."""
    if not city or not city.strip():
        raise ValidationError("city is required.")
    return update_profile(user_id, {"city": city.strip()})


def wishlist_add(user_id: str, product_id: str) -> dict:
    """Add a product to a user's wishlist (idempotent)."""
    if not user_id or not product_id:
        raise ValidationError("user_id and product_id are required.")

    existing = (
        supabase.table("wishlist")
        .select("id")
        .eq("user_id", user_id)
        .eq("product_id", product_id)
        .execute()
    )
    if existing.data:
        return ok(message="Product is already in your wishlist.")

    supabase.table("wishlist").insert(
        {"user_id": user_id, "product_id": product_id}
    ).execute()
    return ok(message="Product added to wishlist.")


def wishlist_remove(user_id: str, product_id: str) -> dict:
    """Remove a product from a user's wishlist."""
    if not user_id or not product_id:
        raise ValidationError("user_id and product_id are required.")

    supabase.table("wishlist").delete().eq("user_id", user_id).eq(
        "product_id", product_id
    ).execute()
    return ok(message="Product removed from wishlist.")


def wishlist(user_id: str) -> dict:
    """Return a user's wishlist with joined product details."""
    if not user_id:
        raise ValidationError("user_id is required.")

    response = (
        supabase.table("wishlist")
        .select("product_id, products(*)")
        .eq("user_id", user_id)
        .execute()
    )
    return ok(response.data)


def add_review(user_id: str, product_id: str, rating: int, comment: Optional[str] = None) -> dict:
    """Add a product review by a user. `comment` maps to the `review` column."""
    if not user_id or not product_id:
        raise ValidationError("user_id and product_id are required.")
    if rating is None or not (1 <= int(rating) <= 5):
        raise ValidationError("rating must be an integer between 1 and 5.")

    response = (
        supabase.table("reviews")
        .insert(
            {
                "user_id": user_id,
                "product_id": product_id,
                "rating": int(rating),
                "review": comment,
            }
        )
        .execute()
    )
    if not response.data:
        raise ValidationError("Failed to submit review.")
    return ok(response.data[0], "Review submitted successfully.")