"""
services/product_service.py

All product catalog reads/writes. No SQL outside this module for the
`products` / `categories` tables.
"""

from database.supabase import supabase
from services.utils import ok, ValidationError, NotFoundError


def get_all_products() -> dict:
    """Return every product in the catalog."""
    response = supabase.table("products").select("*").execute()
    return ok(response.data)


def get_product_by_id(product_id: str) -> dict:
    """Return a single product by id."""
    if not product_id:
        raise ValidationError("product_id is required.")

    response = supabase.table("products").select("*").eq("id", product_id).execute()
    if not response.data:
        raise NotFoundError(f"No product found with id {product_id}.")
    return ok(response.data[0])


def search_product(keyword: str) -> dict:
    """Search products by name/description keyword."""
    if not keyword or not keyword.strip():
        raise ValidationError("keyword is required.")

    response = (
        supabase.table("products")
        .select("*")
        .or_(f"name.ilike.%{keyword}%,description.ilike.%{keyword}%")
        .execute()
    )
    return ok(response.data)


def search_by_category(category_name: str) -> dict:
    """Search products by category name."""
    if not category_name:
        raise ValidationError("category_name is required.")

    category = (
        supabase.table("categories").select("id").eq("name", category_name).execute()
    )
    if not category.data:
        return ok([], f"No category named '{category_name}' was found.")

    category_id = category.data[0]["id"]
    response = (
        supabase.table("products").select("*").eq("category_id", category_id).execute()
    )
    return ok(response.data)


def search_by_price(max_price: float) -> dict:
    """Return products priced at or below max_price."""
    if max_price is None or max_price < 0:
        raise ValidationError("max_price must be a non-negative number.")

    response = supabase.table("products").select("*").lte("price", max_price).execute()
    return ok(response.data)


def search_by_brand(brand: str) -> dict:
    """Return products matching a given brand."""
    if not brand:
        raise ValidationError("brand is required.")

    response = supabase.table("products").select("*").ilike("brand", f"%{brand}%").execute()
    return ok(response.data)


def get_best_sellers(limit: int = 10) -> dict:
    """
    Return top-rated products as a proxy for "best sellers".

    NOTE: the live schema has no units_sold/sales-count column, so this
    ranks by `rating` instead. If you later add a units_sold column
    (e.g. incremented in order_service.create_order), switch the
    .order() call below to rank by that instead.
    """
    response = (
        supabase.table("products")
        .select("*")
        .order("rating", desc=True)
        .limit(limit)
        .execute()
    )
    return ok(response.data)


def get_new_arrivals(limit: int = 10) -> dict:
    """Return the most recently added products."""
    response = (
        supabase.table("products")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return ok(response.data)


def get_discounted_products() -> dict:
    """
    Return products currently on discount.
    """
    response = supabase.table("products").select("*").gt("discount_percent", 0).execute()
    return ok(response.data)


def recommend_products(product_id: str | None = None, limit: int = 5) -> dict:
    """
    Recommend products.

    If product_id is given, recommend other products from the same
    category (simple content-based recommendation). Otherwise fall
    back to best sellers.
    """
    if product_id:
        product = get_product_by_id(product_id)["data"]
        response = (
            supabase.table("products")
            .select("*")
            .eq("category_id", product["category_id"])
            .neq("id", product_id)
            .limit(limit)
            .execute()
        )
        return ok(response.data)

    return get_best_sellers(limit)


def compare_products(product1_id: str, product2_id: str) -> dict:
    """Return both products side by side for comparison."""
    if not product1_id or not product2_id:
        raise ValidationError("product1_id and product2_id are required.")

    p1 = get_product_by_id(product1_id)["data"]
    p2 = get_product_by_id(product2_id)["data"]
    return ok({"product1": p1, "product2": p2})


def update_stock(product_id: str, qty: int) -> dict:
    """
    Adjust stock for a product by a delta (positive to restock,
    negative to deduct, e.g. after an order is placed).
    """
    if not product_id:
        raise ValidationError("product_id is required.")

    product = get_product_by_id(product_id)["data"]
    new_stock = product["stock"] + qty
    if new_stock < 0:
        raise ValidationError("Insufficient stock for this operation.")

    response = (
        supabase.table("products")
        .update({"stock": new_stock})
        .eq("id", product_id)
        .execute()
    )
    return ok(response.data[0], "Stock updated.")