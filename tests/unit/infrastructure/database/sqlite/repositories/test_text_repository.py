"""
Unit tests for SQLiteTextRepository.

Tests cover all methods of the repository implementation including
CRUD operations, queries, existence checks, and entity conversions.
"""

from collections.abc import Callable
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ulid import ULID

from app.domain.entities.enums import ProficiencyLevel
from app.domain.entities.text import Text as TextEntity
from app.infrastructure.database.sqlite.models import (
    Base,
    TextModel,
    TextTagAssociation,
)
from app.infrastructure.database.sqlite.models import (
    Language as LanguageModel,
)
from app.infrastructure.database.sqlite.models import (
    TextTag as TagModel,
)
from app.infrastructure.database.sqlite.models import (
    User as UserModel,
)
from app.infrastructure.database.sqlite.repositories.text_repository_impl import (
    SQLiteTextRepository,
)

# Fixtures


@pytest.fixture(scope="function")
def setup_database(tmp_path):
    """Create a temporary database and seed it with required data."""
    db_file = tmp_path / "test_text_repo.db"
    engine = create_engine(f"sqlite:///{db_file}", echo=False)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        # Seed Languages
        lang1 = LanguageModel(
            id=str(ULID.from_str("01ARZ3NDEKTSV4RRFFQ69G5FAV")),
            name="English",
            code="en",
            nativeName="English",
        )
        # Seed Users
        user1 = UserModel(
            id=str(ULID.from_str("01ARZ3NDEKTSV4RRFFQ69G5FAX")),
            email="author@example.com",
            username="author1",
            passwordHash="hash",
            firstName="Author",
            lastName="One",
            nativeLanguageId=lang1.id,
            currentLanguageId=lang1.id,
        )
        # Seed Tags
        tag1 = TagModel(
            id=str(ULID.from_str("01ARZ3NDEKTSV4RRFFQ69G5FAY")), name="news"
        )
        tag2 = TagModel(
            id=str(ULID.from_str("01ARZ3NDEKTSV4RRFFQ69G5FAZ")), name="history"
        )

        session.add_all([lang1, user1, tag1, tag2])
        session.commit()

    yield str(db_file)
    engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def repository(setup_database):
    """Create a SQLiteTextRepository instance with a test database."""
    repo = SQLiteTextRepository(db_path=setup_database)
    yield repo
    await repo.engine.dispose()


@pytest.fixture
def language_id() -> ULID:
    return ULID.from_str("01ARZ3NDEKTSV4RRFFQ69G5FAV")


@pytest.fixture
def user_id() -> ULID:
    return ULID.from_str("01ARZ3NDEKTSV4RRFFQ69G5FAX")


@pytest.fixture
def tag_ids() -> list[ULID]:
    return [
        ULID.from_str("01ARZ3NDEKTSV4RRFFQ69G5FAY"),
        ULID.from_str("01ARZ3NDEKTSV4RRFFQ69G5FAZ"),
    ]


@pytest.fixture
def sample_text_entity(language_id: ULID, user_id: ULID) -> Callable[..., TextEntity]:
    """Factory fixture for creating Text entities."""

    def _create_text(
        text_id: ULID | None = None,
        title: str = "Sample Text",
        content: str = "This is the content.",
        level: ProficiencyLevel = ProficiencyLevel.B1,
        is_public: bool = True,
    ) -> TextEntity:
        now = datetime.now(UTC)
        return TextEntity(
            id=str(text_id or ULID()),
            title=title,
            content=content,
            languageId=str(language_id),
            userId=str(user_id),
            proficiencyLevel=level,
            wordCount=len(content.split()),
            isPublic=is_public,
            source="Test Source",
            createdAt=now,
            updatedAt=now,
        )

    return _create_text


# Test Classes


class TestCreateText:
    """Test text creation."""

    @pytest.mark.asyncio
    async def test_create_text_success(self, repository, sample_text_entity):
        """Test creating a text successfully."""
        text_entity = sample_text_entity()
        created_text = await repository.create(text_entity)

        assert created_text is not None
        assert created_text.id == text_entity.id
        assert created_text.title == "Sample Text"
        assert created_text.proficiency_level == ProficiencyLevel.B1

    @pytest.mark.asyncio
    async def test_create_text_generates_id(self, repository, sample_text_entity):
        """Test that an ID is generated when not provided."""
        text_entity = sample_text_entity(text_id=None)
        text_entity.id = None

        created_text = await repository.create(text_entity)
        assert created_text.id is not None
        assert isinstance(created_text.id, str)
        assert ULID.from_str(created_text.id)


class TestGetTextById:
    """Test retrieving texts by ID."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, sample_text_entity):
        """Test retrieving an existing text by ID."""
        created_text = await repository.create(sample_text_entity())
        retrieved_text = await repository.get_by_id(created_text.id)

        assert retrieved_text is not None
        assert retrieved_text.id == created_text.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test retrieving a non-existent text returns None."""
        assert await repository.get_by_id(ULID()) is None


class TestGetAllTexts:
    """Test retrieving all texts with pagination."""

    @pytest.mark.asyncio
    async def test_get_all_multiple_texts(self, repository, sample_text_entity):
        """Test retrieving all texts."""
        await repository.create(sample_text_entity(title="Text 1"))
        await repository.create(sample_text_entity(title="Text 2"))

        texts = await repository.get_all()
        assert len(texts) == 2

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, repository, sample_text_entity):
        """Test pagination with skip and limit."""
        for i in range(5):
            await repository.create(sample_text_entity(title=f"Text {i}"))

        page1 = await repository.get_all(skip=0, limit=3)
        assert len(page1) == 3

        page2 = await repository.get_all(skip=3, limit=3)
        assert len(page2) == 2


class TestUpdateText:
    """Test text update operations."""

    @pytest.mark.asyncio
    async def test_update_text_success(self, repository, sample_text_entity):
        """Test updating a text successfully."""
        created_text = await repository.create(sample_text_entity())
        created_text.title = "Updated Title"
        created_text.proficiency_level = ProficiencyLevel.C1

        updated_text = await repository.update(created_text.id, created_text)

        assert updated_text is not None
        assert updated_text.title == "Updated Title"
        assert updated_text.proficiency_level == ProficiencyLevel.C1
        assert updated_text.updated_at > created_text.created_at

    @pytest.mark.asyncio
    async def test_update_text_not_found(self, repository, sample_text_entity):
        """Test updating a non-existent text returns None."""
        result = await repository.update(ULID(), sample_text_entity())
        assert result is None


class TestDeleteText:
    """Test text deletion."""

    @pytest.mark.asyncio
    async def test_delete_text_success(self, repository, sample_text_entity):
        """Test deleting an existing text returns True."""
        created_text = await repository.create(sample_text_entity())
        result = await repository.delete(created_text.id)
        assert result is True
        assert await repository.get_by_id(created_text.id) is None

    @pytest.mark.asyncio
    async def test_delete_text_not_found(self, repository):
        """Test deleting a non-existent text returns False."""
        assert await repository.delete(ULID()) is False


class TestTextQueries:
    """Test various query methods for texts."""

    @pytest.mark.asyncio
    async def test_get_by_language(self, repository, sample_text_entity, language_id):
        """Test retrieving texts by language."""
        await repository.create(sample_text_entity())
        texts = await repository.get_by_language(language_id)
        assert len(texts) == 1
        assert texts[0].language_id == language_id

    @pytest.mark.asyncio
    async def test_get_by_user(self, repository, sample_text_entity, user_id):
        """Test retrieving texts by user."""
        await repository.create(sample_text_entity())
        texts = await repository.get_by_user(user_id)
        assert len(texts) == 1
        assert texts[0].user_id == user_id

    @pytest.mark.asyncio
    async def test_get_by_proficiency_level(self, repository, sample_text_entity):
        """Test retrieving texts by proficiency level."""
        await repository.create(sample_text_entity(level=ProficiencyLevel.A2))
        texts = await repository.get_by_proficiency_level(ProficiencyLevel.A2)
        assert len(texts) == 1
        assert texts[0].proficiency_level == ProficiencyLevel.A2

    @pytest.mark.asyncio
    async def test_get_public_texts(self, repository, sample_text_entity):
        """Test retrieving only public texts."""
        await repository.create(sample_text_entity(title="Public", is_public=True))
        await repository.create(sample_text_entity(title="Private", is_public=False))
        texts = await repository.get_public_texts()
        assert len(texts) == 1
        assert texts[0].title == "Public"

    @pytest.mark.asyncio
    async def test_search_by_title(self, repository, sample_text_entity):
        """Test searching texts by title."""
        await repository.create(sample_text_entity(title="A Quick Brown Fox"))
        await repository.create(sample_text_entity(title="Another Story"))

        results = await repository.search_by_title("Quick Brown")
        assert len(results) == 1
        assert results[0].title == "A Quick Brown Fox"

        results_case = await repository.search_by_title("quick brown")
        assert len(results_case) == 1  # Assuming case-insensitivity from LIKE

    @pytest.mark.asyncio
    async def test_get_by_tags(self, repository, sample_text_entity, tag_ids):
        """Test retrieving texts by associated tags."""
        text1 = await repository.create(sample_text_entity(title="Text 1"))
        text2 = await repository.create(sample_text_entity(title="Text 2"))

        # Associate text1 with tag1, text2 with tag2
        async with repository.SessionLocal() as session:
            assoc1 = TextTagAssociation(textId=str(text1.id), tagId=str(tag_ids[0]))
            assoc2 = TextTagAssociation(textId=str(text2.id), tagId=str(tag_ids[1]))
            session.add_all([assoc1, assoc2])
            await session.commit()

        # Find texts with the first tag
        results = await repository.get_by_tags([tag_ids[0]])
        assert len(results) == 1
        assert results[0].id == text1.id

        # Find texts with either tag
        results_either = await repository.get_by_tags(tag_ids)
        assert len(results_either) == 2


class TestEntityConversionText:
    """Test entity/model conversion methods for Text."""

    @pytest.mark.asyncio
    async def test_model_to_entity_conversion(self, repository, language_id, user_id):
        """Test converting Text ORM model to domain entity."""
        text_model = TextModel(
            id=str(ULID()),
            title="Model Title",
            content="Model content.",
            languageId=str(language_id),
            userId=str(user_id),
            proficiencyLevel=ProficiencyLevel.B2.value,
            wordCount=3,
            isPublic=1,
            source="Model Source",
            createdAt=datetime.now(UTC),
            updatedAt=datetime.now(UTC),
        )
        entity = repository._model_to_entity(text_model)
        assert isinstance(entity, TextEntity)
        assert str(entity.id) == text_model.id
        assert entity.title == text_model.title
        assert entity.proficiency_level == ProficiencyLevel.B2

    @pytest.mark.asyncio
    async def test_entity_to_model_conversion(self, repository, sample_text_entity):
        """Test converting Text domain entity to ORM model."""
        entity = sample_text_entity()
        model = repository._entity_to_model(entity)
        assert isinstance(model, TextModel)
        assert model.id == str(entity.id)
        assert model.title == entity.title
        assert model.proficiencyLevel == entity.proficiency_level.value
