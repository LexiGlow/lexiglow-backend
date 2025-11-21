"""
User service with business logic.

This module implements the application service layer for User operations,
handling business logic, validation, and password hashing.
"""

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

import bcrypt

from app.application.dto.user_dto import (
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.domain.entities.user import User as UserEntity
from app.domain.interfaces.user_repository import IUserRepository

logger = logging.getLogger(__name__)


class UserService:
    """
    User service for handling business logic.

    This service encapsulates user-related business operations including
    password hashing, validation, and coordination between the repository
    and presentation layers.
    """

    def __init__(self, repository: IUserRepository):
        """
        Initialize the User service.

        Args:
            repository: A user repository that conforms to the
                IUserRepository interface.
        """
        self.repository = repository
        logger.info("UserService initialized")

    def _hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    def _entity_to_response(self, entity: UserEntity) -> UserResponse:
        """
        Convert domain entity to response schema.

        Args:
            entity: User domain entity

        Returns:
            UserResponse schema (excludes password hash)

        Raises:
            ValueError: If entity ID is None (should not happen for persisted entities)
        """
        if entity.id is None:
            raise ValueError("Cannot create UserResponse from entity without ID")

        return UserResponse(
            id=entity.id,
            email=entity.email,
            username=entity.username,
            firstName=entity.first_name,
            lastName=entity.last_name,
            nativeLanguageId=entity.native_language_id,
            currentLanguageId=entity.current_language_id,
            createdAt=entity.created_at,
            updatedAt=entity.updated_at,
            lastActiveAt=entity.last_active_at,
        )

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Create a new user with validation and password hashing.

        Args:
            user_data: User creation data

        Returns:
            Created user response

        Raises:
            ValueError: If email or username already exists
            Exception: If creation fails
        """
        logger.info(f"Creating user with email: {user_data.email}")

        # Validate email uniqueness
        if self.repository.email_exists(user_data.email):
            logger.warning(f"Email already exists: {user_data.email}")
            raise ValueError(f"Email {user_data.email} is already registered")

        # Validate username uniqueness
        if self.repository.username_exists(user_data.username):
            logger.warning(f"Username already exists: {user_data.username}")
            raise ValueError(f"Username {user_data.username} is already taken")

        # Hash password
        password_hash = self._hash_password(user_data.password)

        # Create entity
        user_entity = UserEntity(
            id=uuid4(),
            email=user_data.email,
            username=user_data.username,
            passwordHash=password_hash,
            firstName=user_data.first_name,
            lastName=user_data.last_name,
            nativeLanguageId=user_data.native_language_id,
            currentLanguageId=user_data.current_language_id,
            createdAt=datetime.now(UTC),
            updatedAt=datetime.now(UTC),
            lastActiveAt=None,
        )

        # Save to repository
        created_entity = self.repository.create(user_entity)
        logger.info(f"User created successfully: {created_entity.id}")

        return self._entity_to_response(created_entity)

    async def get_user(self, user_id: UUID) -> UserResponse | None:
        """
        Retrieve a user by ID.

        Args:
            user_id: User UUID

        Returns:
            User response if found, None otherwise

        Raises:
            Exception: If retrieval fails
        """
        logger.debug(f"Retrieving user: {user_id}")

        entity = self.repository.get_by_id(user_id)
        if entity is None:
            logger.debug(f"User not found: {user_id}")
            return None

        return self._entity_to_response(entity)

    async def get_all_users(
        self, skip: int = 0, limit: int = 100
    ) -> list[UserResponse]:
        """
        Retrieve all users with pagination.

        Args:
            skip: Number of users to skip (for pagination)
            limit: Maximum number of users to return

        Returns:
            List of user responses

        Raises:
            Exception: If retrieval fails
        """
        logger.debug(f"Retrieving all users (skip={skip}, limit={limit})")

        entities = self.repository.get_all(skip=skip, limit=limit)
        return [self._entity_to_response(entity) for entity in entities]

    async def update_user(
        self, user_id: UUID, user_data: UserUpdate
    ) -> UserResponse | None:
        """
        Update a user with validation.

        Args:
            user_id: User UUID
            user_data: User update data

        Returns:
            Updated user response if found, None otherwise

        Raises:
            ValueError: If email or username conflict with existing users
            Exception: If update fails
        """
        logger.info(f"Updating user: {user_id}")

        # Check if user exists
        existing_entity = self.repository.get_by_id(user_id)
        if existing_entity is None:
            logger.warning(f"User not found for update: {user_id}")
            return None

        # Validate email uniqueness if changed
        if user_data.email is not None and user_data.email != existing_entity.email:
            if self.repository.email_exists(user_data.email):
                logger.warning(f"Email already exists: {user_data.email}")
                raise ValueError(f"Email {user_data.email} is already registered")

        # Validate username uniqueness if changed
        if (
            user_data.username is not None
            and user_data.username != existing_entity.username
        ):
            if self.repository.username_exists(user_data.username):
                logger.warning(f"Username already exists: {user_data.username}")
                raise ValueError(f"Username {user_data.username} is already taken")

        # Build updated entity with only changed fields
        updated_entity = UserEntity(
            id=existing_entity.id,
            email=(
                user_data.email
                if user_data.email is not None
                else existing_entity.email
            ),
            username=(
                user_data.username
                if user_data.username is not None
                else existing_entity.username
            ),
            # Don't allow password updates via this method
            passwordHash=existing_entity.password_hash,
            firstName=(
                user_data.first_name
                if user_data.first_name is not None
                else existing_entity.first_name
            ),
            lastName=user_data.last_name or existing_entity.last_name,
            nativeLanguageId=(
                user_data.native_language_id or existing_entity.native_language_id
            ),
            currentLanguageId=(
                user_data.current_language_id
                if user_data.current_language_id is not None
                else existing_entity.current_language_id
            ),
            createdAt=existing_entity.created_at,
            updatedAt=datetime.now(UTC),
            lastActiveAt=existing_entity.last_active_at,
        )

        # Update in repository
        updated = self.repository.update(user_id, updated_entity)

        if updated is None:
            logger.error(f"Failed to update user: {user_id}")
            return None

        logger.info(f"User updated successfully: {user_id}")
        return self._entity_to_response(updated)

    async def delete_user(self, user_id: UUID) -> bool:
        """
        Delete a user by ID.

        Args:
            user_id: User UUID

        Returns:
            True if deleted, False if not found

        Raises:
            Exception: If deletion fails
        """
        logger.info(f"Deleting user: {user_id}")

        deleted = self.repository.delete(user_id)
        if deleted:
            logger.info(f"User deleted successfully: {user_id}")
        else:
            logger.warning(f"User not found for deletion: {user_id}")

        return deleted
