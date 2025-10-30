# MCP Tools Reference

This document describes all available MCP tools for the Shadowrun GM system.

## Available Tools

### 1. get_character

Get complete character data including attributes, skills, cyberware, bioware, and gear.

**Parameters:**
- `character_name` (string, required): Name or street name of the character

**Returns:**
- Complete character sheet data
- All attributes (base and augmented)
- Skills grouped by type
- Cyberware with essence costs
- Bioware with body index costs
- Weapons, armor, equipment
- Vehicles, cyberdecks, contacts
- Edges, flaws, spells, spirits

**Example:**
```json
{
  "character_name": "Platinum"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Platinum",
  "street_name": "Platinum",
  "attributes": {
    "body": 6,
    "quickness": 7,
    "strength": 4,
    ...
  },
  "skills": {
    "active": [...],
    "knowledge": [...],
    "language": [...]
  },
  "cyberware": [...],
  "bioware": [...],
  ...
}
```

---

### 2. get_character_skill

Get a specific skill rating and associated attribute for a character.

**Parameters:**
- `character_name` (string, required): Name of the character
- `skill_name` (string, required): Name of the skill (e.g., 'Firearms', 'Sorcery')

**Returns:**
- Skill rating
- Associated attribute and rating
- Specialization (if any)

**Example:**
```json
{
  "character_name": "Block",
  "skill_name": "Sorcery"
}
```

**Response:**
```json
{
  "character": "Block",
  "skill": "Sorcery",
  "skill_rating": 7,
  "attribute": "willpower",
  "attribute_rating": 5,
  "specialization": null
}
```

---

### 3. calculate_dice_pool

Calculate total dice pool from skill, attribute, and modifiers.

**Parameters:**
- `skill_rating` (integer, required): Skill rating
- `attribute_rating` (integer, required): Attribute rating
- `modifiers` (array of integers, optional): List of modifier values

**Returns:**
- Total dice pool
- Breakdown of calculation

**Example:**
```json
{
  "skill_rating": 5,
  "attribute_rating": 6,
  "modifiers": [2, -1]
}
```

**Response:**
```json
{
  "pool": 12,
  "breakdown": "5 (skill) + 6 (attribute) + 1 (modifiers)",
  "skill": 5,
  "attribute": 6,
  "modifiers": 1
}
```

---

### 4. calculate_target_number

Calculate target number for a given situation and difficulty.

**Parameters:**
- `situation` (string, required): Description of the situation
- `difficulty` (string, optional): Difficulty level (trivial, easy, average, difficult, very_difficult)

**Returns:**
- Target number
- Breakdown explanation

**Example:**
```json
{
  "situation": "Picking a standard lock",
  "difficulty": "average"
}
```

**Response:**
```json
{
  "target_number": 5,
  "situation": "Picking a standard lock",
  "difficulty": "average",
  "breakdown": "Base TN 5 for average task"
}
```

---

### 5. roll_dice

Roll dice pool against target number using Shadowrun rules (exploding 6s).

**Parameters:**
- `pool` (integer, required): Number of dice to roll
- `target_number` (integer, required): Target number for successes

**Returns:**
- Individual die rolls
- Number of successes
- Success/failure result
- Critical glitch detection

**Example:**
```json
{
  "pool": 8,
  "target_number": 5
}
```

**Response:**
```json
{
  "pool": 8,
  "target_number": 5,
  "rolls": [6, 4, 5, 2, 6, 3, 5, 1, 4, 6, 2],
  "successes": 5,
  "result": "success",
  "all_ones": false,
  "critical_glitch": false
}
```

---

### 6. calculate_ranged_attack

Calculate complete ranged attack with all character modifiers, vision enhancements, and environmental factors.

**Parameters:**
- `character_name` (string, required): Name of character making the attack
- `weapon_name` (string, required): Name of weapon (e.g., 'Morrissey Alta', 'Ares Predator')
- `target_distance` (integer, required): Distance to target in meters
- `target_description` (string, required): Description of target (e.g., 'rat', 'human', 'large troll')
- `environment` (string, required): Environmental conditions (e.g., 'complete darkness', 'dim light', 'normal light')
- `combat_pool` (integer, optional): Number of combat pool dice to use (0 for calculation only)

**Returns:**
- Base target number (determined by range category)
- All applicable modifiers (smartlink, vision, range, etc.)
- Final target number
- Dice rolls (if combat_pool > 0)
- Detailed breakdown

**Vision Magnification and Range Categories:**

Vision magnification (from cybereyes, scopes, etc.) shifts the range category DOWN toward "short":
- **Mag ×1**: extreme→long, long→medium, medium→short, short→short
- **Mag ×2**: extreme→medium, long→short, medium→short, short→short  
- **Mag ×3**: extreme→short, long→short, medium→short, short→short

Each level of magnification moves the effective range category one step closer to "short", which reduces the base target number:
- **Short range**: Base TN 4
- **Medium range**: Base TN 5
- **Long range**: Base TN 6
- **Extreme range**: Base TN 9

**Example**: Shooting at 55m with a hold-out pistol (short range 0-15m, medium 16-30m, long 31-45m, extreme 46-60m):
- Without magnification: 55m = extreme range (Base TN 9)
- With Mag ×1: 55m = long range (Base TN 6)
- With Mag ×2: 55m = medium range (Base TN 5)
- With Mag ×3: 55m = short range (Base TN 4)

**Example:**
```json
{
  "character_name": "Platinum",
  "weapon_name": "Morrissey Alta",
  "target_distance": 5,
  "target_description": "rat in sewer",
  "environment": "dim light",
  "combat_pool": 8
}
```

**Response:**
```json
{
  "character": "Platinum",
  "weapon": "Morrissey Alta",
  "weapon_type": "hold-out pistol",
  "target_distance": 5,
  "vision_magnification": 3,
  "range_category": "short",
  "light_level": "DIM",
  "vision_enhancements": {
    "thermographic": "cybernetic",
    "lowLight": "cybernetic",
    "magnification": 3
  },
  "combat_modifiers": [
    {
      "source": "Smartlink-3 Prototype",
      "type": "cyberware",
      "value": -3
    }
  ],
  "base_tn": 4,
  "combat_bonus": -3,
  "final_tn": 2,
  "roll": {
    "rolls": [6, 5, 4, 2, 6, 3, 5, 1, 4],
    "successes": 8,
    "all_ones": false
  }
}
```

---

### 7. cast_spell

Cast a spell in Shadowrun 2nd Edition with complete Magic Pool management, totem bonuses/penalties, spell foci, automatic drain calculation, and sustained spell tracking.

**Parameters:**
- `caster_name` (string, required): Name of character casting the spell
- `spell_name` (string, required): Name of spell (e.g., 'Levitate', 'Fireball', 'Heal', 'Armor')
- `force` (integer, required): Force level of spell (1-12, determines TN and drain)
- `target_name` (string, required): Name of target ('self' for self-targeted spells, or another character name)
- `spell_pool_dice` (integer, required): Magic Pool dice allocated to spellcasting
- `drain_pool_dice` (integer, required): Magic Pool dice allocated to drain resistance

**Returns:**
- Complete spellcasting results with all modifiers
- Totem bonuses/penalties (if applicable)
- Spell focus/fetish bonuses (if applicable)
- Spell roll with successes
- Drain calculation and resistance
- Sustained spell tracking (if spell has duration "Sustained")
- Detailed summary

**Sustained Spells:**
When a spell with duration "Sustained" is successfully cast, the system automatically:
1. Creates modifiers in the `character_modifiers` table for spell effects
2. Tracks the spell as sustained by the caster
3. Applies a -2 dice pool penalty per sustained spell to ALL actions
4. Allows the caster to drop sustained spells at any time

**Sustained Spell Examples:**
- **Armor**: Adds armor rating to target (Impact and Ballistic)
- **Increase Attribute**: Boosts an attribute temporarily
- **Levitate**: Allows target to fly
- **Invisibility**: Makes target invisible

**Sustaining Penalty:**
- Each sustained spell: -2 dice from ALL dice pools
- Cumulative: 3 sustained spells = -6 dice penalty
- Applies to combat, spellcasting, skills, everything
- Penalty removed when spell is dropped

**IMPORTANT: Magic Pool Split**

The Magic Pool MUST be split between spellcasting and drain resistance:
- **spell_pool_dice**: Added to Sorcery skill for the spellcasting test
- **drain_pool_dice**: Added to Willpower for resisting drain
- **Total**: spell_pool_dice + drain_pool_dice cannot exceed Magic rating

This is a MANDATORY mechanic in Shadowrun 2nd Edition. The AI must always ask the player how they want to split their Magic Pool before calling this tool.

**Shadowrun 2nd Edition Mechanics:**

**Spellcasting:**
- **Dice Pool**: Sorcery + spell_pool_dice + totem_bonus + focus_bonus
- **Target Number**: Equal to Force of spell
- **Success**: Any successes = spell succeeds
- **Totem Bonus**: +2 dice for favored spell categories
- **Totem Penalty**: -2 dice for opposed spell categories (20 of 55 totems have these)
- **Spell Focus**: Bonus dice if focus Force >= spell Force

**Drain:**
- **Base Drain**: Force / 2 (rounded down)
- **Drain Code**: M (Mental) for Force 1-6, S (Serious) for Force 7+
- **Drain Modifier**: Some spells add to drain (e.g., deadly spells)
- **Resistance**: Willpower + drain_pool_dice
- **Damage**: Drain Level - Successes (minimum 0)

**Totem Examples:**
- **Bear**: +2 Health spells (no opposed categories)
- **Cat**: +2 Illusion, -2 Combat
- **Boar**: +2 Combat, -2 Illusion
- **Dragonslayer**: +2 Combat, -2 Combat AND Illusion (penalty to own favored!)
- **Horse**: +2 Health, -2 Combat AND Illusion

**Basic Example (No Totem Modifiers):**
```json
{
  "caster_name": "Manticore",
  "spell_name": "Levitate",
  "force": 4,
  "target_name": "self",
  "spell_pool_dice": 2,
  "drain_pool_dice": 2
}
```

**Response:**
```json
{
  "caster": "Manticore",
  "spell": "Levitate",
  "spell_category": "Manipulation",
  "force": 4,
  "target": "self",
  "sorcery_skill": 6,
  "magic_rating": 6,
  "spell_pool_dice": 2,
  "drain_pool_dice": 2,
  "totem_name": "Bear",
  "totem_bonus": 0,
  "focus_name": null,
  "focus_bonus": 0,
  "spell_dice_pool": 8,
  "target_number": 4,
  "spell_roll": {
    "rolls": [6, 5, 4, 3, 2, 1, 4, 6],
    "successes": 5,
    "result": "success"
  },
  "drain": {
    "base_level": 2,
    "modifier": 0,
    "total_level": 2,
    "code": "M",
    "resist_dice": 6,
    "resist_roll": {
      "rolls": [5, 4, 3, 2, 1, 6],
      "successes": 4
    },
    "damage_taken": 0
  },
  "summary": "Manticore casts Levitate at Force 4 on self. Spell pool: 6 (Sorcery) + 2 (Magic Pool) = 8 dice vs TN 4. Rolled 5 successes - spell succeeds! Drain: 2M, resisted with 6 dice (4 (Willpower) + 2 (Magic Pool)), took 0 damage."
}
```

**Example with Totem Bonus:**
```json
{
  "caster_name": "Manticore",
  "spell_name": "Heal",
  "force": 3,
  "target_name": "self",
  "spell_pool_dice": 2,
  "drain_pool_dice": 3
}
```

**Response:**
```json
{
  "caster": "Manticore",
  "spell": "Heal",
  "spell_category": "Health",
  "force": 3,
  "target": "self",
  "sorcery_skill": 6,
  "magic_rating": 6,
  "spell_pool_dice": 2,
  "drain_pool_dice": 3,
  "totem_name": "Bear",
  "totem_bonus": 2,
  "focus_name": "Health Spell Focus (Force 4)",
  "focus_bonus": 2,
  "spell_dice_pool": 12,
  "target_number": 3,
  "spell_roll": {
    "rolls": [6, 5, 4, 3, 2, 1, 4, 6, 5, 3, 2, 6, 4],
    "successes": 10,
    "result": "success"
  },
  "drain": {
    "base_level": 1,
    "modifier": 0,
    "total_level": 1,
    "code": "M",
    "resist_dice": 7,
    "resist_roll": {
      "rolls": [5, 4, 3, 2, 1, 6, 5],
      "successes": 5
    },
    "damage_taken": 0
  },
  "summary": "Manticore casts Heal at Force 3 on self. Bear totem grants +2 dice for Health spells. Health Spell Focus (Force 4) grants +2 dice. Spell pool: 6 (Sorcery) + 2 (Magic Pool) + 2 (totem) + 2 (focus) = 12 dice vs TN 3. Rolled 10 successes - spell succeeds! Drain: 1M, resisted with 7 dice (4 (Willpower) + 3 (Magic Pool)), took 0 damage."
}
```

**Example with Totem Penalty:**
```json
{
  "caster_name": "Shadow",
  "spell_name": "Fireball",
  "force": 6,
  "target_name": "enemy",
  "spell_pool_dice": 3,
  "drain_pool_dice": 2
}
```

**Response (assuming Shadow has Cat totem):**
```json
{
  "caster": "Shadow",
  "spell": "Fireball",
  "spell_category": "Combat",
  "force": 6,
  "target": "enemy",
  "sorcery_skill": 5,
  "magic_rating": 5,
  "spell_pool_dice": 3,
  "drain_pool_dice": 2,
  "totem_name": "Cat",
  "totem_bonus": -2,
  "focus_name": null,
  "focus_bonus": 0,
  "spell_dice_pool": 6,
  "target_number": 6,
  "spell_roll": {
    "rolls": [6, 5, 4, 3, 2, 1, 6],
    "successes": 2,
    "result": "success"
  },
  "drain": {
    "base_level": 3,
    "modifier": 0,
    "total_level": 3,
    "code": "M",
    "resist_dice": 6,
    "resist_roll": {
      "rolls": [5, 4, 3, 2, 1, 6],
      "successes": 3
    },
    "damage_taken": 0
  },
  "summary": "Shadow casts Fireball at Force 6 on enemy. Cat totem imposes -2 dice penalty for Combat spells. Spell pool: 5 (Sorcery) + 3 (Magic Pool) - 2 (totem penalty) = 6 dice vs TN 6. Rolled 2 successes - spell succeeds! Drain: 3M, resisted with 6 dice (4 (Willpower) + 2 (Magic Pool)), took 0 damage."
}
```

**High Force Example:**
```json
{
  "caster_name": "Manticore",
  "spell_name": "Powerball",
  "force": 8,
  "target_name": "enemy",
  "spell_pool_dice": 2,
  "drain_pool_dice": 4
}
```

**Response:**
```json
{
  "caster": "Manticore",
  "spell": "Powerball",
  "spell_category": "Combat",
  "force": 8,
  "target": "enemy",
  "sorcery_skill": 6,
  "magic_rating": 6,
  "spell_pool_dice": 2,
  "drain_pool_dice": 4,
  "totem_name": "Bear",
  "totem_bonus": 0,
  "focus_name": null,
  "focus_bonus": 0,
  "spell_dice_pool": 8,
  "target_number": 8,
  "spell_roll": {
    "rolls": [6, 5, 4, 3, 2, 1, 4, 6, 5],
    "successes": 2,
    "result": "success"
  },
  "drain": {
    "base_level": 4,
    "modifier": 0,
    "total_level": 4,
    "code": "S",
    "resist_dice": 8,
    "resist_roll": {
      "rolls": [5, 4, 3, 2, 1, 6, 5, 4],
      "successes": 5
    },
    "damage_taken": 0
  },
  "summary": "Manticore casts Powerball at Force 8 on enemy. Spell pool: 6 (Sorcery) + 2 (Magic Pool) = 8 dice vs TN 8. Rolled 2 successes - spell succeeds! Drain: 4S (Serious), resisted with 8 dice (4 (Willpower) + 4 (Magic Pool)), took 0 damage."
}
```

**Error Example (Magic Pool Exceeded):**
```json
{
  "caster_name": "Manticore",
  "spell_name": "Heal",
  "force": 3,
  "target_name": "self",
  "spell_pool_dice": 5,
  "drain_pool_dice": 3
}
```

**Response:**
```json
{
  "error": "Magic Pool exceeded: 5 + 3 = 8, but Manticore's Magic rating is only 6",
  "magic_rating": 6,
  "requested_total": 8,
  "hint": "Reduce spell_pool_dice an

---

### 8. add_karma

Add karma to a character's total and available pool.

**Parameters:**
- `character_name` (string, required): Name of the character
- `amount` (integer, required): Amount of karma to add
- `reason` (string, optional): Reason for karma award

**Returns:**
- Updated karma totals
- Confirmation message

**Example:**
```json
{
  "character_name": "Oak",
  "amount": 5,
  "reason": "Completed mission successfully"
}
```

**Response:**
```json
{
  "character": "Oak",
  "karma_added": 5,
  "total_karma": 170,
  "available_karma": 24,
  "reason": "Completed mission successfully",
  "message": "Added 5 karma to Oak. Total: 170, Available: 24"
}
```

---

### 9. spend_karma

Spend karma from a character's available pool with validation.

**Parameters:**
- `character_name` (string, required): Name of the character
- `amount` (integer, required): Amount of karma to spend
- `reason` (string, optional): Reason for karma expenditure

**Returns:**
- Updated available karma
- Confirmation message

**Example:**
```json
{
  "character_name": "Oak",
  "amount": 2,
  "reason": "Improved Firearms skill"
}
```

**Response:**
```json
{
  "character": "Oak",
  "karma_spent": 2,
  "available_karma": 22,
  "reason": "Improved Firearms skill",
  "message": "Spent 2 karma for Oak. Remaining: 22"
}
```

**Error Response (Insufficient Karma):**
```json
{
  "error": "Insufficient karma: has 22, needs 100",
  "character": "Oak",
  "available": 22,
  "requested": 100
}
```

---

### 10. update_karma_pool

Update a character's karma pool (for in-game spending).

**Parameters:**
- `character_name` (string, required): Name of the character
- `new_pool` (integer, required): New karma pool value
- `reason` (string, optional): Reason for change

**Returns:**
- Updated karma pool
- Confirmation message

**Example:**
```json
{
  "character_name": "Oak",
  "new_pool": 15,
  "reason": "Start of new encounter"
}
```

**Response:**
```json
{
  "character": "Oak",
  "karma_pool": 15,
  "reason": "Start of new encounter",
  "message": "Set Oak's karma pool to 15"
}
```

---

### 11. set_karma

Set both total and available karma (for error correction).

**Parameters:**
- `character_name` (string, required): Name of the character
- `total` (integer, required): Total karma earned
- `available` (integer, required): Available karma to spend
- `reason` (string, optional): Reason for correction

**Returns:**
- Updated karma values
- Confirmation message

**Example:**
```json
{
  "character_name": "Oak",
  "total": 200,
  "available": 50,
  "reason": "Correcting karma tracking error"
}
```

**Response:**
```json
{
  "character": "Oak",
  "total_karma": 200,
  "available_karma": 50,
  "reason": "Correcting karma tracking error",
  "message": "Set Oak's karma to Total: 200, Available: 50"
}
```

---

### 12. add_nuyen

Add nuyen to a character's account.

**Parameters:**
- `character_name` (string, required): Name of the character
- `amount` (integer, required): Amount of nuyen to add
- `reason` (string, optional): Reason for payment

**Returns:**
- Updated nuyen total
- Confirmation message

**Example:**
```json
{
  "character_name": "Oak",
  "amount": 5000,
  "reason": "Payment for completed run"
}
```

**Response:**
```json
{
  "character": "Oak",
  "nuyen_added": 5000,
  "total_nuyen": 580988,
  "reason": "Payment for completed run",
  "message": "Added 5,000¥ to Oak. Total: 580,988¥"
}
```

---

### 13. spend_nuyen

Spend nuyen from a character's account with validation.

**Parameters:**
- `character_name` (string, required): Name of the character
- `amount` (integer, required): Amount of nuyen to spend
- `reason` (string, optional): Reason for expenditure

**Returns:**
- Updated nuyen total
- Confirmation message

**Example:**
```json
{
  "character_name": "Oak",
  "amount": 1500,
  "reason": "Purchased new cyberware"
}
```

**Response:**
```json
{
  "character": "Oak",
  "nuyen_spent": 1500,
  "remaining_nuyen": 579488,
  "reason": "Purchased new cyberware",
  "message": "Spent 1,500¥ for Oak. Remaining: 579,488¥"
}
```

**Error Response (Insufficient Nuyen):**
```json
{
  "error": "Insufficient nuyen: has 579488¥, needs 1000000¥",
  "character": "Oak",
  "available": 579488,
  "requested": 1000000
}
```

---

## Error Handling

All tools return structured error responses when validation fails:

```json
{
  "error": "Character 'InvalidName' not found",
  "available_characters": ["Platinum", "Block", "Manticore"],
  "hint": "Try using the character's street name or full name"
}
```

Common error scenarios:
- Character not found
- Character has no magic rating (for spellcasting)
- Character has no required skill
- Weapon not found
- Invalid parameters

---

## Testing

Test scripts are available in the `tools/` directory:
- `test-spellcasting.py` - Test spellcasting functionality
- `test-character-api.py` - Test character data retrieval
- `test-manticore-bioware-api.py` - Test bioware/cyberware data

Run tests with:
```bash
python tools/test-spellcasting.py
```

---

## Implementation Notes

### UUID Serialization
All tools use `convert_db_types()` to ensure UUID and Decimal types are properly serialized to JSON-compatible formats.

### Dice Rolling
All dice rolls use the `DiceRoller` class which implements:
- Exploding 6s (Rule of 6)
- Success counting
- Critical glitch detection (all 1s)

### Combat Modifiers
The `calculate_ranged_attack` tool automatically applies:
- Smartlink bonuses (from character_modifiers)
- Vision enhancements (thermographic, low-light, magnification)
- Range modifiers
- Environmental modifiers (light level, weather)
- Target size modifiers
- Spell effects (if active)

### Character Data
Character data is pulled from the PostgreSQL database with the v5 schema:
- `characters` table - Base attributes and stats
- `character_skills` table - Skills with base and current ratings
- `character_modifiers` table - Cyberware, bioware, and other modifiers
- `character_gear` table - Weapons, armor, equipment
- `character_vehicles` table - Vehicles
- `character_cyberdecks` table - Cyberdecks
- `character_contacts` table - Contacts
- `character_edges_flaws` table - Edges and flaws
- `character_spirits` table - Bound spirits

---

---

## Dice Rolling Tools

The system provides comprehensive dice rolling capabilities through integration with the dice-server API at https://shadowrun2.com/dice/api.php. All dice rolling tools support exploding dice (6s explode and add another roll) and follow Shadowrun 2nd Edition mechanics.

### Dice Notation Format

- `XdY` - Roll X dice with Y sides (e.g., `2d6` = two six-sided dice)
- `XdY!` - Roll X exploding dice with Y sides (e.g., `4d6!` = four d6 where 6s explode)
- `XdY+Z` - Roll X dice with Y sides and add Z (e.g., `1d20+5`)
- `XdY-Z` - Roll X dice with Y sides and subtract Z (e.g., `3d8-2`)
- `XdY!+Z` - Exploding dice with modifier (e.g., `4d6!+3`)

**Exploding Dice:**
When a die rolls its maximum value, it "explodes" - you roll it again and add the result. This continues until you don't roll the maximum. For example, rolling a 6 on a d6! means you roll again. If you get another 6, that's 12 total and you roll again, etc.

**IMPORTANT: Initiative dice NEVER explode**, even if you include `!` in the notation. This follows Shadowrun rules where initiative is Reaction + 1d6 base (or more with cyberware/magic), but the dice don't explode.

---

### 8. roll_dice (Basic)

Roll dice using standard notation with optional exploding dice.

**Parameters:**
- `notation` (string, required): Dice notation (e.g., '2d6', '4d6!', '1d20+5')

**Returns:**
- Individual rolls
- Sum of rolls
- Modifier applied
- Total result
- Whether dice were exploding

**Example:**
```json
{
  "notation": "4d6!"
}
```

**Response:**
```json
{
  "notation": "4d6!",
  "rolls": [9, 5, 4, 3],
  "sum": 21,
  "modifier": 0,
  "total": 21,
  "exploding": true,
  "timestamp": "2025-10-24T17:30:00-04:00"
}
```

---

### 9. roll_multiple_dice

Roll multiple different dice in a single request.

**Parameters:**
- `notations` (array of strings, required): Array of dice notations

**Returns:**
- Array of roll results, one for each notation

**Example:**
```json
{
  "notations": ["2d6", "1d20+5", "3d8"]
}
```

**Response:**
```json
{
  "rolls": [
    {
      "notation": "2d6",
      "rolls": [5, 4],
      "sum": 9,
      "modifier": 0,
      "total": 9
    },
    {
      "notation": "1d20+5",
      "rolls": [14],
      "sum": 14,
      "modifier": 5,
      "total": 19
    },
    {
      "notation": "3d8",
      "rolls": [6, 3, 7],
      "sum": 16,
      "modifier": 0,
      "total": 16
    }
  ]
}
```

---

### 10. roll_with_advantage

Roll with advantage (D&D 5e mechanics) - roll twice and take the higher result.

**Parameters:**
- `notation` (string, required): Dice notation (typically '1d20')

**Returns:**
- Both rolls
- Which roll was selected
- Final result

**Example:**
```json
{
  "notation": "1d20"
}
```

**Response:**
```json
{
  "notation": "1d20",
  "roll1": {
    "rolls": [14],
    "total": 14
  },
  "roll2": {
    "rolls": [8],
    "total": 8
  },
  "selected": "roll1",
  "result": 14
}
```

---

### 11. roll_with_disadvantage

Roll with disadvantage (D&D 5e mechanics) - roll twice and take the lower result.

**Parameters:**
- `notation` (string, required): Dice notation (typically '1d20')

**Returns:**
- Both rolls
- Which roll was selected
- Final result

**Example:**
```json
{
  "notation": "1d20"
}
```

**Response:**
```json
{
  "notation": "1d20",
  "roll1": {
    "rolls": [14],
    "total": 14
  },
  "roll2": {
    "rolls": [8],
    "total": 8
  },
  "selected": "roll2",
  "result": 8
}
```

---

### 12. roll_with_target_number

Roll dice with Shadowrun-style success counting against a target number.

**Parameters:**
- `notation` (string, required): Dice notation (typically with exploding, e.g., '6d6!')
- `target_number` (integer, required): Target number for successes (2-1000)

**Returns:**
- Individual rolls
- Number of successes (rolls >= target number)
- Whether dice were exploding

**Example:**
```json
{
  "notation": "6d6!",
  "target_number": 5
}
```

**Response:**
```json
{
  "notation": "6d6!",
  "target_number": 5,
  "rolls": [6, 5, 4, 3, 2, 1, 4],
  "successes": 2,
  "exploding": true,
  "timestamp": "2025-10-24T17:30:00-04:00"
}
```

---

### 13. roll_opposed

Roll two sets of dice against each other with net success calculation.

**Parameters:**
- `notation1` (string, required): First dice notation
- `target_number1` (integer, required): Target number for first roll
- `notation2` (string, required): Second dice notation
- `target_number2` (integer, required): Target number for second roll

**Returns:**
- Both rolls with successes
- Net successes (roll1 successes - roll2 successes)
- Winner determination

**Example:**
```json
{
  "notation1": "6d6!",
  "target_number1": 5,
  "notation2": "4d6!",
  "target_number2": 4
}
```

**Response:**
```json
{
  "roll1": {
    "notation": "6d6!",
    "target_number": 5,
    "rolls": [6, 5, 4, 3, 2, 1, 4],
    "successes": 2
  },
  "roll2": {
    "notation": "4d6!",
    "target_number": 4,
    "rolls": [5, 4, 3, 2],
    "successes": 2
  },
  "net_successes": 0,
  "winner": "tie"
}
```

---

### 14. roll_initiative

Roll initiative for a single character (Shadowrun-style).

**Parameters:**
- `notation` (string, required): Initiative dice notation (e.g., '2d6+10')

**Returns:**
- Individual rolls
- Modifier
- Initiative score
- Action phases (initiative and every -10)

**Example:**
```json
{
  "notation": "2d6+10"
}
```

**Response:**
```json
{
  "notation": "2d6+10",
  "rolls": [5, 4],
  "modifier": 10,
  "initiative": 19,
  "phases": [19, 9],
  "timestamp": "2025-10-24T17:30:00-04:00"
}
```

---

### 15. track_initiative

Track initiative for multiple characters with automatic phase ordering and tie-breaking.

**Parameters:**
- `characters` (array, required): Array of character objects with:
  - `name` (string): Character name
  - `notation` (string): Initiative dice notation

**Returns:**
- Initiative results for each character
- Phase-by-phase action order
- Tie-breaking by modifier
- Turn summary

**Example:**
```json
{
  "characters": [
    {"name": "Street Samurai", "notation": "2d6+10"},
    {"name": "Decker", "notation": "1d6+11"},
    {"name": "Mage", "notation": "3d6+8"},
    {"name": "Ganger", "notation": "1d6+5"}
  ]
}
```

**Response:**
```json
{
  "characters": [
    {
      "name": "Street Samurai",
      "notation": "2d6+10",
      "rolls": [5, 4],
      "modifier": 10,
      "initiative": 19,
      "phases": [19, 9]
    },
    {
      "name": "Decker",
      "notation": "1d6+11",
      "rolls": [6],
      "modifier": 11,
      "initiative": 17,
      "phases": [17, 7]
    },
    {
      "name": "Mage",
      "notation": "3d6+8",
      "rolls": [4, 3, 2],
      "modifier": 8,
      "initiative": 17,
      "phases": [17, 7]
    },
    {
      "name": "Ganger",
      "notation": "1d6+5",
      "rolls": [3],
      "modifier": 5,
      "initiative": 8,
      "phases": []
    }
  ],
  "phase_order": [
    {"phase": 19, "actors": ["Street Samurai"]},
    {"phase": 17, "actors": ["Decker", "Mage"]},
    {"phase": 9, "actors": ["Street Samurai"]},
    {"phase": 8, "actors": ["Ganger"]},
    {"phase": 7, "actors": ["Decker", "Mage"]}
  ],
  "turn_summary": "Phase 19: Street Samurai\nPhase 17: Decker, Mage (ties broken by higher modifier)\nPhase 9: Street Samurai\nPhase 8: Ganger\nPhase 7: Decker, Mage (ties broken by higher modifier)"
}
```

---

### 16. roll_with_pools

Roll with dice pools (Shadowrun-style) - track different sources of dice separately.

**Parameters:**
- `pools` (array, required): Array of pool objects with:
  - `name` (string): Pool name (e.g., 'Firearms Skill', 'Combat Pool', 'Karma Pool')
  - `notation` (string): Dice notation for this pool
- `target_number` (integer, required): Target number for successes

**Returns:**
- Results for each pool separately
- Combined total successes
- Individual pool breakdowns

**Common Pool Types:**
- **Combat Pool**: Used for attacks, defense, and dodging
- **Karma Pool**: Bonus dice for critical moments (limited use)
- **Hacking Pool**: Used for decking/hacking operations
- **Task Pool**: Used for decking operations
- **Spell Pool**: Used for magic casting
- **Astral Pool**: Used for astral combat and perception
- **Control Pool**: Used for rigging and vehicle control

**Example:**
```json
{
  "pools": [
    {"name": "Firearms Skill", "notation": "6d6!"},
    {"name": "Combat Pool", "notation": "4d6!"}
  ],
  "target_number": 5
}
```

**Response:**
```json
{
  "pools": [
    {
      "name": "Firearms Skill",
      "notation": "6d6!",
      "rolls": [6, 5, 4, 3, 2, 1, 4],
      "successes": 2
    },
    {
      "name": "Combat Pool",
      "notation": "4d6!",
      "rolls": [6, 5, 3, 2, 5],
      "successes": 3
    }
  ],
  "target_number": 5,
  "total_successes": 5,
  "breakdown": "Firearms Skill: 2 successes, Combat Pool: 3 successes"
}
```

---

### 17. roll_opposed_pools

Roll opposed tests with pool tracking for both sides.

**Parameters:**
- `attacker_pools` (array, required): Attacker's pools
- `attacker_tn` (integer, required): Attacker's target number
- `defender_pools` (array, required): Defender's pools
- `defender_tn` (integer, required): Defender's target number

**Returns:**
- Complete data for both sides
- Net successes
- Winner determination
- Pool breakdowns

**Example:**
```json
{
  "attacker_pools": [
    {"name": "Firearms", "notation": "6d6!"},
    {"name": "Combat Pool", "notation": "4d6!"}
  ],
  "attacker_tn": 5,
  "defender_pools": [
    {"name": "Body", "notation": "5d6"},
    {"name": "Combat Pool", "notation": "3d6"}
  ],
  "defender_tn": 4
}
```

**Response:**
```json
{
  "attacker": {
    "pools": [
      {
        "name": "Firearms",
        "notation": "6d6!",
        "rolls": [6, 5, 4, 3, 2, 1, 4],
        "successes": 2
      },
      {
        "name": "Combat Pool",
        "notation": "4d6!",
        "rolls": [6, 5, 3, 2, 5],
        "successes": 3
      }
    ],
    "target_number": 5,
    "total_successes": 5
  },
  "defender": {
    "pools": [
      {
        "name": "Body",
        "notation": "5d6",
        "rolls": [5, 4, 3, 2, 1],
        "successes": 2
      },
      {
        "name": "Combat Pool",
        "notation": "3d6",
        "rolls": [5, 4, 2],
        "successes": 2
      }
    ],
    "target_number": 4,
    "total_successes": 4
  },
  "net_successes": 1,
  "winner": "attacker"
}
```

---

### 18. reroll_failures (Karma Pool)

Re-roll failed dice using Karma Pool with escalating costs.

**Parameters:**
- `original_rolls` (array, required): Original dice rolls
- `target_number` (integer, required): Target number for successes
- `iteration` (integer, required): Re-roll iteration (1st = 1 Karma, 2nd = 2 Karma, etc.)

**Returns:**
- Re-rolled dice results
- New successes
- Karma cost for this iteration
- Combined total successes

**Karma Pool Re-roll Mechanics:**
- 1st re-roll: 1 Karma
- 2nd re-roll: 2 Karma
- 3rd re-roll: 3 Karma (and so on)
- Can be used iteratively until all dice succeed or Karma runs out

**Example:**
```json
{
  "original_rolls": [4, 3, 2, 1],
  "target_number": 5,
  "iteration": 1
}
```

**Response:**
```json
{
  "iteration": 1,
  "karma_cost": 1,
  "failed_dice": [4, 3, 2, 1],
  "rerolls": [5, 4, 2, 1],
  "new_successes": 1,
  "remaining_failures": [4, 2, 1],
  "summary": "Re-rolled 4 failures for 1 Karma, got 1 new success, 3 failures remain"
}
```

---

### 19. avoid_disaster (Karma Pool)

Use Karma Pool to avoid critical failure (Rule of One).

**Parameters:**
- `rolls` (array, required): The dice rolls (all 1s)

**Returns:**
- Confirmation of disaster avoidance
- Karma cost (always 1)

**Rule of One:**
When all dice come up 1 (critical failure), spend 1 Karma to convert it to a simple failure. No re-roll allowed after using this.

**Example:**
```json
{
  "rolls": [1, 1, 1, 1]
}
```

**Response:**
```json
{
  "disaster_avoided": true,
  "karma_cost": 1,
  "original_rolls": [1, 1, 1, 1],
  "summary": "Spent 1 Karma to avoid critical failure (all 1s)"
}
```

---

### 20. buy_karma_dice

Buy additional dice using Karma Pool before or during a roll.

**Parameters:**
- `dice_to_buy` (integer, required): Number of dice to purchase
- `skill_level` (integer, optional): Skill level (for cap validation)

**Returns:**
- Dice purchased
- Karma cost (1 per die)
- Validation against skill cap

**Mechanics:**
- Cost: 1 Karma per die
- Maximum: Usually capped at skill/attribute level
- These dice roll normally and can explode

**Example:**
```json
{
  "dice_to_buy": 3,
  "skill_level": 6
}
```

**Response:**
```json
{
  "dice_purchased": 3,
  "karma_cost": 3,
  "skill_cap": 6,
  "within_cap": true,
  "summary": "Purchased 3 additional dice for 3 Karma (within skill cap of 6)"
}
```

---

### 21. buy_successes

Buy raw successes using permanent Karma (does not refresh).

**Parameters:**
- `successes_to_buy` (integer, required): Number of successes to purchase
- `has_natural_success` (boolean, required): Whether at least 1 natural success was rolled

**Returns:**
- Successes purchased
- Karma cost (1 per success, PERMANENT)
- Validation that natural success exists

**Mechanics:**
- Cost: 1 Karma per success (PERMANENT - does not refresh)
- Requires: At least 1 natural success in the original roll
- Use sparingly for critical moments

**Example:**
```json
{
  "successes_to_buy": 3,
  "has_natural_success": true
}
```

**Response:**
```json
{
  "successes_purchased": 3,
  "karma_cost": 3,
  "permanent": true,
  "valid": true,
  "summary": "Purchased 3 successes for 3 PERMANENT Karma (requires at least 1 natural success)"
}
```

**Invalid Example:**
```json
{
  "successes_to_buy": 2,
  "has_natural_success": false
}
```

**Response:**
```json
{
  "successes_purchased": 0,
  "karma_cost": 0,
  "permanent": true,
  "valid": false,
  "error": "Cannot buy successes without at least 1 natural success",
  "summary": "Failed to purchase successes - no natural success in original roll"
}
```

---

## Karma Pool Usage Guide

The Karma Pool system allows players to spend Karma to improve their chances of success. One-tenth (round up) of all earned Karma goes into the Karma Pool, which refreshes at the start of each encounter.

### Karma Pool Options

1. **Re-rolling Failures** (Escalating Cost) - Use `reroll_failures`
   - Re-roll any failed dice from a test
   - Can be used iteratively until all dice succeed or Karma runs out
   - Cost increases with each iteration (1, 2, 3, etc.)

2. **Avoid Disaster** (Rule of One) - Use `avoid_disaster`
   - When all dice come up 1 (critical failure), spend 1 Karma to convert to simple failure
   - No re-roll allowed after using this
   - Prevents catastrophic outcomes

3. **Buy Additional Dice** - Use `buy_karma_dice`
   - Add extra dice to a test before or during the roll
   - Maximum usually capped at skill/attribute level
   - These dice roll normally and can explode
   - Cost: 1 Karma per die

4. **Buy Successes** (Permanent Karma) - Use `buy_successes`
   - Purchase raw successes without rolling
   - Requires at least 1 natural success in the original roll
   - Cost: 1 Karma per success (PERMANENT - does not refresh)
   - Use sparingly for critical moments

### AI Workflow for Karma Pool

The AI assistant manages Karma Pool interactions through an iterative conversation:

1. **Initial Roll**: Present results with success/failure breakdown
2. **Offer Options**: If failures exist, ask if player wants to spend Karma
3. **Re-roll Loop**: 
   - Show current successes and remaining failures
   - Display escalating Karma cost for next re-roll
   - Ask if player wants to continue
4. **Track State**: Keep track of re-roll iteration for cost calculation
5. **Final Result**: Present total successes after all Karma spending

**Example Workflow:**
```
AI: "Rolling Firearms 6d6! at TN 5..."
    Result: [6, 5, 4, 3, 2, 1] = 2 successes, 4 failures
    "You got 2 successes. You have 4 failures [4,3,2,1]. 
     Spend 1 Karma to re-roll them?"

User: "Yes"

AI: "Re-rolling 4 failures for 1 Karma..."
    Result: [5, 4, 2, 1] = 1 new success, 3 failures remain
    "You now have 3 total successes. 3 failures remain [4,2,1].
     Spend 2 Karma to re-roll again?"

User: "Yes"

AI: "Re-rolling 3 failures for 2 Karma..."
    Result: [6, 3, 2] = 1 new success, 2 failures remain
    "You now have 4 total successes. 2 failures remain [3,2].
     Spend 3 Karma to re-roll again?"

User: "No, I'll keep the 4 successes"

AI: "Final result: 4 successes. Total Karma spent: 3"
```

---

## Skill Web Defaulting

When a character attempts to use a skill they don't have, they can default from a related skill or the linked attribute by following the Shadowrun Skill Web.

### Defaulting Mechanics

The MCP server provides skill web data to help calculate the target number modifier:

1. **Find the path**: Determine the shortest path from the starting skill/attribute to the target skill
2. **Count the dots**: Each dot (connection point) on the path adds +2 to the target number
3. **Apply the modifier**: Add the calculated modifier to the base target number

### Example: Defaulting from QUICKNESS to Firearms

**Path**: QUICKNESS → dot_p4 → dot_p5 → Firearms
- **Dots traversed**: 2 (dot_p4, dot_p5)
- **Modifier**: 2 × +2 = **+4 to target number**

If the base target number was 5, defaulting would make it 9.

### Graph Structure

The skill web is stored as a directed graph where:
- Nodes prefixed with `dot_` are connection points (dots/circles)
- Named nodes are actual skills and attributes (e.g., "Firearms", "QUICKNESS")
- Each connection has a cost (0 = direct connection, 2 = one dot between)
- The shortest path should always be used for defaulting calculations

---

## Campaign Management Tools

The system provides comprehensive campaign and NPC tracking capabilities to maintain narrative state across sessions.

### 22. create_campaign

Create a new campaign with initial state.

**Parameters:**
- `title` (string, required): Campaign title
- `description` (string, optional): Campaign description
- `theme` (string, optional): Campaign theme/setting

**Returns:**
- Campaign ID (UUID)
- Created campaign data

**Example:**
```json
{
  "title": "Shadows of Seattle",
  "description": "A corporate espionage campaign in the Seattle sprawl",
  "theme": "Corporate intrigue and street-level shadowrunning"
}
```

**Response:**
```json
{
  "id": "7a4a2507-3193-4d00-b9e8-81cab3d7884c",
  "title": "Shadows of Seattle",
  "description": "A corporate espionage campaign in the Seattle sprawl",
  "theme": "Corporate intrigue and street-level shadowrunning",
  "current_situation": null,
  "location": null,
  "objectives": [],
  "active_complications": [],
  "completed_milestones": [],
  "session_id": null,
  "created_at": "2025-10-26T03:29:01.918973",
  "updated_at": "2025-10-26T03:29:01.918973"
}
```

---

### 23. update_campaign_state

Update campaign's current situation, location, objectives, complications, or milestones.

**Parameters:**
- `campaign_id` (string, required): Campaign UUID
- `current_situation` (string, optional): Current narrative situation
- `location` (string, optional): Current location
- `objectives` (array, optional): Array of objective objects with `objective`, `completed`, `order`
- `active_complications` (array, optional): Array of active complication strings
- `completed_milestones` (array, optional): Array of completed milestone strings

**Returns:**
- Updated campaign data

**Example:**
```json
{
  "campaign_id": "7a4a2507-3193-4d00-b9e8-81cab3d7884c",
  "current_situation": "Team has infiltrated the Seamstress Union. Guards at main entrance defeated. Currently in the bar talking to Crusher.",
  "location": "Seamstress Union - Bar",
  "objectives": [
    {"objective": "Find the stolen data chip", "completed": false, "order": 1},
    {"objective": "Avoid alerting building security", "completed": true, "order": 2},
    {"objective": "Extract without casualties", "completed": false, "order": 3}
  ],
  "active_complications": [
    "Building security has been alerted",
    "Backup guards en route to garage"
  ],
  "completed_milestones": [
    "Infiltrated Seamstress Union",
    "Defeated entrance guards"
  ]
}
```

**Response:**
```json
{
  "id": "7a4a2507-3193-4d00-b9e8-81cab3d7884c",
  "title": "Shadows of Seattle",
  "current_situation": "Team has infiltrated the Seamstress Union. Guards at main entrance defeated. Currently in the bar talking to Crusher.",
  "location": "Seamstress Union - Bar",
  "objectives": [
    {"objective": "Find the stolen data chip", "completed": false, "order": 1},
    {"objective": "Avoid alerting building security", "completed": true, "order": 2},
    {"objective": "Extract without casualties", "completed": false, "order": 3}
  ],
  "active_complications": [
    "Building security has been alerted",
    "Backup guards en route to garage"
  ],
  "completed_milestones": [
    "Infiltrated Seamstress Union",
    "Defeated entrance guards"
  ],
  "updated_at": "2025-10-26T03:35:00.000000"
}
```

---

### 24. get_campaign

Retrieve complete campaign data.

**Parameters:**
- `campaign_id` (string, required): Campaign UUID

**Returns:**
- Complete campaign data including all state

**Example:**
```json
{
  "campaign_id": "7a4a2507-3193-4d00-b9e8-81cab3d7884c"
}
```

**Response:**
```json
{
  "id": "7a4a2507-3193-4d00-b9e8-81cab3d7884c",
  "title": "Shadows of Seattle",
  "description": "A corporate espionage campaign in the Seattle sprawl",
  "theme": "Corporate intrigue and street-level shadowrunning",
  "current_situation": "Team has infiltrated the Seamstress Union...",
  "location": "Seamstress Union - Bar",
  "objectives": [...],
  "active_complications": [...],
  "completed_milestones": [...],
  "session_id": null,
  "created_at": "2025-10-26T03:29:01.918973",
  "updated_at": "2025-10-26T03:35:00.000000"
}
```

---

### 25. register_npc

Register a new NPC in the campaign with tracking data.

**Parameters:**
- `campaign_id` (string, required): Campaign UUID
- `name` (string, required): NPC name
- `role` (string, required): NPC role (e.g., 'guard', 'bartender', 'johnson', 'contact')
- `location` (string, required): Current location
- `relevance` (string, required): Relevance level ('current', 'background', 'future')
- `description` (string, optional): NPC description
- `stats` (object, optional): Combat stats (body, quickness, strength, armor, etc.)
- `notes` (string, optional): GM notes

**Returns:**
- Created NPC data with UUID

**Relevance Levels:**
- **current**: NPCs actively involved in the current scene
- **background**: NPCs present but not immediately relevant
- **future**: NPCs mentioned but not yet encountered

**Example:**
```json
{
  "campaign_id": "7a4a2507-3193-4d00-b9e8-81cab3d7884c",
  "name": "Guard Alpha",
  "role": "guard",
  "location": "Seamstress Union - Main Entrance",
  "relevance": "current",
  "description": "Heavily armed security guard at the main entrance",
  "stats": {
    "body": 5,
    "quickness": 4,
    "strength": 5,
    "armor": "5/3"
  }
}
```

**Response:**
```json
{
  "id": "npc-uuid-here",
  "campaign_id": "7a4a2507-3193-4d00-b9e8-81cab3d7884c",
  "name": "Guard Alpha",
  "role": "guard",
  "location": "Seamstress Union - Main Entrance",
  "relevance": "current",
  "status": "active",
  "description": "Heavily armed security guard at the main entrance",
  "stats": {
    "body": 5,
    "quickness": 4,
    "strength": 5,
    "armor": "5/3"
  },
  "notes": null,
  "created_at": "2025-10-26T03:30:00.000000",
  "updated_at": "2025-10-26T03:30:00.000000"
}
```

---

### 26. update_npc

Update NPC status, location, relevance, or notes.

**Parameters:**
- `npc_id` (string, required): NPC UUID
- `status` (string, optional): Status ('active' or 'inactive')
- `location` (string, optional): New location
- `relevance` (string, optional): New relevance level
- `notes` (string, optional): Additional notes (appended to existing)

**Returns:**
- Updated NPC data

**Example:**
```json
{
  "npc_id": "npc-uuid-here",
  "status": "inactive",
  "relevance": "background",
  "notes": "Defeated in combat at main entrance"
}
```

**Response:**
```json
{
  "id": "npc-uuid-here",
  "campaign_id": "7a4a2507-3193-4d00-b9e8-81cab3d7884c",
  "name": "Guard Alpha",
  "role": "guard",
  "location": "Seamstress Union - Main Entrance",
  "relevance": "background",
  "status": "inactive",
  "description": "Heavily armed security guard at the main entrance",
  "stats": {...},
  "notes": "Defeated in combat at main entrance",
  "updated_at": "2025-10-26T03:32:00.000000"
}
```

---

### 27. get_campaign_npcs

Retrieve NPCs for a campaign with optional filtering.

**Parameters:**
- `campaign_id` (string, required): Campaign UUID
- `relevance` (string, optional): Filter by relevance ('current', 'background', 'future')
- `location` (string, optional): Filter by location (partial match)
- `status` (string, optional): Filter by status ('active' or 'inactive')

**Returns:**
- Array of matching NPCs

**Example (Get current NPCs):**
```json
{
  "campaign_id": "7a4a2507-3193-4d00-b9e8-81cab3d7884c",
  "relevance": "current"
}
```

**Response:**
```json
{
  "npcs": [
    {
      "id": "npc-uuid-1",
      "name": "Guard Beta",
      "role": "guard",
      "location": "Seamstress Union - Garage Sublevel 2",
      "relevance": "current",
      "status": "active",
      "description": "Second guard at main entrance",
      "stats": {...}
    },
    {
      "id": "npc-uuid-2",
      "name": "Crusher",
      "role": "bartender",
      "location": "Seamstress Union - Bar",
      "relevance": "current",
      "status": "active",
      "description": "Troll bartender, knows everyone in the building",
      "stats": null
    }
  ],
  "count": 2
}
```

**Example (Get NPCs by location):**
```json
{
  "campaign_id": "7a4a2507-3193-4d00-b9e8-81cab3d7884c",
  "location": "Main Entrance"
}
```

**Response:**
```json
{
  "npcs": [
    {
      "id": "npc-uuid-1",
      "name": "Guard Alpha",
      "role": "guard",
      "location": "Seamstress Union - Main Entrance",
      "relevance": "background",
      "status": "inactive",
      ...
    }
  ],
  "count": 1
}
```

---

## Campaign Management Workflow

### Typical Campaign Flow

1. **Campaign Creation**
   - Use `create_campaign` to start a new campaign
   - Store the campaign_id for all future operations

2. **NPC Registration**
   - As NPCs are introduced, use `register_npc` to track them
   - Set appropriate relevance level (current/background/future)
   - Include combat stats for NPCs that may fight

3. **State Updates**
   - Use `update_campaign_state` to track narrative progress
   - Update objectives as they're completed
   - Add complications as they arise
   - Record milestones for major achievements

4. **NPC Management**
   - Use `update_npc` when NPCs change status or location
   - Move defeated NPCs to 'inactive' status
   - Adjust relevance as NPCs enter/exit scenes
   - Append notes for important events

5. **Context Retrieval**
   - Use `get_campaign` to load campaign state
   - Use `get_campaign_npcs` with filters to get relevant NPCs
   - Inject this data into narrative generation prompts

### Example Session Flow

```
1. Load campaign: get_campaign(campaign_id)
2. Get current NPCs: get_campaign_npcs(campaign_id, relevance='current')
3. [Players enter new area]
4. Register new NPCs: register_npc(...) for each new NPC
5. [Combat occurs]
6. Update defeated NPC: update_npc(npc_id, status='inactive')
7. Update campaign: update_campaign_state(location='New Area', ...)
8. [Session ends]
9. Record milestone: update_campaign_state(completed_milestones=[...])
```

---

## Version History

### v1.4.0 (2025-10-25)
- Added campaign management tools (6 tools total)
- Campaign state tracking (situation, location, objectives, complications, milestones)
- NPC registration and tracking system
- Relevance-based NPC filtering (current/background/future)
- Location-based NPC queries
- Status management for NPCs (active/inactive)

### v1.3.0 (2025-10-24)
- Added comprehensive dice rolling tools (14 tools total)
- Integration with dice-server API at https://shadowrun2.com/dice/api.php
- Dice pool tracking (Combat Pool, Karma Pool, Spell Pool, etc.)
- Initiative tracking with phase calculation
- Karma Pool mechanics (re-rolls, buying dice, buying successes)
- Opposed tests with pool tracking
- Advantage/Disadvantage mechanics (D&D 5e)
- Skill web defaulting support

### v1.2.0 (2025-10-24)
- Added `cast_spell` tool for Shadowrun 2nd Edition spellcasting
- Implements official SR2 drain mechanics
- Supports Spell Pool dice
- Validates magic rating and Sorcery skill
- Returns detailed drain information

### v1.1.0 (2025-10-23)
- Added `calculate_ranged_attack` tool
- Automatic modifier application from character sheet
- Vision enhancement support
- Environmental modifier handling

### v1.0.0 (2025-10-20)
- Initial MCP tool implementation
- Basic character data retrieval
- Dice rolling with exploding 6s
- Skill and attribute queries

---

## Python Library Modules (New in v1.5.0)

The system now includes Python library modules that provide enhanced functionality for the MCP server. These are **helper libraries** that the MCP tools can use internally - they do not replace any existing tools.

### Hybrid Search Module (`lib/hybrid_search.py`)

Provides advanced search capabilities combining vector similarity (OpenAI embeddings + pgvector) with PostgreSQL full-text search using Reciprocal Rank Fusion (RRF).

**Key Features:**
- Vector similarity search using OpenAI embeddings
- PostgreSQL full-text search
- Reciprocal Rank Fusion (RRF) to combine results
- Specialized searches for spells, gear, rules, and lore
- Automatic fallback to keyword-only if vector search fails

**Usage in Python:**
```python
from lib.hybrid_search import HybridSearch
import psycopg

conn = psycopg.connect(...)
searcher = HybridSearch(conn)

# General hybrid search
results = searcher.hybrid_search("initiative combat", limit=5)

# Specialized searches
spell_info = searcher.search_spells("Heal")
gear_info = searcher.search_gear("smartlink")
rules = searcher.search_rules("initiative")
lore = searcher.search_lore("Seattle 2050s")
```

**Search Result Format:**
```python
{
    'id': 'uuid',
    'title': 'INITIATIVE',
    'content': 'Initiative determines the order...',
    'category': 'combat',
    'subcategory': 'combat_turn',
    'tags': ['initiative', 'combat'],
    'content_type': 'rule_mechanic',
    'source_file': 'core-combat-rules',
    'rrf_score': 0.0325,  # Combined score
    'vector_rank': 2,      # Rank in vector search
    'keyword_rank': 1,     # Rank in keyword search
    'similarity_score': 0.85  # Vector similarity (if available)
}
```

### Character CRUD API (`lib/character_crud_api.py`)

Provides comprehensive Create, Read, Update, Delete operations for character data with complete audit logging and soft delete support.

**Key Features:**
- Full CRUD operations for spells, modifiers, gear, vehicles
- Automatic audit logging (who, when, why)
- Soft delete (data never truly deleted, can be restored)
- RAG supplementation (auto-fill missing data from rules database)
- User attribution (USER, AI, SYSTEM)
- Session-based audit context

**Usage in Python:**
```python
from lib.character_crud_api import CharacterCRUDAPI, get_ai_user_id
import psycopg

# Get AI user ID for attribution
conn = psycopg.connect(...)
ai_user_id = get_ai_user_id(conn)
conn.close()

# Initialize API
api = CharacterCRUDAPI(user_id=ai_user_id, user_type='AI')

# Add spell with RAG supplementation
spell_data = {
    'spell_name': 'Heal',
    'learned_force': 6
}
spell = api.add_spell(
    character_id=2,
    spell_data=spell_data,
    reason="Character advancement"
)
# RAG automatically fills in drain_code, target_type, etc.

# Update spell force
updated = api.update_spell_force(
    character_id=2,
    spell_name='Heal',
    new_force=8,
    reason="Increased mastery"
)

# Soft delete (can be restored later)
deleted = api.soft_delete_spell(
    character_id=2,
    spell_name='Heal',
    reason="Character forgot spell"
)

# Restore deleted spell
restored = api.restore_spell(
    character_id=2,
    spell_name='Heal',
    reason="Character re-learned spell"
)

# Get audit history
history = api.get_audit_log(
    table_name='character_spells',
    limit=20
)

api.close()
```

**Audit Log Format:**
```python
{
    'id': 'uuid',
    'table_name': 'character_spells',
    'record_id': 'spell-uuid',
    'operation': 'UPDATE',  # INSERT, UPDATE, DELETE
    'changed_by': 'ai-user-id',
    'changed_by_type': 'AI',  # USER, AI, SYSTEM
    'changed_by_email': 'ai@shadowrun-gm.system',
    'changed_by_name': 'AI Assistant',
    'changed_at': '2025-10-27T21:00:00Z',
    'old_values': {...},  # Previous state
    'new_values': {...},  # New state
    'change_reason': 'Increased spell mastery'
}
```

### Database Schema Enhancements (Migration 019)

**New Tables:**
- `users` - User accounts for audit tracking
  - Tracks USER (Rick St Jean), AI (AI Assistant), SYSTEM
- `audit_log` - Complete change history for all character data
  - Captures who, when, what, why for every change

**Enhanced Character Tables:**
All character tables now include:
- `created_by` - User who created the record
- `created_at` - Creation timestamp
- `modified_by` - User who last modified
- `modified_at` - Last modification timestamp
- `deleted_at` - Soft delete timestamp (NULL = active)
- `deleted_by` - User who deleted the record

**Enhanced Spell Fields:**
- `drain_code` - Spell drain code (e.g., "6S", "(F/2)M")
- `target_type` - Spell target type (e.g., "M/S/D")
- `totem_modifier` - Totem bonus dice for this spell
- `spell_notes` - Additional spell notes from character sheet

**Active Views:**
- `active_character_spells` - Only non-deleted spells
- `active_character_modifiers` - Only non-deleted modifiers
- `active_character_gear` - Only non-deleted gear
- `active_character_vehicles` - Only non-deleted vehicles

### User Types

**USER** (rickstjean@gmail.com - Rick St Jean)
- Human user making manual changes
- Full permissions

**AI** (ai@shadowrun-gm.system - AI Assistant)
- AI making automated changes
- Used for RAG supplementation, auto-calculations

**SYSTEM** (system@shadowrun-gm.internal - System)
- System-level operations
- Migrations, batch operations, imports

### RAG Supplementation

The CRUD API can automatically supplement missing spell data from the rules database:

```python
# When adding a spell with minimal data
spell_data = {
    'spell_name': 'Heal',
    'learned_force': 6
}

# RAG searches rules database and fills in:
# - drain_code: "(F/2)D"
# - target_type: "M"
# - spell_category: "health"
# - spell_notes: "Heal spell description from rules..."
# - totem_modifier: 2 (if character has Bear totem)
```

### Integration with MCP Tools

The Python libraries are designed to be used by the MCP tools in `game-server.py`:

1. **Hybrid Search** - Can enhance rule lookups, spell descriptions, gear stats
2. **CRUD API** - Provides audit trail for all character modifications
3. **RAG Supplementation** - Auto-fills missing data when importing/updating

**Example Integration:**
```python
# In game-server.py MCP tool
@server.call_tool()
async def add_spell_with_rag(character_name: str, spell_name: str, force: int):
    """Add spell with automatic RAG supplementation"""
    
    # Get character ID
    char_id = get_character_id(character_name)
    
    # Use CRUD API with RAG
    api = CharacterCRUDAPI(user_id=ai_user_id, user_type='AI')
    
    # Add spell (minimal data)
    spell_data = {
        'spell_name': spell_name,
        'learned_force': force
    }
    
    # RAG supplements missing fields
    rag_data = api.supplement_spell_from_rag(spell_name)
    spell_data.update(rag_data)
    
    # Create with full data + audit trail
    result = api.add_spell(
        character_id=char_id,
        spell_data=spell_data,
        reason=f"Added via MCP tool by AI"
    )
    
    api.close()
    return result
```

---

## Version History

### v1.5.0 (2025-10-27)
- Added Python library modules (hybrid_search.py, character_crud_api.py)
- Implemented audit logging system with user attribution
- Added soft delete support for all character data
- Implemented RAG supplementation for missing spell data
- Added migration 019 (users, audit_log, enhanced spell fields)
- Installed pgvector for vector similarity search
- Archived server-unified.js (Node.js version)

### v1.4.0 (2025-10-25)
- Added campaign management tools (6 tools total)
- Campaign state tracking (situation, location, objectives, complications, milestones)
- NPC registration and tracking system
- Relevance-based NPC filtering (current/background/future)
- Location-based NPC queries
- Status management for NPCs (active/inactive)

### v1.3.0 (2025-10-24)
- Added comprehensive dice rolling tools (14 tools total)
- Integration with dice-server API at https://shadowrun2.com/dice/api.php
- Dice pool tracking (Combat Pool, Karma Pool, Spell Pool, etc.)
- Initiative tracking with phase calculation
- Karma Pool mechanics (re-rolls, buying dice, buying successes)
- Opposed tests with pool tracking
- Advantage/Disadvantage mechanics (D&D 5e)
- Skill web defaulting support

### v1.2.0 (2025-10-24)
- Added `cast_spell` tool for Shadowrun 2nd Edition spellcasting
- Implements official SR2 drain mechanics
- Supports Spell Pool dice
- Validates magic rating and Sorcery skill
- Returns detailed drain information

### v1.1.0 (2025-10-23)
- Added `calculate_ranged_attack` tool
- Automatic modifier application from character sheet
- Vision enhancement support
- Environmental modifier handling

### v1.0.0 (2025-10-20)
- Initial MCP tool implementation
- Basic character data retrieval
- Dice rolling with exploding 6s
- Skill and attribute queries
