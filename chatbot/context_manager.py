"""
chatbot/context_manager.py

Tracks per-user multi-turn conversation state (e.g. "waiting for the
user to send their new shipping address"). Backed by a simple
in-memory dict, keyed by user_id.

NOTE: In-memory state is fine for a single-process FYP deployment /
demo. For a multi-worker production deployment, swap the dict below
for a Redis-backed store without changing the public functions - that
is the whole point of isolating this behind a small API.
"""

from typing import Any, Optional

# { user_id: {"state": str, "data": dict} }
_conversation_state: dict[str, dict[str, Any]] = {}


def set_state(user_id: str, state: str, data: Optional[dict] = None) -> None:
    """Mark a user as waiting for a specific follow-up input."""
    _conversation_state[user_id] = {"state": state, "data": data or {}}


def get_state(user_id: str) -> Optional[dict]:
    """Return the current state for a user, or None if there isn't one."""
    return _conversation_state.get(user_id)


def is_waiting_for(user_id: str, state: str) -> bool:
    """Check whether a user is currently waiting in a specific state."""
    current = _conversation_state.get(user_id)
    return bool(current and current["state"] == state)


def update_data(user_id: str, key: str, value: Any) -> None:
    """Attach a piece of data to a user's in-progress conversation state."""
    if user_id not in _conversation_state:
        _conversation_state[user_id] = {"state": None, "data": {}}
    _conversation_state[user_id]["data"][key] = value


def clear_state(user_id: str) -> None:
    """Clear a user's conversation state (call this once a flow completes)."""
    _conversation_state.pop(user_id, None)


# Well-known state names, defined centrally so actions.py and predict.py
# don't rely on scattered magic strings.
WAITING_FOR_ADDRESS = "waiting_for_address"
WAITING_FOR_PRODUCT = "waiting_for_product"
WAITING_FOR_ORDER_ID = "waiting_for_order_id"
WAITING_FOR_NAME = "waiting_for_name"
WAITING_FOR_PHONE = "waiting_for_phone"
WAITING_FOR_EMAIL = "waiting_for_email"
WAITING_FOR_CITY = "waiting_for_city"
WAITING_FOR_REVIEW_RATING = "waiting_for_review_rating"