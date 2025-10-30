# Spell Effects & Sustained Spells - Design Document V2

## Revised Approach: Use Existing character_modifiers Table

After reviewing the schema, we'll use the existing `character_modifiers` table instead of creating a new table. This provides better integration with the existing modifier system.

## character_modifiers Table Structure

```
- id: UUID
- character_id: UUID
- modifier_type: TEXT (e.g., 'attribute', 'armor', 'dice_pool', 'sustained_spell')
- target_name: TEXT (e.g., 'strength', 'armor', 'all_actions')
- modifier_value: INTEGER
- source: TEXT (spell name)
- source_type: TEXT ('spell')
- is_permanent: BOOLEAN
- condition: TEXT (for conditional modifiers)
- modifier_data: JSONB (flexible storage)
- deleted_at: TIMESTAMP (NULL = active)
```

## Spell Effect Examples Using character_modifiers

### 1. Armor Spell (Sustained)
```sql
INSERT INTO character_modifiers (
    character_id, modifier_type, target_name, modifier_value,
    source, source_type, is_permanent, modifier_data
) VALUES (
    'char_id', 'armor', 'impact', 6,
    'Armor', 'spell', false,
    '{"spell_force": 6, "is_sustained": true, "sustained_by": "caster_id", "spell_class": "manipulation"}'
);

-- Second entry for ballistic armor
INSERT INTO character_modifiers (
    character_id, modifier_type, target_name, modifier_value,
    source, source_type, is_permanent, modifier_data
) VALUES (
    'char_id', 'armor', 'ballistic', 6,
    'Armor', 'spell', false,
    '{"spell_force": 6, "is_sustained": true, "sustained_by": "caster_id", "spell_class": "manipulation"}'
);
```

### 2. Increase Strength (Sustained)
```sql
INSERT INTO character_modifiers (
    character_id, modifier_type, target_name, modifier_value,
    source, source_type, is_permanent, modifier_data
) VALUES (
    'char_id', 'attribute', 'strength', 2,
    'Increase Strength', 'spell', false,
    '{"spell_force": 4, "is_sustained": true, "sustained_by": "caster_id", "successes": 2}'
);
```

### 3. Invisibility (Sustained)
```sql
INSERT INTO character_modifiers (
    character_id, modifier_type, target_name, modifier_value,
    source, source_type, is_permanent, condition, modifier_data
) VALUES (
    'char_id', 'target_number', 'perception', 5,
    'Invisibility', 'spell', false, 'others_perceiving_character',
    '{"spell_force": 5, "is_sustained": true, "sustained_by": "caster_id"}'
);
```

### 4. Sustaining Penalty Tracker
```sql
-- Track that character is sustaining a spell (causes -2 dice pool penalty)
INSERT INTO character_modifiers (
    character_id, modifier_type, target_name, modifier_value,
    source, source_type, is_permanent, modifier_data
) VALUES (
    'caster_id', 'dice_pool', 'all_actions', -2,
    'Sustaining: Armor', 'spell', false,
    '{"is_sustaining_penalty": true, "spell_name": "Armor", "target_character_id": "char_id"}'
);
```

## Implementation Plan

### Step 1: Add Helper Columns (Optional Migration)
We may want to add a few helper columns to make spell tracking easier:

```sql
ALTER TABLE character_modifiers 
ADD COLUMN IF NOT EXISTS spell_force INTEGER,
ADD COLUMN IF NOT EXISTS is_sustained BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS sustained_by UUID REFERENCES characters(id);

CREATE INDEX IF NOT EXISTS idx_modifiers_sustained 
    ON character_modifiers(sustained_by) 
    WHERE is_sustained = true AND deleted_at IS NULL;
```

### Step 2: Extend SpellcastingEngine
Add methods to manage spell effects:

```python
def apply_spell_effect(character_id, caster_id, spell_name, effect_config):
    """Create modifier entries for spell effect"""
    
def get_sustained_spells(character_id):
    """Get all spells being sustained by character"""
    
def drop_sustained_spell(character_id, spell_name):
    """End a sustained spell (soft delete modifiers)"""
    
def calculate_sustaining_penalty(character_id):
    """Calculate total -2 per sustained spell penalty"""
```

### Step 3: Spell Effect Configurations
Define how each spell type creates modifiers:

```python
SPELL_EFFECTS = {
    'Armor': {
        'modifiers': [
            {'type': 'armor', 'target': 'impact', 'value': 'force'},
            {'type': 'armor', 'target': 'ballistic', 'value': 'force'}
        ],
        'is_sustained': True
    },
    'Increase Strength': {
        'modifiers': [
            {'type': 'attribute', 'target': 'strength', 'value': 'successes'}
        ],
        'is_sustained': True
    },
    'Heal': {
        'modifiers': [],  # Instant effect, no modifiers
        'is_sustained': False
    }
}
```

## Advantages of Using character_modifiers

1. **Unified System**: All modifiers (cyberware, spells, edges) in one place
2. **Existing Infrastructure**: Leverage existing modifier calculation code
3. **Soft Deletes**: Use deleted_at for ending effects
4. **Flexible**: JSONB modifier_data for spell-specific info
5. **Queryable**: Easy to get all active effects on a character

## Sustaining Penalties

When a character sustains spells:
1. Create modifier with `modifier_type='dice_pool'`, `target_name='all_actions'`, `modifier_value=-2`
2. Store `is_sustaining_penalty=true` in modifier_data
3. Link to the spell being sustained
4. When spell is dropped, soft delete both the effect AND the penalty

## Next Steps

1. Create optional migration to add helper columns
2. Implement SpellcastingEngine methods
3. Define spell effect configurations
4. Test with Armor and Increase Attribute spells
5. Document usage patterns
