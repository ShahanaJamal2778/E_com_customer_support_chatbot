"""
routers/cart_router.py

Shopping cart endpoints. Delegates entirely to services/cart_service.py
- no SQL here.
"""

from fastapi import APIRouter, status

from schemas.requests import CartAddRequest, CartRemoveRequest, CartUpdateRequest
from schemas.responses import StandardResponse
from services import cart_service
from routers.common import run_service

router = APIRouter(tags=["Cart"])


@router.get("/cart/{user_id}", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def get_cart(user_id: str):
    """Get a user's current cart contents."""
    return run_service(cart_service.get_cart, user_id)


@router.post("/cart/add", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(payload: CartAddRequest):
    """Add a product to a user's cart (merges quantity if already present)."""
    return run_service(cart_service.add_to_cart, payload.user_id, payload.product_id, payload.quantity)


@router.delete("/cart/remove", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def remove_from_cart(payload: CartRemoveRequest):
    """Remove a single product line from a user's cart."""
    return run_service(cart_service.remove_from_cart, payload.user_id, payload.product_id)


@router.put("/cart/update", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def update_cart(payload: CartUpdateRequest):
    """Set the exact quantity for an existing cart line."""
    return run_service(cart_service.update_quantity, payload.user_id, payload.product_id, payload.quantity)


@router.delete("/cart/clear", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def clear_cart(user_id: str):
    """Empty a user's cart entirely."""
    return run_service(cart_service.clear_cart, user_id)