"""Test cases for the about API endpoints.

Tests both /api/v1/about and /api/v1/about/version endpoints using FastAPI's
TestClient.
"""

import logging

from fastapi.testclient import TestClient

from app.main import app

# Configure logging for test
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# API version prefix
API_V1 = "/api/v1"


class TestAboutEndpoints:
    """Test class for about API endpoints."""

    def setup_method(self):
        """Set up test client for each test method."""
        self.client = TestClient(app)

    def test_about_endpoint_success(self):
        """Test the /api/v1/about endpoint returns correct response structure."""
        response = self.client.get(f"{API_V1}/about")

        # Assertions
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()

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
        assert data["framework"] == "FastAPI"
        assert data["database"] in [
            "sqlite",
            "mongodb",
        ]
        assert data["api_documentation"] == "/docs"
        assert data["health_check"] == "/health"
        assert data["status"] == "operational"

        logger.info(f"About endpoint test passed: {data}")

    def test_about_endpoint_method_not_allowed(self):
        """Test that /api/v1/about endpoint only accepts GET requests."""
        response = self.client.post(f"{API_V1}/about")
        assert response.status_code == 405

        response = self.client.put(f"{API_V1}/about")
        assert response.status_code == 405

        response = self.client.delete(f"{API_V1}/about")
        assert response.status_code == 405

    def test_version_endpoint_success(self):
        """Test the /api/v1/about/version endpoint returns correct response."""
        response = self.client.get(f"{API_V1}/about/version")

        # Assertions
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()

        # Check required fields
        assert "version" in data
        assert "build_date" in data
        assert "python_version" in data
        assert "fastapi_version" in data

        # Check field values
        assert data["version"] == "1.0.0"
        assert data["build_date"] == "2024-01-01"
        assert data["python_version"]
        assert data["fastapi_version"]

        logger.info(f"Version endpoint test passed: {data}")

    def test_version_endpoint_method_not_allowed(self):
        """Test that /api/v1/about/version endpoint only accepts GET requests."""
        response = self.client.post(f"{API_V1}/about/version")
        assert response.status_code == 405

        response = self.client.put(f"{API_V1}/about/version")
        assert response.status_code == 405

        response = self.client.delete(f"{API_V1}/about/version")
        assert response.status_code == 405

    def test_about_endpoint_with_query_params(self):
        """Test that /api/v1/about endpoint works with query parameters."""
        response = self.client.get(f"{API_V1}/about?param1=value1&param2=value2")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "LexiGlow Backend"

        logger.info("About endpoint with query params test passed")

    def test_version_endpoint_with_query_params(self):
        """Test that /api/v1/about/version endpoint works with query parameters."""
        response = self.client.get(
            f"{API_V1}/about/version?param1=value1&param2=value2"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0.0"

        logger.info("Version endpoint with query params test passed")

    def test_about_endpoint_response_headers(self):
        """Test that /api/v1/about endpoint returns appropriate headers."""
        response = self.client.get(f"{API_V1}/about")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        logger.info("About endpoint headers test passed")

    def test_version_endpoint_response_headers(self):
        """Test that /api/v1/about/version endpoint returns appropriate headers."""
        response = self.client.get(f"{API_V1}/about/version")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        logger.info("Version endpoint headers test passed")

    def test_about_endpoint_json_structure(self):
        """Test that /api/v1/about endpoint returns valid JSON structure."""
        response = self.client.get(f"{API_V1}/about")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert len(data) >= 8

        logger.info("About endpoint JSON structure test passed")

    def test_version_endpoint_json_structure(self):
        """Test that /api/v1/about/version endpoint returns valid JSON structure."""
        response = self.client.get(f"{API_V1}/about/version")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert len(data) >= 4

        logger.info("Version endpoint JSON structure test passed")


def test_about_endpoint_integration():
    """Integration test for about endpoint using the app directly."""
    with TestClient(app) as client:
        response = client.get(f"{API_V1}/about")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "LexiGlow Backend"
        logger.info("About endpoint integration test passed")


def test_version_endpoint_integration():
    """Integration test for version endpoint using the app directly."""
    with TestClient(app) as client:
        response = client.get(f"{API_V1}/about/version")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0.0"
        logger.info("Version endpoint integration test passed")
