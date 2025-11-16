"""
SQLite implementation of User repository.

This module provides a concrete implementation of IUserRepository
using SQLAlchemy ORM and raw SQL queries.
"""

import logging
import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.core.config import BASE_DIR
from app.domain.entities.user import User as UserEntity
from app.domain.interfaces.user_repository import IUserRepository
from app.infrastructure.database.sqlite.models import User as UserModel

logger = logging.getLogger(__name__)


class SQLiteUserRepository(IUserRepository):
    """
    SQLite implementation of User repository.

    This implementation uses SQLAlchemy ORM for type-safe database operations
    and provides all methods defined in IUserRepository interface.
    """

    def __init__(self, db_path: str | None = None):
        """
        Initialize the SQLite User repository.

        Args:
            db_path: Optional path to SQLite database file.
                     If None, uses SQLITE_DB_PATH from environment.
        """
        import os

        if db_path is None:
            db_path = str(BASE_DIR / os.getenv("SQLITE_DB_PATH", "data/lexiglow.db"))

        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info(f"SQLiteUserRepository initialized with database: {db_path}")

    def _model_to_entity(self, model: UserModel) -> UserEntity:
        """
        Convert ORM model to domain entity.

        Args:
            model: SQLAlchemy User model

        Returns:
            Pydantic User entity
        """
        return UserEntity(
            id=UUID(str(model.id)),
            email=str(model.email),
            username=str(model.username),
            passwordHash=str(model.passwordHash),
            firstName=str(model.firstName),
            lastName=str(model.lastName),
            nativeLanguageId=UUID(str(model.nativeLanguageId)),
            currentLanguageId=UUID(str(model.currentLanguageId)),
            createdAt=model.createdAt,
            updatedAt=model.updatedAt,
            lastActiveAt=model.lastActiveAt,
        )

    def _entity_to_model(self, entity: UserEntity) -> UserModel:
        """
        Convert domain entity to ORM model.

        Args:
            entity: Pydantic User entity

        Returns:
            SQLAlchemy User model
        """
        return UserModel(
            id=str(entity.id),
            email=entity.email,
            username=entity.username,
            passwordHash=entity.password_hash,
            firstName=entity.first_name,
            lastName=entity.last_name,
            nativeLanguageId=str(entity.native_language_id),
            currentLanguageId=str(entity.current_language_id),
            createdAt=entity.created_at,
            updatedAt=entity.updated_at,
            lastActiveAt=entity.last_active_at,
        )

    def create(self, entity: UserEntity) -> UserEntity:
        """
        Create a new user in the repository.

        Args:
            entity: User entity to create

        Returns:
            Created user entity with generated ID if not provided

        Raises:
            RepositoryError: If creation fails
        """
        user_model: UserModel
        try:
            with self.SessionLocal() as session:
                # Generate ID if not provided
                if entity.id is None:
                    entity.id = UUID(str(uuid.uuid4()))

                # Convert entity to model
                user_model = self._entity_to_model(entity)

                # Add and commit
                session.add(user_model)
                session.commit()
                session.refresh(user_model)

                logger.info(
                    f"Created user: {user_model.username} (ID: {user_model.id})"
                )
            return self._model_to_entity(user_model)

        except SQLAlchemyError as e:
            logger.error(f"Failed to create user: {e}")
            raise Exception(f"Failed to create user: {e}") from e

    def get_by_id(self, entity_id: UUID) -> UserEntity | None:
        """
        Retrieve a user by their ID.

        Args:
            entity_id: UUID of the user

        Returns:
            User entity if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            with self.SessionLocal() as session:
                user_model = (
                    session.query(UserModel).filter_by(id=str(entity_id)).first()
                )

                if user_model:
                    logger.debug(f"Retrieved user by ID: {entity_id}")
                    return self._model_to_entity(user_model)

                logger.debug(f"User not found with ID: {entity_id}")
                return None

        except SQLAlchemyError as e:
            logger.error(f"Failed to get user by ID: {e}")
            raise Exception(f"Failed to get user by ID: {e}") from e

    def get_all(self, skip: int = 0, limit: int = 100) -> list[UserEntity]:
        """
        Retrieve all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user entities

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            with self.SessionLocal() as session:
                users = session.query(UserModel).offset(skip).limit(limit).all()

                logger.debug(
                    f"Retrieved {len(users)} users (skip={skip}, limit={limit})"
                )
                return [self._model_to_entity(user) for user in users]

        except SQLAlchemyError as e:
            logger.error(f"Failed to get all users: {e}")
            raise Exception(f"Failed to get all users: {e}") from e

    def update(self, entity_id: UUID, entity: UserEntity) -> UserEntity | None:
        """
        Update an existing user.

        Args:
            entity_id: UUID of the user to update
            entity: Updated user entity

        Returns:
            Updated user entity if found, None otherwise

        Raises:
            RepositoryError: If update fails
        """
        try:
            with self.SessionLocal() as session:
                user_model = (
                    session.query(UserModel).filter_by(id=str(entity_id)).first()
                )

                if not user_model:
                    logger.warning(f"User not found for update: {entity_id}")
                    return None

                # Update fields
                user_model.email = entity.email
                user_model.username = entity.username
                user_model.passwordHash = entity.password_hash
                user_model.firstName = entity.first_name
                user_model.lastName = entity.last_name
                user_model.nativeLanguageId = str(entity.native_language_id)
                user_model.currentLanguageId = str(entity.current_language_id)
                user_model.updatedAt = datetime.now(UTC)

                if entity.last_active_at:
                    user_model.lastActiveAt = entity.last_active_at

                session.commit()
                session.refresh(user_model)

                logger.info(f"Updated user: {user_model.username} (ID: {entity_id})")
                return self._model_to_entity(user_model)

        except SQLAlchemyError as e:
            logger.error(f"Failed to update user: {e}")
            raise Exception(f"Failed to update user: {e}") from e

    def delete(self, entity_id: UUID) -> bool:
        """
        Delete a user by their ID.

        Args:
            entity_id: UUID of the user to delete

        Returns:
            True if deleted successfully, False if not found

        Raises:
            RepositoryError: If deletion fails
        """
        try:
            with self.SessionLocal() as session:
                user_model = (
                    session.query(UserModel).filter_by(id=str(entity_id)).first()
                )

                if not user_model:
                    logger.warning(f"User not found for deletion: {entity_id}")
                    return False

                session.delete(user_model)
                session.commit()

                logger.info(f"Deleted user: {user_model.username} (ID: {entity_id})")
                return True

        except SQLAlchemyError as e:
            logger.error(f"Failed to delete user: {e}")
            raise Exception(f"Failed to delete user: {e}") from e

    def exists(self, entity_id: UUID) -> bool:
        """
        Check if a user exists by their ID.

        Args:
            entity_id: UUID of the user

        Returns:
            True if user exists, False otherwise

        Raises:
            RepositoryError: If check fails
        """
        try:
            with self.SessionLocal() as session:
                exists = (
                    session.query(UserModel.id).filter_by(id=str(entity_id)).first()
                    is not None
                )

                logger.debug(f"User exists check for {entity_id}: {exists}")
                return exists

        except SQLAlchemyError as e:
            logger.error(f"Failed to check user existence: {e}")
            raise Exception(f"Failed to check user existence: {e}") from e

    def get_by_email(self, email: str) -> UserEntity | None:
        """
        Retrieve a user by their email address.

        Args:
            email: The email address to search for

        Returns:
            The user if found, None otherwise

        Raises:
            RepositoryError: If the retrieval fails
        """
        try:
            with self.SessionLocal() as session:
                user_model = session.query(UserModel).filter_by(email=email).first()

                if user_model:
                    logger.debug(f"Retrieved user by email: {email}")
                    return self._model_to_entity(user_model)

                logger.debug(f"User not found with email: {email}")
                return None

        except SQLAlchemyError as e:
            logger.error(f"Failed to get user by email: {e}")
            raise Exception(f"Failed to get user by email: {e}") from e

    def get_by_username(self, username: str) -> UserEntity | None:
        """
        Retrieve a user by their username.

        Args:
            username: The username to search for

        Returns:
            The user if found, None otherwise

        Raises:
            RepositoryError: If the retrieval fails
        """
        try:
            with self.SessionLocal() as session:
                user_model = (
                    session.query(UserModel).filter_by(username=username).first()
                )

                if user_model:
                    logger.debug(f"Retrieved user by username: {username}")
                    return self._model_to_entity(user_model)

                logger.debug(f"User not found with username: {username}")
                return None

        except SQLAlchemyError as e:
            logger.error(f"Failed to get user by username: {e}")
            raise Exception(f"Failed to get user by username: {e}") from e

    def email_exists(self, email: str) -> bool:
        """
        Check if an email is already registered.

        Args:
            email: The email address to check

        Returns:
            True if the email exists, False otherwise

        Raises:
            RepositoryError: If the check fails
        """
        try:
            with self.SessionLocal() as session:
                exists = (
                    session.query(UserModel.id).filter_by(email=email).first()
                    is not None
                )

                logger.debug(f"Email exists check for {email}: {exists}")
                return exists

        except SQLAlchemyError as e:
            logger.error(f"Failed to check email existence: {e}")
            raise Exception(f"Failed to check email existence: {e}") from e

    def username_exists(self, username: str) -> bool:
        """
        Check if a username is already taken.

        Args:
            username: The username to check

        Returns:
            True if the username exists, False otherwise

        Raises:
            RepositoryError: If the check fails
        """
        try:
            with self.SessionLocal() as session:
                exists = (
                    session.query(UserModel.id).filter_by(username=username).first()
                    is not None
                )

                logger.debug(f"Username exists check for {username}: {exists}")
                return exists

        except SQLAlchemyError as e:
            logger.error(f"Failed to check username existence: {e}")
            raise Exception(f"Failed to check username existence: {e}") from e

    def update_last_active(self, user_id: UUID) -> bool:
        """
        Update the last active timestamp for a user.

        Args:
            user_id: The UUID of the user

        Returns:
            True if updated successfully, False otherwise

        Raises:
            RepositoryError: If the update fails
        """
        try:
            with self.SessionLocal() as session:
                user_model = session.query(UserModel).filter_by(id=str(user_id)).first()

                if not user_model:
                    logger.warning(f"User not found for last active update: {user_id}")
                    return False

                user_model.lastActiveAt = datetime.now(UTC)
                session.commit()

                logger.debug(f"Updated last active for user: {user_id}")
                return True

        except SQLAlchemyError as e:
            logger.error(f"Failed to update last active: {e}")
            raise Exception(f"Failed to update last active: {e}") from e
