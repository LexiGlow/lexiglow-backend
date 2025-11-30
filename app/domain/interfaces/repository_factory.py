"""
Repository factory interface.

This module defines the abstract interface for repository factories that create
database-specific repository implementations.
"""

from abc import ABC, abstractmethod


class IRepositoryFactory(ABC):
    """
    Abstract interface for repository factories.

    This interface defines the contract for factories that create repository
    instances. Implementations should provide database-specific factories
    (e.g., SQLite, MongoDB) that create repositories following the singleton pattern.
    """

    @abstractmethod
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
        pass

    @abstractmethod
    async def dispose(self) -> None:
        """
        Dispose of shared database resources.

        This should be called during application shutdown to properly
        close all database connections and free resources.

        Returns:
            None
        """
        pass
