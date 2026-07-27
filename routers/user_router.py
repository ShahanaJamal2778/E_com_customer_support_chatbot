"""
routers/user_router.py

Profile, address, review, and wishlist endpoints. Delegates entirely
to services/user_service.py - no SQL here.
"""

from fastapi import APIRouter, status

from schemas.requests import (
    ProfileUpdateRequest,
    AddressUpdateRequest,
    ReviewRequest,
    WishlistRequest,
)
from schemas.responses import StandardResponse
from services import user_service
from routers.common import run_service

router = APIRouter(tags=["User"])


@router.put("/profile/update", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def update_profile(payload: ProfileUpdateRequest):
    """Update one or more profile fields at once."""
    fields = payload.model_dump(exclude={"user_id"}, exclude_none=True)
    return run_service(user_service.update_profile, payload.user_id, fields)


@router.put("/address/update", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def update_address(payload: AddressUpdateRequest):
    """Update a user's shipping address."""
    return run_service(user_service.update_shipping_address, payload.user_id, payload.address)


@router.post("/review", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def add_review(payload: ReviewRequest):
    """Submit a product review."""
    return run_service(
        user_service.add_review,
        payload.user_id,
        payload.product_id,
        payload.rating,
        payload.comment,
    )


@router.get("/wishlist/{user_id}", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def get_wishlist(user_id: str):
    """Get a user's wishlist."""
    return run_service(user_service.wishlist, user_id)


@router.post("/wishlist/add", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def add_wishlist(payload: WishlistRequest):
    """Add a product to a user's wishlist."""
    return run_service(user_service.wishlist_add, payload.user_id, payload.product_id)


@router.delete("/wishlist/remove", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def remove_wishlist(payload: WishlistRequest):
    """Remove a product from a user's wishlist."""
    return run_service(user_service.wishlist_remove, payload.user_id, payload.product_id)