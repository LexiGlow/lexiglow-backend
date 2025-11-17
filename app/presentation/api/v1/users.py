"""
User API endpoints.

This module provides REST API handlers for user CRUD operations.
Handlers are called by Connexion based on operationId in openapi.yaml.
"""

import logging
from typing import Any
from uuid import UUID

from pydantic import ValidationError

from app.application.dto.user_dto import UserCreate, UserUpdate
from app.core.dependencies import get_container

logger = logging.getLogger(__name__)


def get_users(
    skip: int = 0, limit: int = 100
) -> tuple[list[dict[str, Any]] | dict[str, Any], int]:
    """
    Get all users with pagination.

    Args:
        skip: Number of users to skip (for pagination)
        limit: Maximum number of users to return

    Returns:
        Tuple of (list of user dictionaries for success, or error dict
        for errors, HTTP status code)
    """
    try:
        logger.info(f"GET /users called with skip={skip}, limit={limit}")
        container = get_container()
        service = container.get_user_service()
        users = service.get_all_users(skip=skip, limit=limit)

        # Convert Pydantic models to dicts for JSON response
        users_data = [user.model_dump(by_alias=True) for user in users]

        logger.info(f"Retrieved {len(users_data)} users")
        return users_data, 200

    except Exception as e:
        logger.error(f"Error retrieving users: {e}", exc_info=True)
        return {"error": "Internal server error", "message": str(e)}, 500


def get_user_by_id(userId: str) -> tuple[dict[str, Any], int]:
    """
    Get a user by ID.

    Args:
        userId: User UUID as string

    Returns:
        Tuple of (user dictionary or error, HTTP status code)
    """
    try:
        logger.info(f"GET /users/{userId} called")

        # Parse UUID
        try:
            user_uuid = UUID(userId)
        except ValueError:
            logger.warning(f"Invalid UUID format: {userId}")
            return {
                "error": "Invalid user ID format",
                "message": "User ID must be a valid UUID",
            }, 400

        container = get_container()
        service = container.get_user_service()
        user = service.get_user(user_uuid)

        if user is None:
            logger.warning(f"User not found: {userId}")
            return {
                "error": "User not found",
                "message": f"User with ID {userId} does not exist",
            }, 404

        logger.info(f"Retrieved user: {userId}")
        return user.model_dump(by_alias=True), 200

    except Exception as e:
        logger.error(f"Error retrieving user {userId}: {e}", exc_info=True)
        return {"error": "Internal server error", "message": str(e)}, 500


def create_user(body: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """
    Create a new user.

    Args:
        body: User creation data from request body

    Returns:
        Tuple of (created user dictionary or error, HTTP status code)
    """
    try:
        logger.info(f"POST /users called with email: {body.get('email')}")

        # Validate and parse request body
        try:
            user_data = UserCreate(**body)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return {"error": "Invalid input data", "message": str(e)}, 400

        # Create user via service
        container = get_container()
        service = container.get_user_service()
        try:
            created_user = service.create_user(user_data)
            logger.info(f"User created successfully: {created_user.id}")
            return created_user.model_dump(by_alias=True), 201

        except ValueError as e:
            # Email or username already exists
            logger.warning(f"Conflict error: {e}")
            return {"error": "Conflict", "message": str(e)}, 409

    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        return {"error": "Internal server error", "message": str(e)}, 500


def update_user(userId: str, body: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """
    Update a user.

    Args:
        userId: User UUID as string
        body: User update data from request body

    Returns:
        Tuple of (updated user dictionary or error, HTTP status code)
    """
    try:
        logger.info(f"PUT /users/{userId} called")

        # Parse UUID
        try:
            user_uuid = UUID(userId)
        except ValueError:
            logger.warning(f"Invalid UUID format: {userId}")
            return {
                "error": "Invalid user ID format",
                "message": "User ID must be a valid UUID",
            }, 400

        # Validate and parse request body
        try:
            user_data = UserUpdate(**body)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return {"error": "Invalid input data", "message": str(e)}, 400

        # Update user via service
        container = get_container()
        service = container.get_user_service()
        try:
            updated_user = service.update_user(user_uuid, user_data)

            if updated_user is None:
                logger.warning(f"User not found: {userId}")
                return {
                    "error": "User not found",
                    "message": f"User with ID {userId} does not exist",
                }, 404

            logger.info(f"User updated successfully: {userId}")
            return updated_user.model_dump(by_alias=True), 200

        except ValueError as e:
            # Email or username conflict
            logger.warning(f"Conflict error: {e}")
            return {"error": "Conflict", "message": str(e)}, 409

    except Exception as e:
        logger.error(f"Error updating user {userId}: {e}", exc_info=True)
        return {"error": "Internal server error", "message": str(e)}, 500


def delete_user(userId: str) -> tuple[dict[str, Any], int]:
    """
    Delete a user.

    Args:
        userId: User UUID as string

    Returns:
        Tuple of (empty dict or error, HTTP status code)
    """
    try:
        logger.info(f"DELETE /users/{userId} called")

        # Parse UUID
        try:
            user_uuid = UUID(userId)
        except ValueError:
            logger.warning(f"Invalid UUID format: {userId}")
            return {
                "error": "Invalid user ID format",
                "message": "User ID must be a valid UUID",
            }, 400

        container = get_container()
        service = container.get_user_service()
        deleted = service.delete_user(user_uuid)

        if not deleted:
            logger.warning(f"User not found for deletion: {userId}")
            return {
                "error": "User not found",
                "message": f"User with ID {userId} does not exist",
            }, 404

        logger.info(f"User deleted successfully: {userId}")
        return {}, 204

    except Exception as e:
        logger.error(f"Error deleting user {userId}: {e}", exc_info=True)
        return {"error": "Internal server error", "message": str(e)}, 500
