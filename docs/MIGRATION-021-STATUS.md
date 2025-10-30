# Migration 021 Status

## Issue
The migration script is hanging when trying to apply migration 021. This is likely due to:
1. Multiple Python processes accessing the database simultaneously
2. A database lock from an earlier command that didn't complete cleanly

## What Was Created

### Migration File
- **File**: `migrations/021_add_master_spells_table.sql`
- **Purpose**: Creates master_spells table for canonical spell definitions
- **Status**: Ready to apply, but hanging during execution

### Import Script
- **File**: `tools/import-master-spells.py`
- **Purpose**: Imports SPELLS.csv data into master_spells table
- **Status**: Ready to run after migration completes

### Helper Scripts
- **File**: `tools/apply-migration.py` - General migration helper
- **File**: `tools/test-migration-021.py` - Quick test for migration 021

## Manual Steps to Complete

### 1. Kill Hanging Processes
```powershell
# Find and kill hanging Python processes
tasklist | findstr python
# Kill specific PIDs if needed
taskkill /F /PID <pid>
```

### 2. Apply Migration Manually
Option A - Using psql:
```bash
psql -h <host> -U <user> -d <database> -f migrations/021_add_master_spells_table.sql
```

Option B - Using Python directly:
```python
python tools/test-migration-021.py
```

### 3. Import Spell Data
```bash
python tools/import-master-spells.py
```

### 4. Verify
```python
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM master_spells")
print(f"Spells in database: {cursor.fetchone()[0]}")
cursor.close()
conn.close()
```

## What's Next

After the migration and import complete:

1. **Add Custom Spells** (like Oak's Charge):
```sql
INSERT INTO master_spells (
    spell_name, spell_class, spell_type, duration,
    drain_formula, is_house_rule, description
) VALUES (
    'Charge', 'manipulation', 'mana', 'instant',
    '(F/2)L', TRUE, 'Recharges batteries and electronic devices'
);
```

2. **Implement cast_spell Operation**:
   - Add drain formula parser to lib/mcp_operations.py
   - Implement drain calculation based on force
   - Apply totem modifiers
   - Roll drain resistance
   - Track damage

3. **Test**:
   - Test with canonical spells
   - Test with house rule spells
   - Test totem modifiers
   - Test variable force casting

## Files Created

- `migrations/021_add_master_spells_table.sql`
- `tools/import-master-spells.py`
- `tools/apply-migration.py`
- `tools/test-migration-021.py`
- `docs/SPELLCASTING-SPEC.md`
- `docs/SPELLCASTING-IMPLEMENTATION.md`
- `docs/MIGRATION-021-STATUS.md` (this file)
