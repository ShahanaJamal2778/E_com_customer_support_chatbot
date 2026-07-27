"""
schemas/responses.py

All Pydantic response (output) models. `StandardResponse` wraps every
plain CRUD endpoint (the service layer already returns this exact
shape as a dict: {"success", "message", "data"}). `ChatResponse` is
the dedicated contract for the /chat endpoint.
"""

from typing import Any, Optional
from pydantic import BaseModel


class StandardResponse(BaseModel):
    """Generic envelope returned by every non-chat endpoint."""
    success: bool
    message: str
    data: Optional[Any] = None


class ChatResponse(BaseModel):
    """
    Structured contract for POST /chat.

    intent      - final intent tag (already fallback-adjusted if the
                  model's confidence was below CONFIDENCE_THRESHOLD)
    confidence  - the model's raw confidence for its top prediction
    entities    - entities extracted from the user's message
    message     - human-readable chat reply
    data        - structured payload behind the reply (product list,
                  cart, order, etc.), or null for purely conversational
                  intents
    """
    intent: str
    confidence: float
    entities: dict[str, Any]
    message: str
    data: Optional[Any] = None