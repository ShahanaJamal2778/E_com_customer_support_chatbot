"""
routers/chat_router.py

The core chatbot pipeline, wired end-to-end:

    user message
        |
        v
    predict.py        -> raw intent + confidence (TensorFlow)
        |
        v
    confidence check   -> if confidence < CONFIDENCE_THRESHOLD, use "fallback"
        |
        v
    entity_extractor.py -> structured entities (regex, no ML)
        |
        v
    actions.py          -> executes business logic via the service layer,
                            resuming any in-flight multi-turn state from
                            context_manager.py
        |
        v
    chatbot_service.py  -> logs the turn to chatbot_logs (best-effort)
        |
        v
    structured JSON response
"""

from fastapi import APIRouter

from schemas.requests import ChatRequest
from schemas.responses import ChatResponse

from chatbot.predict import predict_intent, CONFIDENCE_THRESHOLD
from chatbot.entity_extractor import extract_entities
from chatbot.actions import execute_action
from services import chatbot_service
from services.utils import ServiceError

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    """
    Classify the user's message, extract entities, execute the
    matching business action, log the turn, and return a structured
    response the frontend can render directly.
    """
    # 1. Predict intent (pure TensorFlow classification, no fallback logic).
    prediction = predict_intent(payload.message)
    raw_intent = prediction["intent"]
    confidence = prediction["confidence"]

    # 2. Apply the confidence threshold. Below 0.70, treat as "fallback"
    #    regardless of what the model's top guess was.
    intent = raw_intent if confidence >= CONFIDENCE_THRESHOLD else "fallback"

    # 3. Extract structured entities from the raw message (regex-based).
    entities = extract_entities(payload.message)

    # 4. Execute the business action for this intent. This is the only
    #    place that talks to the service layer / context_manager for
    #    multi-turn state.
    result = execute_action(
        intent=intent,
        message=payload.message,
        user_id=payload.user_id,
        entities=entities,
    )

    # 5. Log the full turn. Logging failures must never break the chat
    #    reply itself.
    try:
        chatbot_service.save_chat(
            user_id=payload.user_id,
            question=payload.message,
            intent=intent,
            response=result["message"],
        )
    except ServiceError:
        pass

    # 6. Return the structured contract the frontend expects.
    return ChatResponse(
        intent=intent,
        confidence=round(confidence, 4),
        entities=entities,
        message=result["message"],
        data=result["data"],
    )