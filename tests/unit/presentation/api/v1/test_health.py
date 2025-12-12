"""Test cases for the health API endpoint."""

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


def test_health():
    """Test the health endpoint returns correct response."""
    # Test the health endpoint
    client = TestClient(app)
    res = client.get(f"{API_V1}/health")

    # Assertions
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
    assert res.headers["content-type"] == "application/json"

    logger.info(f"Health endpoint test passed: {res.json()}")
