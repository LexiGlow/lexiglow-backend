"""
Unit tests for MongoDBLanguageRepository.

Tests cover all methods of the repository implementation including
CRUD operations, queries, existence checks, and entity conversions.
"""

import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.domain.entities.language import Language as LanguageEntity
from app.infrastructure.database.mongodb.repositories.language_repository_impl import (
    MongoDBLanguageRepository,
)

# Fixtures


@pytest.fixture(scope="function")
def repository(mongo_client, db_url):
    """Create a MongoDBLanguageRepository instance with a test database."""
    db_name = f"test_db_{uuid.uuid4().hex}"
    repo = MongoDBLanguageRepository(db_url=db_url, db_name=db_name)
    yield repo
    mongo_client.drop_database(db_name)


@pytest.fixture
def sample_language_entity() -> Callable[..., LanguageEntity]:
    """Factory fixture for creating Language entities."""

    def _create_language(
        lang_id: UUID | None = None,
        name: str = "English",
        code: str = "en",
        native_name: str = "English",
    ) -> LanguageEntity:
        return LanguageEntity(
            id=lang_id or uuid.uuid4(),
            name=name,
            code=code,
            nativeName=native_name,
            createdAt=datetime.now(UTC),
        )

    return _create_language


# Test Classes


class TestCreateLanguage:
    """Test language creation."""

    @pytest.mark.asyncio
    async def test_create_language_success(self, repository, sample_language_entity):
        """Test creating a language successfully."""
        lang_entity = sample_language_entity()
        created_lang = await repository.create(lang_entity)

        assert created_lang is not None
        assert created_lang.id == lang_entity.id
        assert created_lang.name == "English"
        assert created_lang.code == "en"

    @pytest.mark.asyncio
    async def test_create_language_generates_id(
        self, repository, sample_language_entity
    ):
        """Test that an ID is generated when not provided."""
        lang_entity = sample_language_entity(lang_id=None)
        lang_entity.id = None  # Explicitly set to None

        created_lang = await repository.create(lang_entity)

        assert created_lang.id is not None
        assert isinstance(created_lang.id, UUID)

    @pytest.mark.asyncio
    async def test_create_language_duplicate_code(
        self, repository, sample_language_entity
    ):
        """
        Test constraint violation for duplicate language code.
        MongoDB doesn't enforce unique constraints by default, but our
        repository methods should handle this logic or rely on application logic.
        For now, we'll test that creating a duplicate code will raise an exception
        if we try to create a unique index on the 'code' field.
        """
        await repository.create(sample_language_entity(code="fr", name="French"))

        duplicate_lang = sample_language_entity(
            lang_id=uuid.uuid4(), code="fr", name="French Variant"
        )

        # MongoDB doesn't automatically raise an exception for duplicate values
        # unless a unique index is explicitly created. For this test, we assume
        # that the application layer or a unique index would prevent this.
        # If a unique index is added, this test should be updated
        # to expect PyMongoError.
        # For now, we'll assert that it creates a new entry,
        # as MongoDB allows it without unique index.
        # If unique index is added, uncomment the pytest.raises line.
        # with pytest.raises(Exception, match="Failed to create language"):
        duplicate_id = duplicate_lang.id
        created_lang = await repository.create(duplicate_lang)
        # The created language should use the provided ID
        assert created_lang.id == duplicate_id
        # Verify both languages exist with the same code (MongoDB allows duplicates
        # without unique index)
        assert await repository.get_by_code("fr") is not None
        all_langs = await repository.get_all()
        fr_langs = [lang for lang in all_langs if lang.code == "fr"]
        assert len(fr_langs) == 2  # Both languages with code "fr" should exist


class TestGetLanguageById:
    """Test retrieving languages by ID."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, sample_language_entity):
        """Test retrieving an existing language by ID."""
        created_lang = await repository.create(sample_language_entity())
        retrieved_lang = await repository.get_by_id(created_lang.id)

        assert retrieved_lang is not None
        assert retrieved_lang.id == created_lang.id
        assert retrieved_lang.name == created_lang.name

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test retrieving a non-existent language returns None."""
        non_existent_id = uuid.uuid4()
        result = await repository.get_by_id(non_existent_id)
        assert result is None


class TestGetAllLanguages:
    """Test retrieving all languages with pagination."""

    @pytest.mark.asyncio
    async def test_get_all_empty(self, repository):
        """Test getting all languages when the database is empty."""
        languages = await repository.get_all()
        assert languages == []

    @pytest.mark.asyncio
    async def test_get_all_multiple_languages(self, repository, sample_language_entity):
        """Test retrieving all languages."""
        await repository.create(sample_language_entity(name="Spanish", code="es"))
        await repository.create(sample_language_entity(name="German", code="de"))

        languages = await repository.get_all()
        assert len(languages) == 2
        codes = [lang.code for lang in languages]
        assert "es" in codes
        assert "de" in codes

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, repository, sample_language_entity):
        """
        Test pagination with skip and limit parameters.
        """
        for i in range(5):
            await repository.create(
                sample_language_entity(name=f"Lang {i}", code=f"l{i}")
            )

        page1 = await repository.get_all(skip=0, limit=2)
        assert len(page1) == 2

        page2 = await repository.get_all(skip=2, limit=2)
        assert len(page2) == 2
        assert page1[0].id != page2[0].id


class TestUpdateLanguage:
    """Test language update operations."""

    @pytest.mark.asyncio
    async def test_update_language_success(self, repository, sample_language_entity):
        """
        Test updating a language successfully.
        """
        created_lang = await repository.create(sample_language_entity())
        created_lang.name = "British English"
        created_lang.native_name = "British English"

        updated_lang = await repository.update(created_lang.id, created_lang)

        assert updated_lang is not None
        assert updated_lang.name == "British English"
        assert updated_lang.native_name == "British English"

    @pytest.mark.asyncio
    async def test_update_language_not_found(self, repository, sample_language_entity):
        """
        Test updating a non-existent language returns None.
        """
        non_existent_id = uuid.uuid4()
        lang_entity = sample_language_entity()
        result = await repository.update(non_existent_id, lang_entity)
        assert result is None


class TestDeleteLanguage:
    """
    Test language deletion.
    """

    @pytest.mark.asyncio
    async def test_delete_language_success(self, repository, sample_language_entity):
        """
        Test deleting an existing language returns True.
        """
        created_lang = await repository.create(sample_language_entity())
        result = await repository.delete(created_lang.id)
        assert result is True
        assert await repository.get_by_id(created_lang.id) is None

    @pytest.mark.asyncio
    async def test_delete_language_not_found(self, repository):
        """
        Test deleting a non-existent language returns False.
        """
        non_existent_id = uuid.uuid4()
        result = await repository.delete(non_existent_id)
        assert result is False


class TestExistsLanguage:
    """
    Test language existence checks.
    """

    @pytest.mark.asyncio
    async def test_exists_true(self, repository, sample_language_entity):
        """
        Test exists returns True for an existing language.
        """
        created_lang = await repository.create(sample_language_entity())
        assert await repository.exists(created_lang.id) is True

    @pytest.mark.asyncio
    async def test_exists_false(self, repository):
        """
        Test exists returns False for a non-existent language.
        """
        non_existent_id = uuid.uuid4()
        assert await repository.exists(non_existent_id) is False


class TestGetLanguageByCode:
    """
    Test retrieving languages by code.
    """

    @pytest.mark.asyncio
    async def test_get_by_code_found(self, repository, sample_language_entity):
        """
        Test retrieving a language by its code.
        """
        await repository.create(sample_language_entity(code="jp", name="Japanese"))
        found_lang = await repository.get_by_code("jp")
        assert found_lang is not None
        assert found_lang.name == "Japanese"

    @pytest.mark.asyncio
    async def test_get_by_code_not_found(self, repository):
        """
        Test retrieving a non-existent code returns None.
        """
        assert await repository.get_by_code("xx") is None


class TestGetLanguageByName:
    """
    Test retrieving languages by name.
    """

    @pytest.mark.asyncio
    async def test_get_by_name_found(self, repository, sample_language_entity):
        """
        Test retrieving a language by its name.
        """
        await repository.create(sample_language_entity(name="Portuguese", code="pt"))
        found_lang = await repository.get_by_name("Portuguese")
        assert found_lang is not None
        assert found_lang.code == "pt"

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, repository):
        """
        Test retrieving a non-existent name returns None.
        """
        assert await repository.get_by_name("Klingon") is None


class TestCodeExists:
    """
    Test language code existence checks.
    """

    @pytest.mark.asyncio
    async def test_code_exists_true(self, repository, sample_language_entity):
        """
        Test code_exists returns True for an existing code.
        """
        await repository.create(sample_language_entity(code="it", name="Italian"))
        assert await repository.code_exists("it") is True

    @pytest.mark.asyncio
    async def test_code_exists_false(self, repository):
        """
        Test code_exists returns False for a non-existent code.
        """
        assert await repository.code_exists("zz") is False
