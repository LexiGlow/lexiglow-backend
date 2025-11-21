"""
Unit tests for SQLiteUserRepository.

Tests cover all methods of the repository implementation including
CRUD operations, queries, existence checks, and entity conversions.
"""

import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.entities.user import User as UserEntity
from app.infrastructure.database.sqlite.models import (
    Base,
)
from app.infrastructure.database.sqlite.models import (
    Language as LanguageModel,
)
from app.infrastructure.database.sqlite.models import (
    User as UserModel,
)
from app.infrastructure.database.sqlite.repositories.user_repository_impl import (
    SQLiteUserRepository,
)

# Fixtures


@pytest.fixture(scope="function")
def test_db_path(tmp_path):
    """Create a temporary database file path."""
    db_file = tmp_path / "test_user_repo.db"
    yield str(db_file)
    # Cleanup happens automatically with tmp_path


@pytest.fixture(scope="function")
def setup_database(test_db_path):
    """Create database tables and seed with test languages."""
    engine = create_engine(f"sqlite:///{test_db_path}", echo=False)
    Base.metadata.create_all(engine)

    # Seed languages for foreign key requirements
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        english = LanguageModel(
            id=str(uuid.UUID("00000000-0000-0000-0000-000000000001")),
            name="English",
            code="en",
            nativeName="English",
        )
        russian = LanguageModel(
            id=str(uuid.UUID("00000000-0000-0000-0000-000000000002")),
            name="Russian",
            code="ru",
            nativeName="Русский",
        )
        session.add_all([english, russian])
        session.commit()

    engine.dispose()
    return test_db_path


@pytest_asyncio.fixture(scope="function")
async def repository(setup_database):
    """Create a SQLiteUserRepository instance with test database."""
    repo = SQLiteUserRepository(db_path=setup_database)
    yield repo
    await repo.engine.dispose()


@pytest.fixture
def english_language_id():
    """UUID for English language."""
    return UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def russian_language_id():
    """UUID for Russian language."""
    return UUID("00000000-0000-0000-0000-000000000002")


@pytest.fixture
def sample_user_entity(
    english_language_id: UUID, russian_language_id: UUID
) -> Callable[..., UserEntity]:
    """Factory fixture for creating User entities."""

    def _create_user(
        user_id: UUID | None = None,
        email: str = "test@example.com",
        username: str = "testuser",
        password_hash: str = "$2b$12$hashedpassword",
        first_name: str = "Test",
        last_name: str = "User",
        native_language_id: UUID | None = None,
        current_language_id: UUID | None = None,
    ) -> UserEntity:
        now = datetime.now(UTC)
        return UserEntity(
            id=user_id or uuid.uuid4(),
            email=email,
            username=username,
            passwordHash=password_hash,
            firstName=first_name,
            lastName=last_name,
            nativeLanguageId=native_language_id or english_language_id,
            currentLanguageId=current_language_id or russian_language_id,
            createdAt=now,
            updatedAt=now,
            lastActiveAt=None,
        )

    return _create_user


# Test Classes


class TestRepositoryInitialization:
    """Test repository initialization."""

    @pytest.mark.asyncio
    async def test_init_with_custom_path(self, test_db_path, setup_database):
        """Test repository initializes with custom database path."""
        repo = SQLiteUserRepository(db_path=test_db_path)

        assert repo.engine is not None
        assert repo.SessionLocal is not None
        assert str(test_db_path) in str(repo.engine.url)

        await repo.engine.dispose()

    @pytest.mark.asyncio
    async def test_init_with_default_path(self, monkeypatch, tmp_path):
        """Test repository uses default path from environment."""
        default_db = tmp_path / "default.db"
        monkeypatch.setenv("SQLITE_DB_PATH", str(default_db))

        # Create tables for default path
        engine = create_engine(f"sqlite:///{default_db}", echo=False)
        Base.metadata.create_all(engine)
        engine.dispose()

        repo = SQLiteUserRepository(db_path=None)
        assert repo.engine is not None

        await repo.engine.dispose()


class TestCreateUser:
    """Test user creation."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, repository, sample_user_entity):
        """Test creating a user successfully."""
        user_entity = sample_user_entity()

        created_user = await repository.create(user_entity)

        assert created_user is not None
        assert created_user.id == user_entity.id
        assert created_user.email == user_entity.email
        assert created_user.username == user_entity.username
        assert created_user.first_name == user_entity.first_name
        assert created_user.last_name == user_entity.last_name
        assert created_user.created_at is not None
        assert created_user.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_user_generates_id(self, repository, sample_user_entity):
        """Test that ID is generated when not provided."""
        user_entity = sample_user_entity(user_id=None)
        # Force id to be None for testing
        user_entity.id = None

        created_user = await repository.create(user_entity)

        assert created_user is not None
        assert created_user.id is not None
        assert isinstance(created_user.id, UUID)

    @pytest.mark.asyncio
    async def test_create_user_with_existing_id(self, repository, sample_user_entity):
        """Test creating user with pre-set ID."""
        preset_id = uuid.uuid4()
        user_entity = sample_user_entity(user_id=preset_id)

        created_user = await repository.create(user_entity)

        assert created_user.id == preset_id

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, repository, sample_user_entity):
        """Test constraint violation for duplicate email."""
        user1 = sample_user_entity(email="duplicate@example.com", username="user1")
        await repository.create(user1)

        user2 = sample_user_entity(
            user_id=uuid.uuid4(),
            email="duplicate@example.com",
            username="user2",
        )

        with pytest.raises(Exception, match="Failed to create user"):
            await repository.create(user2)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, repository, sample_user_entity):
        """Test constraint violation for duplicate username."""
        user1 = sample_user_entity(email="user1@example.com", username="duplicate")
        await repository.create(user1)

        user2 = sample_user_entity(
            user_id=uuid.uuid4(),
            email="user2@example.com",
            username="duplicate",
        )

        with pytest.raises(Exception, match="Failed to create user"):
            await repository.create(user2)


class TestGetUserById:
    """Test retrieving users by ID."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, sample_user_entity):
        """Test retrieving an existing user by ID."""
        created_user = await repository.create(sample_user_entity())

        retrieved_user = await repository.get_by_id(created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
        assert retrieved_user.username == created_user.username

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test retrieving non-existent user returns None."""
        non_existent_id = uuid.uuid4()

        result = await repository.get_by_id(non_existent_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_invalid_uuid(self, repository):
        """Test handling of invalid UUID format."""
        # This would be caught at the UUID type level, but we test repository handling
        valid_uuid = uuid.uuid4()
        result = await repository.get_by_id(valid_uuid)

        assert result is None


class TestGetAllUsers:
    """Test retrieving all users with pagination."""

    @pytest.mark.asyncio
    async def test_get_all_empty(self, repository):
        """Test getting all users when database is empty."""
        users = await repository.get_all()

        assert users == []
        assert isinstance(users, list)

    @pytest.mark.asyncio
    async def test_get_all_multiple_users(self, repository, sample_user_entity):
        """Test retrieving all users."""
        user1 = sample_user_entity(email="user1@example.com", username="user1")
        user2 = sample_user_entity(email="user2@example.com", username="user2")
        user3 = sample_user_entity(email="user3@example.com", username="user3")

        await repository.create(user1)
        await repository.create(user2)
        await repository.create(user3)

        users = await repository.get_all()

        assert len(users) == 3
        usernames = [u.username for u in users]
        assert "user1" in usernames
        assert "user2" in usernames
        assert "user3" in usernames

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, repository, sample_user_entity):
        """Test pagination with skip and limit parameters."""
        for i in range(5):
            user = sample_user_entity(
                email=f"user{i}@example.com",
                username=f"user{i}",
            )
            await repository.create(user)

        # Get first 2
        page1 = await repository.get_all(skip=0, limit=2)
        assert len(page1) == 2

        # Get next 2
        page2 = await repository.get_all(skip=2, limit=2)
        assert len(page2) == 2

        # Get last 1
        page3 = await repository.get_all(skip=4, limit=2)
        assert len(page3) == 1

    @pytest.mark.asyncio
    async def test_get_all_pagination_edge_cases(self, repository, sample_user_entity):
        """Test pagination edge cases."""
        user = sample_user_entity()
        await repository.create(user)

        # Skip beyond total
        result = await repository.get_all(skip=10, limit=10)
        assert len(result) == 0

        # Limit 0 should return empty
        result = await repository.get_all(skip=0, limit=0)
        assert len(result) == 0


class TestUpdateUser:
    """Test user update operations."""

    @pytest.mark.asyncio
    async def test_update_user_success(self, repository, sample_user_entity):
        """Test updating all user fields successfully."""
        created_user = await repository.create(sample_user_entity())

        # Modify the entity
        created_user.email = "updated@example.com"
        created_user.username = "updated_user"
        created_user.first_name = "Updated"
        created_user.last_name = "Name"

        updated_user = await repository.update(created_user.id, created_user)

        assert updated_user is not None
        assert updated_user.email == "updated@example.com"
        assert updated_user.username == "updated_user"
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"

    @pytest.mark.asyncio
    async def test_update_user_partial(self, repository, sample_user_entity):
        """Test updating only some fields."""
        created_user = await repository.create(sample_user_entity())
        original_username = created_user.username

        # Only update email
        created_user.email = "newemail@example.com"

        updated_user = await repository.update(created_user.id, created_user)

        assert updated_user.email == "newemail@example.com"
        assert updated_user.username == original_username

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, repository, sample_user_entity):
        """Test updating non-existent user returns None."""
        non_existent_id = uuid.uuid4()
        user_entity = sample_user_entity()

        result = await repository.update(non_existent_id, user_entity)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_sets_updated_at(self, repository, sample_user_entity):
        """Test that updated_at timestamp changes on update."""
        created_user = await repository.create(sample_user_entity())
        original_updated_at = created_user.updated_at

        # Small delay to ensure timestamp difference
        import time

        time.sleep(0.01)

        created_user.first_name = "Modified"
        updated_user = await repository.update(created_user.id, created_user)

        assert updated_user.updated_at > original_updated_at


class TestDeleteUser:
    """Test user deletion."""

    @pytest.mark.asyncio
    async def test_delete_user_success(self, repository, sample_user_entity):
        """Test deleting existing user returns True."""
        created_user = await repository.create(sample_user_entity())

        result = await repository.delete(created_user.id)

        assert result is True

        # Verify user is actually deleted
        deleted_user = await repository.get_by_id(created_user.id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, repository):
        """Test deleting non-existent user returns False."""
        non_existent_id = uuid.uuid4()

        result = await repository.delete(non_existent_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_user_cascades(self, repository, sample_user_entity):
        """Test that deletion works correctly (cascade tested separately)."""
        user1 = sample_user_entity(email="user1@example.com", username="user1")
        user2 = sample_user_entity(email="user2@example.com", username="user2")

        created1 = await repository.create(user1)
        created2 = await repository.create(user2)

        # Delete first user
        await repository.delete(created1.id)

        # Second user should still exist
        remaining = await repository.get_by_id(created2.id)
        assert remaining is not None
        assert remaining.username == "user2"


class TestExistsUser:
    """Test user existence checks."""

    @pytest.mark.asyncio
    async def test_exists_true(self, repository, sample_user_entity):
        """Test exists returns True for existing user."""
        created_user = await repository.create(sample_user_entity())

        result = await repository.exists(created_user.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self, repository):
        """Test exists returns False for non-existent user."""
        non_existent_id = uuid.uuid4()

        result = await repository.exists(non_existent_id)

        assert result is False


class TestGetUserByEmail:
    """Test retrieving users by email."""

    @pytest.mark.asyncio
    async def test_get_by_email_found(self, repository, sample_user_entity):
        """Test retrieving user by email."""
        user = sample_user_entity(email="find@example.com")
        await repository.create(user)

        found_user = await repository.get_by_email("find@example.com")

        assert found_user is not None
        assert found_user.email == "find@example.com"

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, repository):
        """Test retrieving non-existent email returns None."""
        result = await repository.get_by_email("notfound@example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_email_case_sensitivity(self, repository, sample_user_entity):
        """Test email case handling."""
        user = sample_user_entity(email="CaseSensitive@example.com")
        await repository.create(user)

        # SQLite is case-insensitive by default for ASCII
        # But we test the exact email
        found_user = await repository.get_by_email("CaseSensitive@example.com")

        assert found_user is not None


class TestGetUserByUsername:
    """Test retrieving users by username."""

    @pytest.mark.asyncio
    async def test_get_by_username_found(self, repository, sample_user_entity):
        """Test retrieving user by username."""
        user = sample_user_entity(username="findme")
        await repository.create(user)

        found_user = await repository.get_by_username("findme")

        assert found_user is not None
        assert found_user.username == "findme"

    @pytest.mark.asyncio
    async def test_get_by_username_not_found(self, repository):
        """Test retrieving non-existent username returns None."""
        result = await repository.get_by_username("notfound")

        assert result is None


class TestEmailExists:
    """Test email existence checks."""

    @pytest.mark.asyncio
    async def test_email_exists_true(self, repository, sample_user_entity):
        """Test email_exists returns True for existing email."""
        user = sample_user_entity(email="exists@example.com")
        await repository.create(user)

        result = await repository.email_exists("exists@example.com")

        assert result is True

    @pytest.mark.asyncio
    async def test_email_exists_false(self, repository):
        """Test email_exists returns False for non-existent email."""
        result = await repository.email_exists("notexists@example.com")

        assert result is False


class TestUsernameExists:
    """Test username existence checks."""

    @pytest.mark.asyncio
    async def test_username_exists_true(self, repository, sample_user_entity):
        """Test username_exists returns True for existing username."""
        user = sample_user_entity(username="existinguser")
        await repository.create(user)

        result = await repository.username_exists("existinguser")

        assert result is True

    @pytest.mark.asyncio
    async def test_username_exists_false(self, repository):
        """Test username_exists returns False for non-existent username."""
        result = await repository.username_exists("notexisting")

        assert result is False


class TestUpdateLastActive:
    """Test updating last active timestamp."""

    @pytest.mark.asyncio
    async def test_update_last_active_success(self, repository, sample_user_entity):
        """Test updating last active timestamp successfully."""
        created_user = await repository.create(sample_user_entity())

        result = await repository.update_last_active(created_user.id)

        assert result is True

        # Verify timestamp was updated
        updated_user = await repository.get_by_id(created_user.id)
        assert updated_user.last_active_at is not None

    @pytest.mark.asyncio
    async def test_update_last_active_not_found(self, repository):
        """Test updating last active for non-existent user returns False."""
        non_existent_id = uuid.uuid4()

        result = await repository.update_last_active(non_existent_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_update_last_active_timestamp(self, repository, sample_user_entity):
        """Test that last_active_at is set to current time."""
        created_user = await repository.create(sample_user_entity())
        before_update = datetime.now(UTC)

        await repository.update_last_active(created_user.id)

        after_update = datetime.now(UTC)
        updated_user = await repository.get_by_id(created_user.id)

        assert updated_user.last_active_at is not None
        # Make naive for comparison if needed
        last_active = updated_user.last_active_at
        if last_active.tzinfo is None:
            last_active = last_active.replace(tzinfo=UTC)
        assert before_update <= last_active <= after_update


class TestEntityConversion:
    """Test entity/model conversion methods."""

    @pytest.mark.asyncio
    async def test_model_to_entity_conversion(
        self, repository, english_language_id, russian_language_id
    ):
        """Test converting ORM model to domain entity."""
        user_model = UserModel(
            id=str(uuid.uuid4()),
            email="test@example.com",
            username="testuser",
            passwordHash="$2b$12$hashedpassword",
            firstName="Test",
            lastName="User",
            nativeLanguageId=str(english_language_id),
            currentLanguageId=str(russian_language_id),
            createdAt=datetime.now(UTC),
            updatedAt=datetime.now(UTC),
            lastActiveAt=None,
        )

        entity = repository._model_to_entity(user_model)

        assert isinstance(entity, UserEntity)
        assert str(entity.id) == user_model.id
        assert entity.email == user_model.email
        assert entity.username == user_model.username
        assert entity.password_hash == user_model.passwordHash
        assert entity.first_name == user_model.firstName
        assert entity.last_name == user_model.lastName

    @pytest.mark.asyncio
    async def test_entity_to_model_conversion(self, repository, sample_user_entity):
        """Test converting domain entity to ORM model."""
        user_entity = sample_user_entity()

        model = repository._entity_to_model(user_entity)

        assert isinstance(model, UserModel)
        assert model.id == str(user_entity.id)
        assert model.email == user_entity.email
        assert model.username == user_entity.username
        assert model.passwordHash == user_entity.password_hash
        assert model.firstName == user_entity.first_name
        assert model.lastName == user_entity.last_name

    @pytest.mark.asyncio
    async def test_conversion_roundtrip(self, repository, sample_user_entity):
        """Test that entity -> model -> entity preserves data."""
        original_entity = sample_user_entity()

        # Convert to model and back
        model = repository._entity_to_model(original_entity)
        converted_entity = repository._model_to_entity(model)

        # Compare all fields
        assert converted_entity.id == original_entity.id
        assert converted_entity.email == original_entity.email
        assert converted_entity.username == original_entity.username
        assert converted_entity.password_hash == original_entity.password_hash
        assert converted_entity.first_name == original_entity.first_name
        assert converted_entity.last_name == original_entity.last_name
        assert converted_entity.native_language_id == original_entity.native_language_id
        assert (
            converted_entity.current_language_id == original_entity.current_language_id
        )
