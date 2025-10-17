# Shapeshifter Character Handling

## The Challenge

Shapeshifters like Block (Rhino) have **dual stat sets**:
- **Human Form**: One set of attributes, skills, powers
- **Animal Form**: Different attributes, natural abilities, restrictions

### Block's Dual Stats Example

| Attribute | Human | Rhino |
|-----------|-------|-------|
| Body | 6 | 9 |
| Quickness | 2 | 1 |
| Strength | 5 | 8 |
| Charisma | 4 | 4 |
| Intelligence | 5 | 4 |
| Willpower | 5 | 4 |
| Reaction | 3 | 2 |

**Additional Complexities:**
- Adept powers only work in human form
- Natural weapons/armor in animal form
- Regeneration in animal form
- Dual nature (astral + physical)
- Form-specific restrictions

## Solution: JSONB Shapeshifter Structure

### Option 1: Nested Forms (RECOMMENDED)

Store both forms in the `attributes` JSONB with a `current_form` indicator:

```json
{
  "current_form": "human",
  "human": {
    "body": 6,
    "quickness": 2,
    "strength": 5,
    "charisma": 4,
    "intelligence": 5,
    "willpower": 5,
    "reaction": 3,
    "essence": 6,
    "magic": 9
  },
  "rhino": {
    "body": 9,
    "quickness": 1,
    "strength": 8,
    "charisma": 4,
    "intelligence": 4,
    "willpower": 4,
    "reaction": 2,
    "essence": 6,
    "magic": 9
  }
}
```

**Advantages:**
- ✅ Both forms in one place
- ✅ Easy to query current form
- ✅ Simple to switch forms
- ✅ Clear structure

**Queries:**
```sql
-- Get current form attributes
SELECT attributes->current_form FROM sr_characters WHERE id = 1;

-- Get human form body
SELECT attributes->'human'->>'body' FROM sr_characters WHERE id = 1;

-- Switch forms (update current_form)
UPDATE sr_characters 
SET attributes = jsonb_set(attributes, '{current_form}', '"rhino"')
WHERE id = 1;
```

### Option 2: Separate Shapeshifter Field

Keep `attributes` for current/active stats, add `shapeshifter_forms` JSONB:

```json
// attributes (current active form)
{
  "body": 6,
  "quickness": 2,
  "strength": 5,
  ...
}

// shapeshifter_forms (all forms)
{
  "current": "human",
  "forms": {
    "human": {
      "body": 6,
      "quickness": 2,
      ...
    },
    "rhino": {
      "body": 9,
      "quickness": 1,
      ...
    }
  },
  "animal_traits": {
    "natural_weapons": "Horns (10S Physical)",
    "natural_armor": "+2 Ballistic / +4 Impact",
    "regeneration": true,
    "dual_nature": true
  }
}
```

**Advantages:**
- ✅ `attributes` always shows active stats
- ✅ Shapeshifter data isolated
- ✅ Easy to identify shapeshifters
- ✅ Animal traits clearly separated

**Disadvantages:**
- ⚠️ Data duplication (current form in two places)
- ⚠️ Need to sync on form change

### Option 3: Biography Field Extension

Store shapeshifter info in `biography` JSONB:

```json
{
  "background": "Refugee from Zimbabwe...",
  "appearance": "Rhino form: Massive, armored hide...",
  "shapeshifter": {
    "animal_type": "rhino",
    "current_form": "human",
    "rhino_stats": {
      "body": 9,
      "quickness": 1,
      ...
    },
    "traits": {
      "natural_weapons": "Horns (10S Physical)",
      "natural_armor": "+2/+4",
      "regeneration": true
    }
  }
}
```

**Advantages:**
- ✅ No schema changes needed
- ✅ Keeps character-specific data together

**Disadvantages:**
- ⚠️ Harder to query shapeshifter stats
- ⚠️ Mixing biographical and mechanical data

## RECOMMENDED APPROACH: Option 1 (Nested Forms)

### Implementation for Block

```json
{
  "name": "Block",
  "player_name": "Player Name",
  "metatype_id": 999,  // Shapeshifter (Rhino) - custom metatype
  
  "attributes": {
    "current_form": "human",
    "human": {
      "body": 6,
      "quickness": 2,
      "strength": 5,
      "charisma": 4,
      "intelligence": 5,
      "willpower": 5,
      "reaction": 3,
      "essence": 6,
      "magic": 9
    },
    "rhino": {
      "body": 9,
      "quickness": 1,
      "strength": 8,
      "charisma": 4,
      "intelligence": 4,
      "willpower": 4,
      "reaction": 2,
      "essence": 6,
      "magic": 9
    }
  },
  
  "essence": 6.00,
  "karma_pool": 8,
  "good_karma": 11,
  
  "skills_data": [
    {
      "skill_id": 123,
      "skill_name": "Sorcery",
      "rating": 7,
      "notes": "Aptitude: -1 TN"
    },
    {
      "skill_id": 124,
      "skill_name": "Conjuring",
      "rating": 5
    }
  ],
  
  "powers_active": [
    {
      "power_id": 456,
      "power_name": "Missile Mastery",
      "level": 1,
      "notes": "Human form only"
    },
    {
      "power_id": 457,
      "power_name": "Traceless Walk",
      "level": 0.5
    },
    {
      "power_id": 458,
      "power_name": "Pain Resistance",
      "level": 0.5
    },
    {
      "power_id": 459,
      "power_name": "Empathic Healing",
      "level": 1
    }
  ],
  
  "spells_known": [
    {"spell_id": 789, "spell_name": "Stunbolt", "force": 3},
    {"spell_id": 790, "spell_name": "Stunball", "force": 9},
    {"spell_id": 791, "spell_name": "Improved Invisibility", "force": 1}
  ],
  
  "biography": {
    "street_name": "Block",
    "concept": "Physical Magician, Hermetic tradition",
    "appearance": "Rhino form: Massive, armored hide; Human form: Stocky, tough build",
    "background": "Refugee from Zimbabwe, hiding in Seattle from hunters like Kraven",
    "nuyen": "595,543¥",
    "lifestyle": "Low (1 month prepaid)",
    "initiative": "3 +4D6 / 2 +4D6",
    "combat_pool": "4 (human)",
    "magic_pool": "13 (5 spellcasting, 3 adept)",
    "initiate_level": "2 (masking, centering)",
    "tradition": "Hermetic (nosferatu group)",
    
    "shapeshifter_traits": {
      "animal_type": "Rhino (custom)",
      "natural_weapons": "Horns (10S Physical)",
      "natural_armor": "+2 Ballistic / +4 Impact",
      "regeneration": "Heals Essence boxes per turn (except silver)",
      "dual_nature": "Perceives astrally, vulnerable to astral attacks",
      "shift_action": "Complex Action",
      "adept_restriction": "Powers only work in human form",
      "vulnerabilities": ["Silver (mandatory flaw)"]
    }
  }
}
```

## Metatype Table Entry for Shapeshifters

```sql
INSERT INTO metatypes (name, variant_of, is_variant, description, special_abilities, racial_traits)
VALUES (
  'Shapeshifter (Rhino)',
  'Shapeshifter',
  true,
  'Custom rhino shapeshifter with dual nature and regeneration',
  ARRAY['Dual Nature', 'Regeneration', 'Shapeshifting'],
  '{
    "animal_type": "rhino",
    "natural_weapons": "Horns (10S Physical)",
    "natural_armor": "+2 Ballistic / +4 Impact",
    "regeneration": true,
    "dual_nature": true,
    "vulnerabilities": ["silver"],
    "form_change": "Complex Action"
  }'::jsonb
);
```

## Helper Functions for Shapeshifters

```sql
-- Get current form attributes
CREATE OR REPLACE FUNCTION get_current_form_attributes(char_id INTEGER)
RETURNS JSONB AS $$
DECLARE
    current_form TEXT;
    attrs JSONB;
BEGIN
    SELECT attributes->>'current_form' INTO current_form
    FROM sr_characters WHERE id = char_id;
    
    SELECT attributes->current_form INTO attrs
    FROM sr_characters WHERE id = char_id;
    
    RETURN attrs;
END;
$$ LANGUAGE plpgsql;

-- Switch forms
CREATE OR REPLACE FUNCTION switch_form(char_id INTEGER, new_form TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE sr_characters
    SET attributes = jsonb_set(attributes, '{current_form}', to_jsonb(new_form))
    WHERE id = char_id;
END;
$$ LANGUAGE plpgsql;

-- Check if character is shapeshifter
CREATE OR REPLACE FUNCTION is_shapeshifter(char_id INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    has_forms BOOLEAN;
BEGIN
    SELECT attributes ? 'current_form' INTO has_forms
    FROM sr_characters WHERE id = char_id;
    
    RETURN COALESCE(has_forms, false);
END;
$$ LANGUAGE plpgsql;
```

## Import Considerations

When importing Block's character:

1. **Detect Shapeshifter**: Look for dual stats (e.g., "6 / 9" format)
2. **Parse Both Forms**: Extract human and animal stats separately
3. **Set Current Form**: Default to "human" unless specified
4. **Store Traits**: Capture natural weapons, armor, regeneration
5. **Flag Powers**: Note which powers are form-restricted
6. **Create Metatype**: Add custom "Shapeshifter (Rhino)" to metatypes table

## Querying Shapeshifters

```sql
-- Find all shapeshifters
SELECT name, attributes->>'current_form' as current_form
FROM sr_characters
WHERE attributes ? 'current_form';

-- Get Block's rhino form body
SELECT attributes->'rhino'->>'body' as rhino_body
FROM sr_characters
WHERE name = 'Block';

-- Compare forms
SELECT 
    name,
    attributes->'human'->>'body' as human_body,
    attributes->'rhino'->>'body' as rhino_body
FROM sr_characters
WHERE attributes ? 'current_form';
```

## Conclusion

**Option 1 (Nested Forms in attributes JSONB) is the best solution** because:

✅ Clean, intuitive structure  
✅ Easy to query and update  
✅ No schema changes needed  
✅ Supports any number of forms (if needed)  
✅ Clear separation of form-specific data  
✅ Simple form switching  

The existing schema handles shapeshifters perfectly with JSONB flexibility!
