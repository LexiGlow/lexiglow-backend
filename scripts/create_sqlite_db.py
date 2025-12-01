#!/usr/bin/env python3
"""SQLite Database Creation Script for LexiGlow using SQLAlchemy.

This script creates the SQLite database and all necessary tables based on the
SQLAlchemy ORM models.

Usage:
    python scripts/create_sqlite_db.py [--db-path PATH] [--force] [--verbose]
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Ensure the app directory is in the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.infrastructure.database.sqlite.models import Base

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# Configuration
SQLITE_DB_PATH = BASE_DIR / os.getenv("SQLITE_DB_PATH", "data/lexiglow.db")


def create_database(db_path: Path, force: bool = False) -> None:
    """Creates an SQLite database from SQLAlchemy models.

    Args:
        db_path (Path): The path where the database file should be created.
        force (bool): If True, deletes the existing database file before creation.

    Raises:
        FileExistsError: If the database file already exists and `force` is False.
        SQLAlchemyError: If an error occurs during database creation.
    """
    if db_path.exists():
        if not force:
            raise FileExistsError(
                f"Database already exists at {db_path}. Use --force to recreate."
            )
        logger.warning(f"Force mode: Removing existing database at {db_path}")
        db_path.unlink()

    db_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Creating database at: {db_path}")

    try:
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=engine)
        logger.info("All tables created successfully based on SQLAlchemy models.")

    except SQLAlchemyError as e:
        logger.error(f"Failed to create database: {e}")
        if db_path.exists():
            db_path.unlink()
        raise

    logger.info(f"✅ Database created successfully at: {db_path}")


def main():
    """Parses command-line arguments and orchestrates database creation."""
    parser = argparse.ArgumentParser(
        description="Create SQLite database for LexiGlow from SQLAlchemy models.",
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

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        create_database(args.db_path, args.force)
        logger.info("=" * 60)
        logger.info("Database setup complete!")
        logger.info(f"Database location: {args.db_path.absolute()}")
        logger.info("=" * 60)
        return 0
    except (FileExistsError, SQLAlchemyError) as e:
        logger.error(str(e))
        return 1
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
