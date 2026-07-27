"""
services/chatbot_service.py

Persists chatbot conversation logs. No SQL outside this module for
the `chatbot_logs` table.
"""

from typing import Optional

from database.supabase import supabase
from services.utils import ok, ValidationError


def save_chat(user_id: Optional[str], question: str, intent: str, response: str) -> dict:
    """Persist one full chat turn (question + predicted intent + response)."""
    if not question or not intent:
        raise ValidationError("question and intent are required.")

    result = (
        supabase.table("chatbot_logs")
        .insert(
            {
                "user_id": user_id,
                "question": question,
                "intent": intent,
                "response": response,
            }
        )
        .execute()
    )
    return ok(result.data[0] if result.data else None, "Chat log saved.")


def save_intent(log_id: str, intent: str) -> dict:
    """Update the recorded intent for an existing chat log entry."""
    if not log_id or not intent:
        raise ValidationError("log_id and intent are required.")

    result = (
        supabase.table("chatbot_logs").update({"intent": intent}).eq("id", log_id).execute()
    )
    return ok(result.data[0] if result.data else None)


def save_question(log_id: str, question: str) -> dict:
    """Update the recorded question text for an existing chat log entry."""
    if not log_id or not question:
        raise ValidationError("log_id and question are required.")

    result = (
        supabase.table("chatbot_logs")
        .update({"question": question})
        .eq("id", log_id)
        .execute()
    )
    return ok(result.data[0] if result.data else None)


def save_response(log_id: str, response: str) -> dict:
    """Update the recorded bot response for an existing chat log entry."""
    if not log_id or response is None:
        raise ValidationError("log_id and response are required.")

    result = (
        supabase.table("chatbot_logs")
        .update({"response": response})
        .eq("id", log_id)
        .execute()
    )
    return ok(result.data[0] if result.data else None)


def chat_history(user_id: str, limit: int = 50) -> dict:
    """Return a user's recent chat history, most recent first."""
    if not user_id:
        raise ValidationError("user_id is required.")

    result = (
        supabase.table("chatbot_logs")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return ok(result.data)