"""
Language repository interface.

This module defines the repository interface for Language entity operations,
extending the base repository with language-specific methods.
"""

from abc import abstractmethod

from app.domain.entities.language import Language
from app.domain.interfaces.base_repository import IRepository


class ILanguageRepository(IRepository[Language]):
    """
    Repository interface for Language entity.

    Extends the base repository with language-specific query methods.
    """

    @abstractmethod
    def get_by_code(self, code: str) -> Language | None:
        """
        Retrieve a language by its ISO 639-1 code.

        Args:
            code: The ISO 639-1 language code (e.g., 'en', 'es')

        Returns:
            The language if found, None otherwise

        Raises:
            RepositoryError: If the retrieval fails
        """
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Language | None:
        """
        Retrieve a language by its name.

        Args:
            name: The language name to search for

        Returns:
            The language if found, None otherwise

        Raises:
            RepositoryError: If the retrieval fails
        """
        pass

    @abstractmethod
    def code_exists(self, code: str) -> bool:
        """
        Check if a language code is already registered.

        Args:
            code: The ISO 639-1 language code to check

        Returns:
            True if the code exists, False otherwise

        Raises:
            RepositoryError: If the check fails
        """
        pass
