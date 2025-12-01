"""Health check endpoint for monitoring service availability."""

import logging

from fastapi import APIRouter

from app.presentation.schemas.responses import HealthResponse

logger = logging.getLogger(__name__)

# Create router for health check endpoints
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=200,
    summary="Health check",
    description="Check if the service is running and healthy",
)
async def get_health() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse: Status indicating service health
    """
    logger.info("Health check endpoint was called")
    return HealthResponse(status="ok")
