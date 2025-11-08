import logging

logger = logging.getLogger(__name__)


def get_health():
    """Simple health endpoint used by OpenAPI mapping."""
    logger.info("Health check endpoint was called.")
    return {"status": "ok"}, 200
