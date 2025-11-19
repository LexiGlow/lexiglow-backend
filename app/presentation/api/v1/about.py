"""
About API endpoints.
This module provides information about the LexiGlow backend service.
"""

import logging
import os
import sys

from fastapi import APIRouter

from app.presentation.schemas.responses import AboutResponse, VersionResponse

logger = logging.getLogger(__name__)

# Create router for about endpoints
router = APIRouter()


@router.get(
    "/about",
    response_model=AboutResponse,
    status_code=200,
    summary="Get information about the service",
    description="Returns general information about the LexiGlow backend service",
)
def get_about() -> AboutResponse:
    """
    Get information about the LexiGlow backend service.

    Returns:
        AboutResponse: Service information including version, framework, and database
    """
    logger.info("About endpoint accessed")

    return AboutResponse(
        service="LexiGlow Backend",
        version="1.0.0",
        description="REST API backend for LexiGlow application",
        framework="FastAPI",
        database=os.getenv("ACTIVE_DATABASE_TYPE", "sqlite"),
        api_documentation="/docs",
        health_check="/health",
        status="operational",
    )


@router.get(
    "/about/version",
    response_model=VersionResponse,
    status_code=200,
    summary="Get service version details",
    description=(
        "Returns detailed version information for the service and its dependencies"
    ),
)
def get_version() -> VersionResponse:
    """
    Get version information for the service.

    Returns:
        VersionResponse: Detailed version information including Python,
            FastAPI, and Uvicorn versions
    """
    logger.info("Version endpoint accessed")

    # Get package versions dynamically
    try:
        import fastapi
        import uvicorn

        fastapi_version = fastapi.__version__
        uvicorn_version = uvicorn.__version__
    except (ImportError, AttributeError):
        fastapi_version = "unknown"
        uvicorn_version = "unknown"

    return VersionResponse(
        version="1.0.0",
        build_date="2024-01-01",
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        fastapi_version=fastapi_version,
        uvicorn_version=uvicorn_version,
    )
