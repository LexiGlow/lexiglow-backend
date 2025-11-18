"""
Shared fixtures for MongoDB repository tests.
"""

from collections.abc import Generator

import pytest
from pymongo import MongoClient


@pytest.fixture(scope="session")
def db_url() -> str:
    """Database URL with credentials for testing."""
    return "mongodb://admin:password123@localhost:27017/"


@pytest.fixture(scope="function")
def mongo_client(db_url: str) -> Generator[MongoClient, None, None]:
    """Provides a PyMongo client for testing."""
    client: MongoClient = MongoClient(db_url, uuidRepresentation="standard")
    yield client
    client.close()
