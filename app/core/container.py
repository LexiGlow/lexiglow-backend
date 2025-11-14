"""
Dependency Injection Container for LexiGlow Backend.

This module provides a lightweight dependency injection container that manages
the lifecycle of repositories and services, enabling centralized dependency
configuration and easy testing with mock dependencies.
"""

import logging
from typing import Any

from app.application.services.user_service import UserService
from app.domain.interfaces.language_repository import ILanguageRepository
from app.domain.interfaces.text_repository import ITextRepository
from app.domain.interfaces.user_repository import IUserRepository

logger = logging.getLogger(__name__)


class Container:
    """
    Dependency injection container for managing application dependencies.

    This container implements the singleton pattern for repositories and services,
    ensuring single instances are reused across the application. It supports
    dependency overrides for testing purposes.

    Attributes:
        _repositories: Cache of instantiated repository instances
        _services: Cache of instantiated service instances
        _overrides: Map of interface types to override implementations
    """

    def __init__(self):
        """Initialize the DI container with empty caches."""
        self._repositories: dict[str, Any] = {}
        self._services: dict[str, Any] = {}
        self._overrides: dict[type, Any] = {}
        logger.info("DI Container initialized")

    def register_override(self, interface: type, implementation: Any) -> None:
        """
        Register an override for dependency injection (primarily for testing).

        Args:
            interface: The interface or class type to override
            implementation: The override implementation (instance or class)
        """
        self._overrides[interface] = implementation
        logger.debug(f"Registered override for {interface.__name__}")

    def clear_overrides(self) -> None:
        """Clear all registered overrides."""
        self._overrides.clear()
        logger.debug("Cleared all dependency overrides")

    def reset(self) -> None:
        """
        Reset the container by clearing all caches and overrides.

        This is useful for testing to ensure a clean state between tests.
        """
        self._repositories.clear()
        self._services.clear()
        self._overrides.clear()
        logger.debug("Container reset: cleared all caches and overrides")

    def get_user_repository(self) -> IUserRepository:
        """
        Get the UserRepository instance (singleton).

        Returns:
            IUserRepository implementation instance

        Raises:
            Exception: If repository instantiation fails
        """
        # Check for override first
        if IUserRepository in self._overrides:
            override = self._overrides[IUserRepository]
            # If override is a class, instantiate it; if it's an instance, return it
            if isinstance(override, type):
                return override()
            return override

        # Return cached instance if available
        if "user_repository" in self._repositories:
            return self._repositories["user_repository"]

        # Create new instance (lazy initialization)
        try:
            from app.core.config import ACTIVE_DATABASE_TYPE, MONGO_URI

            if ACTIVE_DATABASE_TYPE == "sqlite":
                from app.infrastructure.database.repositories import (
                    SQLiteUserRepository,
                )

                logger.debug("Creating SQLiteUserRepository instance")
                repository = SQLiteUserRepository()
            elif ACTIVE_DATABASE_TYPE == "mongodb":
                from app.infrastructure.database.repositories import (
                    MongoDBUserRepository,
                )

                logger.debug("Creating MongoDBUserRepository instance")
                repository = MongoDBUserRepository(db_url=MONGO_URI, db_name="lexiglow")
            else:
                raise ValueError(f"Unsupported database type: {ACTIVE_DATABASE_TYPE}")

            self._repositories["user_repository"] = repository
            logger.info("UserRepository initialized and cached")
            return repository

        except Exception as e:
            logger.error(f"Failed to create UserRepository: {e}", exc_info=True)
            raise

    def get_user_service(self) -> UserService:
        """
        Get the UserService instance (singleton).

        Returns:
            UserService instance with injected dependencies

        Raises:
            Exception: If service instantiation fails
        """
        # Check for override first
        if UserService in self._overrides:
            override = self._overrides[UserService]
            # If override is a class, instantiate it; if it's an instance, return it
            if isinstance(override, type):
                return override(repository=self.get_user_repository())
            return override

        # Return cached instance if available
        if "user_service" in self._services:
            return self._services["user_service"]

        # Create new instance with dependencies (lazy initialization)
        try:
            logger.debug("Creating UserService instance with dependencies")
            repository = self.get_user_repository()
            service = UserService(repository=repository)
            self._services["user_service"] = service
            logger.info("UserService initialized and cached")
            return service

        except Exception as e:
            logger.error(f"Failed to create UserService: {e}", exc_info=True)
            raise

    def get_language_repository(self) -> ILanguageRepository:
        """
        Get the LanguageRepository instance (singleton).

        Returns:
            ILanguageRepository implementation instance

        Raises:
            Exception: If repository instantiation fails
        """
        # Check for override first
        if ILanguageRepository in self._overrides:
            override = self._overrides[ILanguageRepository]
            # If override is a class, instantiate it; if it's an instance, return it
            if isinstance(override, type):
                return override()
            return override

        # Return cached instance if available
        if "language_repository" in self._repositories:
            return self._repositories["language_repository"]

        # Create new instance (lazy initialization)
        try:
            from app.core.config import ACTIVE_DATABASE_TYPE, MONGO_URI

            if ACTIVE_DATABASE_TYPE == "sqlite":
                from app.infrastructure.database.repositories import (
                    SQLiteLanguageRepository,
                )

                logger.debug("Creating SQLiteLanguageRepository instance")
                repository = SQLiteLanguageRepository()
            elif ACTIVE_DATABASE_TYPE == "mongodb":
                from app.infrastructure.database.repositories import (
                    MongoDBLanguageRepository,
                )

                logger.debug("Creating MongoDBLanguageRepository instance")
                repository = MongoDBLanguageRepository(
                    db_url=MONGO_URI, db_name="lexiglow"
                )
            else:
                raise ValueError(f"Unsupported database type: {ACTIVE_DATABASE_TYPE}")

            self._repositories["language_repository"] = repository
            logger.info("LanguageRepository initialized and cached")
            return repository

        except Exception as e:
            logger.error(f"Failed to create LanguageRepository: {e}", exc_info=True)
            raise

    def get_text_repository(self) -> ITextRepository:
        """
        Get the TextRepository instance (singleton).

        Returns:
            ITextRepository implementation instance

        Raises:
            Exception: If repository instantiation fails
        """
        # Check for override first
        if ITextRepository in self._overrides:
            override = self._overrides[ITextRepository]
            # If override is a class, instantiate it; if it's an instance, return it
            if isinstance(override, type):
                return override()
            return override

        # Return cached instance if available
        if "text_repository" in self._repositories:
            return self._repositories["text_repository"]

        # Create new instance (lazy initialization)
        try:
            from app.core.config import ACTIVE_DATABASE_TYPE, MONGO_URI

            if ACTIVE_DATABASE_TYPE == "sqlite":
                from app.infrastructure.database.repositories import (
                    SQLiteTextRepository,
                )

                logger.debug("Creating SQLiteTextRepository instance")
                repository = SQLiteTextRepository()
            elif ACTIVE_DATABASE_TYPE == "mongodb":
                from app.infrastructure.database.repositories import (
                    MongoDBTextRepository,
                )

                logger.debug("Creating MongoDBTextRepository instance")
                repository = MongoDBTextRepository(db_url=MONGO_URI, db_name="lexiglow")
            else:
                raise ValueError(f"Unsupported database type: {ACTIVE_DATABASE_TYPE}")

            self._repositories["text_repository"] = repository
            logger.info("TextRepository initialized and cached")
            return repository

        except Exception as e:
            logger.error(f"Failed to create TextRepository: {e}", exc_info=True)
            raise

    def __repr__(self) -> str:
        """Return string representation of the container state."""
        return (
            f"Container(repositories={list(self._repositories.keys())}, "
            f"services={list(self._services.keys())}, "
            f"overrides={len(self._overrides)})"
        )
