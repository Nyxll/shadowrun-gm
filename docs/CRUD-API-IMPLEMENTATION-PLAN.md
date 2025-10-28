# CRUD API Implementation Plan

## Current Status
- Created comprehensive CRUD API in `lib/comprehensive_crud.py`
- Added character lookup helpers (get_character_by_name, list_characters)
- Identified schema mismatches that need fixing

## Critical Issues Found

### 1. Schema Mismatches
The CRUD API was written based on assumed schema, but actual schema differs:

**character_skills:**
- ❌ CRUD uses: `rating`
- ✓ Actual schema: `base_rating`, `current_rating`
- Also has: `skill_type`, `conditional_bonuses`

**character_modifiers:**
- ❌ CRUD uses: `source_name`, `is_temporary`
- ✓ Actual schema: `source` (text), `is_permanent` (boolean)
- Also has: `source_type`, `source_id`, `parent_modifier_id`, audit fields

**character_active_effects:**
- ❌ CRUD uses: `source`, `duration`, `modifiers` (JSONB)
- ✓ Actual schema: `duration_type`, `expires_at`, individual fields for modifiers
- Also has: `caster_id`, `force`, `drain_taken`

### 2. Foreign Key Issues
- `created_by` references `users` table
- Need to ensure AI user exists in users table
- All audit fields (created_by, modified_by, deleted_by) must reference valid users

### 3. UUID Usage
- ✓ All character IDs are UUIDs
- ✓ Added lookup helpers to CRUD API
- ⚠️ Need to audit ALL code to ensure UUID usage, not names

## Implementation Plan

### Phase 1: Fix CRUD API Schema Mismatches
1. Update `character_skills` operations to use `base_rating`/`current_rating`
2. Update `character_modifiers` operations to use `source`/`is_permanent`
3. Update `character_active_effects` operations to match actual schema
4. Ensure all operations handle audit fields correctly

### Phase 2: Fix User/Audit System
1. Verify AI user exists in users table
2. Update `get_ai_user_id()` to create user if missing
3. Test all audit logging

### Phase 3: Update Tests
1. Fix test suite to match corrected CRUD API
2. Add tests for all 40+ operations
3. Test UUID lookup functionality
4. Test audit logging

### Phase 4: Code Audit for UUID Usage
Files to check:
- `game-server.py` - MCP tools
- `www/app.js` - Frontend character selection
- `www/character-sheet-renderer.js` - Character display
- All test files
- All tool scripts

### Phase 5: Update Documentation
1. Update `MCP-TOOLS-REFERENCE.md` with UUID requirements
2. Update `ORCHESTRATOR-REFERENCE.md` with CRUD API usage
3. Update `UI-REFERENCE.md` with character selection flow
4. Update `README.md` with architecture overview

### Phase 6: Update MCP Tools
1. Add character lookup tool (name -> UUID)
2. Update all character-specific tools to require UUID
3. Add validation for UUID format
4. Update tool descriptions

## Schema Reference

### character_skills (ACTUAL)
```sql
id                  uuid PRIMARY KEY
character_id        uuid REFERENCES characters(id)
skill_name          text
base_rating         integer  -- Base skill level
current_rating      integer  -- Current (with modifiers)
specialization      text
conditional_bonuses jsonb
skill_type          text
created_at          timestamp
```

### character_modifiers (ACTUAL)
```sql
id                  uuid PRIMARY KEY
character_id        uuid
modifier_type       text
target_name         text
modifier_value      integer
source              text     -- Source description
source_type         text     -- 'cyberware', 'spell', etc.
source_id           uuid     -- Reference to source
is_permanent        boolean  -- NOT is_temporary!
modifier_data       jsonb
parent_modifier_id  uuid     -- For nested modifiers
-- Audit fields
created_by          uuid REFERENCES users(id)
modified_by         uuid
modified_at         timestamp
deleted_at          timestamp
deleted_by          uuid
-- Other fields...
```

### character_active_effects (ACTUAL)
```sql
id              uuid PRIMARY KEY
character_id    uuid
effect_type     text
effect_name     text
target_type     text
target_name     text
modifier_value  integer
duration_type   text        -- 'sustained', 'instant', 'permanent'
expires_at      timestamp
is_active       boolean
caster_id       uuid        -- Who cast the spell
force           integer     -- Spell force
drain_taken     integer
notes           text
created_at      timestamp
```

## Next Steps

1. ✅ Document current state (this file)
2. ⏳ Fix CRUD API to match actual schema
3. ⏳ Fix tests
4. ⏳ Audit all code for UUID usage
5. ⏳ Update documentation
6. ⏳ Update MCP tools

## Notes

- **CRITICAL**: Always use UUIDs for character references
- **CRITICAL**: Use lookup helpers to convert names to UUIDs
- **CRITICAL**: Validate UUID format before database operations
- Schema is authoritative - code must match schema, not vice versa
- Audit logging requires valid user IDs in users table
