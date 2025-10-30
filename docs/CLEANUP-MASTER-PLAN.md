# Cleanup Master Plan - Tools & Tests Consolidation

## Current State Analysis

**CRITICAL ISSUES:**
- **268 Python files in /tools/** - Massive duplication and technical debt
- **36 Python test files** - Overlapping coverage, no unified runner
- **No helper library** - Every script reimplements database connections
- **No test isolation** - Tests interfere with each other, database locking
- **Broken one-off scripts** - Many obsolete tools still present

---

## Phase 1: Helper Library Creation (lib/helpers/)

### 1.1 Create Core Helper Modules

**lib/helpers/db_utils.py** - Database connection patterns
```python
"""Database connection utilities for all tools and tests"""
import os
import psycopg2
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Optional, Dict, Any

load_dotenv()

def get_db_config() -> Dict[str, str]:
    """Get database configuration from environment"""
    return {
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'dbname': os.getenv('POSTGRES_DB')
    }

@contextmanager
def get_db_connection(autocommit: bool = False):
    """Context manager for database connections
    
    Usage:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM characters")
    """
    conn = None
    try:
        config = get_db_config()
        conn = psycopg2.connect(**config)
        if autocommit:
            conn.autocommit = True
        yield conn
        if not autocommit:
            conn.commit()
    except Exception as e:
        if conn and not autocommit:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def execute_query(query: str, params: Optional[tuple] = None, fetch: str = 'all') -> Any:
    """Execute a query and return results
    
    Args:
        query: SQL query string
        params: Query parameters (optional)
        fetch: 'all', 'one', or 'none'
    
    Returns:
        Query results based on fetch parameter
    """
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        
        if fetch == 'all':
            return cur.fetchall()
        elif fetch == 'one':
            return cur.fetchone()
        else:
            return None

def get_character_id(character_name: str) -> Optional[int]:
    """Get character ID by name or street name"""
    query = """
        SELECT id FROM characters 
        WHERE LOWER(name) = LOWER(%s) 
           OR LOWER(street_name) = LOWER(%s)
        LIMIT 1
    """
    result = execute_query(query, (character_name, character_name), fetch='one')
    return result[0] if result else None
```

**lib/helpers/test_utils.py** - Test isolation and fixtures
```python
"""Test utilities for isolated, transaction-based testing"""
import psycopg2
from contextlib import contextmanager
from typing import Generator, Dict, Any
from .db_utils import get_db_config

@contextmanager
def isolated_test_db() -> Generator[psycopg2.extensions.connection, None, None]:
    """Provide isolated database connection with automatic rollback
    
    All changes made within this context are rolled back after the test.
    This prevents test pollution and database locking.
    
    Usage:
        def test_something():
            with isolated_test_db() as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO characters ...")
                # Test assertions here
            # Automatic rollback - no permanent changes
    """
    conn = None
    try:
        config = get_db_config()
        conn = psycopg2.connect(**config)
        conn.autocommit = False
        
        # Start transaction
        cur = conn.cursor()
        cur.execute("BEGIN")
        
        yield conn
        
    finally:
        if conn:
            # Always rollback - never commit test data
            conn.rollback()
            conn.close()

def create_test_character(conn, name: str = "Test Character") -> int:
    """Create a test character and return ID"""
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO characters (name, street_name, metatype, body, quickness, strength, 
                               charisma, intelligence, willpower, essence, magic, reaction)
        VALUES (%s, %s, 'Human', 3, 3, 3, 3, 3, 3, 6.0, 0, 3)
        RETURNING id
    """, (name, name))
    return cur.fetchone()[0]

def cleanup_test_data(conn, character_id: int):
    """Clean up test character and related data"""
    cur = conn.cursor()
    tables = [
        'character_spells',
        'character_modifiers', 
        'character_gear',
        'character_skills',
        'characters'
    ]
    for table in tables:
        cur.execute(f"DELETE FROM {table} WHERE character_id = %s", (character_id,))
```

**lib/helpers/logging_utils.py** - Standardized logging
```python
"""Logging utilities for consistent output"""
import logging
import sys
from typing import Optional

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up a logger with consistent formatting
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (default INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Format: [2025-10-29 00:23:45] INFO: Message
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger

def log_operation(logger: logging.Logger, operation: str, details: Optional[str] = None):
    """Log an operation with consistent formatting"""
    msg = f"[{operation}]"
    if details:
        msg += f" {details}"
    logger.info(msg)
```

**lib/helpers/validation_utils.py** - Common validation patterns
```python
"""Validation utilities for data integrity"""
from typing import Any, List, Optional, Dict
import re

def validate_character_name(name: str) -> bool:
    """Validate character name format"""
    if not name or len(name) < 2:
        return False
    # Allow letters, numbers, spaces, hyphens, apostrophes
    return bool(re.match(r"^[A-Za-z0-9\s\-']+$", name))

def validate_attribute_value(value: int, min_val: int = 1, max_val: int = 20) -> bool:
    """Validate attribute is within valid range"""
    return min_val <= value <= max_val

def validate_skill_rating(rating: int) -> bool:
    """Validate skill rating (0-12 in SR2)"""
    return 0 <= rating <= 12

def validate_essence(essence: float) -> bool:
    """Validate essence value (0.0-6.0)"""
    return 0.0 <= essence <= 6.0

def check_required_fields(data: Dict[str, Any], required: List[str]) -> List[str]:
    """Check for missing required fields
    
    Returns:
        List of missing field names (empty if all present)
    """
    return [field for field in required if field not in data or data[field] is None]
```

---

## Phase 2: Tool Consolidation

### 2.1 Tool Categories & Reorganization

**Create organized structure:**
```
tools/
├── __init__.py
├── import/          # Data import scripts
│   ├── import_characters.py (consolidated)
│   ├── import_spells.py
│   └── import_gear.py
├── check/           # Validation/diagnostic scripts
│   ├── check_schema.py (consolidated)
│   ├── check_characters.py
│   └── check_modifiers.py
├── fix/             # Repair/migration scripts
│   ├── apply_migration.py (consolidated)
│   └── fix_schema.py
├── test/            # Test utilities (move to tests/)
└── archive/         # Obsolete scripts (for reference)
```

### 2.2 Scripts to Consolidate

**Import Scripts (11 versions → 1)**
- Consolidate: import-characters-v6.py through v11.py
- Keep: `tools/import/import_characters.py` (latest version)
- Archive: All older versions

**Check Scripts (80+ → 10)**
- Consolidate all `check-*-schema.py` → `tools/check/check_schema.py`
- Consolidate all `check-*-modifiers.py` → `tools/check/check_modifiers.py`
- Consolidate all `check-platinum-*.py` → `tools/check/check_character.py --name Platinum`
- Archive: All duplicates

**Fix Scripts (30+ → 5)**
- Consolidate all `fix-*-schema.py` → `tools/fix/fix_schema.py`
- Consolidate all `apply-*-migration.py` → `tools/fix/apply_migration.py`
- Archive: All duplicates

**Test Scripts (Move to tests/)**
- Move all `test-*.py` from tools/ to tests/
- Consolidate with existing test files

### 2.3 Deletion Candidates (Archive First)

**Obsolete/Broken Scripts:**
- All `*-v[0-9].py` files (keep only latest version)
- All `debug-*.py` files (one-off debugging)
- All `compare-*.py` files (one-off comparisons)
- All `show-*.py` files (one-off displays)
- All `find-*.py` files (one-off searches)

**Estimated Reduction: 268 → 30 files (89% reduction)**

---

## Phase 3: Test Suite Consolidation

### 3.1 Test Organization

**New structure:**
```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_runner.py           # Unified test runner
├── unit/                    # Pure logic tests (no DB)
│   ├── test_dice_roller.py
│   ├── test_drain_parser.py
│   └── test_validators.py
├── integration/             # Database tests
│   ├── test_character_crud.py
│   ├── test_spellcasting.py
│   ├── test_modifiers.py
│   └── test_campaign.py
├── mcp/                     # MCP tool tests
│   ├── test_mcp_character.py
│   ├── test_mcp_spellcasting.py
│   └── test_mcp_campaign.py
├── api/                     # API endpoint tests
│   ├── test_game_server.py
│   └── test_crud_api.py
└── e2e/                     # End-to-end tests
    ├── test_character_sheet_ui.py
    └── test_spellcasting_ui.py
```

### 3.2 Test Consolidation

**Character Tests (8 files → 2)**
- Consolidate: test-character-*.py files
- Result: `tests/integration/test_character_crud.py`, `tests/e2e/test_character_sheet_ui.py`

**Spellcasting Tests (5 files → 2)**
- Consolidate: test-spellcasting-*.py, test-cast-spell.py
- Result: `tests/integration/test_spellcasting.py`, `tests/mcp/test_mcp_spellcasting.py`

**CRUD Tests (4 files → 1)**
- Consolidate: test-crud-*.py, test-all-crud-operations.py
- Result: `tests/integration/test_character_crud.py`

**MCP Tests (4 files → 3)**
- Consolidate by functionality
- Result: test_mcp_character.py, test_mcp_spellcasting.py, test_mcp_campaign.py

**UI Tests (6 files → 2)**
- Consolidate: test-ui*.py, test-character-sheet*.py
- Result: test_character_sheet_ui.py, test_spellcasting_ui.py

**Estimated Reduction: 36 → 15 files (58% reduction)**

### 3.3 Unified Test Runner

**tests/test_runner.py:**
```python
#!/usr/bin/env python3
"""
Unified test runner with transaction isolation and proper cleanup
"""
import sys
import argparse
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.helpers.logging_utils import setup_logger

logger = setup_logger(__name__)

def run_tests(category: str = 'all', verbose: bool = False):
    """Run tests by category with proper isolation
    
    Args:
        category: 'unit', 'integration', 'mcp', 'api', 'e2e', or 'all'
        verbose: Enable verbose output
    """
    test_dir = Path(__file__).parent
    
    if category == 'all':
        pattern = 'test_*.py'
        start_dir = test_dir
    else:
        pattern = 'test_*.py'
        start_dir = test_dir / category
        if not start_dir.exists():
            logger.error(f"Test category '{category}' not found")
            return False
    
    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(start_dir),
        pattern=pattern,
        top_level_dir=str(test_dir)
    )
    
    # Run tests
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Report results
    logger.info(f"\n{'='*70}")
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info(f"Skipped: {len(result.skipped)}")
    logger.info(f"{'='*70}")
    
    return result.wasSuccessful()

def main():
    parser = argparse.ArgumentParser(description='Run Shadowrun GM tests')
    parser.add_argument(
        'category',
        nargs='?',
        default='all',
        choices=['all', 'unit', 'integration', 'mcp', 'api', 'e2e'],
        help='Test category to run'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    logger.info(f"Running {args.category} tests...")
    success = run_tests(args.category, args.verbose)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
```

**Usage:**
```bash
# Run all tests
python tests/test_runner.
