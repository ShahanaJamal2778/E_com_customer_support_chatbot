"""
chatbot/entity_extractor.py

Pulls structured entities out of a raw user message using regex.
This module never touches the database - it is pure text processing.
"""

import re
from typing import Optional

# Common Pakistani cities, used to bias city extraction. Extend as needed.
_KNOWN_CITIES = [
    "karachi", "lahore", "islamabad", "rawalpindi", "faisalabad",
    "multan", "peshawar", "quetta", "hyderabad", "sialkot", "gujranwala",
]

_KNOWN_CATEGORIES = ["men", "women", "kids", "electronics"]


def extract_price(message: str) -> Optional[float]:
    """Extract a price/budget figure, e.g. 'under 3000', '5000 PKR'."""
    match = re.search(r"(?:under|below|less than|within)?\s*(?:rs\.?|pkr)?\s*(\d{2,7})(?:\s*(?:pkr|rs))?", message, re.IGNORECASE)
    return float(match.group(1)) if match else None


def extract_product_id(message: str) -> Optional[str]:
    """Extract a product id, e.g. 'product 42', '#P123', 'id: 17'."""
    match = re.search(r"(?:product\s*id|product|item|#)\s*[:#]?\s*([a-zA-Z0-9\-]{1,20})", message, re.IGNORECASE)
    return match.group(1) if match else None


def extract_order_id(message: str) -> Optional[str]:
    """Extract an order id, e.g. 'order #ORD1029', 'order id 55'."""
    match = re.search(r"order\s*(?:id|number|no\.?|#)?\s*[:#]?\s*([a-zA-Z0-9\-]{1,20})", message, re.IGNORECASE)
    return match.group(1) if match else None


def extract_category(message: str) -> Optional[str]:
    """Extract a known product category name."""
    lowered = message.lower()
    for category in _KNOWN_CATEGORIES:
        if category in lowered:
            return category.capitalize()
    return None


def extract_brand(message: str) -> Optional[str]:
    """Extract a brand name, e.g. 'Nike shoes', 'brand: Samsung'."""
    match = re.search(r"brand\s*[:\-]?\s*([a-zA-Z][a-zA-Z0-9 ]{1,30})", message, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_city(message: str) -> Optional[str]:
    """Extract a known city name."""
    lowered = message.lower()
    for city in _KNOWN_CITIES:
        if city in lowered:
            return city.capitalize()
    return None


def extract_address(message: str) -> Optional[str]:
    """
    Extract a free-form address, conservatively.

    IMPORTANT: this used to fall back to returning the entire raw
    message whenever no explicit pattern matched - which meant a
    message like "update my address" was itself saved as the address.
    Now it only returns something when the message actually looks like
    an address: an explicit "address is/at: ..." phrase, a known city
    name, or the presence of digits (house/block numbers). Otherwise
    it returns None so the calling handler asks a follow-up question
    instead of guessing. Once that follow-up question is asked,
    actions.py's multi-turn flow uses the raw next message directly -
    it does NOT call this function again - so this stays conservative
    without breaking that flow.
    """
    match = re.search(r"address\s*(?:is|at|:|=)\s*(.+)", message, re.IGNORECASE)
    if match:
        return _strip_leading_connector(match.group(1).strip())

    if extract_city(message) or re.search(r"\d", message):
        return _strip_leading_connector(message.strip())

    return None


def _strip_leading_connector(text: str) -> str:
    """Drop a leading 'to '/'at '/'in ' left over from phrases like 'update my address to X'."""
    return re.sub(r"^(to|at|in)\s+", "", text, flags=re.IGNORECASE).strip()


def extract_coupon_code(message: str) -> Optional[str]:
    """
    Extract a coupon/promo code, e.g. 'apply SUMMER20', 'use code EID15'.
    Looks for an explicit 'code'/'coupon'/'promo' keyword first, then
    falls back to a bare all-caps alphanumeric token (typical coupon
    shape) elsewhere in the message.
    """
    match = re.search(r"(?:coupon|promo|code)\s*[:\-]?\s*([A-Za-z0-9]{4,15})", message, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    bare = re.search(r"\b([A-Z]{3,10}\d{0,4}|[A-Z]+\d{2,4})\b", message)
    if bare and bare.group(1).lower() not in _KNOWN_CATEGORIES:
        return bare.group(1).upper()

    return None


def extract_quantity(message: str) -> Optional[int]:
    """Extract a quantity, e.g. 'add 3 of this', 'qty: 2'."""
    match = re.search(r"(?:qty|quantity)\s*[:\-]?\s*(\d{1,3})|(\d{1,3})\s*(?:pcs|pieces|units|x)\b", message, re.IGNORECASE)
    if match:
        return int(match.group(1) or match.group(2))
    return None


def extract_product_name_guess(message: str) -> Optional[str]:
    """
    Heuristic: find a run of 2+ consecutive Capitalized Words, which is
    how a product name tends to appear inside a full sentence when a
    user types or copies it from a listing (e.g. "...current stock of
    Kids School Bag" -> "Kids School Bag"). Returns None if no such run
    is found, so the caller can fall back to searching the whole
    message instead.
    """
    match = re.search(r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)", message)
    return match.group(1).strip() if match else None


def extract_entities(message: str) -> dict:
    """Run every extractor over a message and return the combined result."""
    return {
        "price": extract_price(message),
        "product_id": extract_product_id(message),
        "product_name_guess": extract_product_name_guess(message),
        "order_id": extract_order_id(message),
        "category": extract_category(message),
        "brand": extract_brand(message),
        "city": extract_city(message),
        "address": extract_address(message),
        "quantity": extract_quantity(message),
        "coupon_code": extract_coupon_code(message),
    }