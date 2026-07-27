"""
routers/order_router.py

Checkout and order lifecycle endpoints. Delegates entirely to
services/order_service.py - no SQL here.
"""

from fastapi import APIRouter, status

from schemas.requests import CheckoutRequest
from schemas.responses import StandardResponse
from services import order_service
from routers.common import run_service

router = APIRouter(tags=["Orders"])


@router.post("/checkout", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def checkout(payload: CheckoutRequest):
    """Create an order from the user's cart and (for non-COD) record payment."""
    return run_service(
        order_service.checkout,
        payload.user_id,
        payload.shipping_address,
        payload.payment_method,
        payload.coupon_code,
    )


@router.get("/orders/{user_id}", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def get_orders(user_id: str):
    """List a user's order history, most recent first."""
    return run_service(order_service.order_history, user_id)


@router.get("/track/{order_id}", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def track_order(order_id: str):
    """Get the current status of an order."""
    return run_service(order_service.track_order, order_id)


@router.put("/cancel/{order_id}", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def cancel_order(order_id: str):
    """Cancel an order, if it hasn't shipped yet."""
    return run_service(order_service.cancel_order, order_id)