"""
SQLite implementation of Language repository.

This module provides a concrete implementation of ILanguageRepository
using SQLAlchemy ORM and raw SQL queries.
"""

import logging
import uuid
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.core.config import BASE_DIR
from app.domain.entities.language import Language as LanguageEntity
from app.domain.interfaces.language_repository import ILanguageRepository
from app.infrastructure.database.sqlite.models import Language as LanguageModel

logger = logging.getLogger(__name__)


class SQLiteLanguageRepository(ILanguageRepository):
    """
    SQLite implementation of Language repository.

    This implementation uses SQLAlchemy ORM for type-safe database operations
    and provides all methods defined in ILanguageRepository interface.
    """

    def __init__(self, db_path: str | None = None):
        """
        Initialize the SQLite Language repository.

        Args:
            db_path: Optional path to SQLite database file.
                     If None, uses SQLITE_DB_PATH from environment.
        """
        import os

        if db_path is None:
            db_path = str(BASE_DIR / os.getenv("SQLITE_DB_PATH", "data/lexiglow.db"))

        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info(f"SQLiteLanguageRepository initialized with database: {db_path}")

    def _model_to_entity(self, model: LanguageModel) -> LanguageEntity:
        """
        Convert ORM model to domain entity.

        Args:
            model: SQLAlchemy Language model

        Returns:
            Pydantic Language entity
        """
        return LanguageEntity(
            id=UUID(str(model.id)),
            name=str(model.name),
            code=str(model.code),
            nativeName=str(model.nativeName),
            createdAt=model.createdAt,
        )

    def _entity_to_model(self, entity: LanguageEntity) -> LanguageModel:
        """
        Convert domain entity to ORM model.

        Args:
            entity: Pydantic Language entity

        Returns:
            SQLAlchemy Language model
        """
        return LanguageModel(
            id=str(entity.id),
            name=entity.name,
            code=entity.code,
            nativeName=entity.native_name,
            createdAt=entity.created_at,
        )

    def create(self, entity: LanguageEntity) -> LanguageEntity:
        """
        Create a new language in the repository.

        Args:
            entity: Language entity to create

        Returns:
            Created language entity with generated ID if not provided

        Raises:
            RepositoryError: If creation fails
        """
        try:
            with self.SessionLocal() as session:
                # Generate ID if not provided
                if entity.id is None:
                    entity.id = UUID(str(uuid.uuid4()))

                # Convert entity to model
                language_model = self._entity_to_model(entity)

                # Add and commit
                session.add(language_model)
                session.commit()
                session.refresh(language_model)

                logger.info(
                    f"Created language: {language_model.name} (ID: {language_model.id})"
                )
                return self._model_to_entity(language_model)

        except SQLAlchemyError as e:
            logger.error(f"Failed to create language: {e}")
            raise Exception(f"Failed to create language: {e}") from e

    def get_by_id(self, entity_id: UUID) -> LanguageEntity | None:
        """
        Retrieve a language by its ID.

        Args:
            entity_id: UUID of the language

        Returns:
            Language entity if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            with self.SessionLocal() as session:
                language_model = (
                    session.query(LanguageModel).filter_by(id=str(entity_id)).first()
                )

                if language_model:
                    logger.debug(f"Retrieved language by ID: {entity_id}")
                    return self._model_to_entity(language_model)

                logger.debug(f"Language not found with ID: {entity_id}")
                return None

        except SQLAlchemyError as e:
            logger.error(f"Failed to get language by ID: {e}")
            raise Exception(f"Failed to get language by ID: {e}") from e

    def get_all(self, skip: int = 0, limit: int = 100) -> list[LanguageEntity]:
        """
        Retrieve all languages with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of language entities

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            with self.SessionLocal() as session:
                languages = session.query(LanguageModel).offset(skip).limit(limit).all()

                logger.debug(
                    f"Retrieved {len(languages)} languages (skip={skip}, limit={limit})"
                )
                return [self._model_to_entity(language) for language in languages]

        except SQLAlchemyError as e:
            logger.error(f"Failed to get all languages: {e}")
            raise Exception(f"Failed to get all languages: {e}") from e

    def update(self, entity_id: UUID, entity: LanguageEntity) -> LanguageEntity | None:
        """
        Update an existing language.

        Args:
            entity_id: UUID of the language to update
            entity: Updated language entity

        Returns:
            Updated language entity if found, None otherwise

        Raises:
            RepositoryError: If update fails
        """
        try:
            with self.SessionLocal() as session:
                language_model = (
                    session.query(LanguageModel).filter_by(id=str(entity_id)).first()
                )

                if not language_model:
                    logger.warning(f"Language not found for update: {entity_id}")
                    return None

                # Update fields
                language_model.name = entity.name
                language_model.code = entity.code
                language_model.nativeName = entity.native_name

                session.commit()
                session.refresh(language_model)

                logger.info(
                    f"Updated language: {language_model.name} (ID: {entity_id})"
                )
                return self._model_to_entity(language_model)

        except SQLAlchemyError as e:
            logger.error(f"Failed to update language: {e}")
            raise Exception(f"Failed to update language: {e}") from e

    def delete(self, entity_id: UUID) -> bool:
        """
        Delete a language by its ID.

        Args:
            entity_id: UUID of the language to delete

        Returns:
            True if deleted successfully, False if not found

        Raises:
            RepositoryError: If deletion fails
        """
        try:
            with self.SessionLocal() as session:
                language_model = (
                    session.query(LanguageModel).filter_by(id=str(entity_id)).first()
                )

                if not language_model:
                    logger.warning(f"Language not found for deletion: {entity_id}")
                    return False

                session.delete(language_model)
                session.commit()

                logger.info(
                    f"Deleted language: {language_model.name} (ID: {entity_id})"
                )
                return True

        except SQLAlchemyError as e:
            logger.error(f"Failed to delete language: {e}")
            raise Exception(f"Failed to delete language: {e}") from e

    def exists(self, entity_id: UUID) -> bool:
        """
        Check if a language exists by its ID.

        Args:
            entity_id: UUID of the language

        Returns:
            True if language exists, False otherwise

        Raises:
            RepositoryError: If check fails
        """
        try:
            with self.SessionLocal() as session:
                exists = (
                    session.query(LanguageModel.id).filter_by(id=str(entity_id)).first()
                    is not None
                )

                logger.debug(f"Language exists check for {entity_id}: {exists}")
                return exists

        except SQLAlchemyError as e:
            logger.error(f"Failed to check language existence: {e}")
            raise Exception(f"Failed to check language existence: {e}") from e

    def get_by_code(self, code: str) -> LanguageEntity | None:
        """
        Retrieve a language by its ISO 639-1 code.

        Args:
            code: The ISO 639-1 language code (e.g., 'en', 'es')

        Returns:
            The language if found, None otherwise

        Raises:
            RepositoryError: If the retrieval fails
        """
        try:
            with self.SessionLocal() as session:
                language_model = (
                    session.query(LanguageModel).filter_by(code=code).first()
                )

                if language_model:
                    logger.debug(f"Retrieved language by code: {code}")
                    return self._model_to_entity(language_model)

                logger.debug(f"Language not found with code: {code}")
                return None

        except SQLAlchemyError as e:
            logger.error(f"Failed to get language by code: {e}")
            raise Exception(f"Failed to get language by code: {e}") from e

    def get_by_name(self, name: str) -> LanguageEntity | None:
        """
        Retrieve a language by its name.

        Args:
            name: The language name to search for

        Returns:
            The language if found, None otherwise

        Raises:
            RepositoryError: If the retrieval fails
        """
        try:
            with self.SessionLocal() as session:
                language_model = (
                    session.query(LanguageModel).filter_by(name=name).first()
                )

                if language_model:
                    logger.debug(f"Retrieved language by name: {name}")
                    return self._model_to_entity(language_model)

                logger.debug(f"Language not found with name: {name}")
                return None

        except SQLAlchemyError as e:
            logger.error(f"Failed to get language by name: {e}")
            raise Exception(f"Failed to get language by name: {e}") from e

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
        try:
            with self.SessionLocal() as session:
                exists = (
                    session.query(LanguageModel.id).filter_by(code=code).first()
                    is not None
                )

                logger.debug(f"Language code exists check for {code}: {exists}")
                return exists

        except SQLAlchemyError as e:
            logger.error(f"Failed to check language code existence: {e}")
            raise Exception(f"Failed to check language code existence: {e}") from e
