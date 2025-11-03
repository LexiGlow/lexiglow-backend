"""
Unit tests for SQLAlchemy ORM models.

Tests cover CRUD operations, relationships, queries, and constraints
for all database models in the LexiGlow backend.
"""

import uuid
from datetime import datetime

import pytest
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
    get_model_by_table_name,
)


@pytest.fixture(scope="function")
def engine():
    """Create an in-memory SQLite database engine for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def session(engine):
    """Create a new database session for a test."""
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def english_language(session):
    """Create and return an English language record."""
    language = Language(
        id=str(uuid.uuid4()),
        name="English",
        code="en",
        nativeName="English",
        isActive=1,
    )
    session.add(language)
    session.commit()
    return language


@pytest.fixture
def russian_language(session):
    """Create and return a Russian language record."""
    language = Language(
        id=str(uuid.uuid4()),
        name="Russian",
        code="ru",
        nativeName="Русский",
        isActive=1,
    )
    session.add(language)
    session.commit()
    return language


@pytest.fixture
def test_user(session, english_language, russian_language):
    """Create and return a test user."""
    user = User(
        id=str(uuid.uuid4()),
        email="john@example.com",
        username="johndoe",
        passwordHash="$2b$12$hashedpassword",
        firstName="John",
        lastName="Doe",
        nativeLanguageId=english_language.id,
        currentLanguageId=russian_language.id,
    )
    session.add(user)
    session.commit()
    return user


# Language Model Tests


class TestLanguageModel:
    """Test cases for the Language model."""

    def test_create_language(self, session):
        """Test creating a new language."""
        language = Language(
            id=str(uuid.uuid4()),
            name="Spanish",
            code="es",
            nativeName="Español",
            isActive=1,
        )
        session.add(language)
        session.commit()

        queried_language = session.query(Language).filter_by(id=language.id).first()
        assert queried_language is not None
        assert queried_language.id == language.id
        assert queried_language.name == "Spanish"
        assert queried_language.code == "es"
        assert queried_language.nativeName == "Español"
        assert queried_language.isActive == 1
        assert queried_language.createdAt == language.createdAt
        

    def test_language_unique_code(self, session, english_language):
        """Test that language codes must be unique."""
        duplicate_language = Language(
            id=str(uuid.uuid4()),
            name="English US",
            code="en",  # Duplicate code
            nativeName="English",
            isActive=1,
        )
        session.add(duplicate_language)

        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            session.commit()

    def test_language_repr(self, english_language):
        """Test language string representation."""
        expected = f"<Language(id='{english_language.id}', code='en', name='English')>"
        assert repr(english_language) == expected


# User Model Tests


class TestUserModel:
    """Test cases for the User model."""

    def test_create_user(self, session, english_language, russian_language):
        """Test creating a new user."""
        user = User(
            id=str(uuid.uuid4()),
            email="alice@example.com",
            username="alice",
            passwordHash="$2b$12$hashedpassword",
            firstName="Alice",
            lastName="Smith",
            nativeLanguageId=english_language.id,
            currentLanguageId=russian_language.id,
        )
        session.add(user)
        session.commit()

        assert user.id is not None
        assert user.email == "alice@example.com"
        assert user.username == "alice"
        assert user.firstName == "Alice"
        assert user.lastName == "Smith"
        assert user.createdAt is not None
        assert user.updatedAt is not None

    def test_user_unique_email(self, session, test_user, russian_language):
        """Test that user emails must be unique."""
        duplicate_user = User(
            id=str(uuid.uuid4()),
            email=test_user.email,  # Duplicate email
            username="different",
            passwordHash="$2b$12$hashedpassword",
            firstName="Jane",
            lastName="Doe",
            nativeLanguageId=test_user.nativeLanguageId,
            currentLanguageId=russian_language.id,
        )
        session.add(duplicate_user)

        with pytest.raises(Exception):
            session.commit()

    def test_user_unique_username(self, session, test_user, russian_language):
        """Test that usernames must be unique."""
        duplicate_user = User(
            id=str(uuid.uuid4()),
            email="different@example.com",
            username=test_user.username,  # Duplicate username
            passwordHash="$2b$12$hashedpassword",
            firstName="Jane",
            lastName="Doe",
            nativeLanguageId=test_user.nativeLanguageId,
            currentLanguageId=russian_language.id,
        )
        session.add(duplicate_user)

        with pytest.raises(Exception):
            session.commit()

    def test_user_language_relationships(
        self, test_user, english_language, russian_language
    ):
        """Test user relationships with languages."""
        assert test_user.native_language.id == english_language.id
        assert test_user.current_language.id == russian_language.id
        assert test_user.native_language.name == "English"
        assert test_user.current_language.name == "Russian"

    def test_update_user_last_active(self, session, test_user):
        """Test updating user's last active timestamp."""
        now = datetime.utcnow()
        test_user.lastActiveAt = now
        session.commit()

        updated_user = session.query(User).filter_by(id=test_user.id).first()
        assert updated_user.lastActiveAt is not None
        assert updated_user.lastActiveAt.replace(microsecond=0) == now.replace(
            microsecond=0
        )

    def test_delete_user_cascade(self, session, test_user, russian_language):
        """Test that deleting a user cascades to related records."""
        # Create user language association
        user_lang = UserLanguage(
            userId=test_user.id,
            languageId=russian_language.id,
            proficiencyLevel="A2",
            startedAt=datetime.utcnow(),
        )
        session.add(user_lang)
        session.commit()

        user_id = test_user.id

        # Delete user
        session.delete(test_user)
        session.commit()

        # Verify user is deleted
        deleted_user = session.query(User).filter_by(id=user_id).first()
        assert deleted_user is None

        # Verify user language association is also deleted (cascade)
        deleted_user_lang = (
            session.query(UserLanguage).filter_by(userId=user_id).first()
        )
        assert deleted_user_lang is None

    def test_user_repr(self, test_user):
        """Test user string representation."""
        expected = (
            f"<User(id='{test_user.id}', username='johndoe', email='john@example.com')>"
        )
        assert repr(test_user) == expected


# UserLanguage Model Tests


class TestUserLanguageModel:
    """Test cases for the UserLanguage model."""

    def test_create_user_language(self, session, test_user, russian_language):
        """Test creating a user language association."""
        started_at = datetime.utcnow()
        user_lang = UserLanguage(
            userId=test_user.id,
            languageId=russian_language.id,
            proficiencyLevel="A2",
            startedAt=started_at,
        )
        session.add(user_lang)
        session.commit()

        assert user_lang.userId == test_user.id
        assert user_lang.languageId == russian_language.id
        assert user_lang.proficiencyLevel == "A2"
        assert user_lang.startedAt is not None
        assert user_lang.createdAt is not None

    def test_user_language_relationships(self, session, test_user, russian_language):
        """Test user language relationships."""
        user_lang = UserLanguage(
            userId=test_user.id,
            languageId=russian_language.id,
            proficiencyLevel="B1",
            startedAt=datetime.utcnow(),
        )
        session.add(user_lang)
        session.commit()

        assert user_lang.user.username == test_user.username
        assert user_lang.language.name == "Russian"

    def test_user_language_proficiency_levels(
        self, session, test_user, russian_language
    ):
        """Test valid proficiency levels."""
        valid_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]

        for level in valid_levels:
            user_lang = UserLanguage(
                userId=test_user.id,
                languageId=russian_language.id,
                proficiencyLevel=level,
                startedAt=datetime.utcnow(),
            )
            session.add(user_lang)
            # Clean up after each test
            session.rollback()

    def test_user_language_repr(self, session, test_user, russian_language):
        """Test user language string representation."""
        user_lang = UserLanguage(
            userId=test_user.id,
            languageId=russian_language.id,
            proficiencyLevel="A2",
            startedAt=datetime.utcnow(),
        )
        session.add(user_lang)
        session.commit()

        expected = f"<UserLanguage(userId='{test_user.id}', languageId='{russian_language.id}', level='A2')>"
        assert repr(user_lang) == expected


# Text Model Tests


class TestTextModel:
    """Test cases for the Text model."""

    def test_create_text(self, session, test_user, english_language):
        """Test creating a new text."""
        text = TextModel(
            id=str(uuid.uuid4()),
            title="Introduction to Python",
            content="Python is a high-level programming language...",
            languageId=english_language.id,
            authorId=test_user.id,
            proficiencyLevel="B1",
            wordCount=50,
            isPublic=1,
        )
        session.add(text)
        session.commit()

        assert text.id is not None
        assert text.title == "Introduction to Python"
        assert text.proficiencyLevel == "B1"
        assert text.wordCount == 50
        assert text.isPublic == 1
        assert text.createdAt is not None

    def test_text_relationships(self, session, test_user, english_language):
        """Test text relationships with author and language."""
        text = TextModel(
            id=str(uuid.uuid4()),
            title="Test Article",
            content="Content here...",
            languageId=english_language.id,
            authorId=test_user.id,
            proficiencyLevel="A1",
            wordCount=20,
            isPublic=1,
        )
        session.add(text)
        session.commit()

        assert text.author.username == test_user.username
        assert text.language.name == "English"

    def test_text_with_source(self, session, test_user, english_language):
        """Test creating text with optional source."""
        text = TextModel(
            id=str(uuid.uuid4()),
            title="Article",
            content="Content...",
            languageId=english_language.id,
            authorId=test_user.id,
            proficiencyLevel="B2",
            wordCount=100,
            isPublic=1,
            source="https://example.com/article",
        )
        session.add(text)
        session.commit()

        assert text.source == "https://example.com/article"

    def test_text_repr(self, session, test_user, english_language):
        """Test text string representation."""
        text = TextModel(
            id=str(uuid.uuid4()),
            title="Test Text",
            content="Content...",
            languageId=english_language.id,
            authorId=test_user.id,
            proficiencyLevel="C1",
            wordCount=75,
            isPublic=1,
        )
        session.add(text)
        session.commit()

        expected = f"<Text(id='{text.id}', title='Test Text', level='C1')>"
        assert repr(text) == expected


# TextTag Model Tests


class TestTextTagModel:
    """Test cases for the TextTag model."""

    def test_create_text_tag(self, session):
        """Test creating a text tag."""
        tag = TextTag(
            id=str(uuid.uuid4()),
            name="programming",
            description="Programming tutorials",
        )
        session.add(tag)
        session.commit()

        assert tag.id is not None
        assert tag.name == "programming"
        assert tag.description == "Programming tutorials"

    def test_text_tag_unique_name(self, session):
        """Test that tag names must be unique."""
        tag1 = TextTag(
            id=str(uuid.uuid4()),
            name="science",
            description="Science articles",
        )
        session.add(tag1)
        session.commit()

        tag2 = TextTag(
            id=str(uuid.uuid4()),
            name="science",  # Duplicate name
            description="Different description",
        )
        session.add(tag2)

        with pytest.raises(Exception):
            session.commit()

    def test_text_tag_repr(self, session):
        """Test text tag string representation."""
        tag = TextTag(
            id=str(uuid.uuid4()),
            name="education",
        )
        session.add(tag)
        session.commit()

        expected = f"<TextTag(id='{tag.id}', name='education')>"
        assert repr(tag) == expected


# TextTagAssociation Model Tests


class TestTextTagAssociationModel:
    """Test cases for the TextTagAssociation model."""

    def test_create_text_tag_association(self, session, test_user, english_language):
        """Test creating a text-tag association."""
        text = TextModel(
            id=str(uuid.uuid4()),
            title="Python Guide",
            content="Guide content...",
            languageId=english_language.id,
            authorId=test_user.id,
            proficiencyLevel="B1",
            wordCount=100,
            isPublic=1,
        )
        tag = TextTag(id=str(uuid.uuid4()), name="tutorial")

        session.add_all([text, tag])
        session.commit()

        assoc = TextTagAssociation(textId=text.id, tagId=tag.id)
        session.add(assoc)
        session.commit()

        assert assoc.textId == text.id
        assert assoc.tagId == tag.id

    def test_text_tag_association_relationships(
        self, session, test_user, english_language
    ):
        """Test text-tag association relationships."""
        text = TextModel(
            id=str(uuid.uuid4()),
            title="Article",
            content="Content...",
            languageId=english_language.id,
            authorId=test_user.id,
            proficiencyLevel="A2",
            wordCount=50,
            isPublic=1,
        )
        tag = TextTag(id=str(uuid.uuid4()), name="news")

        session.add_all([text, tag])
        session.commit()

        assoc = TextTagAssociation(textId=text.id, tagId=tag.id)
        session.add(assoc)
        session.commit()

        assert assoc.text.title == "Article"
        assert assoc.tag.name == "news"

    def test_text_with_multiple_tags(self, session, test_user, english_language):
        """Test text with multiple tags."""
        text = TextModel(
            id=str(uuid.uuid4()),
            title="Python Tutorial",
            content="Content...",
            languageId=english_language.id,
            authorId=test_user.id,
            proficiencyLevel="B1",
            wordCount=150,
            isPublic=1,
        )
        tag1 = TextTag(id=str(uuid.uuid4()), name="programming")
        tag2 = TextTag(id=str(uuid.uuid4()), name="education")

        session.add_all([text, tag1, tag2])
        session.commit()

        assoc1 = TextTagAssociation(textId=text.id, tagId=tag1.id)
        assoc2 = TextTagAssociation(textId=text.id, tagId=tag2.id)
        session.add_all([assoc1, assoc2])
        session.commit()

        queried_text = session.query(TextModel).filter_by(id=text.id).first()
        assert len(queried_text.tag_associations) == 2
        tag_names = [assoc.tag.name for assoc in queried_text.tag_associations]
        assert "programming" in tag_names
        assert "education" in tag_names

    def test_delete_text_cascades_associations(
        self, session, test_user, english_language
    ):
        """Test that deleting a text deletes its tag associations."""
        text = TextModel(
            id=str(uuid.uuid4()),
            title="Article",
            content="Content...",
            languageId=english_language.id,
            authorId=test_user.id,
            proficiencyLevel="A1",
            wordCount=25,
            isPublic=1,
        )
        tag = TextTag(id=str(uuid.uuid4()), name="test")

        session.add_all([text, tag])
        session.commit()

        assoc = TextTagAssociation(textId=text.id, tagId=tag.id)
        session.add(assoc)
        session.commit()

        text_id = text.id

        # Delete text
        session.delete(text)
        session.commit()

        # Verify association is deleted
        deleted_assoc = (
            session.query(TextTagAssociation).filter_by(textId=text_id).first()
        )
        assert deleted_assoc is None

    def test_text_tag_association_repr(self, session, test_user, english_language):
        """Test text tag association string representation."""
        text = TextModel(
            id=str(uuid.uuid4()),
            title="Article",
            content="Content...",
            languageId=english_language.id,
            authorId=test_user.id,
            proficiencyLevel="B2",
            wordCount=80,
            isPublic=1,
        )
        tag = TextTag(id=str(uuid.uuid4()), name="sample")

        session.add_all([text, tag])
        session.commit()

        assoc = TextTagAssociation(textId=text.id, tagId=tag.id)
        session.add(assoc)
        session.commit()

        expected = f"<TextTagAssociation(textId='{text.id}', tagId='{tag.id}')>"
        assert repr(assoc) == expected


# UserVocabulary Model Tests


class TestUserVocabularyModel:
    """Test cases for the UserVocabulary model."""

    def test_create_user_vocabulary(self, session, test_user, english_language):
        """Test creating a user vocabulary."""
        vocab = UserVocabulary(
            id=str(uuid.uuid4()),
            userId=test_user.id,
            languageId=english_language.id,
            name="My English Vocabulary",
        )
        session.add(vocab)
        session.commit()

        assert vocab.id is not None
        assert vocab.userId == test_user.id
        assert vocab.languageId == english_language.id
        assert vocab.name == "My English Vocabulary"
        assert vocab.createdAt is not None

    def test_user_vocabulary_relationships(self, session, test_user, english_language):
        """Test user vocabulary relationships."""
        vocab = UserVocabulary(
            id=str(uuid.uuid4()),
            userId=test_user.id,
            languageId=english_language.id,
            name="Test Vocabulary",
        )
        session.add(vocab)
        session.commit()

        assert vocab.user.username == test_user.username
        assert vocab.language.name == "English"

    def test_user_vocabulary_unique_constraint(
        self, session, test_user, english_language
    ):
        """Test unique constraint on userId and languageId."""
        vocab1 = UserVocabulary(
            id=str(uuid.uuid4()),
            userId=test_user.id,
            languageId=english_language.id,
            name="First Vocabulary",
        )
        session.add(vocab1)
        session.commit()

        vocab2 = UserVocabulary(
            id=str(uuid.uuid4()),
            userId=test_user.id,
            languageId=english_language.id,  # Same user and language
            name="Second Vocabulary",
        )
        session.add(vocab2)

        with pytest.raises(Exception):
            session.commit()

    def test_delete_user_cascades_vocabulary(
        self, session, test_user, english_language
    ):
        """Test that deleting a user deletes their vocabularies."""
        vocab = UserVocabulary(
            id=str(uuid.uuid4()),
            userId=test_user.id,
            languageId=english_language.id,
            name="Test Vocabulary",
        )
        session.add(vocab)
        session.commit()

        vocab_id = vocab.id

        # Delete user
        session.delete(test_user)
        session.commit()

        # Verify vocabulary is deleted
        deleted_vocab = session.query(UserVocabulary).filter_by(id=vocab_id).first()
        assert deleted_vocab is None

    def test_user_vocabulary_repr(self, session, test_user, english_language):
        """Test user vocabulary string representation."""
        vocab = UserVocabulary(
            id=str(uuid.uuid4()),
            userId=test_user.id,
            languageId=english_language.id,
            name="My Vocabulary",
        )
        session.add(vocab)
        session.commit()

        expected = f"<UserVocabulary(id='{vocab.id}', userId='{test_user.id}', name='My Vocabulary')>"
        assert repr(vocab) == expected


# UserVocabularyItem Model Tests


class TestUserVocabularyItemModel:
    """Test cases for the UserVocabularyItem model."""

    @pytest.fixture
    def test_vocabulary(self, session, test_user, english_language):
        """Create a test vocabulary."""
        vocab = UserVocabulary(
            id=str(uuid.uuid4()),
            userId=test_user.id,
            languageId=english_language.id,
            name="Test Vocabulary",
        )
        session.add(vocab)
        session.commit()
        return vocab

    def test_create_vocabulary_item(self, session, test_vocabulary):
        """Test creating a vocabulary item."""
        item = UserVocabularyItem(
            id=str(uuid.uuid4()),
            userVocabularyId=test_vocabulary.id,
            term="function",
            lemma="function",
            partOfSpeech="NOUN",
            frequency=0.85,
            status="LEARNING",
            timesReviewed=5,
            confidenceLevel="A2",
        )
        session.add(item)
        session.commit()

        assert item.id is not None
        assert item.term == "function"
        assert item.lemma == "function"
        assert item.partOfSpeech == "NOUN"
        assert item.status == "LEARNING"
        assert item.timesReviewed == 5
        assert item.confidenceLevel == "A2"

    def test_vocabulary_item_defaults(self, session, test_vocabulary):
        """Test vocabulary item default values."""
        item = UserVocabularyItem(
            id=str(uuid.uuid4()),
            userVocabularyId=test_vocabulary.id,
            term="test",
        )
        session.add(item)
        session.commit()

        assert item.status == "NEW"
        assert item.timesReviewed == 0
        assert item.confidenceLevel == "A1"
        assert item.createdAt is not None

    def test_vocabulary_item_relationship(self, session, test_vocabulary):
        """Test vocabulary item relationship with vocabulary."""
        item = UserVocabularyItem(
            id=str(uuid.uuid4()),
            userVocabularyId=test_vocabulary.id,
            term="variable",
        )
        session.add(item)
        session.commit()

        assert item.vocabulary.name == "Test Vocabulary"

    def test_vocabulary_with_multiple_items(self, session, test_vocabulary):
        """Test vocabulary with multiple items."""
        items = [
            UserVocabularyItem(
                id=str(uuid.uuid4()),
                userVocabularyId=test_vocabulary.id,
                term="function",
                status="KNOWN",
            ),
            UserVocabularyItem(
                id=str(uuid.uuid4()),
                userVocabularyId=test_vocabulary.id,
                term="variable",
                status="LEARNING",
            ),
            UserVocabularyItem(
                id=str(uuid.uuid4()),
                userVocabularyId=test_vocabulary.id,
                term="constant",
                status="NEW",
            ),
        ]
        session.add_all(items)
        session.commit()

        queried_vocab = (
            session.query(UserVocabulary).filter_by(id=test_vocabulary.id).first()
        )
        assert len(queried_vocab.items) == 3
        terms = [item.term for item in queried_vocab.items]
        assert "function" in terms
        assert "variable" in terms
        assert "constant" in terms

    def test_vocabulary_item_unique_constraint(self, session, test_vocabulary):
        """Test unique constraint on userVocabularyId and term."""
        item1 = UserVocabularyItem(
            id=str(uuid.uuid4()),
            userVocabularyId=test_vocabulary.id,
            term="duplicate",
        )
        session.add(item1)
        session.commit()

        item2 = UserVocabularyItem(
            id=str(uuid.uuid4()),
            userVocabularyId=test_vocabulary.id,
            term="duplicate",  # Duplicate term in same vocabulary
        )
        session.add(item2)

        with pytest.raises(Exception):
            session.commit()

    def test_delete_vocabulary_cascades_items(self, session, test_vocabulary):
        """Test that deleting a vocabulary deletes its items."""
        item = UserVocabularyItem(
            id=str(uuid.uuid4()),
            userVocabularyId=test_vocabulary.id,
            term="test",
        )
        session.add(item)
        session.commit()

        item_id = item.id

        # Delete vocabulary
        session.delete(test_vocabulary)
        session.commit()

        # Verify item is deleted
        deleted_item = session.query(UserVocabularyItem).filter_by(id=item_id).first()
        assert deleted_item is None

    def test_vocabulary_item_with_notes(self, session, test_vocabulary):
        """Test vocabulary item with optional notes."""
        item = UserVocabularyItem(
            id=str(uuid.uuid4()),
            userVocabularyId=test_vocabulary.id,
            term="algorithm",
            notes="Important concept in computer science",
        )
        session.add(item)
        session.commit()

        assert item.notes == "Important concept in computer science"

    def test_vocabulary_item_repr(self, session, test_vocabulary):
        """Test vocabulary item string representation."""
        item = UserVocabularyItem(
            id=str(uuid.uuid4()),
            userVocabularyId=test_vocabulary.id,
            term="test",
            status="MASTERED",
        )
        session.add(item)
        session.commit()

        expected = (
            f"<UserVocabularyItem(id='{item.id}', term='test', status='MASTERED')>"
        )
        assert repr(item) == expected


# Query Tests


class TestQueryPatterns:
    """Test various query patterns."""

    def test_query_all_users(self, session, english_language):
        """Test querying all users."""
        users_data = [
            ("alice", "alice@example.com", "Alice", "Smith"),
            ("bob", "bob@example.com", "Bob", "Johnson"),
            ("charlie", "charlie@example.com", "Charlie", "Brown"),
        ]

        for username, email, first_name, last_name in users_data:
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                username=username,
                passwordHash="$2b$12$hashedpassword",
                firstName=first_name,
                lastName=last_name,
                nativeLanguageId=english_language.id,
                currentLanguageId=english_language.id,
            )
            session.add(user)
        session.commit()

        all_users = session.query(User).all()
        assert len(all_users) == 3

    def test_filter_query(self, session, test_user):
        """Test filtering users by username."""
        found_user = session.query(User).filter_by(username="johndoe").first()
        assert found_user is not None
        assert found_user.username == "johndoe"
        assert found_user.firstName == "John"

    def test_filter_with_condition(self, session, english_language):
        """Test filtering with conditions."""
        users_data = [
            ("alice", "alice@example.com", "Alice", "Smith"),
            ("bob", "bob@example.com", "Bob", "Johnson"),
            ("andrew", "andrew@example.com", "Andrew", "Brown"),
        ]

        for username, email, first_name, last_name in users_data:
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                username=username,
                passwordHash="$2b$12$hashedpassword",
                firstName=first_name,
                lastName=last_name,
                nativeLanguageId=english_language.id,
                currentLanguageId=english_language.id,
            )
            session.add(user)
        session.commit()

        users_with_a = session.query(User).filter(User.firstName.startswith("A")).all()
        assert len(users_with_a) == 2
        first_names = [u.firstName for u in users_with_a]
        assert "Alice" in first_names
        assert "Andrew" in first_names

    def test_order_by_query(self, session, english_language):
        """Test ordering query results."""
        users_data = [
            ("charlie", "charlie@example.com", "Charlie", "Brown"),
            ("alice", "alice@example.com", "Alice", "Smith"),
            ("bob", "bob@example.com", "Bob", "Johnson"),
        ]

        for username, email, first_name, last_name in users_data:
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                username=username,
                passwordHash="$2b$12$hashedpassword",
                firstName=first_name,
                lastName=last_name,
                nativeLanguageId=english_language.id,
                currentLanguageId=english_language.id,
            )
            session.add(user)
        session.commit()

        ordered_users = session.query(User).order_by(User.username).all()
        usernames = [u.username for u in ordered_users]
        assert usernames == ["alice", "bob", "charlie"]

    def test_count_query(self, session, english_language):
        """Test counting query results."""
        for i in range(5):
            user = User(
                id=str(uuid.uuid4()),
                email=f"user{i}@example.com",
                username=f"user{i}",
                passwordHash="$2b$12$hashedpassword",
                firstName=f"User{i}",
                lastName="Test",
                nativeLanguageId=english_language.id,
                currentLanguageId=english_language.id,
            )
            session.add(user)
        session.commit()

        user_count = session.query(User).count()
        assert user_count == 5

    def test_join_query(self, session, english_language):
        """Test join query with languages."""
        users_data = [
            ("alice", "alice@example.com", "Alice", "Smith"),
            ("bob", "bob@example.com", "Bob", "Johnson"),
        ]

        for username, email, first_name, last_name in users_data:
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                username=username,
                passwordHash="$2b$12$hashedpassword",
                firstName=first_name,
                lastName=last_name,
                nativeLanguageId=english_language.id,
                currentLanguageId=english_language.id,
            )
            session.add(user)
        session.commit()

        users_with_lang = (
            session.query(User, Language)
            .join(Language, User.nativeLanguageId == Language.id)
            .all()
        )

        assert len(users_with_lang) == 2
        for user, lang in users_with_lang:
            assert lang.name == "English"


# Helper Functions Tests


class TestHelperFunctions:
    """Test helper functions."""

    def test_get_all_models(self):
        """Test getting all model classes."""
        models = get_all_models()
        assert len(models) == 8
        assert Language in models
        assert User in models
        assert UserLanguage in models
        assert TextModel in models
        assert UserVocabulary in models
        assert UserVocabularyItem in models
        assert TextTag in models
        assert TextTagAssociation in models

    def test_get_model_by_table_name(self):
        """Test getting model by table name."""
        assert get_model_by_table_name("Language") == Language
        assert get_model_by_table_name("User") == User
        assert get_model_by_table_name("Text") == TextModel
        assert get_model_by_table_name("UserVocabulary") == UserVocabulary

    def test_get_model_by_invalid_table_name(self):
        """Test getting model with invalid table name."""
        with pytest.raises(
            ValueError, match="Model for table 'InvalidTable' not found"
        ):
            get_model_by_table_name("InvalidTable")
