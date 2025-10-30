# Spell Effects & Sustained Spells - Design Document

## Phase 11.1.3 Overview

This phase implements tracking and management of active spell effects, particularly sustained spells that remain active and require ongoing concentration.

## Requirements

### 1. Active Effects Tracking
- Track spells currently affecting a character
- Store effect type, magnitude, duration
- Link to source spell and caster
- Support multiple simultaneous effects

### 2. Sustained Spells
- Track which character is sustaining the spell
- Apply -2 dice pool penalty per sustained spell
- Allow dropping sustained spells
- Track sustained spell Force

### 3. Spell Effect Types

#### Instant Spells
- Take effect immediately
- No ongoing tracking needed
- Examples: Heal, Manabolt, Powerball

#### Sustained Spells
- Remain active while sustained
- Caster takes -2 dice pool penalty per spell
- Examples: Armor, Invisibility, Increase Attribute

#### Permanent Spells
- Effect is permanent once cast
- No sustaining required
- Examples: Increase Attribute (permanent version)

## Database Schema

### active_spell_effects Table
```sql
CREATE TABLE active_spell_effects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID NOT NULL REFERENCES characters(id),
    caster_id UUID REFERENCES characters(id),  -- Who cast it (may be self)
    spell_name VARCHAR(100) NOT NULL,
    spell_class VARCHAR(50),
    effect_type VARCHAR(50) NOT NULL,  -- 'sustained', 'permanent', 'temporary'
    force INTEGER NOT NULL,
    magnitude INTEGER,  -- Effect strength (e.g., +2 to attribute)
    target_attribute VARCHAR(50),  -- For attribute modifiers
    effect_data JSONB,  -- Flexible storage for spell-specific data
    is_sustained BOOLEAN DEFAULT false,
    sustained_by UUID REFERENCES characters(id),  -- Who is sustaining it
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,  -- For temporary effects
    ended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_active_effects_character ON active_spell_effects(character_id) 
    WHERE ended_at IS NULL;
CREATE INDEX idx_active_effects_sustained ON active_spell_effects(sustained_by) 
    WHERE is_sustained = true AND ended_at IS NULL;
```

## Spell Effect Examples

### 1. Armor (Sustained)
```json
{
    "spell_name": "Armor",
    "effect_type": "sustained",
    "force": 6,
    "magnitude": 6,  // +6 Impact and Ballistic armor
    "is_sustained": true,
    "sustained_by": "caster_id",
    "effect_data": {
        "armor_type": "both",
        "impact_bonus": 6,
        "ballistic_bonus": 6
    }
}
```

### 2. Increase Attribute (Sustained)
```json
{
    "spell_name": "Increase Strength",
    "effect_type": "sustained",
    "force": 4,
    "magnitude": 2,  // +2 to Strength (successes)
    "target_attribute": "strength",
    "is_sustained": true,
    "sustained_by": "caster_id"
}
```

### 3. Invisibility (Sustained)
```json
{
    "spell_name": "Invisibility",
    "effect_type": "sustained",
    "force": 5,
    "is_sustained": true,
    "sustained_by": "caster_id",
    "effect_data": {
        "target_number_modifier": 5  // +5 TN to see target
    }
}
```

## Implementation Plan

### Step 1: Create Migration
- Create migration 022 for active_spell_effects table
- Add indexes for performance
- Add triggers for updated_at

### Step 2: Extend SpellcastingEngine
- Add methods:
  - `apply_spell_effect()` - Create active effect
  - `get_active_effects()` - Get character's active effects
  - `get_sustained_spells()` - Get spells being sustained
  - `drop_sustained_spell()` - End a sustained spell
  - `calculate_sustaining_penalty()` - Get dice pool penalty

### Step 3: Effect Calculations
- Implement effect application logic
- Calculate attribute modifiers
- Calculate armor bonuses
- Handle target number modifiers

### Step 4: Integration
- Update cast_spell() to create effects
- Add sustaining penalty to dice pools
- Implement effect expiration

## Dice Pool Penalties

Characters sustaining spells take penalties:
- 1 sustained spell: -2 dice
- 2 sustained spells: -4 dice
- 3 sustained spells: -6 dice
- etc.

This penalty applies to ALL actions while sustaining.

## Effect Duration Types

1. **Instant**: No tracking needed
2. **Sustained**: Active while sustained, ends when dropped
3. **Permanent**: Never expires (rare)
4. **Temporary**: Expires after duration (e.g., 1 combat turn, 1 hour)

## Next Steps

1. Create migration 022
2. Implement SpellcastingEngine methods
3. Add effect calculation logic
4. Create comprehensive tests
5. Document usage examples
