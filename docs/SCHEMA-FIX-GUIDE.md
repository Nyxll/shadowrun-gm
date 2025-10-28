# Schema Fix Guide

## Problem: Foreign Key Type Mismatch

### The Issue

The database had a schema mismatch where foreign key types didn't match the primary key they referenced:

- `characters.id` = **UUID** (primary key)
- `character_skills.character_id` = **INTEGER** (foreign key)
- `character_gear.character_id` = **INTEGER** (foreign key)

Additionally, the foreign key constraints were pointing to a non-existent table `sr_characters` instead of the actual `characters` table.

### Symptoms

- Character sheet endpoint returned HTTP 500 errors
- Error message: `operator does not exist: integer = uuid`
- Skills and gear data couldn't be loaded for characters
- Database joins failed due to type mismatch

## Solution: UUID Migration

### What Was Done

1. **Migrated Foreign Keys to UUID**
   - Changed `character_skills.character_id` from INTEGER to UUID
   - Changed `character_gear.character_id` from INTEGER to UUID
   - Cleared existing data (15 skill records, 0 gear records)

2. **Fixed Foreign Key Constraints**
   - Dropped incorrect constraints pointing to `sr_characters`
   - Created new constraints pointing to `characters` table
   - Added CASCADE delete behavior

3. **Removed Workaround Code**
   - Removed try/except blocks that were hiding the error
   - Restored clean database queries
   - Character sheets now load properly

4. **Archived Unused Schema**
   - Moved `schema/character_system.sql` to `docs/archive/`
   - This file contained the `sr_characters` table definition
   - Was a proposed schema that was never implemented

## Migration Script

### Location
`tools/migrate-foreign-keys-to-uuid.py`

### Features
- Checks current schema state
- Shows existing data counts
- Prompts for confirmation before changes
- Safely migrates column types
- Recreates foreign key constraints
- Verifies migration success
- Provides rollback information

### Usage

```bash
python tools/migrate-foreign-keys-to-uuid.py
```

The script will:
1. Display current schema state
2. Show data counts
3. Ask for confirmation
4. Migrate each table
5. Verify the changes

### Example Output

```
============================================================
CHARACTER FOREIGN KEY MIGRATION TO UUID
============================================================

=== CURRENT SCHEMA STATE ===

characters.id: uuid
character_skills.character_id: integer
character_gear.character_id: integer

=== DATA CHECK ===

Characters: 6 records
Character Skills: 15 records
Character Gear: 0 records

=== FOREIGN KEY CONSTRAINTS ===

character_skills.character_id -> sr_characters.id
  Constraint: character_skills_character_id_fkey

============================================================
READY TO MIGRATE
============================================================

Proceed with migration? (yes/no): yes

=== MIGRATING CHARACTER_SKILLS ===

1. Checking for foreign key constraints...
   Dropping constraint: character_skills_character_id_fkey
2. Converting character_id from INTEGER to UUID...
   Deleted 15 rows from character_skills
   ✓ Column type changed to UUID
3. Creating foreign key constraint...
   ✓ Foreign key constraint created

✓ character_skills migration complete!

=== VERIFICATION ===

characters.id: uuid
character_skills.character_id: uuid
character_gear.character_id: uuid

Foreign key constraints: 2
  character_skills: fk_character_skills_character
  character_gear: fk_character_gear_character

============================================================
✓ MIGRATION COMPLETE!
============================================================
```

## Verification

### Check Schema
```bash
python tools/check-schema.py
```

### Test Character Sheets
1. Start server: `python game-server.py`
2. Open http://localhost:8001
3. Click any character name
4. Character sheet should load without errors
5. Skills and gear sections should display (if data exists)

### Database Query
```sql
-- Check column types
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name IN ('characters', 'character_skills', 'character_gear')
    AND column_name IN ('id', 'character_id')
ORDER BY table_name, column_name;

-- Check foreign keys
SELECT
    tc.table_name,
    tc.constraint_name,
    ccu.table_name AS foreign_table_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name IN ('character_skills', 'character_gear');
```

## About sr_characters

### What It Was
The `schema/character_system.sql` file contained a comprehensive character system design with:
- `sr_characters` table (note the "sr_" prefix)
- Reference tables for metatypes, qualities, skills, powers, spells, totems
- JSONB-based flexible storage
- Helper functions and views

### Why It Wasn't Used
- The actual database uses a simpler `characters` table (no "sr_" prefix)
- The proposed schema was never implemented
- Foreign keys were incorrectly pointing to the non-existent `sr_characters` table

### What We Did
- Archived the file to `docs/archive/character_system.sql.unused`
- Kept it for reference in case useful features are needed later
- Fixed foreign keys to point to the actual `characters` table

### Useful Features from sr_characters Schema
If you want to implement these in the future:
- **Metatype system**: Structured race/variant data
- **Qualities system**: Edges and flaws with costs
- **Skills reference**: Linked attributes, specializations, defaulting
- **Powers/Spells**: Structured magical abilities
- **Audit trail**: Change history tracking
- **Helper functions**: Essence calculation, etc.

## Current Schema

### characters
- `id`: UUID (primary key)
- `name`: TEXT
- `street_name`: TEXT
- `character_type`: TEXT
- `archetype`: TEXT
- `attributes`: JSONB (contains body, quickness, strength, etc.)
- Other fields...

### character_skills
- `id`: INTEGER (auto-increment)
- `character_id`: UUID (foreign key → characters.id)
- `skill_name`: VARCHAR
- `rating`: INTEGER
- `specialization`: VARCHAR

### character_gear
- `id`: INTEGER (auto-increment)
- `character_id`: UUID (foreign key → characters.id)
- `gear_name`: VARCHAR
- `category`: VARCHAR
- `quantity`: INTEGER
- `cost`: INTEGER
- `notes`: TEXT

## Repopulating Data

Since the migration cleared the skills and gear tables, you'll need to repopulate them:

### Option 1: Manual Entry
Add skills/gear through the database or a data entry interface

### Option 2: Import from Source
If you have character data in another format, create an import script

### Option 3: Extract from Character Sheets
If character data is stored in the `characters.full_sheet` TEXT field, parse and extract

## Lessons Learned

1. **Always match foreign key types to primary keys**
   - UUID → UUID
   - INTEGER → INTEGER
   - Never mix types

2. **Verify foreign key constraints point to correct tables**
   - Check `information_schema.table_constraints`
   - Ensure referenced table actually exists

3. **Document schema decisions**
   - Why certain types were chosen
   - What tables reference what
   - Migration history

4. **Test after schema changes**
   - Run queries to verify joins work
   - Test application endpoints
   - Check for error logs

## Future Improvements

1. **Add schema validation tests**
   - Automated checks for type mismatches
   - Foreign key integrity tests
   - Constraint verification

2. **Migration tracking**
   - Version schema changes
   - Track applied migrations
   - Rollback capabilities

3. **Data preservation**
   - Backup before migrations
   - Map old IDs to new UUIDs
   - Preserve historical data

## Support

If you encounter issues:
1. Check server logs for errors
2. Run `tools/check-schema.py` to verify schema
3. Test with `curl http://localhost:8001/api/character/CharacterName`
4. Review this guide for troubleshooting steps
