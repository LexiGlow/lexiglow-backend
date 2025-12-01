"""
Text repository interface.

This module defines the repository interface for Text entity operations,
extending the base repository with text-specific methods.
"""

from abc import abstractmethod

from app.core.types import ULIDStr
from app.domain.entities.enums import ProficiencyLevel
from app.domain.entities.text import Text
from app.domain.interfaces.base_repository import IRepository


class ITextRepository(IRepository[Text]):
    """
    Repository interface for Text entity.

    Extends the base repository with text-specific query methods.
    """

    @abstractmethod
    async def get_by_language(
        self, language_id: ULIDStr, skip: int = 0, limit: int = 100
    ) -> list[Text]:
        """
        Retrieve texts by language.

        Args:
            language_id: The ULID of the language
            skip: Number of texts to skip (for pagination)
            limit: Maximum number of texts to return

        Returns:
            List of texts in the specified language

        Raises:
            RepositoryError: If the retrieval fails
        """
        pass

    @abstractmethod
    async def get_by_user(
        self, user_id: ULIDStr, skip: int = 0, limit: int = 100
    ) -> list[Text]:
        """
        Retrieve texts by user.

        Args:
            user_id: The ULID of the user
            skip: Number of texts to skip (for pagination)
            limit: Maximum number of texts to return

        Returns:
            List of texts by the specified user

        Raises:
            RepositoryError: If the retrieval fails
        """
        pass

    @abstractmethod
    async def get_by_proficiency_level(
        self, proficiency_level: ProficiencyLevel, skip: int = 0, limit: int = 100
    ) -> list[Text]:
        """
        Retrieve texts by proficiency level.

        Args:
            proficiency_level: The CEFR proficiency level
            skip: Number of texts to skip (for pagination)
            limit: Maximum number of texts to return

        Returns:
            List of texts for the specified proficiency level

        Raises:
            RepositoryError: If the retrieval fails
        """
        pass

    @abstractmethod
    async def get_public_texts(self, skip: int = 0, limit: int = 100) -> list[Text]:
        """
        Retrieve all public texts.

        Args:
            skip: Number of texts to skip (for pagination)
            limit: Maximum number of texts to return

        Returns:
            List of public texts

        Raises:
            RepositoryError: If the retrieval fails
        """
        pass

    @abstractmethod
    async def search_by_title(
        self, title_query: str, skip: int = 0, limit: int = 100
    ) -> list[Text]:
        """
        Search texts by title.

        Args:
            title_query: The search query for title
            skip: Number of texts to skip (for pagination)
            limit: Maximum number of texts to return

        Returns:
            List of texts matching the search query

        Raises:
            RepositoryError: If the search fails
        """
        pass

    @abstractmethod
    async def get_by_tags(
        self, tag_ids: list[ULIDStr], skip: int = 0, limit: int = 100
    ) -> list[Text]:
        """
        Retrieve texts by tags.

        Args:
            tag_ids: List of tag ULIDs to filter by
            skip: Number of texts to skip (for pagination)
            limit: Maximum number of texts to return

        Returns:
            List of texts with the specified tags

        Raises:
            RepositoryError: If the retrieval fails
        """
        pass
