#!/usr/bin/env python3
"""
Test script for SQLAlchemy ORM models.

This script demonstrates how to use the SQLAlchemy ORM models
to interact with the SQLite database.
"""

import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.database.sqlite.models import (
    Base,
    Language,
    User,
    UserLanguage,
    TextModel,
    UserVocabulary,
    UserVocabularyItem,
    TextTag,
    TextTagAssociation,
    get_all_models,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_test_database(db_path: Path):
    """
    Create a test database with tables.

    Args:
        db_path: Path to database file

    Returns:
        SQLAlchemy engine
    """
    # Create engine
    engine = create_engine(f"sqlite:///{db_path}", echo=False)

    # Create all tables
    Base.metadata.create_all(engine)
    logger.info(f"Created database with {len(get_all_models())} tables")

    return engine


def test_basic_crud():
    """Test basic CRUD operations with ORM models."""
    logger.info("Testing basic CRUD operations...")

    db_path = Path("/tmp/test_orm.db")
    engine = create_test_database(db_path)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        # Create languages
        english = Language(
            id=str(uuid.uuid4()),
            name="English",
            code="en",
            nativeName="English",
            isActive=1,
        )
        russian = Language(
            id=str(uuid.uuid4()),
            name="Russian",
            code="ru",
            nativeName="Русский",
            isActive=1,
        )

        session.add_all([english, russian])
        session.commit()
        logger.info("✅ Created 2 languages")

        # Create user
        user = User(
            id=str(uuid.uuid4()),
            email="john@example.com",
            username="johndoe",
            passwordHash="$2b$12$...",
            firstName="John",
            lastName="Doe",
            nativeLanguageId=english.id,
            currentLanguageId=russian.id,
        )

        session.add(user)
        session.commit()
        logger.info(f"✅ Created user: {user.username}")

        # Create user language association
        user_lang = UserLanguage(
            userId=user.id,
            languageId=russian.id,
            proficiencyLevel="A2",
            startedAt=datetime.utcnow(),
        )

        session.add(user_lang)
        session.commit()
        logger.info("✅ Created user-language association")

        # Query data using relationships
        queried_user = session.query(User).filter_by(username="johndoe").first()
        logger.info(f"Queried user: {queried_user.username}")
        logger.info(f"  Native language: {queried_user.native_language.name}")
        logger.info(f"  Current language: {queried_user.current_language.name}")
        logger.info(f"  Learning languages: {len(queried_user.user_languages)}")

        # Update user
        queried_user.lastActiveAt = datetime.utcnow()
        session.commit()
        logger.info("✅ Updated user last active timestamp")

        # Delete user (cascade will delete related records)
        session.delete(queried_user)
        session.commit()
        logger.info("✅ Deleted user")

    logger.info("✅ Basic CRUD test passed")


def test_relationships():
    """Test model relationships."""
    logger.info("Testing model relationships...")

    db_path = Path("/tmp/test_orm_relations.db")
    engine = create_test_database(db_path)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        # Create base data
        english = Language(
            id=str(uuid.uuid4()),
            name="English",
            code="en",
            nativeName="English",
            isActive=1,
        )

        user = User(
            id=str(uuid.uuid4()),
            email="alice@example.com",
            username="alice",
            passwordHash="$2b$12$...",
            firstName="Alice",
            lastName="Smith",
            nativeLanguageId=english.id,
            currentLanguageId=english.id,
        )

        session.add_all([english, user])
        session.commit()

        # Create text with tags
        text = TextModel(
            id=str(uuid.uuid4()),
            title="Introduction to Python",
            content="Python is a high-level programming language...",
            languageId=english.id,
            authorId=user.id,
            proficiencyLevel="B1",
            wordCount=50,
            isPublic=1,
        )

        tag1 = TextTag(id=str(uuid.uuid4()), name="programming", description="Programming tutorials")
        tag2 = TextTag(id=str(uuid.uuid4()), name="education", description="Educational content")

        session.add_all([text, tag1, tag2])
        session.commit()

        # Create tag associations
        assoc1 = TextTagAssociation(textId=text.id, tagId=tag1.id)
        assoc2 = TextTagAssociation(textId=text.id, tagId=tag2.id)

        session.add_all([assoc1, assoc2])
        session.commit()

        # Query with relationships
        queried_text = session.query(TextModel).filter_by(id=text.id).first()
        logger.info(f"Text: {queried_text.title}")
        logger.info(f"  Author: {queried_text.author.username}")
        logger.info(f"  Language: {queried_text.language.name}")
        logger.info(f"  Tags: {len(queried_text.tag_associations)}")
        for assoc in queried_text.tag_associations:
            logger.info(f"    - {assoc.tag.name}")

        # Create vocabulary
        vocab = UserVocabulary(
            id=str(uuid.uuid4()),
            userId=user.id,
            languageId=english.id,
            name="My English Vocabulary",
        )

        session.add(vocab)
        session.commit()

        # Add vocabulary items
        item1 = UserVocabularyItem(
            id=str(uuid.uuid4()),
            userVocabularyId=vocab.id,
            term="function",
            lemma="function",
            partOfSpeech="NOUN",
            frequency=0.85,
            status="LEARNING",
            timesReviewed=5,
            confidenceLevel="A2",
        )

        item2 = UserVocabularyItem(
            id=str(uuid.uuid4()),
            userVocabularyId=vocab.id,
            term="variable",
            lemma="variable",
            partOfSpeech="NOUN",
            frequency=0.90,
            status="KNOWN",
            timesReviewed=10,
            confidenceLevel="B1",
        )

        session.add_all([item1, item2])
        session.commit()

        # Query vocabulary with items
        queried_vocab = session.query(UserVocabulary).filter_by(id=vocab.id).first()
        logger.info(f"Vocabulary: {queried_vocab.name}")
        logger.info(f"  User: {queried_vocab.user.username}")
        logger.info(f"  Language: {queried_vocab.language.name}")
        logger.info(f"  Items: {len(queried_vocab.items)}")
        for item in queried_vocab.items:
            logger.info(
                f"    - {item.term} ({item.partOfSpeech}): {item.status}, "
                f"reviewed {item.timesReviewed} times"
            )

    logger.info("✅ Relationships test passed")


def test_queries():
    """Test various query patterns."""
    logger.info("Testing query patterns...")

    db_path = Path("/tmp/test_orm_queries.db")
    engine = create_test_database(db_path)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        # Create test data
        english = Language(
            id=str(uuid.uuid4()),
            name="English",
            code="en",
            nativeName="English",
            isActive=1,
        )

        users_data = [
            ("alice", "alice@example.com", "Alice", "Smith"),
            ("bob", "bob@example.com", "Bob", "Johnson"),
            ("charlie", "charlie@example.com", "Charlie", "Brown"),
        ]

        users = []
        for username, email, first_name, last_name in users_data:
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                username=username,
                passwordHash="$2b$12$...",
                firstName=first_name,
                lastName=last_name,
                nativeLanguageId=english.id,
                currentLanguageId=english.id,
            )
            users.append(user)

        session.add(english)
        session.add_all(users)
        session.commit()

        # Query all users
        all_users = session.query(User).all()
        logger.info(f"All users: {len(all_users)}")

        # Filter query
        alice = session.query(User).filter_by(username="alice").first()
        logger.info(f"Found user by username: {alice.firstName} {alice.lastName}")

        # Filter with condition
        users_with_a = session.query(User).filter(User.firstName.startswith("A")).all()
        logger.info(f"Users with first name starting with 'A': {len(users_with_a)}")

        # Order by
        ordered_users = session.query(User).order_by(User.username).all()
        logger.info("Users ordered by username:")
        for user in ordered_users:
            logger.info(f"  - {user.username}")

        # Count
        user_count = session.query(User).count()
        logger.info(f"Total users: {user_count}")

        # Join query
        users_with_lang = (
            session.query(User, Language)
            .join(Language, User.nativeLanguageId == Language.id)
            .all()
        )
        logger.info(f"Users with their native language: {len(users_with_lang)}")
        for user, lang in users_with_lang:
            logger.info(f"  - {user.username}: {lang.name}")

    logger.info("✅ Query patterns test passed")


def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("SQLAlchemy ORM Models Tests")
    logger.info("=" * 60)

    try:
        test_basic_crud()
        print()
        test_relationships()
        print()
        test_queries()

        logger.info("=" * 60)
        logger.info("✅ All ORM tests passed!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

