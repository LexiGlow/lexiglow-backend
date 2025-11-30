"""
SQLite database infrastructure module.

This module provides ORM models and SQLite repository factory
for the LexiGlow application.
"""

import logging
from typing import Any, cast

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.domain.interfaces.language_repository import ILanguageRepository
from app.domain.interfaces.repository_factory import IRepositoryFactory
from app.domain.interfaces.text_repository import ITextRepository
from app.domain.interfaces.user_repository import IUserRepository

from .models import (
    Base,
    Language,
    TextModel,
    TextTag,
    TextTagAssociation,
    User,
    UserLanguage,
    UserVocabulary,
    UserVocabularyItem,
    get_all_models,
    get_model_by_table_name,
)

logger = logging.getLogger(__name__)


class SQLiteRepositoryFactory(IRepositoryFactory):
    """
    Factory for creating SQLite repository implementations.

    This factory maps repository interfaces to their SQLite implementations
    and provides a generic get_repository method. Uses singleton pattern to ensure
    only one factory instance exists per configuration.

    This factory also caches repository instances to ensure singleton behavior
    for repositories. Uses a shared async engine for connection pooling.
    """

    _instance: "SQLiteRepositoryFactory | None" = None
    _initialized: bool = False
    _shared_async_engine: AsyncEngine | None = None

    def __new__(cls, db_path: str | None = None) -> "SQLiteRepositoryFactory":
        """
        Create or return existing singleton instance.

        Args:
            db_path: Optional path to SQLite database file.
                     If None, uses SQLITE_DB_PATH from environment.

        Returns:
            Singleton instance of SQLiteRepositoryFactory
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path: str | None = None):
        """
        Initialize the SQLite factory.

        Args:
            db_path: Optional path to SQLite database file.
                     If None, uses SQLITE_DB_PATH from environment.
        """
        # Only initialize once (singleton pattern)
        if self.__class__._initialized:
            return

        import os

        from app.core.config import BASE_DIR

        # Lazy imports - only load SQLite classes when this factory is used
        from .repositories.language_repository_impl import SQLiteLanguageRepository
        from .repositories.text_repository_impl import SQLiteTextRepository
        from .repositories.user_repository_impl import SQLiteUserRepository

        if db_path is None:
            db_path = str(BASE_DIR / os.getenv("SQLITE_DB_PATH", "data/lexiglow.db"))

        self.db_path = db_path

        # Create shared async engine if not already created
        if SQLiteRepositoryFactory._shared_async_engine is None:
            SQLiteRepositoryFactory._shared_async_engine = create_async_engine(
                f"sqlite+aiosqlite:///{db_path}",
                echo=False,
                pool_pre_ping=True,
            )
            logger.info(f"Created shared async engine for database: {db_path}")

        # Map interface types to their SQLite implementations
        self._repository_classes: dict[type, type] = {
            IUserRepository: SQLiteUserRepository,
            ILanguageRepository: SQLiteLanguageRepository,
            ITextRepository: SQLiteTextRepository,
        }
        # Cache for repository instances (singleton pattern)
        self._repository_cache: dict[type, Any] = {}
        self.__class__._initialized = True

    async def dispose(self) -> None:
        """
        Dispose the shared async engine.

        This should be called during application shutdown to properly
        close all database connections.

        Returns:
            None
        """
        if SQLiteRepositoryFactory._shared_async_engine is not None:
            await SQLiteRepositoryFactory._shared_async_engine.dispose()
            SQLiteRepositoryFactory._shared_async_engine = None
            logger.info("Disposed shared async engine")

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
                f"SQLite repository for {repository_type.__name__} is not supported. "
                f"Available types: {list(self._repository_classes.keys())}"
            )

        repository_class = self._repository_classes[repository_type]
        logger.debug(
            f"Creating {repository_class.__name__} instance with db_path={self.db_path}"
        )
        return cast(
            T,
            repository_class(
                db_path=self.db_path,
                engine=SQLiteRepositoryFactory._shared_async_engine,
            ),
        )


__all__ = [
    # Factory
    "SQLiteRepositoryFactory",
    # ORM Models
    "Base",
    "Language",
    "User",
    "UserLanguage",
    "TextModel",
    "TextTag",
    "TextTagAssociation",
    "UserVocabulary",
    "UserVocabularyItem",
    "get_all_models",
    "get_model_by_table_name",
]
