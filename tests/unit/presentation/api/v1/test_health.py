import sys, os
import logging


from scripts.wsgi import app

# Configure logging for test
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_health():
    """Test the health endpoint returns correct response."""

    # Test the health endpoint
    client = app.test_client()
    res = client.get("/health")

    # Assertions
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}
    assert res.content_type == "application/json"

    logger.info(f"Health endpoint test passed: {res.get_json()}")
