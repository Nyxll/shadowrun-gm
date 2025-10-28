# Schema Mismatches Found

## Critical Issues to Fix

### 1. character_skills
**CRUD uses:** `rating` (single field)
**Schema has:** `base_rating`, `current_rating` (two fields)
**Fix:** Update all skill operations to use both fields

### 2. character_spirits
**CRUD uses:** `created_by`, `modified_by`, `modified_at`, `deleted_at`, `deleted_by`
**Schema has:** Only `created_at` (no audit fields)
**Fix:** Remove audit operations or add audit columns

### 3. character_foci
**CRUD uses:** `created_by`, `modified_by`, `modified_at`, `deleted_at`, `deleted_by`
**Schema has:** Only `created_at` (no audit fields)
**Fix:** Remove audit operations or add audit columns

### 4. character_contacts
**CRUD uses:** `created_by`, `modified_by`, `modified_at`, `deleted_at`, `deleted_by`
**Schema has:** Only `created_at` (no audit fields)
**Fix:** Remove audit operations or add audit columns

### 5. character_vehicles
**Schema has:** `pilot` field
**CRUD uses:** `autopilot`, `sensor` fields (don't exist)
**Fix:** Use correct field names from schema

### 6. character_cyberdecks
**Schema has:** `memory`, `storage`, `response_increase`, `persona_programs`, `utilities`, `ai_companions`
**CRUD uses:** `active_memory`, `storage_memory`, `reaction_increase`, `programs`
**Fix:** Use correct field names from schema

### 7. character_edges_flaws
**CRUD uses:** `cost`, `created_by`, `modified_by`, etc.
**Schema has:** Only `id`, `character_id`, `name`, `type`, `description`, `created_at`
**Fix:** Remove non-existent fields

### 8. character_powers
**Schema has:** `id` as INTEGER, `character_id` as INTEGER
**CRUD uses:** UUID types
**Fix:** Use correct types (this table needs migration to UUID)

### 9. character_relationships
**Schema has:** `relationship_type`, `relationship_name`, `data` (JSONB)
**CRUD uses:** `entity_name`, `status`, `notes`
**Fix:** Use correct schema structure

### 10. character_active_effects
**Schema has:** `effect_type`, `effect_name`, `target_type`, `target_name`, `modifier_value`, `duration_type`, `expires_at`, `caster_id`, `force`, `drain_taken`
**CRUD uses:** `source`, `duration`, `modifiers`
**Fix:** Use correct schema structure

### 11. character_modifiers
**Schema has:** `source` (text), `is_permanent` (boolean), `source_type`, `source_id`
**CRUD uses:** `source_type`, `source_name`, `is_temporary`
**Fix:** Use correct field names and logic

## UUID Architecture

### Primary UUIDs in System:
1. **User/Player UUID** (`users.id`) - Identifies players/GMs
2. **Character UUID** (`characters.id`) - Identifies characters
3. **Campaign UUID** (`campaigns.id`) - Identifies campaigns
4. **Audit UUIDs** - `created_by`, `modified_by`, `deleted_by` reference `users.id`

### Mixed ID Types Found:
- **character_powers**: Uses INTEGER for both `id` and `character_id` (NEEDS MIGRATION)
- **character_cyberdecks**: Uses INTEGER for `id`, UUID for `character_id`
- **house_rules**: Uses INTEGER for `id`
- **character_campaign_links**: Uses INTEGER for `id` and `campaign_id`, UUID for `character_id`

### Audit Trail Pattern:
Tables with full audit support (created_by, modified_by, deleted_by as UUID):
- character_spells ✓
- character_gear ✓
- character_vehicles ✓
- character_modifiers ✓

Tables WITHOUT audit fields:
- character_spirits ✗
- character_foci ✗
- character_contacts ✗
- character_skills ✗
- character_edges_flaws ✗
- character_powers ✗
- character_relationships ✗
- character_active_effects ✗

## Summary
- **11 tables** have schema mismatches
- **character_skills** is the most critical (base_rating/current_rating)
- **character_powers** needs UUID migration (currently INTEGER)
- **character_cyberdecks** has mixed types (INTEGER id, UUID character_id)
- **4 tables** have audit fields, **8 tables** don't
- Field name mismatches in cyberdecks, vehicles, relationships, active_effects, modifiers
- **campaign_id** is INTEGER in some tables, UUID in campaigns table
