# Character Sheet Data Comparison

## What Should Be Displayed (from GEMINI-CHARACTER-SHEET-PROMPT.md)

### Basic Information
- [x] Name (full legal name)
- [x] Street Name
- [ ] Metatype (Human/Elf/Dwarf/Ork/Troll)
- [x] Archetype
- [ ] Sex
- [ ] Age
- [ ] Height
- [ ] Weight
- [ ] Hair
- [ ] Eyes
- [ ] Skin

### Attributes
- [x] Body (with augmented value if different)
- [x] Quickness (with augmented value if different)
- [x] Strength (with augmented value if different)
- [x] Charisma (with augmented value if different)
- [x] Intelligence (with augmented value if different)
- [x] Willpower (with augmented value if different)
- [x] Essence
- [x] Magic (if applicable)
- [x] Reaction

### Derived Stats
- [x] Initiative
- [x] Combat Pool
- [x] Karma Pool
- [x] Total Karma Earned
- [ ] Total Karma Available
- [x] Nuyen
- [ ] Lifestyle (Type, cost/month, months prepaid)
- [ ] Essence Hole (if applicable)

### Edges and Flaws
- [ ] Edges list
- [ ] Flaws list

### Decker Stats (if applicable)
- [ ] Body Index (Current/Max)
- [ ] Task Pool
- [ ] Hacking Pool
- [ ] Matrix Initiative

### Mage Stats (if applicable)
- [ ] Magic Pool
- [ ] Spell Pool
- [ ] Initiate Level
- [ ] Metamagics
- [ ] Magical Group/Lodge
- [ ] Tradition

### Adept Powers (if applicable)
- [ ] Power Name, Cost, Description

### Rigger Stats (if applicable)
- [ ] Rigged Reaction
- [ ] Rigged Initiative
- [ ] Vehicle Control Rig level

### Skills
- [x] Active Skills (name, rating, specialization)
- [ ] Knowledge Skills
- [ ] Language Skills

### Cyberware/Bioware
- [ ] Cyberware items with essence cost and details
- [ ] Bioware items with body index and details
- [ ] Special abilities granted by augmentations

### Gear
#### Weapons
- [ ] Weapon name
- [ ] Type
- [ ] Damage
- [ ] Concealability
- [ ] Ammo capacity
- [ ] Modifications

#### Armor
- [ ] Armor name
- [ ] Rating (Ballistic/Impact)
- [ ] Concealability

#### Equipment
- [ ] Item name
- [ ] Quantity
- [ ] Description/notes

#### Cyberdecks (for Deckers)
- [ ] Deck name
- [ ] MPCP
- [ ] Hardening
- [ ] Memory
- [ ] Storage
- [ ] I/O Speed
- [ ] Response Increase
- [ ] Persona Programs
- [ ] Utilities
- [ ] AI Companions

#### Magical Items (for Mages)
- [ ] Item name
- [ ] Type (Focus/Fetish/Talisman)
- [ ] Rating
- [ ] Bonuses
- [ ] Karma Cost

#### Vehicles
- [ ] Vehicle name
- [ ] Type
- [ ] Handling
- [ ] Speed
- [ ] Body
- [ ] Armor
- [ ] Signature
- [ ] Pilot
- [ ] Modifications

### Magic (if applicable)
#### Spells
- [ ] Spell name
- [ ] Force
- [ ] Type (Combat/Detection/Health/Illusion/Manipulation)
- [ ] Target
- [ ] Drain code

#### Spell Locks/Quickened Spells
- [ ] Spell name
- [ ] Force
- [ ] Successes
- [ ] Effect

#### Spell Formulas (Unlearned)
- [ ] Spell name
- [ ] Force
- [ ] Type
- [ ] Drain

#### Bound Spirits
- [ ] Spirit name/type
- [ ] Force
- [ ] Services
- [ ] Special Abilities
- [ ] Notes

#### Totems/Traditions
- [ ] Totem name
- [ ] Advantages
- [ ] Disadvantages

#### Power Sites (if applicable)
- [ ] Site name
- [ ] Location
- [ ] Background Count
- [ ] Effects
- [ ] Attuned status

### Contacts
- [ ] Contact name
- [ ] Role/Profession
- [ ] Level (1-3)
- [ ] Notes

### Background
- [ ] Character background, personality, motivations

### Notes
- [x] Additional notes

---

## What's Currently in Database (from schema.sql)

### characters table
- id, name, street_name, character_type, archetype
- metatype, sex, age, height, weight, hair, eyes, skin
- base_* and current_* for all attributes
- nuyen, karma_pool, karma_total, karma_available
- lifestyle, lifestyle_cost, lifestyle_months_prepaid
- essence_hole
- initiative
- notes, background

### character_skills table
- character_id, skill_name, skill_type (active/knowledge/language)
- base_rating, current_rating, specialization

### character_gear table
- character_id, gear_name, gear_type, quantity
- damage, conceal, ammo_capacity
- ballistic_rating, impact_rating
- modifications (JSONB)
- notes

### character_modifiers table
- character_id, modifier_type, target_name, modifier_value
- source, source_type (cyberware/bioware/spell/adept_power)
- weapon_specific, condition
- modifier_data (JSONB)
- essence_cost, body_index_cost
- is_permanent, is_homebrew, house_rule_id

### character_spells table
- character_id, spell_name, force, category
- target_type, drain_code
- is_quickened, quickened_successes

### character_contacts table
- character_id, contact_name, role, level, notes

### character_edges_flaws table
- character_id, name, type (edge/flaw), description

### character_vehicles table
- character_id, vehicle_name, vehicle_type
- handling, speed, body, armor, signature, pilot
- modifications (JSONB)

---

## What's Currently Returned by API (game-server.py lines 1150-1350)

```python
{
    "id": str,
    "name": str,
    "street_name": str,
    "character_type": str,
    "archetype": str,
    "nuyen": int,
    "karma_pool": int,
    "karma_total": int,
    "initiative": str,
    "notes": str,
    "attributes": {
        "body": int,
        "quickness": int,
        "strength": int,
        "charisma": int,
        "intelligence": int,
        "willpower": int,
        "essence": float,
        "magic": int,
        "reaction": int
    },
    "skills": [
        {
            "skill_name": str,
            "rating": int,
            "specialization": str
        }
    ],
    "gear": [
        {
            "name": str,
            "gear_name": str,
            "quantity": int,
            "notes": str
        }
    ],
    "spells": [
        {
            "spell_name": str,
            "force": int,
            "category": str
        }
    ]
}
```

---

## MISSING FROM API RESPONSE

### Basic Information
- metatype
- sex
- age
- height
- weight
- hair
- eyes
- skin

### Derived Stats
- karma_available
- lifestyle (type, cost, months prepaid)
- essence_hole
- combat_pool (calculated)
- magic_pool (for mages)
- spell_pool (for mages)
- task_pool (for deckers)
- hacking_pool (for deckers)
- body_index (for bioware users)

### Edges and Flaws
- edges list
- flaws list

### Skills
- skill_type distinction (active/knowledge/language)
- Currently returns ALL skills mixed together

### Cyberware/Bioware
- NOT RETURNED AT ALL
- Should query character_modifiers where source_type='cyberware' or 'bioware'
- Should include essence_cost, body_index_cost
- Should include special abilities from modifier_data

### Gear Details
- Currently only returns: name, quantity, notes
- MISSING: gear_type, damage, conceal, ammo_capacity
- MISSING: ballistic_rating, impact_rating (for armor)
- MISSING: modifications (JSONB)

### Weapons (should be separate from gear)
- Should filter gear where gear_type='weapon'
- Should include: damage, conceal, ammo_capacity, modifications

### Armor (should be separate from gear)
- Should filter gear where gear_type='armor'
- Should include: ballistic_rating, impact_rating, conceal

### Vehicles
- NOT RETURNED AT ALL
- Should query character_vehicles table

### Contacts
- NOT RETURNED AT ALL
- Should query character_contacts table

### Spell Details
- Currently returns: spell_name, force, category
- MISSING: target_type, drain_code
- MISSING: is_quickened, quickened_successes

### Background
- NOT RETURNED (exists in DB but not in API response)

---

## ACTION ITEMS

### 1. Update API Endpoint (game-server.py)
Add queries for:
- [x] Basic physical description (metatype, sex, age, height, weight, hair, eyes, skin)
- [ ] Derived stats (karma_available, lifestyle, essence_hole, body_index)
- [ ] Calculated pools (combat_pool, magic_pool, spell_pool, task_pool, hacking_pool)
- [ ] Edges and flaws (from character_edges_flaws table)
- [ ] Skills grouped by type (active/knowledge/language)
- [ ] Cyberware (from character_modifiers where source_type='cyberware')
- [ ] Bioware (from character_modifiers where source_type='bioware')
- [ ] Weapons (from character_gear where gear_type='weapon' with full details)
- [ ] Armor (from character_gear where gear_type='armor' with full details)
- [ ] Equipment (from character_gear where gear_type NOT IN ('weapon', 'armor'))
- [ ] Vehicles (from character_vehicles table)
- [ ] Contacts (from character_contacts table)
- [ ] Spell details (target_type, drain_code, quickened info)
- [ ] Background field

### 2. Update Character Sheet Renderer (character-sheet-renderer.js)
Add sections for:
- [ ] Physical description in Basic Info
- [ ] Lifestyle and essence hole in Derived Stats
- [ ] All calculated pools
- [ ] Edges and Flaws section
- [ ] Decker Stats section (if applicable)
- [ ] Mage Stats section (if applicable)
- [ ] Rigger Stats section (if applicable)
- [ ] Skills grouped by type (Active/Knowledge/Language)
- [ ] Cyberware section with essence costs and abilities
- [ ] Bioware section with body index costs and abilities
- [ ] Weapons section (separate from gear)
- [ ] Armor section (separate from gear)
- [ ] Equipment section (non-weapon/armor gear)
- [ ] Vehicles section
- [ ] Contacts section
- [ ] Spell details (drain codes, quickened spells)
- [ ] Background section

### 3. Test Thoroughly
- [ ] Test with Platinum (Street Samurai with heavy cyberware/bioware)
- [ ] Test with Manticore (Decker)
- [ ] Test with Oak (Shaman/Mage)
- [ ] Test with Block (Physical Magician)
- [ ] Verify all sections display correctly
- [ ] Verify no data is missing
