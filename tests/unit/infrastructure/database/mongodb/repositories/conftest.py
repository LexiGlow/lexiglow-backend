"""
Shared fixtures for MongoDB repository tests.
"""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient


@pytest.fixture(scope="session")
def db_url() -> str:
    """Database URL with credentials for testing."""
    return "mongodb://admin:password123@localhost:27017/"


@pytest_asyncio.fixture(scope="function")
async def mongo_client(db_url: str) -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Provides an AsyncIOMotorClient for testing."""
    client: AsyncIOMotorClient = AsyncIOMotorClient(
        db_url, uuidRepresentation="standard"
    )
    yield client
    client.close()
