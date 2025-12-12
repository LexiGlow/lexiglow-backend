"""Authentication API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dto.user_dto import UserCreate, UserResponse
from app.application.services.user_service import UserService
from app.core.dependencies import get_user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth")


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign up",
    description="Create a new user account with email, username, and password.",
)
async def signup(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),  # noqa: B008
) -> UserResponse:
    """
    Register a new user with validation and password hashing.

    Args:
        payload: Signup data including email, username, and password.
        service: User service instance (injected).

    Returns:
        Created user response without password hash.

    Raises:
        HTTPException: 400 for validation issues, 409 for duplicates, 500 otherwise.
    """
    try:
        logger.info("POST /auth/signup called for email=%s", payload.email)
        user = await service.create_user(payload)
        logger.info("User signed up successfully: %s", user.id)
        return user
    except ValueError as exc:
        # Conflicts (email/username already exist)
        logger.warning("Signup conflict: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "Conflict", "message": str(exc)},
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - safety net
        logger.error("Internal error during signup: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(exc)},
        ) from exc
