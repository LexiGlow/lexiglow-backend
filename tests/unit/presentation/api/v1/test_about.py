"""
Test cases for the about API endpoints.
Tests both /about and /about/version endpoints using Flask test client.
"""

import sys
import os
import logging
import pytest


from scripts.wsgi import app

# Configure logging for test
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestAboutEndpoints:
    """Test class for about API endpoints."""

    def setup_method(self):
        """Set up test client for each test method."""
        self.client = app.test_client()

    def test_about_endpoint_success(self):
        """Test the /about endpoint returns correct response structure."""
        response = self.client.get("/about")

        # Assertions
        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = response.get_json()

        # Check required fields
        assert "service" in data
        assert "version" in data
        assert "description" in data
        assert "framework" in data
        assert "database" in data
        assert "api_documentation" in data
        assert "health_check" in data
        assert "status" in data

        # Check field values
        assert data["service"] == "LexiGlow Backend"
        assert data["version"] == "1.0.0"
        assert data["description"] == "REST API backend for LexiGlow application"
        assert data["framework"] == "Flask with Connexion"
        assert data["database"] == "MongoDB"
        assert data["api_documentation"] == "/ui"
        assert data["health_check"] == "/health"
        assert data["status"] == "operational"

        logger.info(f"About endpoint test passed: {data}")

    def test_about_endpoint_method_not_allowed(self):
        """Test that /about endpoint only accepts GET requests."""
        # Test POST method
        response = self.client.post("/about")
        assert response.status_code == 405  # Method Not Allowed

        # Test PUT method
        response = self.client.put("/about")
        assert response.status_code == 405

        # Test DELETE method
        response = self.client.delete("/about")
        assert response.status_code == 405

    def test_version_endpoint_success(self):
        """Test the /about/version endpoint returns correct response structure."""
        response = self.client.get("/about/version")

        # Assertions
        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = response.get_json()

        # Check required fields
        assert "version" in data
        assert "build_date" in data
        assert "python_version" in data
        assert "flask_version" in data
        assert "connexion_version" in data

        # Check field values
        assert data["version"] == "1.0.0"
        assert data["build_date"] == "2024-01-01"
        assert data["python_version"] == "3.13.7"
        assert data["flask_version"] == "3.0.0"
        assert data["connexion_version"] == "3.0.0"

        logger.info(f"Version endpoint test passed: {data}")

    def test_version_endpoint_method_not_allowed(self):
        """Test that /about/version endpoint only accepts GET requests."""
        # Test POST method
        response = self.client.post("/about/version")
        assert response.status_code == 405  # Method Not Allowed

        # Test PUT method
        response = self.client.put("/about/version")
        assert response.status_code == 405

        # Test DELETE method
        response = self.client.delete("/about/version")
        assert response.status_code == 405

    def test_about_endpoint_with_query_params(self):
        """Test that /about endpoint works with query parameters (should be ignored)."""
        response = self.client.get("/about?param1=value1&param2=value2")

        assert response.status_code == 200
        data = response.get_json()
        assert data["service"] == "LexiGlow Backend"

        logger.info("About endpoint with query params test passed")

    def test_version_endpoint_with_query_params(self):
        """Test that /about/version endpoint works with query parameters (should be ignored)."""
        response = self.client.get("/about/version?param1=value1&param2=value2")

        assert response.status_code == 200
        data = response.get_json()
        assert data["version"] == "1.0.0"

        logger.info("Version endpoint with query params test passed")

    def test_about_endpoint_response_headers(self):
        """Test that /about endpoint returns appropriate headers."""
        response = self.client.get("/about")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        # Check for CORS headers (if configured)
        # Note: CORS headers might not be present in test environment
        logger.info("About endpoint headers test passed")

    def test_version_endpoint_response_headers(self):
        """Test that /about/version endpoint returns appropriate headers."""
        response = self.client.get("/about/version")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        logger.info("Version endpoint headers test passed")

    def test_about_endpoint_json_structure(self):
        """Test that /about endpoint returns valid JSON structure."""
        response = self.client.get("/about")

        assert response.status_code == 200

        # This will raise an exception if JSON is invalid
        data = response.get_json()
        assert isinstance(data, dict)
        assert len(data) == 8  # Should have exactly 8 fields

        logger.info("About endpoint JSON structure test passed")

    def test_version_endpoint_json_structure(self):
        """Test that /about/version endpoint returns valid JSON structure."""
        response = self.client.get("/about/version")

        assert response.status_code == 200

        # This will raise an exception if JSON is invalid
        data = response.get_json()
        assert isinstance(data, dict)
        assert len(data) == 5  # Should have exactly 5 fields

        logger.info("Version endpoint JSON structure test passed")


def test_about_endpoint_integration():
    """Integration test for about endpoint using the app directly."""
    with app.test_client() as client:
        response = client.get("/about")
        assert response.status_code == 200
        data = response.get_json()
        assert data["service"] == "LexiGlow Backend"
        logger.info("About endpoint integration test passed")


def test_version_endpoint_integration():
    """Integration test for version endpoint using the app directly."""
    with app.test_client() as client:
        response = client.get("/about/version")
        assert response.status_code == 200
        data = response.get_json()
        assert data["version"] == "1.0.0"
        logger.info("Version endpoint integration test passed")


class TestDatabaseConnectionEndpoint:
    """Test class for database connection endpoint."""

    def setup_method(self):
        """Set up test client for each test method."""
        self.client = app.test_client()

    def test_db_test_endpoint_success_structure(self):
        """Test the /about/db-test endpoint returns correct response structure."""
        response = self.client.get("/about/db-test")

        # Should return either 200 (success) or 503 (connection failed)
        assert response.status_code in [200, 503]
        assert response.content_type == "application/json"

        data = response.get_json()

        # Check required fields
        assert "status" in data
        assert "message" in data
        assert "connected" in data

        # Check that connected is a boolean
        assert isinstance(data["connected"], bool)

        logger.info(f"Database test endpoint structure test passed: {data}")

    def test_db_test_endpoint_method_not_allowed(self):
        """Test that /about/db-test endpoint only accepts GET requests."""
        # Test POST method
        response = self.client.post("/about/db-test")
        assert response.status_code == 405  # Method Not Allowed

        # Test PUT method
        response = self.client.put("/about/db-test")
        assert response.status_code == 405

        # Test DELETE method
        response = self.client.delete("/about/db-test")
        assert response.status_code == 405

    def test_db_test_endpoint_with_query_params(self):
        """Test that /about/db-test endpoint works with query parameters."""
        response = self.client.get("/about/db-test?param1=value1&param2=value2")

        assert response.status_code in [200, 503]
        data = response.get_json()
        assert "status" in data
        assert "connected" in data

        logger.info("Database test endpoint with query params test passed")

    def test_db_test_endpoint_response_headers(self):
        """Test that /about/db-test endpoint returns appropriate headers."""
        response = self.client.get("/about/db-test")

        assert response.status_code in [200, 503]
        assert response.content_type == "application/json"

        logger.info("Database test endpoint headers test passed")

    def test_db_test_endpoint_json_structure(self):
        """Test that /about/db-test endpoint returns valid JSON structure."""
        response = self.client.get("/about/db-test")

        assert response.status_code in [200, 503]

        # This will raise an exception if JSON is invalid
        data = response.get_json()
        assert isinstance(data, dict)
        assert len(data) >= 3  # Should have at least status, message, connected

        logger.info("Database test endpoint JSON structure test passed")

    def test_db_test_endpoint_error_handling(self):
        """Test that /about/db-test endpoint handles errors gracefully."""
        response = self.client.get("/about/db-test")

        # Should not return 500 (internal server error) for connection issues
        assert response.status_code != 500

        data = response.get_json()

        # If connection fails, should have error details
        if not data.get("connected", False):
            assert "error_type" in data
            assert data["status"] == "error"

        logger.info("Database test endpoint error handling test passed")


def test_db_test_endpoint_integration():
    """Integration test for database test endpoint using the app directly."""
    with app.test_client() as client:
        response = client.get("/about/db-test")
        assert response.status_code in [200, 503]
        data = response.get_json()
        assert "status" in data
        assert "connected" in data
        logger.info("Database test endpoint integration test passed")
