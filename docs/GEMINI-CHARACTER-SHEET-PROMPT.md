# Gemini Prompt: Standardize Shadowrun Character Sheets

## Instructions for Gemini

Please reformat this Shadowrun 2nd Edition character sheet into a standardized Markdown format that can be consistently parsed by automated tools. Follow this exact structure:

---

## Character Sheet Format Template

```markdown
# [Character Name] ([Street Name])

## Basic Information
- **Name**: [Full legal name]
- **Street Name**: [Street/runner name]
- **Metatype**: [Human/Elf/Dwarf/Ork/Troll]
- **Archetype**: [Street Samurai/Decker/Mage/etc.]
- **Sex**: [M/F/Other]
- **Age**: [Number]
- **Height**: [cm or feet/inches]
- **Weight**: [kg or lbs]
- **Hair**: [Color/style]
- **Eyes**: [Color]
- **Skin**: [Tone/color]

## Attributes
### Base Form (or Human Form for Shapeshifters)
- **Body**: [Rating]
- **Quickness**: [Rating]
- **Strength**: [Rating]
- **Charisma**: [Rating]
- **Intelligence**: [Rating]
- **Willpower**: [Rating]
- **Essence**: [Rating (typically 6.0 for unaugmented)]
- **Magic**: [Rating or N/A]
- **Reaction**: [Rating]

### Animal Form (Shapeshifters Only)
- **Form**: [Animal type - e.g., Wolf, Eagle, Bear]
- **Body**: [Rating]
- **Quickness**: [Rating]
- **Strength**: [Rating]
- **Charisma**: [Rating]
- **Intelligence**: [Rating]
- **Willpower**: [Rating]
- **Essence**: [Same as base]
- **Magic**: [Same as base]
- **Reaction**: [Rating]
- **Special Abilities**: [Natural weapons, movement modes, senses, etc.]

## Derived Stats
- **Initiative**: [Base + Dice (e.g., "1d6+5")]
- **Combat Pool**: [Number]
- **Karma Pool**: [Current/Total (e.g., "2/5")]
- **Total Karma Earned**: [Number]
- **Total Karma Available**: [Number]
- **Nuyen**: [Amount]
- **Lifestyle**: [Type (cost/month, months prepaid)]
- **Essence Hole**: [Amount, if applicable - e.g., "0.18"]

## Edges and Flaws (if using Shadowrun Companion)
### Edges
- **[Edge Name]**: [Description]

### Flaws
- **[Flaw Name]**: [Description]

## Decker Stats (if applicable)
- **Body Index**: [Current/Max]
- **Task Pool**: [Number]
- **Hacking Pool**: [Number]
- **Matrix Initiative**: [Base + Dice]

## Mage Stats (if applicable)
- **Magic Pool**: [Number]
- **Spell Pool**: [Number]
- **Initiate Level**: [Number or None]
- **Metamagics**: [List metamagics - e.g., centering, quickening, anchoring, masking, etc.]
- **Magical Group/Lodge**: [Name and description]
- **Tradition**: [Hermetic/Shamanic/etc.]

## Adept Powers (if applicable)
- **[Power Name]**: [Cost in points] - [Description]

## Rigger Stats (if applicable)
- **Rigged Reaction**: [Number]
- **Rigged Initiative**: [Base + Dice]
- **Vehicle Control Rig**: [Level]

## Skills
### Active Skills
- **[Skill Name]**: [Rating] [Specialization if any]
- **[Skill Name]**: [Rating] [Specialization if any]
[Continue for all active skills]

### Knowledge Skills
- **[Skill Name]**: [Rating]
- **[Skill Name]**: [Rating]
[Continue for all knowledge skills]

### Language Skills
- **[Language]**: [Rating] (R/W)
[Continue for all languages]

## Cyberware/Bioware
### Cyberware
- **[Item Name]** ([Essence Cost])
  - [Details/ratings if applicable]
  - [Special abilities or modifiers]

### Bioware
- **[Item Name]** ([Essence Cost])
  - [Details/ratings if applicable]

## Gear
### Weapons
- **[Weapon Name]**
  - Type: [Weapon type]
  - Damage: [Damage code]
  - Concealability: [Rating]
  - Ammo: [Capacity]
  - Modifications: [List any mods]

### Armor
- **[Armor Name]**
  - Rating: [Ballistic/Impact]
  - Concealability: [Rating]

### Equipment
- **[Item Name]** (Qty: [Number])
  - [Description/notes]

### Cyberdecks (for Deckers)
- **[Deck Name]**
  - MPCP: [Rating]
  - Hardening: [Rating]
  - Memory: [MP]
  - Storage: [MP]
  - I/O Speed: [Rating]
  - Response Increase: [+Number]
  - Persona Programs: [List with ratings]
  - Utilities: [List installed utilities]
  - AI Companions: [List any AI helpers like K.A.R.R., ARESIA, etc.]

### Magical Items (for Mages)
- **[Item Name]**
  - Type: [Focus/Fetish/Talisman/etc.]
  - Rating: [Number]
  - Bonuses: [List effects]
  - Karma Cost: [If applicable]

### Vehicles
- **[Vehicle Name]**
  - Type: [Vehicle type]
  - Handling: [Rating]
  - Speed: [Rating]
  - Body: [Rating]
  - Armor: [Rating]
  - Signature: [Rating]
  - Pilot: [Rating]
  - Modifications: [List any mods]

## Magic (if applicable)
### Spells
- **[Spell Name]** (Force [X])
  - Type: [Combat/Detection/Health/Illusion/Manipulation]
  - Target: [Target type]
  - Drain: [(F÷2)-1 or similar]

### Spell Locks/Quickened Spells
- **[Spell Name]** (Force [X])
  - Successes: [Number]
  - Effect: [Description]

### Spell Formulas (Unlearned)
- **[Spell Name]** (Force [X])
  - Type: [Combat/Detection/Health/Illusion/Manipulation]
  - Drain: [(F÷2)-1 or similar]

### Bound Spirits
- **[Spirit Name/Type]** (Force [X])
  - Services: [Number or "Permanent"]
  - Special Abilities: [List]
  - Notes: [Relationship, true name binding, etc.]

### Totems/Traditions
- **Totem**: [Totem name]
- **Advantages**: [List]
- **Disadvantages**: [List]

### Power Sites (if applicable)
- **[Site Name]**
  - Location: [Description]
  - Background Count: [Rating]
  - Effects: [List magical effects]
  - Attuned: [Yes/No and details]

## Contacts
- **[Contact Name]** - [Role/Profession]
  - Level: [1-3]
  - Notes: [Brief description]

## Background
[Character background, personality, motivations, etc.]

## Notes
[Any additional notes, house rules, special conditions, etc.]
```

---

## Formatting Rules

1. **Consistency**: Use the exact same headers and structure for every character
2. **Sections**: Include ALL sections even if empty (mark as "None" or "N/A")
3. **Shapeshifters**: 
   - Always include both "Base Form" and "Animal Form" attribute sections
   - List animal form's special abilities (natural weapons, enhanced senses, movement)
   - Note any attribute differences between forms
   - If not a shapeshifter, only use "Base Form" section
4. **Cyberware/Bioware**:
   - List essence cost in parentheses
   - Include all ratings (e.g., "Smartlink 3", "Cybereyes Alpha")
   - List special abilities as sub-bullets
5. **Weapons**:
   - Always include Type, Damage, Concealability, Ammo
   - List modifications separately
6. **Skills**:
   - Format as "Skill Name: Rating Specialization"
   - Group by type (Active/Knowledge/Language)
7. **Attributes**:
   - Always use full names (Body, not Bod)
   - Include current values if different from base
8. **Numbers**:
   - Use consistent decimal format for Essence (e.g., 5.4 not 5.40)
   - Use integers for other ratings
9. **Lists**:
   - Use bullet points (-)
   - Indent sub-items with spaces
10. **Special Abilities**:
   - List under the item that grants them
   - Be specific about bonuses (e.g., "-2 TN for ranged attacks")

## Example Cyberware Section

```markdown
## Cyberware/Bioware
### Cyberware
- **Cybereyes Alpha** (0.4 Essence)
  - Thermographic Vision (cybernetic)
  - Low-Light Vision (cybernetic)
  - Optical Magnification 3
  - Flare Compensation
  - Image Link

- **Smartlink 3** (0.5 Essence)
  - -3 TN to ranged attacks with smartlink-equipped weapons
  - No magazine size penalty
  - +2 TN for grenade attacks
  - Displays ammo count, range, and targeting data

- **Wired Reflexes 2** (3.0 Essence)
  - +2 Reaction
  - +2d6 Initiative
  - +2 to all Combat Pools
```

## Example Shapeshifter Attributes

```markdown
## Attributes
### Base Form (Human)
- **Body**: 4
- **Quickness**: 5
- **Strength**: 3
- **Charisma**: 6
- **Intelligence**: 5
- **Willpower**: 6
- **Essence**: 6.0
- **Magic**: 6
- **Reaction**: 5

### Animal Form (Wolf)
- **Form**: Wolf
- **Body**: 5 (+1 from base)
- **Quickness**: 6 (+1 from base)
- **Strength**: 4 (+1 from base)
- **Charisma**: 6 (same)
- **Intelligence**: 5 (same)
- **Willpower**: 6 (same)
- **Essence**: 6.0
- **Magic**: 6
- **Reaction**: 6 (+1 from base)
- **Special Abilities**:
  - Bite: (STR+2)M damage
  - Enhanced Hearing: +2 to Perception (sound-based)
  - Enhanced Smell: +2 to Perception (scent-based)
  - Low-Light Vision (natural)
  - Running: 4x normal movement rate
```

## What to Preserve

- All numerical values exactly as they appear
- All item names and descriptions
- All special abilities and bonuses
- Background and personality information
- Contact relationships

## What to Standardize

- Header formatting (use # ## ### consistently)
- Bullet point style (always use -)
- Attribute names (full names, not abbreviations)
- Section order (follow template exactly)
- Essence cost format (always in parentheses)
- Rating format (always after item name)

---

## Verification Checklist

Before processing, ensure the character sheet contains these elements (check all that apply):

### Basic Information
- [ ] Full name and street name
- [ ] Metatype (Human/Elf/Dwarf/Ork/Troll/Shapeshifter)
- [ ] Physical description (height, weight, hair, eyes, skin)
- [ ] Age and sex

### Attributes & Stats
- [ ] All 6 core attributes (Body, Quickness, Strength, Charisma, Intelligence, Willpower)
- [ ] Essence and Magic ratings
- [ ] Reaction rating
- [ ] Initiative (base + dice)
- [ ] Combat Pool
- [ ] Karma Pool (current/total)
- [ ] Nuyen/resources

### Shapeshifter-Specific (if applicable)
- [ ] Base form attributes
- [ ] Animal form attributes
- [ ] Animal form special abilities (natural weapons, senses, movement)
- [ ] Attribute modifiers between forms

### Skills
- [ ] Active skills with ratings and specializations
- [ ] Knowledge skills
- [ ] Language skills with Read/Write notation

### Augmentations
- [ ] Cyberware with essence costs
- [ ] Bioware with essence costs
- [ ] Ratings for all augmentations (e.g., Smartlink 3, Wired Reflexes 2)
- [ ] Special abilities granted by augmentations
- [ ] Vision enhancements (thermographic, low-light, magnification, etc.)

### Gear
- [ ] Weapons with full stats (Type, Damage, Concealability, Ammo)
- [ ] Weapon modifications (smartlink, laser sight, scope, etc.)
- [ ] Armor with ratings (Ballistic/Impact)
- [ ] Equipment and quantities
- [ ] Vehicles with full stats (if any)

### Magic (if applicable)
- [ ] Spell list with Force ratings
- [ ] Spell types and drain codes
- [ ] Totem/tradition information
- [ ] Totem advantages and disadvantages

### Other
- [ ] Contacts with levels and descriptions
- [ ] Background/personality
- [ ] Special notes or house rules
- [ ] Edge/Flaw information (if using Shadowrun Companion rules)

### Common Missing Details to Watch For
- **Essence costs**: Always include in parentheses after cyberware/bioware
- **Body Index**: For bioware users, track current/max
- **Essence Hole**: Note if character has lost essence from removed cyberware
- **Ratings**: Include for all items that have them (Smartlink 3, not just Smartlink)
- **Special abilities**: List all bonuses/penalties (e.g., "-3 TN for ranged attacks")
- **Vision types**: Specify if cybernetic or natural (affects darkness penalties)
- **Weapon mods**: List separately from base weapon
- **Spell drain**: Include drain code for each spell
- **Attribute changes**: Note if cyberware/bioware modifies attributes
- **Metamagics**: List all metamagic techniques for initiates
- **Spell Locks**: Note active spell locks with force and successes
- **Bound Spirits**: Include force, services, and special relationships
- **Adept Powers**: List with point costs
- **Shapeshifter Traits**: Natural weapons, armor, regeneration, dual nature
- **Rigger Stats**: Separate meat/rigged initiative and reaction
- **AI Companions**: For deckers, note any AI helpers in cyberdecks
- **Power Sites**: For mages with attuned locations

---

Please process the character sheet and output it in this exact format. Maintain all game-mechanical information while ensuring the structure is identical across all characters.

**IMPORTANT**: If any section is missing from the source character sheet, include the section header but mark it as "None" or "N/A". This ensures consistent structure across all character sheets.
