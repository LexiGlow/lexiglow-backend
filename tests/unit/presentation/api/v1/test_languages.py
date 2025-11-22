"""
Unit tests for the Language API handlers.

This module contains tests for the language API handler functions in isolation,
with the LanguageService dependency mocked.
"""

import logging
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.application.dto.language_dto import LanguageResponse
from app.core.dependencies import get_language_service
from app.main import app

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_language_service() -> AsyncMock:
    """Fixture for a mocked language service."""
    return AsyncMock()


@pytest.fixture
def client(mock_language_service: AsyncMock) -> TestClient:
    """Fixture for a test client with a mocked language service."""
    app.dependency_overrides[get_language_service] = lambda: mock_language_service
    return TestClient(app)


@pytest.fixture
def sample_language_id() -> UUID:
    """Fixture for a sample language UUID."""
    return uuid4()


@pytest.fixture
def sample_language_response(sample_language_id: UUID) -> LanguageResponse:
    """Fixture for a sample LanguageResponse object."""
    return LanguageResponse(
        id=sample_language_id,
        name="Spanish",
        code="es",
        nativeName="Español",
        createdAt=datetime.now(),
    )


@pytest.fixture
def sample_language_create_data() -> dict[str, Any]:
    """Fixture for sample language creation request body."""
    return {
        "name": "Spanish",
        "code": "es",
        "nativeName": "Español",
    }


@pytest.fixture
def sample_language_update_data() -> dict[str, Any]:
    """Fixture for sample language update request body."""
    return {
        "name": "Updated Spanish",
        "code": "es",
        "nativeName": "Español Actualizado",
    }


class TestGetLanguages:
    """Tests for the get_languages handler."""

    def test_get_languages_success(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_response: LanguageResponse,
    ) -> None:
        """
        Test get_languages returns 200 and a list of languages on success.
        """
        # Arrange
        mock_language_service.get_all_languages.return_value = [
            sample_language_response
        ]
        logger.info("Testing get_languages with a single language")

        # Act
        response = client.get("/languages/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == str(sample_language_response.id)
        assert data[0]["name"] == sample_language_response.name
        mock_language_service.get_all_languages.assert_called_once_with(
            skip=0, limit=100
        )
        logger.info("get_languages success test passed")

    def test_get_languages_with_pagination(
        self, client: TestClient, mock_language_service: AsyncMock
    ) -> None:
        """
        Test get_languages correctly passes pagination parameters to the service.
        """
        # Arrange
        mock_language_service.get_all_languages.return_value = []
        logger.info("Testing get_languages with pagination skip=10, limit=50")

        # Act
        client.get("/languages/?skip=10&limit=50")

        # Assert
        mock_language_service.get_all_languages.assert_called_once_with(
            skip=10, limit=50
        )
        logger.info("get_languages pagination test passed")

    def test_get_languages_empty(
        self, client: TestClient, mock_language_service: AsyncMock
    ) -> None:
        """
        Test get_languages returns 200 and an empty list when no languages exist.
        """
        # Arrange
        mock_language_service.get_all_languages.return_value = []
        logger.info("Testing get_languages with no languages")

        # Act
        response = client.get("/languages/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
        logger.info("get_languages empty list test passed")

    def test_get_languages_handles_exception(
        self, client: TestClient, mock_language_service: AsyncMock
    ) -> None:
        """
        Test get_languages returns 500 when the service raises an exception.
        """
        # Arrange
        error_message = "Database connection failed"
        mock_language_service.get_all_languages.side_effect = Exception(error_message)
        logger.info("Testing get_languages with a service exception")

        # Act
        response = client.get("/languages/")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "Internal server error"
        assert data["detail"]["message"] == error_message
        logger.info("get_languages exception handling test passed")


class TestGetLanguageById:
    """Tests for the get_language_by_id handler."""

    def test_get_language_by_id_success(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_response: LanguageResponse,
        sample_language_id: UUID,
    ) -> None:
        """
        Test get_language_by_id returns 200 and a language on success.
        """
        # Arrange
        mock_language_service.get_language.return_value = sample_language_response
        logger.info(f"Testing get_language_by_id with ID: {sample_language_id}")

        # Act
        response = client.get(f"/languages/{sample_language_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_language_id)
        assert data["name"] == sample_language_response.name
        mock_language_service.get_language.assert_called_once_with(sample_language_id)
        logger.info("get_language_by_id success test passed")

    def test_get_language_by_id_not_found(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_id: UUID,
    ) -> None:
        """
        Test get_language_by_id returns 404 when the language does not exist.
        """
        # Arrange
        mock_language_service.get_language.return_value = None
        logger.info(
            f"Testing get_language_by_id with non-existent ID: {sample_language_id}"
        )

        # Act
        response = client.get(f"/languages/{sample_language_id}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"]["error"] == "Language not found"
        mock_language_service.get_language.assert_called_once_with(sample_language_id)
        logger.info("get_language_by_id not found test passed")

    def test_get_language_by_id_invalid_uuid(
        self, client: TestClient, mock_language_service: AsyncMock
    ) -> None:
        """
        Test get_language_by_id returns 422 for a malformed UUID.
        """
        # Arrange
        invalid_id = "not-a-valid-uuid"
        logger.info(f"Testing get_language_by_id with invalid ID: {invalid_id}")

        # Act
        response = client.get(f"/languages/{invalid_id}")

        # Assert
        assert response.status_code == 422
        mock_language_service.get_language.assert_not_called()
        logger.info("get_language_by_id invalid UUID test passed")

    def test_get_language_by_id_handles_exception(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_id: UUID,
    ) -> None:
        """
        Test get_language_by_id returns 500 when the service raises an exception.
        """
        # Arrange
        error_message = "Service unavailable"
        mock_language_service.get_language.side_effect = Exception(error_message)
        logger.info(
            f"Testing get_language_by_id with service exception "
            f"for ID: {sample_language_id}"
        )

        # Act
        response = client.get(f"/languages/{sample_language_id}")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "Internal server error"
        assert data["detail"]["message"] == error_message
        logger.info("get_language_by_id exception handling test passed")


class TestCreateLanguage:
    """Tests for the create_language handler."""

    def test_create_language_success(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_response: LanguageResponse,
        sample_language_create_data: dict[str, Any],
    ) -> None:
        """
        Test create_language returns 201 and the created language on success.
        """
        # Arrange
        mock_language_service.create_language.return_value = sample_language_response
        logger.info(
            f"Testing create_language with code: {sample_language_create_data['code']}"
        )

        # Act
        response = client.post("/languages/", json=sample_language_create_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == str(sample_language_response.id)
        assert data["name"] == sample_language_response.name
        mock_language_service.create_language.assert_called_once()
        logger.info("create_language success test passed")

    def test_create_language_invalid_body(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_create_data: dict[str, Any],
    ) -> None:
        """
        Test create_language returns 422 for an invalid request body.
        """
        # Arrange
        del sample_language_create_data["code"]  # Make the data invalid
        logger.info("Testing create_language with missing code field")

        # Act
        response = client.post("/languages/", json=sample_language_create_data)

        # Assert
        assert response.status_code == 422
        mock_language_service.create_language.assert_not_called()
        logger.info("create_language invalid body test passed")

    def test_create_language_conflict(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_create_data: dict[str, Any],
    ) -> None:
        """
        Test create_language returns 409 when the service reports a conflict.
        """
        # Arrange
        error_message = "Language code es is already registered"
        mock_language_service.create_language.side_effect = ValueError(error_message)
        logger.info(
            "Testing create_language with a data conflict (e.g., duplicate code)"
        )

        # Act
        response = client.post("/languages/", json=sample_language_create_data)

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error"] == "Conflict"
        assert data["detail"]["message"] == error_message
        logger.info("create_language conflict test passed")

    def test_create_language_handles_exception(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_create_data: dict[str, Any],
    ) -> None:
        """
        Test create_language returns 500 when the service raises
        an unexpected exception.
        """
        # Arrange
        error_message = "Internal service failure"
        mock_language_service.create_language.side_effect = Exception(error_message)
        logger.info("Testing create_language with an unexpected service exception")

        # Act
        response = client.post("/languages/", json=sample_language_create_data)

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "Internal server error"
        assert data["detail"]["message"] == error_message
        logger.info("create_language exception handling test passed")


class TestUpdateLanguage:
    """Tests for the update_language handler."""

    def test_update_language_success(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_response: LanguageResponse,
        sample_language_id: UUID,
        sample_language_update_data: dict[str, Any],
    ) -> None:
        """
        Test update_language returns 200 and the updated language on success.
        """
        # Arrange
        mock_language_service.update_language.return_value = sample_language_response
        logger.info(f"Testing update_language for ID: {sample_language_id}")

        # Act
        response = client.put(
            f"/languages/{sample_language_id}", json=sample_language_update_data
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_language_response.id)
        mock_language_service.update_language.assert_called_once()
        logger.info("update_language success test passed")

    def test_update_language_not_found(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_id: UUID,
        sample_language_update_data: dict[str, Any],
    ) -> None:
        """
        Test update_language returns 404 when the language does not exist.
        """
        # Arrange
        mock_language_service.update_language.return_value = None
        logger.info(
            f"Testing update_language for non-existent ID: {sample_language_id}"
        )

        # Act
        response = client.put(
            f"/languages/{sample_language_id}", json=sample_language_update_data
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"]["error"] == "Language not found"
        mock_language_service.update_language.assert_called_once()
        logger.info("update_language not found test passed")

    def test_update_language_invalid_uuid(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_update_data: dict[str, Any],
    ) -> None:
        """
        Test update_language returns 422 for a malformed UUID.
        """
        # Arrange
        invalid_id = "not-a-valid-uuid"
        logger.info(f"Testing update_language with invalid ID: {invalid_id}")

        # Act
        response = client.put(
            f"/languages/{invalid_id}", json=sample_language_update_data
        )

        # Assert
        assert response.status_code == 422
        mock_language_service.update_language.assert_not_called()
        logger.info("update_language invalid UUID test passed")

    def test_update_language_conflict(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_id: UUID,
        sample_language_update_data: dict[str, Any],
    ) -> None:
        """
        Test update_language returns 409 when the service reports a conflict.
        """
        # Arrange
        error_message = "Language code en is already registered"
        mock_language_service.update_language.side_effect = ValueError(error_message)
        logger.info("Testing update_language with a data conflict")

        # Act
        response = client.put(
            f"/languages/{sample_language_id}", json=sample_language_update_data
        )

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error"] == "Conflict"
        assert data["detail"]["message"] == error_message
        logger.info("update_language conflict test passed")

    def test_update_language_handles_exception(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_id: UUID,
        sample_language_update_data: dict[str, Any],
    ) -> None:
        """
        Test update_language returns 500 for an unexpected service exception.
        """
        # Arrange
        error_message = "Database transaction failed"
        mock_language_service.update_language.side_effect = Exception(error_message)
        logger.info("Testing update_language with an unexpected service exception")

        # Act
        response = client.put(
            f"/languages/{sample_language_id}", json=sample_language_update_data
        )

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "Internal server error"
        assert data["detail"]["message"] == error_message
        logger.info("update_language exception handling test passed")


class TestDeleteLanguage:
    """Tests for the delete_language handler."""

    def test_delete_language_success(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_id: UUID,
    ) -> None:
        """
        Test delete_language returns 204 on successful deletion.
        """
        # Arrange
        mock_language_service.delete_language.return_value = True
        logger.info(f"Testing delete_language for ID: {sample_language_id}")

        # Act
        response = client.delete(f"/languages/{sample_language_id}")

        # Assert
        assert response.status_code == 204
        mock_language_service.delete_language.assert_called_once_with(
            sample_language_id
        )
        logger.info("delete_language success test passed")

    def test_delete_language_not_found(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_id: UUID,
    ) -> None:
        """
        Test delete_language returns 404 when the language does not exist.
        """
        # Arrange
        mock_language_service.delete_language.return_value = False
        logger.info(
            f"Testing delete_language for non-existent ID: {sample_language_id}"
        )

        # Act
        response = client.delete(f"/languages/{sample_language_id}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"] == "Language not found"
        mock_language_service.delete_language.assert_called_once_with(
            sample_language_id
        )
        logger.info("delete_language not found test passed")

    def test_delete_language_invalid_uuid(
        self, client: TestClient, mock_language_service: AsyncMock
    ) -> None:
        """
        Test delete_language returns 422 for a malformed UUID.
        """
        # Arrange
        invalid_id = "not-a-valid-uuid"
        logger.info(f"Testing delete_language with invalid ID: {invalid_id}")

        # Act
        response = client.delete(f"/languages/{invalid_id}")

        # Assert
        assert response.status_code == 422
        mock_language_service.delete_language.assert_not_called()
        logger.info("delete_language invalid UUID test passed")

    def test_delete_language_handles_exception(
        self,
        client: TestClient,
        mock_language_service: AsyncMock,
        sample_language_id: UUID,
    ) -> None:
        """
        Test delete_language returns 500 for an unexpected service exception.
        """
        # Arrange
        error_message = "Failed to delete language"
        mock_language_service.delete_language.side_effect = Exception(error_message)
        logger.info("Testing delete_language with an unexpected service exception")

        # Act
        response = client.delete(f"/languages/{sample_language_id}")

        # Assert
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "Internal server error"
        assert data["detail"]["message"] == error_message
        logger.info("delete_language exception handling test passed")
