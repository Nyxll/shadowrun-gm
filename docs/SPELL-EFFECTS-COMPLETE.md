# Spell Effects & Sustained Spells - COMPLETE

## Status: ✅ COMPLETE

Phase 11.1.3 of the spellcasting system is now complete with full sustained spell tracking using the existing `character_modifiers` table.

## What Was Implemented

### 1. Database Schema Enhancement (Migration 022)
Added helper columns to `character_modifiers` table:
- `spell_force` (INTEGER): Force at which spell was cast
- `is_sustained` (BOOLEAN): True if this is a sustained spell effect
- `sustained_by` (UUID): Character sustaining the spell (usually caster)
- Indexes for efficient querying of sustained spells

### 2. SpellcastingEngine Methods
Implemented three new methods in `lib/spellcasting.py`:

#### `get_sustained_spells(character_id)`
- Returns list of all spells being sustained by a character
- Each entry includes spell_name, force, and target_character_id
- Queries character_modifiers where is_sustained=true

#### `calculate_sustaining_penalty(character_id)`
- Calculates total dice pool penalty for sustained spells
- Returns -2 per sustained spell (SR2 rules)
- Example: 2 sustained spells = -4 dice penalty

#### `drop_sustained_spell(character_id, spell_name)`
- Ends a sustained spell by soft-deleting all related modifiers
- Sets deleted_at timestamp on all modifiers for that spell
- Returns True if spell was found and dropped

### 3. Integration with character_modifiers Table
Spell effects are stored as modifiers with:
- `source_type = 'spell'`
- `source = spell_name`
- `is_sustained = true` for sustained spells
- `sustained_by = caster_id`
- `spell_force = force` at which cast
- `modifier_data` JSONB for spell-specific info

## Example: Armor Spell

When Oak casts Armor at Force 6 on himself:

```sql
-- Impact armor modifier
INSERT INTO character_modifiers (
    character_id, modifier_type, target_name, modifier_value,
    source, source_type, is_permanent, is_sustained, sustained_by, spell_force
) VALUES (
    oak_id, 'armor', 'impact', 6,
    'Armor', 'spell', false, true, oak_id, 6
);

-- Ballistic armor modifier
INSERT INTO character_modifiers (
    character_id, modifier_type, target_name, modifier_value,
    source, source_type, is_permanent, is_sustained, sustained_by, spell_force
) VALUES (
    oak_id, 'armor', 'ballistic', 6,
    'Armor', 'spell', false, true, oak_id, 6
);
```

Result:
- Oak gains +6 Impact and +6 Ballistic armor
- Oak takes -2 dice pool penalty on all actions (sustaining 1 spell)
- When Oak drops the spell, both modifiers are soft-deleted

## Testing Results

All tests in `tests/test-sustained-spells.py` pass:

1. ✓ Initial state: No sustained spells, no penalty
2. ✓ Add Armor spell: 1 sustained spell, -2 penalty
3. ✓ Add Increase Strength: 2 sustained spells, -4 penalty
4. ✓ Drop Armor: 1 sustained spell remaining, -2 penalty
5. ✓ Drop Increase Strength: No sustained spells, no penalty

## Advantages of This Approach

1. **Unified System**: All modifiers (cyberware, bioware, spells, edges) in one table
2. **Existing Infrastructure**: Leverages existing modifier calculation code
3. **Soft Deletes**: Easy to end effects without losing history
4. **Flexible**: JSONB modifier_data for spell-specific information
5. **Queryable**: Simple queries to get all active effects
6. **Efficient**: Indexed for fast lookups

## Sustaining Penalty Rules

Per Shadowrun 2nd Edition rules:
- Each sustained spell: -2 dice from all dice pools
- Applies to ALL actions while sustaining
- Cumulative: 3 sustained spells = -6 dice
- Dropping a spell immediately removes its penalty

## Files Created/Modified

- `migrations/022_add_spell_effect_columns.sql` - Applied ✓
- `lib/spellcasting.py` - Added 3 new methods ✓
- `tests/test-sustained-spells.py` - Comprehensive test suite ✓
- `docs/SPELL-EFFECTS-DESIGN-V2.md` - Design documentation ✓

## Next Steps

Phase 11.2: UI Integration
- Add spellcasting interface to character sheet
- Display spell list with learned forces
- Add "Cast Spell" button/modal
- Show sustained spells and penalties
- Add "Drop Spell" functionality
- Display drain results

## Notes

- Spell effects use the same modifier system as cyberware/bioware
- This ensures consistent application across all game mechanics
- Future spell effects (Invisibility, Increase Attribute, etc.) follow the same pattern
- The system is ready for more complex spell effects as needed
