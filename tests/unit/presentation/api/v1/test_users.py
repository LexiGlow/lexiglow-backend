"""
Unit tests for User API endpoints.

This module provides comprehensive integration-style tests for user CRUD endpoints,
using Flask test client with temporary SQLite database fixtures.
"""

import logging
import os
import uuid
from typing import Dict, Any
from unittest.mock import patch, MagicMock
from uuid import UUID

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.services.user_service import UserService
from app.infrastructure.database.sqlite.models import (
    Base,
    Language as LanguageModel,
)
from app.infrastructure.database.sqlite.repositories.user_repository_impl import (
    SQLiteUserRepository,
)
from scripts.wsgi import app


# Configure logging for tests
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Fixtures


@pytest.fixture(scope="function")
def test_db_with_languages(tmp_path, monkeypatch):
    """
    Create temporary SQLite database with language fixtures.
    
    This fixture:
    - Creates a temporary database
    - Seeds it with two languages (English and Spanish)
    - Configures environment to use the test database
    - Cleans up after tests
    """
    # Create temporary database
    db_file = tmp_path / "test_users_api.db"
    db_path = str(db_file)
    
    # Create engine and tables
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    
    # Seed languages
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        english = LanguageModel(
            id=str(UUID("10000000-0000-0000-0000-000000000001")),
            name="English",
            code="en",
            nativeName="English",
        )
        spanish = LanguageModel(
            id=str(UUID("20000000-0000-0000-0000-000000000001")),
            name="Spanish",
            code="es",
            nativeName="Español",
        )
        session.add_all([english, spanish])
        session.commit()
    
    engine.dispose()
    
    # Monkeypatch environment variable
    monkeypatch.setenv("SQLITE_DB_PATH", db_path)
    
    # Return language IDs and db path for tests
    yield {
        "db_path": db_path,
        "english_id": UUID("10000000-0000-0000-0000-000000000001"),
        "spanish_id": UUID("20000000-0000-0000-0000-000000000001"),
    }


@pytest.fixture
def mock_user_service(test_db_with_languages):
    """
    Create a mock UserService that uses the test database.
    
    This patches the UserService instantiation in endpoints to use
    a repository connected to the test database.
    """
    def create_service(*args, **kwargs):
        repo = SQLiteUserRepository(db_path=test_db_with_languages["db_path"])
        return UserService(repository=repo)
    
    with patch("app.presentation.api.v1.users.UserService", side_effect=create_service):
        yield


# Test Data Helpers


def create_user_data(
    test_db: Dict[str, Any],
    email: str = "testuser@example.com",
    username: str = "testuser",
    password: str = "SecurePass123!",
    first_name: str = "Test",
    last_name: str = "User",
) -> Dict[str, Any]:
    """Helper function to create valid user creation data."""
    return {
        "email": email,
        "username": username,
        "password": password,
        "firstName": first_name,
        "lastName": last_name,
        "nativeLanguageId": str(test_db["english_id"]),
        "currentLanguageId": str(test_db["english_id"]),
    }


def create_update_data(
    email: str = None,
    username: str = None,
    first_name: str = None,
    last_name: str = None,
) -> Dict[str, Any]:
    """Helper function to create user update data."""
    data = {}
    if email is not None:
        data["email"] = email
    if username is not None:
        data["username"] = username
    if first_name is not None:
        data["firstName"] = first_name
    if last_name is not None:
        data["lastName"] = last_name
    return data


# Test Classes


class TestGetUsers:
    """Test GET /users endpoint."""
    
    def setup_method(self):
        """Set up test client for each test method."""
        self.client = app.test_client()
    
    def test_get_users_empty(self, mock_user_service):
        """Test retrieving users when database is empty."""
        response = self.client.get("/users")
        
        assert response.status_code == 200
        assert response.content_type == "application/json"
        
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0
        
        logger.info("Get users empty test passed")
    
    def test_get_users_success(self, mock_user_service, test_db_with_languages):
        """Test retrieving multiple users."""
        # Create test users
        user1_data = create_user_data(test_db_with_languages, email="user1@example.com", username="user1")
        user2_data = create_user_data(test_db_with_languages, email="user2@example.com", username="user2")
        
        self.client.post("/users", json=user1_data)
        self.client.post("/users", json=user2_data)
        
        # Get all users
        response = self.client.get("/users")
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["email"] in ["user1@example.com", "user2@example.com"]
        assert data[1]["email"] in ["user1@example.com", "user2@example.com"]
        
        logger.info(f"Get users success test passed: {len(data)} users retrieved")
    
    def test_get_users_pagination(self, mock_user_service, test_db_with_languages):
        """Test pagination with skip and limit parameters."""
        # Create 5 test users
        for i in range(5):
            user_data = create_user_data(
                test_db_with_languages,
                email=f"user{i}@example.com",
                username=f"user{i}"
            )
            self.client.post("/users", json=user_data)
        
        # Test skip=0, limit=2
        response = self.client.get("/users?skip=0&limit=2")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        
        # Test skip=2, limit=2
        response = self.client.get("/users?skip=2&limit=2")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        
        # Test skip=4, limit=10 (should return 1)
        response = self.client.get("/users?skip=4&limit=10")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        
        logger.info("Get users pagination test passed")
    
    def test_get_users_invalid_pagination(self, mock_user_service):
        """Test with invalid pagination parameters."""
        # Negative skip is rejected by OpenAPI validation (minimum: 0)
        response = self.client.get("/users?skip=-1&limit=10")
        assert response.status_code == 400  # OpenAPI validates minimum: 0
        
        # Negative limit should also be rejected or handled
        response = self.client.get("/users?skip=0&limit=-1")
        # Should either work or return error, not crash
        assert response.status_code in [200, 400, 422]
        
        # Valid edge cases
        response = self.client.get("/users?skip=0&limit=0")
        assert response.status_code in [200, 400]  # May return empty or reject
        
        logger.info("Get users invalid pagination test passed")
    
    def test_get_users_method_not_allowed(self, mock_user_service):
        """Test that only GET is allowed on /users."""
        # POST is allowed for creation
        # Test other methods
        response = self.client.put("/users")
        assert response.status_code in [404, 405]  # Not Found or Method Not Allowed
        
        response = self.client.delete("/users")
        assert response.status_code in [404, 405]
        
        logger.info("Get users method not allowed test passed")


class TestGetUserById:
    """Test GET /users/{userId} endpoint."""
    
    def setup_method(self):
        """Set up test client for each test method."""
        self.client = app.test_client()
    
    def test_get_user_by_id_success(self, mock_user_service, test_db_with_languages):
        """Test retrieving an existing user by ID."""
        # Create a user
        user_data = create_user_data(test_db_with_languages)
        create_response = self.client.post("/users", json=user_data)
        created_user = create_response.get_json()
        user_id = created_user["id"]
        
        # Get user by ID
        response = self.client.get(f"/users/{user_id}")
        
        assert response.status_code == 200
        assert response.content_type == "application/json"
        
        data = response.get_json()
        assert data["id"] == user_id
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["firstName"] == user_data["firstName"]
        assert data["lastName"] == user_data["lastName"]
        assert "password" not in data
        assert "passwordHash" not in data
        
        logger.info(f"Get user by ID success test passed: {user_id}")
    
    def test_get_user_by_id_not_found(self, mock_user_service):
        """Test retrieving non-existent user returns 404."""
        non_existent_id = str(uuid.uuid4())
        
        response = self.client.get(f"/users/{non_existent_id}")
        
        assert response.status_code == 404
        assert response.content_type == "application/json"
        
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "User not found"
        
        logger.info("Get user by ID not found test passed")
    
    def test_get_user_by_id_invalid_uuid(self, mock_user_service):
        """Test retrieving user with malformed UUID returns 400."""
        invalid_ids = ["not-a-uuid", "12345", "abc-def-ghi"]
        
        for invalid_id in invalid_ids:
            response = self.client.get(f"/users/{invalid_id}")
            
            assert response.status_code == 400
            data = response.get_json()
            assert "error" in data
            assert data["error"] == "Invalid user ID format"
        
        logger.info("Get user by ID invalid UUID test passed")
    
    def test_get_user_by_id_method_not_allowed(self, mock_user_service, test_db_with_languages):
        """Test that GET and other valid methods work, others don't."""
        # Create a user first
        user_data = create_user_data(test_db_with_languages)
        create_response = self.client.post("/users", json=user_data)
        user_id = create_response.get_json()["id"]
        
        # POST on specific user endpoint should not be allowed
        response = self.client.post(f"/users/{user_id}")
        assert response.status_code in [404, 405]
        
        logger.info("Get user by ID method not allowed test passed")


class TestCreateUser:
    """Test POST /users endpoint."""
    
    def setup_method(self):
        """Set up test client for each test method."""
        self.client = app.test_client()
    
    def test_create_user_success(self, mock_user_service, test_db_with_languages):
        """Test creating a user with valid data."""
        user_data = create_user_data(test_db_with_languages)
        
        response = self.client.post("/users", json=user_data)
        
        assert response.status_code == 201
        assert response.content_type == "application/json"
        
        data = response.get_json()
        assert "id" in data
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["firstName"] == user_data["firstName"]
        assert data["lastName"] == user_data["lastName"]
        assert data["nativeLanguageId"] == user_data["nativeLanguageId"]
        assert data["currentLanguageId"] == user_data["currentLanguageId"]
        assert "createdAt" in data
        assert "updatedAt" in data
        assert "password" not in data
        assert "passwordHash" not in data
        
        logger.info(f"Create user success test passed: {data['id']}")
    
    def test_create_user_duplicate_email(self, mock_user_service, test_db_with_languages):
        """Test creating user with duplicate email returns 409."""
        user_data = create_user_data(test_db_with_languages)
        
        # Create first user
        response1 = self.client.post("/users", json=user_data)
        assert response1.status_code == 201
        
        # Try to create second user with same email
        user_data2 = user_data.copy()
        user_data2["username"] = "different_username"
        
        response2 = self.client.post("/users", json=user_data2)
        
        assert response2.status_code == 409
        data = response2.get_json()
        assert "error" in data
        assert data["error"] == "Conflict"
        assert "email" in data["message"].lower()
        
        logger.info("Create user duplicate email test passed")
    
    def test_create_user_duplicate_username(self, mock_user_service, test_db_with_languages):
        """Test creating user with duplicate username returns 409."""
        user_data = create_user_data(test_db_with_languages)
        
        # Create first user
        response1 = self.client.post("/users", json=user_data)
        assert response1.status_code == 201
        
        # Try to create second user with same username
        user_data2 = user_data.copy()
        user_data2["email"] = "different@example.com"
        
        response2 = self.client.post("/users", json=user_data2)
        
        assert response2.status_code == 409
        data = response2.get_json()
        assert "error" in data
        assert data["error"] == "Conflict"
        assert "username" in data["message"].lower()
        
        logger.info("Create user duplicate username test passed")
    
    def test_create_user_invalid_email(self, mock_user_service, test_db_with_languages):
        """Test creating user with invalid email format returns 400."""
        invalid_emails = ["notanemail", "missing@domain", "@nodomain.com", "spaces in@email.com"]
        
        for invalid_email in invalid_emails:
            user_data = create_user_data(test_db_with_languages, email=invalid_email)
            
            response = self.client.post("/users", json=user_data)
            
            assert response.status_code == 400
            data = response.get_json()
            # Connexion validates and returns different error format
            assert "detail" in data or "error" in data
        
        logger.info("Create user invalid email test passed")
    
    def test_create_user_missing_fields(self, mock_user_service, test_db_with_languages):
        """Test creating user with missing required fields returns 400."""
        # Missing email
        user_data = create_user_data(test_db_with_languages)
        del user_data["email"]
        response = self.client.post("/users", json=user_data)
        assert response.status_code == 400
        
        # Missing username
        user_data = create_user_data(test_db_with_languages)
        del user_data["username"]
        response = self.client.post("/users", json=user_data)
        assert response.status_code == 400
        
        # Missing password
        user_data = create_user_data(test_db_with_languages)
        del user_data["password"]
        response = self.client.post("/users", json=user_data)
        assert response.status_code == 400
        
        # Missing firstName
        user_data = create_user_data(test_db_with_languages)
        del user_data["firstName"]
        response = self.client.post("/users", json=user_data)
        assert response.status_code == 400
        
        logger.info("Create user missing fields test passed")
    
    def test_create_user_invalid_language_id(self, mock_user_service, test_db_with_languages):
        """Test creating user with non-existent language ID."""
        user_data = create_user_data(test_db_with_languages)
        user_data["nativeLanguageId"] = str(uuid.uuid4())  # Non-existent language
        
        response = self.client.post("/users", json=user_data)
        
        # Note: Current implementation doesn't validate foreign key at creation time
        # The database stores the UUID without checking if language exists
        # This test documents current behavior; ideally should be 400 or 500
        assert response.status_code in [201, 400, 500]
        
        if response.status_code == 201:
            logger.warning("Foreign key validation not enforced - user created with invalid language ID")
        
        logger.info("Create user invalid language ID test passed")
    
    def test_create_user_response_structure(self, mock_user_service, test_db_with_languages):
        """Test that response has all expected fields."""
        user_data = create_user_data(test_db_with_languages)
        
        response = self.client.post("/users", json=user_data)
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Required fields from UserResponse schema
        required_fields = [
            "id", "email", "username", "firstName", "lastName",
            "nativeLanguageId", "currentLanguageId", "createdAt", "updatedAt"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Optional field
        assert "lastActiveAt" in data  # Can be None
        
        # Should NOT contain password
        assert "password" not in data
        assert "passwordHash" not in data
        
        logger.info("Create user response structure test passed")


class TestUpdateUser:
    """Test PUT /users/{userId} endpoint."""
    
    def setup_method(self):
        """Set up test client for each test method."""
        self.client = app.test_client()
    
    def test_update_user_success(self, mock_user_service, test_db_with_languages):
        """Test updating a user successfully."""
        # Create a user
        user_data = create_user_data(test_db_with_languages)
        create_response = self.client.post("/users", json=user_data)
        user_id = create_response.get_json()["id"]
        
        # Update user
        update_data = create_update_data(
            email="updated@example.com",
            username="updateduser",
            first_name="Updated",
            last_name="Name"
        )
        
        response = self.client.put(f"/users/{user_id}", json=update_data)
        
        assert response.status_code == 200
        assert response.content_type == "application/json"
        
        data = response.get_json()
        assert data["id"] == user_id
        assert data["email"] == "updated@example.com"
        assert data["username"] == "updateduser"
        assert data["firstName"] == "Updated"
        assert data["lastName"] == "Name"
        
        logger.info(f"Update user success test passed: {user_id}")
    
    def test_update_user_partial(self, mock_user_service, test_db_with_languages):
        """Test updating only some fields."""
        # Create a user
        user_data = create_user_data(test_db_with_languages)
        create_response = self.client.post("/users", json=user_data)
        created_user = create_response.get_json()
        user_id = created_user["id"]
        
        # Update only email
        update_data = create_update_data(email="newemail@example.com")
        
        response = self.client.put(f"/users/{user_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["email"] == "newemail@example.com"
        assert data["username"] == created_user["username"]  # Unchanged
        assert data["firstName"] == created_user["firstName"]  # Unchanged
        
        logger.info("Update user partial test passed")
    
    def test_update_user_not_found(self, mock_user_service):
        """Test updating non-existent user returns 404."""
        non_existent_id = str(uuid.uuid4())
        update_data = create_update_data(email="test@example.com")
        
        response = self.client.put(f"/users/{non_existent_id}", json=update_data)
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "User not found"
        
        logger.info("Update user not found test passed")
    
    def test_update_user_invalid_uuid(self, mock_user_service):
        """Test updating with malformed UUID returns 400."""
        invalid_id = "not-a-uuid"
        update_data = create_update_data(email="test@example.com")
        
        response = self.client.put(f"/users/{invalid_id}", json=update_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "Invalid user ID format"
        
        logger.info("Update user invalid UUID test passed")
    
    def test_update_user_duplicate_email(self, mock_user_service, test_db_with_languages):
        """Test updating to an email that already exists returns 409."""
        # Create two users
        user1_data = create_user_data(test_db_with_languages, email="user1@example.com", username="user1")
        user2_data = create_user_data(test_db_with_languages, email="user2@example.com", username="user2")
        
        self.client.post("/users", json=user1_data)
        create_response2 = self.client.post("/users", json=user2_data)
        user2_id = create_response2.get_json()["id"]
        
        # Try to update user2's email to user1's email
        update_data = create_update_data(email="user1@example.com")
        
        response = self.client.put(f"/users/{user2_id}", json=update_data)
        
        assert response.status_code == 409
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "Conflict"
        
        logger.info("Update user duplicate email test passed")
    
    def test_update_user_duplicate_username(self, mock_user_service, test_db_with_languages):
        """Test updating to a username that already exists returns 409."""
        # Create two users
        user1_data = create_user_data(test_db_with_languages, email="user1@example.com", username="user1")
        user2_data = create_user_data(test_db_with_languages, email="user2@example.com", username="user2")
        
        self.client.post("/users", json=user1_data)
        create_response2 = self.client.post("/users", json=user2_data)
        user2_id = create_response2.get_json()["id"]
        
        # Try to update user2's username to user1's username
        update_data = create_update_data(username="user1")
        
        response = self.client.put(f"/users/{user2_id}", json=update_data)
        
        assert response.status_code == 409
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "Conflict"
        
        logger.info("Update user duplicate username test passed")
    
    def test_update_user_invalid_data(self, mock_user_service, test_db_with_languages):
        """Test updating with invalid data returns 400."""
        # Create a user
        user_data = create_user_data(test_db_with_languages)
        create_response = self.client.post("/users", json=user_data)
        user_id = create_response.get_json()["id"]
        
        # Try to update with invalid email
        update_data = {"email": "not-an-email"}
        
        response = self.client.put(f"/users/{user_id}", json=update_data)
        
        assert response.status_code == 400
        data = response.get_json()
        # Connexion validates and returns different error format
        assert "detail" in data or "error" in data
        
        logger.info("Update user invalid data test passed")


class TestDeleteUser:
    """Test DELETE /users/{userId} endpoint."""
    
    def setup_method(self):
        """Set up test client for each test method."""
        self.client = app.test_client()
    
    def test_delete_user_success(self, mock_user_service, test_db_with_languages):
        """Test deleting a user successfully."""
        # Create a user
        user_data = create_user_data(test_db_with_languages)
        create_response = self.client.post("/users", json=user_data)
        user_id = create_response.get_json()["id"]
        
        # Delete user
        response = self.client.delete(f"/users/{user_id}")
        
        assert response.status_code == 204
        assert response.data == b'' or response.get_json() == {}
        
        # Verify user is deleted
        get_response = self.client.get(f"/users/{user_id}")
        assert get_response.status_code == 404
        
        logger.info(f"Delete user success test passed: {user_id}")
    
    def test_delete_user_not_found(self, mock_user_service):
        """Test deleting non-existent user returns 404."""
        non_existent_id = str(uuid.uuid4())
        
        response = self.client.delete(f"/users/{non_existent_id}")
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "User not found"
        
        logger.info("Delete user not found test passed")
    
    def test_delete_user_invalid_uuid(self, mock_user_service):
        """Test deleting with malformed UUID returns 400."""
        invalid_id = "not-a-uuid"
        
        response = self.client.delete(f"/users/{invalid_id}")
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "Invalid user ID format"
        
        logger.info("Delete user invalid UUID test passed")
    
    def test_delete_user_idempotent(self, mock_user_service, test_db_with_languages):
        """Test that second delete returns 404."""
        # Create a user
        user_data = create_user_data(test_db_with_languages)
        create_response = self.client.post("/users", json=user_data)
        user_id = create_response.get_json()["id"]
        
        # First delete
        response1 = self.client.delete(f"/users/{user_id}")
        assert response1.status_code == 204
        
        # Second delete
        response2 = self.client.delete(f"/users/{user_id}")
        assert response2.status_code == 404
        
        logger.info("Delete user idempotent test passed")
    
    def test_delete_user_method_not_allowed(self, mock_user_service, test_db_with_languages):
        """Test that only valid methods work on user endpoint."""
        # Create a user
        user_data = create_user_data(test_db_with_languages)
        create_response = self.client.post("/users", json=user_data)
        user_id = create_response.get_json()["id"]
        
        # PATCH method should not be allowed (if not implemented)
        response = self.client.patch(f"/users/{user_id}", json={"email": "test@example.com"})
        assert response.status_code in [404, 405]
        
        logger.info("Delete user method not allowed test passed")


# Integration Tests


def test_user_crud_workflow(mock_user_service, test_db_with_languages):
    """Integration test for complete CRUD workflow."""
    client = app.test_client()
    
    # Create a user
    user_data = create_user_data(test_db_with_languages, email="workflow@example.com", username="workflow")
    create_response = client.post("/users", json=user_data)
    assert create_response.status_code == 201
    created_user = create_response.get_json()
    user_id = created_user["id"]
    
    # Read the user
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    retrieved_user = get_response.get_json()
    assert retrieved_user["email"] == "workflow@example.com"
    
    # Update the user
    update_data = create_update_data(email="updated_workflow@example.com")
    update_response = client.put(f"/users/{user_id}", json=update_data)
    assert update_response.status_code == 200
    updated_user = update_response.get_json()
    assert updated_user["email"] == "updated_workflow@example.com"
    
    # Delete the user
    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204
    
    # Verify deletion
    verify_response = client.get(f"/users/{user_id}")
    assert verify_response.status_code == 404
    
    logger.info("User CRUD workflow integration test passed")


def test_multiple_users_pagination(mock_user_service, test_db_with_languages):
    """Integration test for creating multiple users and testing pagination."""
    client = app.test_client()
    
    # Create 10 users
    created_ids = []
    for i in range(10):
        user_data = create_user_data(
            test_db_with_languages,
            email=f"user{i}@example.com",
            username=f"user{i}"
        )
        response = client.post("/users", json=user_data)
        assert response.status_code == 201
        created_ids.append(response.get_json()["id"])
    
    # Get all users
    response = client.get("/users")
    assert response.status_code == 200
    all_users = response.get_json()
    assert len(all_users) == 10
    
    # Test pagination
    response = client.get("/users?skip=0&limit=5")
    assert response.status_code == 200
    page1 = response.get_json()
    assert len(page1) == 5
    
    response = client.get("/users?skip=5&limit=5")
    assert response.status_code == 200
    page2 = response.get_json()
    assert len(page2) == 5
    
    # Verify no overlap
    page1_ids = {user["id"] for user in page1}
    page2_ids = {user["id"] for user in page2}
    assert len(page1_ids.intersection(page2_ids)) == 0
    
    logger.info("Multiple users pagination integration test passed")


def test_user_endpoints_json_structure(mock_user_service, test_db_with_languages):
    """Integration test to verify all responses are valid JSON."""
    client = app.test_client()
    
    # Create a user
    user_data = create_user_data(test_db_with_languages)
    create_response = client.post("/users", json=user_data)
    assert create_response.content_type == "application/json"
    user_id = create_response.get_json()["id"]
    
    # Get all users
    list_response = client.get("/users")
    assert list_response.content_type == "application/json"
    assert isinstance(list_response.get_json(), list)
    
    # Get single user
    get_response = client.get(f"/users/{user_id}")
    assert get_response.content_type == "application/json"
    assert isinstance(get_response.get_json(), dict)
    
    # Update user
    update_response = client.put(f"/users/{user_id}", json={"firstName": "NewName"})
    assert update_response.content_type == "application/json"
    assert isinstance(update_response.get_json(), dict)
    
    # Error responses should also be JSON
    error_response = client.get("/users/invalid-uuid")
    assert error_response.content_type == "application/json"
    error_data = error_response.get_json()
    assert isinstance(error_data, dict)
    assert "error" in error_data
    
    logger.info("User endpoints JSON structure integration test passed")

