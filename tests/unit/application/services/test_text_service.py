"""
Unit tests for the TextService.

These tests mock the ITextRepository to test the service's business logic in isolation.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from app.application.dto.text_dto import TextCreate, TextResponse, TextUpdate
from app.application.services.text_service import TextService
from app.domain.entities.enums import ProficiencyLevel
from app.domain.entities.text import Text as TextEntity
from app.domain.interfaces.text_repository import ITextRepository


@pytest.fixture
def mock_text_repo() -> AsyncMock:
    """Provides a mock text repository."""
    return AsyncMock(spec=ITextRepository)


@pytest.fixture
def text_service(mock_text_repo: AsyncMock) -> TextService:
    """Provides a TextService instance with a mocked repository."""
    return TextService(repository=mock_text_repo)


@pytest.fixture
def sample_text_id() -> UUID:
    """Provides a sample UUID for a text."""
    return uuid4()


@pytest.fixture
def sample_text_create() -> TextCreate:
    """Provides a sample TextCreate schema object."""
    return TextCreate(
        title="Test Title",
        content="Test content.",
        languageId=uuid4(),
        userId=uuid4(),
        proficiencyLevel=ProficiencyLevel.A1,
        wordCount=2,
        isPublic=True,
        source="http://example.com",
    )


@pytest.fixture
def sample_text_entity(sample_text_id: UUID) -> TextEntity:
    now = datetime.now(UTC)
    return TextEntity(
        id=sample_text_id,
        title="Test Title",
        content="Test content.",
        languageId=uuid4(),
        userId=uuid4(),
        proficiencyLevel=ProficiencyLevel.A1,
        wordCount=2,
        isPublic=True,
        source="http://example.com",
        createdAt=now,
        updatedAt=now,
    )


class TestTextService:
    """Test suite for the TextService class."""

    @pytest.mark.asyncio
    async def test_create_text_success(
        self,
        text_service: TextService,
        mock_text_repo: AsyncMock,
        sample_text_create: TextCreate,
    ) -> None:
        """Test Case 2.1: Successful text creation."""
        # Arrange
        mock_text_repo.create.return_value = TextEntity(
            id=uuid4(),
            title=sample_text_create.title,
            content=sample_text_create.content,
            languageId=sample_text_create.language_id,
            userId=sample_text_create.user_id,
            proficiencyLevel=sample_text_create.proficiency_level,
            wordCount=sample_text_create.word_count,
            isPublic=sample_text_create.is_public,
            source=sample_text_create.source,
        )

        # Act
        result = await text_service.create_text(sample_text_create)

        # Assert
        mock_text_repo.create.assert_called_once()
        created_entity_arg = mock_text_repo.create.call_args[0][0]
        assert isinstance(created_entity_arg, TextEntity)
        assert created_entity_arg.title == sample_text_create.title
        assert isinstance(result, TextResponse)
        assert result.title == sample_text_create.title

    @pytest.mark.asyncio
    async def test_create_text_repository_error(
        self,
        text_service: TextService,
        mock_text_repo: AsyncMock,
        sample_text_create: TextCreate,
    ) -> None:
        """Test Case 2.2: Handle repository exceptions during creation."""
        # Arrange
        mock_text_repo.create.side_effect = Exception("Database connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="Database connection failed"):
            await text_service.create_text(sample_text_create)

        mock_text_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_text_success(
        self,
        text_service: TextService,
        mock_text_repo: AsyncMock,
        sample_text_entity: TextEntity,
    ) -> None:
        """Test Case 3.1: Get existing text."""
        # Arrange
        mock_text_repo.get_by_id.return_value = sample_text_entity

        # Act
        assert sample_text_entity.id is not None
        result = await text_service.get_text(sample_text_entity.id)

        # Assert
        mock_text_repo.get_by_id.assert_called_once_with(sample_text_entity.id)
        assert isinstance(result, TextResponse)
        assert result.id == sample_text_entity.id

    @pytest.mark.asyncio
    async def test_get_text_not_found(
        self, text_service: TextService, mock_text_repo: AsyncMock
    ) -> None:
        """Test Case 3.2: Get non-existent text."""
        # Arrange
        text_id = uuid4()
        mock_text_repo.get_by_id.return_value = None

        # Act
        result = await text_service.get_text(text_id)

        # Assert
        mock_text_repo.get_by_id.assert_called_once_with(text_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_texts_success(
        self,
        text_service: TextService,
        mock_text_repo: AsyncMock,
        sample_text_entity: TextEntity,
    ) -> None:
        """Test Case 4.1: Get all texts."""
        # Arrange
        mock_text_repo.get_all.return_value = [sample_text_entity]

        # Act
        results = await text_service.get_all_texts(skip=5, limit=50)

        # Assert
        mock_text_repo.get_all.assert_called_once_with(skip=5, limit=50)
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0].id == sample_text_entity.id

    @pytest.mark.asyncio
    async def test_get_all_texts_empty(
        self, text_service: TextService, mock_text_repo: AsyncMock
    ) -> None:
        """Test Case 4.2: Get all texts when none exist."""
        # Arrange
        mock_text_repo.get_all.return_value = []

        # Act
        results = await text_service.get_all_texts()

        # Assert
        mock_text_repo.get_all.assert_called_once()
        assert results == []

    @pytest.mark.asyncio
    async def test_get_all_texts_pagination_params(
        self, text_service: TextService, mock_text_repo: AsyncMock
    ) -> None:
        """Test Case 4.3: Verify pagination parameters are passed correctly."""
        # Arrange
        mock_text_repo.get_all.return_value = []

        # Act - Test with explicit parameters
        await text_service.get_all_texts(skip=10, limit=25)

        # Assert
        mock_text_repo.get_all.assert_called_with(skip=10, limit=25)

        # Act - Test with defaults
        mock_text_repo.get_all.reset_mock()
        await text_service.get_all_texts()

        # Assert defaults are used
        call_kwargs = mock_text_repo.get_all.call_args[1]
        assert call_kwargs["skip"] == 0
        assert call_kwargs["limit"] == 100

    @pytest.mark.asyncio
    async def test_update_text_success(
        self,
        text_service: TextService,
        mock_text_repo: AsyncMock,
        sample_text_entity: TextEntity,
    ) -> None:
        """Test Case 5.1: Successful update."""
        # Arrange
        assert sample_text_entity.id is not None
        text_id = sample_text_entity.id
        update_data = TextUpdate(
            title="Updated Title",
            content=None,
            languageId=None,
            proficiencyLevel=None,
            wordCount=None,
            isPublic=None,
            source=None,
        )

        mock_text_repo.get_by_id.return_value = sample_text_entity

        expected_updated_entity = sample_text_entity.model_copy()
        assert update_data.title is not None  # Ensure title is not None for mypy
        expected_updated_entity.title = update_data.title
        expected_updated_entity.updated_at = datetime.now(UTC)

        mock_text_repo.update.return_value = expected_updated_entity

        # Act
        result = await text_service.update_text(text_id, update_data)

        # Assert
        mock_text_repo.get_by_id.assert_called_once_with(text_id)
        mock_text_repo.update.assert_called_once()

        update_arg = mock_text_repo.update.call_args[0][1]
        assert update_arg.title == "Updated Title"
        assert update_arg.updated_at > sample_text_entity.updated_at

        assert result is not None
        assert result.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_text_not_found(
        self, text_service: TextService, mock_text_repo: AsyncMock
    ) -> None:
        """Test Case 5.2: Attempt to update a non-existent text."""
        # Arrange
        text_id = uuid4()
        update_data = TextUpdate(
            title="Updated Title",
            content=None,
            languageId=None,
            proficiencyLevel=None,
            wordCount=None,
            isPublic=None,
            source=None,
        )
        mock_text_repo.get_by_id.return_value = None

        # Act
        result = await text_service.update_text(text_id, update_data)

        # Assert
        assert result is None
        mock_text_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_text_no_changes(
        self,
        text_service: TextService,
        mock_text_repo: AsyncMock,
        sample_text_entity: TextEntity,
    ) -> None:
        """Test Case 5.3: Update text with no field changes."""
        # Arrange
        update_data = TextUpdate(
            title=None,
            content=None,
            languageId=None,
            proficiencyLevel=None,
            wordCount=None,
            isPublic=None,
            source=None,
        )
        mock_text_repo.get_by_id.return_value = sample_text_entity

        updated_entity = sample_text_entity.model_copy()
        updated_entity.updated_at = datetime.now(UTC)
        mock_text_repo.update.return_value = updated_entity

        # Act
        assert sample_text_entity.id is not None
        result = await text_service.update_text(sample_text_entity.id, update_data)

        # Assert
        mock_text_repo.get_by_id.assert_called_once()
        mock_text_repo.update.assert_called_once()
        assert result is not None
        # Only updated_at should change
        assert result.title == sample_text_entity.title
        assert result.content == sample_text_entity.content

    @pytest.mark.asyncio
    async def test_delete_text_success(
        self, text_service: TextService, mock_text_repo: AsyncMock
    ) -> None:
        """Test Case 6.1: Successful deletion."""
        # Arrange
        text_id = uuid4()
        mock_text_repo.delete.return_value = True

        # Act
        result = await text_service.delete_text(text_id)

        # Assert
        mock_text_repo.delete.assert_called_once_with(text_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_text_not_found(
        self, text_service: TextService, mock_text_repo: AsyncMock
    ) -> None:
        """Test Case 6.2: Attempt to delete a non-existent text."""
        # Arrange
        text_id = uuid4()
        mock_text_repo.delete.return_value = False

        # Act
        result = await text_service.delete_text(text_id)

        # Assert
        mock_text_repo.delete.assert_called_once_with(text_id)
        assert result is False
