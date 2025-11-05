"""
Unit tests for the UserService.

These tests mock the IUserRepository to test the service's business logic in isolation.
"""

import pytest
from unittest.mock import Mock, patch, ANY
from uuid import UUID, uuid4
from datetime import datetime

from app.application.services.user_service import UserService
from app.domain.interfaces.user_repository import IUserRepository
from app.domain.entities.user import User as UserEntity
from app.presentation.schemas.user_schema import UserCreate, UserUpdate, UserResponse


@pytest.fixture
def mock_user_repo() -> Mock:
    """Provides a mock user repository."""
    return Mock(spec=IUserRepository)


@pytest.fixture
def user_service(mock_user_repo: Mock) -> UserService:
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
        first_name="Test",
        last_name="User",
        native_language_id=uuid4(),
        current_language_id=uuid4(),
    )


@pytest.fixture
def sample_user_entity(sample_user_id: UUID) -> UserEntity:
    """Provides a sample UserEntity object."""
    now = datetime.utcnow()
    return UserEntity(
        id=sample_user_id,
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        native_language_id=uuid4(),
        current_language_id=uuid4(),
        created_at=now,
        updated_at=now,
    )


class TestUserService:
    """Test suite for the UserService class."""

    def test_create_user_success(
        self, user_service: UserService, mock_user_repo: Mock, sample_user_create: UserCreate
    ):
        """Test Case 2.1: Successful user creation."""
        # Arrange
        mock_user_repo.email_exists.return_value = False
        mock_user_repo.username_exists.return_value = False
        mock_user_repo.create.return_value = UserEntity(
            id=uuid4(), password_hash="hashed_password", **sample_user_create.model_dump(exclude={"password"})
        )

        # Act
        result = user_service.create_user(sample_user_create)

        # Assert
        mock_user_repo.email_exists.assert_called_once_with(sample_user_create.email)
        mock_user_repo.username_exists.assert_called_once_with(sample_user_create.username)
        mock_user_repo.create.assert_called_once()

        created_entity_arg = mock_user_repo.create.call_args[0][0]
        assert isinstance(created_entity_arg, UserEntity)
        assert created_entity_arg.email == sample_user_create.email
        assert created_entity_arg.password_hash != sample_user_create.password

        assert isinstance(result, UserResponse)
        assert result.email == sample_user_create.email

    def test_create_user_email_exists(
        self, user_service: UserService, mock_user_repo: Mock, sample_user_create: UserCreate
    ):
        """Test Case 2.2: Fail on existing email."""
        # Arrange
        mock_user_repo.email_exists.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="Email .* is already registered"):
            user_service.create_user(sample_user_create)

        mock_user_repo.email_exists.assert_called_once_with(sample_user_create.email)
        mock_user_repo.username_exists.assert_not_called()
        mock_user_repo.create.assert_not_called()

    def test_create_user_username_exists(
        self, user_service: UserService, mock_user_repo: Mock, sample_user_create: UserCreate
    ):
        """Test Case 2.3: Fail on existing username."""
        # Arrange
        mock_user_repo.email_exists.return_value = False
        mock_user_repo.username_exists.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="Username .* is already taken"):
            user_service.create_user(sample_user_create)

        mock_user_repo.username_exists.assert_called_once_with(sample_user_create.username)
        mock_user_repo.create.assert_not_called()

    def test_password_hashing_bcrypt_format(
        self, user_service: UserService, mock_user_repo: Mock
    ):
        """Test Case 2.4: Verify bcrypt password hashing format."""
        # Arrange
        user_create = UserCreate(
            email="hash@example.com",
            username="hashuser",
            password="PlainPassword123!",
            first_name="Hash",
            last_name="Test",
            native_language_id=uuid4(),
            current_language_id=uuid4(),
        )
        mock_user_repo.email_exists.return_value = False
        mock_user_repo.username_exists.return_value = False
        
        # Create a return entity with proper password hash
        mock_user_repo.create.return_value = UserEntity(
            id=uuid4(),
            email=user_create.email,
            username=user_create.username,
            password_hash="$2b$12$somehashvalue",
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            native_language_id=user_create.native_language_id,
            current_language_id=user_create.current_language_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        # Act
        user_service.create_user(user_create)
        
        # Assert
        entity = mock_user_repo.create.call_args[0][0]
        assert entity.password_hash.startswith("$2b$")  # bcrypt prefix
        assert len(entity.password_hash) == 60  # bcrypt fixed length
        assert entity.password_hash != user_create.password

    def test_create_user_repository_error(
        self, user_service: UserService, mock_user_repo: Mock, sample_user_create: UserCreate
    ):
        """Test Case 2.5: Handle repository exceptions during creation."""
        # Arrange
        mock_user_repo.email_exists.return_value = False
        mock_user_repo.username_exists.return_value = False
        mock_user_repo.create.side_effect = Exception("Database connection failed")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database connection failed"):
            user_service.create_user(sample_user_create)
        
        # Verify validation was performed before error
        mock_user_repo.email_exists.assert_called_once()
        mock_user_repo.username_exists.assert_called_once()

    def test_get_user_success(
        self, user_service: UserService, mock_user_repo: Mock, sample_user_entity: UserEntity
    ):
        """Test Case 3.1: Get existing user."""
        # Arrange
        mock_user_repo.get_by_id.return_value = sample_user_entity

        # Act
        result = user_service.get_user(sample_user_entity.id)

        # Assert
        mock_user_repo.get_by_id.assert_called_once_with(sample_user_entity.id)
        assert isinstance(result, UserResponse)
        assert result.id == sample_user_entity.id

    def test_get_user_not_found(self, user_service: UserService, mock_user_repo: Mock):
        """Test Case 3.2: Get non-existent user."""
        # Arrange
        user_id = uuid4()
        mock_user_repo.get_by_id.return_value = None

        # Act
        result = user_service.get_user(user_id)

        # Assert
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        assert result is None

    def test_get_all_users(
        self, user_service: UserService, mock_user_repo: Mock, sample_user_entity: UserEntity
    ):
        """Test Case 4.1: Get all users."""
        # Arrange
        mock_user_repo.get_all.return_value = [sample_user_entity]

        # Act
        results = user_service.get_all_users(skip=5, limit=50)

        # Assert
        mock_user_repo.get_all.assert_called_once_with(skip=5, limit=50)
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0].id == sample_user_entity.id

    def test_get_all_users_empty(self, user_service: UserService, mock_user_repo: Mock):
        """Test Case 4.2: Get all users when none exist."""
        # Arrange
        mock_user_repo.get_all.return_value = []

        # Act
        results = user_service.get_all_users()

        # Assert
        mock_user_repo.get_all.assert_called_once()
        assert results == []

    def test_get_all_users_pagination_params(
        self, user_service: UserService, mock_user_repo: Mock
    ):
        """Test Case 4.3: Verify pagination parameters are passed correctly."""
        # Arrange
        mock_user_repo.get_all.return_value = []
        
        # Act - Test with explicit parameters
        user_service.get_all_users(skip=10, limit=25)
        
        # Assert
        mock_user_repo.get_all.assert_called_with(skip=10, limit=25)
        
        # Act - Test with defaults
        mock_user_repo.get_all.reset_mock()
        user_service.get_all_users()
        
        # Assert defaults are used
        call_kwargs = mock_user_repo.get_all.call_args[1]
        assert call_kwargs['skip'] == 0
        assert call_kwargs['limit'] == 100

    def test_update_user_success(
        self, user_service: UserService, mock_user_repo: Mock, sample_user_entity: UserEntity
    ):
        """Test Case 5.1: Successful update."""
        # Arrange
        user_id = sample_user_entity.id
        update_data = UserUpdate(first_name="UpdatedName")

        mock_user_repo.get_by_id.return_value = sample_user_entity
        # The updated entity will have a new `updated_at` time
        updated_entity = sample_user_entity.model_copy()
        updated_entity.first_name = "UpdatedName"
        updated_entity.updated_at = datetime.utcnow()
        mock_user_repo.update.return_value = updated_entity

        # Act
        result = user_service.update_user(user_id, update_data)

        # Assert
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_user_repo.update.assert_called_once()

        update_arg = mock_user_repo.update.call_args[0][1]
        assert update_arg.first_name == "UpdatedName"
        assert update_arg.password_hash == sample_user_entity.password_hash # Ensure password not changed
        assert update_arg.updated_at > sample_user_entity.updated_at

        assert result.first_name == "UpdatedName"

    def test_update_user_not_found(self, user_service: UserService, mock_user_repo: Mock):
        """Test Case 5.2: Attempt to update a non-existent user."""
        # Arrange
        user_id = uuid4()
        update_data = UserUpdate(first_name="UpdatedName")
        mock_user_repo.get_by_id.return_value = None

        # Act
        result = user_service.update_user(user_id, update_data)

        # Assert
        assert result is None
        mock_user_repo.update.assert_not_called()

    def test_update_user_email_conflict(
        self, user_service: UserService, mock_user_repo: Mock, sample_user_entity: UserEntity
    ):
        """Test Case 5.3: Fail on email conflict."""
        # Arrange
        update_data = UserUpdate(email="conflict@example.com")
        mock_user_repo.get_by_id.return_value = sample_user_entity
        mock_user_repo.email_exists.return_value = True

        # Act & Assert
        with pytest.raises(ValueError, match="Email .* is already registered"):
            user_service.update_user(sample_user_entity.id, update_data)

        mock_user_repo.email_exists.assert_called_once_with("conflict@example.com")
        mock_user_repo.update.assert_not_called()

    def test_update_user_username_conflict(
        self, user_service: UserService, mock_user_repo: Mock, sample_user_entity: UserEntity
    ):
        """Test Case 5.4: Fail on username conflict during update."""
        # Arrange
        update_data = UserUpdate(username="existinguser")
        mock_user_repo.get_by_id.return_value = sample_user_entity
        mock_user_repo.username_exists.return_value = True
        
        # Act & Assert
        with pytest.raises(ValueError, match="Username .* is already taken"):
            user_service.update_user(sample_user_entity.id, update_data)
        
        mock_user_repo.username_exists.assert_called_once_with("existinguser")
        mock_user_repo.update.assert_not_called()

    def test_update_user_no_changes(
        self, user_service: UserService, mock_user_repo: Mock, sample_user_entity: UserEntity
    ):
        """Test Case 5.5: Update user with no field changes."""
        # Arrange
        update_data = UserUpdate()  # All fields None
        mock_user_repo.get_by_id.return_value = sample_user_entity
        
        updated_entity = sample_user_entity.model_copy()
        updated_entity.updated_at = datetime.utcnow()
        mock_user_repo.update.return_value = updated_entity
        
        # Act
        result = user_service.update_user(sample_user_entity.id, update_data)
        
        # Assert
        mock_user_repo.get_by_id.assert_called_once()
        mock_user_repo.update.assert_called_once()
        assert result is not None
        # Only updated_at should change
        assert result.email == sample_user_entity.email
        assert result.username == sample_user_entity.username

    def test_delete_user_success(self, user_service: UserService, mock_user_repo: Mock):
        """Test Case 6.1: Successful deletion."""
        # Arrange
        user_id = uuid4()
        mock_user_repo.delete.return_value = True

        # Act
        result = user_service.delete_user(user_id)

        # Assert
        mock_user_repo.delete.assert_called_once_with(user_id)
        assert result is True

    def test_delete_user_not_found(self, user_service: UserService, mock_user_repo: Mock):
        """Test Case 6.2: Attempt to delete a non-existent user."""
        # Arrange
        user_id = uuid4()
        mock_user_repo.delete.return_value = False

        # Act
        result = user_service.delete_user(user_id)

        # Assert
        mock_user_repo.delete.assert_called_once_with(user_id)
        assert result is False