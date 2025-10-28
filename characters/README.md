# Character Sheets

This folder contains standardized character sheets for all player characters in the Shadowrun campaign.

## Format

All character sheets follow a standardized markdown format with the following sections:

1. **Basic Information** - Name, street name, race, archetype, resources
2. **Attributes** - Physical and mental attributes
3. **Skills** - All learned skills with ratings and specializations
4. **Edges and Flaws** - Character advantages and disadvantages
5. **Contacts** - NPCs the character knows
6. **Gear** - Equipment organized by category:
   - Weapons (with full stats, ammo, and modifications)
   - Vehicles (with stats)
   - Equipment (general gear)
7. **Cyberware** - Cybernetic implants with essence costs
8. **Bioware** - Biological augmentations with body index costs
9. **Spells** - For magical characters
10. **Adept Powers** - For physical adepts
11. **Matrix Stats** - For deckers

## Characters

- **Platinum** (Kent Jefferies) - Human Street Samurai
- **Oak** (Simon Stalman) - Human
- **Manticore** (Edom Pentathor) - Dwarf Decker
- **Block** (Mok' TuBing) - Rhino Shapeshifter Physical Magician
- **Axel** (Riley O'Connor) - Human

## Maintenance

These files are automatically generated from the database using:

```bash
python tools/export-character-sheets.py
```

To import character sheets into the database:

```bash
python tools/import-character-sheets.py
```

## Standardized Format

The weapon format follows this pattern:
```markdown
- **Weapons**:
  - **Weapon Name** (Conceal X, Capacity(c), Mode, Damage, Reach X)
    - **Ammo Type** (details)
    - **Modification** (details)
```

This ensures consistent parsing and prevents formatting issues.
