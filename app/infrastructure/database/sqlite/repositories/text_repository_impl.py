"""
SQLite implementation of Text repository.

This module provides a concrete implementation of ITextRepository
using SQLAlchemy async ORM and raw SQL queries.
"""

import logging
import uuid
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.core.config import BASE_DIR
from app.domain.entities.enums import ProficiencyLevel
from app.domain.entities.text import Text as TextEntity
from app.domain.interfaces.text_repository import ITextRepository
from app.infrastructure.database.sqlite.models import (
    TextModel,
    TextTagAssociation,
)

logger = logging.getLogger(__name__)


class SQLiteTextRepository(ITextRepository):
    """
    SQLite implementation of Text repository.

    This implementation uses SQLAlchemy ORM for type-safe database operations
    and provides all methods defined in ITextRepository interface.
    """

    def __init__(self, db_path: str | None = None, engine: AsyncEngine | None = None):
        """
        Initialize the SQLite Text repository.

        Args:
            db_path: Optional path to SQLite database file.
                     If None, uses SQLITE_DB_PATH from environment.
            engine: Optional shared async engine. If provided, uses this engine.
                    Otherwise, creates a new one (for backward compatibility).
        """
        import os

        if engine is not None:
            self.engine = engine
        else:
            # Fallback: create own engine (for backward compatibility)
            from sqlalchemy.ext.asyncio import create_async_engine

            if db_path is None:
                db_path = str(
                    BASE_DIR / os.getenv("SQLITE_DB_PATH", "data/lexiglow.db")
                )
            self.engine = create_async_engine(
                f"sqlite+aiosqlite:///{db_path}", echo=False, pool_pre_ping=True
            )

        self.SessionLocal = async_sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info("SQLiteTextRepository initialized")

    def _model_to_entity(self, model: TextModel) -> TextEntity:
        """
        Convert ORM model to domain entity.

        Args:
            model: SQLAlchemy Text model

        Returns:
            Pydantic Text entity
        """
        return TextEntity(
            id=UUID(str(model.id)),
            title=str(model.title),
            content=str(model.content),
            languageId=UUID(str(model.languageId)),
            userId=UUID(str(model.userId)) if model.userId else None,
            proficiencyLevel=ProficiencyLevel(model.proficiencyLevel),
            wordCount=int(model.wordCount),
            isPublic=bool(model.isPublic),
            source=str(model.source) if model.source else None,
            createdAt=model.createdAt,
            updatedAt=model.updatedAt,
        )

    def _entity_to_model(self, entity: TextEntity) -> TextModel:
        """
        Convert domain entity to ORM model.

        Args:
            entity: Pydantic Text entity

        Returns:
            SQLAlchemy Text model
        """
        return TextModel(
            id=str(entity.id),
            title=entity.title,
            content=entity.content,
            languageId=str(entity.language_id),
            userId=str(entity.user_id) if entity.user_id else None,
            proficiencyLevel=entity.proficiency_level.value,
            wordCount=entity.word_count,
            isPublic=int(entity.is_public),
            source=entity.source,
            createdAt=entity.created_at,
            updatedAt=entity.updated_at,
        )

    async def create(self, entity: TextEntity) -> TextEntity:
        """
        Create a new text in the repository.

        Args:
            entity: Text entity to create

        Returns:
            Created text entity with generated ID if not provided

        Raises:
            RepositoryError: If creation fails
        """
        text_model: TextModel
        try:
            async with self.SessionLocal() as session:
                # Generate ID if not provided
                if entity.id is None:
                    entity.id = uuid.uuid4()

                # Convert entity to model
                text_model = self._entity_to_model(entity)

                # Add and commit
                session.add(text_model)
                await session.commit()
                await session.refresh(text_model)

                logger.info(f"Created text: {text_model.title} (ID: {text_model.id})")
            return self._model_to_entity(text_model)

        except SQLAlchemyError as e:
            logger.error(f"Failed to create text: {e}")
            raise Exception(f"Failed to create text: {e}") from e

    async def get_by_id(self, entity_id: UUID) -> TextEntity | None:
        """
        Retrieve a text by its ID.

        Args:
            entity_id: UUID of the text

        Returns:
            Text entity if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            async with self.SessionLocal() as session:
                result = await session.execute(
                    select(TextModel).filter_by(id=str(entity_id))
                )
                text_model = result.scalar_one_or_none()

                if text_model:
                    logger.debug(f"Retrieved text by ID: {entity_id}")
                    return self._model_to_entity(text_model)

                logger.debug(f"Text not found with ID: {entity_id}")
                return None

        except SQLAlchemyError as e:
            logger.error(f"Failed to get text by ID: {e}")
            raise Exception(f"Failed to get text by ID: {e}") from e

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[TextEntity]:
        """
        Retrieve all texts with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of text entities

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            async with self.SessionLocal() as session:
                result = await session.execute(
                    select(TextModel).offset(skip).limit(limit)
                )
                texts = result.scalars().all()

                logger.debug(
                    f"Retrieved {len(texts)} texts (skip={skip}, limit={limit})"
                )
                return [self._model_to_entity(text) for text in texts]

        except SQLAlchemyError as e:
            logger.error(f"Failed to get all texts: {e}")
            raise Exception(f"Failed to get all texts: {e}") from e

    async def update(self, entity_id: UUID, entity: TextEntity) -> TextEntity | None:
        """
        Update an existing text.

        Args:
            entity_id: UUID of the text to update
            entity: Updated text entity

        Returns:
            Updated text entity if found, None otherwise

        Raises:
            RepositoryError: If update fails
        """
        try:
            async with self.SessionLocal() as session:
                result = await session.execute(
                    select(TextModel).filter_by(id=str(entity_id))
                )
                text_model = result.scalar_one_or_none()

                if not text_model:
                    logger.warning(f"Text not found for update: {entity_id}")
                    return None

                # Update fields
                text_model.title = entity.title
                text_model.content = entity.content
                text_model.languageId = str(entity.language_id)
                text_model.userId = str(entity.user_id) if entity.user_id else None
                text_model.proficiencyLevel = entity.proficiency_level.value
                text_model.wordCount = entity.word_count
                text_model.isPublic = int(entity.is_public)
                text_model.source = entity.source
                text_model.updatedAt = datetime.now(UTC)

                await session.commit()
                await session.refresh(text_model)

                logger.info(f"Updated text: {text_model.title} (ID: {entity_id})")
                return self._model_to_entity(text_model)

        except SQLAlchemyError as e:
            logger.error(f"Failed to update text: {e}")
            raise Exception(f"Failed to update text: {e}") from e

    async def delete(self, entity_id: UUID) -> bool:
        """
        Delete a text by its ID.

        Args:
            entity_id: UUID of the text to delete

        Returns:
            True if deleted successfully, False if not found

        Raises:
            RepositoryError: If deletion fails
        """
        try:
            async with self.SessionLocal() as session:
                result = await session.execute(
                    select(TextModel).filter_by(id=str(entity_id))
                )
                text_model = result.scalar_one_or_none()

                if not text_model:
                    logger.warning(f"Text not found for deletion: {entity_id}")
                    return False

                session.delete(text_model)
                await session.commit()

                logger.info(f"Deleted text: {text_model.title} (ID: {entity_id})")
                return True

        except SQLAlchemyError as e:
            logger.error(f"Failed to delete text: {e}")
            raise Exception(f"Failed to delete text: {e}") from e

    async def exists(self, entity_id: UUID) -> bool:
        """
        Check if a text exists by its ID.

        Args:
            entity_id: UUID of the text

        Returns:
            True if text exists, False otherwise

        Raises:
            RepositoryError: If check fails
        """
        try:
            async with self.SessionLocal() as session:
                result = await session.execute(
                    select(TextModel.id).filter_by(id=str(entity_id))
                )
                exists = result.scalar_one_or_none() is not None

                logger.debug(f"Text exists check for {entity_id}: {exists}")
                return exists

        except SQLAlchemyError as e:
            logger.error(f"Failed to check text existence: {e}")
            raise Exception(f"Failed to check text existence: {e}") from e

    async def get_by_language(
        self, language_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[TextEntity]:
        """
        Retrieve texts by language.

        Args:
            language_id: The UUID of the language
            skip: Number of texts to skip (for pagination)
            limit: Maximum number of texts to return

        Returns:
            List of texts in the specified language

        Raises:
            RepositoryError: If the retrieval fails
        """
        try:
            async with self.SessionLocal() as session:
                result = await session.execute(
                    select(TextModel)
                    .filter_by(languageId=str(language_id))
                    .offset(skip)
                    .limit(limit)
                )
                texts = result.scalars().all()

                logger.debug(
                    f"Retrieved {len(texts)} texts for language {language_id} "
                    f"(skip={skip}, limit={limit})"
                )
                return [self._model_to_entity(text) for text in texts]

        except SQLAlchemyError as e:
            logger.error(f"Failed to get texts by language: {e}")
            raise Exception(f"Failed to get texts by language: {e}") from e

    async def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[TextEntity]:
        """
        Retrieve texts by user.

        Args:
            user_id: The UUID of the user
            skip: Number of texts to skip (for pagination)
            limit: Maximum number of texts to return

        Returns:
            List of texts by the specified user

        Raises:
            RepositoryError: If the retrieval fails
        """
        try:
            async with self.SessionLocal() as session:
                result = await session.execute(
                    select(TextModel)
                    .filter_by(userId=str(user_id))
                    .offset(skip)
                    .limit(limit)
                )
                texts = result.scalars().all()

                logger.debug(
                    f"Retrieved {len(texts)} texts for user {user_id} "
                    f"(skip={skip}, limit={limit})"
                )
                return [self._model_to_entity(text) for text in texts]

        except SQLAlchemyError as e:
            logger.error(f"Failed to get texts by user: {e}")
            raise Exception(f"Failed to get texts by user: {e}") from e

    async def get_by_proficiency_level(
        self, proficiency_level: ProficiencyLevel, skip: int = 0, limit: int = 100
    ) -> list[TextEntity]:
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
        try:
            async with self.SessionLocal() as session:
                result = await session.execute(
                    select(TextModel)
                    .filter_by(proficiencyLevel=proficiency_level.value)
                    .offset(skip)
                    .limit(limit)
                )
                texts = result.scalars().all()

                logger.debug(
                    f"Retrieved {len(texts)} texts for proficiency level "
                    f"{proficiency_level.value} (skip={skip}, limit={limit})"
                )
                return [self._model_to_entity(text) for text in texts]

        except SQLAlchemyError as e:
            logger.error(f"Failed to get texts by proficiency level: {e}")
            raise Exception(f"Failed to get texts by proficiency level: {e}") from e

    async def get_public_texts(
        self, skip: int = 0, limit: int = 100
    ) -> list[TextEntity]:
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
        try:
            async with self.SessionLocal() as session:
                result = await session.execute(
                    select(TextModel).filter_by(isPublic=1).offset(skip).limit(limit)
                )
                texts = result.scalars().all()

                logger.debug(
                    f"Retrieved {len(texts)} public texts (skip={skip}, limit={limit})"
                )
                return [self._model_to_entity(text) for text in texts]

        except SQLAlchemyError as e:
            logger.error(f"Failed to get public texts: {e}")
            raise Exception(f"Failed to get public texts: {e}") from e

    async def search_by_title(
        self, title_query: str, skip: int = 0, limit: int = 100
    ) -> list[TextEntity]:
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
        try:
            async with self.SessionLocal() as session:
                # Case-insensitive search using LIKE
                search_pattern = f"%{title_query}%"
                result = await session.execute(
                    select(TextModel)
                    .filter(TextModel.title.like(search_pattern))
                    .offset(skip)
                    .limit(limit)
                )
                texts = result.scalars().all()

                logger.debug(
                    f"Found {len(texts)} texts matching title query '{title_query}' "
                    f"(skip={skip}, limit={limit})"
                )
                return [self._model_to_entity(text) for text in texts]

        except SQLAlchemyError as e:
            logger.error(f"Failed to search texts by title: {e}")
            raise Exception(f"Failed to search texts by title: {e}") from e

    async def get_by_tags(
        self, tag_ids: list[UUID], skip: int = 0, limit: int = 100
    ) -> list[TextEntity]:
        """
        Retrieve texts by tags.

        Args:
            tag_ids: List of tag UUIDs to filter by
            skip: Number of texts to skip (for pagination)
            limit: Maximum number of texts to return

        Returns:
            List of texts with the specified tags

        Raises:
            RepositoryError: If the retrieval fails
        """
        try:
            async with self.SessionLocal() as session:
                # Convert tag_ids to strings
                str_tag_ids = [str(tag_id) for tag_id in tag_ids]

                # Query texts that have associations with any of the provided tags
                result = await session.execute(
                    select(TextModel)
                    .join(TextTagAssociation, TextModel.id == TextTagAssociation.textId)
                    .filter(TextTagAssociation.tagId.in_(str_tag_ids))
                    .distinct()
                    .offset(skip)
                    .limit(limit)
                )
                texts = result.scalars().all()

                logger.debug(
                    f"Retrieved {len(texts)} texts with tags {tag_ids} "
                    f"(skip={skip}, limit={limit})"
                )
                return [self._model_to_entity(text) for text in texts]

        except SQLAlchemyError as e:
            logger.error(f"Failed to get texts by tags: {e}")
            raise Exception(f"Failed to get texts by tags: {e}") from e
