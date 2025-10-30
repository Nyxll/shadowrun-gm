# Cleanup Implementation Plan - Step-by-Step Execution

## Overview
This document provides the detailed execution plan for cleaning up 268 tools and 36 tests down to a maintainable codebase with helper libraries and proper test isolation.

---

## Phase 1: Create Helper Library (Day 1)

### Step 1.1: Create Directory Structure
```bash
mkdir -p lib/helpers
touch lib/helpers/__init__.py
```

### Step 1.2: Create Helper Modules

Create these files in order:

1. **lib/helpers/db_utils.py** - Database utilities (see CLEANUP-MASTER-PLAN.md)
2. **lib/helpers/test_utils.py** - Test isolation utilities
3. **lib/helpers/logging_utils.py** - Logging utilities
4. **lib/helpers/validation_utils.py** - Validation utilities

### Step 1.3: Update .clinerules

Add helper library documentation to `.clinerules`:

```markdown
## Helper Library Usage (lib/helpers/)

### Database Connections
**ALWAYS use lib/helpers/db_utils.py for database operations**

```python
from lib.helpers.db_utils import get_db_connection, execute_query, get_character_id

# Context manager pattern (preferred)
with get_db_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM characters")
    results = cur.fetchall()

# Quick query pattern
results = execute_query("SELECT * FROM characters WHERE id = %s", (char_id,))

# Get character ID by name
char_id = get_character_id("Platinum")
```

### Test Isolation
**ALWAYS use lib/helpers/test_utils.py for tests**

```python
from lib.helpers.test_utils import isolated_test_db, create_test_character

def test_something():
    with isolated_test_db() as conn:
        # Create test data
        char_id = create_test_character(conn, "Test Char")
        
        # Run test
        cur = conn.cursor()
        cur.execute("SELECT * FROM characters WHERE id = %s", (char_id,))
        
        # Assert results
        assert cur.fetchone() is not None
        
    # Automatic rollback - no cleanup needed!
```

### Logging
**ALWAYS use lib/helpers/logging_utils.py for consistent logging**

```python
from lib.helpers.logging_utils import setup_logger, log_operation

logger = setup_logger(__name__)

logger.info("Starting operation")
log_operation(logger, "IMPORT", "Importing characters from file")
logger.error("Operation failed")
```

### Validation
**ALWAYS use lib/helpers/validation_utils.py for data validation**

```python
from lib.helpers.validation_utils import (
    validate_character_name,
    validate_attribute_value,
    check_required_fields
)

if not validate_character_name(name):
    raise ValueError(f"Invalid character name: {name}")

missing = check_required_fields(data, ['name', 'metatype', 'body'])
if missing:
    raise ValueError(f"Missing required fields: {missing}")
```
```

### Step 1.4: Test Helper Library

Create `tests/test_helpers.py`:
```python
#!/usr/bin/env python3
"""Test helper library functions"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.helpers.db_utils import get_db_connection, get_character_id
from lib.helpers.test_utils import isolated_test_db, create_test_character
from lib.helpers.validation_utils import validate_character_name

def test_db_connection():
    """Test database connection helper"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        assert cur.fetchone()[0] == 1
    print("✓ Database connection works")

def test_isolated_db():
    """Test transaction isolation"""
    with isolated_test_db() as conn:
        char_id = create_test_character(conn, "Isolation Test")
        assert char_id is not None
        
        # Verify character exists in transaction
        cur = conn.cursor()
        cur.execute("SELECT name FROM characters WHERE id = %s", (char_id,))
        assert cur.fetchone()[0] == "Isolation Test"
    
    # Verify character was rolled back
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM characters WHERE name = 'Isolation Test'")
        assert cur.fetchone()[0] == 0
    
    print("✓ Transaction isolation works")

def test_validation():
    """Test validation utilities"""
    assert validate_character_name("Platinum") == True
    assert validate_character_name("A") == False
    assert validate_character_name("") == False
    print("✓ Validation works")

if __name__ == '__main__':
    test_db_connection()
    test_isolated_db()
    test_validation()
    print("\n✅ All helper tests passed!")
```

Run: `python tests/test_helpers.py`

---

## Phase 2: Tool Audit & Categorization (Day 2)

### Step 2.1: Create Tool Inventory

Run this script to categorize all tools:

```python
#!/usr/bin/env python3
"""Audit and categorize all tools"""
import os
from pathlib import Path
from collections import defaultdict

tools_dir = Path('tools')
categories = defaultdict(list)

# Categorization patterns
patterns = {
    'import': ['import-', 'load-', 'insert-'],
    'check': ['check-', 'verify-', 'inspect-', 'list-'],
    'fix': ['fix-', 'apply-', 'migrate-', 'update-', 'clean-'],
    'test': ['test-', 'debug-', 'diagnose-'],
    'generate': ['generate-', 'create-', 'export-'],
    'compare': ['compare-', 'show-', 'find-'],
    'obsolete': ['-v6.py', '-v7.py', '-v8.py', '-v9.py', '-v10.py']
}

for file in sorted(tools_dir.glob('*.py')):
    name = file.name
    categorized = False
    
    for category, pattern_list in patterns.items():
        if any(p in name for p in pattern_list):
            categories[category].append(name)
            categorized = True
            break
    
    if not categorized:
        categories['uncategorized'].append(name)

# Print report
print("=" * 70)
print("TOOL AUDIT REPORT")
print("=" * 70)

for category in sorted(categories.keys()):
    files = categories[category]
    print(f"\n{category.upper()} ({len(files)} files):")
    for f in sorted(files)[:10]:  # Show first 10
        print(f"  - {f}")
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more")

print(f"\n{'=' * 70}")
print(f"TOTAL: {sum(len(v) for v in categories.values())} files")
print(f"{'=' * 70}")

# Save to file
with open('docs/TOOL-AUDIT.md', 'w') as f:
    f.write("# Tool Audit Report\n\n")
    for category in sorted(categories.keys()):
        f.write(f"## {category.upper()} ({len(categories[category])} files)\n\n")
        for file in sorted(categories[category]):
            f.write(f"- {file}\n")
        f.write("\n")

print("\n✅ Audit saved to docs/TOOL-AUDIT.md")
```

Save as `tools/audit_tools.py` and run: `python tools/audit_tools.py`

### Step 2.2: Create Archive Directory

```bash
mkdir -p tools/archive
```

### Step 2.3: Identify Keepers

Create `docs/TOOLS-TO-KEEP.md`:

```markdown
# Tools to Keep (30 files)

## Import Tools (3)
- import-characters-v11.py → tools/import/import_characters.py
- import-master-spells.py → tools/import/import_spells.py
- load_dat_files.py → tools/import/import_gear.py

## Check Tools (10)
- check-character-tables.py → tools/check/check_schema.py
- check-all-uuids.py → tools/check/check_data_integrity.py
- check-modifiers-table.py → tools/check/check_modifiers.py
- check-cyberware-structure.py → tools/check/check_cyberware.py
- check-totem-columns.py → tools/check/check_magic.py
- verify-tables-ready.py → tools/check/verify_schema.py
- audit-schema-compliance.py → tools/check/audit_schema.py
- audit-all-operations.py → tools/check/audit_operations.py
- check-edges-flaws.py → tools/check/check_edges_flaws.py
- check-system-status.py → tools/check/system_status.py

## Fix Tools (5)
- apply-migration.py → tools/fix/apply_migration.py
- fix-all-schema-mismatches.py → tools/fix/fix_schema.py
- safe-cleanup-test-data.py → tools/fix/cleanup_test_data.py
- ensure-system-user.py → tools/fix/ensure_system_user.py
- create-user-functions.py → tools/fix/create_user_functions.py

## Generate Tools (3)
- generate-remaining-tool-defs.py → tools/generate/generate_tool_defs.py
- export-character-sheets.py → tools/generate/export_characters.py
- training-processor.py → tools/generate/process_training_data.py

## Utility Tools (9)
- link-oak-spells.py → tools/utils/link_character_spells.py
- add-comprehensive-logging.py → tools/utils/add_logging.py
- expand-mcp-operations.py → tools/utils/expand_operations.py
- add-all-phases-to-gameserver.py → tools/utils/update_gameserver.py
- roll-platinum-attack.py → tools/utils/test_combat.py
- test-spellcasting.py → tools/utils/test_spellcasting.py
- quick-crud-test.py → tools/utils/test_crud.py
- test-ui-debug.py → tools/utils/test_ui.py
- test-character-sheet-display.py → tools/utils/test_character_display.py
```

---

## Phase 3: Tool Consolidation (Days 3-4)

### Step 3.1: Create New Directory Structure

```bash
mkdir -p tools/import
mkdir -p tools/check
mkdir -p tools/fix
mkdir -p tools/generate
mkdir -p tools/utils
```

### Step 3.2: Consolidate Import Tools

**tools/import/import_characters.py** (consolidate v6-v11):
```python
#!/usr/bin/env python3
"""
Consolidated character import tool
Imports characters from NSRCG JSON format
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.helpers.db_utils import get_db_connection
from lib.helpers.logging_utils import setup_logger
from lib.helpers.validation_utils import validate_character_name

logger = setup_logger(__name__)

def import_character(file_path: str):
    """Import a single character from JSON file"""
    # Implementation from import-characters-v11.py
    pass

def import_all_characters(directory: str):
    """Import all characters from directory"""
    # Implementation
    pass

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Import characters')
    parser.add_argument('path', help='File or directory to import')
    args = parser.parse_args()
    
    if Path(args.path).is_file():
        import_character(args.path)
    else:
        import_all_characters(args.path)
```

### Step 3.3: Consolidate Check Tools

**tools/check/check_schema.py** (consolidate 20+ check-*-schema files):
```python
#!/usr/bin/env python3
"""
Consolidated schema validation tool
Checks database schema integrity
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.helpers.db_utils import get_db_connection
from lib.helpers.logging_utils import setup_logger

logger = setup_logger(__name__)

def check_table_exists(conn, table_name: str) -> bool:
    """Check if table exists"""
    cur = conn.cursor()
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        )
    """, (table_name,))
    return cur.fetchone()[0]

def check_all_tables(conn):
    """Check all required tables exist"""
    required_tables = [
        'characters', 'character_skills', 'character_modifiers',
        'character_gear', 'character_spells', 'master_spells',
        'campaigns', 'campaign_npcs'
    ]
    
    for table in required_tables:
        exists = check_table_exists(conn, table)
        status = "✓" if exists else "✗"
        logger.info(f"{status} {table}")

if __name__ == '__main__':
    with get_db_connection() as conn:
        check_all_tables(conn)
```

### Step 3.4: Move Obsolete Tools to Archive

```bash
# Move all versioned files
mv tools/*-v[0-9].py tools/archive/
mv tools/*-v[0-9][0-9].py tools/archive/

# Move debug/test files
mv tools/debug-*.py tools/archive/
mv tools/test-*.py tools/archive/  # Will move to tests/ later

# Move one-off comparison files
mv tools/compare-*.py tools/archive/
mv tools/show-*.py tools/archive/
mv tools/find-*.py tools/archive/
```

---

## Phase 4: Test Consolidation (Days 5-6)

### Step 4.1: Create Test Directory Structure

```bash
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/mcp
mkdir -p tests/api
mkdir -p tests/e2e
```

### Step 4.2: Create conftest.py (Pytest Fixtures)

**tests/conftest.py:**
```python
"""Pytest configuration and fixtures"""
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.helpers.test_utils import isolated_test_db, create_test_character

@pytest.fixture
def db_conn():
    """Provide isolated database connection"""
    with isolated_test_db() as conn:
        yield conn

@pytest.fixture
def test_character(db_conn):
    """Create a test character"""
    char_id = create_test_character(db_conn, "Test Character")
    yield char_id
    # Automatic cleanup via transaction rollback

@pytest.fixture
def test_mage(db_conn):
    """Create a test mage character"""
    cur = db_conn.cursor()
    cur.execute("""
        INSERT INTO characters (name, street_name, metatype, body, quickness, 
                               strength, charisma, intelligence, willpower, 
                               essence, magic, reaction)
        VALUES ('Test Mage', 'Test Mage', 'Human', 3, 3, 3, 3, 5, 6, 6.0, 6, 3)
        RETURNING
