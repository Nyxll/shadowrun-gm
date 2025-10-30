# Spellcasting Implementation Plan

## Overview
Implementation of the cast_spell MCP operation with proper drain calculation, totem modifiers, and spell data management.

## Architecture

### Data Flow
```
SPELLS.csv (canonical spell data)
    ↓
master_spells table (spell definitions with drain formulas)
    ↓
character_spells table (spells learned by character with force)
    ↓
cast_spell operation (calculates drain, applies modifiers, rolls resistance)
```

### Database Schema

#### master_spells Table
- **Purpose**: Canonical spell definitions from rulebooks and house rules
- **Key Fields**:
  - `spell_name` - Unique spell name
  - `spell_class` - combat, detection, health, illusion, manipulation
  - `spell_type` - mana or physical
  - `duration` - instant, sustained, permanent
  - `drain_formula` - Formula string (e.g., "(F/2)S", "[(F/2)+1]D")
  - `is_house_rule` - TRUE for custom/homebrew spells
  - `house_rule_id` - Links to house_rules table

#### character_spells Table (Enhanced)
- **Purpose**: Spells known by each character
- **Key Fields**:
  - `character_id` - Character who knows the spell
  - `spell_name` - Name of the spell
  - `force` - Force at which spell was learned (NULL for variable force)
  - `master_spell_id` - Reference to master_spells (NULL for fully custom)
  - `drain_code` - Cached drain code for quick reference
  - `totem_modifier` - Totem bonus/penalty for this spell

### Drain Formula Parsing

Drain formulas from SPELLS.csv follow these patterns:
- `(F/2)S` = Force/2, Stun damage
- `[(F/2)+1]D` = (Force/2)+1, Deadly damage
- `[(F/2)-1]M` = (Force/2)-1, Moderate damage
- `[(F/2)+2]L` = (Force/2)+2, Light damage

The cast_spell operation will:
1. Look up spell in master_spells
2. Parse drain formula
3. Calculate drain based on force used
4. Apply totem modifiers
5. Roll drain resistance

### House Rule Support

Custom spells (like Oak's "Charge" spell) are handled via:
1. Insert into master_spells with `is_house_rule=TRUE`
2. Link to house_rules table via `house_rule_id`
3. Provide custom drain_formula
4. Character learns spell normally via character_spells

Example for Oak's Charge spell:
```sql
INSERT INTO master_spells (
    spell_name, spell_class, spell_type, duration,
    drain_formula, is_house_rule, description
) VALUES (
    'Charge', 'manipulation', 'mana', 'instant',
    '(F/2)L', TRUE, 'Recharges batteries and electronic devices'
);
```

## Implementation Status

### Completed
- [x] Created SPELLCASTING-SPEC.md with mechanics
- [x] Designed master_spells table schema
- [x] Created migration 021 for master_spells
- [x] Created import script for SPELLS.csv
- [x] Fixed house_rules foreign key type mismatch

### In Progress
- [ ] Apply migration 021
- [ ] Import spell data from SPELLS.csv
- [ ] Build cast_spell operation in lib/mcp_operations.py
- [ ] Add drain formula parser
- [ ] Test with real spell data

### Next Steps
1. Complete migration and data import
2. Implement drain formula parser
3. Build cast_spell operation with:
   - Spell lookup from master_spells
   - Drain calculation
   - Totem modifier application
   - Drain resistance roll
   - Damage tracking
4. Add to game-server.py tool definitions
5. Test with various spells and scenarios

## Files Created/Modified

### New Files
- `migrations/021_add_master_spells_table.sql` - Master spells table
- `tools/import-master-spells.py` - Import SPELLS.csv data
- `tools/apply-migration.py` - Helper for applying migrations
- `docs/SPELLCASTING-SPEC.md` - Detailed mechanics specification
- `docs/SPELLCASTING-IMPLEMENTATION.md` - This file

### Modified Files
- `ROADMAP.md` - Added spellcasting tasks

## Testing Plan

1. **Unit Tests**:
   - Drain formula parsing
   - Drain calculation for various forces
   - Totem modifier application

2. **Integration Tests**:
   - Cast spell with learned force
   - Cast spell at variable force
   - Custom house rule spells
   - Totem favored/opposed spells

3. **End-to-End Tests**:
   - Full spellcasting sequence
   - Drain resistance and damage
   - Multiple sustained spells
   - Spell failure scenarios
