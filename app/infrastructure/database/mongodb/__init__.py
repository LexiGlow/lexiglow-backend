"""
MongoDB database infrastructure module.

This module provides MongoDB repository factory and implementations.
"""

import logging
from typing import Any, cast

from app.domain.interfaces.language_repository import ILanguageRepository
from app.domain.interfaces.repository_factory import IRepositoryFactory
from app.domain.interfaces.text_repository import ITextRepository
from app.domain.interfaces.user_repository import IUserRepository

logger = logging.getLogger(__name__)


class MongoDBRepositoryFactory(IRepositoryFactory):
    """
    Factory for creating MongoDB repository implementations.

    This factory maps repository interfaces to their MongoDB implementations
    and provides a generic get_repository method. Uses singleton pattern to ensure
    only one factory instance exists per configuration.

    This factory also caches repository instances to ensure singleton behavior
    for repositories.
    """

    _instance: "MongoDBRepositoryFactory | None" = None
    _initialized: bool = False

    def __new__(cls, db_url: str, db_name: str) -> "MongoDBRepositoryFactory":
        """
        Create or return existing singleton instance.

        Args:
            db_url: MongoDB connection URL
            db_name: MongoDB database name

        Returns:
            Singleton instance of MongoDBRepositoryFactory
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_url: str, db_name: str):
        """
        Initialize the MongoDB factory.

        Args:
            db_url: MongoDB connection URL
            db_name: MongoDB database name
        """
        # Only initialize once (singleton pattern)
        if self.__class__._initialized:
            return

        # Lazy imports - only load MongoDB classes when this factory is used
        from .repositories.language_repository_impl import MongoDBLanguageRepository
        from .repositories.text_repository_impl import MongoDBTextRepository
        from .repositories.user_repository_impl import MongoDBUserRepository

        self.db_url = db_url
        self.db_name = db_name
        # Map interface types to their MongoDB implementations
        self._repository_classes: dict[type, type] = {
            IUserRepository: MongoDBUserRepository,
            ILanguageRepository: MongoDBLanguageRepository,
            ITextRepository: MongoDBTextRepository,
        }
        # Cache for repository instances (singleton pattern)
        self._repository_cache: dict[type, Any] = {}
        self.__class__._initialized = True

    def get_repository[T](self, repository_type: type[T]) -> T:
        """
        Get a repository instance for the given interface type (singleton).

        Returns cached instance if available, otherwise creates a new one.

        Args:
            repository_type: The repository interface type
                           (e.g., IUserRepository, ILanguageRepository)

        Returns:
            Repository instance implementing the interface

        Raises:
            ValueError: If repository type is not supported
        """
        # Return cached instance if available
        if repository_type in self._repository_cache:
            logger.debug(f"Returning cached {repository_type.__name__} instance")
            return cast(T, self._repository_cache[repository_type])

        # Create new instance and cache it
        repository = self._create_repository(repository_type)
        self._repository_cache[repository_type] = repository
        return repository

    def _create_repository[T](self, repository_type: type[T]) -> T:
        """
        Create a new repository instance for the given interface type.

        Args:
            repository_type: The repository interface type
                           (e.g., IUserRepository, ILanguageRepository)

        Returns:
            Repository instance implementing the interface

        Raises:
            ValueError: If repository type is not supported
        """
        if repository_type not in self._repository_classes:
            raise ValueError(
                f"MongoDB repository for {repository_type.__name__} is not supported. "
                f"Available types: {list(self._repository_classes.keys())}"
            )

        repository_class = self._repository_classes[repository_type]
        logger.debug(
            f"Creating {repository_class.__name__} instance with "
            f"db_url={self.db_url}, db_name={self.db_name}"
        )
        return cast(T, repository_class(db_url=self.db_url, db_name=self.db_name))


__all__ = ["MongoDBRepositoryFactory"]
