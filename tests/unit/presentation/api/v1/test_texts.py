"""
Unit tests for the Text API handlers.

This module contains tests for the text API handler functions in isolation,
with the TextService dependency mocked.
"""

import logging
from collections.abc import Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.application.dto.text_dto import TextResponse
from app.core.dependencies import get_text_service
from app.domain.entities.enums import ProficiencyLevel
from app.main import app

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_text_service() -> AsyncMock:
    """Fixture for a mocked text service."""
    return AsyncMock()


@pytest.fixture
def client(mock_text_service: AsyncMock) -> Generator[TestClient, None, None]:
    """Fixture for a test client with a mocked text service."""
    app.dependency_overrides[get_text_service] = lambda: mock_text_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_text_id() -> UUID:
    """Fixture for a sample text UUID."""
    return uuid4()


@pytest.fixture
def sample_text_response(sample_text_id: UUID) -> TextResponse:
    """Fixture for a sample TextResponse object."""
    return TextResponse(
        id=sample_text_id,
        title="Sample Title",
        content="This is sample content.",
        languageId=uuid4(),
        userId=uuid4(),
        proficiencyLevel=ProficiencyLevel.A1,
        wordCount=4,
        isPublic=True,
        source="http://example.com/source",
        createdAt=datetime.now(UTC),
        updatedAt=datetime.now(UTC),
    )


@pytest.fixture
def sample_text_create_data() -> dict[str, Any]:
    """Fixture for sample text creation request body."""
    return {
        "title": "New Title",
        "content": "A new piece of text content.",
        "language_id": str(uuid4()),
        "user_id": str(uuid4()),
        "proficiency_level": "B1",
        "word_count": 10,
        "is_public": False,
        "source": "http://example.com/new",
    }


@pytest.fixture
def sample_text_update_data() -> dict[str, Any]:
    """Fixture for sample text update request body."""
    return {
        "title": "Updated Title",
        "proficiency_level": "B2",
    }


class TestGetTexts:
    """Tests for the get_texts handler."""

    def test_get_texts_success(
        self,
        client: TestClient,
        mock_text_service: AsyncMock,
        sample_text_response: TextResponse,
    ) -> None:
        """Test get_texts returns 200 and a list of texts on success."""
        mock_text_service.get_all_texts.return_value = [sample_text_response]
        logger.info("Testing get_texts with a single text")

        response = client.get("/texts/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == str(sample_text_response.id)
        assert data[0]["title"] == sample_text_response.title
        mock_text_service.get_all_texts.assert_called_once_with(skip=0, limit=100)
        logger.info("get_texts success test passed")

    def test_get_texts_with_pagination(
        self, client: TestClient, mock_text_service: AsyncMock
    ) -> None:
        """Test get_texts correctly passes pagination parameters to the service."""
        mock_text_service.get_all_texts.return_value = []
        logger.info("Testing get_texts with pagination skip=5, limit=20")

        client.get("/texts/?skip=5&limit=20")

        mock_text_service.get_all_texts.assert_called_once_with(skip=5, limit=20)
        logger.info("get_texts pagination test passed")

    def test_get_texts_empty(
        self, client: TestClient, mock_text_service: AsyncMock
    ) -> None:
        """Test get_texts returns 200 and an empty list when no texts exist."""
        mock_text_service.get_all_texts.return_value = []
        logger.info("Testing get_texts with no texts")

        response = client.get("/texts/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
        logger.info("get_texts empty list test passed")

    def test_get_texts_handles_exception(
        self, client: TestClient, mock_text_service: AsyncMock
    ) -> None:
        """Test get_texts returns 500 when the service raises an exception."""
        error_message = "Database connection error"
        mock_text_service.get_all_texts.side_effect = Exception(error_message)
        logger.info("Testing get_texts with a service exception")

        response = client.get("/texts/")

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "Internal server error"
        assert data["detail"]["message"] == error_message
        logger.info("get_texts exception handling test passed")


class TestGetTextById:
    """Tests for the get_text_by_id handler."""

    def test_get_text_by_id_success(
        self,
        client: TestClient,
        mock_text_service: AsyncMock,
        sample_text_response: TextResponse,
        sample_text_id: UUID,
    ) -> None:
        """Test get_text_by_id returns 200 and a text on success."""
        mock_text_service.get_text.return_value = sample_text_response
        logger.info(f"Testing get_text_by_id with ID: {sample_text_id}")

        response = client.get(f"/texts/{sample_text_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_text_id)
        assert data["title"] == sample_text_response.title
        mock_text_service.get_text.assert_called_once_with(sample_text_id)
        logger.info("get_text_by_id success test passed")

    def test_get_text_by_id_not_found(
        self, client: TestClient, mock_text_service: AsyncMock, sample_text_id: UUID
    ) -> None:
        """Test get_text_by_id returns 404 when the text does not exist."""
        mock_text_service.get_text.return_value = None
        logger.info(f"Testing get_text_by_id with non-existent ID: {sample_text_id}")

        response = client.get(f"/texts/{sample_text_id}")

        assert response.status_code == 404
        assert response.json()["detail"]["error"] == "Text not found"
        mock_text_service.get_text.assert_called_once_with(sample_text_id)
        logger.info("get_text_by_id not found test passed")

    def test_get_text_by_id_invalid_uuid(
        self, client: TestClient, mock_text_service: AsyncMock
    ) -> None:
        """Test get_text_by_id returns 422 for a malformed UUID."""
        invalid_id = "not-a-uuid"
        logger.info(f"Testing get_text_by_id with invalid ID: {invalid_id}")

        response = client.get(f"/texts/{invalid_id}")

        assert response.status_code == 422
        mock_text_service.get_text.assert_not_called()
        logger.info("get_text_by_id invalid UUID test passed")

    def test_get_text_by_id_handles_exception(
        self, client: TestClient, mock_text_service: AsyncMock, sample_text_id: UUID
    ) -> None:
        """Test get_text_by_id returns 500 when the service raises an exception."""
        error_message = "Service unavailable"
        mock_text_service.get_text.side_effect = Exception(error_message)
        logger.info(
            f"Testing get_text_by_id with service exception for ID: {sample_text_id}"
        )

        response = client.get(f"/texts/{sample_text_id}")

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "Internal server error"
        assert data["detail"]["message"] == error_message
        logger.info("get_text_by_id exception handling test passed")


class TestCreateText:
    """Tests for the create_text handler."""

    def test_create_text_success(
        self,
        client: TestClient,
        mock_text_service: AsyncMock,
        sample_text_response: TextResponse,
        sample_text_create_data: dict[str, Any],
    ) -> None:
        """Test create_text returns 201 and the created text on success."""
        mock_text_service.create_text.return_value = sample_text_response
        logger.info(
            f"Testing create_text with title: {sample_text_create_data['title']}"
        )

        response = client.post("/texts/", json=sample_text_create_data)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == str(sample_text_response.id)
        assert data["title"] == sample_text_response.title
        mock_text_service.create_text.assert_called_once()
        logger.info("create_text success test passed")

    def test_create_text_invalid_body(
        self,
        client: TestClient,
        mock_text_service: AsyncMock,
        sample_text_create_data: dict[str, Any],
    ) -> None:
        """Test create_text returns 422 for an invalid request body."""
        del sample_text_create_data["title"]  # Make data invalid
        logger.info("Testing create_text with missing title field")

        response = client.post("/texts/", json=sample_text_create_data)

        assert response.status_code == 422
        mock_text_service.create_text.assert_not_called()
        logger.info("create_text invalid body test passed")

    def test_create_text_conflict(
        self,
        client: TestClient,
        mock_text_service: AsyncMock,
        sample_text_create_data: dict[str, Any],
    ) -> None:
        """Test create_text returns 409 when the service reports a conflict."""
        error_message = "Text with this title already exists for the user"
        mock_text_service.create_text.side_effect = ValueError(error_message)
        logger.info("Testing create_text with a data conflict")

        response = client.post("/texts/", json=sample_text_create_data)

        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error"] == "Conflict"
        assert data["detail"]["message"] == error_message
        logger.info("create_text conflict test passed")

    def test_create_text_handles_exception(
        self,
        client: TestClient,
        mock_text_service: AsyncMock,
        sample_text_create_data: dict[str, Any],
    ) -> None:
        """Test create_text returns 500 on unexpected service exception."""
        error_message = "Internal service failure"
        mock_text_service.create_text.side_effect = Exception(error_message)
        logger.info("Testing create_text with an unexpected service exception")

        response = client.post("/texts/", json=sample_text_create_data)

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "Internal server error"
        assert data["detail"]["message"] == error_message
        logger.info("create_text exception handling test passed")


class TestUpdateText:
    """Tests for the update_text handler."""

    def test_update_text_success(
        self,
        client: TestClient,
        mock_text_service: AsyncMock,
        sample_text_response: TextResponse,
        sample_text_id: UUID,
        sample_text_update_data: dict[str, Any],
    ) -> None:
        """Test update_text returns 200 and the updated text on success."""
        mock_text_service.update_text.return_value = sample_text_response
        logger.info(f"Testing update_text for ID: {sample_text_id}")

        response = client.put(f"/texts/{sample_text_id}", json=sample_text_update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_text_response.id)
        mock_text_service.update_text.assert_called_once()
        logger.info("update_text success test passed")

    def test_update_text_not_found(
        self,
        client: TestClient,
        mock_text_service: AsyncMock,
        sample_text_id: UUID,
        sample_text_update_data: dict[str, Any],
    ) -> None:
        """Test update_text returns 404 when the text does not exist."""
        mock_text_service.update_text.return_value = None
        logger.info(f"Testing update_text for non-existent ID: {sample_text_id}")

        response = client.put(f"/texts/{sample_text_id}", json=sample_text_update_data)

        assert response.status_code == 404
        assert response.json()["detail"]["error"] == "Text not found"
        mock_text_service.update_text.assert_called_once()
        logger.info("update_text not found test passed")

    def test_update_text_invalid_uuid(
        self,
        client: TestClient,
        mock_text_service: AsyncMock,
        sample_text_update_data: dict[str, Any],
    ) -> None:
        """Test update_text returns 422 for a malformed UUID."""
        invalid_id = "not-a-uuid"
        logger.info(f"Testing update_text with invalid ID: {invalid_id}")

        response = client.put(f"/texts/{invalid_id}", json=sample_text_update_data)

        assert response.status_code == 422
        mock_text_service.update_text.assert_not_called()
        logger.info("update_text invalid UUID test passed")

    def test_update_text_invalid_body(
        self, client: TestClient, mock_text_service: AsyncMock, sample_text_id: UUID
    ) -> None:
        """Test update_text returns 422 for an invalid request body."""
        invalid_body = {"proficiency_level": "INVALID_LEVEL"}
        logger.info("Testing update_text with invalid body")

        response = client.put(f"/texts/{sample_text_id}", json=invalid_body)

        assert response.status_code == 422
        mock_text_service.update_text.assert_not_called()
        logger.info("update_text invalid body test passed")

    def test_update_text_conflict(
        self,
        client: TestClient,
        mock_text_service: AsyncMock,
        sample_text_id: UUID,
        sample_text_update_data: dict[str, Any],
    ) -> None:
        """Test update_text returns 409 when the service reports a conflict."""
        error_message = "Update conflicts with an existing resource"
        mock_text_service.update_text.side_effect = ValueError(error_message)
        logger.info("Testing update_text with a data conflict")

        response = client.put(f"/texts/{sample_text_id}", json=sample_text_update_data)

        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error"] == "Conflict"
        assert data["detail"]["message"] == error_message
        logger.info("update_text conflict test passed")

    def test_update_text_handles_exception(
        self,
        client: TestClient,
        mock_text_service: AsyncMock,
        sample_text_id: UUID,
        sample_text_update_data: dict[str, Any],
    ) -> None:
        """Test update_text returns 500 for an unexpected service exception."""
        error_message = "Database transaction failed"
        mock_text_service.update_text.side_effect = Exception(error_message)
        logger.info("Testing update_text with an unexpected service exception")

        response = client.put(f"/texts/{sample_text_id}", json=sample_text_update_data)

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "Internal server error"
        assert data["detail"]["message"] == error_message
        logger.info("update_text exception handling test passed")


class TestDeleteText:
    """Tests for the delete_text handler."""

    def test_delete_text_success(
        self, client: TestClient, mock_text_service: AsyncMock, sample_text_id: UUID
    ) -> None:
        """Test delete_text returns 204 on successful deletion."""
        mock_text_service.delete_text.return_value = True
        logger.info(f"Testing delete_text for ID: {sample_text_id}")

        response = client.delete(f"/texts/{sample_text_id}")

        assert response.status_code == 204
        mock_text_service.delete_text.assert_called_once_with(sample_text_id)
        logger.info("delete_text success test passed")

    def test_delete_text_not_found(
        self, client: TestClient, mock_text_service: AsyncMock, sample_text_id: UUID
    ) -> None:
        """Test delete_text returns 404 when the text does not exist."""
        mock_text_service.delete_text.return_value = False
        logger.info(f"Testing delete_text for non-existent ID: {sample_text_id}")

        response = client.delete(f"/texts/{sample_text_id}")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "Text not found"
        mock_text_service.delete_text.assert_called_once_with(sample_text_id)
        logger.info("delete_text not found test passed")

    def test_delete_text_invalid_uuid(
        self, client: TestClient, mock_text_service: AsyncMock
    ) -> None:
        """Test delete_text returns 422 for a malformed UUID."""
        invalid_id = "not-a-uuid"
        logger.info(f"Testing delete_text with invalid ID: {invalid_id}")

        response = client.delete(f"/texts/{invalid_id}")

        assert response.status_code == 422
        mock_text_service.delete_text.assert_not_called()
        logger.info("delete_text invalid UUID test passed")

    def test_delete_text_handles_exception(
        self, client: TestClient, mock_text_service: AsyncMock, sample_text_id: UUID
    ) -> None:
        """Test delete_text returns 500 for an unexpected service exception."""
        error_message = "Failed to delete text"
        mock_text_service.delete_text.side_effect = Exception(error_message)
        logger.info("Testing delete_text with an unexpected service exception")

        response = client.delete(f"/texts/{sample_text_id}")

        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "Internal server error"
        assert data["detail"]["message"] == error_message
        logger.info("delete_text exception handling test passed")
