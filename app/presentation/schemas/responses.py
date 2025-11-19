"""
Response models for API endpoints.

This module defines Pydantic models used as response schemas for FastAPI
endpoints. These models are used for automatic validation, serialization,
and OpenAPI documentation.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., examples=["ok"])


class AboutResponse(BaseModel):
    """Response model for about endpoint."""

    service: str = Field(..., examples=["LexiGlow Backend"])
    version: str = Field(..., examples=["1.0.0"])
    description: str = Field(
        ..., examples=["REST API backend for LexiGlow application"]
    )
    framework: str = Field(..., examples=["FastAPI"])
    database: str = Field(..., examples=["sqlite"])
    api_documentation: str = Field(..., examples=["/docs"])
    health_check: str = Field(..., examples=["/health"])
    status: str = Field(..., examples=["operational"])


class VersionResponse(BaseModel):
    """Response model for version endpoint."""

    version: str = Field(..., examples=["1.0.0"])
    build_date: str = Field(..., examples=["2024-01-01"])
    python_version: str = Field(..., examples=["3.13.7"])
    fastapi_version: str = Field(..., examples=["0.104.0"])
    uvicorn_version: str = Field(..., examples=["0.24.0"])


class ErrorResponse(BaseModel):
    """Standardized error response model."""

    error: str = Field(..., examples=["An error occurred"])
    message: str = Field(..., examples=["Detailed error message"])
