#!/usr/bin/env python3
"""
Fix type mismatches in all data-load-final-*.sql files
- metatypes.special_abilities: should be TEXT[] (convert '[]'::jsonb to ARRAY[]::text[])
"""

import os
import re
import glob

print('Fixing type mismatches in split SQL files...\n')

# Get the directory
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(script_dir, '..')

# Find all data-load-final-*.sql files
sql_files = glob.glob(os.path.join(parent_dir, 'data-load-final-*.sql'))
sql_files.sort()

print(f'Found {len(sql_files)} SQL files to process\n')

total_fixes = 0

for sql_file in sql_files:
    filename = os.path.basename(sql_file)
    
    # Read the file
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_size = len(content)
    
    # Count metatypes with '[]'::jsonb for special_abilities
    # Pattern: special_abilities comes before racial_traits in metatypes
    # So we look for '[]'::jsonb followed by '{}'::jsonb
    fixes_needed = len(re.findall(r"INSERT INTO metatypes.*?'\[\]'::jsonb,\s*'\{\}'::jsonb", content, re.DOTALL))
    
    if fixes_needed > 0:
        # Fix: Replace '[]'::jsonb, '{}'::jsonb with ARRAY[]::text[], '{}'::jsonb
        content = re.sub(
            r"'\[\]'::jsonb,(\s*)'\{\}'::jsonb",
            r"ARRAY[]::text[],\1'{}'::jsonb",
            content
        )
        
        # Write back
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        new_size = len(content)
        total_fixes += fixes_needed
        print(f'✓ {filename:<30} Fixed {fixes_needed} metatype(s)')
    else:
        print(f'  {filename:<30} No fixes needed')

print(f'\n✅ Total fixes applied: {total_fixes}')
