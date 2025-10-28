#!/usr/bin/env python3
"""
Proper fix that handles each table's columns correctly
"""
import glob
import re

files = glob.glob('data-load-final-*.sql')
files.sort()

def fix_powers_table(content):
    """Powers: levels=JSONB, loaded_from=TEXT[]"""
    # Fix levels column (should be JSONB) - it comes right after game_effects
    # Pattern: game_effects, levels, description
    content = re.sub(
        r"(INSERT INTO powers[^;]*?'\{\}'::jsonb,\s*)ARRAY\[\]::text\[\](,\s*'[^']*',)",
        r"\1'[]'::jsonb\2",
        content
    )
    # loaded_from should already be TEXT[] or NULL, no fix needed
    return content

def fix_metatypes_table(content):
    """Metatypes: special_abilities=TEXT[], racial_traits=JSONB, loaded_from=TEXT[]"""
    # Fix racial_traits (should be JSONB) - comes right after special_abilities
    # Pattern: special_abilities, racial_traits, description
    # special_abilities is TEXT[] (correct), racial_traits should be JSONB
    content = re.sub(
        r"(INSERT INTO metatypes[^;]*?ARRAY\[\]::text\[\],\s*)ARRAY\[\]::text\[\](,\s*'[^']*',)",
        r"\1'{}'::jsonb\2",
        content
    )
    # special_abilities and loaded_from should already be TEXT[], no fix needed
    return content

def fix_gear_table(content):
    """Gear: base_stats/modifiers/requirements=JSONB, tags/loaded_from=TEXT[]"""
    # All columns are currently ARRAY[]::text[]
    # Need to fix: base_stats, modifiers, requirements back to JSONB
    # Keep: tags, loaded_from as TEXT[]
    
    # Fix base_stats (first JSONB column after subcategory)
    content = re.sub(
        r"(INSERT INTO gear[^;]*?(?:NULL|'[^']*'),\s*)ARRAY\[\]::text\[\](,\s*ARRAY\[\]::text\[\],\s*ARRAY\[\]::text\[\])",
        r"\1'{}'::jsonb\2",
        content
    )
    # Fix modifiers (second JSONB column)
    content = re.sub(
        r"(INSERT INTO gear[^;]*?'\{\}'::jsonb,\s*)ARRAY\[\]::text\[\](,\s*ARRAY\[\]::text\[\],\s*ARRAY\[\]::text\[\])",
        r"\1'{}'::jsonb\2",
        content
    )
    # Fix requirements (third JSONB column)
    content = re.sub(
        r"(INSERT INTO gear[^;]*?'\{\}'::jsonb,\s*'\{\}'::jsonb,\s*)ARRAY\[\]::text\[\](,\s*ARRAY\[\]::text\[\])",
        r"\1'{}'::jsonb\2",
        content
    )
    # tags and loaded_from should already be TEXT[], no fix needed
    return content

total_fixed = 0

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    original = content
    
    # Apply fixes for each table
    content = fix_powers_table(content)
    content = fix_metatypes_table(content)
    content = fix_gear_table(content)
    
    if content != original:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        total_fixed += 1
        print(f'Fixed {f}')

print(f'\nDone! Fixed {total_fixed} files')
