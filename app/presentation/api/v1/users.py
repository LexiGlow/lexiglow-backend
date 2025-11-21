"""User API endpoints.

This module provides REST API handlers for user CRUD operations using FastAPI.
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.dto.user_dto import UserCreate, UserResponse, UserUpdate
from app.application.services.user_service import UserService
from app.core.dependencies import get_user_service

logger = logging.getLogger(__name__)

# Create router for user endpoints
router = APIRouter(prefix="/users")


@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all users",
    description="Retrieve a paginated list of users",
)
async def get_users(
    skip: Annotated[
        int, Query(ge=0, description="Number of users to skip (pagination)")
    ] = 0,
    limit: Annotated[
        int, Query(ge=1, le=1000, description="Maximum number of users to return")
    ] = 100,
    service: UserService = Depends(get_user_service),  # noqa: B008
) -> list[UserResponse]:
    """
    Get all users with pagination.

    Args:
        skip: Number of users to skip (for pagination)
        limit: Maximum number of users to return
        service: User service instance (injected)

    Returns:
        List of user response objects

    Raises:
        HTTPException: 500 if an internal server error occurs
    """
    try:
        logger.info(f"GET /users called with skip={skip}, limit={limit}")
        users = await service.get_all_users(skip=skip, limit=limit)
        logger.info(f"Retrieved {len(users)} users")
        return users

    except Exception as e:
        logger.error(f"Error retrieving users: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e


@router.get(
    "/{userId}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Retrieve a specific user by their UUID",
)
async def get_user_by_id(
    userId: UUID,
    service: UserService = Depends(get_user_service),  # noqa: B008
) -> UserResponse:
    """
    Get a user by ID.

    Args:
        userId: User UUID
        service: User service instance (injected)

    Returns:
        User response object

    Raises:
        HTTPException: 404 if user not found, 500 if internal server error
    """
    try:
        logger.info(f"GET /users/{userId} called")
        user = await service.get_user(userId)

        if user is None:
            logger.warning(f"User not found: {userId}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "User not found",
                    "message": f"User with ID {userId} does not exist",
                },
            )

        logger.info(f"Retrieved user: {userId}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {userId}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user account with the provided information",
)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),  # noqa: B008
) -> UserResponse:
    """
    Create a new user.

    Args:
        user_data: User creation data (validated automatically by FastAPI)
        service: User service instance (injected)

    Returns:
        Created user response object

    Raises:
        HTTPException: 400 if validation fails, 409 if conflict,
            500 if internal server error
    """
    try:
        logger.info(f"POST /users called with email: {user_data.email}")

        try:
            created_user = await service.create_user(user_data)
            logger.info(f"User created successfully: {created_user.id}")
            return created_user

        except ValueError as e:
            # Email or username already exists
            logger.warning(f"Conflict error: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "Conflict", "message": str(e)},
            ) from e

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e


@router.put(
    "/{userId}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user",
    description="Update an existing user's information",
)
async def update_user(
    userId: UUID,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service),  # noqa: B008
) -> UserResponse:
    """
    Update a user.

    Args:
        userId: User UUID
        user_data: User update data (validated automatically by FastAPI)
        service: User service instance (injected)

    Returns:
        Updated user response object

    Raises:
        HTTPException: 400 if validation fails, 404 if not found,
            409 if conflict, 500 if internal server error
    """
    try:
        logger.info(f"PUT /users/{userId} called")

        try:
            updated_user = await service.update_user(userId, user_data)

            if updated_user is None:
                logger.warning(f"User not found: {userId}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "User not found",
                        "message": f"User with ID {userId} does not exist",
                    },
                )

            logger.info(f"User updated successfully: {userId}")
            return updated_user

        except ValueError as e:
            # Email or username conflict
            logger.warning(f"Conflict error: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "Conflict", "message": str(e)},
            ) from e

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {userId}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e


@router.delete(
    "/{userId}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete an existing user by their UUID",
)
async def delete_user(
    userId: UUID,
    service: UserService = Depends(get_user_service),  # noqa: B008
) -> None:
    """
    Delete a user.

    Args:
        userId: User UUID
        service: User service instance (injected)

    Returns:
        None (204 No Content on success)

    Raises:
        HTTPException: 404 if user not found, 500 if internal server error
    """
    try:
        logger.info(f"DELETE /users/{userId} called")
        deleted = await service.delete_user(userId)

        if not deleted:
            logger.warning(f"User not found for deletion: {userId}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "User not found",
                    "message": f"User with ID {userId} does not exist",
                },
            )

        logger.info(f"User deleted successfully: {userId}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {userId}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        ) from e
