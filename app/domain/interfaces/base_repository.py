"""
Base repository interface using the Repository pattern.

This module defines the abstract base repository interface using Python generics
to provide type-safe repository operations for domain entities.
"""

from abc import ABC, abstractmethod
from uuid import UUID


class IRepository[T](ABC):
    """
    Abstract base repository interface using generics.

    This interface defines the contract for all repository implementations,
    providing CRUD operations for domain entities.

    Type Parameters:
        T: The type of entity this repository manages
    """

    @abstractmethod
    def create(self, entity: T) -> T:
        """
        Create a new entity in the repository.

        Args:
            entity: The entity to create

        Returns:
            The created entity with populated fields (e.g., generated ID)

        Raises:
            RepositoryError: If the creation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, entity_id: UUID) -> T | None:
        """
        Retrieve an entity by its ID.

        Args:
            entity_id: The UUID of the entity to retrieve

        Returns:
            The entity if found, None otherwise

        Raises:
            RepositoryError: If the retrieval fails
        """
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """
        Retrieve all entities with pagination.

        Args:
            skip: Number of entities to skip (for pagination)
            limit: Maximum number of entities to return

        Returns:
            List of entities

        Raises:
            RepositoryError: If the retrieval fails
        """
        pass

    @abstractmethod
    def update(self, entity_id: UUID, entity: T) -> T | None:
        """
        Update an existing entity.

        Args:
            entity_id: The UUID of the entity to update
            entity: The entity with updated values

        Returns:
            The updated entity if found, None otherwise

        Raises:
            RepositoryError: If the update fails
        """
        pass

    @abstractmethod
    def delete(self, entity_id: UUID) -> bool:
        """
        Delete an entity by its ID.

        Args:
            entity_id: The UUID of the entity to delete

        Returns:
            True if the entity was deleted, False if not found

        Raises:
            RepositoryError: If the deletion fails
        """
        pass

    @abstractmethod
    def exists(self, entity_id: UUID) -> bool:
        """
        Check if an entity exists by its ID.

        Args:
            entity_id: The UUID of the entity to check

        Returns:
            True if the entity exists, False otherwise

        Raises:
            RepositoryError: If the check fails
        """
        pass
