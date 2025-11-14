"""
User repository interface.

This module defines the repository interface for User entity operations,
extending the base repository with user-specific methods.
"""

from abc import abstractmethod
from uuid import UUID

from app.domain.entities.user import User
from app.domain.interfaces.base_repository import IRepository


class IUserRepository(IRepository[User]):
    """
    Repository interface for User entity.

    Extends the base repository with user-specific query methods.
    """

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.

        Args:
            email: The email address to search for

        Returns:
            The user if found, None otherwise

        Raises:
            RepositoryError: If the retrieval fails
        """
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.

        Args:
            username: The username to search for

        Returns:
            The user if found, None otherwise

        Raises:
            RepositoryError: If the retrieval fails
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass
