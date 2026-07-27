"""
api.py

FastAPI application entrypoint. This file does exactly two things:
  1. Registers every feature router.
  2. Serves the static HTML/CSS/JS frontend.

No business logic, no SQL, and no route handlers live here directly -
see routers/ for those.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from routers import (
    auth_router,
    product_router,
    cart_router,
    order_router,
    user_router,
    chat_router,
)

BASE_DIR = Path(__file__).parent

app = FastAPI(
    title="Jamal Cart Chatbot API",
    description="AI-powered e-commerce chatbot backend for Jamal Cart.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this for production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Feature routers - each owns one slice of the API surface.
app.include_router(auth_router.router)
app.include_router(product_router.router)
app.include_router(cart_router.router)
app.include_router(order_router.router)
app.include_router(user_router.router)
app.include_router(chat_router.router)

# Serve the frontend's static assets (CSS/JS/images) at /static/*.
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend():
    """Serve the single-page frontend."""
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.get("/health", tags=["System"])
def health_check():
    """Simple liveness check."""
    return {"status": "ok"}