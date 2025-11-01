"""
SQLite database connection management.

This module handles SQLite database connections, including connection pooling,
configuration, and lifecycle management.
"""

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from app.core.config import BASE_DIR

logger = logging.getLogger(__name__)


class SQLiteConnection:
    """
    SQLite connection manager.

    Manages database connections with proper configuration and lifecycle handling.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize SQLite connection manager.

        Args:
            db_path: Path to SQLite database file. If None, uses SQLITE_DB_PATH from env.
        """
        if db_path is None:
            import os

            db_path = BASE_DIR / os.getenv("SQLITE_DB_PATH", "data/lexiglow.db")

        self.db_path = Path(db_path)
        self._connection: Optional[sqlite3.Connection] = None

        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"SQLite connection manager initialized for: {self.db_path}")

    @property
    def connection(self) -> sqlite3.Connection:
        """
        Get or create database connection.

        Returns:
            Active SQLite connection
        """
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection

    def _create_connection(self) -> sqlite3.Connection:
        """
        Create a new SQLite connection with proper configuration.

        Returns:
            Configured SQLite connection
        """
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,  # Allow multi-threaded access
                timeout=30.0,  # Wait up to 30 seconds for locks
            )

            # Enable foreign key constraints
            conn.execute("PRAGMA foreign_keys = ON")

            # Enable Write-Ahead Logging for better concurrency
            conn.execute("PRAGMA journal_mode = WAL")

            # Optimize for performance
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
            conn.execute("PRAGMA temp_store = MEMORY")

            # Return rows as sqlite3.Row objects for dict-like access
            conn.row_factory = sqlite3.Row

            logger.info(f"SQLite connection established: {self.db_path}")
            return conn

        except sqlite3.Error as e:
            logger.error(f"Failed to connect to SQLite database: {e}")
            raise

    def close(self) -> None:
        """Close the database connection if it exists."""
        if self._connection is not None:
            try:
                self._connection.close()
                logger.info("SQLite connection closed")
            except sqlite3.Error as e:
                logger.error(f"Error closing SQLite connection: {e}")
            finally:
                self._connection = None

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Execute a SQL query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Cursor with query results
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise

    def executemany(self, query: str, params_list: list) -> sqlite3.Cursor:
        """
        Execute a SQL query with multiple parameter sets.

        Args:
            query: SQL query string
            params_list: List of parameter tuples

        Returns:
            Cursor with query results
        """
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            return cursor
        except sqlite3.Error as e:
            logger.error(f"Batch query execution failed: {e}")
            logger.error(f"Query: {query}")
            raise

    def commit(self) -> None:
        """Commit the current transaction."""
        try:
            self.connection.commit()
            logger.debug("Transaction committed")
        except sqlite3.Error as e:
            logger.error(f"Commit failed: {e}")
            raise

    def rollback(self) -> None:
        """Rollback the current transaction."""
        try:
            self.connection.rollback()
            logger.debug("Transaction rolled back")
        except sqlite3.Error as e:
            logger.error(f"Rollback failed: {e}")
            raise

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        Usage:
            with db.transaction():
                db.execute("INSERT INTO ...")
                db.execute("UPDATE ...")
            # Automatically commits on success, rolls back on exception
        """
        try:
            yield self
            self.commit()
        except Exception as e:
            self.rollback()
            logger.error(f"Transaction failed, rolled back: {e}")
            raise

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close()
        return False

    def __del__(self):
        """Destructor - ensure connection is closed."""
        self.close()


# Global connection instance
_connection_instance: Optional[SQLiteConnection] = None


def get_connection(db_path: Optional[Path] = None) -> SQLiteConnection:
    """
    Get or create a global SQLite connection instance.

    Args:
        db_path: Optional path to database file

    Returns:
        SQLite connection manager instance
    """
    global _connection_instance

    if _connection_instance is None:
        _connection_instance = SQLiteConnection(db_path)

    return _connection_instance


def close_connection() -> None:
    """Close the global SQLite connection."""
    global _connection_instance

    if _connection_instance is not None:
        _connection_instance.close()
        _connection_instance = None
