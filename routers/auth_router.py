"""
routers/auth_router.py

Registration and login. Delegates entirely to services/auth_service.py
- no SQL, no password logic here.
"""

from fastapi import APIRouter, status

from schemas.requests import RegisterRequest, LoginRequest
from schemas.responses import StandardResponse
from services import auth_service
from routers.common import run_service

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    """Create a new user account."""
    return run_service(
        auth_service.register,
        payload.email,
        payload.full_name,
        payload.password,
        payload.phone,
    )


@router.post("/login", response_model=StandardResponse, status_code=status.HTTP_200_OK)
def login(payload: LoginRequest):
    """Authenticate a user by email + password."""
    return run_service(auth_service.login, payload.email, payload.password)