#!/usr/bin/env python3
"""
Fix type mismatches in SQL INSERT statements
- powers.levels: should be JSONB (convert ARRAY[]::text[] to '[]'::jsonb)
- metatypes.special_abilities: should be TEXT[] (convert '[]'::jsonb to ARRAY[]::text[])
"""

import os
import re

print('Fixing type mismatches in SQL data...\n')

# Get the path to the SQL file
script_dir = os.path.dirname(os.path.abspath(__file__))
sql_file_path = os.path.join(script_dir, '..', 'supabase-data-fixed.sql')

# Read the SQL file
with open(sql_file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f'Original file size: {len(content)} bytes')

# Count issues before fix
powers_text_arrays = len(re.findall(r'INSERT INTO powers.*?ARRAY\[\]::text\[\]', content, re.DOTALL))
metatypes_jsonb_arrays = len(re.findall(r"INSERT INTO metatypes.*?'\\[\\]'::jsonb.*?special_abilities", content, re.DOTALL))

print(f'Found {powers_text_arrays} powers with ARRAY[]::text[] (should be jsonb)')
print(f'Found {metatypes_jsonb_arrays} metatypes with \'[]\'::jsonb for special_abilities (should be text[])')

# Fix powers table: levels column should be JSONB
# Match INSERT INTO powers statements and replace ARRAY[]::text[] with '[]'::jsonb for the levels column
def fix_powers_levels(match):
    insert_stmt = match.group(0)
    # Replace ARRAY[]::text[] with '[]'::jsonb in powers INSERT statements
    fixed = re.sub(r'ARRAY\[\]::text\[\]', "'[]'::jsonb", insert_stmt)
    return fixed

content = re.sub(
    r'INSERT INTO powers \([^)]+\) VALUES \([^;]+\);',
    fix_powers_levels,
    content,
    flags=re.DOTALL
)

# Fix metatypes table: special_abilities column should be TEXT[]
# Match INSERT INTO metatypes statements and replace '[]'::jsonb with ARRAY[]::text[] for special_abilities
def fix_metatypes_special_abilities(match):
    insert_stmt = match.group(0)
    # Find the special_abilities position and replace '[]'::jsonb with ARRAY[]::text[]
    # The pattern is: ..., special_abilities, racial_traits, ...
    # We need to replace '[]'::jsonb that comes BEFORE '{}'::jsonb (racial_traits)
    fixed = re.sub(r"'\\[\\]'::jsonb,\s*'\\{\\}'::jsonb", "ARRAY[]::text[], '{}'::jsonb", insert_stmt)
    return fixed

content = re.sub(
    r'INSERT INTO metatypes \([^)]+\) VALUES \([^;]+\);',
    fix_metatypes_special_abilities,
    content,
    flags=re.DOTALL
)

# Count after fix
powers_text_arrays_after = len(re.findall(r'INSERT INTO powers.*?ARRAY\[\]::text\[\]', content, re.DOTALL))
metatypes_jsonb_arrays_after = len(re.findall(r"INSERT INTO metatypes.*?'\\[\\]'::jsonb.*?special_abilities", content, re.DOTALL))

print(f'\nAfter fix:')
print(f'Powers with ARRAY[]::text[]: {powers_text_arrays_after}')
print(f'Metatypes with \'[]\'::jsonb for special_abilities: {metatypes_jsonb_arrays_after}')

# Write the fixed content back
with open(sql_file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✓ Fixed! Updated file saved to: {sql_file_path}')
print(f'File size after fix: {len(content)} bytes')
