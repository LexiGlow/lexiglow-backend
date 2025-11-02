#!/usr/bin/env python3
"""
Test script for SQLite connection and session management.

This script demonstrates how to use the SQLite connection and session
management modules.
"""

import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.infrastructure.database.sqlite import (
    get_connection,
    get_session,
    execute_query,
    execute_insert,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_connection():
    """Test basic connection functionality."""
    logger.info("Testing SQLite connection...")

    # Get connection instance
    conn = get_connection(Path("/tmp/test_connection.db"))

    # Execute a simple query
    cursor = conn.execute("SELECT sqlite_version()")
    version = cursor.fetchone()[0]
    logger.info(f"SQLite version: {version}")

    # Close connection
    conn.close()
    logger.info("✅ Connection test passed")


def test_session():
    """Test session functionality."""
    logger.info("Testing SQLite session...")

    # Use session context manager
    with get_session(Path("/tmp/test_session.db")) as session:
        # Create a test table
        session.execute("""
            CREATE TABLE IF NOT EXISTS test_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
        session.commit()
        logger.info("Test table created")

        # Insert data with transaction
        with session.transaction():
            last_id = session.insert(
                "INSERT INTO test_users (username, email) VALUES (?, ?)",
                ("testuser1", "test1@example.com"),
            )
            logger.info(f"Inserted user with ID: {last_id}")

            session.insert(
                "INSERT INTO test_users (username, email) VALUES (?, ?)",
                ("testuser2", "test2@example.com"),
            )

        # Query data
        users = session.fetchall("SELECT * FROM test_users")
        logger.info(f"Found {len(users)} users:")
        for user in users:
            logger.info(f"  - ID: {user['id']}, Username: {user['username']}")

        # Update data
        updated = session.update(
            "UPDATE test_users SET email = ? WHERE username = ?",
            ("newemail@example.com", "testuser1"),
        )
        session.commit()
        logger.info(f"Updated {updated} rows")

        # Delete data
        deleted = session.delete(
            "DELETE FROM test_users WHERE username = ?", ("testuser2",)
        )
        session.commit()
        logger.info(f"Deleted {deleted} rows")

    logger.info("✅ Session test passed")


def test_helper_functions():
    """Test helper functions."""
    logger.info("Testing helper functions...")

    db_path = Path("/tmp/test_helpers.db")

    # Use helper to execute queries
    with get_session(db_path) as session:
        session.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        """)
        session.commit()

    # Insert using helper
    product_id = execute_insert(
        "INSERT INTO products (name, price) VALUES (?, ?)",
        ("Widget", 19.99),
        db_path=db_path,
    )
    logger.info(f"Inserted product with ID: {product_id}")

    # Query using helper
    products = execute_query("SELECT * FROM products", db_path=db_path)
    logger.info(f"Found {len(products)} products:")
    for product in products:
        logger.info(
            f"  - ID: {product['id']}, Name: {product['name']}, "
            f"Price: ${product['price']:.2f}"
        )

    logger.info("✅ Helper functions test passed")


def test_transaction_rollback():
    """Test transaction rollback on error."""
    logger.info("Testing transaction rollback...")

    with get_session(Path("/tmp/test_rollback.db")) as session:
        # Create table
        session.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                balance REAL NOT NULL
            )
        """)
        session.commit()

        # Insert initial data
        with session.transaction():
            session.insert(
                "INSERT INTO accounts (name, balance) VALUES (?, ?)",
                ("Alice", 1000.0),
            )

        # Try transaction that will fail
        try:
            with session.transaction():
                session.update(
                    "UPDATE accounts SET balance = balance - ? WHERE name = ?",
                    (500.0, "Alice"),
                )
                # This will fail (violates NOT NULL constraint)
                session.insert("INSERT INTO accounts (name, balance) VALUES (?, ?)", ("Bob", None))
        except Exception as e:
            logger.info(f"Transaction failed as expected: {e}")

        # Check that rollback worked
        accounts = session.fetchall("SELECT * FROM accounts")
        logger.info(f"Accounts after rollback: {len(accounts)}")
        for account in accounts:
            logger.info(
                f"  - Name: {account['name']}, Balance: ${account['balance']:.2f}"
            )

        # Alice's balance should still be 1000
        alice = session.fetchone("SELECT * FROM accounts WHERE name = ?", ("Alice",))
        assert alice["balance"] == 1000.0, "Rollback failed!"

    logger.info("✅ Transaction rollback test passed")


def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("SQLite Connection and Session Management Tests")
    logger.info("=" * 60)

    try:
        test_connection()
        print()
        test_session()
        print()
        test_helper_functions()
        print()
        test_transaction_rollback()

        logger.info("=" * 60)
        logger.info("✅ All tests passed!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())

