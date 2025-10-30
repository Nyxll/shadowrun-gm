# SHADOWRUN 2E SPELLCASTING SYSTEM SPECIFICATION

**Version:** 1.0  
**Last Updated:** 2025-10-28  
**Status:** Draft for Implementation

---

## TABLE OF CONTENTS

1. [Overview](#overview)
2. [Core Mechanics](#core-mechanics)
3. [Spell Success Test](#spell-success-test)
4. [Drain Resistance Test](#drain-resistance-test)
5. [Spell Effects](#spell-effects)
6. [Advanced Features](#advanced-features)
7. [Database Schema](#database-schema)
8. [Implementation Phases](#implementation-phases)

---

## OVERVIEW

The spellcasting system in Shadowrun 2nd Edition is a complex mechanic involving:
- Force selection and validation
- Dice pool calculation with multiple modifiers
- Target number calculation with situational modifiers
- Spell success resolution
- Drain calculation and resistance
- Effect application and tracking

This specification documents the complete system for implementation in the MCP `cast_spell` operation.

---

## CORE MECHANICS

### Force Selection

**Rules:**
- Minimum Force: 1
- Maximum Force: `learned_force` (from `character_spells.learned_force`)
- Magician can cast at **any force up to learned_force**
- Casting at lower force is a tactical choice to reduce drain
- To cast at higher force, must re-learn the spell

**Validation:**
```python
if force < 1:
    raise ValueError("Force must be at least 1")
if force > learned_force:
    raise ValueError(f"Cannot cast at Force {force} (learned at {learned_force})")
```

### Physical vs Stun Drain

**Critical Rule:**
- If `Force > Magic Rating`: Drain is **PHYSICAL**
- If `Force ≤ Magic Rating`: Drain is **STUN**

This is independent of the spell's base drain code.

---

## SPELL SUCCESS TEST

### Step 1: Calculate Dice Pool

**Base Dice:** Force of the spell

**Additional Dice Sources:**

1. **Magic Pool** (user must specify allocation)
   - Maximum dice that can be added: `Magic Rating`
   - User specifies split between Success Test and Drain Resistance
   - Example: Magic 6, can add up to 6 dice to success test
   
2. **Totem Modifiers** (from `totems` table or `character_relationships`)
   - **Favored categories:** +2 dice
   - **Opposed categories:** -2 dice
   - Examples:
     - Bear: Favors Health (+2), Opposes Combat (-2)
     - Leviathan: Favors Combat (+2), Opposes Illusion (-2)
     - Owl: Time/place based (night/outdoors)
   
3. **Power Foci** (from `character_gear` where `gear_type='focus'`)
   - Adds focus rating to Magic Pool
   - Only applies if focus matches spell category
   - Types: Specific Spell, Spell Category, Power Focus
   
4. **Fetish Dice** (if spell requires fetish)
   - Fetish rating adds dice
   - Stored in `character_gear` or `modifier_data`
   - Required for some spells
   
5. **Elemental Aid** (for hermetic mages)
   - Bound elementals can provide dice
   - From `character_relationships` where `type='elemental'`
   - Elemental must be present and willing
   
6. **Attuned Power Sites** (environmental)
   - Bonus dice from magical locations
   - Would require campaign/location tracking
   - Future enhancement

**Total Dice Pool:**
```python
dice_pool = force + magic_pool_allocated + totem_modifier + foci_dice + fetish_dice + elemental_dice
```

### Step 2: Calculate Target Number

**Base TN:** Typically 4 (varies by spell type)

**TN Modifiers:**

1. **Background Count** (environmental mana level)
   - Positive background: +TN for spells
   - Negative background: -TN for spells
   - From campaign/location data
   
2. **Sustained Spells** (each active sustained spell)
   - +2 TN per sustained spell
   - Query `character_active_effects` where `duration_type='sustained'`
   
3. **Wound Modifiers** (damage penalties)
   - Light wounds: +1 TN
   - Moderate wounds: +2 TN
   - Serious wounds: +3 TN
   - Deadly wounds: +4 TN
   - From character damage tracking
   
4. **Edge/Flaw Modifiers**
   - Edges may reduce TN (e.g., "Focused Concentration")
   - Flaws may increase TN (e.g., "Incompetent: Sorcery")
   - From `character_edges_flaws` table
   
5. **Visibility/Range** (for combat spells)
   - Partial cover: +2 TN
   - Full cover: +4 TN
   - Long range: +TN based on distance
   - Situational, provided by user/GM

**Total TN:**
```python
target_number = base_tn + background_count + (sustained_spells * 2) + wound_modifier + edge_flaw_modifier + visibility_modifier
```

### Step 3: Roll Dice

**Dice Roll:**
```python
successes = count_successes(roll_dice(dice_pool, target_number))
```

**Special Cases:**
- **No successes:** Spell is miscast (no effect)
- **All ones (Rule of Ones):** Misfire! Drain TN increases by +2
- **Glitch:** If >50% of dice show 1, something goes wrong
- **Critical Glitch:** All dice show 1, catastrophic failure

---

## DRAIN RESISTANCE TEST

### Step 1: Calculate Drain Target Number

**CORRECTED FORMULA:**

```
Drain TN = (Force / 2) rounded down
```

**Examples:**
- Force 1: TN = 0 (minimum 2)
- Force 2: TN = 1 (minimum 2)
- Force 3: TN = 1 (minimum 2)
- Force 4: TN = 2
- Force 5: TN = 2
- Force 6: TN = 3
- Force 8: TN = 4
- Force 10: TN = 5

**Modifiers:**
- **Misfire (all 1s on success test):** +2 to Drain TN
- **Spell stacking:** +2 per stacked spell
- **Multiple targets:** Separate drain test per target

### Step 2: Determine Drain Level (Damage Code)

**From Spell Definition:**
Each spell has a base drain code: L (Light), M (Moderate), S (Serious), D (Deadly)

**Physical vs Stun:**
- If `Force > Magic Rating`: Drain is **PHYSICAL**
- If `Force ≤ Magic Rating`: Drain is **STUN**

**Example Drain Codes:**
- Mana Bolt: (F÷2)M
- Fireball: (F÷2)S
- Heal: (F÷2)D
- Detect Enemies: (F÷2)L

### Step 3: Calculate Drain Resistance Dice Pool

**Base Dice:** Willpower

**Additional Dice:**
1. **Magic Pool** (user-specified allocation)
   - No limit on drain resistance (unlike success test)
   - User specifies how many from Magic Pool
   
2. **Totem Modifiers** (apply to drain too)
   - Same bonuses/penalties as success test
   
3. **Spell Foci** (if applicable)
   - Specific spell foci add dice to drain resistance
   - Category foci add dice to drain resistance
   
4. **Spirit Aid** (if spirit is helping)
   - Spirits can add dice to resist drain

**Total Dice:**
```python
drain_dice = willpower + magic_pool_allocated + totem_modifier + foci_dice + spirit_dice
```

### Step 4: Roll Drain Resistance

**Dice Roll:**
```python
successes = count_successes(roll_dice(drain_dice, drain_tn))
```

**CORRECTED STAGING RULE:**

**Every 2 successes reduces Drain Level by 1 stage**

**Damage Level Progression:**
- L (Light) → No damage
- M (Moderate) → L → No damage
- S (Serious) → M → L → No damage
- D (Deadly) → S → M → L → No damage

**Examples:**
1. Force 6 Mana Bolt (M Stun), Magic 6
   - Drain TN: 3
   - Drain Level: M Stun
   - Roll 8 dice (Willpower 6 + 2 Magic Pool)
   - Get 4 successes → Stages down 2 levels: M → L → None
   - **No drain taken**

2. Force 8 Fireball (S Physical), Magic 6
   - Force > Magic, so Physical drain
   - Drain TN: 4
   - Drain Level: S Physical
   - Roll 6 dice (Willpower only)
   - Get 2 successes → Stages down 1 level: S → M
   - **Take M Physical damage**

### Step 5: Apply Drain Damage

**Update Character:**
```python
if drain_level > 0:
    if drain_type == 'physical':
        apply_physical_damage(character_id, drain_level)
    else:
        apply_stun_damage(character_id, drain_level)
```

---

## SPELL EFFECTS

### Combat Spells

**Damage Calculation:**
```
Damage = Force + Net Successes
```

**Target Resistance:**
- Mana spells: Target resists with Willpower
- Physical spells: Target resists with Body
- Opposed test: Attacker successes vs Defender successes

**Example:**
- Mana Bolt Force 6, 4 successes
- Target rolls Willpower (5 dice), gets 2 successes
- Net: 4 - 2 = 2 successes
- Damage: 6 + 2 = 8M Stun

### Detection Spells

**Success Levels:**
- 1 success: Basic information
- 2-3 successes: Detailed information
- 4+ successes: Comprehensive information

**May create temporary perception bonus:**
```sql
INSERT INTO character_active_effects (
    character_id, effect_type, effect_name,
    target_type, target_name, modifier_value,
    duration_type, force
)
```

### Health Spells

**Healing:**
- Successes heal damage boxes
- May require sustained concentration
- Drain based on severity

**Example - Heal Spell:**
- Force 6, 5 successes
- Heals 5 boxes of damage
- Drain: (6÷2)D = TN 3, Deadly

### Illusion Spells

**Resistance:**
- Target resists with Willpower
- Net successes determine believability
- May create active effect for duration

### Manipulation Spells

**Control Strength:**
- Successes determine control level
- Opposed by target's Willpower
- Create active effect for duration

### Sustained Spells

**If spell requires sustaining:**

```sql
INSERT INTO character_active_effects (
    character_id,
    effect_type,
    effect_name,
    target_type,
    target_name,
    modifier_value,
    duration_type,
    caster_id,
    force,
    drain_taken,
    is_active
) VALUES (
    character_id,
    'spell',
    spell_name,
    'attribute',  -- or 'skill', 'initiative', etc.
    target_attribute,
    modifier_value,
    'sustained',
    caster_id,
    force,
    drain_taken,
    true
)
```

**Effects of Sustaining:**
- +2 TN to all future spellcasting
- Requires concentration
- Can be dropped as Free Action
- Can be disrupted by damage

---

## ADVANCED FEATURES

### Metamagic: Shielding

**Purpose:** Reduce incoming spell damage

**Mechanics:**
- Allocate Magic Pool dice
- Roll against spell's Force
- Each success reduces damage by 1
- Separate from Spell Defense

### Metamagic: Reflecting

**Purpose:** Bounce spell back at caster

**Mechanics:**
- Opposed test: Reflector's Magic vs Spell Force
- If reflector wins, spell bounces back
- Complex resolution

### Metamagic: Centering

**Purpose:** Reduce drain or improve success

**Mechanics:**
- Requires Centering skill
- Additional test before spellcasting
- Successes can reduce drain or add to success

### Spell Stacking

**Multiple spells in one action:**
- +2 TN to all tests per stacked spell
- Magic Pool allocated separately
- Drain tests for each spell
- Resolved in caster's chosen order

### Multiple Targets

**Single spell, multiple targets:**
- Split Force dice among targets
- Separate success test per target
- Separate drain test per target (at full Force TN)
- Magic Pool allocated per target

---

## DATABASE SCHEMA

### Required Tables

#### character_spells
```sql
CREATE TABLE character_spells (
    id UUID PRIMARY KEY,
    character_id UUID REFERENCES characters(id),
    spell_name TEXT NOT NULL,
    spell_category TEXT NOT NULL,  -- 'combat', 'detection', 'health', 'illusion', 'manipulation'
    learned_force INTEGER NOT NULL,
    drain_code TEXT NOT NULL,      -- 'L', 'M', 'S', 'D'
    spell_type TEXT,               -- 'mana', 'physical'
    is_exclusive BOOLEAN,
    notes TEXT
);
```

#### totems
```sql
CREATE TABLE totems (
    id SERIAL PRIMARY KEY,
    totem_name TEXT UNIQUE NOT NULL,
    favored_category TEXT,         -- Category that gets +2
    opposed_category TEXT,         -- Category that gets -2
    special_conditions JSONB,      -- Time/place modifiers
    description TEXT
);
```

#### character_active_effects
```sql
-- Already exists in schema.sql
-- Used for sustained spells, quickened spells, etc.
```

#### spell_casts (audit log)
```sql
CREATE TABLE spell_casts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id),
    spell_name TEXT NOT NULL,
    force INTEGER NOT NULL,
    successes INTEGER,
    drain_taken INTEGER,
    drain_type TEXT,               -- 'stun' or 'physical'
    target_id UUID,                -- If targeting another character
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## IMPLEMENTATION PHASES

### Phase 1: Core Mechanics (MVP)
**Goal:** Basic spellcasting with force validation and drain

**Features:**
- [ ] Force validation against learned_force
- [ ] Basic dice pool (Force + Magic Pool)
- [ ] Simple TN calculation (base + sustained spells)
- [ ] Spell success test
- [ ] Drain calculation (Force÷2, staging with 2 successes)
- [ ] Apply drain damage
- [ ] Record spell cast

**Estimated Effort:** 2-3 days

### Phase 2: Totem & Foci Support
**Goal:** Add magical tradition modifiers

**Features:**
- [ ] Totem bonus/penalty system
- [ ] Power foci integration
- [ ] Spell foci (specific & category)
- [ ] Fetish requirements
- [ ] Enhanced dice pool calculation

**Estimated Effort:** 2 days

### Phase 3: Spell Effects & Sustained Spells
**Goal:** Implement spell categories and effects

**Features:**
- [ ] Combat spell damage calculation
- [ ] Detection spell information levels
- [ ] Health spell healing
- [ ] Illusion spell resistance
- [ ] Manipulation spell control
- [ ] Sustained spell tracking
- [ ] Active effects creation

**Estimated Effort:** 3-4 days

### Phase 4: Advanced Features & Edge Cases
**Goal:** Complete implementation with metamagic and special cases

**Features:**
- [ ] Metamagic: Shielding implementation
- [ ] Metamagic: Reflecting implementation
- [ ] Metamagic: Centering implementation
- [ ] Spell stacking mechanics (+2 TN per spell)
- [ ] Multiple target handling (split Force dice)
- [ ] Background count integration
- [ ] Attuned power site bonuses
- [ ] Edge case handling (glitches, misfires)
- [ ] Comprehensive error handling
- [ ] Performance optimization

**Estimated Effort:** 4-5 days

---

## TESTING STRATEGY

### Unit Tests
**File:** `tests/unit/test_spellcasting_mechanics.py`

**Test Cases:**
1. Force validation
   - Valid force (1 to learned_force)
   - Invalid force (0, negative, above learned)
   - Edge cases (exactly at learned_force)

2. Drain TN calculation
   - Various force levels (1-10)
   - Minimum TN enforcement
   - Misfire modifier (+2)

3. Drain staging
   - 0 successes (no staging)
   - 2 successes (1 level down)
   - 4 successes (2 levels down)
   - Edge cases (staging to no damage)

4. Physical vs Stun determination
   - Force < Magic (Stun)
   - Force = Magic (Stun)
   - Force > Magic (Physical)

### Integration Tests
**File:** `tests/integration/test_spellcasting_integration.py`

**Test Cases:**
1. Complete spell cast workflow
   - Character retrieval
   - Spell data lookup
   - Dice pool calculation
   - Success test
   - Drain resistance
   - Damage application
   - Audit log creation

2. Totem modifier integration
   - Favored category (+2 dice)
   - Opposed category (-2 dice)
   - Neutral category (no modifier)

3. Sustained spell tracking
   - Create active effect
   - TN penalty for future casts
   - Drop sustained spell
   - Multiple sustained spells

4. Foci integration
   - Power foci (adds to Magic Pool)
   - Spell foci (specific & category)
   - Multiple foci stacking

### End-to-End Tests
**File:** `tests/e2e/test_spellcasting_scenarios.py`

**Test Scenarios:**
1. Combat mage casting Mana Bolt
   - Full workflow from character to damage
   - Target resistance
   - Drain application

2. Shaman casting Heal spell
   - High drain (Deadly)
   - Totem bonuses
   - Healing application

3. Street mage with sustained spells
   - Multiple sustained spells active
   - TN penalties accumulating
   - Dropping sustained spells

4. Adept with limited spellcasting
   - Shamanic adept restrictions
   - Category limitations

---

## PERFORMANCE CONSIDERATIONS

### Database Queries
**Optimization Strategies:**

1. **Single Query for Character Data**
   ```sql
   SELECT 
       c.*,
       cr.data->>'totem' as totem,
       COUNT(cae.id) FILTER (WHERE cae.duration_type='sustained') as sustained_count
   FROM characters c
   LEFT JOIN character_relationships cr ON cr.character_id = c.id AND cr.relationship_type = 'totem'
   LEFT JOIN character_active_effects cae ON cae.character_id = c.id AND cae.is_active = true
   WHERE c.id = $1
   GROUP BY c.id, cr.data
   ```

2. **Batch Foci Lookup**
   ```sql
   SELECT * FROM character_gear
   WHERE character_id = $1 
     AND gear_type = 'focus'
     AND (modifications->>'category' = $2 OR modifications->>'spell_name' = $3)
   ```

3. **Indexed Queries**
   - Ensure indexes on `character_id`, `gear_type`, `duration_type`
   - Use JSONB indexes for modifier_data queries

### Caching Strategy
**Cache frequently accessed data:**
- Totem definitions (rarely change)
- Spell definitions (static)
- Character base stats (cache with TTL)

### Dice Rolling Optimization
**Use efficient random number generation:**
```python
import random
def roll_dice(count: int, target_number: int) -> int:
    """Optimized dice rolling"""
    rolls = [random.randint(1, 6) for _ in range(count)]
    return sum(1 for roll in rolls if roll >= target_number)
```

---

## ERROR HANDLING

### Validation Errors
**Clear, actionable error messages:**

```python
class SpellcastingError(Exception):
    """Base exception for spellcasting errors"""
    pass

class InvalidForceError(SpellcastingError):
    """Force validation failed"""
    def __init__(self, force: int, learned_force: int):
        self.force = force
        self.learned_force = learned_force
        super().__init__(
            f"Cannot cast at Force {force}. "
            f"Spell learned at Force {learned_force}. "
            f"Valid range: 1-{learned_force}"
        )

class InsufficientMagicPoolError(SpellcastingError):
    """Not enough Magic Pool dice"""
    def __init__(self, requested: int, available: int):
        super().__init__(
            f"Requested {requested} Magic Pool dice, "
            f"but only {available} available"
        )

class SpellNotFoundError(SpellcastingError):
    """Character doesn't know this spell"""
    def __init__(self, character_name: str, spell_name: str):
        super().__init__(
            f"{character_name} does not know the spell '{spell_name}'"
        )
```

### Database Errors
**Handle connection issues gracefully:**

```python
try:
    result = cast_spell(character_id, spell_name, force, magic_pool_split)
except psycopg.OperationalError as e:
    logger.error(f"Database connection failed: {e}")
    raise SpellcastingError("Unable to connect to database")
except psycopg.IntegrityError as e:
    logger.error(f"Data integrity error: {e}")
    raise SpellcastingError("Invalid data state")
```

### Logging
**Comprehensive logging for debugging:**

```python
import logging

logger = logging.getLogger('spellcasting')

def cast_spell(...):
    logger.info(f"Casting {spell_name} at Force {force}")
    logger.debug(f"Character: {character_id}, Magic Pool: {magic_pool_split}")
    
    # ... casting logic ...
    
    logger.info(f"Success: {successes} successes, Drain: {drain_level} {drain_type}")
    logger.debug(f"Dice pool: {dice_pool}, TN: {target_number}")
```

---

## API REFERENCE

### cast_spell() Function Signature

```python
def cast_spell(
    character_id: str,
    spell_name: str,
    force: int,
    magic_pool_success: int,
    magic_pool_drain: int,
    target_id: Optional[str] = None,
    situational_modifiers: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Cast a spell with full Shadowrun 2E mechanics.
    
    Args:
        character_id: UUID of the casting character
        spell_name: Name of the spell to cast
        force: Force level to cast at (1 to learned_force)
        magic_pool_success: Magic Pool dice allocated to success test
        magic_pool_drain: Magic Pool dice allocated to drain resistance
        target_id: Optional UUID of target character
        situational_modifiers: Optional dict of situational TN modifiers
            {
                'background_count': int,
                'visibility': int,
                'range': int
            }
    
    Returns:
        Dict containing:
        {
            'success': bool,
            'successes': int,
            'spell_effect': str,
            'drain_taken': int,
            'drain_type': str,
            'target_damage': Optional[int],
            'active_effect_id': Optional[str],
            'details': {
                'dice_pool': int,
                'target_number': int,
                'drain_tn': int,
                'drain_level': str,
                'modifiers': Dict[str, int]
            }
        }
    
    Raises:
        InvalidForceError: Force outside valid range
        SpellNotFoundError: Character doesn't know spell
        InsufficientMagicPoolError: Not enough Magic Pool
        SpellcastingError: Other casting errors
    """
```

### Example Usage

```python
# Basic spell cast
result = cast_spell(
    character_id="550e8400-e29b-41d4-a716-446655440000",
    spell_name="Mana Bolt",
    force=6,
    magic_pool_success=4,
    magic_pool_drain=2
)

# Combat spell with target
result = cast_spell(
    character_id="550e8400-e29b-41d4-a716-446655440000",
    spell_name="Fireball",
    force=8,
    magic_pool_success=6,
    magic_pool_drain=0,
    target_id="660e8400-e29b-41d4-a716-446655440001",
    situational_modifiers={
        'visibility': 2,  # Partial cover
        'range': 1        # Long range
    }
)

# Sustained spell
result = cast_spell(
    character_id="550e8400-e29b-41d4-a716-446655440000",
    spell_name="Invisibility",
    force=4,
    magic_pool_success=3,
    magic_pool_drain=3
)
# Creates active_effect, returns active_effect_id
```

---

## FUTURE ENHANCEMENTS

### Phase 5: Ritual Sorcery
- Team spellcasting mechanics
- Material link requirements
- Extended casting times
- Ritual Magic Pool management

### Phase 6: Quickening & Spell Locks
- Permanent spell effects
- Karma cost for quickening
- Spell lock mechanics
- Dispelling quickened spells

### Phase 7: Astral Combat Integration
- Spells in astral space
- Astral perception requirements
- Mana barriers
- Astral signature tracking

### Phase 8: AI-Assisted Spellcasting
- Spell selection recommendations
- Optimal force calculation
- Magic Pool allocation suggestions
- Tactical advice based on situation

---

## APPENDIX A: SPELL EXAMPLES

### Combat Spells

**Mana Bolt**
- Category: Combat
- Type: Mana
- Drain: (F÷2)M
- Range: Line of Sight
- Duration: Instant
- Effect: Force + net successes = Stun damage (resisted by Willpower)

**Fireball**
- Category: Combat
- Type: Physical
- Drain: (F÷2)S
- Range: Line of Sight
- Duration: Instant
- Effect: Force + net successes = Physical damage (resisted by Body)

### Detection Spells

**Detect Enemies**
- Category: Detection
- Type: Mana
- Drain: (F÷2)L
- Range: Force × Magic meters
- Duration: Sustained
- Effect: Reveals hostile intent within range

**Clairvoyance**
- Category: Detection
- Type: Mana
- Drain: (F÷2)M
- Range: Force × Magic meters
- Duration: Sustained
- Effect: Remote viewing of location

### Health Spells

**Heal**
- Category: Health
- Type: Mana
- Drain: (F÷2)D
- Range: Touch
- Duration: Permanent
- Effect: Heals successes boxes of damage

**Treat**
- Category: Health
- Type: Mana
- Drain: (F÷2)L
- Range: Touch
- Duration: Force hours
- Effect: Stabilizes wounds, prevents deterioration

### Illusion Spells

**Invisibility**
- Category: Illusion
- Type: Mana
- Drain: (F÷2)M
- Range: Touch
- Duration: Sustained
- Effect: Target becomes invisible (resisted by Willpower)

**Mask**
- Category: Illusion
- Type: Mana
- Drain: (F÷2)L
- Range: Touch
- Duration: Sustained
- Effect: Changes appearance (resisted by Willpower)

### Manipulation Spells

**Levitate**
- Category: Manipulation
- Type: Physical
- Drain: (F÷2)M
- Range: Line of Sight
- Duration: Sustained
- Effect: Lifts Force × 100 kg

**Control Actions**
- Category: Manipulation
- Type: Mana
- Drain: (F÷2)S
- Range: Line of Sight
- Duration: Sustained
- Effect: Controls target's actions (resisted by Willpower)

---

## APPENDIX B: TOTEM REFERENCE

### Wilderness Totems

**Bear**
- Favored: Health (+2)
- Opposed: Combat (-2)
- Environment: Forest, mountains
- Personality: Protective, nurturing

**Eagle**
- Favored: Detection (+2)
- Opposed: Manipulation (-2)
- Environment: Mountains, open sky
- Personality: Proud, far-seeing

**Wolf**
- Favored: Detection (+2)
- Opposed: Illusion (-2)
- Environment: Forest, plains
- Personality: Pack-oriented, loyal

### Urban Totems

**Coyote**
- Favored: None
- Opposed: None
- Special: No modifiers, but trickster nature
- Personality: Cunning, unpredictable

**Rat**
- Favored: Illusion (+2)
- Opposed: Combat (-2)
- Environment: Urban, sewers
- Personality: Survivor, adaptable

**Dog**
- Favored: Detection (+2)
- Opposed: Illusion (-2)
- Environment: Urban, anywhere humans are
- Personality: Loyal, protective

---

## DOCUMENT HISTORY

**Version 1.0** (2025-10-28)
- Initial specification
- Corrected drain mechanics (Force÷2, 2 successes per stage)
- Complete system coverage
- Implementation phases defined
- Testing strategy outlined
- API reference added

---

**END OF SPECIFICATION**
