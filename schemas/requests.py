"""
schemas/requests.py

All Pydantic request (input) models, grouped by feature. Kept
separate from the service-layer function signatures so the API's
public contract can evolve independently of internal business logic.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Raw text typed by the user")
    user_id: Optional[str] = Field(None, description="Logged-in user id, omit for guests")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

class CartAddRequest(BaseModel):
    user_id: str
    product_id: str
    quantity: int = Field(default=1, ge=1)


class CartRemoveRequest(BaseModel):
    user_id: str
    product_id: str


class CartUpdateRequest(BaseModel):
    user_id: str
    product_id: str
    quantity: int = Field(..., ge=1)


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

class CheckoutRequest(BaseModel):
    user_id: str
    shipping_address: str = Field(..., min_length=3)
    payment_method: str = "COD"
    coupon_code: Optional[str] = None


# ---------------------------------------------------------------------------
# User / profile / wishlist / reviews
# ---------------------------------------------------------------------------

class ProfileUpdateRequest(BaseModel):
    user_id: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None


class AddressUpdateRequest(BaseModel):
    user_id: str
    address: str = Field(..., min_length=3)


class ReviewRequest(BaseModel):
    user_id: str
    product_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class WishlistRequest(BaseModel):
    user_id: str
    product_id: str