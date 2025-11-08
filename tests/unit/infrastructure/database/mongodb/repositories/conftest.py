"""
Shared fixtures for MongoDB repository tests.
"""

import pytest
from pymongo import MongoClient


@pytest.fixture(scope="session")
def db_url():
    """Database URL with credentials for testing."""
    return "mongodb://admin:password123@localhost:27017/"


@pytest.fixture(scope="function")
def mongo_client(db_url):
    """Provides a PyMongo client for testing."""
    client = MongoClient(db_url, uuidRepresentation="standard")
    yield client
    client.close()
