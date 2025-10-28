# Character Sheet Section Header Cleanup

## Problem Identified

Character gear data in the database contained section headers (items ending with `:`) that were imported from the original markdown files. These section headers were being treated as actual gear items.

Examples of problematic section headers:
- `Additional Gear:`
- `Explosives:`
- `Magical Items:`
- `Other:`
- `Weapons:`
- `Vehicles:`
- `Worn:`
- `In Pockets:`
- `Go Bags (1 in Eurocar Westwind, 1 in House):`
- `Each contains:`

## Solution Implemented

### 1. Database Cleanup (`tools/clean-gear-sections.py`)

Created a script to remove all gear items ending with `:` from the `character_gear` table:

```bash
python tools/clean-gear-sections.py
```

**Result**: Removed 12 section headers from the database

### 2. Import Script Update (`tools/import-character-sheets.py`)

Updated the gear parsing logic to skip section headers during import:

```python
# Skip section headers (items ending with ':')
if gear_item and len(gear_item) > 2 and not gear_item.endswith(':'):
    character['gear'].append({
        'gear_name': gear_item[:200],
        'quantity': 1,
        'notes': None
    })
```

This prevents future imports from adding section headers to the database.

### 3. Export Script Behavior (`tools/export-character-sheets.py`)

The export script creates its own organizational headers:
- `- **Weapons**:` (for weapons section)
- `- **Vehicles**:` (for vehicles section)  
- `- **Equipment**:` (for general gear)

These are **intentional formatting headers** created by the export script, not data from the database.

## Verification

After cleanup and re-export:

```bash
# Before cleanup
Found 12 section headers to remove:
  - Additional Gear:
  - Each contains:
  - Explosives:
  - Go Bags (1 in Eurocar Westwind, 1 in House):
  - In Pockets:
  - Magical Items:
  - Other:
  - Vehicles:
  - Vehicles and Drones:
  - Weapons:
  - Weapons:
  - Worn:

# After cleanup
Section headers found: 3
  - **Weapons**: (export script header)
  - **Vehicles**: (export script header)
  - **Equipment**: (export script header)
```

## Workflow

### To Clean Existing Data
```bash
python tools/clean-gear-sections.py
python tools/export-character-sheets.py
```

### To Import New Character Sheets
```bash
python tools/import-character-sheets.py
```

The import script now automatically skips section headers, so they won't be added to the database.

## Files Modified

1. **tools/clean-gear-sections.py** - New cleanup script
2. **tools/check-gear-sections.py** - New diagnostic script
3. **tools/import-character-sheets.py** - Updated to skip section headers
4. **tools/export-character-sheets.py** - No changes needed (already creates proper headers)

## Notes

- Section headers ending with `:` are now filtered out during import
- The export script creates its own organizational headers for readability
- This ensures clean data in the database while maintaining readable markdown output
- Future imports will not add section headers to the database
