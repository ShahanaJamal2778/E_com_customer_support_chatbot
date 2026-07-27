"""
chatbot/predict.py

Loads the trained TensorFlow intent-classification model (trained by
chatbot/train.py, bag-of-words representation) and turns a raw user
message into a predicted intent tag. This module NEVER touches
Supabase - it only knows about text in, intent out.

Artifacts expected (produced by train.py):
    chatbot/model/chatbot_model.keras
    chatbot/model/words.pkl
    chatbot/model/classes.pkl
"""

import json
import pickle
import random
from pathlib import Path

import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

_BASE_DIR = Path(__file__).parent
_MODEL_DIR = _BASE_DIR / "model"

# Exposed so chat_router.py can apply the same threshold the model was
# tuned against. predict_intent() itself stays a pure classifier - it
# does NOT decide the fallback; that's an orchestration decision made
# by the caller (see routers/chat_router.py).
CONFIDENCE_THRESHOLD = 0.70

_lemmatizer = WordNetLemmatizer()

_model = None
_words: list[str] | None = None
_classes: list[str] | None = None


def _load_artifacts() -> None:
    """Lazily load the model + vocabulary artifacts (once per process)."""
    global _model, _words, _classes

    if _model is not None:
        return

    model_path = _MODEL_DIR / "chatbot_model.keras"
    words_path = _MODEL_DIR / "words.pkl"
    classes_path = _MODEL_DIR / "classes.pkl"

    if not (model_path.exists() and words_path.exists() and classes_path.exists()):
        raise FileNotFoundError(
            "Model artifacts not found in chatbot/model/. Run "
            "`python -m chatbot.train` first to train and save the model."
        )

    _model = load_model(model_path)

    with open(words_path, "rb") as f:
        _words = pickle.load(f)
    with open(classes_path, "rb") as f:
        _classes = pickle.load(f)


def _tokenize(message: str) -> list[str]:
    """Tokenize + lemmatize + lowercase a message, matching train.py."""
    tokens = nltk.word_tokenize(message)
    return [_lemmatizer.lemmatize(t.lower()) for t in tokens]


def _bag_of_words(message: str) -> np.ndarray:
    """Vectorize a message into the same bag-of-words space as training."""
    tokens = _tokenize(message)
    bag = [1 if w in tokens else 0 for w in _words]
    return np.array([bag], dtype=np.float32)


def predict_intent(message: str) -> dict:
    """
    Predict the raw top intent tag for a message. This is a pure
    classifier: it always returns its best guess and the model's
    confidence for that guess, with NO fallback logic applied. The
    caller (chat_router.py) is responsible for comparing the returned
    confidence against CONFIDENCE_THRESHOLD and substituting the
    "fallback" intent when the model isn't confident enough.

    Returns:
        {"intent": str, "confidence": float}
    """
    if not message or not message.strip():
        return {"intent": "fallback", "confidence": 0.0}

    _load_artifacts()

    bag = _bag_of_words(message)
    probabilities = _model.predict(bag, verbose=0)[0]

    best_index = int(np.argmax(probabilities))
    confidence = float(probabilities[best_index])
    intent_tag = _classes[best_index]

    return {"intent": intent_tag, "confidence": confidence}


def get_response_for_intent(intent_tag: str) -> str:
    """
    Pick a random canned response for an intent from intents.json.
    Used only for purely conversational intents (greeting, thanks,
    goodbye, policy questions). Data-driven intents get their reply
    from actions.py / the service layer instead.
    """
    intents_path = _BASE_DIR / "intents.json"
    with open(intents_path, "r", encoding="utf-8") as f:
        intents_data = json.load(f)

    for intent in intents_data["intents"]:
        if intent["tag"] == intent_tag:
            return random.choice(intent["responses"])

    return "I'm not sure how to respond to that."