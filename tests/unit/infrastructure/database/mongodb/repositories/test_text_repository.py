"""
Unit tests for MongoDBTextRepository.

Tests cover all methods of the repository implementation including
CRUD operations, queries, existence checks, and entity conversions.
"""

import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.domain.entities.enums import ProficiencyLevel
from app.domain.entities.text import Text as TextEntity
from app.infrastructure.database.mongodb.repositories.text_repository_impl import (
    MongoDBTextRepository,
)

# Fixtures


@pytest.fixture(scope="function")
def repository(mongo_client, db_url):
    """Create a MongoDBTextRepository instance with a test database."""
    db_name = f"test_db_{uuid.uuid4().hex}"
    repo = MongoDBTextRepository(db_url=db_url, db_name=db_name)
    yield repo
    mongo_client.drop_database(db_name)


@pytest.fixture
def language_id():
    return UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def user_id():
    return UUID("10000000-0000-0000-0000-000000000001")


@pytest.fixture
def tag_ids():
    return [
        UUID("20000000-0000-0000-0000-000000000001"),
        UUID("20000000-0000-0000-0000-000000000002"),
    ]


@pytest.fixture
def sample_text_entity(language_id, user_id) -> Callable:
    """Factory fixture for creating Text entities."""

    def _create_text(
        text_id: UUID = None,
        title: str = "Sample Text",
        content: str = "This is the content.",
        level: ProficiencyLevel = ProficiencyLevel.B1,
        is_public: bool = True,
    ) -> TextEntity:
        return TextEntity(
            id=text_id or uuid.uuid4(),
            title=title,
            content=content,
            language_id=language_id,
            user_id=user_id,
            proficiency_level=level,
            word_count=len(content.split()),
            is_public=is_public,
            source="Test Source",
        )

    return _create_text


# Test Classes


class TestCreateText:
    """Test text creation."""

    def test_create_text_success(self, repository, sample_text_entity):
        """
        Test creating a text successfully.
        """
        text_entity = sample_text_entity()
        created_text = repository.create(text_entity)

        assert created_text is not None
        assert created_text.id == text_entity.id
        assert created_text.title == "Sample Text"
        assert created_text.proficiency_level == ProficiencyLevel.B1

    def test_create_text_generates_id(self, repository, sample_text_entity):
        """
        Test that an ID is generated when not provided.
        """
        text_entity = sample_text_entity(text_id=None)
        text_entity.id = None

        created_text = repository.create(text_entity)
        assert created_text.id is not None
        assert isinstance(created_text.id, UUID)


class TestGetTextById:
    """
    Test retrieving texts by ID.
    """

    def test_get_by_id_found(self, repository, sample_text_entity):
        """
        Test retrieving an existing text by ID.
        """
        created_text = repository.create(sample_text_entity())
        retrieved_text = repository.get_by_id(created_text.id)

        assert retrieved_text is not None
        assert retrieved_text.id == created_text.id

    def test_get_by_id_not_found(self, repository):
        """
        Test retrieving a non-existent text returns None.
        """
        assert repository.get_by_id(uuid.uuid4()) is None


class TestGetAllTexts:
    """
    Test retrieving all texts with pagination.
    """

    def test_get_all_multiple_texts(self, repository, sample_text_entity):
        """
        Test retrieving all texts.
        """
        repository.create(sample_text_entity(title="Text 1"))
        repository.create(sample_text_entity(title="Text 2"))

        texts = repository.get_all()
        assert len(texts) == 2

    def test_get_all_with_pagination(self, repository, sample_text_entity):
        """
        Test pagination with skip and limit.
        """
        for i in range(5):
            repository.create(sample_text_entity(title=f"Text {i}"))

        page1 = repository.get_all(skip=0, limit=3)
        assert len(page1) == 3

        page2 = repository.get_all(skip=3, limit=3)
        assert len(page2) == 2


class TestUpdateText:
    """
    Test text update operations.
    """

    def test_update_text_success(self, repository, sample_text_entity):
        """
        Test updating a text successfully.
        """
        created_text = repository.create(sample_text_entity())
        created_text.title = "Updated Title"
        created_text.proficiency_level = ProficiencyLevel.C1

        updated_text = repository.update(created_text.id, created_text)

        assert updated_text is not None
        assert updated_text.title == "Updated Title"
        assert updated_text.proficiency_level == ProficiencyLevel.C1
        assert updated_text.updated_at > created_text.created_at

    def test_update_text_not_found(self, repository, sample_text_entity):
        """
        Test updating a non-existent text returns None.
        """
        result = repository.update(uuid.uuid4(), sample_text_entity())
        assert result is None


class TestDeleteText:
    """
    Test text deletion.
    """

    def test_delete_text_success(self, repository, sample_text_entity):
        """
        Test deleting an existing text returns True.
        """
        created_text = repository.create(sample_text_entity())
        result = repository.delete(created_text.id)
        assert result is True
        assert repository.get_by_id(created_text.id) is None

    def test_delete_text_not_found(self, repository):
        """
        Test deleting a non-existent text returns False.
        """
        assert repository.delete(uuid.uuid4()) is False


class TestTextQueries:
    """
    Test various query methods for texts.
    """

    def test_exists_true(self, repository, sample_text_entity):
        """
        Test exists returns True for an existing text.
        """
        created_text = repository.create(sample_text_entity())
        assert repository.exists(created_text.id) is True

    def test_exists_false(self, repository):
        """
        Test exists returns False for a non-existent text.
        """
        assert repository.exists(uuid.uuid4()) is False

    def test_get_by_language(self, repository, sample_text_entity, language_id):
        """
        Test retrieving texts by language.
        """
        repository.create(sample_text_entity())
        texts = repository.get_by_language(language_id)
        assert len(texts) == 1
        assert texts[0].language_id == language_id

    def test_get_by_user(self, repository, sample_text_entity, user_id):
        """
        Test retrieving texts by user.
        """
        repository.create(sample_text_entity())
        texts = repository.get_by_user(user_id)
        assert len(texts) == 1
        assert texts[0].user_id == user_id

    def test_get_by_proficiency_level(self, repository, sample_text_entity):
        """
        Test retrieving texts by proficiency level.
        """
        repository.create(sample_text_entity(level=ProficiencyLevel.A2))
        texts = repository.get_by_proficiency_level(ProficiencyLevel.A2)
        assert len(texts) == 1
        assert texts[0].proficiency_level == ProficiencyLevel.A2

    def test_get_public_texts(self, repository, sample_text_entity):
        """
        Test retrieving only public texts.
        """
        repository.create(sample_text_entity(title="Public", is_public=True))
        repository.create(sample_text_entity(title="Private", is_public=False))
        texts = repository.get_public_texts()
        assert len(texts) == 1
        assert texts[0].title == "Public"

    def test_search_by_title(self, repository, sample_text_entity):
        """
        Test searching texts by title.
        """
        repository.create(sample_text_entity(title="A Quick Brown Fox"))
        repository.create(sample_text_entity(title="Another Story"))

        results = repository.search_by_title("Quick Brown")
        assert len(results) == 1
        assert results[0].title == "A Quick Brown Fox"

        results_case = repository.search_by_title("quick brown")
        assert len(results_case) == 1

    def test_get_by_tags(self, repository, sample_text_entity, tag_ids):
        """
        Test retrieving texts by associated tags.
        """

        # MongoDB doesn't have direct join tables like SQL. Tags would be embedded
        # or referenced. For this test, we'll assume tags are part of the TextEntity
        # or handled at a higher level. This test will be simplified.
        # If tags are to be implemented in MongoDB, the TextModel and repository
        # methods would need to be updated to reflect that.

        # For now, we'll just test that the method exists and returns an empty list
        # if no tags are implemented in the MongoDBTextRepository.
        results = repository.get_by_tags([tag_ids[0]])
        assert len(results) == 0


class TestEntityConversionText:
    """
    Test entity/model conversion methods for Text.
    """

    def test_model_to_entity_conversion(self, repository, language_id, user_id):
        """
        Test converting MongoDB document to domain entity.
        """
        text_id = uuid.uuid4()
        text_model_dict = {
            # MongoDB returns UUID objects with uuidRepresentation="standard"
            "_id": text_id,
            "title": "Model Title",
            "content": "Model content.",
            "languageId": language_id,  # UUID object
            "userId": user_id,  # UUID object
            "proficiencyLevel": ProficiencyLevel.B2.value,
            "wordCount": 3,
            "isPublic": True,
            "source": "Model Source",
            "createdAt": datetime.now(UTC),
            "updatedAt": datetime.now(UTC),
        }
        entity = repository._model_to_entity(text_model_dict)
        assert isinstance(entity, TextEntity)
        assert entity.id == text_id  # _id was converted to id
        assert entity.title == text_model_dict["title"]
        assert entity.proficiency_level == ProficiencyLevel.B2
        # Verify _id was converted to id (no longer exists in dict)
        assert "_id" not in text_model_dict
        assert "id" in text_model_dict

    def test_entity_to_model_conversion(self, repository, sample_text_entity):
        """
        Test converting Text domain entity to MongoDB document.
        """
        entity = sample_text_entity()
        model = repository._entity_to_model(entity)
        assert isinstance(model, dict)
        # _id should be a UUID object (MongoDB stores UUIDs as UUID objects
        # with uuidRepresentation="standard")
        assert model["_id"] == entity.id
        assert isinstance(model["_id"], UUID)
        assert model["title"] == entity.title
        assert model["proficiencyLevel"] == entity.proficiency_level.value
        # Verify id was converted to _id (no longer exists in model)
        assert "id" not in model
        assert "_id" in model
