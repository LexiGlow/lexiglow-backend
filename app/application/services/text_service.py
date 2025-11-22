"""
Text service with business logic.

This module implements the application service layer for Text operations.
"""

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.dto.text_dto import (
    TextCreate,
    TextResponse,
    TextUpdate,
)
from app.domain.entities.text import Text as TextEntity
from app.domain.interfaces.text_repository import ITextRepository

logger = logging.getLogger(__name__)


class TextService:
    """
    Text service for handling business logic.
    """

    def __init__(self, repository: ITextRepository):
        """
        Initialize the Text service.

        Args:
            repository: A text repository that conforms to the
                ITextRepository interface.
        """
        self.repository = repository
        logger.info("TextService initialized")

    def _entity_to_response(self, entity: TextEntity) -> TextResponse:
        """
        Convert domain entity to response schema.

        Args:
            entity: Text domain entity

        Returns:
            TextResponse schema

        Raises:
            ValueError: If entity ID is None (should not happen for persisted entities)
        """
        if entity.id is None:
            raise ValueError("Cannot create TextResponse from entity without ID")

        return TextResponse(
            id=entity.id,
            title=entity.title,
            content=entity.content,
            languageId=entity.language_id,  # Use aliased name
            userId=entity.user_id,  # Use aliased name
            proficiencyLevel=entity.proficiency_level,  # Use aliased name
            wordCount=entity.word_count,  # Use aliased name
            isPublic=entity.is_public,  # Use aliased name
            source=entity.source,
            createdAt=entity.created_at,  # Use aliased name
            updatedAt=entity.updated_at,  # Use aliased name
        )

    async def create_text(self, text_data: TextCreate) -> TextResponse:
        """
        Create a new text.

        Args:
            text_data: Text creation data

        Returns:
            Created text response

        Raises:
            Exception: If creation fails
        """
        logger.info(f"Creating text with title: {text_data.title}")

        # Construct TextEntity using camelCase aliases for fields that have them
        # model_dump(by_alias=True) provides camelCase keys where aliases are defined
        text_entity = TextEntity(
            id=uuid4(),
            createdAt=datetime.now(UTC),
            updatedAt=datetime.now(UTC),
            **text_data.model_dump(by_alias=True, exclude_unset=True),
        )

        created_entity = await self.repository.create(text_entity)
        logger.info(f"Text created successfully: {created_entity.id}")

        return self._entity_to_response(created_entity)

    async def get_text(self, text_id: UUID) -> TextResponse | None:
        """
        Retrieve a text by ID.

        Args:
            text_id: Text UUID

        Returns:
            Text response if found, None otherwise

        Raises:
            Exception: If retrieval fails
        """
        logger.debug(f"Retrieving text: {text_id}")

        entity = await self.repository.get_by_id(text_id)
        if entity is None:
            logger.debug(f"Text not found: {text_id}")
            return None

        return self._entity_to_response(entity)

    async def get_all_texts(
        self, skip: int = 0, limit: int = 100
    ) -> list[TextResponse]:
        """
        Retrieve all texts with pagination.

        Args:
            skip: Number of texts to skip (for pagination)
            limit: Maximum number of texts to return

        Returns:
            List of text responses

        Raises:
            Exception: If retrieval fails
        """
        logger.debug(f"Retrieving all texts (skip={skip}, limit={limit})")

        entities = await self.repository.get_all(skip=skip, limit=limit)
        return [self._entity_to_response(entity) for entity in entities]

    async def update_text(
        self, text_id: UUID, text_data: TextUpdate
    ) -> TextResponse | None:
        """
        Update a text.

        Args:
            text_id: Text UUID
            text_data: Text update data

        Returns:
            Updated text response if found, None otherwise

        Raises:
            Exception: If update fails
        """
        logger.info(f"Updating text: {text_id}")

        existing_entity = await self.repository.get_by_id(text_id)
        if existing_entity is None:
            logger.warning(f"Text not found for update: {text_id}")
            return None

        # Prepare update data using model_dump(by_alias=True) for aliased fields
        update_dict = text_data.model_dump(by_alias=True, exclude_unset=True)

        # Create a new TextEntity with updated fields
        updated_entity_data = {
            "id": existing_entity.id,
            "title": update_dict.get("title", existing_entity.title),
            "content": update_dict.get("content", existing_entity.content),
            "languageId": update_dict.get("languageId", existing_entity.language_id),
            "userId": update_dict.get("userId", existing_entity.user_id),
            "proficiencyLevel": update_dict.get(
                "proficiencyLevel", existing_entity.proficiency_level
            ),
            "wordCount": update_dict.get("wordCount", existing_entity.word_count),
            "isPublic": update_dict.get("isPublic", existing_entity.is_public),
            "source": update_dict.get("source", existing_entity.source),
            "createdAt": existing_entity.created_at,
            "updatedAt": datetime.now(UTC),
        }
        updated_entity = TextEntity(**updated_entity_data)

        updated = await self.repository.update(text_id, updated_entity)

        if updated is None:
            logger.error(f"Failed to update text: {text_id}")
            return None

        logger.info(f"Text updated successfully: {text_id}")
        return self._entity_to_response(updated)

    async def delete_text(self, text_id: UUID) -> bool:
        """
        Delete a text by ID.

        Args:
            text_id: Text UUID

        Returns:
            True if deleted, False if not found

        Raises:
            Exception: If deletion fails
        """
        logger.info(f"Deleting text: {text_id}")

        deleted = await self.repository.delete(text_id)
        if deleted:
            logger.info(f"Text deleted successfully: {text_id}")
        else:
            logger.warning(f"Text not found for deletion: {text_id}")

        return deleted
