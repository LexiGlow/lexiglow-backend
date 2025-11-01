"""
SQLite session management.

This module provides session management for SQLite database operations,
including transaction handling and connection lifecycle management.
"""

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.infrastructure.database.sqlite.connection import (
    SQLiteConnection,
    get_connection,
)

logger = logging.getLogger(__name__)


class SQLiteSession:
    """
    SQLite session manager for database operations.

    Provides a high-level interface for database operations with
    automatic transaction management and error handling.
    """

    def __init__(self, connection: Optional[SQLiteConnection] = None):
        """
        Initialize SQLite session.

        Args:
            connection: SQLite connection manager. If None, uses global connection.
        """
        self._connection = connection or get_connection()
        self._in_transaction = False
        logger.debug("SQLite session initialized")

    @property
    def connection(self) -> SQLiteConnection:
        """Get the underlying connection."""
        return self._connection

    def execute(
        self, query: str, params: Union[tuple, Dict[str, Any]] = ()
    ) -> sqlite3.Cursor:
        """
        Execute a SQL query.

        Args:
            query: SQL query string
            params: Query parameters (tuple or dict)

        Returns:
            Cursor with query results
        """
        return self._connection.execute(query, params)

    def fetchone(
        self, query: str, params: Union[tuple, Dict[str, Any]] = ()
    ) -> Optional[sqlite3.Row]:
        """
        Execute query and fetch one result.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Single row or None
        """
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def fetchall(
        self, query: str, params: Union[tuple, Dict[str, Any]] = ()
    ) -> List[sqlite3.Row]:
        """
        Execute query and fetch all results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of rows
        """
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def fetchmany(
        self, query: str, size: int, params: Union[tuple, Dict[str, Any]] = ()
    ) -> List[sqlite3.Row]:
        """
        Execute query and fetch multiple results.

        Args:
            query: SQL query string
            size: Number of rows to fetch
            params: Query parameters

        Returns:
            List of rows (up to size)
        """
        cursor = self.execute(query, params)
        return cursor.fetchmany(size)

    def insert(self, query: str, params: Union[tuple, Dict[str, Any]] = ()) -> int:
        """
        Execute INSERT query and return last inserted row ID.

        Args:
            query: INSERT query string
            params: Query parameters

        Returns:
            Last inserted row ID
        """
        cursor = self.execute(query, params)
        return cursor.lastrowid

    def update(self, query: str, params: Union[tuple, Dict[str, Any]] = ()) -> int:
        """
        Execute UPDATE query and return number of affected rows.

        Args:
            query: UPDATE query string
            params: Query parameters

        Returns:
            Number of affected rows
        """
        cursor = self.execute(query, params)
        return cursor.rowcount

    def delete(self, query: str, params: Union[tuple, Dict[str, Any]] = ()) -> int:
        """
        Execute DELETE query and return number of affected rows.

        Args:
            query: DELETE query string
            params: Query parameters

        Returns:
            Number of affected rows
        """
        cursor = self.execute(query, params)
        return cursor.rowcount

    def executemany(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute query with multiple parameter sets.

        Args:
            query: SQL query string
            params_list: List of parameter tuples

        Returns:
            Number of affected rows
        """
        cursor = self._connection.executemany(query, params_list)
        return cursor.rowcount

    def commit(self) -> None:
        """Commit the current transaction."""
        self._connection.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self._connection.rollback()

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        Usage:
            with session.transaction():
                session.insert("INSERT INTO ...")
                session.update("UPDATE ...")
            # Automatically commits on success, rolls back on exception
        """
        if self._in_transaction:
            # Nested transaction - just yield
            yield self
            return

        self._in_transaction = True
        try:
            yield self
            self.commit()
            logger.debug("Transaction committed successfully")
        except Exception as e:
            self.rollback()
            logger.error(f"Transaction failed and rolled back: {e}")
            raise
        finally:
            self._in_transaction = False

    def close(self) -> None:
        """Close the session and underlying connection."""
        self._connection.close()
        logger.debug("SQLite session closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type is not None:
            self.rollback()
        return False


# Session factory functions


def create_session(connection: Optional[SQLiteConnection] = None) -> SQLiteSession:
    """
    Create a new SQLite session.

    Args:
        connection: Optional SQLite connection. If None, uses global connection.

    Returns:
        New SQLite session instance
    """
    return SQLiteSession(connection)


@contextmanager
def get_session(db_path: Optional[Path] = None):
    """
    Context manager for SQLite sessions.

    Usage:
        with get_session() as session:
            result = session.fetchone("SELECT * FROM users WHERE id = ?", (user_id,))

    Args:
        db_path: Optional path to database file

    Yields:
        SQLite session instance
    """
    connection = get_connection(db_path) if db_path else get_connection()
    session = SQLiteSession(connection)
    try:
        yield session
    finally:
        # Note: We don't close the connection here as it's a global singleton
        pass


# Helper functions for common patterns


def execute_query(
    query: str, params: Union[tuple, Dict[str, Any]] = (), db_path: Optional[Path] = None
) -> List[sqlite3.Row]:
    """
    Execute a query and return all results.

    Args:
        query: SQL query string
        params: Query parameters
        db_path: Optional database path

    Returns:
        List of result rows
    """
    with get_session(db_path) as session:
        return session.fetchall(query, params)


def execute_insert(
    query: str, params: Union[tuple, Dict[str, Any]] = (), db_path: Optional[Path] = None
) -> int:
    """
    Execute an INSERT query and return the last row ID.

    Args:
        query: INSERT query string
        params: Query parameters
        db_path: Optional database path

    Returns:
        Last inserted row ID
    """
    with get_session(db_path) as session:
        with session.transaction():
            return session.insert(query, params)


def execute_update(
    query: str, params: Union[tuple, Dict[str, Any]] = (), db_path: Optional[Path] = None
) -> int:
    """
    Execute an UPDATE query and return affected rows count.

    Args:
        query: UPDATE query string
        params: Query parameters
        db_path: Optional database path

    Returns:
        Number of affected rows
    """
    with get_session(db_path) as session:
        with session.transaction():
            return session.update(query, params)


def execute_delete(
    query: str, params: Union[tuple, Dict[str, Any]] = (), db_path: Optional[Path] = None
) -> int:
    """
    Execute a DELETE query and return affected rows count.

    Args:
        query: DELETE query string
        params: Query parameters
        db_path: Optional database path

    Returns:
        Number of affected rows
    """
    with get_session(db_path) as session:
        with session.transaction():
            return session.delete(query, params)

