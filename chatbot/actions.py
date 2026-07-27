# """
# chatbot/actions.py

# Intent router. Every intent tag from intents.json maps to exactly one
# handler function below. Handlers NEVER touch Supabase directly - they
# only call functions from the services/ layer.

# Each handler returns a dict: {"message": str, "data": Any}
#   - "message" is the human-readable chat reply.
#   - "data" is the raw structured payload (product list, cart, order,
#     etc.) so the frontend can render rich UI instead of parsing text.

# Multi-turn flows (e.g. "update my address" -> bot asks for the address
# -> user replies with just the address) are driven by context_manager.
# """

# from typing import Any, Callable, Optional

# from chatbot import context_manager as ctx
# from chatbot.entity_extractor import extract_entities
# from chatbot.predict import get_response_for_intent

# from services import product_service, cart_service, order_service, user_service
# from services.utils import ServiceError

# Entities = dict[str, Any]
# ActionResult = dict[str, Any]  # {"message": str, "data": Any}
# Handler = Callable[[str, Optional[str], Entities], ActionResult]


# def _result(message: str, data: Any = None) -> ActionResult:
#     return {"message": message, "data": data}


# def _require_login(user_id: Optional[str]) -> Optional[ActionResult]:
#     if not user_id:
#         return _result("Please log in first so I can do that for you.", None)
#     return None


# def _summary_line(p: dict) -> str:
#     return f"- **{p['name']}** - {p['price']} PKR"


# # ---------------------------------------------------------------------------
# # Conversational intents (static replies sourced from intents.json)
# # ---------------------------------------------------------------------------

# def _canned(intent_tag: str) -> Handler:
#     def _handler(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#         return _result(get_response_for_intent(intent_tag))
#     return _handler


# # ---------------------------------------------------------------------------
# # Product intents
# # ---------------------------------------------------------------------------

# def handle_show_products(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     products = product_service.get_all_products()["data"]
#     text = "Here's our catalog:\n\n" + "\n".join(_summary_line(p) for p in products[:5]) if products else "No products are currently available."
#     return _result(text, products)


# def handle_search_product(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     keyword = entities.get("brand") or entities.get("category") or message
#     products = product_service.search_product(keyword)["data"]
#     text = f"Results for '{keyword}':\n\n" + "\n".join(_summary_line(p) for p in products[:5]) if products else f"No products found matching '{keyword}'."
#     return _result(text, products)


# def handle_search_by_category(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     category = entities.get("category")
#     if not category:
#         return _result("Which category would you like to browse - Men, Women, Kids, or Electronics?", [])
#     products = product_service.search_by_category(category)["data"]
#     text = f"Products in '{category}':\n\n" + "\n".join(_summary_line(p) for p in products[:5]) if products else f"No products found in category '{category}'."
#     return _result(text, products)


# def handle_search_by_price(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     price = entities.get("price")
#     if price is None:
#         return _result("What's your budget? For example, 'products under 3000'.", [])
#     products = product_service.search_by_price(price)["data"]
#     text = f"Products under {price:.0f} PKR:\n\n" + "\n".join(_summary_line(p) for p in products[:5]) if products else f"No products found under {price:.0f} PKR."
#     return _result(text, products)


# def handle_product_details(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     product_id = entities.get("product_id")
#     if not product_id:
#         return _result("Which product would you like details for? Please share the product ID.", None)
#     p = product_service.get_product_by_id(product_id)["data"]
#     text = (
#         f"**{p['name']}**\n"
#         f"Price: {p['price']} PKR\n"
#         f"Stock: {p.get('stock', 'N/A')}\n"
#         f"Description: {p.get('description', 'N/A')}"
#     )
#     return _result(text, p)


# def handle_best_sellers(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     products = product_service.get_best_sellers()["data"]
#     text = "Our best sellers:\n\n" + "\n".join(_summary_line(p) for p in products[:5]) if products else "No best sellers to show yet."
#     return _result(text, products)


# def handle_new_arrivals(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     products = product_service.get_new_arrivals()["data"]
#     text = "Fresh new arrivals:\n\n" + "\n".join(_summary_line(p) for p in products[:5]) if products else "No new arrivals yet."
#     return _result(text, products)


# def handle_discounts(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     products = product_service.get_discounted_products()["data"]
#     text = "Current deals:\n\n" + "\n".join(_summary_line(p) for p in products[:5]) if products else "No active deals right now."
#     return _result(text, products)


# def _handle_fixed_category(category_name: str) -> Handler:
#     def _handler(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#         products = product_service.search_by_category(category_name)["data"]
#         text = (
#             f"Here are the latest items in **{category_name}**:\n\n" + "\n".join(_summary_line(p) for p in products[:5])
#             if products
#             else f"Currently, we don't have any products listed in {category_name}."
#         )
#         return _result(text, products)
#     return _handler


# # ---------------------------------------------------------------------------
# # Cart intents
# # ---------------------------------------------------------------------------

# def handle_add_to_cart(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     if (err := _require_login(user_id)):
#         return err
#     product_id = entities.get("product_id")
#     if not product_id:
#         return _result("Please tell me the product ID you'd like to add to your cart.", None)
#     quantity = entities.get("quantity") or 1
#     result = cart_service.add_to_cart(user_id, product_id, quantity)
#     return _result("Added to your cart! Anything else?", result["data"])


# def handle_remove_from_cart(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     if (err := _require_login(user_id)):
#         return err
#     product_id = entities.get("product_id")
#     if not product_id:
#         return _result("Please tell me the product ID to remove from your cart.", None)
#     cart_service.remove_from_cart(user_id, product_id)
#     return _result("Removed that item from your cart.", None)


# def handle_show_cart(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     if (err := _require_login(user_id)):
#         return err
#     items = cart_service.get_cart(user_id)["data"]
#     if not items:
#         return _result("Your cart is empty.", [])
#     total = cart_service.cart_total(user_id)["data"]["total"]
#     lines = [f"- **{i['products']['name']}** (x{i['quantity']})" for i in items if i.get("products")]
#     text = "Your cart:\n\n" + "\n".join(lines) + f"\n\n**Total: {total:.2f} PKR**"
#     return _result(text, {"items": items, "total": total})


# # ---------------------------------------------------------------------------
# # Order intents
# # ---------------------------------------------------------------------------

# def handle_checkout(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     if (err := _require_login(user_id)):
#         return err
#     address = entities.get("address")
#     if not address:
#         ctx.set_state(user_id, ctx.WAITING_FOR_ADDRESS, {"intent": "checkout"})
#         return _result("Sure! What's the shipping address for this order?", None)
#     order = order_service.checkout(user_id, address)["data"]
#     ctx.clear_state(user_id)
#     return _result(f"Order placed! Order ID: `{order['id']}`, Total: {order['total']} PKR.", order)


# def handle_track_order(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     order_id = entities.get("order_id")
#     if not order_id:
#         return _result("What's your order ID?", None)
#     o = order_service.track_order(order_id)["data"]
#     return _result(f"\U0001F4E6 Order `{o['id']}` status: **{o['status']}**, Total: {o['total']} PKR.", o)


# def handle_cancel_order(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     order_id = entities.get("order_id")
#     if not order_id:
#         return _result("Which order would you like to cancel? Please provide the order ID.", None)
#     order = order_service.cancel_order(order_id)["data"]
#     return _result(f"Order `{order_id}` has been cancelled.", order)


# def handle_order_history(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     if (err := _require_login(user_id)):
#         return err
#     orders = order_service.order_history(user_id)["data"]
#     if not orders:
#         return _result("You haven't placed any orders yet.", [])
#     lines = [f"- `{o['id']}` - {o['status']} - {o['total']} PKR" for o in orders[:10]]
#     return _result("Your recent orders:\n\n" + "\n".join(lines), orders)


# # ---------------------------------------------------------------------------
# # Account intents
# # ---------------------------------------------------------------------------

# def handle_update_shipping_address(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     if (err := _require_login(user_id)):
#         return err

#     address = entities.get("address")
#     if not address:
#         ctx.set_state(user_id, ctx.WAITING_FOR_ADDRESS, {"intent": "update_shipping_address"})
#         return _result("Sure! Please send me your new shipping address.", None)

#     result = user_service.update_shipping_address(user_id, address)
#     ctx.clear_state(user_id)
#     return _result(f"Your shipping address has been updated to: {address}", result["data"])


# def handle_wishlist_add(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     if (err := _require_login(user_id)):
#         return err
#     product_id = entities.get("product_id")
#     if not product_id:
#         return _result("Which product should I add to your wishlist? Please provide the product ID.", None)
#     user_service.wishlist_add(user_id, product_id)
#     return _result("Added to your wishlist!", None)


# def handle_show_wishlist(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     if (err := _require_login(user_id)):
#         return err
#     items = user_service.wishlist(user_id)["data"]
#     if not items:
#         return _result("Your wishlist is empty.", [])
#     lines = [f"- {i['products']['name']}" for i in items if i.get("products")]
#     return _result("Your wishlist:\n\n" + "\n".join(lines), items)


# # ---------------------------------------------------------------------------
# # Static / informational intents (no service call needed)
# # ---------------------------------------------------------------------------

# def handle_fallback(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
#     return _result(get_response_for_intent("fallback"), None)


# # ---------------------------------------------------------------------------
# # Dictionary-based intent routing table - keys MUST match intents.json tags
# # ---------------------------------------------------------------------------

# INTENT_HANDLERS: dict[str, Handler] = {
#     "greeting": _canned("greeting"),
#     "goodbye": _canned("goodbye"),
#     "thanks": _canned("thanks"),
#     "payment_methods": _canned("payment_methods"),
#     "shipping_policy": _canned("shipping_policy"),
#     "refund_policy": _canned("refund_policy"),
#     "contact": _canned("contact"),
#     "show_products": handle_show_products,
#     "search_product": handle_search_product,
#     "search_by_category": handle_search_by_category,
#     "search_by_price": handle_search_by_price,
#     "product_details": handle_product_details,
#     "best_sellers": handle_best_sellers,
#     "new_arrivals": handle_new_arrivals,
#     "discounts": handle_discounts,
#     "men_products": _handle_fixed_category("Men"),
#     "women_products": _handle_fixed_category("Women"),
#     "kids_products": _handle_fixed_category("Kids"),
#     "electronics": _handle_fixed_category("Electronics"),
#     "add_to_cart": handle_add_to_cart,
#     "remove_from_cart": handle_remove_from_cart,
#     "show_cart": handle_show_cart,
#     "checkout": handle_checkout,
#     "track_order": handle_track_order,
#     "cancel_order": handle_cancel_order,
#     "order_history": handle_order_history,
#     "update_shipping_address": handle_update_shipping_address,
#     "wishlist_add": handle_wishlist_add,
#     "show_wishlist": handle_show_wishlist,
#     "fallback": handle_fallback,
# }


# def _resume_conversation_state(message: str, user_id: str, state: dict) -> Optional[ActionResult]:
#     """
#     If the user is mid-flow (e.g. we just asked for their address),
#     treat this message as the answer to that question rather than
#     re-running intent classification on it.
#     """
#     state_name = state["state"]
#     pending_intent = state["data"].get("intent")

#     if state_name == ctx.WAITING_FOR_ADDRESS:
#         entities = {"address": message.strip()}
#         handler = INTENT_HANDLERS.get(pending_intent)
#         if handler:
#             return handler(message, user_id, entities)

#     return None


# def execute_action(intent: str, message: str = "", user_id: Optional[str] = None, entities: Optional[Entities] = None) -> ActionResult:
#     """
#     Route a predicted intent to its handler.

#     Args:
#         intent: predicted intent tag (already fallback-adjusted by the caller).
#         message: original user message (used for entity fallback / multi-turn).
#         user_id: logged-in user id, or None for guests.
#         entities: pre-extracted entities; extracted from `message` if omitted.

#     Returns:
#         {"message": str, "data": Any}. Never raises - service errors are
#         caught and turned into a friendly message with data=None.
#     """
#     entities = entities if entities is not None else extract_entities(message)

#     if user_id:
#         state = ctx.get_state(user_id)
#         if state:
#             resumed = _resume_conversation_state(message, user_id, state)
#             if resumed is not None:
#                 return resumed

#     handler = INTENT_HANDLERS.get(intent, handle_fallback)

#     try:
#         return handler(message, user_id, entities)
#     except ServiceError as exc:
#         return _result(str(exc), None)
#     except Exception:
#         return _result("Something went wrong while processing that. Please try again.", None)



"""
chatbot/actions.py

Intent router. Every intent tag from intents.json maps to exactly one
handler function below. Handlers NEVER touch Supabase directly - they
only call functions from the services/ layer.

Each handler returns a dict: {"message": str, "data": Any}

Multi-turn flows are driven by context_manager:
  - WAITING_FOR_ADDRESS: after asking for a shipping address, the very
    next message is used as-is (no re-classification).
  - WAITING_FOR_PRODUCT: after asking "which product?", the next
    message is resolved to a product either by an extracted product_id
    or by name-searching the catalog - this is what fixes the old bug
    where typing a product name after being asked for an ID just
    re-triggered category browsing instead of completing the add.
  - WAITING_FOR_ORDER_ID: same idea, for track/cancel/refund order.
"""

from typing import Any, Callable, Optional

from chatbot import context_manager as ctx
from chatbot.entity_extractor import extract_entities
from chatbot.predict import get_response_for_intent

from services import product_service, cart_service, order_service, user_service, notification_service
from services.utils import ServiceError

Entities = dict[str, Any]
ActionResult = dict[str, Any]  # {"message": str, "data": Any}
Handler = Callable[[str, Optional[str], Entities], ActionResult]

ESCALATION_FOOTER = (
    "Kindly note, I've forwarded this to our senior support manager - "
    "they'll call you or email you back within the next 3 business days. "
    "Thank you for your patience \U0001F64F"
)


def _result(message: str, data: Any = None) -> ActionResult:
    return {"message": message, "data": data}


def _require_login(user_id: Optional[str]) -> Optional[ActionResult]:
    if not user_id:
        return _result("Please log in first so I can do that for you.", None)
    return None


def _summary_line(p: dict) -> str:
    return f"- **{p['name']}** - {p['price']} PKR"


# ---------------------------------------------------------------------------
# Product / order resolution helpers (used both inline and on state-resume)
# ---------------------------------------------------------------------------

def _resolve_product(message: str, entities: Entities) -> Optional[dict]:
    """
    Resolve a product from (in order): an explicit product_id entity,
    a capitalized-phrase guess extracted from the sentence (handles
    "what's the stock of Kids School Bag" where the whole sentence
    would never match via ILIKE), or a name search on the raw message
    as a last resort. Returns the full product dict, or None.
    """
    product_id = entities.get("product_id")
    if product_id:
        try:
            return product_service.get_product_by_id(product_id)["data"]
        except ServiceError:
            pass

    for keyword in filter(None, [entities.get("product_name_guess"), message]):
        try:
            matches = product_service.search_product(keyword)["data"]
        except ServiceError:
            matches = []
        if matches:
            return matches[0]

    return None


def _resolve_order_id(entities: Entities) -> Optional[str]:
    return entities.get("order_id")


# ---------------------------------------------------------------------------
# Conversational / canned intents (sourced from intents.json)
# ---------------------------------------------------------------------------

def _canned(intent_tag: str) -> Handler:
    def _handler(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
        return _result(get_response_for_intent(intent_tag))
    return _handler


def _escalate(intent_tag: str) -> Handler:
    """
    Complaint-style intents: acknowledge with the canned line from
    intents.json, email the admin the full query, and append the
    standard "escalated to a manager" footer.
    """
    def _handler(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
        acknowledgment = get_response_for_intent(intent_tag)
        try:
            notification_service.notify_customer_query(user_id, intent_tag, message)
        except Exception:
            pass  # never let email failure break the chat reply
        return _result(f"{acknowledgment}\n\n{ESCALATION_FOOTER}")
    return _handler


# ---------------------------------------------------------------------------
# Product intents
# ---------------------------------------------------------------------------

def handle_show_products(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    products = product_service.get_all_products()["data"]
    text = "Here's our catalog:\n\n" + "\n".join(_summary_line(p) for p in products[:5]) if products else "No products are currently available."
    return _result(text, products)


def handle_search_product(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    keyword = entities.get("brand") or entities.get("category") or message
    products = product_service.search_product(keyword)["data"]
    text = f"Results for '{keyword}':\n\n" + "\n".join(_summary_line(p) for p in products[:5]) if products else f"No products found matching '{keyword}'."
    return _result(text, products)


def handle_search_by_category(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    category = entities.get("category")
    if not category:
        return _result("Which category would you like to browse - Men, Women, Kids, or Electronics?", [])
    products = product_service.search_by_category(category)["data"]
    text = f"Products in '{category}':\n\n" + "\n".join(_summary_line(p) for p in products[:5]) if products else f"No products found in category '{category}'."
    return _result(text, products)


def handle_search_by_price(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    price = entities.get("price")
    if price is None:
        return _result("What's your budget? For example, 'products under 3000'.", [])
    products = product_service.search_by_price(price)["data"]
    text = f"Products under {price:.0f} PKR:\n\n" + "\n".join(_summary_line(p) for p in products[:5]) if products else f"No products found under {price:.0f} PKR."
    return _result(text, products)


def handle_product_details(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    p = _resolve_product(message, entities)
    if not p:
        ctx.set_state(user_id or "guest", ctx.WAITING_FOR_PRODUCT, {"intent": "product_details"})
        return _result("Which product would you like details for? You can give me the product ID or its name.", None)
    text = (
        f"**{p['name']}**\n"
        f"Price: {p['price']} PKR\n"
        f"Stock: {p.get('stock', 'N/A')}\n"
        f"Description: {p.get('description', 'N/A')}"
    )
    return _result(text, p)


def handle_check_stock(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    p = _resolve_product(message, entities)
    if not p:
        ctx.set_state(user_id or "guest", ctx.WAITING_FOR_PRODUCT, {"intent": "check_stock"})
        return _result("Which product's stock would you like me to check? Give me the product ID or its name.", None)
    stock = p.get("stock", 0)
    if stock <= 0:
        text = f"**{p['name']}** is currently out of stock."
    else:
        text = f"**{p['name']}** has {stock} unit(s) currently in stock."
    return _result(text, p)


def handle_best_sellers(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    products = product_service.get_best_sellers()["data"]
    text = "Our best sellers:\n\n" + "\n".join(_summary_line(p) for p in products[:5]) if products else "No best sellers to show yet."
    return _result(text, products)


def handle_new_arrivals(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    products = product_service.get_new_arrivals()["data"]
    text = "Fresh new arrivals:\n\n" + "\n".join(_summary_line(p) for p in products[:5]) if products else "No new arrivals yet."
    return _result(text, products)


def _handle_fixed_category(category_name: str) -> Handler:
    def _handler(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
        products = product_service.search_by_category(category_name)["data"]
        text = (
            f"Here are the latest items in **{category_name}**:\n\n" + "\n".join(_summary_line(p) for p in products[:5])
            if products
            else f"Currently, we don't have any products listed in {category_name}."
        )
        return _result(text, products)
    return _handler


# ---------------------------------------------------------------------------
# Cart intents
# ---------------------------------------------------------------------------

def handle_add_to_cart(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    if (err := _require_login(user_id)):
        return err

    p = _resolve_product(message, entities)
    if not p:
        ctx.set_state(user_id, ctx.WAITING_FOR_PRODUCT, {"intent": "add_to_cart"})
        return _result("Which product would you like to add? Give me the product ID or its name.", None)

    quantity = entities.get("quantity") or 1
    result = cart_service.add_to_cart(user_id, p["id"], quantity)
    ctx.clear_state(user_id)
    return _result(f"Added **{p['name']}** to your cart!", result["data"])


def handle_remove_from_cart(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    if (err := _require_login(user_id)):
        return err

    p = _resolve_product(message, entities)
    if not p:
        ctx.set_state(user_id, ctx.WAITING_FOR_PRODUCT, {"intent": "remove_from_cart"})
        return _result("Which product should I remove? Give me the product ID or its name.", None)

    cart_service.remove_from_cart(user_id, p["id"])
    ctx.clear_state(user_id)
    return _result(f"Removed **{p['name']}** from your cart.", None)


def handle_show_cart(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    if (err := _require_login(user_id)):
        return err
    items = cart_service.get_cart(user_id)["data"]
    if not items:
        return _result("Your cart is empty.", [])
    total = cart_service.cart_total(user_id)["data"]["total"]
    lines = [f"- **{i['products']['name']}** (x{i['quantity']})" for i in items if i.get("products")]
    text = "Your cart:\n\n" + "\n".join(lines) + f"\n\n**Total: {total:.2f} PKR**"
    return _result(text, {"items": items, "total": total})


def handle_apply_coupon(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    if (err := _require_login(user_id)):
        return err

    code = entities.get("coupon_code")
    if not code:
        return _result("Which coupon code would you like to apply? For example: 'apply SUMMER20'.", None)

    cart_response = cart_service.get_cart(user_id)
    items = cart_response["data"]
    if not items:
        return _result("Your cart is empty, so there's nothing to apply a coupon to yet.", None)

    subtotal = cart_service.cart_total(user_id)["data"]["total"]
    try:
        discount = order_service.apply_coupon(code, subtotal)["data"]
    except ServiceError as exc:
        return _result(str(exc), None)

    text = (
        f"Coupon **{code}** applied! \n"
        f"Subtotal: {subtotal:.2f} PKR\n"
        f"Discount: -{discount['discount_amount']:.2f} PKR\n"
        f"**New total: {discount['final_total']:.2f} PKR**"
    )
    return _result(text, discount)


# ---------------------------------------------------------------------------
# Order intents
# ---------------------------------------------------------------------------

def handle_checkout(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    if (err := _require_login(user_id)):
        return err
    address = entities.get("address")
    if not address:
        ctx.set_state(user_id, ctx.WAITING_FOR_ADDRESS, {"intent": "checkout"})
        return _result("Sure! What's the shipping address for this order?", None)
    order = order_service.checkout(user_id, address, coupon_code=entities.get("coupon_code"))["data"]
    ctx.clear_state(user_id)
    return _result(f"Order placed! Order ID: `{order['id']}`, Total: {order['total']} PKR.", order)


def handle_track_order(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    order_id = _resolve_order_id(entities)
    if not order_id:
        ctx.set_state(user_id or "guest", ctx.WAITING_FOR_ORDER_ID, {"intent": "track_order"})
        return _result("What's your order ID?", None)
    o = order_service.track_order(order_id)["data"]
    return _result(f"\U0001F4E6 Order `{o['id']}` status: **{o['status']}**, Total: {o['total']} PKR.", o)


def handle_cancel_order(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    order_id = _resolve_order_id(entities)
    if not order_id:
        ctx.set_state(user_id or "guest", ctx.WAITING_FOR_ORDER_ID, {"intent": "cancel_order"})
        return _result("Which order would you like to cancel? Please provide the order ID.", None)
    order = order_service.cancel_order(order_id)["data"]
    return _result(f"Order `{order_id}` has been cancelled.", order)


def handle_refund_order(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    order_id = _resolve_order_id(entities)
    if not order_id:
        ctx.set_state(user_id or "guest", ctx.WAITING_FOR_ORDER_ID, {"intent": "refund_order"})
        return _result("Which order would you like refunded? Please provide the order ID.", None)
    order = order_service.refund_order(order_id, reason=message)["data"]
    try:
        notification_service.notify_customer_query(user_id, "refund_order", message)
    except Exception:
        pass
    return _result(
        f"Your refund for order `{order_id}` has been submitted and is being processed. "
        "You'll be notified once it's complete.",
        order,
    )


def handle_order_history(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    if (err := _require_login(user_id)):
        return err
    orders = order_service.order_history(user_id)["data"]
    if not orders:
        return _result("You haven't placed any orders yet.", [])
    lines = [f"- `{o['id']}` - {o['status']} - {o['total']} PKR" for o in orders[:10]]
    return _result("Your recent orders:\n\n" + "\n".join(lines), orders)


# ---------------------------------------------------------------------------
# Account intents
# ---------------------------------------------------------------------------

def handle_update_shipping_address(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    if (err := _require_login(user_id)):
        return err

    address = entities.get("address")
    if not address:
        ctx.set_state(user_id, ctx.WAITING_FOR_ADDRESS, {"intent": "update_shipping_address"})
        return _result("Sure! Please send me your new shipping address.", None)

    result = user_service.update_shipping_address(user_id, address)
    ctx.clear_state(user_id)
    return _result(f"Your shipping address has been updated to: {address}", result["data"])


def handle_wishlist_add(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    if (err := _require_login(user_id)):
        return err

    p = _resolve_product(message, entities)
    if not p:
        ctx.set_state(user_id, ctx.WAITING_FOR_PRODUCT, {"intent": "wishlist_add"})
        return _result("Which product should I add to your wishlist? Give me the product ID or its name.", None)

    user_service.wishlist_add(user_id, p["id"])
    ctx.clear_state(user_id)
    return _result(f"Added **{p['name']}** to your wishlist!", None)


def handle_show_wishlist(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    if (err := _require_login(user_id)):
        return err
    items = user_service.wishlist(user_id)["data"]
    if not items:
        return _result("Your wishlist is empty.", [])
    lines = [f"- {i['products']['name']}" for i in items if i.get("products")]
    return _result("Your wishlist:\n\n" + "\n".join(lines), items)


# ---------------------------------------------------------------------------
# Static / informational intents (no service call needed)
# ---------------------------------------------------------------------------

def handle_fallback(message: str, user_id: Optional[str], entities: Entities) -> ActionResult:
    try:
        notification_service.notify_customer_query(user_id, "fallback", message)
    except Exception:
        pass
    return _result(get_response_for_intent("fallback"), None)


# ---------------------------------------------------------------------------
# Dictionary-based intent routing table - keys MUST match intents.json tags
# ---------------------------------------------------------------------------

INTENT_HANDLERS: dict[str, Handler] = {
    "greeting": _canned("greeting"),
    "goodbye": _canned("goodbye"),
    "thanks": _canned("thanks"),
    "payment_methods": _canned("payment_methods"),
    "shipping_policy": _canned("shipping_policy"),
    "ship_international": _canned("ship_international"),
    "refund_policy": _canned("refund_policy"),
    "discounts": _canned("discounts"),
    "membership_offer": _canned("membership_offer"),
    "data_privacy_policy": _canned("data_privacy_policy"),
    "forgot_password": _canned("forgot_password"),
    "contact": _canned("contact"),

    "payment_failed": _escalate("payment_failed"),
    "coupon_issue": _escalate("coupon_issue"),
    "shipping_cost_complaint": _escalate("shipping_cost_complaint"),
    "checkout_trouble": _escalate("checkout_trouble"),
    "delayed_order": _escalate("delayed_order"),
    "wrong_item": _escalate("wrong_item"),
    "damaged_product": _escalate("damaged_product"),
    "warranty_claim": _escalate("warranty_claim"),
    "account_locked": _escalate("account_locked"),
    "complaint_general": _escalate("complaint_general"),
    "feedback": _escalate("feedback"),

    "show_products": handle_show_products,
    "search_product": handle_search_product,
    "search_by_category": handle_search_by_category,
    "search_by_price": handle_search_by_price,
    "product_details": handle_product_details,
    "check_stock": handle_check_stock,
    "best_sellers": handle_best_sellers,
    "new_arrivals": handle_new_arrivals,
    "men_products": _handle_fixed_category("Men"),
    "women_products": _handle_fixed_category("Women"),
    "kids_products": _handle_fixed_category("Kids"),
    "electronics": _handle_fixed_category("Electronics"),

    "add_to_cart": handle_add_to_cart,
    "remove_from_cart": handle_remove_from_cart,
    "show_cart": handle_show_cart,
    "apply_coupon": handle_apply_coupon,

    "checkout": handle_checkout,
    "track_order": handle_track_order,
    "cancel_order": handle_cancel_order,
    "refund_order": handle_refund_order,
    "order_history": handle_order_history,

    "update_shipping_address": handle_update_shipping_address,
    "wishlist_add": handle_wishlist_add,
    "show_wishlist": handle_show_wishlist,

    "fallback": handle_fallback,
}


def _resume_conversation_state(message: str, user_id: str, state: dict, raw_entities: Entities) -> Optional[ActionResult]:
    """
    If the user is mid-flow (e.g. we just asked for an address, a
    product, or an order ID), treat this message as the answer to that
    question. Each branch consumes the state either way - if it can't
    resolve an answer from this message, it clears the state and
    returns None so the message falls through to normal intent
    classification instead of re-prompting forever (that re-prompt
    loop was the original bug: an unrelated follow-up message kept
    getting hijacked by a stale "which product?" question).
    """
    state_name = state["state"]
    pending_intent = state["data"].get("intent")
    handler = INTENT_HANDLERS.get(pending_intent)
    if not handler:
        ctx.clear_state(user_id)
        return None

    if state_name == ctx.WAITING_FOR_ADDRESS:
        ctx.clear_state(user_id)
        return handler(message, user_id, {**raw_entities, "address": message.strip()})

    if state_name == ctx.WAITING_FOR_PRODUCT:
        product = _resolve_product(message, raw_entities)
        ctx.clear_state(user_id)
        if product is None:
            return None  # give up gracefully - let this message be classified normally
        return handler(message, user_id, {**raw_entities, "product_id": product["id"]})

    if state_name == ctx.WAITING_FOR_ORDER_ID:
        order_id = raw_entities.get("order_id")
        if not order_id:
            candidate = message.strip()
            if candidate.replace(" ", "").isalnum() and len(candidate) <= 20:
                order_id = candidate
        ctx.clear_state(user_id)
        if not order_id:
            return None
        return handler(message, user_id, {**raw_entities, "order_id": order_id})

    ctx.clear_state(user_id)
    return None


def execute_action(intent: str, message: str = "", user_id: Optional[str] = None, entities: Optional[Entities] = None) -> ActionResult:
    """
    Route a predicted intent to its handler.

    Returns:
        {"message": str, "data": Any}. Never raises - service errors are
        caught and turned into a friendly message with data=None.
    """
    entities = entities if entities is not None else extract_entities(message)

    state_key = user_id or "guest"
    state = ctx.get_state(state_key)
    if state:
        resumed = _resume_conversation_state(message, state_key, state, entities)
        if resumed is not None:
            return resumed

    handler = INTENT_HANDLERS.get(intent, handle_fallback)

    try:
        return handler(message, user_id, entities)
    except ServiceError as exc:
        return _result(str(exc), None)
    except Exception:
        return _result("Something went wrong while processing that. Please try again.", None)