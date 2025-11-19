"""
Response models for API endpoints.

This module defines Pydantic models used as response schemas for FastAPI
endpoints. These models are used for automatic validation, serialization,
and OpenAPI documentation.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., example="ok")


class AboutResponse(BaseModel):
    """Response model for about endpoint."""

    service: str = Field(..., example="LexiGlow Backend")
    version: str = Field(..., example="1.0.0")
    description: str = Field(..., example="REST API backend for LexiGlow application")
    framework: str = Field(..., example="FastAPI")
    database: str = Field(..., example="sqlite")
    api_documentation: str = Field(..., example="/docs")
    health_check: str = Field(..., example="/health")
    status: str = Field(..., example="operational")


class VersionResponse(BaseModel):
    """Response model for version endpoint."""

    version: str = Field(..., example="1.0.0")
    build_date: str = Field(..., example="2024-01-01")
    python_version: str = Field(..., example="3.13.7")
    fastapi_version: str = Field(..., example="0.104.0")
    uvicorn_version: str = Field(..., example="0.24.0")


class ErrorResponse(BaseModel):
    """Standardized error response model."""

    error: str = Field(..., example="An error occurred")
    message: str = Field(..., example="Detailed error message")
