"""
Unit tests for the User API handlers.

This module contains tests for the user API handler functions in isolation,
with the UserService dependency mocked.
"""

import logging
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4
import pytest
from pydantic import ValidationError

from app.application.dto.user_dto import UserCreate, UserUpdate, UserResponse
from app.presentation.api.v1.users import (
    create_user,
    delete_user,
    get_user_by_id,
    get_users,
    update_user,
)


# Configure logging for tests
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@pytest.fixture
def mock_user_service():
    """Fixture for a mocked user service."""
    return MagicMock()


@pytest.fixture(autouse=True)
def mock_container(mock_user_service):
    """
    Fixture to patch get_container to return a mock container
    with a mock user service.
    """
    mock_container_instance = MagicMock()
    mock_container_instance.get_user_service.return_value = mock_user_service
    
    with patch('app.presentation.api.v1.users.get_container') as mock_get_container:
        mock_get_container.return_value = mock_container_instance
        yield mock_get_container


@pytest.fixture
def sample_user_id() -> UUID:
    """Fixture for a sample user UUID."""
    return uuid4()


@pytest.fixture
def sample_user_response(sample_user_id: UUID) -> UserResponse:
    """Fixture for a sample UserResponse object."""
    return UserResponse(
        id=sample_user_id,
        email="test@example.com",
        username="testuser",
        firstName="Test",
        lastName="User",
        nativeLanguageId=uuid4(),
        currentLanguageId=uuid4(),
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
        lastActiveAt=None,
    )


@pytest.fixture
def sample_user_create_data() -> dict:
    """Fixture for sample user creation request body."""
    return {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "a-secure-password",
        "firstName": "New",
        "lastName": "User",
        "nativeLanguageId": str(uuid4()),
        "currentLanguageId": str(uuid4()),
    }


@pytest.fixture
def sample_user_update_data() -> dict:
    """Fixture for sample user update request body."""
    return {
        "email": "updated@example.com",
        "username": "updateduser",
        "firstName": "Updated",
        "lastName": "User",
    }


class TestGetUsers:
    """Tests for the get_users handler."""

    def test_get_users_success(self, mock_user_service, sample_user_response: UserResponse):
        """
        Test get_users returns 200 and a list of users on success.
        """
        # Arrange
        mock_user_service.get_all_users.return_value = [sample_user_response]
        logger.info("Testing get_users with a single user")

        # Act
        response, status_code = get_users()

        # Assert
        assert status_code == 200
        assert isinstance(response, list)
        assert len(response) == 1
        assert str(response[0]["id"]) == str(sample_user_response.id)
        assert response[0]["email"] == sample_user_response.email
        mock_user_service.get_all_users.assert_called_once_with(skip=0, limit=100)
        logger.info("get_users success test passed")

    def test_get_users_with_pagination(self, mock_user_service):
        """
        Test get_users correctly passes pagination parameters to the service.
        """
        # Arrange
        mock_user_service.get_all_users.return_value = []
        logger.info("Testing get_users with pagination skip=10, limit=50")

        # Act
        get_users(skip=10, limit=50)

        # Assert
        mock_user_service.get_all_users.assert_called_once_with(skip=10, limit=50)
        logger.info("get_users pagination test passed")

    def test_get_users_empty(self, mock_user_service):
        """
        Test get_users returns 200 and an empty list when no users exist.
        """
        # Arrange
        mock_user_service.get_all_users.return_value = []
        logger.info("Testing get_users with no users")

        # Act
        response, status_code = get_users()

        # Assert
        assert status_code == 200
        assert isinstance(response, list)
        assert len(response) == 0
        logger.info("get_users empty list test passed")

    def test_get_users_handles_exception(self, mock_user_service):
        """
        Test get_users returns 500 when the service raises an exception.
        """
        # Arrange
        error_message = "Database connection failed"
        mock_user_service.get_all_users.side_effect = Exception(error_message)
        logger.info("Testing get_users with a service exception")

        # Act
        response, status_code = get_users()

        # Assert
        assert status_code == 500
        assert response["error"] == "Internal server error"
        assert response["message"] == error_message
        logger.info("get_users exception handling test passed")


class TestGetUserById:
    """Tests for the get_user_by_id handler."""

    def test_get_user_by_id_success(self, mock_user_service, sample_user_response: UserResponse, sample_user_id: UUID):
        """
        Test get_user_by_id returns 200 and a user on success.
        """
        # Arrange
        mock_user_service.get_user.return_value = sample_user_response
        logger.info(f"Testing get_user_by_id with ID: {sample_user_id}")

        # Act
        response, status_code = get_user_by_id(str(sample_user_id))

        # Assert
        assert status_code == 200
        assert str(response["id"]) == str(sample_user_id)
        assert response["email"] == sample_user_response.email
        mock_user_service.get_user.assert_called_once_with(sample_user_id)
        logger.info("get_user_by_id success test passed")

    def test_get_user_by_id_not_found(self, mock_user_service, sample_user_id: UUID):
        """
        Test get_user_by_id returns 404 when the user does not exist.
        """
        # Arrange
        mock_user_service.get_user.return_value = None
        logger.info(f"Testing get_user_by_id with non-existent ID: {sample_user_id}")

        # Act
        response, status_code = get_user_by_id(str(sample_user_id))

        # Assert
        assert status_code == 404
        assert response["error"] == "User not found"
        mock_user_service.get_user.assert_called_once_with(sample_user_id)
        logger.info("get_user_by_id not found test passed")

    def test_get_user_by_id_invalid_uuid(self, mock_user_service):
        """
        Test get_user_by_id returns 400 for a malformed UUID.
        """
        # Arrange
        invalid_id = "not-a-valid-uuid"
        logger.info(f"Testing get_user_by_id with invalid ID: {invalid_id}")

        # Act
        response, status_code = get_user_by_id(invalid_id)

        # Assert
        assert status_code == 400
        assert response["error"] == "Invalid user ID format"
        mock_user_service.get_user.assert_not_called()
        logger.info("get_user_by_id invalid UUID test passed")

    def test_get_user_by_id_handles_exception(self, mock_user_service, sample_user_id: UUID):
        """
        Test get_user_by_id returns 500 when the service raises an exception.
        """
        # Arrange
        error_message = "Service unavailable"
        mock_user_service.get_user.side_effect = Exception(error_message)
        logger.info(f"Testing get_user_by_id with service exception for ID: {sample_user_id}")

        # Act
        response, status_code = get_user_by_id(str(sample_user_id))

        # Assert
        assert status_code == 500
        assert response["error"] == "Internal server error"
        assert response["message"] == error_message
        logger.info("get_user_by_id exception handling test passed")


class TestCreateUser:
    """Tests for the create_user handler."""

    def test_create_user_success(self, mock_user_service, sample_user_response: UserResponse, sample_user_create_data: dict):
        """
        Test create_user returns 201 and the created user on success.
        """
        # Arrange
        mock_user_service.create_user.return_value = sample_user_response
        logger.info(f"Testing create_user with email: {sample_user_create_data['email']}")

        # Act
        response, status_code = create_user(sample_user_create_data)

        # Assert
        assert status_code == 201
        assert str(response["id"]) == str(sample_user_response.id)
        assert response["email"] == sample_user_response.email

        # Verify the service was called with a UserCreate DTO
        mock_user_service.create_user.assert_called_once()
        call_args = mock_user_service.create_user.call_args[0]
        assert isinstance(call_args[0], UserCreate)
        assert call_args[0].email == sample_user_create_data["email"]
        logger.info("create_user success test passed")

    def test_create_user_invalid_body(self, mock_user_service, sample_user_create_data: dict):
        """
        Test create_user returns 400 for an invalid request body.
        """
        # Arrange
        del sample_user_create_data["email"]  # Make the data invalid
        logger.info("Testing create_user with missing email field")

        # Act
        response, status_code = create_user(sample_user_create_data)

        # Assert
        assert status_code == 400
        assert response["error"] == "Invalid input data"
        assert "email" in response["message"]
        mock_user_service.create_user.assert_not_called()
        logger.info("create_user invalid body test passed")

    def test_create_user_conflict(self, mock_user_service, sample_user_create_data: dict):
        """
        Test create_user returns 409 when the service reports a conflict.
        """
        # Arrange
        error_message = "User with this email already exists"
        mock_user_service.create_user.side_effect = ValueError(error_message)
        logger.info("Testing create_user with a data conflict (e.g., duplicate email)")

        # Act
        response, status_code = create_user(sample_user_create_data)

        # Assert
        assert status_code == 409
        assert response["error"] == "Conflict"
        assert response["message"] == error_message
        logger.info("create_user conflict test passed")

    def test_create_user_handles_exception(self, mock_user_service, sample_user_create_data: dict):
        """
        Test create_user returns 500 when the service raises an unexpected exception.
        """
        # Arrange
        error_message = "Internal service failure"
        mock_user_service.create_user.side_effect = Exception(error_message)
        logger.info("Testing create_user with an unexpected service exception")

        # Act
        response, status_code = create_user(sample_user_create_data)

        # Assert
        assert status_code == 500
        assert response["error"] == "Internal server error"
        assert response["message"] == error_message
        logger.info("create_user exception handling test passed")


class TestUpdateUser:
    """Tests for the update_user handler."""

    def test_update_user_success(self, mock_user_service, sample_user_response: UserResponse, sample_user_id: UUID, sample_user_update_data: dict):
        """
        Test update_user returns 200 and the updated user on success.
        """
        # Arrange
        mock_user_service.update_user.return_value = sample_user_response
        logger.info(f"Testing update_user for ID: {sample_user_id}")

        # Act
        response, status_code = update_user(str(sample_user_id), sample_user_update_data)

        # Assert
        assert status_code == 200
        assert str(response["id"]) == str(sample_user_response.id)

        # Verify the service was called correctly
        mock_user_service.update_user.assert_called_once()
        call_args = mock_user_service.update_user.call_args[0]
        assert call_args[0] == sample_user_id
        assert isinstance(call_args[1], UserUpdate)
        assert call_args[1].email == sample_user_update_data["email"]
        logger.info("update_user success test passed")

    def test_update_user_not_found(self, mock_user_service, sample_user_id: UUID, sample_user_update_data: dict):
        """
        Test update_user returns 404 when the user does not exist.
        """
        # Arrange
        mock_user_service.update_user.return_value = None
        logger.info(f"Testing update_user for non-existent ID: {sample_user_id}")

        # Act
        response, status_code = update_user(str(sample_user_id), sample_user_update_data)

        # Assert
        assert status_code == 404
        assert response["error"] == "User not found"
        mock_user_service.update_user.assert_called_once()
        logger.info("update_user not found test passed")

    def test_update_user_invalid_uuid(self, mock_user_service, sample_user_update_data: dict):
        """
        Test update_user returns 400 for a malformed UUID.
        """
        # Arrange
        invalid_id = "not-a-valid-uuid"
        logger.info(f"Testing update_user with invalid ID: {invalid_id}")

        # Act
        response, status_code = update_user(invalid_id, sample_user_update_data)

        # Assert
        assert status_code == 400
        assert response["error"] == "Invalid user ID format"
        mock_user_service.update_user.assert_not_called()
        logger.info("update_user invalid UUID test passed")

    def test_update_user_invalid_body(self, mock_user_service, sample_user_id: UUID):
        """
        Test update_user returns 400 for an invalid request body.
        """
        # Arrange
        invalid_body = {"email": "this-is-not-an-email"}
        logger.info("Testing update_user with invalid body")

        # Act
        response, status_code = update_user(str(sample_user_id), invalid_body)

        # Assert
        assert status_code == 400
        assert response["error"] == "Invalid input data"
        mock_user_service.update_user.assert_not_called()
        logger.info("update_user invalid body test passed")

    def test_update_user_conflict(self, mock_user_service, sample_user_id: UUID, sample_user_update_data: dict):
        """
        Test update_user returns 409 when the service reports a conflict.
        """
        # Arrange
        error_message = "Username already taken"
        mock_user_service.update_user.side_effect = ValueError(error_message)
        logger.info("Testing update_user with a data conflict")

        # Act
        response, status_code = update_user(str(sample_user_id), sample_user_update_data)

        # Assert
        assert status_code == 409
        assert response["error"] == "Conflict"
        assert response["message"] == error_message
        logger.info("update_user conflict test passed")

    def test_update_user_handles_exception(self, mock_user_service, sample_user_id: UUID, sample_user_update_data: dict):
        """
        Test update_user returns 500 for an unexpected service exception.
        """
        # Arrange
        error_message = "Database transaction failed"
        mock_user_service.update_user.side_effect = Exception(error_message)
        logger.info("Testing update_user with an unexpected service exception")

        # Act
        response, status_code = update_user(str(sample_user_id), sample_user_update_data)

        # Assert
        assert status_code == 500
        assert response["error"] == "Internal server error"
        assert response["message"] == error_message
        logger.info("update_user exception handling test passed")


class TestDeleteUser:
    """Tests for the delete_user handler."""

    def test_delete_user_success(self, mock_user_service, sample_user_id: UUID):
        """
        Test delete_user returns 204 on successful deletion.
        """
        # Arrange
        mock_user_service.delete_user.return_value = True
        logger.info(f"Testing delete_user for ID: {sample_user_id}")

        # Act
        response, status_code = delete_user(str(sample_user_id))

        # Assert
        assert status_code == 204
        assert response == {}
        mock_user_service.delete_user.assert_called_once_with(sample_user_id)
        logger.info("delete_user success test passed")

    def test_delete_user_not_found(self, mock_user_service, sample_user_id: UUID):
        """
        Test delete_user returns 404 when the user does not exist.
        """
        # Arrange
        mock_user_service.delete_user.return_value = False
        logger.info(f"Testing delete_user for non-existent ID: {sample_user_id}")

        # Act
        response, status_code = delete_user(str(sample_user_id))

        # Assert
        assert status_code == 404
        assert response["error"] == "User not found"
        mock_user_service.delete_user.assert_called_once_with(sample_user_id)
        logger.info("delete_user not found test passed")

    def test_delete_user_invalid_uuid(self, mock_user_service):
        """
        Test delete_user returns 400 for a malformed UUID.
        """
        # Arrange
        invalid_id = "not-a-valid-uuid"
        logger.info(f"Testing delete_user with invalid ID: {invalid_id}")

        # Act
        response, status_code = delete_user(invalid_id)

        # Assert
        assert status_code == 400
        assert response["error"] == "Invalid user ID format"
        mock_user_service.delete_user.assert_not_called()
        logger.info("delete_user invalid UUID test passed")

    def test_delete_user_handles_exception(self, mock_user_service, sample_user_id: UUID):
        """
        Test delete_user returns 500 for an unexpected service exception.
        """
        # Arrange
        error_message = "Failed to delete user"
        mock_user_service.delete_user.side_effect = Exception(error_message)
        logger.info("Testing delete_user with an unexpected service exception")

        # Act
        response, status_code = delete_user(str(sample_user_id))

        # Assert
        assert status_code == 500
        assert response["error"] == "Internal server error"
        assert response["message"] == error_message
        logger.info("delete_user exception handling test passed")
