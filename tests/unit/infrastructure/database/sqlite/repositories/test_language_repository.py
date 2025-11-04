"""
Unit tests for SQLiteLanguageRepository.

Tests cover all methods of the repository implementation including
CRUD operations, queries, existence checks, and entity conversions.
"""

import uuid
from datetime import datetime, timezone
from typing import Callable
from uuid import UUID

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entities.language import Language as LanguageEntity
from app.infrastructure.database.sqlite.models import Base, Language as LanguageModel
from app.infrastructure.database.sqlite.repositories.language_repository_impl import (
    SQLiteLanguageRepository,
)


# Fixtures


@pytest.fixture(scope="function")
def setup_database(tmp_path):
    """Create a temporary database and tables for tests."""
    db_file = tmp_path / "test_language_repo.db"
    engine = create_engine(f"sqlite:///{db_file}", echo=False)
    Base.metadata.create_all(engine)
    yield str(db_file)
    engine.dispose()


@pytest.fixture(scope="function")
def repository(setup_database):
    """Create a SQLiteLanguageRepository instance with a test database."""
    repo = SQLiteLanguageRepository(db_path=setup_database)
    yield repo
    repo.engine.dispose()


@pytest.fixture
def sample_language_entity() -> Callable:
    """Factory fixture for creating Language entities."""

    def _create_language(
        lang_id: UUID = None,
        name: str = "English",
        code: str = "en",
        native_name: str = "English",
    ) -> LanguageEntity:
        return LanguageEntity(
            id=lang_id or uuid.uuid4(),
            name=name,
            code=code,
            native_name=native_name,
            created_at=datetime.now(timezone.utc),
        )

    return _create_language


# Test Classes


class TestCreateLanguage:
    """Test language creation."""

    def test_create_language_success(self, repository, sample_language_entity):
        """Test creating a language successfully."""
        lang_entity = sample_language_entity()
        created_lang = repository.create(lang_entity)

        assert created_lang is not None
        assert created_lang.id == lang_entity.id
        assert created_lang.name == "English"
        assert created_lang.code == "en"

    def test_create_language_generates_id(self, repository, sample_language_entity):
        """Test that an ID is generated when not provided."""
        lang_entity = sample_language_entity(lang_id=None)
        lang_entity.id = None  # Explicitly set to None

        created_lang = repository.create(lang_entity)

        assert created_lang.id is not None
        assert isinstance(created_lang.id, UUID)

    def test_create_language_duplicate_code(self, repository, sample_language_entity):
        """Test constraint violation for duplicate language code."""
        repository.create(sample_language_entity(code="fr", name="French"))

        duplicate_lang = sample_language_entity(
            lang_id=uuid.uuid4(), code="fr", name="French Variant"
        )

        with pytest.raises(Exception, match="Failed to create language"):
            repository.create(duplicate_lang)


class TestGetLanguageById:
    """Test retrieving languages by ID."""

    def test_get_by_id_found(self, repository, sample_language_entity):
        """Test retrieving an existing language by ID."""
        created_lang = repository.create(sample_language_entity())
        retrieved_lang = repository.get_by_id(created_lang.id)

        assert retrieved_lang is not None
        assert retrieved_lang.id == created_lang.id
        assert retrieved_lang.name == created_lang.name

    def test_get_by_id_not_found(self, repository):
        """Test retrieving a non-existent language returns None."""
        non_existent_id = uuid.uuid4()
        result = repository.get_by_id(non_existent_id)
        assert result is None


class TestGetAllLanguages:
    """Test retrieving all languages with pagination."""

    def test_get_all_empty(self, repository):
        """Test getting all languages when the database is empty."""
        languages = repository.get_all()
        assert languages == []

    def test_get_all_multiple_languages(self, repository, sample_language_entity):
        """Test retrieving all languages."""
        repository.create(sample_language_entity(name="Spanish", code="es"))
        repository.create(sample_language_entity(name="German", code="de"))

        languages = repository.get_all()
        assert len(languages) == 2
        codes = [lang.code for lang in languages]
        assert "es" in codes
        assert "de" in codes

    def test_get_all_with_pagination(self, repository, sample_language_entity):
        """Test pagination with skip and limit parameters."""
        for i in range(5):
            repository.create(
                sample_language_entity(name=f"Lang {i}", code=f"l{i}")
            )

        page1 = repository.get_all(skip=0, limit=2)
        assert len(page1) == 2

        page2 = repository.get_all(skip=2, limit=2)
        assert len(page2) == 2
        assert page1[0].id != page2[0].id


class TestUpdateLanguage:
    """Test language update operations."""

    def test_update_language_success(self, repository, sample_language_entity):
        """Test updating a language successfully."""
        created_lang = repository.create(sample_language_entity())
        created_lang.name = "British English"
        created_lang.native_name = "British English"

        updated_lang = repository.update(created_lang.id, created_lang)

        assert updated_lang is not None
        assert updated_lang.name == "British English"
        assert updated_lang.native_name == "British English"

    def test_update_language_not_found(self, repository, sample_language_entity):
        """Test updating a non-existent language returns None."""
        non_existent_id = uuid.uuid4()
        lang_entity = sample_language_entity()
        result = repository.update(non_existent_id, lang_entity)
        assert result is None


class TestDeleteLanguage:
    """Test language deletion."""

    def test_delete_language_success(self, repository, sample_language_entity):
        """Test deleting an existing language returns True."""
        created_lang = repository.create(sample_language_entity())
        result = repository.delete(created_lang.id)
        assert result is True
        assert repository.get_by_id(created_lang.id) is None

    def test_delete_language_not_found(self, repository):
        """Test deleting a non-existent language returns False."""
        non_existent_id = uuid.uuid4()
        result = repository.delete(non_existent_id)
        assert result is False


class TestExistsLanguage:
    """Test language existence checks."""

    def test_exists_true(self, repository, sample_language_entity):
        """Test exists returns True for an existing language."""
        created_lang = repository.create(sample_language_entity())
        assert repository.exists(created_lang.id) is True

    def test_exists_false(self, repository):
        """Test exists returns False for a non-existent language."""
        non_existent_id = uuid.uuid4()
        assert repository.exists(non_existent_id) is False


class TestGetLanguageByCode:
    """Test retrieving languages by code."""

    def test_get_by_code_found(self, repository, sample_language_entity):
        """Test retrieving a language by its code."""
        repository.create(sample_language_entity(code="jp", name="Japanese"))
        found_lang = repository.get_by_code("jp")
        assert found_lang is not None
        assert found_lang.name == "Japanese"

    def test_get_by_code_not_found(self, repository):
        """Test retrieving a non-existent code returns None."""
        assert repository.get_by_code("xx") is None


class TestGetLanguageByName:
    """Test retrieving languages by name."""

    def test_get_by_name_found(self, repository, sample_language_entity):
        """Test retrieving a language by its name."""
        repository.create(sample_language_entity(name="Portuguese", code="pt"))
        found_lang = repository.get_by_name("Portuguese")
        assert found_lang is not None
        assert found_lang.code == "pt"

    def test_get_by_name_not_found(self, repository):
        """Test retrieving a non-existent name returns None."""
        assert repository.get_by_name("Klingon") is None


class TestCodeExists:
    """Test language code existence checks."""

    def test_code_exists_true(self, repository, sample_language_entity):
        """Test code_exists returns True for an existing code."""
        repository.create(sample_language_entity(code="it", name="Italian"))
        assert repository.code_exists("it") is True

    def test_code_exists_false(self, repository):
        """Test code_exists returns False for a non-existent code."""
        assert repository.code_exists("zz") is False


class TestEntityConversion:
    """Test entity/model conversion methods."""

    def test_model_to_entity_conversion(self, repository):
        """Test converting ORM model to domain entity."""
        lang_model = LanguageModel(
            id=str(uuid.uuid4()),
            name="Test Language",
            code="tl",
            nativeName="Test",
            createdAt=datetime.now(timezone.utc),
        )
        entity = repository._model_to_entity(lang_model)
        assert isinstance(entity, LanguageEntity)
        assert str(entity.id) == lang_model.id
        assert entity.name == lang_model.name

    def test_entity_to_model_conversion(self, repository, sample_language_entity):
        """Test converting domain entity to ORM model."""
        lang_entity = sample_language_entity()
        model = repository._entity_to_model(lang_entity)
        assert isinstance(model, LanguageModel)
        assert model.id == str(lang_entity.id)
        assert model.name == lang_entity.name

    def test_conversion_roundtrip(self, repository, sample_language_entity):
        """Test that entity -> model -> entity preserves data."""
        original_entity = sample_language_entity()
        model = repository._entity_to_model(original_entity)
        converted_entity = repository._model_to_entity(model)
        assert converted_entity == original_entity
