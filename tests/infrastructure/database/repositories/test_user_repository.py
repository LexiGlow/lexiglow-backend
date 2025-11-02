#!/usr/bin/env python3
"""
Test script for User Repository implementation.

This script demonstrates and tests the SQLiteUserRepository implementation.
"""

import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from uuid import UUID
from sqlalchemy import create_engine

from app.domain.entities.user import User as UserEntity
from app.infrastructure.database.sqlite.models import Base, Language as LanguageModel
from app.infrastructure.database.repositories import SQLiteUserRepository

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def setup_test_database(db_path: Path):
    """Create test database with Language table populated."""
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)

    # Create test languages
    from sqlalchemy.orm import sessionmaker

    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        # Check if languages already exist
        existing = session.query(LanguageModel).first()
        if existing:
            logger.info("Languages already exist, skipping creation")
            return

        english = LanguageModel(
            id=str(uuid.uuid4()),
            name="English",
            code="en",
            nativeName="English",
            isActive=1,
        )

        russian = LanguageModel(
            id=str(uuid.uuid4()),
            name="Russian",
            code="ru",
            nativeName="Русский",
            isActive=1,
        )

        session.add_all([english, russian])
        session.commit()
        logger.info("Created test languages")


def test_create_user(repo: SQLiteUserRepository, lang_id: str):
    """Test creating a new user."""
    logger.info("Testing user creation...")

    user = UserEntity(
        id=UUID(str(uuid.uuid4())),
        email="john.doe@example.com",
        username="johndoe",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYuHwZU3Y4u",
        first_name="John",
        last_name="Doe",
        native_language_id=UUID(lang_id),
        current_language_id=UUID(lang_id),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        last_active_at=None,
    )

    created_user = repo.create(user)
    logger.info(f"✅ Created user: {created_user.username} (ID: {created_user.id})")

    return created_user


def test_get_by_id(repo: SQLiteUserRepository, user_id: UUID):
    """Test retrieving a user by ID."""
    logger.info("Testing get by ID...")

    user = repo.get_by_id(user_id)
    if user:
        logger.info(f"✅ Retrieved user: {user.username} ({user.email})")
    else:
        logger.error(f"❌ User not found with ID: {user_id}")

    return user


def test_get_by_email(repo: SQLiteUserRepository, email: str):
    """Test retrieving a user by email."""
    logger.info("Testing get by email...")

    user = repo.get_by_email(email)
    if user:
        logger.info(f"✅ Retrieved user by email: {user.username}")
    else:
        logger.error(f"❌ User not found with email: {email}")

    return user


def test_get_by_username(repo: SQLiteUserRepository, username: str):
    """Test retrieving a user by username."""
    logger.info("Testing get by username...")

    user = repo.get_by_username(username)
    if user:
        logger.info(f"✅ Retrieved user by username: {user.email}")
    else:
        logger.error(f"❌ User not found with username: {username}")

    return user


def test_email_exists(repo: SQLiteUserRepository, email: str):
    """Test checking if email exists."""
    logger.info("Testing email exists...")

    exists = repo.email_exists(email)
    logger.info(f"✅ Email '{email}' exists: {exists}")

    return exists


def test_username_exists(repo: SQLiteUserRepository, username: str):
    """Test checking if username exists."""
    logger.info("Testing username exists...")

    exists = repo.username_exists(username)
    logger.info(f"✅ Username '{username}' exists: {exists}")

    return exists


def test_get_all(repo: SQLiteUserRepository):
    """Test retrieving all users."""
    logger.info("Testing get all users...")

    users = repo.get_all(skip=0, limit=10)
    logger.info(f"✅ Retrieved {len(users)} users")

    for user in users:
        logger.info(f"  - {user.username} ({user.email})")

    return users


def test_update(repo: SQLiteUserRepository, user_id: UUID):
    """Test updating a user."""
    logger.info("Testing user update...")

    user = repo.get_by_id(user_id)
    if not user:
        logger.error("❌ User not found for update")
        return None

    # Update user data
    user.first_name = "Jonathan"
    user.email = "jonathan.doe@example.com"

    updated_user = repo.update(user_id, user)
    if updated_user:
        logger.info(f"✅ Updated user: {updated_user.first_name} ({updated_user.email})")
    else:
        logger.error("❌ User update failed")

    return updated_user


def test_update_last_active(repo: SQLiteUserRepository, user_id: UUID):
    """Test updating last active timestamp."""
    logger.info("Testing update last active...")

    success = repo.update_last_active(user_id)
    if success:
        logger.info("✅ Updated last active timestamp")

        # Verify update
        user = repo.get_by_id(user_id)
        if user and user.last_active_at:
            logger.info(f"  Last active: {user.last_active_at}")
    else:
        logger.error("❌ Failed to update last active")

    return success


def test_exists(repo: SQLiteUserRepository, user_id: UUID):
    """Test checking if user exists."""
    logger.info("Testing user exists...")

    exists = repo.exists(user_id)
    logger.info(f"✅ User {user_id} exists: {exists}")

    return exists


def test_delete(repo: SQLiteUserRepository, user_id: UUID):
    """Test deleting a user."""
    logger.info("Testing user deletion...")

    success = repo.delete(user_id)
    if success:
        logger.info(f"✅ Deleted user with ID: {user_id}")

        # Verify deletion
        user = repo.get_by_id(user_id)
        if user is None:
            logger.info("  Verified: User no longer exists")
        else:
            logger.error("  Error: User still exists after deletion!")
    else:
        logger.error("❌ User deletion failed")

    return success


def main():
    """Run all repository tests."""
    logger.info("=" * 60)
    logger.info("User Repository Implementation Tests")
    logger.info("=" * 60)

    try:
        # Setup test database
        db_path = Path("/tmp/test_user_repository.db")
        setup_test_database(db_path)

        # Create repository instance
        repo = SQLiteUserRepository(str(db_path))

        # Get language ID for testing
        engine = create_engine(f"sqlite:///{db_path}")
        from sqlalchemy.orm import sessionmaker

        SessionLocal = sessionmaker(bind=engine)
        with SessionLocal() as session:
            lang = session.query(LanguageModel).first()
            lang_id = lang.id

        # Test CRUD operations
        print()
        created_user = test_create_user(repo, lang_id)

        print()
        test_get_by_id(repo, created_user.id)

        print()
        test_get_by_email(repo, created_user.email)

        print()
        test_get_by_username(repo, created_user.username)

        print()
        test_email_exists(repo, created_user.email)
        test_email_exists(repo, "nonexistent@example.com")

        print()
        test_username_exists(repo, created_user.username)
        test_username_exists(repo, "nonexistent_user")

        print()
        test_get_all(repo)

        print()
        test_update(repo, created_user.id)

        print()
        test_update_last_active(repo, created_user.id)

        print()
        test_exists(repo, created_user.id)

        print()
        test_delete(repo, created_user.id)

        print()
        test_exists(repo, created_user.id)

        logger.info("=" * 60)
        logger.info("✅ All repository tests passed!")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

