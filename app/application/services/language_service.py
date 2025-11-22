"""
Language service with business logic.

This module implements the application service layer for Language operations,
handling business logic and validation.
"""

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.dto.language_dto import (
    LanguageCreate,
    LanguageResponse,
    LanguageUpdate,
)
from app.domain.entities.language import Language as LanguageEntity
from app.domain.interfaces.language_repository import ILanguageRepository

logger = logging.getLogger(__name__)


class LanguageService:
    """
    Language service for handling business logic.

    This service encapsulates language-related business operations including
    validation and coordination between the repository and presentation layers.
    """

    def __init__(self, repository: ILanguageRepository):
        """
        Initialize the Language service.

        Args:
            repository: A language repository that conforms to the
                ILanguageRepository interface.
        """
        self.repository = repository
        logger.info("LanguageService initialized")

    def _entity_to_response(self, entity: LanguageEntity) -> LanguageResponse:
        """
        Convert domain entity to response schema.

        Args:
            entity: Language domain entity

        Returns:
            LanguageResponse schema

        Raises:
            ValueError: If entity ID is None (should not happen for persisted entities)
        """
        if entity.id is None:
            raise ValueError("Cannot create LanguageResponse from entity without ID")

        return LanguageResponse(
            id=entity.id,
            name=entity.name,
            code=entity.code,
            nativeName=entity.native_name,
            createdAt=entity.created_at,
        )

    async def create_language(self, language_data: LanguageCreate) -> LanguageResponse:
        """
        Create a new language with validation.

        Args:
            language_data: Language creation data

        Returns:
            Created language response

        Raises:
            ValueError: If language code already exists
            Exception: If creation fails
        """
        logger.info(f"Creating language with code: {language_data.code}")

        # Validate code uniqueness
        if await self.repository.code_exists(language_data.code):
            logger.warning(f"Language code already exists: {language_data.code}")
            raise ValueError(
                f"Language code {language_data.code} is already registered"
            )

        # Create entity
        language_entity = LanguageEntity(
            id=uuid4(),
            name=language_data.name,
            code=language_data.code,
            nativeName=language_data.native_name,
            createdAt=datetime.now(UTC),
        )

        # Save to repository
        created_entity = await self.repository.create(language_entity)
        logger.info(f"Language created successfully: {created_entity.id}")

        return self._entity_to_response(created_entity)

    async def get_language(self, language_id: UUID) -> LanguageResponse | None:
        """
        Retrieve a language by ID.

        Args:
            language_id: Language UUID

        Returns:
            Language response if found, None otherwise

        Raises:
            Exception: If retrieval fails
        """
        logger.debug(f"Retrieving language: {language_id}")

        entity = await self.repository.get_by_id(language_id)
        if entity is None:
            logger.debug(f"Language not found: {language_id}")
            return None

        return self._entity_to_response(entity)

    async def get_all_languages(
        self, skip: int = 0, limit: int = 100
    ) -> list[LanguageResponse]:
        """
        Retrieve all languages with pagination.

        Args:
            skip: Number of languages to skip (for pagination)
            limit: Maximum number of languages to return

        Returns:
            List of language responses

        Raises:
            Exception: If retrieval fails
        """
        logger.debug(f"Retrieving all languages (skip={skip}, limit={limit})")

        entities = await self.repository.get_all(skip=skip, limit=limit)
        return [self._entity_to_response(entity) for entity in entities]

    async def update_language(
        self, language_id: UUID, language_data: LanguageUpdate
    ) -> LanguageResponse | None:
        """
        Update a language with validation.

        Args:
            language_id: Language UUID
            language_data: Language update data

        Returns:
            Updated language response if found, None otherwise

        Raises:
            ValueError: If language code conflict with existing languages
            Exception: If update fails
        """
        logger.info(f"Updating language: {language_id}")

        # Check if language exists
        existing_entity = await self.repository.get_by_id(language_id)
        if existing_entity is None:
            logger.warning(f"Language not found for update: {language_id}")
            return None

        # Validate code uniqueness if changed
        if (
            language_data.code is not None
            and language_data.code != existing_entity.code
        ):
            if await self.repository.code_exists(language_data.code):
                logger.warning(f"Language code already exists: {language_data.code}")
                raise ValueError(
                    f"Language code {language_data.code} is already registered"
                )

        # Build updated entity with only changed fields
        updated_entity = LanguageEntity(
            id=existing_entity.id,
            name=(
                language_data.name
                if language_data.name is not None
                else existing_entity.name
            ),
            code=(
                language_data.code
                if language_data.code is not None
                else existing_entity.code
            ),
            nativeName=(
                language_data.native_name
                if language_data.native_name is not None
                else existing_entity.native_name
            ),
            createdAt=existing_entity.created_at,
        )

        # Update in repository
        updated = await self.repository.update(language_id, updated_entity)

        if updated is None:
            logger.error(f"Failed to update language: {language_id}")
            return None

        logger.info(f"Language updated successfully: {language_id}")
        return self._entity_to_response(updated)

    async def delete_language(self, language_id: UUID) -> bool:
        """
        Delete a language by ID.

        Args:
            language_id: Language UUID

        Returns:
            True if deleted, False if not found

        Raises:
            Exception: If deletion fails
        """
        logger.info(f"Deleting language: {language_id}")

        deleted = await self.repository.delete(language_id)
        if deleted:
            logger.info(f"Language deleted successfully: {language_id}")
        else:
            logger.warning(f"Language not found for deletion: {language_id}")

        return deleted
