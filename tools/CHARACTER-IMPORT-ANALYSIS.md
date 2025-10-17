# Character Import Analysis

## Character File Structure

Based on analysis of existing character markdown files in `D:\RPG\Shadowrun\shadowrun 2e\characters`:

### File Format
- **Format**: Markdown (.markdown)
- **Structure**: Hierarchical sections with headers
- **Data**: Mix of structured fields and free-form text

### Character Types Found
1. **Player Characters** (Platinum, Oak, Manticore, Block, Axel, Raven)
2. **NPCs/Special Entities** (KARR - AI description, not a character)

## Schema Compatibility Analysis

### ✅ PERFECT FIT - Direct Mapping

| Character Field | Database Column | Notes |
|----------------|-----------------|-------|
| Name | `name` | Direct string |
| Street Name | `biography->>'street_name'` | JSONB field |
| Race | `metatype_id` | Requires lookup to metatypes table |
| Sex | `biography->>'sex'` | JSONB field |
| Concept | `biography->>'concept'` | JSONB field |
| Description | `biography->>'appearance'` | JSONB field |
| Nuyen | `biography->>'nuyen'` | JSONB field |
| Lifestyle | `biography->>'lifestyle'` | JSONB field |
| Karma Pool | `karma_pool` | Direct integer |
| Total Karma | `good_karma` | Direct integer |
| Essence | `essence` | Direct decimal |
| Reaction | `attributes->>'reaction'` | JSONB field |
| Initiative | `biography->>'initiative'` | JSONB field (calculated) |
| Combat Pool | `biography->>'combat_pool'` | JSONB field (calculated) |
| Body Index | `biography->>'body_index'` | JSONB field (bioware tracking) |

### ✅ ATTRIBUTES - Perfect Match

All attributes map to `attributes` JSONB:
```json
{
  "body": 10,
  "quickness": 15,
  "strength": 14,
  "charisma": 4,
  "intelligence": 12,
  "willpower": 9,
  "essence": 2.55,
  "magic": 0,
  "reaction": 27
}
```

### ✅ EDGES/FLAWS - Requires Reference Table

Character files list edges/flaws by name:
- **Platinum**: Exceptional Attribute-Quickness, Ambidexterity, Amnesia, Distinctive Style, Guilt Spur
- **Raven**: None listed

**Storage**: `qualities_taken` JSONB array
```json
[1, 5, 12, 23, 45]  // quality IDs after lookup
```

**Action Required**: Populate `qualities` reference table first

### ✅ SKILLS - Requires Reference Table

Character files list skills with ratings and modifiers:
- **Format**: "Skill Name: Rating (modifiers/notes)"
- **Examples**: 
  - "Firearms: 7 (8 with Reflex Recorder, 9 dice with Enhanced Articulation)"
  - "Sorcery: 6"

**Storage**: `skills_data` JSONB array
```json
[
  {
    "skill_id": 123,
    "skill_name": "Firearms",
    "rating": 7,
    "specialization": null,
    "notes": "8 with Reflex Recorder, 9 dice with Enhanced Articulation"
  },
  {
    "skill_id": 124,
    "skill_name": "Whips",
    "rating": 2,
    "specialization": "Monowhip",
    "notes": "specialization 6, 7 dice"
  }
]
```

**Action Required**: Populate `skills` reference table first

### ✅ CYBERWARE/BIOWARE - Requires Gear Table

Character files list cyber/bioware with essence/body index costs:
- **Platinum**: Wired Reflexes 3 (Beta), Reaction Enhancers 6 (Delta), Cybereyes, etc.
- **Raven**: None (mage, Essence 6)

**Storage**: `cyberware_installed` JSONB array
```json
[
  {
    "gear_id": 456,
    "name": "Wired Reflexes 3 (Beta-Grade)",
    "essence_cost": 2.4,
    "body_index": 0,
    "notes": "+6 Reaction, +3D6 Initiative"
  },
  {
    "gear_id": 457,
    "name": "Enhanced Articulation",
    "essence_cost": 0,
    "body_index": 0.3,
    "notes": "+1 die to physical skills, +1 Reaction"
  }
]
```

**Action Required**: Cyberware already in `gear` table (561 items loaded)

### ✅ SPELLS - Requires Reference Table

Character files list spells (for mages):
- **Raven**: Manabolt 5, Invisibility 4, Levitate 3, Detect Enemies 4, Heal 4

**Storage**: `spells_known` JSONB array
```json
[
  {
    "spell_id": 789,
    "spell_name": "Manabolt",
    "force": 5
  },
  {
    "spell_id": 790,
    "spell_name": "Invisibility",
    "force": 4
  }
]
```

**Action Required**: Populate `spells` reference table first

### ✅ CONTACTS - Can Store Directly

Character files list contacts with levels:
- **Platinum**: Tanis Driscol (Level 2), Volaren (Level 2), Fuzzy Eddy (Level 2), etc.

**Storage Option 1**: `contacts_list` JSONB array (simpler for import)
```json
[
  {
    "name": "Tanis Driscol",
    "archetype": "DocWagon Manager",
    "loyalty": 2,
    "connection": 2
  }
]
```

**Storage Option 2**: Create entries in `contacts` table and reference by ID
- More normalized
- Allows sharing contacts between characters
- Better for campaign management

**Recommendation**: Use JSONB for initial import, migrate to contacts table later

### ✅ GEAR - Complex but Manageable

Character files have extensive gear lists organized by category:
- Weapons (with ammo types and quantities)
- Armor (worn vs stored)
- Vehicles
- Equipment
- Go bags with nested items

**Storage**: `gear_owned` JSONB array
```json
[
  {
    "gear_id": 234,
    "name": "Morrissey Alta",
    "category": "weapon",
    "quantity": 1,
    "location": "worn",
    "notes": "Conceal 6, 12(c), SA, 9S Stun with gel ammo",
    "ammo": [
      {"type": "Silver APDS", "quantity": 80},
      {"type": "APDS", "quantity": 24}
    ]
  },
  {
    "name": "GMC Bulldog Stepvan",
    "category": "vehicle",
    "quantity": 1,
    "location": "owned",
    "notes": "Handling 4/8, Speed 90, Body 8, Armor 4"
  }
]
```

**Challenge**: Gear items may not all be in `gear` table (only cyberware loaded so far)
**Solution**: Store as free-form JSONB initially, link to gear table where possible

## Import Strategy

### Phase 1: Reference Data (REQUIRED FIRST)
1. ✅ Metatypes (Human, Elf, Dwarf, Ork, Troll)
2. ⏳ Qualities (Edges + Flaws)
3. ⏳ Skills (All skills from character sheets)
4. ⏳ Spells (All spells from mage characters)
5. ⏳ Powers (If any adepts exist)
6. ⏳ Totems (If any shamans exist)

### Phase 2: Character Import
1. Parse markdown files
2. Extract structured data
3. Look up reference IDs (metatypes, skills, spells, qualities)
4. Build JSONB structures
5. Insert into `sr_characters` table
6. Validate essence calculations

### Phase 3: Validation
1. Verify all characters imported
2. Check essence calculations match
3. Validate attribute totals
4. Ensure all skills/spells/gear captured

## Parsing Challenges

### 1. Inconsistent Formatting
- Some fields have extra notes in parentheses
- Skill modifiers vary in format
- Gear descriptions are free-form

**Solution**: Flexible regex patterns, store raw text in notes fields

### 2. Calculated Values
- Initiative, Combat Pool, Spell Pool are derived
- Need to preserve both base and modified values

**Solution**: Store formulas in notes, calculated values in separate fields

### 3. Nested Structures
- Go bags contain multiple items
- Weapons have multiple ammo types
- Cyberware has multiple effects

**Solution**: Use nested JSONB arrays/objects

### 4. Missing Reference Data
- Not all skills/spells/gear may be in reference tables yet

**Solution**: 
- Import what we can link
- Store unlinked items as free-form JSONB with names
- Flag for manual review

## Recommended Import Tool Features

1. **Markdown Parser**: Extract sections and fields
2. **Reference Lookup**: Match names to IDs in reference tables
3. **JSONB Builder**: Construct proper JSON structures
4. **Validation**: Check essence, attributes, required fields
5. **Dry Run Mode**: Preview import without committing
6. **Error Reporting**: List unmatched references, validation failures
7. **Manual Override**: Allow fixing mismatches interactively

## Conclusion

### ✅ Schema is EXCELLENT for these characters!

The `sr_characters` table with JSONB fields is **perfectly suited** for importing these markdown character sheets:

1. **Flexible**: JSONB handles varying data structures
2. **Complete**: All character data can be stored
3. **Queryable**: Can still search/filter on key fields
4. **Extensible**: Easy to add new fields as needed

### Next Steps

1. **Load Reference Data**: Populate metatypes, qualities, skills, spells tables
2. **Build Import Tool**: Python script to parse markdown and insert characters
3. **Test Import**: Start with one character (Raven - simpler mage)
4. **Iterate**: Refine parser based on results
5. **Bulk Import**: Load all 6 characters
6. **Validate**: Verify data integrity

The schema design was excellent - no changes needed! 🎉
