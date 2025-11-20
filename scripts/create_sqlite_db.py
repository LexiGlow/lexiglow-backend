#!/usr/bin/env python3
"""SQLite Database Creation Script for LexiGlow.

This script creates the SQLite database with all tables, indexes, and triggers
as defined in the schema file. It can parse SQL from both raw .sql files
and markdown files containing SQL code blocks.

Usage:
    python scripts/create_sqlite_db.py [--db-path PATH] [--force] [--verbose]
"""

import argparse
import logging
import os
import re
import sqlite3
import sys
from pathlib import Path

from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# Configuration
SCHEMA_FILE = SCRIPTS_DIR / "create_test_sqlite_db.sql"
SQLITE_DB_PATH = BASE_DIR / os.getenv("SQLITE_DB_PATH", "data/lexiglow.db")


def extract_sql_from_file(file_path: Path) -> str:
    """Extracts SQL code from a file.

    This function supports both pure .sql files and markdown files with
    fenced SQL code blocks (```sql).

    Args:
        file_path (Path): The path to the SQL or markdown file.

    Returns:
        str: The extracted SQL code as a single string.

    Raises:
        FileNotFoundError: If the specified schema file does not exist.
        ValueError: If no SQL code can be found in the file.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Schema file not found: {file_path}")

    logger.info(f"Reading schema from: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # If it's a .sql file, return content directly
    if file_path.suffix == ".sql":
        logger.info("Processing pure SQL file")
        return content

    # Otherwise, try to extract from markdown
    sql_pattern = r"```sql\s*(.*?)\s*```"
    matches = re.findall(sql_pattern, content, re.DOTALL)

    if matches:
        sql_code = "\n\n".join(matches)
        logger.info(f"Extracted {len(matches)} SQL code block(s) from markdown")
        return sql_code

    # Fallback: try extracting from markdown format without code blocks
    lines = content.split("\n")
    if lines and lines[0].startswith("##"):
        sql_lines = []
        in_sql = False
        for line in lines:
            if line.startswith("#"):
                continue
            if line.strip() == "```sql":
                in_sql = True
                continue
            if line.strip() == "```" and in_sql:
                in_sql = False
                continue
            if line.strip() and not line.startswith("```"):
                sql_lines.append(line)

        if sql_lines:
            sql_code = "\n".join(sql_lines)
            logger.info("Extracted SQL from markdown-formatted file")
            return sql_code

    raise ValueError("No SQL code found in schema file")


def split_sql_statements(sql_code: str) -> list[str]:
    """Splits a string of SQL code into individual statements.

    This function correctly handles multi-line statements and complex
    constructs like triggers, which end with `END;`.

    Args:
        sql_code (str): The complete SQL code as a single string.

    Returns:
        list[str]: A list of individual, stripped SQL statements.
    """
    # Remove comments
    sql_code = re.sub(r"--.*?$", "", sql_code, flags=re.MULTILINE)

    statements = []
    current_statement = []
    in_trigger = False

    for line in sql_code.split("\n"):
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Check for trigger start
        if stripped.upper().startswith("CREATE TRIGGER"):
            in_trigger = True

        current_statement.append(line)

        # Check for statement end
        if stripped.endswith(";"):
            if in_trigger:
                # Triggers end with END;
                if stripped.upper() == "END;":
                    statements.append("\n".join(current_statement))
                    current_statement = []
                    in_trigger = False
            else:
                # Regular statement
                statements.append("\n".join(current_statement))
                current_statement = []

    return [stmt.strip() for stmt in statements if stmt.strip()]


def create_database(db_path: Path, sql_code: str, force: bool = False) -> None:
    """Creates an SQLite database from a SQL schema.

    This function establishes a connection to the database file, executes
    all provided SQL statements to build the schema, and verifies the
    creation of tables, indexes, and triggers.

    Args:
        db_path (Path): The path where the database file should be created.
        sql_code (str): A string containing the complete SQL schema.
        force (bool): If True, deletes the existing database file before
            creation. Defaults to False.

    Raises:
        FileExistsError: If the database file already exists and `force` is False.
        sqlite3.Error: If an error occurs during SQL execution.
    """
    # Check if database already exists
    if db_path.exists():
        if not force:
            raise FileExistsError(
                f"Database already exists at {db_path}. Use --force to recreate."
            )
        logger.warning(f"Force mode: Removing existing database at {db_path}")
        db_path.unlink()

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Split SQL into statements
    statements = split_sql_statements(sql_code)
    logger.info(f"Parsed {len(statements)} SQL statements")

    # Create database and execute statements
    logger.info(f"Creating database at: {db_path}")

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")

        # Execute each statement
        for i, statement in enumerate(statements, 1):
            try:
                # Determine statement type for logging
                stmt_type = statement.split()[0:2]
                stmt_desc = " ".join(stmt_type).upper()

                logger.debug(f"Executing statement {i}/{len(statements)}: {stmt_desc}")
                cursor.execute(statement)

            except sqlite3.Error as e:
                logger.error(f"Error executing statement {i}:")
                logger.error(f"Statement: {statement[:100]}...")
                logger.error(f"Error: {e}")
                raise

        # Commit changes
        conn.commit()
        logger.info("All statements executed successfully")

        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        logger.info(f"Created {len(tables)} tables: {[t[0] for t in tables]}")

        # Verify indexes were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()
        logger.info(f"Created {len(indexes)} indexes")

        # Verify triggers were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
        triggers = cursor.fetchall()
        logger.info(f"Created {len(triggers)} triggers: {[t[0] for t in triggers]}")

    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        if db_path.exists():
            db_path.unlink()
        raise

    finally:
        conn.close()

    logger.info(f"✅ Database created successfully at: {db_path}")


def main():
    """Parses command-line arguments and orchestrates database creation.

    This function serves as the main entry point for the script. It handles
    argument parsing, sets the logging level, and calls the core functions
    to extract the SQL schema and create the database.
    """
    parser = argparse.ArgumentParser(
        description="Create SQLite database for LexiGlow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=SQLITE_DB_PATH,
        help=f"Path to SQLite database file (default: {SQLITE_DB_PATH})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force recreate database even if it exists",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose debug logging",
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Extract SQL from schema file
        sql_code = extract_sql_from_file(SCHEMA_FILE)

        # Create database
        create_database(args.db_path, sql_code, args.force)

        logger.info("=" * 60)
        logger.info("Database setup complete!")
        logger.info(f"Database location: {args.db_path.absolute()}")
        logger.info("=" * 60)

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except FileExistsError as e:
        logger.error(str(e))
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
