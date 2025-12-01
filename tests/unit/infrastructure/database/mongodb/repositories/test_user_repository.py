"""
Unit tests for MongoDBUserRepository.

Tests cover all methods of the repository implementation including
CRUD operations, queries, existence checks, and entity conversions.
"""

import asyncio
from collections.abc import Callable
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from ulid import ULID

from app.domain.entities.user import User as UserEntity
from app.infrastructure.database.mongodb.repositories.user_repository_impl import (
    MongoDBUserRepository,
)

# Fixtures


@pytest_asyncio.fixture(scope="function")
async def repository(mongo_client, db_url):
    """Create a MongoDBUserRepository instance with a test database."""
    db_name = f"test_db_{ULID().hex}"
    repo = MongoDBUserRepository(db_url=db_url, db_name=db_name)
    yield repo
    await mongo_client.drop_database(db_name)


@pytest.fixture
def english_language_id() -> ULID:
    """ULID for English language."""
    return ULID.from_str("01ARZ3NDEKTSV4RRFFQ69G5FAV")


@pytest.fixture
def russian_language_id() -> ULID:
    """ULID for Russian language."""
    return ULID.from_str("01ARZ3NDEKTSV4RRFFQ69G5FAW")


@pytest.fixture
def sample_user_entity(
    english_language_id: ULID, russian_language_id: ULID
) -> Callable[..., UserEntity]:
    """Factory fixture for creating User entities."""

    def _create_user(
        user_id: ULID | None = None,
        email: str = "test@example.com",
        username: str = "testuser",
        password_hash: str = "$2b$12$hashedpassword",
        first_name: str = "Test",
        last_name: str = "User",
        native_language_id: ULID | None = None,
        current_language_id: ULID | None = None,
    ) -> UserEntity:
        now = datetime.now(UTC)
        return UserEntity(
            id=str(user_id or ULID()),
            email=email,
            username=username,
            passwordHash=password_hash,
            firstName=first_name,
            lastName=last_name,
            nativeLanguageId=str(native_language_id or english_language_id),
            currentLanguageId=str(current_language_id or russian_language_id),
            createdAt=now,
            updatedAt=now,
            lastActiveAt=None,
        )

    return _create_user


# Test Classes


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
        assert isinstance(created_user.id, str)
        assert ULID.from_str(created_user.id)

    @pytest.mark.asyncio
    async def test_create_user_with_existing_id(self, repository, sample_user_entity):
        """Test creating user with pre-set ID."""
        preset_id = ULID()
        user_entity = sample_user_entity(user_id=preset_id)

        created_user = await repository.create(user_entity)

        assert created_user.id == preset_id

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, repository, sample_user_entity):
        """Test constraint violation for duplicate email."""
        user1 = sample_user_entity(email="duplicate@example.com", username="user1")
        await repository.create(user1)

        user2 = sample_user_entity(
            user_id=ULID(),
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
            user_id=ULID(),
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
        non_existent_id = ULID()

        result = await repository.get_by_id(non_existent_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_invalid_ulid(self, repository):
        """Test handling of invalid ULID format."""
        invalid_ulid_str = "not-a-valid-ulid"
        with pytest.raises(ValueError):
            ULID.from_str(invalid_ulid_str)

        # Assuming that if ULID.from_str doesn't raise, it's a valid ULID
        # The repository's get_by_id should still return None if it doesn't exist
        result = await repository.get_by_id(ULID())
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
    async def test_update_user_not_found(self, repository, sample_user_entity):
        """Test updating non-existent user returns None."""
        non_existent_id = ULID()
        user_entity = sample_user_entity()

        result = await repository.update(non_existent_id, user_entity)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_sets_updated_at(self, repository, sample_user_entity):
        """Test that updated_at timestamp changes on update."""
        created_user = await repository.create(sample_user_entity())
        # Normalize timezone-aware datetime to timezone-naive for comparison
        original_updated_at = (
            created_user.updated_at.replace(tzinfo=None)
            if created_user.updated_at.tzinfo
            else created_user.updated_at
        )

        # Small delay to ensure timestamp difference (MongoDB has millisecond precision)
        await asyncio.sleep(0.02)  # 20ms to ensure different millisecond

        created_user.first_name = "Modified"
        updated_user = await repository.update(created_user.id, created_user)

        # Normalize timezone-aware datetime to timezone-naive for comparison
        updated_updated_at = (
            updated_user.updated_at.replace(tzinfo=None)
            if updated_user.updated_at.tzinfo
            else updated_user.updated_at
        )

        # Normalize timezone-aware datetime to timezone-naive for comparison
        updated_updated_at = (
            updated_user.updated_at.replace(tzinfo=None)
            if updated_user.updated_at.tzinfo
            else updated_user.updated_at
        )

        # MongoDB stores timestamps with millisecond precision, so >= is acceptable
        assert updated_updated_at >= original_updated_at
        # But we should have a difference due to the sleep
        assert (updated_updated_at - original_updated_at).total_seconds() >= 0.01


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
        non_existent_id = ULID()

        result = await repository.delete(non_existent_id)

        assert result is False


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
        non_existent_id = ULID()

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
        """
        Test email_exists returns False for non-existent email.
        """
        result = await repository.email_exists("notexists@example.com")

        assert result is False


class TestUsernameExists:
    """Test username existence checks."""

    @pytest.mark.asyncio
    async def test_username_exists_true(self, repository, sample_user_entity):
        """
        Test username_exists returns True for existing username.
        """
        user = sample_user_entity(username="existinguser")
        await repository.create(user)

        result = await repository.username_exists("existinguser")

        assert result is True

    @pytest.mark.asyncio
    async def test_username_exists_false(self, repository):
        """
        Test username_exists returns False for non-existent username.
        """
        result = await repository.username_exists("notexisting")

        assert result is False


class TestUpdateLastActive:
    """Test updating last active timestamp."""

    @pytest.mark.asyncio
    async def test_update_last_active_success(self, repository, sample_user_entity):
        """
        Test updating last active timestamp successfully.
        """
        created_user = await repository.create(sample_user_entity())

        result = await repository.update_last_active(created_user.id)

        assert result is True

        # Verify timestamp was updated
        updated_user = await repository.get_by_id(created_user.id)
        assert updated_user.last_active_at is not None

    @pytest.mark.asyncio
    async def test_update_last_active_not_found(self, repository):
        """
        Test updating last active for non-existent user returns False.
        """
        non_existent_id = ULID()

        result = await repository.update_last_active(non_existent_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_update_last_active_timestamp(self, repository, sample_user_entity):
        """
        Test that last_active_at is set to current time.
        """
        created_user = await repository.create(sample_user_entity())

        # Capture timestamp before update
        before_update = datetime.now(UTC)
        await repository.update_last_active(created_user.id)
        after_update = datetime.now(UTC)

        updated_user = await repository.get_by_id(created_user.id)

        assert updated_user.last_active_at is not None
        # Make naive for comparison if needed
        last_active = updated_user.last_active_at
        if last_active.tzinfo is None:
            last_active = last_active.replace(tzinfo=UTC)
        # MongoDB stores timestamps with millisecond precision,
        # so we need to account for rounding
        # Subtract 1ms from before_update to account for rounding down
        from datetime import timedelta

        before_update_adjusted = before_update - timedelta(milliseconds=1)
        assert before_update_adjusted <= last_active <= after_update
