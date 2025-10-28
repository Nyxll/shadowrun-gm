# Schema Fix Plan - Systematic Approach

## Problem Statement
The CRUD API has mismatches with the actual database schema. We need to fix these WITHOUT removing functionality, only matching field names to what actually exists.

## Key Principle
**Keep all CRUD operations, just fix the SQL to match actual schema columns**

## Tables Requiring Fixes

### 1. character_skills ✓ FIXED
- **Issue**: Used `rating` field
- **Schema has**: `base_rating`, `current_rating`
- **Fix**: Update INSERT/UPDATE to use both fields
- **Status**: COMPLETED

### 2. character_spirits
- **Issue**: References `deleted_at`, `deleted_by`, `created_by`, `modified_by`, `modified_at`
- **Schema has**: Only `id`, `character_id`, `spirit_name`, `spirit_type`, `force`, `services`, `special_abilities`, `notes`, `created_at`
- **Fix**: Remove references to non-existent audit columns in SQL
- **Keep**: The reason parameter and _audit() call (for future compatibility)
- **Action**: Just remove the non-existent columns from SQL statements

### 3. character_foci
- **Issue**: Same as spirits - references audit fields that don't exist
- **Schema has**: Only basic fields + `created_at`
- **Fix**: Remove audit column references from SQL
- **Keep**: API structure intact

### 4. character_contacts
- **Issue**: Same as above
- **Fix**: Remove audit column references from SQL

### 5. character_vehicles
- **Issue**: Uses `autopilot`, `sensor` fields
- **Schema has**: `pilot` field (not autopilot), no sensor field
- **Fix**: Change `autopilot` to `pilot`, remove `sensor`

### 6. character_cyberdecks
- **Issue**: Uses `active_memory`, `storage_memory`, `reaction_increase`, `programs`
- **Schema has**: `memory`, `storage`, `response_increase`, `persona_programs`, `utilities`, `ai_companions`
- **Fix**: Map to correct field names

### 7. character_edges_flaws
- **Issue**: Uses `cost` field
- **Schema has**: Only `id`, `character_id`, `name`, `type`, `description`, `created_at`
- **Fix**: Remove `cost` from INSERT

### 8. character_powers
- **Issue**: Uses UUID types, but schema has INTEGER
- **Schema has**: `id` INTEGER, `character_id` INTEGER
- **Fix**: Cast appropriately or note this needs migration

### 9. character_relationships
- **Issue**: Uses `entity_name`, `status`, `notes`
- **Schema has**: `relationship_type`, `relationship_name`, `data` (JSONB)
- **Fix**: Restructure to use correct fields

### 10. character_active_effects
- **Issue**: Uses `source`, `duration`, `modifiers`
- **Schema has**: `effect_type`, `effect_name`, `target_type`, `target_name`, `modifier_value`, `duration_type`, `expires_at`, `caster_id`, `force`, `drain_taken`
- **Fix**: Restructure to match actual schema

### 11. character_modifiers
- **Issue**: Uses `source_name`, `is_temporary`
- **Schema has**: `source` (text), `is_permanent` (boolean), `source_type`, `source_id`
- **Fix**: Use `source` instead of `source_name`, use `is_permanent` (NOT is_temporary)

## Implementation Strategy

1. **One table at a time** - Fix each completely before moving to next
2. **Test after each fix** - Verify the SQL works
3. **Keep all operations** - Don't remove functionality
4. **Only change SQL** - Match column names to schema
5. **Document changes** - Note what was changed and why

## Next Steps
1. Re-read comprehensive_crud.py to see current state
2. Fix character_spirits SQL (keep operations, fix columns)
3. Fix character_foci SQL
4. Fix character_contacts SQL
5. Continue through remaining tables
6. Test each fix
7. Update MCP operations
8. Update orchestrator
9. Update UI
10. Update documentation
