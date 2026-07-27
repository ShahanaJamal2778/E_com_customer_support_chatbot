"""
services/order_service.py

Orders, payments, and coupons. No SQL outside this module for the
`orders`, `order_items`, `payments`, and `coupons` tables.

Depends on cart_service (to read/clear the cart) and product_service
(to decrement stock), composed at the service layer - never inside
actions.py or api.py.
"""

from database.supabase import supabase
from services.utils import ok, ValidationError, NotFoundError
from services.cart_service import get_cart, clear_cart
from services.product_service import update_stock


def apply_coupon(code: str, subtotal: float) -> dict:
    """
    Validate a coupon code and return the discounted total.

    NOTE: the live `coupons` table has a single `discount` INT column
    (not `discount_percent`), so this treats it as a flat PKR amount
    subtracted from the subtotal, clamped at 0 - not a percentage. If
    your coupons are meant to be percentages, either add a boolean
    `is_percent` column to distinguish them, or rename the column to
    `discount_percent` and switch the calculation below back to
    `subtotal * (discount / 100)`.
    """
    if not code:
        raise ValidationError("coupon code is required.")

    response = supabase.table("coupons").select("*").eq("code", code).execute()
    if not response.data:
        raise NotFoundError("Invalid coupon code.")

    coupon = response.data[0]

    expiry = coupon.get("expiry_date")
    if expiry:
        from datetime import date
        if date.fromisoformat(str(expiry)) < date.today():
            raise ValidationError("This coupon has expired.")

    discount_amount = min(float(coupon.get("discount", 0)), subtotal)
    final_total = round(subtotal - discount_amount, 2)

    return ok(
        {
            "code": code,
            "discount_amount": round(discount_amount, 2),
            "final_total": final_total,
        }
    )


def create_order(user_id: str, shipping_address: str, payment_method: str = "COD", coupon_code: str | None = None) -> dict:
    """Create an order from the user's current cart contents."""
    if not user_id or not shipping_address:
        raise ValidationError("user_id and shipping_address are required.")

    cart_response = get_cart(user_id)
    cart_items = cart_response["data"]
    if not cart_items:
        raise ValidationError("Your cart is empty.")

    subtotal = sum(
        float(item["products"]["price"]) * item["quantity"]
        for item in cart_items
        if item.get("products")
    )

    total = subtotal
    if coupon_code:
        discount = apply_coupon(coupon_code, subtotal)["data"]
        total = discount["final_total"]

    order_response = (
        supabase.table("orders")
        .insert(
            {
                "user_id": user_id,
                "total": total,
                "shipping_address": shipping_address,
                "status": "Pending",
                "payment_method": payment_method,
            }
        )
        .execute()
    )
    if not order_response.data:
        raise ValidationError("Failed to create order.")

    order = order_response.data[0]
    order_id = order["id"]

    items_payload = [
        {
            "order_id": order_id,
            "product_id": item["product_id"],
            "quantity": item["quantity"],
            "price": item["products"]["price"],
        }
        for item in cart_items
        if item.get("products")
    ]
    if items_payload:
        supabase.table("order_items").insert(items_payload).execute()

    for item in cart_items:
        if item.get("products"):
            update_stock(item["product_id"], -item["quantity"])

    clear_cart(user_id)
    order["items"] = items_payload
    return ok(order, "Order created successfully.")


def payment(order_id: str, amount: float, method: str) -> dict:
    """Record a payment against an order."""
    if not order_id or amount is None or not method:
        raise ValidationError("order_id, amount, and method are required.")

    response = (
        supabase.table("payments")
        .insert({"order_id": order_id, "amount": amount, "method": method, "status": "Paid"})
        .execute()
    )
    if not response.data:
        raise ValidationError("Failed to record payment.")

    supabase.table("orders").update({"status": "Paid"}).eq("id", order_id).execute()
    return ok(response.data[0], "Payment recorded successfully.")


def checkout(user_id: str, shipping_address: str, payment_method: str = "COD", coupon_code: str | None = None) -> dict:
    """
    Full checkout flow: create the order, then (for non-COD methods)
    record the payment immediately. Kept separate from create_order so
    the chatbot can offer a "review before pay" step if needed.
    """
    order_result = create_order(user_id, shipping_address, payment_method, coupon_code)
    order = order_result["data"]

    if payment_method != "COD":
        payment(order["id"], order["total"], payment_method)

    return ok(order, "Checkout complete.")


def track_order(order_id: str) -> dict:
    """Fetch the current status of an order."""
    if not order_id:
        raise ValidationError("order_id is required.")

    response = supabase.table("orders").select("*").eq("id", order_id).execute()
    if not response.data:
        raise NotFoundError(f"No order found with id {order_id}.")
    return ok(response.data[0])


def cancel_order(order_id: str) -> dict:
    """Cancel an order, provided it hasn't already shipped/been delivered."""
    order = track_order(order_id)["data"]
    if order["status"] in ("Shipped", "Delivered", "Cancelled"):
        raise ValidationError(f"Order cannot be cancelled - current status is '{order['status']}'.")

    response = (
        supabase.table("orders").update({"status": "Cancelled"}).eq("id", order_id).execute()
    )
    return ok(response.data[0], "Order cancelled.")


def refund_order(order_id: str, reason: str | None = None) -> dict:
    """
    Mark an order as refunded and store the reason.

    Requires an `orders.refund_reason TEXT` column - if you haven't
    added it yet:
        ALTER TABLE orders ADD COLUMN refund_reason TEXT;
    """
    order = track_order(order_id)["data"]
    if order["status"] not in ("Paid", "Delivered"):
        raise ValidationError(f"Order in status '{order['status']}' is not eligible for refund.")

    payload = {"status": "Refunded"}
    if reason:
        payload["refund_reason"] = reason

    response = (
        supabase.table("orders")
        .update(payload)
        .eq("id", order_id)
        .execute()
    )
    return ok(response.data[0] if response.data else order, "Refund processed.")


def order_history(user_id: str) -> dict:
    """Return all orders placed by a user, most recent first."""
    if not user_id:
        raise ValidationError("user_id is required.")

    response = (
        supabase.table("orders")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return ok(response.data)