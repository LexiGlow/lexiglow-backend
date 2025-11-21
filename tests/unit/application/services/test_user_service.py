"""
Unit tests for the UserService.

These tests mock the IUserRepository to test the service's business logic in isolation.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from app.application.dto.user_dto import UserCreate, UserResponse, UserUpdate
from app.application.services.user_service import UserService
from app.domain.entities.user import User as UserEntity
from app.domain.interfaces.user_repository import IUserRepository


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    """Provides a mock user repository."""
    return AsyncMock(spec=IUserRepository)


@pytest.fixture
def user_service(mock_user_repo: AsyncMock) -> UserService:
    """Provides a UserService instance with a mocked repository."""
    # Instantiate the service and then replace its repository with our mock
    return UserService(repository=mock_user_repo)


@pytest.fixture
def sample_user_id() -> UUID:
    """Provides a sample UUID for a user."""
    return uuid4()


@pytest.fixture
def sample_user_create() -> UserCreate:
    """Provides a sample UserCreate schema object."""
    return UserCreate(
        email="test@example.com",
        username="testuser",
        password="strongpassword123",
        firstName="Test",
        lastName="User",
        nativeLanguageId=uuid4(),
        currentLanguageId=uuid4(),
    )


@pytest.fixture
def sample_user_entity(sample_user_id: UUID) -> UserEntity:
    now = datetime.now(UTC)
    return UserEntity(
        id=sample_user_id,
        email="test@example.com",
        username="testuser",
        passwordHash="hashed_password",
        firstName="Test",
        lastName="User",
        nativeLanguageId=uuid4(),
        currentLanguageId=uuid4(),
        createdAt=now,
        updatedAt=now,
        lastActiveAt=None,
    )


class TestUserService:
    """Test suite for the UserService class."""

    @pytest.mark.asyncio
    async def test_create_user_success(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        sample_user_create: UserCreate,
    ) -> None:
        """Test Case 2.1: Successful user creation."""
        # Arrange
        mock_user_repo.email_exists.return_value = False
        mock_user_repo.username_exists.return_value = False
        mock_user_repo.create.return_value = UserEntity(
            id=uuid4(),
            passwordHash="hashed_password",
            **sample_user_create.model_dump(exclude={"password"}, by_alias=True),
        )

        # Act
        result = await user_service.create_user(sample_user_create)

        # Assert
        mock_user_repo.email_exists.assert_called_once_with(sample_user_create.email)
        mock_user_repo.username_exists.assert_called_once_with(
            sample_user_create.username
        )
        mock_user_repo.create.assert_called_once()

        created_entity_arg = mock_user_repo.create.call_args[0][0]
        assert isinstance(created_entity_arg, UserEntity)
        assert created_entity_arg.email == sample_user_create.email
        assert created_entity_arg.password_hash != sample_user_create.password

        assert isinstance(result, UserResponse)
        assert result.email == sample_user_create.email

    @pytest.mark.asyncio
    async def test_create_user_email_exists(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        sample_user_create: UserCreate,
    ) -> None:
        """Test Case 2.2: Fail on existing email."""
        # Arrange
        mock_user_repo.email_exists.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="Email .* is already registered"):
            await user_service.create_user(sample_user_create)

        mock_user_repo.email_exists.assert_called_once_with(sample_user_create.email)
        mock_user_repo.username_exists.assert_not_called()
        mock_user_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_user_username_exists(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        sample_user_create: UserCreate,
    ) -> None:
        """Test Case 2.3: Fail on existing username."""
        # Arrange
        mock_user_repo.email_exists.return_value = False
        mock_user_repo.username_exists.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="Username .* is already taken"):
            await user_service.create_user(sample_user_create)

        mock_user_repo.username_exists.assert_called_once_with(
            sample_user_create.username
        )
        mock_user_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_password_hashing_bcrypt_format(
        self, user_service: UserService, mock_user_repo: AsyncMock
    ) -> None:
        """Test Case 2.4: Verify bcrypt password hashing format."""
        # Arrange
        user_create = UserCreate(
            email="hash@example.com",
            username="hashuser",
            password="PlainPassword123!",
            firstName="Hash",
            lastName="Test",
            nativeLanguageId=uuid4(),
            currentLanguageId=uuid4(),
        )
        mock_user_repo.email_exists.return_value = False
        mock_user_repo.username_exists.return_value = False

        # Create a return entity with proper password hash
        now = datetime.now(UTC)
        mock_user_repo.create.return_value = UserEntity(
            id=uuid4(),
            email=user_create.email,
            username=user_create.username,
            passwordHash="$2b$12$somehashvalue",
            firstName=user_create.first_name,
            lastName=user_create.last_name,
            nativeLanguageId=user_create.native_language_id,
            currentLanguageId=user_create.current_language_id,
            createdAt=now,
            updatedAt=now,
            lastActiveAt=None,
        )

        # Act
        await user_service.create_user(user_create)

        # Assert
        entity = mock_user_repo.create.call_args[0][0]
        assert entity.password_hash.startswith("$2b$")  # bcrypt prefix
        assert len(entity.password_hash) == 60  # bcrypt fixed length
        assert entity.password_hash != user_create.password

    @pytest.mark.asyncio
    async def test_create_user_repository_error(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        sample_user_create: UserCreate,
    ) -> None:
        """Test Case 2.5: Handle repository exceptions during creation."""
        # Arrange
        mock_user_repo.email_exists.return_value = False
        mock_user_repo.username_exists.return_value = False
        mock_user_repo.create.side_effect = Exception("Database connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="Database connection failed"):
            await user_service.create_user(sample_user_create)

        # Verify validation was performed before error
        mock_user_repo.email_exists.assert_called_once()
        mock_user_repo.username_exists.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_success(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        sample_user_entity: UserEntity,
    ) -> None:
        """Test Case 3.1: Get existing user."""
        # Arrange
        mock_user_repo.get_by_id.return_value = sample_user_entity

        # Act
        assert sample_user_entity.id is not None
        result = await user_service.get_user(sample_user_entity.id)

        # Assert
        mock_user_repo.get_by_id.assert_called_once_with(sample_user_entity.id)
        assert isinstance(result, UserResponse)
        assert result.id == sample_user_entity.id

    @pytest.mark.asyncio
    async def test_get_user_not_found(
        self, user_service: UserService, mock_user_repo: AsyncMock
    ) -> None:
        """Test Case 3.2: Get non-existent user."""
        # Arrange
        user_id = uuid4()
        mock_user_repo.get_by_id.return_value = None

        # Act
        result = await user_service.get_user(user_id)

        # Assert
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_users(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        sample_user_entity: UserEntity,
    ) -> None:
        """Test Case 4.1: Get all users."""
        # Arrange
        mock_user_repo.get_all.return_value = [sample_user_entity]

        # Act
        results = await user_service.get_all_users(skip=5, limit=50)

        # Assert
        mock_user_repo.get_all.assert_called_once_with(skip=5, limit=50)
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0].id == sample_user_entity.id

    @pytest.mark.asyncio
    async def test_get_all_users_empty(
        self, user_service: UserService, mock_user_repo: AsyncMock
    ) -> None:
        """Test Case 4.2: Get all users when none exist."""
        # Arrange
        mock_user_repo.get_all.return_value = []

        # Act
        results = await user_service.get_all_users()

        # Assert
        mock_user_repo.get_all.assert_called_once()
        assert results == []

    @pytest.mark.asyncio
    async def test_get_all_users_pagination_params(
        self, user_service: UserService, mock_user_repo: AsyncMock
    ) -> None:
        """Test Case 4.3: Verify pagination parameters are passed correctly."""
        # Arrange
        mock_user_repo.get_all.return_value = []

        # Act - Test with explicit parameters
        await user_service.get_all_users(skip=10, limit=25)

        # Assert
        mock_user_repo.get_all.assert_called_with(skip=10, limit=25)

        # Act - Test with defaults
        mock_user_repo.get_all.reset_mock()
        await user_service.get_all_users()

        # Assert defaults are used
        call_kwargs = mock_user_repo.get_all.call_args[1]
        assert call_kwargs["skip"] == 0
        assert call_kwargs["limit"] == 100

    @pytest.mark.asyncio
    async def test_update_user_success(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        sample_user_entity: UserEntity,
    ) -> None:
        """Test Case 5.1: Successful update."""
        # Arrange
        assert sample_user_entity.id is not None
        user_id = sample_user_entity.id
        update_data = UserUpdate(
            firstName="UpdatedName",
            lastName=None,
            nativeLanguageId=None,
            currentLanguageId=None,
        )

        mock_user_repo.get_by_id.return_value = sample_user_entity

        # Create an expected updated entity to be returned by the mock repository
        expected_updated_entity = sample_user_entity.model_copy()
        if update_data.first_name is not None:
            expected_updated_entity.first_name = update_data.first_name
        expected_updated_entity.updated_at = datetime.now(
            UTC
        )  # This will be set by the service

        mock_user_repo.update.return_value = expected_updated_entity

        # Act
        result = await user_service.update_user(user_id, update_data)

        # Assert
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_user_repo.update.assert_called_once()

        update_arg = mock_user_repo.update.call_args[0][1]
        assert update_arg.first_name == "UpdatedName"
        assert (
            update_arg.password_hash == sample_user_entity.password_hash
        )  # Ensure password not changed
        assert update_arg.updated_at > sample_user_entity.updated_at

        assert result is not None
        assert result is not None
        assert result.first_name == "UpdatedName"

    @pytest.mark.asyncio
    async def test_update_user_not_found(
        self, user_service: UserService, mock_user_repo: AsyncMock
    ) -> None:
        """Test Case 5.2: Attempt to update a non-existent user."""
        # Arrange
        user_id = uuid4()
        update_data = UserUpdate(
            firstName="UpdatedName",
            lastName=None,
            nativeLanguageId=None,
            currentLanguageId=None,
        )
        mock_user_repo.get_by_id.return_value = None

        # Act
        result = await user_service.update_user(user_id, update_data)

        # Assert
        assert result is None
        mock_user_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_email_conflict(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        sample_user_entity: UserEntity,
    ) -> None:
        """Test Case 5.3: Fail on email conflict."""
        # Arrange
        update_data = UserUpdate(
            email="conflict@example.com",
            firstName=None,
            lastName=None,
            nativeLanguageId=None,
            currentLanguageId=None,
        )
        mock_user_repo.get_by_id.return_value = sample_user_entity
        mock_user_repo.email_exists.return_value = True

        # Act & Assert
        assert sample_user_entity.id is not None
        with pytest.raises(ValueError, match="Email .* is already registered"):
            await user_service.update_user(sample_user_entity.id, update_data)

        mock_user_repo.email_exists.assert_called_once_with("conflict@example.com")
        mock_user_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_username_conflict(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        sample_user_entity: UserEntity,
    ) -> None:
        """Test Case 5.4: Fail on username conflict during update."""
        # Arrange
        update_data = UserUpdate(
            username="existinguser",
            firstName=None,
            lastName=None,
            nativeLanguageId=None,
            currentLanguageId=None,
        )
        mock_user_repo.get_by_id.return_value = sample_user_entity
        mock_user_repo.username_exists.return_value = True

        # Act & Assert
        assert sample_user_entity.id is not None
        with pytest.raises(ValueError, match="Username .* is already taken"):
            await user_service.update_user(sample_user_entity.id, update_data)

        mock_user_repo.username_exists.assert_called_once_with("existinguser")
        mock_user_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_no_changes(
        self,
        user_service: UserService,
        mock_user_repo: AsyncMock,
        sample_user_entity: UserEntity,
    ) -> None:
        """Test Case 5.5: Update user with no field changes."""
        # Arrange
        update_data = UserUpdate(
            firstName=None,
            lastName=None,
            nativeLanguageId=None,
            currentLanguageId=None,
        )  # All fields None
        mock_user_repo.get_by_id.return_value = sample_user_entity

        updated_entity = sample_user_entity.model_copy()
        updated_entity.updated_at = datetime.now(UTC)
        mock_user_repo.update.return_value = updated_entity

        # Act
        assert sample_user_entity.id is not None
        result = await user_service.update_user(sample_user_entity.id, update_data)

        # Assert
        mock_user_repo.get_by_id.assert_called_once()
        mock_user_repo.update.assert_called_once()
        assert result is not None
        # Only updated_at should change
        assert result.email == sample_user_entity.email
        assert result.username == sample_user_entity.username

    @pytest.mark.asyncio
    async def test_delete_user_success(
        self, user_service: UserService, mock_user_repo: AsyncMock
    ) -> None:
        """Test Case 6.1: Successful deletion."""
        # Arrange
        user_id = uuid4()
        mock_user_repo.delete.return_value = True

        # Act
        result = await user_service.delete_user(user_id)

        # Assert
        mock_user_repo.delete.assert_called_once_with(user_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_user_not_found(
        self, user_service: UserService, mock_user_repo: AsyncMock
    ) -> None:
        """Test Case 6.2: Attempt to delete a non-existent user."""
        # Arrange
        user_id = uuid4()
        mock_user_repo.delete.return_value = False

        # Act
        result = await user_service.delete_user(user_id)

        # Assert
        mock_user_repo.delete.assert_called_once_with(user_id)
        assert result is False
