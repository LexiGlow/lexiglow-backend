# SQLite Database Infrastructure

This module provides SQLite database connection, session management, and ORM models for the LexiGlow application.

## Overview

The SQLite infrastructure consists of three main components:

1. **`connection.py`** - Low-level connection management with connection pooling and configuration
2. **`session.py`** - High-level session management with transaction handling and convenience methods
3. **`models.py`** - SQLAlchemy ORM models for object-oriented database access

## Features

- ✅ **Connection pooling** with singleton pattern
- ✅ **Automatic transaction management** with context managers
- ✅ **WAL (Write-Ahead Logging)** enabled for better concurrency
- ✅ **Foreign key constraints** enabled
- ✅ **Row factory** configured for dict-like access
- ✅ **Performance optimizations** (cache size, synchronous mode, temp storage)
- ✅ **Comprehensive error handling** and logging
- ✅ **Type hints** for better IDE support

## Quick Start

### Basic Connection

```python
from app.infrastructure.database.sqlite import get_connection

# Get global connection instance
conn = get_connection()

# Execute a query
cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
user = cursor.fetchone()

# Commit changes
conn.commit()
```

### Using Sessions (Recommended)

```python
from app.infrastructure.database.sqlite import get_session

# Use session context manager
with get_session() as session:
    # Query data
    user = session.fetchone("SELECT * FROM users WHERE id = ?", (user_id,))
    
    # Insert data with automatic transaction
    with session.transaction():
        session.insert(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            ("john", "john@example.com")
        )
        session.update(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now(), user_id)
        )
```

### Helper Functions

For simple operations, use the convenience functions:

```python
from app.infrastructure.database.sqlite import (
    execute_query,
    execute_insert,
    execute_update,
    execute_delete
)

# Query
users = execute_query("SELECT * FROM users WHERE active = ?", (True,))

# Insert
user_id = execute_insert(
    "INSERT INTO users (username, email) VALUES (?, ?)",
    ("jane", "jane@example.com")
)

# Update
rows_updated = execute_update(
    "UPDATE users SET email = ? WHERE username = ?",
    ("newemail@example.com", "jane")
)

# Delete
rows_deleted = execute_delete(
    "DELETE FROM users WHERE id = ?",
    (user_id,)
)
```

## Connection Management

### SQLiteConnection Class

The `SQLiteConnection` class manages database connections with proper configuration:

```python
from pathlib import Path
from app.infrastructure.database.sqlite import SQLiteConnection

# Create connection with custom path
conn = SQLiteConnection(Path("/path/to/database.db"))

# Execute queries
cursor = conn.execute("SELECT * FROM users")

# Transaction context manager
with conn.transaction():
    conn.execute("INSERT INTO users ...")
    conn.execute("UPDATE logs ...")
# Automatically commits or rolls back on error

# Close connection
conn.close()
```

### Connection Configuration

Connections are configured with:
- **Foreign keys enabled**: `PRAGMA foreign_keys = ON`
- **WAL mode**: `PRAGMA journal_mode = WAL`
- **Normal synchronous**: `PRAGMA synchronous = NORMAL`
- **64MB cache**: `PRAGMA cache_size = -64000`
- **Memory temp storage**: `PRAGMA temp_store = MEMORY`
- **Row factory**: `sqlite3.Row` for dict-like access

### Global Connection

Use `get_connection()` to get a singleton connection instance:

```python
from app.infrastructure.database.sqlite import get_connection, close_connection

# Get global connection
conn = get_connection()

# Use connection...

# Close global connection when done (e.g., at app shutdown)
close_connection()
```

## Session Management

### SQLiteSession Class

The `SQLiteSession` class provides high-level database operations:

```python
from app.infrastructure.database.sqlite import create_session

session = create_session()

# Query operations
user = session.fetchone("SELECT * FROM users WHERE id = ?", (1,))
users = session.fetchall("SELECT * FROM users WHERE active = ?", (True,))
some_users = session.fetchmany("SELECT * FROM users", size=10)

# Insert with last row ID
user_id = session.insert(
    "INSERT INTO users (username, email) VALUES (?, ?)",
    ("alice", "alice@example.com")
)

# Update with affected rows count
updated = session.update(
    "UPDATE users SET email = ? WHERE id = ?",
    ("new@example.com", user_id)
)

# Delete with affected rows count
deleted = session.delete("DELETE FROM users WHERE id = ?", (user_id,))

# Batch operations
session.executemany(
    "INSERT INTO users (username, email) VALUES (?, ?)",
    [("user1", "u1@example.com"), ("user2", "u2@example.com")]
)

# Manual transaction control
session.commit()
session.rollback()
```

### Transaction Management

Transactions are handled automatically with context managers:

```python
from app.infrastructure.database.sqlite import get_session

with get_session() as session:
    # Use transaction context
    with session.transaction():
        # All operations within this block are part of one transaction
        session.insert("INSERT INTO accounts ...")
        session.update("UPDATE balances ...")
        session.delete("DELETE FROM logs ...")
    # Automatically commits on success, rolls back on exception
    
    # Nested transactions are supported (though SQLite doesn't support true nesting)
    with session.transaction():
        with session.transaction():
            session.insert("INSERT INTO ...")
        # Inner transaction commits
    # Outer transaction commits
```

### Error Handling

```python
from app.infrastructure.database.sqlite import get_session

with get_session() as session:
    try:
        with session.transaction():
            session.insert("INSERT INTO users ...")
            # This will fail due to NOT NULL constraint
            session.insert("INSERT INTO users (username) VALUES (NULL)")
    except Exception as e:
        # Transaction automatically rolled back
        print(f"Transaction failed: {e}")
        # Previous insert was rolled back
```

## Row Access

Results are returned as `sqlite3.Row` objects, which support both index and key access:

```python
with get_session() as session:
    user = session.fetchone("SELECT id, username, email FROM users WHERE id = ?", (1,))
    
    # Access by index
    user_id = user[0]
    
    # Access by column name (dict-like)
    username = user["username"]
    email = user["email"]
    
    # Convert to dict
    user_dict = dict(user)
```

## Environment Configuration

The default database path is configured via the `SQLITE_DB_PATH` environment variable in `.env`:

```bash
# .env file
SQLITE_DB_PATH=data/lexiglow.db
```

You can override this in your code:

```python
from pathlib import Path
from app.infrastructure.database.sqlite import get_connection

# Use custom database path
conn = get_connection(Path("/custom/path/database.db"))
```

## Best Practices

### 1. Use Context Managers

Always use context managers for automatic resource cleanup:

```python
# Good
with get_session() as session:
    result = session.fetchone("SELECT ...")

# Avoid
session = create_session()
result = session.fetchone("SELECT ...")
session.close()  # Easy to forget!
```

### 2. Use Transactions

Group related operations in transactions:

```python
with get_session() as session:
    with session.transaction():
        # All or nothing - atomic operation
        session.insert("INSERT INTO orders ...")
        session.update("UPDATE inventory ...")
        session.insert("INSERT INTO audit_log ...")
```

### 3. Use Parameterized Queries

Always use parameter substitution to prevent SQL injection:

```python
# Good
session.execute("SELECT * FROM users WHERE username = ?", (username,))

# BAD - SQL injection vulnerability!
session.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

### 4. Handle Errors Gracefully

```python
from app.infrastructure.database.sqlite import get_session
import sqlite3

with get_session() as session:
    try:
        with session.transaction():
            session.insert("INSERT INTO ...")
    except sqlite3.IntegrityError as e:
        # Handle unique constraint violations, etc.
        logger.error(f"Integrity error: {e}")
    except sqlite3.Error as e:
        # Handle other database errors
        logger.error(f"Database error: {e}")
```

## Testing

A comprehensive test suite is available at `scripts/test_sqlite_session.py`:

```bash
# Run tests
python scripts/test_sqlite_session.py
```

Tests cover:
- Basic connection functionality
- Session operations (CRUD)
- Transaction management
- Helper functions
- Rollback behavior

## Performance Considerations

### Connection Pooling

The module uses a singleton pattern for connection management. The same connection instance is reused across the application, which is efficient for SQLite's single-writer model.

### WAL Mode

Write-Ahead Logging (WAL) is enabled for better concurrency:
- Readers don't block writers
- Writers don't block readers
- Better performance for most workloads

### Cache Configuration

A 64MB cache is configured for better performance with larger datasets.

## Limitations

### SQLite Constraints

Be aware of SQLite's limitations:
- **Single writer**: Only one write operation at a time
- **No true nested transactions**: SQLite uses savepoints, but we simplify this
- **Limited concurrency**: Not suitable for high-concurrency write scenarios
- **Type system**: SQLite's dynamic typing may differ from expectations

### Thread Safety

While `check_same_thread=False` is set, it's recommended to use one connection per thread in multi-threaded applications, or use proper locking mechanisms.

## ORM Models

### Using SQLAlchemy ORM

The module provides full SQLAlchemy ORM models for all database tables:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.database.sqlite.models import Base, User, Language, TextModel

# Create engine and session
engine = create_engine("sqlite:///data/lexiglow.db")
SessionLocal = sessionmaker(bind=engine)

# Use ORM models
with SessionLocal() as session:
    # Query
    user = session.query(User).filter_by(username="john").first()
    print(f"User: {user.email}")
    
    # Access relationships
    print(f"Native language: {user.native_language.name}")
    print(f"Learning: {len(user.user_languages)} languages")
    
    # Create
    new_lang = Language(
        id=str(uuid.uuid4()),
        name="French",
        code="fr",
        nativeName="Français"
    )
    session.add(new_lang)
    session.commit()
```

### Available ORM Models

- **`Language`** - Supported languages
- **`User`** - Application users
- **`UserLanguage`** - Junction table for users learning languages
- **`TextModel`** - Reading materials and content
- **`TextTag`** - Tags for categorizing texts
- **`TextTagAssociation`** - Junction table for texts and tags
- **`UserVocabulary`** - User vocabulary collections
- **`UserVocabularyItem`** - Individual vocabulary items

### Model Relationships

All models include SQLAlchemy relationships for easy navigation:

```python
with SessionLocal() as session:
    # Get user with all relationships
    user = session.query(User).filter_by(id=user_id).first()
    
    # Access related data through relationships
    native_lang = user.native_language  # Language model
    texts = user.texts  # List of TextModel
    vocabularies = user.vocabularies  # List of UserVocabulary
    
    # Access nested relationships
    for vocab in user.vocabularies:
        print(f"Vocabulary: {vocab.name}")
        for item in vocab.items:
            print(f"  - {item.term}: {item.status}")
```

### Creating Tables

Use SQLAlchemy's `Base.metadata` to create tables:

```python
from sqlalchemy import create_engine
from app.infrastructure.database.sqlite.models import Base

engine = create_engine("sqlite:///data/lexiglow.db")
Base.metadata.create_all(engine)
```

## Examples

- See `scripts/test_sqlite_session.py` for raw SQL/session examples
- See `scripts/test_orm_models.py` for comprehensive ORM examples

## API Reference

### Connection Module

- `SQLiteConnection(db_path)` - Connection manager class
- `get_connection(db_path)` - Get global connection instance
- `close_connection()` - Close global connection

### Session Module

- `SQLiteSession(connection)` - Session manager class
- `create_session(connection)` - Create new session
- `get_session(db_path)` - Session context manager
- `execute_query(query, params, db_path)` - Execute query helper
- `execute_insert(query, params, db_path)` - Execute insert helper
- `execute_update(query, params, db_path)` - Execute update helper
- `execute_delete(query, params, db_path)` - Execute delete helper

## Logging

The module uses Python's `logging` module. Configure your logging to see debug information:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

Log levels:
- **DEBUG**: Connection lifecycle, transactions
- **INFO**: Connection establishment, query execution
- **ERROR**: Query failures, connection errors

