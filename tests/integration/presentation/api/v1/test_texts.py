"""
Integration tests for Text API endpoints.

This module provides integration-style tests for text CRUD endpoints,
using FastAPI's TestClient with a temporary SQLite database.
"""

import logging
from collections.abc import Generator
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from ulid import ULID

from app.application.services.text_service import TextService
from app.core.dependencies import get_text_service
from app.infrastructure.database.sqlite.models import Base
from app.infrastructure.database.sqlite.models import Language as LanguageModel
from app.infrastructure.database.sqlite.models import User as UserModel
from app.infrastructure.database.sqlite.repositories.text_repository_impl import (
    SQLiteTextRepository,
)
from app.main import app

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Fixtures


@pytest.fixture(scope="function")
def db_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[Session, None, None]:
    """Create a temporary SQLite database and session for tests."""
    db_file = tmp_path / "test_texts_api.db"
    db_path = str(db_file)
    monkeypatch.setenv("SQLITE_DB_PATH", db_path)

    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db_setup(db_session: Session) -> dict[str, Any]:
    """Seed the database with a language and a user."""
    language = LanguageModel(
        id=str(ULID()),
        name="German",
        code="de",
        nativeName="Deutsch",
    )
    user = UserModel(
        id=str(ULID()),
        email="text.test@example.com",
        username="text_tester",
        passwordHash="some_hash",
        firstName="Text",
        lastName="Tester",
        nativeLanguageId=str(language.id),
        currentLanguageId=str(language.id),
    )
    db_session.add_all([language, user])
    db_session.commit()
    db_session.refresh(language)
    db_session.refresh(user)

    return {
        "db_path": cast(Engine, db_session.get_bind()).url.database,
        "language_id": ULID.from_str(language.id),
        "user_id": ULID.from_str(user.id),
    }


@pytest.fixture
def client(test_db_setup: dict[str, Any]) -> Generator[TestClient, None, None]:
    """Create a test client with a real text service connected to a test database."""
    test_repo = SQLiteTextRepository(db_path=test_db_setup["db_path"])
    test_text_service = TextService(repository=test_repo)

    app.dependency_overrides[get_text_service] = lambda: test_text_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# Test Data Helpers


def create_text_data(
    db_setup: dict[str, Any],
    title: str = "Integration Test",
    content: str = "This is a test.",
) -> dict[str, Any]:
    """Helper function to create valid text creation data."""
    return {
        "title": title,
        "content": content,
        "languageId": str(db_setup["language_id"]),
        "userId": str(db_setup["user_id"]),
        "proficiencyLevel": "A2",
        "wordCount": 4,
        "isPublic": True,
        "source": "http://test.com",
    }


def create_update_data(
    title: str | None = None, content: str | None = None
) -> dict[str, Any]:
    """Helper function to create text update data."""
    data = {}
    if title is not None:
        data["title"] = title
    if content is not None:
        data["content"] = content
    return data


# Test Classes


@pytest.mark.integration
class TestGetTexts:
    """Test GET /texts endpoint."""

    def test_get_texts_empty(self, client: TestClient) -> None:
        """Test retrieving texts when database is empty."""
        response = client.get("/texts/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0
        logger.info("Get texts empty test passed")

    def test_get_texts_success(
        self, client: TestClient, test_db_setup: dict[str, Any]
    ) -> None:
        """Test retrieving multiple texts."""
        text1_data = create_text_data(test_db_setup, title="Text 1")
        text2_data = create_text_data(test_db_setup, title="Text 2")
        client.post("/texts/", json=text1_data)
        client.post("/texts/", json=text2_data)

        response = client.get("/texts/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] in ["Text 1", "Text 2"]
        logger.info("Get texts success test passed")


@pytest.mark.integration
class TestGetTextById:
    """Test GET /texts/{textId} endpoint."""

    def test_get_text_by_id_success(
        self, client: TestClient, test_db_setup: dict[str, Any]
    ) -> None:
        """Test retrieving an existing text by ID."""
        text_data = create_text_data(test_db_setup)
        create_response = client.post("/texts/", json=text_data)
        text_id = create_response.json()["id"]

        response = client.get(f"/texts/{text_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == text_id
        assert data["title"] == text_data["title"]
        logger.info(f"Get text by ID success test passed: {text_id}")

    def test_get_text_by_id_not_found(self, client: TestClient) -> None:
        """Test retrieving non-existent text returns 404."""
        non_existent_id = ULID()
        response = client.get(f"/texts/{non_existent_id}")
        assert response.status_code == 404
        logger.info("Get text by ID not found test passed")


@pytest.mark.integration
class TestCreateText:
    """Test POST /texts/ endpoint."""

    def test_create_text_success(
        self, client: TestClient, test_db_setup: dict[str, Any]
    ) -> None:
        """Test creating a text with valid data."""
        text_data = create_text_data(test_db_setup)
        response = client.post("/texts/", json=text_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == text_data["title"]
        logger.info(f"Create text success test passed: {data['id']}")

    def test_create_text_missing_fields(
        self, client: TestClient, test_db_setup: dict[str, Any]
    ) -> None:
        """Test creating a text with missing required fields returns 422."""
        text_data = create_text_data(test_db_setup)
        del text_data["title"]
        response = client.post("/texts/", json=text_data)
        assert response.status_code == 422
        logger.info("Create text missing fields test passed")


@pytest.mark.integration
class TestUpdateText:
    """Test PUT /texts/{textId} endpoint."""

    def test_update_text_success(
        self, client: TestClient, test_db_setup: dict[str, Any]
    ) -> None:
        """Test updating a text successfully."""
        text_data = create_text_data(test_db_setup)
        create_response = client.post("/texts/", json=text_data)
        text_id = create_response.json()["id"]

        update_data = create_update_data(title="Updated Title")
        response = client.put(f"/texts/{text_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert (
            data["content"] == text_data["content"]
        )  # Check other fields are untouched
        logger.info(f"Update text success test passed: {text_id}")

    def test_update_text_not_found(self, client: TestClient) -> None:
        """Test updating non-existent text returns 404."""
        non_existent_id = ULID()
        update_data = create_update_data(title="Non-existent")
        response = client.put(f"/texts/{non_existent_id}", json=update_data)
        assert response.status_code == 404
        logger.info("Update text not found test passed")


@pytest.mark.integration
class TestDeleteText:
    """Test DELETE /texts/{textId} endpoint."""

    def test_delete_text_success(
        self, client: TestClient, test_db_setup: dict[str, Any]
    ) -> None:
        """Test deleting a text successfully."""
        text_data = create_text_data(test_db_setup)
        create_response = client.post("/texts/", json=text_data)
        text_id = create_response.json()["id"]

        response = client.delete(f"/texts/{text_id}")
        assert response.status_code == 204

        get_response = client.get(f"/texts/{text_id}")
        assert get_response.status_code == 404
        logger.info(f"Delete text success test passed: {text_id}")

    def test_delete_text_not_found(self, client: TestClient) -> None:
        """Test deleting non-existent text returns 404."""
        non_existent_id = ULID()
        response = client.delete(f"/texts/{non_existent_id}")
        assert response.status_code == 404
        logger.info("Delete text not found test passed")


@pytest.mark.integration
def test_text_crud_workflow(client: TestClient, test_db_setup: dict[str, Any]) -> None:
    """Full integration test for the complete Text CRUD workflow."""
    # 1. Create
    text_data = create_text_data(test_db_setup, title="Workflow Text")
    create_response = client.post("/texts/", json=text_data)
    assert create_response.status_code == 201
    created_text = create_response.json()
    text_id = created_text["id"]
    logger.info(f"Workflow: Created text {text_id}")

    # 2. Read (Get by ID)
    get_response = client.get(f"/texts/{text_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Workflow Text"
    logger.info(f"Workflow: Retrieved text {text_id}")

    # 3. Read (Get all)
    all_texts_response = client.get("/texts/")
    assert all_texts_response.status_code == 200
    assert len(all_texts_response.json()) == 1
    logger.info("Workflow: Retrieved all texts")

    # 4. Update
    update_data = create_update_data(title="Updated Workflow Text")
    update_response = client.put(f"/texts/{text_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Workflow Text"
    logger.info(f"Workflow: Updated text {text_id}")

    # 5. Delete
    delete_response = client.delete(f"/texts/{text_id}")
    assert delete_response.status_code == 204
    logger.info(f"Workflow: Deleted text {text_id}")

    # 6. Verify Deletion
    verify_response = client.get(f"/texts/{text_id}")
    assert verify_response.status_code == 404
    logger.info("Workflow: Verified text deletion")
