"""
Unit tests for the LanguageService.

These tests mock the ILanguageRepository to test the service's business logic
in isolation.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from ulid import ULID

from app.application.dto.language_dto import (
    LanguageCreate,
    LanguageResponse,
    LanguageUpdate,
)
from app.application.services.language_service import LanguageService
from app.domain.entities.language import Language as LanguageEntity
from app.domain.interfaces.language_repository import ILanguageRepository


@pytest.fixture
def mock_language_repo() -> AsyncMock:
    """Provides a mock language repository."""
    return AsyncMock(spec=ILanguageRepository)


@pytest.fixture
def language_service(mock_language_repo: AsyncMock) -> LanguageService:
    """Provides a LanguageService instance with a mocked repository."""
    return LanguageService(repository=mock_language_repo)


@pytest.fixture
def sample_language_id() -> ULID:
    """Provides a sample ULID for a language."""
    return ULID()


@pytest.fixture
def sample_language_create() -> LanguageCreate:
    """Provides a sample LanguageCreate schema object."""
    return LanguageCreate(
        name="Spanish",
        code="es",
        nativeName="Español",
    )


@pytest.fixture
def sample_language_entity(sample_language_id: ULID) -> LanguageEntity:
    """Provides a sample LanguageEntity."""
    return LanguageEntity(
        id=str(sample_language_id),
        name="Spanish",
        code="es",
        nativeName="Español",
        createdAt=datetime.now(UTC),
    )


class TestLanguageService:
    """Test suite for the LanguageService class."""

    @pytest.mark.asyncio
    async def test_create_language_success(
        self,
        language_service: LanguageService,
        mock_language_repo: AsyncMock,
        sample_language_create: LanguageCreate,
    ) -> None:
        """Test Case 1.1: Successful language creation."""
        # Arrange
        mock_language_repo.code_exists.return_value = False
        created_entity = LanguageEntity(
            id=str(ULID()),
            name=sample_language_create.name,
            code=sample_language_create.code,
            nativeName=sample_language_create.native_name,
            createdAt=datetime.now(UTC),
        )
        mock_language_repo.create.return_value = created_entity

        # Act
        result = await language_service.create_language(sample_language_create)

        # Assert
        mock_language_repo.code_exists.assert_called_once_with(
            sample_language_create.code
        )
        mock_language_repo.create.assert_called_once()

        created_entity_arg = mock_language_repo.create.call_args[0][0]
        assert isinstance(created_entity_arg, LanguageEntity)
        assert created_entity_arg.name == sample_language_create.name
        assert created_entity_arg.code == sample_language_create.code
        assert created_entity_arg.native_name == sample_language_create.native_name

        assert isinstance(result, LanguageResponse)
        assert result.name == sample_language_create.name
        assert result.code == sample_language_create.code

    @pytest.mark.asyncio
    async def test_create_language_code_exists(
        self,
        language_service: LanguageService,
        mock_language_repo: AsyncMock,
        sample_language_create: LanguageCreate,
    ) -> None:
        """Test Case 1.2: Fail on existing language code."""
        # Arrange
        mock_language_repo.code_exists.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="Language code .* is already registered"):
            await language_service.create_language(sample_language_create)

        mock_language_repo.code_exists.assert_called_once_with(
            sample_language_create.code
        )
        mock_language_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_language_repository_error(
        self,
        language_service: LanguageService,
        mock_language_repo: AsyncMock,
        sample_language_create: LanguageCreate,
    ) -> None:
        """Test Case 1.3: Handle repository exceptions during creation."""
        # Arrange
        mock_language_repo.code_exists.return_value = False
        mock_language_repo.create.side_effect = Exception("Database connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="Database connection failed"):
            await language_service.create_language(sample_language_create)

        # Verify validation was performed before error
        mock_language_repo.code_exists.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_language_success(
        self,
        language_service: LanguageService,
        mock_language_repo: AsyncMock,
        sample_language_entity: LanguageEntity,
    ) -> None:
        """Test Case 2.1: Get existing language."""
        # Arrange
        mock_language_repo.get_by_id.return_value = sample_language_entity

        # Act
        assert sample_language_entity.id is not None
        result = await language_service.get_language(sample_language_entity.id)

        # Assert
        mock_language_repo.get_by_id.assert_called_once_with(sample_language_entity.id)
        assert isinstance(result, LanguageResponse)
        assert result.id == sample_language_entity.id
        assert result.name == sample_language_entity.name

    @pytest.mark.asyncio
    async def test_get_language_not_found(
        self, language_service: LanguageService, mock_language_repo: AsyncMock
    ) -> None:
        """Test Case 2.2: Get non-existent language."""
        # Arrange
        language_id = str(ULID())
        mock_language_repo.get_by_id.return_value = None

        # Act
        result = await language_service.get_language(language_id)

        # Assert
        mock_language_repo.get_by_id.assert_called_once_with(language_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_languages(
        self,
        language_service: LanguageService,
        mock_language_repo: AsyncMock,
        sample_language_entity: LanguageEntity,
    ) -> None:
        """Test Case 3.1: Get all languages."""
        # Arrange
        mock_language_repo.get_all.return_value = [sample_language_entity]

        # Act
        results = await language_service.get_all_languages(skip=5, limit=50)

        # Assert
        mock_language_repo.get_all.assert_called_once_with(skip=5, limit=50)
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0].id == sample_language_entity.id

    @pytest.mark.asyncio
    async def test_get_all_languages_empty(
        self, language_service: LanguageService, mock_language_repo: AsyncMock
    ) -> None:
        """Test Case 3.2: Get all languages when none exist."""
        # Arrange
        mock_language_repo.get_all.return_value = []

        # Act
        results = await language_service.get_all_languages()

        # Assert
        mock_language_repo.get_all.assert_called_once()
        assert results == []

    @pytest.mark.asyncio
    async def test_get_all_languages_pagination_params(
        self, language_service: LanguageService, mock_language_repo: AsyncMock
    ) -> None:
        """Test Case 3.3: Verify pagination parameters are passed correctly."""
        # Arrange
        mock_language_repo.get_all.return_value = []

        # Act - Test with explicit parameters
        await language_service.get_all_languages(skip=10, limit=25)

        # Assert
        mock_language_repo.get_all.assert_called_with(skip=10, limit=25)

        # Act - Test with defaults
        mock_language_repo.get_all.reset_mock()
        await language_service.get_all_languages()

        # Assert defaults are used
        call_kwargs = mock_language_repo.get_all.call_args[1]
        assert call_kwargs["skip"] == 0
        assert call_kwargs["limit"] == 100

    @pytest.mark.asyncio
    async def test_update_language_success(
        self,
        language_service: LanguageService,
        mock_language_repo: AsyncMock,
        sample_language_entity: LanguageEntity,
    ) -> None:
        """Test Case 4.1: Successful update."""
        # Arrange
        assert sample_language_entity.id is not None
        language_id = sample_language_entity.id
        update_data = LanguageUpdate(
            name="Updated Spanish",
            code=None,
            nativeName=None,
        )

        mock_language_repo.get_by_id.return_value = sample_language_entity

        # Create an expected updated entity to be returned by the mock repository
        expected_updated_entity = sample_language_entity.model_copy()
        if update_data.name is not None:
            expected_updated_entity.name = update_data.name

        mock_language_repo.update.return_value = expected_updated_entity

        # Act
        result = await language_service.update_language(language_id, update_data)

        # Assert
        mock_language_repo.get_by_id.assert_called_once_with(language_id)
        mock_language_repo.update.assert_called_once()

        update_arg = mock_language_repo.update.call_args[0][1]
        assert update_arg.name == "Updated Spanish"
        assert update_arg.code == sample_language_entity.code  # Unchanged
        assert update_arg.native_name == sample_language_entity.native_name  # Unchanged

        assert result is not None
        assert result.name == "Updated Spanish"

    @pytest.mark.asyncio
    async def test_update_language_not_found(
        self, language_service: LanguageService, mock_language_repo: AsyncMock
    ) -> None:
        """Test Case 4.2: Attempt to update a non-existent language."""
        # Arrange
        language_id = str(ULID())
        update_data = LanguageUpdate(
            name="Updated Name",
            code=None,
            nativeName=None,
        )
        mock_language_repo.get_by_id.return_value = None

        # Act
        result = await language_service.update_language(language_id, update_data)

        # Assert
        assert result is None
        mock_language_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_language_code_conflict(
        self,
        language_service: LanguageService,
        mock_language_repo: AsyncMock,
        sample_language_entity: LanguageEntity,
    ) -> None:
        """Test Case 4.3: Fail on code conflict."""
        # Arrange
        update_data = LanguageUpdate(
            name=None,
            code="en",
            nativeName=None,
        )
        mock_language_repo.get_by_id.return_value = sample_language_entity
        mock_language_repo.code_exists.return_value = True

        # Act & Assert
        assert sample_language_entity.id is not None
        with pytest.raises(ValueError, match="Language code .* is already registered"):
            await language_service.update_language(
                sample_language_entity.id, update_data
            )

        mock_language_repo.code_exists.assert_called_once_with("en")
        mock_language_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_language_no_changes(
        self,
        language_service: LanguageService,
        mock_language_repo: AsyncMock,
        sample_language_entity: LanguageEntity,
    ) -> None:
        """Test Case 4.4: Update language with no field changes."""
        # Arrange
        update_data = LanguageUpdate(
            name=None,
            code=None,
            nativeName=None,
        )  # All fields None
        mock_language_repo.get_by_id.return_value = sample_language_entity

        updated_entity = sample_language_entity.model_copy()
        mock_language_repo.update.return_value = updated_entity

        # Act
        assert sample_language_entity.id is not None
        result = await language_service.update_language(
            sample_language_entity.id, update_data
        )

        # Assert
        mock_language_repo.get_by_id.assert_called_once()
        mock_language_repo.update.assert_called_once()
        assert result is not None
        # All fields should remain unchanged
        assert result.name == sample_language_entity.name
        assert result.code == sample_language_entity.code
        assert result.native_name == sample_language_entity.native_name

    @pytest.mark.asyncio
    async def test_update_language_same_code_no_conflict(
        self,
        language_service: LanguageService,
        mock_language_repo: AsyncMock,
        sample_language_entity: LanguageEntity,
    ) -> None:
        """Test Case 4.5: Update with same code should not trigger conflict check."""
        # Arrange
        update_data = LanguageUpdate(
            name="Updated Name",
            code=sample_language_entity.code,  # Same code
            nativeName=None,
        )
        mock_language_repo.get_by_id.return_value = sample_language_entity

        updated_entity = sample_language_entity.model_copy()
        updated_entity.name = "Updated Name"
        mock_language_repo.update.return_value = updated_entity

        # Act
        assert sample_language_entity.id is not None
        result = await language_service.update_language(
            sample_language_entity.id, update_data
        )

        # Assert
        mock_language_repo.code_exists.assert_not_called()  # Should not check
        mock_language_repo.update.assert_called_once()
        assert result is not None
        assert result.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete_language_success(
        self, language_service: LanguageService, mock_language_repo: AsyncMock
    ) -> None:
        """Test Case 5.1: Successful deletion."""
        # Arrange
        language_id = str(ULID())
        mock_language_repo.delete.return_value = True

        # Act
        result = await language_service.delete_language(language_id)

        # Assert
        mock_language_repo.delete.assert_called_once_with(language_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_language_not_found(
        self, language_service: LanguageService, mock_language_repo: AsyncMock
    ) -> None:
        """Test Case 5.2: Attempt to delete a non-existent language."""
        # Arrange
        language_id = str(ULID())
        mock_language_repo.delete.return_value = False

        # Act
        result = await language_service.delete_language(language_id)

        # Assert
        mock_language_repo.delete.assert_called_once_with(language_id)
        assert result is False
