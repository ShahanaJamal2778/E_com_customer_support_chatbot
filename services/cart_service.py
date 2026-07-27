"""
services/cart_service.py

All shopping-cart operations. No SQL outside this module for the
`cart` table.
"""

from database.supabase import supabase
from services.utils import ok, ValidationError, NotFoundError


def add_to_cart(user_id: str, product_id: str, quantity: int = 1) -> dict:
    """Add a product to the cart, merging quantity if it's already present."""
    if not user_id or not product_id:
        raise ValidationError("user_id and product_id are required.")
    if quantity < 1:
        raise ValidationError("quantity must be at least 1.")

    product = (
        supabase.table("products").select("id, stock").eq("id", product_id).execute()
    )
    if not product.data:
        raise NotFoundError(f"No product found with id {product_id}.")

    existing = (
        supabase.table("cart")
        .select("*")
        .eq("user_id", user_id)
        .eq("product_id", product_id)
        .execute()
    )

    if existing.data:
        new_quantity = existing.data[0]["quantity"] + quantity
        response = (
            supabase.table("cart")
            .update({"quantity": new_quantity})
            .eq("id", existing.data[0]["id"])
            .execute()
        )
    else:
        response = (
            supabase.table("cart")
            .insert({"user_id": user_id, "product_id": product_id, "quantity": quantity})
            .execute()
        )

    return ok(response.data[0] if response.data else None, "Item added to cart.")


def remove_from_cart(user_id: str, product_id: str) -> dict:
    """Remove a single product line from the cart."""
    if not user_id or not product_id:
        raise ValidationError("user_id and product_id are required.")

    supabase.table("cart").delete().eq("user_id", user_id).eq(
        "product_id", product_id
    ).execute()
    return ok(message="Item removed from cart.")


def update_quantity(user_id: str, product_id: str, quantity: int) -> dict:
    """Set the quantity for an existing cart line to an exact value."""
    if not user_id or not product_id:
        raise ValidationError("user_id and product_id are required.")
    if quantity < 1:
        raise ValidationError("quantity must be at least 1. Use remove_from_cart to delete a line.")

    response = (
        supabase.table("cart")
        .update({"quantity": quantity})
        .eq("user_id", user_id)
        .eq("product_id", product_id)
        .execute()
    )
    if not response.data:
        raise NotFoundError("Cart item not found.")
    return ok(response.data[0], "Cart quantity updated.")


def clear_cart(user_id: str) -> dict:
    """Remove all items from a user's cart."""
    if not user_id:
        raise ValidationError("user_id is required.")

    supabase.table("cart").delete().eq("user_id", user_id).execute()
    return ok(message="Cart cleared.")


def get_cart(user_id: str) -> dict:
    """Return all cart lines for a user with joined product details."""
    if not user_id:
        raise ValidationError("user_id is required.")

    response = (
        supabase.table("cart")
        .select("id, quantity, product_id, products(*)")
        .eq("user_id", user_id)
        .execute()
    )
    return ok(response.data)


def cart_total(user_id: str) -> dict:
    """Compute the total price of a user's cart."""
    cart_response = get_cart(user_id)
    items = cart_response["data"] or []

    total = 0.0
    for item in items:
        product = item.get("products")
        if product and product.get("price") is not None:
            total += float(product["price"]) * item["quantity"]

    return ok({"total": round(total, 2), "item_count": len(items)})