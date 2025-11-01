# LexiGlow Scripts

This directory contains utility scripts for database management and other development tasks.

## Database Scripts

### create_sqlite_db.py

Creates the SQLite database with all tables, indexes, and triggers as defined in the schema file.

**Usage:**

```bash
# Create database at default location (data/lexiglow.db)
python scripts/create_sqlite_db.py

# Create database at custom location
python scripts/create_sqlite_db.py --db-path /path/to/database.db

# Force recreate existing database
python scripts/create_sqlite_db.py --force

# Enable verbose logging
python scripts/create_sqlite_db.py --verbose
```

**Options:**

- `--db-path PATH` - Path to the SQLite database file (default: `data/lexiglow.db`)
- `--force` - Force recreate database even if it exists
- `--verbose, -v` - Enable verbose debug logging

**What it does:**

1. Reads the SQL schema from `scripts/create_test_sqlite_db.sql`
2. Extracts SQL statements from the markdown file
3. Creates the database file at the specified location
4. Executes all SQL statements to create:
   - 8 tables (Language, User, UserLanguage, Text, UserVocabulary, UserVocabularyItem, TextTag, TextTagAssociation)
   - All indexes for performance optimization
   - 5 triggers for automatic timestamp updates
5. Verifies the database structure was created correctly

**Example output:**

```
2025-11-01 12:12:55,793 - __main__ - INFO - Reading schema from: .../create_db
2025-11-01 12:12:55,794 - __main__ - INFO - Extracted SQL from markdown-formatted file
2025-11-01 12:12:55,795 - __main__ - INFO - Parsed 39 SQL statements
2025-11-01 12:12:55,795 - __main__ - INFO - Creating database at: /tmp/test_lexiglow.db
2025-11-01 12:12:55,960 - __main__ - INFO - All statements executed successfully
2025-11-01 12:12:55,960 - __main__ - INFO - Created 8 tables
2025-11-01 12:12:55,960 - __main__ - INFO - Created 39 indexes
2025-11-01 12:12:55,960 - __main__ - INFO - Created 5 triggers
2025-11-01 12:12:55,961 - __main__ - INFO - ✅ Database created successfully
```

### seed_sqlite_db.py

Populates the SQLite database with random test data for development and testing purposes.

**Usage:**

```bash
# Seed database at default location
python scripts/seed_sqlite_db.py

# Seed database at custom location
python scripts/seed_sqlite_db.py --db-path /path/to/database.db

# Force reseed (clears existing data first)
python scripts/seed_sqlite_db.py --force

# Enable verbose logging
python scripts/seed_sqlite_db.py --verbose
```

**Options:**

- `--db-path PATH` - Path to the SQLite database file (default: from `SQLITE_DB_PATH` env var)
- `--force` - Force reseed (clears existing data first)
- `--verbose, -v` - Enable verbose debug logging

**What it does:**

1. Checks if the database file exists (must be created first using `create_sqlite_db.py`)
2. Optionally clears existing data if `--force` is specified
3. Seeds the database with test data:
   - **3 languages**: English, Russian, Serbian
   - **5 users**: Random users with realistic names and emails
   - **User-Language associations**: Each user learns 1-2 languages
   - **5 text tags**: fiction, news, business, education, technology
   - **6 texts**: 2 texts per language (English, Russian, Serbian) with different proficiency levels
   - **9 user vocabularies**: One vocabulary per user per language they're learning
   - **~30-40 vocabulary items**: 3-5 words per vocabulary with learning status
4. Maintains referential integrity with proper foreign key relationships

**Sample data includes:**

- Random user names (e.g., "johndoe", "janemiller")
- Sample texts in English, Russian, and Serbian
- Vocabulary items appropriate to each language
- Realistic timestamps (dates in the past)
- Various proficiency levels (A1-C2)
- Different learning statuses (NEW, LEARNING, KNOWN, MASTERED)

**Example output:**

```
2025-11-01 13:19:03,555 - __main__ - INFO - Starting database seeding...
2025-11-01 13:19:03,562 - __main__ - INFO - Seeding languages...
2025-11-01 13:19:03,570 - __main__ - INFO - Created 3 languages
2025-11-01 13:19:03,570 - __main__ - INFO - Seeding 5 users...
2025-11-01 13:19:03,574 - __main__ - INFO - Created 5 users
2025-11-01 13:19:03,606 - __main__ - INFO - ✅ Database seeded successfully!
2025-11-01 13:19:03,606 - __main__ - INFO - Seeded data summary:
2025-11-01 13:19:03,606 - __main__ - INFO -   - Languages: 3
2025-11-01 13:19:03,606 - __main__ - INFO -   - Users: 5
2025-11-01 13:19:03,606 - __main__ - INFO -   - Text Tags: 5
2025-11-01 13:19:03,606 - __main__ - INFO -   - Texts: 6
2025-11-01 13:19:03,606 - __main__ - INFO -   - User Vocabularies: 9
```

**Quick setup (create + seed):**

```bash
# Create and seed database in one command
python scripts/create_sqlite_db.py --force && python scripts/seed_sqlite_db.py --force
```

## Future Scripts

- **migrate_db.py** - Handle database migrations
- **backup_db.py** - Create database backups

