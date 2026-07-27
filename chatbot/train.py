"""
chatbot/train.py

Trains the TensorFlow intent-classification model from intents.json
using a bag-of-words representation. Run this whenever intents.json
changes:

    python -m chatbot.train

Produces (consumed by chatbot/predict.py):
    chatbot/model/chatbot_model.keras
    chatbot/model/words.pkl
    chatbot/model/classes.pkl
"""

import json
import pickle
import random
from pathlib import Path

import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import SGD

# One-time NLTK data downloads (no-ops if already present).
for pkg in ("punkt", "punkt_tab", "wordnet", "omw-1.4"):
    try:
        nltk.data.find(f"tokenizers/{pkg}" if "punkt" in pkg else f"corpora/{pkg}")
    except LookupError:
        nltk.download(pkg, quiet=True)

lemmatizer = WordNetLemmatizer()

BASE_DIR = Path(__file__).parent
MODEL_DIR = BASE_DIR / "model"
MODEL_DIR.mkdir(exist_ok=True)

INTENTS_PATH = BASE_DIR / "intents.json"
IGNORE_WORDS = {"?", "!", ".", ","}

words = []
classes = []
documents = []

with open(INTENTS_PATH, "r", encoding="utf-8") as f:
    intents = json.load(f)

for intent in intents["intents"]:
    for pattern in intent["patterns"]:
        tokens = nltk.word_tokenize(pattern)
        words.extend(tokens)
        documents.append((tokens, intent["tag"]))

        if intent["tag"] not in classes:
            classes.append(intent["tag"])

# Lemmatize + lowercase every token, drop punctuation, dedupe, sort.
words = sorted(set(lemmatizer.lemmatize(w.lower()) for w in words if w not in IGNORE_WORDS))
classes = sorted(set(classes))

print(len(documents), "documents")
print(len(classes), "classes:", classes)
print(len(words), "unique lemmatized words")

with open(MODEL_DIR / "words.pkl", "wb") as f:
    pickle.dump(words, f)
with open(MODEL_DIR / "classes.pkl", "wb") as f:
    pickle.dump(classes, f)

# Build bag-of-words training vectors.
training = []
output_empty = [0] * len(classes)

for pattern_words, tag in documents:
    pattern_words = [lemmatizer.lemmatize(w.lower()) for w in pattern_words]
    bag = [1 if w in pattern_words else 0 for w in words]

    output_row = list(output_empty)
    output_row[classes.index(tag)] = 1

    training.append([bag, output_row])

random.shuffle(training)
train_x = np.array([row[0] for row in training])
train_y = np.array([row[1] for row in training])
print("Training data created:", train_x.shape, train_y.shape)

# 3-layer network: 128 -> 64 -> softmax(num_classes).
model = Sequential([
    Dense(128, input_shape=(len(train_x[0]),), activation="relu"),
    Dropout(0.5),
    Dense(64, activation="relu"),
    Dropout(0.5),
    Dense(len(train_y[0]), activation="softmax"),
])

sgd = SGD(learning_rate=0.01, weight_decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss="categorical_crossentropy", optimizer=sgd, metrics=["accuracy"])

model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)

# NOTE: model.save() only takes a filepath - passing `hist` as a second
# positional argument (as in the original script) silently misuses the
# `overwrite` parameter. Save the model only; keep `hist` in memory if
# you want to inspect training curves separately.
model.save(MODEL_DIR / "chatbot_model.keras")

print("Model created and saved to", MODEL_DIR / "chatbot_model.keras")