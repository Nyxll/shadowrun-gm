#!/usr/bin/env python3
"""
Fix the levels column type mismatch in supabase-data-fixed.sql
Replaces ARRAY[]::text[] with '[]'::jsonb to match the jsonb column type
"""

import os
import re

# Get the path to the SQL file
script_dir = os.path.dirname(os.path.abspath(__file__))
sql_file_path = os.path.join(script_dir, '..', 'supabase-data-fixed.sql')

print('Fixing levels column type mismatch...')

# Read the SQL file
with open(sql_file_path, 'r', encoding='utf-8') as f:
    sql_content = f.read()

print(f'Original file size: {len(sql_content)} bytes')

# Count occurrences before fix
before_count = len(re.findall(r'ARRAY\[\]::text\[\]', sql_content))
print(f'Found {before_count} instances of ARRAY[]::text[]')

# Replace ARRAY[]::text[] with '[]'::jsonb
sql_content = re.sub(r'ARRAY\[\]::text\[\]', "'[]'::jsonb", sql_content)

# Count occurrences after fix
after_count = len(re.findall(r'ARRAY\[\]::text\[\]', sql_content))
print(f'Remaining instances of ARRAY[]::text[]: {after_count}')

# Count new jsonb arrays
jsonb_count = len(re.findall(r"'?\[\]'?::jsonb", sql_content))
print(f'Total instances of []::jsonb: {jsonb_count}')

# Write the fixed content back
with open(sql_file_path, 'w', encoding='utf-8') as f:
    f.write(sql_content)

print(f'\n✓ Fixed! Updated file saved to: {sql_file_path}')
print(f'File size after fix: {len(sql_content)} bytes')
